from mcp.server.fastmcp import FastMCP
import subprocess
import os

# 全局配置
DEFAULT_DIR = "~/.oedp/"
DOWNLOAD_TIMEOUT = 300  # 默认超时时间(秒)
DOWNLOAD_RETRIES = 60    # 默认重试次数

# Initialize FastMCP server
mcp = FastMCP("安装部署命令行工具oedp调用方法", log_level="ERROR")

async def _download_file(url: str, save_path: str, timeout: int = None, max_retries: int = None) -> str:
    """下载文件并支持断点续传
    
    Args:
        url: 下载URL
        save_path: 文件保存路径
        timeout: 超时时间(秒)，默认使用全局配置
        max_retries: 最大重试次数，默认使用全局配置
        
    Returns:
        str: 成功返回"[Success]"，失败返回错误信息
    """
    timeout = timeout or DOWNLOAD_TIMEOUT
    max_retries = max_retries or DOWNLOAD_RETRIES
    temp_path = save_path + ".download"
    
    # 构建curl命令
    curl_cmd = [
        "curl",
        "-fL",  # 失败时不显示HTML错误页面，跟随重定向
        "-C", "-",  # 自动断点续传
        "--max-time", str(timeout),  # 设置超时时间
        "--retry", str(max_retries),  # 设置重试次数
        "--retry-delay", "2",  # 设置重试间隔(秒)
        "--output", temp_path,  # 输出到临时文件
        url
    ]
    
    for attempt in range(max_retries):
        try:
            # 执行curl命令
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 下载完成后重命名临时文件
                os.rename(temp_path, save_path)
                return "[Success]"
            else:
                if attempt == max_retries - 1:
                    return f"[Fail]Download failed after {max_retries} attempts: {result.stderr}"
                
        except subprocess.CalledProcessError as e:
            if attempt == max_retries - 1:
                return f"[Fail]Download failed after {max_retries} attempts: {str(e)}"
        except Exception as e:
            if attempt == max_retries - 1:
                return f"[Fail]Download failed after {max_retries} attempts: {str(e)}"
    
    return f"[Fail]Download failed after {max_retries} attempts"

def _validate_project_structure(project: str) -> str:
    """校验项目目录结构
    
    Args:
        project: 项目目录路径
    Returns:
        str: 空字符串表示校验通过,否则返回错误信息
    """
    required_files = ["config.yaml", "main.yaml", "workspace"]
    abs_project = os.path.abspath(os.path.expanduser(project))
    for f in required_files:
        path = os.path.join(abs_project, f)
        if not os.path.exists(path):
            return f"Missing required file/directory: {f}"
    return ""

def _check_oedp_installed() -> str:
    """检查oedp是否安装
    
    Returns:
        str: 空字符串表示已安装,否则返回错误信息
    """
    version_check = subprocess.run(
        ["oedp", "-v"],
        capture_output=True,
        text=True
    )
    if version_check.returncode != 0:
        return "oedp is not installed or not in PATH"
    return ""

async def _extract_plugin(tar_path: str, parent_dir: str) -> str:
    """解压插件包到目标目录
    
    Args:
        tar_path: tar.gz文件路径
        parent_dir: 目标父目录
    Returns:
        str: 成功或错误信息
    """
    try:
        plugin_name = os.path.basename(tar_path).replace(".tar.gz", "")
        plugin_dir = os.path.join(parent_dir, plugin_name)
        
        # 强制删除已存在的目录
        if os.path.exists(plugin_dir):
            import shutil
            shutil.rmtree(plugin_dir)
        
        # 解压到目标路径
        result = subprocess.run(
            ["tar", "zxvf", tar_path, "-C", parent_dir],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return "[Success]"
        return f"[Fail]Extraction failed: {result.stderr}"

    except subprocess.CalledProcessError as e:
        return f"[Fail]Tar command failed: {str(e)}"
    except OSError as e:
        return f"[Fail]Directory operation failed: {str(e)}"
    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def install_oedp() -> str:
    """下载并安装noarch架构的oedp软件包(oeDeploy的命令行工具)
    """
    try:
        # 构建下载URL
        url = "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/"
        package_name = "oedp-1.0.2-1.oe2503.noarch.rpm"
        temp_file = os.path.abspath(f"/tmp/{package_name}")
        
        # 使用新的下载函数
        download_result = await _download_file(url + package_name, temp_file)
        if download_result != "[Success]":
            return download_result
            
        # 安装RPM包
        result = subprocess.run(
            ["sudo", "yum", "install", "-y", temp_file],
            capture_output=True,
            text=True
        )
        
        # 清理临时文件
        os.remove(temp_file)
        
        if result.returncode == 0:
            return "[Success]"
        else:
            return f"[Fail]Installation failed: {result.stderr}"
            
    except subprocess.CalledProcessError as e:
        return f"[Fail]Yum command failed: {str(e)}"
    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def remove_oedp() -> str:
    """卸载oedp软件包(oeDeploy的命令行工具)
    """
    try:
        # 执行yum remove命令
        result = subprocess.run(
            ["sudo", "yum", "remove", "-y", "oedp"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return "[Success]"
        else:
            return f"[Fail]Removal failed: {result.stderr}"
            
    except subprocess.CalledProcessError as e:
        return f"[Fail]Yum command failed: {str(e)}"
    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def oedp_init_plugin(plugin: str, parent_dir: str) -> str:
    """获取的oeDeploy插件(又称oedp插件),并初始化

    Args:
        plugin: oeDeploy插件名称或.tar.gz文件路径/名称
        parent_dir: 插件初始化的路径,如果路径不存在,则创建
    """
    try:
        # 检查父路径是否存在并转换为绝对路径
        if parent_dir and os.path.exists(parent_dir):
            parent_dir = os.path.abspath(os.path.expanduser(parent_dir))
        else:
            parent_dir = os.path.abspath(os.path.expanduser(DEFAULT_DIR))
        
        # 转换为绝对路径并确保以/结尾
        parent_dir = os.path.abspath(os.path.expanduser(parent_dir))
        parent_dir = parent_dir if parent_dir.endswith("/") else parent_dir + "/"
        os.makedirs(parent_dir, exist_ok=True)
        
        # 情况1：plugin是.tar.gz文件路径
        if plugin.endswith(".tar.gz"):
            abs_path = os.path.abspath(os.path.expanduser(plugin))
            if os.path.exists(abs_path):
                return await _extract_plugin(abs_path, parent_dir)
            return f"[Fail]tar.gz file not found: {abs_path}"
        
        # 情况2：plugin是.tar.gz文件名
        if plugin.endswith(".tar.gz"):
            # 先在parent_dir目录查找
            local_path = os.path.join(parent_dir, plugin)
            if os.path.exists(local_path):
                return await _extract_plugin(local_path, parent_dir)
            
            # 尝试从网络下载
            base_url = "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins"
            url = f"{base_url}/{plugin}"
            download_path = os.path.join(parent_dir, plugin)
            
            download_result = await _download_file(url, download_path)
            if download_result != "[Success]":
                return download_result
                
            return await _extract_plugin(download_path, parent_dir)
        
        # 情况3：plugin是插件名称
        plugin_dir = os.path.join(parent_dir, plugin)
        package_name = f"{plugin}.tar.gz"
        
        # 优先尝试从本地获取插件包
        local_package = os.path.join(parent_dir, package_name)
        if os.path.exists(local_package):
            return await _extract_plugin(local_package, parent_dir)
        
        # 尝试从网络下载
        base_url = "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins"
        url = f"{base_url}/{package_name}"
        download_path = os.path.join(parent_dir, package_name)
        
        download_result = await _download_file(url, download_path)
        if download_result != "[Success]":
            # 所有获取方式都失败,检查现有目录
            if os.path.exists(plugin_dir):
                validation_result = _validate_project_structure(plugin_dir)
                if not validation_result:
                    return "[Success] (Using existing valid plugin directory)"
                return f"[Fail]Existing directory is invalid: {validation_result}"
            return download_result
            
        return await _extract_plugin(download_path, parent_dir)
        
    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def oedp_info_plugin(project: str) -> str:
    """查询oeDeploy插件(又称oedp插件)信息,仅在明确指定project路径时触发

    Args:
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    
    # 校验项目目录结构
    abs_project = os.path.abspath(os.path.expanduser(project))
    validation_result = _validate_project_structure(abs_project)
    if validation_result:
        return f"[Fail]{validation_result}"
    
    # 检查oedp是否安装
    oedp_check_result = _check_oedp_installed()
    if oedp_check_result:
        return f"[Fail]{oedp_check_result}"
    
    # 执行安装命令
    try:
        result = subprocess.run(
            ["oedp", "info", "-p", abs_project],
            capture_output=True,
            text=True
        )
        
        log_text = result.stdout + "\n" + result.stderr
        
        if result.returncode == 0:
            return "[Success]" + "\n" + log_text
        else:
            return f"[Fail]Installation failed" + "\n" + log_text
            
    except subprocess.CalledProcessError as e:
        return f"[Fail]Command execution failed: {str(e)}"
    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def oedp_setup_plugin(operation: str, project: str) -> str:
    """配置oeDeploy插件(又称oedp插件): 根据operation,修改oeDeploy插件的配置文件{project}/config.yaml

    Args:
        operation: 用户对oeDeploy插件config.yaml的修改说明(人类描述语言)
        project: oeDeploy插件的项目目录,其中必定有config.yaml,main.yaml,workspace/
    """
    
    # 校验项目目录结构
    abs_project = os.path.abspath(os.path.expanduser(project))
    validation_result = _validate_project_structure(abs_project)
    if validation_result:
        return f"[Fail]{validation_result}"
    
    return "请帮我执行: { " + f"阅读{abs_project}/config.yaml并检查参数是否正确,如果不正确请修改" + " }"

@mcp.tool()
async def oedp_run_action_plugin(action: str, project: str) -> str:
    """运行oeDeploy插件(又称oedp插件)的特定操作action,仅在明确指定project路径时触发

    Args:
        action: oeDeploy插件的一个操作名称
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    try:
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = _validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"
        
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
        if oedp_check_result:
            return f"[Fail]{oedp_check_result}"
        
        return "请帮我执行命令行: { " + f"oedp run {action} -p {abs_project}" + " }"

    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def oedp_run_install_plugin(project: str) -> str:
    """运行oeDeploy插件(又称oedp插件)的安装部署流程,仅在明确指定project路径时触发

    Args:
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    try:
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = _validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"
        
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
        if oedp_check_result:
            return f"[Fail]{oedp_check_result}"
        
        return "请帮我执行命令行: { " + f"oedp run install -p {abs_project}" + " }"

    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def oedp_run_uninstall_plugin(project: str) -> str:
    """运行oeDeploy插件(又称oedp插件)的卸载流程,仅在明确指定project路径时触发

    Args:
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    try:
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = _validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"
        
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
        if oedp_check_result:
            return f"[Fail]{oedp_check_result}"
        
        return "请帮我执行命令行: { " + f"oedp run uninstall -p {abs_project}" + " }"

    except Exception as e:
        return f"[Fail]Unexpected error: {str(e)}"

@mcp.tool()
async def oedp_install_software_one_click(software: str, operation: str) -> str:
    """用oeDeploy一键执行特定软件的部署流程(install),仅在用户指定[oeDeploy]与[一键部署]时触发
    
    Args:
        software: 软件名称,可以等价于插件名称
        operation: 用户对部署软件参数的描述,等价于对oeDeploy插件config.yaml的修改说明(人类描述语言)
    Returns:
        str: 下一步需要执行的指令
    """
    
    # 检查oedp是否安装
    oedp_check_result = _check_oedp_installed()
    if oedp_check_result:
        return f"[Fail]{oedp_check_result}"
    
    parent_dir = os.path.abspath(os.path.expanduser(DEFAULT_DIR))
    
    return "请帮我执行: {" + f"""
1. 调用oedp_init_plugin方法,将指定的oeDeploy插件[{software}]初始化到{parent_dir}目录
2. 根据用户的指令[{operation}],阅读{parent_dir}/{software}/config.yaml并检查参数是否正确,如果不正确请修改
3. 调用oedp_run_install_plugin方法,运行oeDeploy插件的安装部署流程 项目路径{parent_dir}/{software}
""" + "}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
