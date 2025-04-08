import argparse
import os.path
import re
import xml.etree.ElementTree as ET
import subprocess
from contextlib import contextmanager

quiet = True


def check_version(src, tar, op=">="):
    src_list = src.split('.')
    tar_list = tar.split('.')

    for index, str in enumerate(tar_list):
        if '*' in str or index >= len(src_list):
            break

        if op == ">=":
            if int(src_list[index]) > int(str):
                return True
            elif int(src_list[index]) == int(str):
                continue
            else:
                return False
        elif op == "<":
            if int(src_list[index]) < int(str):
                return True
            elif int(src_list[index]) == int(str):
                continue
            else:
                return False
        elif op == "=":
            if int(src_list[index]) != int(str):
                return False
        else:
            return False
    return True


class Runcmd(object):
    @staticmethod
    def sendcmd(cmd, workspace=None, check=True, extra_env: dict = None):
        env = os.environ.copy()
        if extra_env:
            for key in extra_env:
                env[key] = extra_env.get(key)

        if not quiet:
            print(f"cmd: {cmd}")
        result = subprocess.run(cmd, cwd=workspace, shell=True, check=check, capture_output=True, encoding='utf-8',
                                env=env)
        if not quiet:
            print(f"done\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}\nreturn code: {result.returncode}")
        return '\n'.join(result.stdout.split('\n')).strip("\n")


class Installer(object):
    __root = None
    __function_dict = dict()

    def __init__(self, xml_path):
        self.__root = ET.parse(xml_path).getroot()
        self.__ROOT_PATH = os.path.abspath(os.path.dirname(os.getcwd()))
        self.__SOURCE_PATH = os.path.join(self.__ROOT_PATH, "source/")
        self.__init_func_dict()
        self.__platform = self.__check_platform()

    def __check_platform(self):
        kunpeng_platform = {"0xd01": "Kunpeng 920", "0xd02": "Kunpeng 920 V200"}
        implementer = Runcmd.sendcmd("cat /proc/cpuinfo | grep 'CPU implementer' | head -n 1 | awk '{print $NF}'")
        part = Runcmd.sendcmd("cat /proc/cpuinfo | grep 'CPU part' | head -n 1 | awk '{print $NF}'")

        if implementer == "0x48":
            return kunpeng_platform.get(part)
        else:
            return Runcmd.sendcmd("lscpu | grep 'BIOS Model name:' | awk '{print $NF}'")

    def __check_env(self):
        with self.__process("检查代理"):
            Runcmd.sendcmd("curl www.baidu.com")

        with self.__process("检查yum源, 并安装必要工具"):
            Runcmd.sendcmd("yum makecache")
            Runcmd.sendcmd("yum install -y git tar gcc gcc-c++ patch")
            Runcmd.sendcmd("git config --global https.sslverify false")
            Runcmd.sendcmd("git config --global http.sslverify false")

    def __chech_env_in_profile(self, key, value):
        libpath = os.getenv(key)
        if libpath and value in libpath:
            return True

        env_list = Runcmd.sendcmd(f"cat /etc/profile | grep {key}").split("\n")
        for env in env_list:
            if value in env and not re.search("#.+export", env):
                return True

        return False

    def __get_element_text(self, tag: str):
        tags = [child.tag for child in self.__root.find(tag)]
        texts = [child.text for child in self.__root.find(tag)]
        info = dict()

        for index, tag in enumerate(tags):
            info[tag] = texts[index]

        return info

    @contextmanager
    def __process(self, topic):
        try:
            print(topic)
            yield
            print(f"{topic}成功")
        except subprocess.CalledProcessError as e:
            print(f"{topic}存在执行命令失败, 报错信息如下:\n{e.stderr}")
            raise e
        except Exception as e:
            print(f"{topic}失败")
            raise e

    def __install_ksl(self):
        Runcmd.sendcmd("rm -rf ./KSL", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd(f"mkdir -p KSL/rpm", workspace=f"{self.__ROOT_PATH}")

        ksl_info = self.__get_element_text("KSL")
        with self.__process("安装KSL"):
            res = Runcmd.sendcmd("cat /etc/os-release")
            name = re.search("NAME=\"(.+)\"", res).group(1)
            assert name == "openEuler", "仅支持在openEuler上安装"
            os_version = re.search("VERSION=\"(.+)\"", res).group(1).replace(' ', '').replace(')', '').replace('(', '-')
            pkg_version = ksl_info.get("version")
            url = ksl_info.get('url').format(f"{name}-{os_version}", pkg_version)

            Runcmd.sendcmd(f"wget {url} --no-check-certificate", workspace=f"{self.__ROOT_PATH}/KSL/rpm")
            Runcmd.sendcmd("rpm -e boostkit-ksl", check=False)
            Runcmd.sendcmd("rpm -ivh rpm/*.rpm", workspace=f"{self.__ROOT_PATH}/KSL")

    def __install_hyperscan_dep(self):
        self.__install_ksl()

        Runcmd.sendcmd("rm -rf ./Hyperscan", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd(f"mkdir -p Hyperscan/resource", workspace=f"{self.__ROOT_PATH}")

        info = self.__get_element_text("Hyperscan")

        with self.__process("安装ragel"):
            download = info.get("ragel")
            bag = info.get("ragel").split('/')[-1]

            Runcmd.sendcmd(f"wget {download} --no-check-certificate", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd(f"tar -zxf {bag}", workspace=f"{self.__ROOT_PATH}/Hyperscan")

            dir = Runcmd.sendcmd(f"ls | grep ragel | grep -v tar", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd(f"./configure", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")
            Runcmd.sendcmd(f"make -j && make install", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")
            Runcmd.sendcmd(f"ragel -v")

        with self.__process("安装boost"):
            download = info.get("boost")
            bag = info.get("boost").split('/')[-1]

            Runcmd.sendcmd(f"wget {download} --no-check-certificate", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd(f"tar -zxf {bag}", workspace=f"{self.__ROOT_PATH}/Hyperscan")

        with self.__process("安装pcre"):
            download = info.get("pcre")
            bag = info.get("pcre").split('/')[-1]

            Runcmd.sendcmd(f"wget {download} --no-check-certificate", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd(f"tar -zxf {bag}", workspace=f"{self.__ROOT_PATH}/Hyperscan")

        with self.__process("安装yum依赖包"):
            Runcmd.sendcmd("yum install -y sqlite sqlite-devel")
            stdout = Runcmd.sendcmd("pkg-config --libs sqlite3")
            assert "-lsqlite3" in stdout, "安装sqlite失败"
            Runcmd.sendcmd("yum install -y cmake make gcc gcc-c++")

        with self.__process("下载测试集"):
            Runcmd.sendcmd("wget https://cdrdv2.intel.com/v1/dl/getContent/739375 --no-check-certificate",
                           workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd("unzip 739375 && mv '[Hyperscan] hsbench-samples' hsbench-samples",
                           workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd(f"cp ./2_suricata_rule_hs_9.txt {self.__ROOT_PATH}/Hyperscan/hsbench-samples/pcres",
                           workspace=f"{self.__ROOT_PATH}/resources/hsbench-samples")

    def __install_hyperscan(self):
        self.__install_hyperscan_dep()

        info = self.__get_element_text("Hyperscan")

        with self.__process("安装Hyperscan"):
            stdout = Runcmd.sendcmd("lscpu | grep Architecture")
            platform = "x86" if "x86" in stdout else "arm"
            download = info.get(f"code_{platform}")
            branch = info.get(f"branch_{platform}")
            dir = download.split('/')[-1].split('.')[0]

            res = Runcmd.sendcmd("rpm -qa | grep boostkit-ksl")
            ksl_version = re.search("boostkit-ksl-(\d+.\d+.\d+)", res).group(1)
            if platform == "arm" and check_version(ksl_version, "2.4.0"):
                Runcmd.sendcmd(f"git clone {download} -b khsel", workspace=f"{self.__ROOT_PATH}/Hyperscan")
                Runcmd.sendcmd("cp hyperscan/khsel.patch ./", workspace=f"{self.__ROOT_PATH}/Hyperscan")
                Runcmd.sendcmd(f"git checkout {branch}", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")
                Runcmd.sendcmd(f"mv ../khsel.patch ./", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")
                Runcmd.sendcmd(f"git apply khsel.patch", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")
            else:
                Runcmd.sendcmd(f"git clone {download} -b {branch}", workspace=f"{self.__ROOT_PATH}/Hyperscan")

            boost_path = Runcmd.sendcmd("ls | grep boost | grep -v tar", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            boost_path = f"{self.__ROOT_PATH}/Hyperscan/{boost_path}"
            Runcmd.sendcmd(f"ln -s {boost_path}/boost include/boost", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")

            pcre_path = Runcmd.sendcmd("ls | grep pcre | grep -v tar", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            Runcmd.sendcmd(f"cp -rf ../{pcre_path} ./pcre", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")

            stdout = Runcmd.sendcmd("cmake --version | grep version", workspace=f"{self.__ROOT_PATH}/Hyperscan")
            version = stdout.split()[-1]
            if check_version(version, "2.8.0", op='<'):
                Runcmd.sendcmd(
                    "sed -i 's/CMAKE_POLICY(SET CMP0026 OLD)/#CMAKE_POLICY(SET CMP0026 OLD)/g' CMakeLists.txt",
                    workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}/pcre")

            Runcmd.sendcmd("mkdir -p build", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}")
            Runcmd.sendcmd("cmake .. && make -j", workspace=f"{self.__ROOT_PATH}/Hyperscan/{dir}/build")

    def __install_compress_decompress_tools(self):
        Runcmd.sendcmd("rm -rf ZIP", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd("mkdir ZIP", workspace=f"{self.__ROOT_PATH}")

        with self.__process("安装软算测试工具lzbench"):
            Runcmd.sendcmd("git clone https://gitee.com/kunpeng_compute/lzbench.git --depth=1",
                           workspace=f"{self.__ROOT_PATH}/ZIP")
            Runcmd.sendcmd("make -j", workspace=f"{self.__ROOT_PATH}/ZIP/lzbench")

        if "KAE" in str(self.__function_dict.keys()) or "QAT" in str(self.__function_dict.keys()):
            with self.__process("安装带宽测试工具"):
                Runcmd.sendcmd(f"make platform='{self.__platform}'",
                               workspace=f"{self.__ROOT_PATH}/resources/bandwidth")
                Runcmd.sendcmd(f"cp ./bin/bandwidth {self.__ROOT_PATH}/ZIP",
                               workspace=f"{self.__ROOT_PATH}/resources/bandwidth")
                Runcmd.sendcmd("make clean", workspace=f"{self.__ROOT_PATH}/resources/bandwidth")

    def __install_kae_dep(self):
        with self.__process("安装KAE相关依赖"):
            Runcmd.sendcmd(
                "yum install -y make kernel-devel libtool numactl-devel openssl-devel chrpath lz4-devel zstd-devel zlib-devel")

    def __install_kae(self):
        version = Runcmd.sendcmd("openssl version | awk '{print $2}'")
        if check_version(version, "1.*", "="):
            engine_path = "/usr/local/lib/engines-1.1/"
            component = "engine"
        elif check_version(version, "3.*", "="):
            engine_path = "/usr/local/lib/engines-3.0/"
            component = "engine3"
        else:
            assert False, f"unsupport openssl version: {version}"

        self.__install_kae_dep()

        info = self.__get_element_text("KAE")
        Runcmd.sendcmd("rm -rf ./KAE", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd("mkdir KAE", workspace=f"{self.__ROOT_PATH}")

        with self.__process("下载编译KAE源码"):
            download = info.get("kae_code")
            branch = info.get("kae_code_tag")
            dir = download.split('/')[-1].split('.')[0]

            Runcmd.sendcmd(f"git clone {download} -b {branch} --depth=1", workspace=f"{self.__ROOT_PATH}/KAE")
            Runcmd.sendcmd("bash build.sh cleanup", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")
            Runcmd.sendcmd("bash build.sh driver", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")
            Runcmd.sendcmd("bash build.sh uadk", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")
            Runcmd.sendcmd(f"bash build.sh {component}", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")
            Runcmd.sendcmd("bash build.sh zlib", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")

            if "Kunpeng 920 V200" == self.__platform:
                Runcmd.sendcmd("bash build.sh lz4", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")
                Runcmd.sendcmd("bash build.sh zstd", workspace=f"{self.__ROOT_PATH}/KAE/{dir}")

        with self.__process("确认KAE模块使能"):
            res = Runcmd.sendcmd("ls /sys/class/uacce", check=False)
            if not res:
                Runcmd.sendcmd("rmmod hisi_zip && rmmod hisi_sec2 && rmmod hisi_hpre")
                Runcmd.sendcmd("inmod hisi_hpre && inmod hisi_sec2 && inmod hisi_zip")
            Runcmd.sendcmd("ls /sys/class/uacce")
            Runcmd.sendcmd("ls /usr/local/lib/libwd*")

            res = Runcmd.sendcmd("ls /usr/local/kaezip/lib", check=False)
            assert "kaezip" in res, "没有找到kaezip相关动态库"
            if "Kunpeng 920 V200" == self.__platform:
                res = Runcmd.sendcmd("ls /usr/local/kaelz4/lib", check=False)
                assert "kaelz4" in res, "没有找到kaelz4相关动态库"
                res = Runcmd.sendcmd("ls /usr/local/kaezstd/lib", check=False)
                assert "kaezstd" in res, "没有找到kaezstd相关动态库"

            res = Runcmd.sendcmd(f"ls {engine_path}", check=False)
            assert "kae.so" in res, "没有找到engine相关动态库"

            if not self.__chech_env_in_profile("OPENSSL_ENGINES", engine_path):
                Runcmd.sendcmd(f"echo 'export OPENSSL_ENGINES={engine_path}:$OPENSSL_ENGINES' >> /etc/profile")

            print("成功安装KAE, 已经添加必要环境变量, 执行source /etc/profile使能")

        self.__install_compress_decompress_tools()

    def __install_libgcrypt_dep(self):
        with self.__process("安装libgcrypt相关依赖"):
            Runcmd.sendcmd("yum install -y texinfo transfig hwloc hwloc-devel autoconf automake")

    def __install_libgcrypt(self):
        self.__install_libgcrypt_dep()

        gpg_info = Runcmd.sendcmd("find /usr/local/lib -name '*libgpg-error.so*'")
        if "libgpg-error.so" in gpg_info:
            print("已经安装了libgpg-error，不用再安装了")
            return

        Runcmd.sendcmd("rm -rf libgpg", workspace=f"{self.__ROOT_PATH}")
        with self.__process("安装libgcrypt"):
            Runcmd.sendcmd(f"unzip libgpg-error-1.51.zip -d {self.__ROOT_PATH}/libgpg",
                           workspace=f"{self.__ROOT_PATH}/resources/libgcrypt")
            Runcmd.sendcmd("chmod 777 autogen.sh; ./autogen.sh",
                           workspace=f"{self.__ROOT_PATH}/libgpg/libgpg-error-1.51")
            Runcmd.sendcmd("chmod 777 configure; ./configure --enable-maintainer-mode",
                           workspace=f"{self.__ROOT_PATH}/libgpg/libgpg-error-1.51")
            Runcmd.sendcmd("make -j; make install", workspace=f"{self.__ROOT_PATH}/libgpg/libgpg-error-1.51")

            if not self.__chech_env_in_profile("LD_LIBRARY_PATH", "/usr/local/lib"):
                Runcmd.sendcmd("echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> /etc/profile")

    def __install_qat_dep(self):
        with self.__process("安装QAT依赖包"):
            Runcmd.sendcmd("yum install -y systemd-devel pciutils libudev-devel readline-devel libxml2-devel "
                           "boost-devel elfutils-libelf-devel python3 libnl3-devel kernel-devel-$(uname -r) "
                           "gcc gcc-c++ yasm nasm zlib openssl-devel zlib-devel make")

    def __install_qat(self):
        self.__install_qat_dep()

        Runcmd.sendcmd(f"rm -rf ./QAT", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd("mkdir -p QAT/qat_driver", workspace=f"{self.__ROOT_PATH}")

        info = self.__get_element_text("QAT")

        with self.__process("安装部署QAT驱动"):
            download = info.get("driver")
            bag = download.split('/')[-1]
            decompresser = "unzip" if "zip" in bag else "tar -xf"
            qat_hw_root = f"{self.__ROOT_PATH}/QAT/qat_driver"

            os.putenv("ICP_ROOT", qat_hw_root)
            Runcmd.sendcmd(f"wget {download} --no-check-certificate", workspace=f"{self.__ROOT_PATH}/QAT/qat_driver")
            Runcmd.sendcmd(f"{decompresser} {bag}", workspace=f"{self.__ROOT_PATH}/QAT/qat_driver")
            Runcmd.sendcmd("./configure", workspace=f"{self.__ROOT_PATH}/QAT/qat_driver")
            Runcmd.sendcmd("make && make install", workspace=f"{self.__ROOT_PATH}/QAT/qat_driver")

            Runcmd.sendcmd("service qat_service status && service qat_service restart")

        with self.__process("安装部署QAT引擎"):
            download = info.get("code_engine")
            branch = info.get("branch_engine")
            dir = download.split('/')[-1].split('.')[0]

            Runcmd.sendcmd(f"git clone {download} -b {branch} --depth=1", workspace=f"{self.__ROOT_PATH}/QAT")
            Runcmd.sendcmd(f"./autogen.sh && ./configure --with-qat_hw-dir={qat_hw_root}",
                           workspace=f"{self.__ROOT_PATH}/QAT/{dir}")
            Runcmd.sendcmd(f"make && make install", workspace=f"{self.__ROOT_PATH}/QAT/{dir}")

        with self.__process("安装部署QATzip"):
            download = info.get("code_zip")
            branch = info.get("branch_zip")
            dir = download.split('/')[-1].split('.')[0]

            Runcmd.sendcmd(f"git clone {download} -b {branch} --depth=1", workspace=f"{self.__ROOT_PATH}/QAT")
            Runcmd.sendcmd(f"./autogen.sh && ./configure --with-ICP_ROOT={qat_hw_root}",
                           workspace=f"{self.__ROOT_PATH}/QAT/{dir}")
            Runcmd.sendcmd("make clean && make all install", workspace=f"{self.__ROOT_PATH}/QAT/{dir}")

            res = Runcmd.sendcmd("ls /usr/local/lib")
            assert "qatzip.so" in res, "没有找到qatzip动态库"

        self.__install_compress_decompress_tools()

    def __install_hct_dep(self):
        with self.__process("安装HCT依赖"):
            Runcmd.sendcmd(
                "yum install -y numactl libuuid-devel kernel-`uname -r` kernel-devel-`uname -r` python3-unversioned-command")

    def __install_hct(self):
        self.__install_hct_dep()

        info = self.__get_element_text("HCT")
        Runcmd.sendcmd("rm -rf HCT", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd("mkdir -p HCT/build", workspace=f"{self.__ROOT_PATH}")

        with self.__process("安装HCT"):
            download = info.get("devkit")
            version = info.get("version")
            dir = download.split('/')[-1].split('.')[0]

            Runcmd.sendcmd(f"git clone {download} -n --filter=blob:none", workspace=f"{self.__ROOT_PATH}/HCT")
            Runcmd.sendcmd(f"git restore --staged hct/pkg/{version} && git restore hct/pkg/{version}",
                           workspace=f"{self.__ROOT_PATH}/HCT/{dir}")
            Runcmd.sendcmd(f"rpm -ivh --nodeps hct-*.rpm", workspace=f"{self.__ROOT_PATH}/HCT/{dir}/hct/pkg/{version}",
                           check=False)
            Runcmd.sendcmd(f"cp ./Makefile {self.__ROOT_PATH}/HCT/build",
                           workspace=f"{self.__ROOT_PATH}/HCT/{dir}/hct/pkg/{version}")
            Runcmd.sendcmd("make && make install", workspace=f"{self.__ROOT_PATH}/HCT/build")
            Runcmd.sendcmd("modprobe hct && /opt/hygon/hct/hct/script/hctconfig start")

    def __install_kqmalloc_dep(self):
        with self.__process("安装kqmalloc编译依赖"):
            Runcmd.sendcmd("yum install -y autoconf gcc gcc-c++")

    def __install_kqmalloc(self):
        self.__install_kqmalloc_dep()

        Runcmd.sendcmd(f"rm -rf ./KQMalloc", workspace=f"{self.__ROOT_PATH}")
        Runcmd.sendcmd(f"mkdir -p KQMalloc/resource", workspace=f"{self.__ROOT_PATH}")

        with self.__process("安装kqmalloc"):
            self.__install_ksl()
            res = Runcmd.sendcmd("rpm -qa | grep boostkit-ksl")
            ksl_version = re.search("boostkit-ksl-(\d+.\d+.\d+)", res).group(1)
            assert check_version(ksl_version, "2.4.0"), "ksl版本过低，请指定2.4.0以上版本"

        with self.__process("安装tcmalloc"):
            Runcmd.sendcmd("yum install -y jemalloc-devel jemalloc")

        with self.__process("编译安装tcmalloc"):
            tcmalloc_info = self.__get_element_text("Tcmalloc")
            download = tcmalloc_info.get("code")
            branch = tcmalloc_info.get("branch")
            dir = download.split('/')[-1].split('.')[0]

            Runcmd.sendcmd("rm -rf /opt/tcmalloc")
            Runcmd.sendcmd(f"git clone {download} -b {branch} --depth=1",
                           workspace=f"{self.__ROOT_PATH}/KQMalloc/resource")
            Runcmd.sendcmd(
                './autogen.sh && ./configure --prefix=/opt/tcmalloc CFLAGS=" -O3 -march=armv8.2-a " CXXFLAGS=" -O3 -march=armv8.2-a "',
                workspace=f"{self.__ROOT_PATH}/KQMalloc/resource/{dir}")
            Runcmd.sendcmd("make -j && make install", workspace=f"{self.__ROOT_PATH}/KQMalloc/resource/{dir}")

        with self.__process("安装KQMalloc benchmark"):
            Runcmd.sendcmd(f"cp -r ./* {self.__ROOT_PATH}/KQMalloc/resource",
                           workspace=f"{self.__ROOT_PATH}/resources/benchmark")
            if check_version(ksl_version, "2.5.0", "<"):
                Runcmd.sendcmd("sed -i 's/-lkqmalloc/-lkqmallocmt/g' Makefile",
                               workspace=f"{self.__ROOT_PATH}/KQMalloc/resource")

            Runcmd.sendcmd("make", workspace=f"{self.__ROOT_PATH}/KQMalloc/resource")
            Runcmd.sendcmd(f"mv ./bin_* {self.__ROOT_PATH}/KQMalloc", workspace=f"{self.__ROOT_PATH}/KQMalloc/resource")

    def __init_func_dict(self):
        self.__function_dict["Hyperscan"] = self.__install_hyperscan
        self.__function_dict["Libgcrypt"] = self.__install_libgcrypt
        res = Runcmd.sendcmd("lscpu | grep 'BIOS Model name:'")
        if "Kunpeng" in res:
            self.__function_dict["KAE"] = self.__install_kae
            self.__function_dict["KQMalloc"] = self.__install_kqmalloc
        elif "INTEL" in res:
            self.__function_dict["QAT"] = self.__install_qat
        elif "Hygon" in res:
            self.__function_dict["HCT"] = self.__install_hct
        else:
            self.__function_dict["SOFT_COMPRESS"] = self.__install_compress_decompress_tools

    def get_support(self):
        return ' '.join(self.__function_dict.keys())

    def install(self, component):
        self.__check_env()

        if "ALL" == component:
            for func in self.__function_dict.values():
                try:
                    func()
                except Exception as e:
                    print(e)
                    if not args.ignore:
                        raise e
        else:
            func = self.__function_dict.get(component)
            if func:
                func()
            else:
                raise "没有找到安装方法"


if __name__ == '__main__':
    installer = Installer('version.xml')
    supports = installer.get_support()

    parser = argparse.ArgumentParser()
    parser.add_argument("--component", type=str, help=f"support component eg. [{supports}], default ALL", default='ALL')
    parser.add_argument("-q", '--quiet', action='store_true', help="print quiet")
    parser.add_argument('--ignore', action='store_true',
                        help="ignore error for each installing component while component is ALL")
    parser.add_argument("-i", '--info', action='store_true')
    args = parser.parse_args()
    quiet = args.quiet
    info_t = args.info
    if info_t:
        print(supports)
        exit(0)

    installer.install(args.component)
