"""
A2AAgentWrapper - 新的三步式API包装器

提供简洁的三步式API来包装Agent为A2A协议服务：
1. set_up() - 初始化必须参数
2. 链式配置方法 - 可选参数配置
3. run_a2a() - 启动A2A服务
"""

import logging
from typing import Any, List, Optional, Dict, Union

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentProvider, AgentSkill

from ..config.agent_config import AgentConfig, AgentSkillConfig, AgentCapabilityConfig
from .executor import ExecutorFactory, BaseAgentExecutor

logger = logging.getLogger(__name__)


class A2AAgentWrapper:
    """
    A2A Agent包装器 - 三步式API设计
    
    使用方式：
    1. wrapper = A2AAgentWrapper.set_up(agent, name, description)
    2. wrapper.add_skill().set_provider().enable_streaming()
    3. wrapper.run_a2a(port=10010)
    """
    
    def __init__(self, agent: Any, name: str, description: str):
        """
        内部初始化方法，不直接调用
        使用 A2AAgentWrapper.set_up() 来创建实例
        """
        self.agent = agent
        self.name = name
        self.description = description
        
        # 内部配置存储
        self._skills: List[AgentSkillConfig] = []
        self._provider_organization = "EasyA2A Agent Services"
        self._provider_url = ""
        self._version = "1.0.0"
        self._host = "0.0.0.0"
        self._agent_url = ""
        
        # 能力配置
        self._streaming = False
        self._push_notifications = True
        self._state_history = False
        self._multimodal = False
        
        # 输入输出模式
        self._input_modes = ["text", "text/plain", "application/json"]
        self._output_modes = ["text", "text/plain", "application/json"]
        
        # 内部状态
        self._executor: Optional[BaseAgentExecutor] = None
        self._server_app: Optional[A2AStarletteApplication] = None
        
        logger.info(f"🎁 A2AAgentWrapper初始化: {name}")
    
    @classmethod
    def set_up(cls, agent: Any, name: str, description: str) -> "A2AAgentWrapper":
        """
        第一步：初始化A2A Agent包装器
        
        Args:
            agent: 要包装的Agent实例
            name: Agent名称
            description: Agent描述
            
        Returns:
            A2AAgentWrapper实例，支持链式调用
            
        Example:
            wrapper = A2AAgentWrapper.set_up(my_agent, "天气助手", "智能天气查询服务")
        """
        return cls(agent, name, description)
    
    def add_skill(self, skill_id: str, name: str, description: str = "", 
                  examples: Optional[List[str]] = None, 
                  tags: Optional[List[str]] = None) -> "A2AAgentWrapper":
        """
        添加技能配置
        
        Args:
            skill_id: 技能唯一标识
            name: 技能名称
            description: 技能描述
            examples: 使用示例列表
            tags: 技能标签列表
            
        Returns:
            self，支持链式调用
        """
        skill = AgentSkillConfig(
            id=skill_id,
            name=name,
            description=description or f"{name}功能",
            examples=examples or [],
            tags=tags or []
        )
        self._skills.append(skill)
        logger.debug(f"添加技能: {name}")
        return self
    
    def set_provider(self, organization: str, url: str = "") -> "A2AAgentWrapper":
        """
        设置提供商信息
        
        Args:
            organization: 提供商组织名称
            url: 提供商网站URL
            
        Returns:
            self，支持链式调用
        """
        self._provider_organization = organization
        self._provider_url = url
        logger.debug(f"设置提供商: {organization}")
        return self
    
    def set_version(self, version: str) -> "A2AAgentWrapper":
        """
        设置Agent版本
        
        Args:
            version: 版本号
            
        Returns:
            self，支持链式调用
        """
        self._version = version
        logger.debug(f"设置版本: {version}")
        return self
    
    def enable_streaming(self) -> "A2AAgentWrapper":
        """
        启用流式响应
        
        Returns:
            self，支持链式调用
        """
        self._streaming = True
        logger.debug("启用流式响应")
        return self
    
    def enable_history(self) -> "A2AAgentWrapper":
        """
        启用状态历史记录
        
        Returns:
            self，支持链式调用
        """
        self._state_history = True
        logger.debug("启用状态历史")
        return self
    
    def enable_multimodal(self) -> "A2AAgentWrapper":
        """
        启用多模态支持
        
        Returns:
            self，支持链式调用
        """
        self._multimodal = True
        logger.debug("启用多模态")
        return self
    
    def set_input_modes(self, modes: List[str]) -> "A2AAgentWrapper":
        """
        设置输入模式
        
        Args:
            modes: 支持的输入模式列表
            
        Returns:
            self，支持链式调用
        """
        self._input_modes = modes
        logger.debug(f"设置输入模式: {modes}")
        return self
    
    def set_output_modes(self, modes: List[str]) -> "A2AAgentWrapper":
        """
        设置输出模式
        
        Args:
            modes: 支持的输出模式列表
            
        Returns:
            self，支持链式调用
        """
        self._output_modes = modes
        logger.debug(f"设置输出模式: {modes}")
        return self
    
    def _build_config(self, port: int, host: str) -> AgentConfig:
        """
        内部方法：构建AgentConfig对象
        
        Args:
            port: 服务端口
            host: 服务主机
            
        Returns:
            完整的AgentConfig对象
        """
        # 设置agent_url，如果没有明确设置则使用默认值
        if not self._agent_url:
            self._agent_url = f"http://localhost:{port}/"
        
        # 构建能力配置
        capabilities = AgentCapabilityConfig(
            streaming=self._streaming,
            push_notifications=self._push_notifications,
            state_transition_history=self._state_history,
            multimodal=self._multimodal
        )
        
        # 构建完整配置
        config = AgentConfig(
            name=self.name,
            description=self.description,
            version=self._version,
            host=host,
            port=port,
            agent_url=self._agent_url,
            provider_organization=self._provider_organization,
            provider_url=self._provider_url,
            capabilities=capabilities,
            default_input_modes=self._input_modes,
            default_output_modes=self._output_modes,
            skills=self._skills
        )
        
        return config
    
    def run_a2a(self, port: int = 10010, host: str = "0.0.0.0") -> None:
        """
        第三步：启动A2A服务
        
        Args:
            port: 服务端口，默认10010
            host: 服务主机，默认"0.0.0.0"
        """
        logger.info(f"🚀 启动A2A服务: {self.name}")
        
        # 构建配置
        config = self._build_config(port, host)
        
        # 显示启动信息
        self._show_startup_info(config)
        
        # 创建执行器
        self._create_executor(config)
        
        # 创建服务器应用
        self._create_server_app(config)
        
        # 启动服务
        self._start_server(host, port)
    
    def _show_startup_info(self, config: AgentConfig) -> None:
        """显示启动信息"""
        print(f"🎯 {config.name} 启动完成")
        print("=" * 50)
        print(f"📋 名称: {config.name}")
        print(f"📝 描述: {config.description}")
        print(f"🔢 版本: {config.version}")
        print(f"🏢 提供商: {config.provider_organization}")
        if config.provider_url:
            print(f"🌐 提供商网站: {config.provider_url}")
        print()
        print(f"🖥️ 服务地址: http://localhost:{config.port}")
        print(f"📡 Agent Card: http://localhost:{config.port}/.well-known/agent-card.json")
        print(f"🎯 技能数量: {len(config.skills)}")
        print()
        print("⚡ 能力:")
        print(f"  • 流式响应: {'✅' if config.capabilities.streaming else '❌'}")
        print(f"  • 推送通知: {'✅' if config.capabilities.push_notifications else '❌'}")
        print(f"  • 状态历史: {'✅' if config.capabilities.state_transition_history else '❌'}")
        print(f"  • 多模态: {'✅' if config.capabilities.multimodal else '❌'}")
        print()
        if config.skills:
            print("🎯 支持技能:")
            for skill in config.skills:
                print(f"  • {skill.name}: {skill.description}")
                if skill.examples:
                    print(f"    示例: {skill.examples[0]}")
        print("=" * 50)
        print("🚀 服务启动中...")
    
    def _create_executor(self, config: AgentConfig) -> None:
        """创建Agent执行器"""
        self._executor = ExecutorFactory.create_executor(
            agent=self.agent,
            name=config.name,
            description=config.description,
            **config.langchain_config
        )
        logger.info(f"⚙️ Agent执行器创建成功: {type(self._executor).__name__}")
    
    def _create_server_app(self, config: AgentConfig) -> None:
        """创建服务器应用"""
        # 创建Agent Card
        agent_card = self._create_agent_card(config)
        
        # 创建任务存储
        task_store = InMemoryTaskStore()
        
        # 创建请求处理器
        request_handler = DefaultRequestHandler(
            agent_executor=self._executor,
            task_store=task_store
        )
        
        # 创建A2A应用
        self._server_app = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
        
        logger.info("🌐 A2A服务器应用创建成功")
    
    def _create_agent_card(self, config: AgentConfig) -> AgentCard:
        """创建Agent Card"""
        # 转换技能配置
        skills = []
        for skill_config in config.skills:
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
            streaming=config.capabilities.streaming,
            push_notifications=config.capabilities.push_notifications,
            state_transition_history=config.capabilities.state_transition_history
        )
        
        # 创建提供商信息
        provider = AgentProvider(
            organization=config.provider_organization,
            url=config.provider_url or config.agent_url
        )
        
        # 创建Agent Card
        agent_card = AgentCard(
            name=config.name,
            description=config.description,
            version=config.version,
            url=config.agent_url,
            skills=skills,
            capabilities=capabilities,
            provider=provider,
            default_input_modes=config.default_input_modes,
            default_output_modes=config.default_output_modes
        )
        
        return agent_card
    
    def _start_server(self, host: str, port: int) -> None:
        """启动服务器"""
        import uvicorn
        
        uvicorn.run(
            self._server_app,
            host=host,
            port=port,
            log_level="info"
        )
