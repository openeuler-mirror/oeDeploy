#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-01-16
# ======================================================================================================================
import binascii
import hashlib
import json
import secrets
from base64 import b64decode, b64encode
from typing import Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from constants.configs.account_config import SALT_LENGTH


class DecryptError(Exception):

    def __int__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class OEDPCipher:

    @staticmethod
    def _generate_root_key(half_key_1: str) -> bytes:
        """
        通过组合两个半秘钥，然后加上盐值，使用 PBKDF2 算法进行哈希计算，最终返回一个根秘钥
        """
        half_key_2 = "fl1HGmk3k45xza89"
        # 组合秘钥，并转换为 utf-8 格式的字符串
        key = (half_key_1 + half_key_2).encode("utf-8")
        salt = b"k\x80bb\xd4\xb1(\x87\xd6\x19;\x8dX\x91^1\xe2\x91\xb6\xf6"
        # 加密秘钥
        encrypted_key = hashlib.pbkdf2_hmac("sha256", key, salt, 16582)
        # 将二进制转换为十六进制，然后截取部分后返回
        return binascii.hexlify(encrypted_key)[13:45]

    @staticmethod
    def _encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
        """
        使用 AES-GCM 算法对给定明文进行加密。
        :param key:  AES-GCM 算法使用的密钥
        :param iv:  初始化向量
        :param plaintext:  需要加密的明文字节串
        """
        # 创建加密器
        encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), default_backend()).encryptor()
        # 加密明文
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return ciphertext

    @staticmethod
    def _decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
        """
        使用 AES-GCM 算法对给定密文进行解密。
        :param key:  AES-GCM 算法使用的密钥
        :param iv:  初始化向量
        :param ciphertext:  需要解密的明文字节串
        """
        # 创建解密器
        decrypter = Cipher(algorithms.AES(key), modes.GCM(iv), default_backend()).decryptor()
        # 解密密文
        plaintext = decrypter.update(ciphertext)
        return plaintext

    def _generate_work_key(self, half_key: str) -> (str, str, bytes):
        """
        随机生成一个工作秘钥和初始化向量，然后通过根秘钥对工作秘钥进行加密，
        最后将加密后的工作秘钥和初始化向量以 Base64 编码的字符串形式返回,
        为加密的工作秘钥以字节串的形式返回。
        """
        # 获取根秘钥
        root_key = self._generate_root_key(half_key)
        # 生成32字节的安全随机字节串作为工作秘钥，16字节的作为初始化向量
        work_key = secrets.token_bytes(32)
        work_key_iv = secrets.token_bytes(16)
        # 加密工作秘钥
        encrypted_work_key = self._encrypt(root_key, work_key_iv, work_key)
        # 编码为 Base64 格式的字节串，方便传输。然后解码为 ASCII 字符串
        encrypted_work_key = b64encode(encrypted_work_key).decode("ascii")
        work_key_iv = b64encode(work_key_iv).decode("ascii")
        return encrypted_work_key, work_key_iv, work_key

    def _decrypt_work_key(self, half_key: str, encrypted_work_key: str, work_key_iv: str) -> bytes:
        """
        解密工作秘钥
        """
        root_key = self._generate_root_key(half_key)
        encrypted_work_key = b64decode(encrypted_work_key.encode("ascii"))
        work_key_iv = b64decode(work_key_iv.encode("ascii"))
        return self._decrypt(root_key, work_key_iv, encrypted_work_key)

    def encrypt_plaintext(self, plaintext: Union[str, dict]) -> dict:
        """
        加密明文, 明文可以是字符串或者字典
        """
        plaintext = json.dumps(plaintext)
        half_key = self.generate_random_string()
        encrypted_work_key, work_key_iv, work_key = self._generate_work_key(half_key)
        plaintext_with_salt = f"{half_key}{plaintext}".encode("utf-8")
        del plaintext
        plaintext_iv = secrets.token_bytes(16)
        ciphertext = self._encrypt(work_key, plaintext_iv, plaintext_with_salt)
        del plaintext_with_salt
        ciphertext = b64encode(ciphertext).decode("ascii")
        plaintext_iv = b64encode(plaintext_iv).decode("ascii")
        ciphertext_data = {
            'half_key': half_key,
            'encrypted_work_key': encrypted_work_key,
            'work_key_iv': work_key_iv,
            'ciphertext': ciphertext,
            'plaintext_iv': plaintext_iv,
        }
        return ciphertext_data

    def decrypt_ciphertext_data(self, ciphertext_data: dict) -> Union[str, dict]:
        """
        解密密文
        """
        half_key = ciphertext_data.get('half_key', '')
        encrypted_work_key = ciphertext_data.get('encrypted_work_key', '')
        work_key_iv = ciphertext_data.get('work_key_iv', '')
        ciphertext = ciphertext_data.get('ciphertext', '')
        plaintext_iv = ciphertext_data.get('plaintext_iv', '')
        # 当 ciphertext_data 字典的某一个 key 的值为空时，解密失败，抛出异常
        if not all([half_key, encrypted_work_key, work_key_iv, ciphertext, plaintext_iv]):
            raise DecryptError('Failed to decrypt, invalid ciphertext json')
        work_key = self._decrypt_work_key(half_key, encrypted_work_key, work_key_iv)
        ciphertext = b64decode(ciphertext.encode("ascii"))
        plaintext_iv = b64decode(plaintext_iv.encode("ascii"))
        plaintext_with_salt = self._decrypt(work_key, plaintext_iv, ciphertext)
        plaintext_with_salt = plaintext_with_salt.decode("utf-8")
        plaintext = plaintext_with_salt[len(half_key):]
        return json.loads(plaintext)

    @staticmethod
    def generate_random_string(length=16, seed=None) -> str:
        """
        根据指定的字符集，生成指定长度的随机字符串
        :return:
        """
        if seed is None:
            seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(secrets.choice(seed) for _ in range(length))

    @staticmethod
    def get_salt(length=SALT_LENGTH):
        return b64encode(secrets.token_bytes(length)).decode()
