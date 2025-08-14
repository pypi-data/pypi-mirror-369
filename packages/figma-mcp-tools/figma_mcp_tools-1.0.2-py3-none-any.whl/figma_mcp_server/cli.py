#!/usr/bin/env python3
"""
Figma MCP Server CLI
"""

import asyncio
import os
import sys
from .server import main as server_main

def main():
    """CLI入口点"""
    # 检查环境变量
    if not os.getenv("FIGMA_ACCESS_TOKEN"):
        print("错误: 请设置 FIGMA_ACCESS_TOKEN 环境变量")
        print("设置方法:")
        if os.name == "nt":  # Windows
            print("  set FIGMA_ACCESS_TOKEN=your_token_here")
        else:
            print("  export FIGMA_ACCESS_TOKEN='your_token_here'")
        sys.exit(1)
    
    print("启动 Figma MCP 服务器...")
    print(f"FIGMA_ACCESS_TOKEN: {'*' * 10}{os.getenv('FIGMA_ACCESS_TOKEN')[-4:]}")
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
