"""
核心功能模块

提供A2A包装的核心功能：
- Agent包装器
- 装饰器
- 执行器
- 服务器启动
"""

from .wrapper import A2AWrapper
from .decorators import a2a_agent, a2a_skill, a2a_tool
from .executor import LangChainAgentExecutor, BaseAgentExecutor
from .server import A2AServer

__all__ = [
    "A2AWrapper",
    "a2a_agent",
    "a2a_skill", 
    "a2a_tool",
    "LangChainAgentExecutor",
    "BaseAgentExecutor",
    "A2AServer",
]
