"""
基础命令类 - 提供所有命令的通用功能
"""


class BaseCommand:
    """命令基类 - 定义命令接口"""
    
    def __init__(self):
        """初始化基础命令"""
        pass
    
    def execute(self, *args, **kwargs) -> bool:
        """
        执行命令（子类需要实现）
        
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        raise NotImplementedError("子类必须实现execute方法")
