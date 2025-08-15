"""
A2A包装器

提供核心的A2A包装功能，将任意Agent包装为A2A协议服务。
"""

import logging
from typing import Any, Optional

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentProvider, AgentSkill

from ..config.agent_config import AgentConfig
from .executor import ExecutorFactory, BaseAgentExecutor

logger = logging.getLogger(__name__)


class A2AWrapper:
    """
    A2A包装器
    
    将任意Agent包装为A2A协议服务的核心类。
    提供简单的接口来配置和启动A2A服务。
    """
    
    def __init__(self, agent: Any, config: AgentConfig):
        """
        初始化A2A包装器
        
        Args:
            agent: 要包装的Agent实例
            config: Agent配置
        """
        self.agent = agent
        self.config = config
        self.executor: Optional[BaseAgentExecutor] = None
        self.server_app: Optional[A2AStarletteApplication] = None
        
        logger.info(f"🎁 初始化A2A包装器: {config.name}")
        
        # 创建执行器
        self._create_executor()
        
        # 创建服务器应用
        self._create_server_app()
    
    def _create_executor(self):
        """创建Agent执行器"""
        self.executor = ExecutorFactory.create_executor(
            agent=self.agent,
            name=self.config.name,
            description=self.config.description,
            **self.config.langchain_config
        )
        logger.info(f"⚙️ Agent执行器创建成功: {type(self.executor).__name__}")
    
    def _create_server_app(self):
        """创建服务器应用"""
        # 创建Agent Card
        agent_card = self._create_agent_card()
        
        # 创建任务存储
        task_store = InMemoryTaskStore()
        
        # 创建请求处理器
        request_handler = DefaultRequestHandler(
            agent_executor=self.executor,
            task_store=task_store
        )
        
        # 创建A2A应用
        self.server_app = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
        
        logger.info("🌐 A2A服务器应用创建成功")
    
    def _create_agent_card(self) -> AgentCard:
        """创建Agent Card"""
        # 转换技能配置
        skills = []
        for skill_config in self.config.skills:
            skill = AgentSkill(
                id=skill_config.id,
                name=skill_config.name,
                description=skill_config.description,
                tags=skill_config.tags,
                examples=skill_config.examples
            )
            skills.append(skill)
        
        # 转换能力配置
        capabilities = AgentCapabilities(
            streaming=self.config.capabilities.streaming,
            push_notifications=self.config.capabilities.push_notifications,
            state_transition_history=self.config.capabilities.state_transition_history
        )
        
        # 创建提供商信息
        provider = AgentProvider(
            organization=self.config.provider_organization,
            url=self.config.provider_url
        )
        
        # 创建Agent Card
        agent_card = AgentCard(
            name=self.config.name,
            description=self.config.description,
            url=self.config.agent_url,  # 使用独立的agent_url
            version=self.config.version,
            provider=provider,
            capabilities=capabilities,
            default_input_modes=self.config.default_input_modes,
            default_output_modes=self.config.default_output_modes,
            skills=skills
        )
        
        logger.info(f"📋 Agent Card创建成功: {agent_card.name}")
        return agent_card
    
    def run(self, **uvicorn_kwargs):
        """
        启动A2A服务器
        
        Args:
            **uvicorn_kwargs: 传递给uvicorn的额外参数
        """
        import uvicorn
        
        # 默认uvicorn配置
        default_config = {
            "host": self.config.host,
            "port": self.config.port,
            "log_level": "info"
        }
        
        # 合并用户配置
        final_config = {**default_config, **uvicorn_kwargs}
        
        logger.info(f"🚀 启动A2A服务器: {self.config.name}")
        logger.info(f"🌐 服务地址: http://{final_config['host']}:{final_config['port']}")
        logger.info(f"📡 Agent Card: http://{final_config['host']}:{final_config['port']}/.well-known/agent-card.json")
        
        # 启动服务器
        uvicorn.run(
            self.server_app.build(),
            **final_config
        )
    
    def get_agent_card_url(self) -> str:
        """获取Agent Card URL"""
        return f"{self.config.agent_url}.well-known/agent-card.json"

    def get_rpc_url(self) -> str:
        """获取RPC端点URL"""
        return self.config.agent_url

    def get_server_url(self) -> str:
        """获取服务器URL（用于启动服务）"""
        return f"http://{self.config.host}:{self.config.port}/"
    
    def get_config(self) -> AgentConfig:
        """获取配置"""
        return self.config
    
    def get_executor(self) -> BaseAgentExecutor:
        """获取执行器"""
        return self.executor


# 便捷函数
def wrap_agent(agent: Any, name: str, description: str = "", **config_kwargs) -> A2AWrapper:
    """
    便捷函数：快速包装Agent
    
    Args:
        agent: 要包装的Agent
        name: Agent名称
        description: Agent描述
        **config_kwargs: 额外的配置参数
        
    Returns:
        A2A包装器实例
    """
    config = AgentConfig(
        name=name,
        description=description,
        **config_kwargs
    )
    
    return A2AWrapper(agent, config)


def quick_serve(agent: Any, name: str, port: int = 10010, **kwargs):
    """
    便捷函数：快速启动Agent服务
    
    Args:
        agent: 要包装的Agent
        name: Agent名称
        port: 服务端口
        **kwargs: 额外配置
    """
    wrapper = wrap_agent(agent, name, port=port, **kwargs)
    wrapper.run()


# 上下文管理器支持
class A2AService:
    """A2A服务上下文管理器"""
    
    def __init__(self, agent: Any, config: AgentConfig):
        self.wrapper = A2AWrapper(agent, config)
        self.server_process = None
    
    def __enter__(self):
        """进入上下文"""
        return self.wrapper
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        # 这里可以添加清理逻辑
        pass
    
    async def __aenter__(self):
        """异步进入上下文"""
        return self.wrapper
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文"""
        # 这里可以添加异步清理逻辑
        pass


# 批量包装支持
class MultiAgentWrapper:
    """多Agent包装器"""
    
    def __init__(self):
        self.agents = {}
        self.wrappers = {}
    
    def add_agent(self, name: str, agent: Any, config: AgentConfig):
        """添加Agent"""
        self.agents[name] = agent
        self.wrappers[name] = A2AWrapper(agent, config)
    
    def run_all(self, base_port: int = 10010):
        """启动所有Agent服务"""
        import threading
        import time
        
        threads = []
        for i, (name, wrapper) in enumerate(self.wrappers.items()):
            port = base_port + i
            wrapper.config.port = port
            
            def run_wrapper(w=wrapper):
                w.run()
            
            thread = threading.Thread(target=run_wrapper, daemon=True)
            thread.start()
            threads.append(thread)
            
            logger.info(f"🚀 启动Agent服务: {name} on port {port}")
            time.sleep(1)  # 避免端口冲突
        
        # 等待所有线程
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("🛑 停止所有Agent服务")
    
    def get_agent_urls(self) -> dict:
        """获取所有Agent的URL"""
        return {
            name: wrapper.get_rpc_url()
            for name, wrapper in self.wrappers.items()
        }
