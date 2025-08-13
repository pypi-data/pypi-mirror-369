#!/usr/bin/env python
"""
桌面贴纸命令行接口
"""

import argparse
import sys
from .main import main


def cli():
    """命令行接口入口点"""
    parser = argparse.ArgumentParser(
        description="桌面卡通贴纸效果程序",
        prog="desktop-stickers"
    )
    
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=10,
        help="运行时长（秒），默认10秒"
    )
    
    parser.add_argument(
        "-n", "--number",
        type=int,
        default=20,
        help="初始贴纸数量，默认20个"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        main(duration=args.duration, initial_stickers=args.number)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()