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
from base64 import b64decode
from ctypes import cdll, c_char_p, c_void_p, c_int, create_string_buffer

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from constants.paths import LIBCRYPTO_SO_FILE


def decrypt(key: bytes, encrypted_iv: bytes, encrypted: bytes) -> bytes:
    """decrypt using AES-GCM algorithms

    Parameters
    ----------
    key : bytes
        AES-GCM key
    encrypted_iv : bytes
        AES-GCM iv
    encrypted : bytes
        bytes to be decrypt

    Returns
    -------
    bytes
        decrypted bytes of encrypted
    """
    decrypter = Cipher(
        algorithms.AES(key),
        modes.GCM(encrypted_iv),
        default_backend()
    ).decryptor()

    plaintext = decrypter.update(encrypted)
    return plaintext


def get_root_key_b(half_key1: str) -> bytes:
    """Get root_key derived from half_key1 + half_key2 + salt

    Parameters
    ----------
    half_key1 : str
        The first half key.

    Returns
    -------
    bytes
        root key in bytes.
    """
    half_key2 = "jsvgf82hso8d"
    key = (half_key1 + half_key2).encode("utf-8")
    half_key3 = b"k\x80bb\xd4\xb1(\x87\xd6\x19;\x8dX\x91^1\xe2\x91\xb6\xf6"
    key_hash = hashlib.pbkdf2_hmac("sha256", key, half_key3, 16582)
    return binascii.hexlify(key_hash)[13:45]


def get_work_key_b(
        half_key1: str,
        work_key_encrypted: str,
        work_key_encrypted_iv: str) -> bytes:
    """Decrypt work_key using root_key

    Parameters
    ----------
    half_key1 : str
        The first half key.
    work_key_encrypted : str
        The encrypted string of work_key.
    work_key_encrypted_iv : str
        The AES-GCM iv used for encrypting work_key.

    Returns
    -------
    bytes
        work_key in bytes.
    """
    root_key_b = get_root_key_b(half_key1)

    work_key_encrypted_b = b64decode(work_key_encrypted.encode("ascii"))
    work_key_encrypted_iv_b = b64decode(work_key_encrypted_iv.encode("ascii"))

    return decrypt(root_key_b, work_key_encrypted_iv_b, work_key_encrypted_b)


def decrypt_string(
    half_key1: str,
    work_key_encrypted: str,
    work_key_encrypted_iv: str,
    encrypted: str,
    encrypted_iv: str
) -> str:
    """Decrypt string using work_key

    Parameters
    ----------
    half_key1 : str
        The first half key.
    work_key_encrypted : str
        The encrypted string of work_key.
    work_key_encrypted_iv : str
        The AES-GCM iv used for encrypting work_key.
    encrypted : str
        The string to decrypt.
    encrypted_iv : str
        The AES-GCM iv used for encrypting plaintext.

    Returns
    -------
    str
        The decrypted plaintext.
    """
    work_key_b = get_work_key_b(
        half_key1,
        work_key_encrypted,
        work_key_encrypted_iv)

    encrypted_b = b64decode(encrypted.encode("ascii"))
    encrypted_iv_b = b64decode(encrypted_iv.encode("ascii"))
    plaintext_b = decrypt(work_key_b, encrypted_iv_b, encrypted_b)
    # 去掉salt长度后得到原文
    salt_plaintext = plaintext_b.decode("utf-8")
    plaintext = salt_plaintext[len(half_key1):]
    return plaintext


def decrypt_mariadb_passwd(secret_key_file, ciphertext):
    """
    解密
    :param secret_key_file: 密钥文件
    :param ciphertext: 密文
    :return: 明文
    """
    with open(secret_key_file, mode='r') as fr_handle:
        config_content = json.load(fr_handle)
        half_key1 = config_content["half_key1"]
        work_key_encrypted = config_content["work_key_encrypted"]
        work_key_encrypted_iv = config_content["work_key_encrypted_iv"]
        encrypted_iv = config_content["encrypted_iv"]
        plaintext = decrypt_string(
            half_key1,
            work_key_encrypted,
            work_key_encrypted_iv,
            ciphertext,
            encrypted_iv
        )
        return plaintext


def rand_bytes(size):
    """
    使用 openssl 的 RAND_pri_bytes 生成随机字节数组
    :param size: 长度
    :return: 字节数组
    """
    gen_rand = cdll.LoadLibrary(LIBCRYPTO_SO_FILE)
    gen_rand.RAND_priv_bytes.argtypes = [c_char_p, c_int]
    gen_rand.RAND_priv_bytes.restype = c_void_p
    # buf 不能使用c_char_p,遇到\0会截断
    buf = create_string_buffer(size)
    gen_rand.RAND_priv_bytes(buf, size)
    return bytes(buf)
