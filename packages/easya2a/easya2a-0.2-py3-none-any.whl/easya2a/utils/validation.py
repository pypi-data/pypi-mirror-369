"""
验证工具

提供Agent和配置的验证功能。
"""

import inspect
import logging
from typing import Any, List, Dict, Optional, Callable

from ..config.agent_config import AgentConfig

logger = logging.getLogger(__name__)


class AgentValidator:
    """Agent验证器"""
    
    @staticmethod
    def validate_agent(agent: Any) -> Dict[str, Any]:
        """
        验证Agent是否符合要求
        
        Args:
            agent: 要验证的Agent
            
        Returns:
            验证结果字典
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {
                "type": type(agent).__name__,
                "module": type(agent).__module__,
                "methods": [],
                "is_langchain": False
            }
        }
        
        try:
            # 检查基本要求
            AgentValidator._check_basic_requirements(agent, result)
            
            # 检查方法
            AgentValidator._check_methods(agent, result)
            
            # 检查LangChain兼容性
            AgentValidator._check_langchain_compatibility(agent, result)
            
            # 检查异步支持
            AgentValidator._check_async_support(agent, result)
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证过程中出现错误: {str(e)}")
        
        return result
    
    @staticmethod
    def _check_basic_requirements(agent: Any, result: Dict[str, Any]):
        """检查基本要求"""
        if agent is None:
            result["valid"] = False
            result["errors"].append("Agent不能为None")
            return
        
        if not hasattr(agent, '__class__'):
            result["valid"] = False
            result["errors"].append("Agent必须是一个对象实例")
            return
        
        result["info"]["type"] = type(agent).__name__
        result["info"]["module"] = type(agent).__module__
    
    @staticmethod
    def _check_methods(agent: Any, result: Dict[str, Any]):
        """检查方法"""
        # 常见的处理方法名
        expected_methods = [
            'process', 'chat', 'handle', 'invoke', 'run',
            'process_message', 'handle_message', 'respond'
        ]
        
        available_methods = []
        for method_name in expected_methods:
            if hasattr(agent, method_name):
                method = getattr(agent, method_name)
                if callable(method):
                    available_methods.append(method_name)
                    
                    # 检查方法签名
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    
                    result["info"]["methods"].append({
                        "name": method_name,
                        "parameters": params,
                        "is_async": inspect.iscoroutinefunction(method)
                    })
        
        if not available_methods:
            result["valid"] = False
            result["errors"].append(f"Agent必须有以下方法之一: {expected_methods}")
        else:
            result["info"]["available_methods"] = available_methods
    
    @staticmethod
    def _check_langchain_compatibility(agent: Any, result: Dict[str, Any]):
        """检查LangChain兼容性"""
        # 检查模块名
        module_name = type(agent).__module__
        if 'langchain' in module_name.lower():
            result["info"]["is_langchain"] = True
            result["info"]["langchain_module"] = module_name
        
        # 检查LangChain特有方法
        langchain_methods = ['invoke', 'stream', 'batch', 'ainvoke', 'astream']
        langchain_attrs = ['input_keys', 'output_keys', 'memory', 'tools']
        
        found_methods = []
        found_attrs = []
        
        for method in langchain_methods:
            if hasattr(agent, method):
                found_methods.append(method)
        
        for attr in langchain_attrs:
            if hasattr(agent, attr):
                found_attrs.append(attr)
        
        if found_methods or found_attrs:
            result["info"]["is_langchain"] = True
            result["info"]["langchain_methods"] = found_methods
            result["info"]["langchain_attributes"] = found_attrs
    
    @staticmethod
    def _check_async_support(agent: Any, result: Dict[str, Any]):
        """检查异步支持"""
        async_methods = []
        sync_methods = []
        
        for method_info in result["info"]["methods"]:
            if method_info["is_async"]:
                async_methods.append(method_info["name"])
            else:
                sync_methods.append(method_info["name"])
        
        result["info"]["async_methods"] = async_methods
        result["info"]["sync_methods"] = sync_methods
        
        if not async_methods and not sync_methods:
            result["warnings"].append("未找到可用的处理方法")
        elif async_methods:
            result["info"]["supports_async"] = True
        else:
            result["info"]["supports_async"] = False
            result["warnings"].append("Agent不支持异步处理，性能可能受限")


def validate_agent(agent: Any) -> Dict[str, Any]:
    """验证Agent的便捷函数"""
    return AgentValidator.validate_agent(agent)


def validate_config(config: AgentConfig) -> Dict[str, Any]:
    """
    验证Agent配置
    
    Args:
        config: Agent配置
        
    Returns:
        验证结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # 检查必需字段
        if not config.name or not config.name.strip():
            result["valid"] = False
            result["errors"].append("Agent名称不能为空")
        
        # 检查端口
        if not isinstance(config.port, int) or config.port < 1 or config.port > 65535:
            result["valid"] = False
            result["errors"].append(f"端口号无效: {config.port}")
        
        # 检查Agent URL格式
        if config.agent_url and not config.agent_url.startswith(('http://', 'https://')):
            result["warnings"].append("Agent URL应该以http://或https://开头")
        
        # 检查技能
        if not config.skills:
            result["warnings"].append("未配置任何技能")
        else:
            for i, skill in enumerate(config.skills):
                if not skill.id or not skill.name:
                    result["errors"].append(f"技能{i+1}缺少ID或名称")
        
        # 检查能力
        if config.capabilities:
            if config.capabilities.streaming:
                result["warnings"].append("启用了流式响应，请确保Agent支持")
            
            if config.capabilities.multimodal:
                result["warnings"].append("启用了多模态，请确保Agent支持")
    
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"配置验证过程中出现错误: {str(e)}")
    
    return result


def check_dependencies() -> Dict[str, Any]:
    """
    检查依赖项
    
    Returns:
        依赖检查结果
    """
    result = {
        "valid": True,
        "missing": [],
        "available": [],
        "versions": {}
    }
    
    # 必需的依赖
    required_deps = [
        "a2a",
        "uvicorn",
        "starlette"
    ]
    
    # 可选的依赖
    optional_deps = [
        "langchain",
        "langchain_openai",
        "langchain_core",
        "openai",
        "anthropic"
    ]
    
    # 检查必需依赖
    for dep in required_deps:
        try:
            module = __import__(dep)
            result["available"].append(dep)
            if hasattr(module, '__version__'):
                result["versions"][dep] = module.__version__
        except ImportError:
            result["valid"] = False
            result["missing"].append(dep)
    
    # 检查可选依赖
    for dep in optional_deps:
        try:
            module = __import__(dep)
            result["available"].append(dep)
            if hasattr(module, '__version__'):
                result["versions"][dep] = module.__version__
        except ImportError:
            pass  # 可选依赖不影响valid状态
    
    return result


def validate_environment() -> Dict[str, Any]:
    """
    验证环境配置
    
    Returns:
        环境验证结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    import sys
    import os
    
    # 检查Python版本
    python_version = sys.version_info
    result["info"]["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    if python_version < (3, 8):
        result["valid"] = False
        result["errors"].append("需要Python 3.8或更高版本")
    
    # 检查环境变量
    env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY"
    ]
    
    found_keys = []
    for var in env_vars:
        if os.getenv(var):
            found_keys.append(var)
    
    if not found_keys:
        result["warnings"].append("未找到任何AI服务的API密钥")
    else:
        result["info"]["api_keys"] = found_keys
    
    # 检查依赖
    deps_result = check_dependencies()
    if not deps_result["valid"]:
        result["valid"] = False
        result["errors"].extend([f"缺少依赖: {dep}" for dep in deps_result["missing"]])
    
    result["info"]["dependencies"] = deps_result
    
    return result


# 诊断工具
def run_diagnostics(agent: Any, config: AgentConfig) -> Dict[str, Any]:
    """
    运行完整诊断
    
    Args:
        agent: Agent实例
        config: Agent配置
        
    Returns:
        诊断结果
    """
    result = {
        "overall_status": "unknown",
        "agent_validation": {},
        "config_validation": {},
        "environment_validation": {}
    }
    
    try:
        # 验证Agent
        result["agent_validation"] = validate_agent(agent)
        
        # 验证配置
        result["config_validation"] = validate_config(config)
        
        # 验证环境
        result["environment_validation"] = validate_environment()
        
        # 确定总体状态
        all_valid = (
            result["agent_validation"]["valid"] and
            result["config_validation"]["valid"] and
            result["environment_validation"]["valid"]
        )
        
        if all_valid:
            result["overall_status"] = "ready"
        else:
            result["overall_status"] = "issues_found"
    
    except Exception as e:
        result["overall_status"] = "error"
        result["error"] = str(e)
    
    return result
