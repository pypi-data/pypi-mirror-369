"""
EasyA2A - 快速将LangChain Agent包装为A2A协议服务

这个库提供了简单而强大的工具，让你能够快速将现有的LangChain Agent
包装成符合A2A协议的服务，支持自动配置、智能包装和一键启动。

主要功能：
- 🚀 一键包装LangChain Agent
- 🔧 自动A2A协议适配
- ⚙️ 灵活的配置管理
- 🛠️ 深度LangChain集成
- 📡 自动Agent Card生成

使用示例：
    from easya2a import A2AAgentWrapper

    # 你的LangChain Agent
    class MyAgent:
        def chat(self, message: str) -> str:
            return "response"

    # 三步式快速包装
    A2AAgentWrapper.set_up(MyAgent(), "My Agent", "智能助手") \
                   .add_skill("chat", "聊天", examples=["你好"]) \
                   .run_a2a(port=10010)
"""

from .config.agent_config import AgentConfig, AgentSkillConfig, AgentCapabilityConfig, ConfigBuilder, SkillTemplates
from .core.wrapper import A2AWrapper, wrap_agent, quick_serve
from .core.agent_wrapper import A2AAgentWrapper
from .core.decorators import a2a_agent, a2a_skill, a2a_tool
from .core.executor import LangChainAgentExecutor
from .core.server import A2AServer

__version__ = "2.0.0"
__author__ = "whillhill"
__email__ = "ooooofish@126.com"
__license__ = "MIT"
__url__ = "https://github.com/whillhill/easya2a"

# 导出主要接口
__all__ = [
    # 新的三步式API（推荐使用）
    "A2AAgentWrapper",

    # 配置类
    "AgentConfig",
    "AgentSkillConfig",
    "AgentCapabilityConfig",
    "ConfigBuilder",
    "SkillTemplates",

    # 核心包装器（向后兼容）
    "A2AWrapper",
    "wrap_agent",
    "quick_serve",

    # 装饰器
    "a2a_agent",
    "a2a_skill",
    "a2a_tool",

    # 执行器
    "LangChainAgentExecutor",

    # 服务器
    "A2AServer",
]

# 版本信息
VERSION = __version__
