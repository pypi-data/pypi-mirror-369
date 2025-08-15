#!/usr/bin/env python3
"""
EasyA2A 命令行工具

提供便捷的命令行接口来管理A2A服务
"""

import sys
import argparse
from typing import Optional


def main(args: Optional[list] = None) -> int:
    """主入口函数"""
    if args is None:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        prog="easya2a",
        description="🚀 EasyA2A - 快速将Agent包装为A2A协议服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  easya2a --version                 显示版本信息
  easya2a --help                    显示帮助信息
  
更多信息:
  GitHub: https://github.com/whillhill/easya2a
  文档:   https://github.com/whillhill/easya2a#readme
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="EasyA2A 2.0.0"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="显示包信息"
    )
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.info:
        show_info()
        return 0
    
    # 如果没有参数，显示帮助
    parser.print_help()
    return 0


def show_info():
    """显示包信息"""
    print("🚀 EasyA2A - Agent to A2A Protocol Wrapper")
    print("=" * 50)
    print("版本: 2.0.0")
    print("作者: whillhill <ooooofish@126.com>")
    print("GitHub: https://github.com/whillhill/easya2a")
    print("许可证: MIT")
    print()
    print("🎯 三步式API设计:")
    print("1. A2AAgentWrapper.set_up(agent, name, desc)")
    print("2. .add_skill().set_provider().enable_streaming()")
    print("3. .run_a2a(port=10010)")
    print()
    print("📚 快速开始:")
    print("from easya2a import A2AAgentWrapper")
    print("A2AAgentWrapper.set_up(agent, '助手', '服务').run_a2a()")


if __name__ == "__main__":
    sys.exit(main())
