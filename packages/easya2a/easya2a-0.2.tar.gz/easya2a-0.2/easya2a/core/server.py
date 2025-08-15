"""
A2A服务器

提供高级的服务器管理功能，支持多种启动模式和配置。
"""

import logging
import signal
import sys
from typing import Any, Optional, Dict, List
from pathlib import Path

from ..config.agent_config import AgentConfig
from ..config.settings import get_settings, setup_logging
from .wrapper import A2AWrapper

logger = logging.getLogger(__name__)


class A2AServer:
    """
    A2A服务器管理器
    
    提供高级的服务器管理功能，包括：
    - 优雅关闭
    - 配置管理
    - 日志设置
    - 健康检查
    """
    
    def __init__(self, agent: Any, config: AgentConfig):
        """
        初始化A2A服务器
        
        Args:
            agent: Agent实例
            config: Agent配置
        """
        self.agent = agent
        self.config = config
        self.wrapper = A2AWrapper(agent, config)
        self.is_running = False
        
        # 设置日志
        setup_logging()
        
        # 注册信号处理器
        self._setup_signal_handlers()
        
        logger.info(f"🖥️ A2A服务器初始化完成: {config.name}")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 接收到信号 {signum}，正在优雅关闭服务器...")
            self.stop()
            sys.exit(0)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self, **uvicorn_kwargs):
        """
        启动服务器
        
        Args:
            **uvicorn_kwargs: 传递给uvicorn的参数
        """
        try:
            self.is_running = True
            
            # 打印启动信息
            self._print_startup_info()
            
            # 启动服务器
            self.wrapper.run(**uvicorn_kwargs)
            
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            raise
        finally:
            self.is_running = False
    
    def stop(self):
        """停止服务器"""
        if self.is_running:
            logger.info("🛑 正在停止A2A服务器...")
            self.is_running = False
            # 这里可以添加清理逻辑
    
    def _print_startup_info(self):
        """打印启动信息"""
        config = self.config
        
        print("\n" + "="*60)
        print(f"🚀 A2A Agent Server Starting")
        print("="*60)
        print(f"📋 Agent Name: {config.name}")
        print(f"📝 Description: {config.description}")
        print(f"🌐 Agent URL: {config.agent_url}")
        print(f"📡 Agent Card: {config.agent_url}.well-known/agent-card.json")
        print(f"🔧 Skills: {len(config.skills)} configured")
        print(f"⚙️ Capabilities: Streaming={config.capabilities.streaming}")
        print("="*60)
        print("🎯 Server is ready to accept connections!")
        print("🛑 Press Ctrl+C to stop the server")
        print("="*60 + "\n")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "agent_name": self.config.name,
            "version": self.config.version,
            "url": self.config.url,
            "skills_count": len(self.config.skills),
            "capabilities": self.config.capabilities.to_dict()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取服务器指标"""
        # 这里可以添加更多指标收集
        return {
            "uptime": "unknown",  # 可以添加运行时间计算
            "requests_total": "unknown",  # 可以添加请求计数
            "errors_total": "unknown",  # 可以添加错误计数
            "agent_type": type(self.agent).__name__,
            "config": self.config.get_agent_card_data()
        }


class A2AServerManager:
    """
    A2A服务器管理器
    
    管理多个A2A服务器实例。
    """
    
    def __init__(self):
        self.servers: Dict[str, A2AServer] = {}
        self.running_servers: List[str] = []
    
    def add_server(self, name: str, agent: Any, config: AgentConfig):
        """添加服务器"""
        server = A2AServer(agent, config)
        self.servers[name] = server
        logger.info(f"➕ 添加服务器: {name}")
    
    def start_server(self, name: str, **uvicorn_kwargs):
        """启动指定服务器"""
        if name not in self.servers:
            raise ValueError(f"服务器 '{name}' 不存在")
        
        server = self.servers[name]
        server.start(**uvicorn_kwargs)
        self.running_servers.append(name)
    
    def stop_server(self, name: str):
        """停止指定服务器"""
        if name in self.servers:
            self.servers[name].stop()
            if name in self.running_servers:
                self.running_servers.remove(name)
    
    def start_all(self, base_port: int = 10010):
        """启动所有服务器"""
        import threading
        import time
        
        threads = []
        for i, (name, server) in enumerate(self.servers.items()):
            port = base_port + i
            server.config.port = port
            
            def start_server_thread(s=server):
                s.start()
            
            thread = threading.Thread(target=start_server_thread, daemon=True)
            thread.start()
            threads.append(thread)
            
            logger.info(f"🚀 启动服务器: {name} on port {port}")
            time.sleep(1)  # 避免端口冲突
        
        # 等待所有线程
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("🛑 停止所有服务器")
            self.stop_all()
    
    def stop_all(self):
        """停止所有服务器"""
        for name in list(self.running_servers):
            self.stop_server(name)
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有服务器状态"""
        return {
            name: server.get_health_status()
            for name, server in self.servers.items()
        }


# 便捷函数
def serve_agent(
    agent: Any,
    name: str,
    description: str = "",
    port: int = 10010,
    host: str = "0.0.0.0",
    **config_kwargs
):
    """
    便捷函数：快速启动Agent服务
    
    Args:
        agent: Agent实例
        name: Agent名称
        description: Agent描述
        port: 服务端口
        host: 服务主机
        **config_kwargs: 额外配置
    """
    config = AgentConfig(
        name=name,
        description=description,
        port=port,
        host=host,
        **config_kwargs
    )
    
    server = A2AServer(agent, config)
    server.start()


def serve_from_config(agent: Any, config_file: Path):
    """
    从配置文件启动服务
    
    Args:
        agent: Agent实例
        config_file: 配置文件路径
    """
    config = AgentConfig.from_file(config_file)
    server = A2AServer(agent, config)
    server.start()


def create_development_server(agent: Any, name: str, **kwargs):
    """
    创建开发环境服务器
    
    Args:
        agent: Agent实例
        name: Agent名称
        **kwargs: 额外配置
    """
    from ..config.settings import ConfigTemplates
    
    dev_config = ConfigTemplates.development()
    config = AgentConfig(
        name=name,
        description=f"Development server for {name}",
        **dev_config,
        **kwargs
    )
    
    return A2AServer(agent, config)


def create_production_server(agent: Any, name: str, **kwargs):
    """
    创建生产环境服务器
    
    Args:
        agent: Agent实例
        name: Agent名称
        **kwargs: 额外配置
    """
    from ..config.settings import ConfigTemplates
    
    prod_config = ConfigTemplates.production()
    config = AgentConfig(
        name=name,
        description=f"Production server for {name}",
        **prod_config,
        **kwargs
    )
    
    return A2AServer(agent, config)


# 上下文管理器
class A2AServerContext:
    """A2A服务器上下文管理器"""
    
    def __init__(self, agent: Any, config: AgentConfig):
        self.server = A2AServer(agent, config)
    
    def __enter__(self):
        return self.server
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.stop()
    
    async def __aenter__(self):
        return self.server
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.server.stop()
