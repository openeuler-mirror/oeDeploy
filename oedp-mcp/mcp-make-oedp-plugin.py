from mcp.server.fastmcp import FastMCP
import requests
import subprocess
import os

DEFAULT_DIR = "~/.oedp/"
DEVELOP_GUIDE_PATH = "~/.oedp/mcp/DevelopGuide.md"

# Initialize FastMCP server
mcp = FastMCP("编写一个oeDeploy插件/oedp插件", log_level="ERROR")

@mcp.tool()
async def make_plugin_auto(plugin: str, parent_dir: str) -> str:
    """编写一个插件

    Args:
        plugin: oeDeploy插件名称,表示安装的软件或者需要执行的操作简称
        parent_dir: 插件初始化的路径,如果路径不存在,则创建;如果用户未指定,默认为~/.oedp/
    Returns:
        str: 下一步需要执行的指令
    """
    
    # 检查父路径是否存在并转换为绝对路径
    if parent_dir and os.path.exists(parent_dir):
        parent_dir = os.path.abspath(os.path.expanduser(parent_dir))
    else:
        parent_dir = os.path.abspath(os.path.expanduser(DEFAULT_DIR))
    
    develop_guide_path = os.path.abspath(os.path.expanduser(DEVELOP_GUIDE_PATH))
    
    return f"""编写一个oeDeploy插件分为多个步骤:
1. (重要!)仔细阅读oeDeploy插件的开发文档{develop_guide_path}
2. 根据用户对eDeploy插件功能的详细描述,完成对oeDeploy插件的开发
3. 开发完成后,用指定方式打包成tar.gz到{parent_dir}目录下(如果有同名文件则强制覆盖)
4. 再调用`oedp info -p {parent_dir}/{plugin}`进行测试
5. 测试通过后,不用执行oedp部署操作
"""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')