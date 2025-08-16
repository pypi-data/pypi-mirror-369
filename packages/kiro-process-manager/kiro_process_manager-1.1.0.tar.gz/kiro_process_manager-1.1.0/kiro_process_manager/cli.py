#!/usr/bin/env python3
"""
命令行接口模块
"""

import argparse
import sys
from .manager import ProcessManager


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='kiro-pm',
        description='Kiro 进程管理器 - 非阻塞后台进程管理工具',
        epilog='示例: kiro-pm start api "uvicorn main:app --port 8000"'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # start 命令
    start_parser = subparsers.add_parser('start', help='启动后台进程')
    start_parser.add_argument('name', help='进程名称')
    start_parser.add_argument('cmd', help='要执行的命令')
    start_parser.add_argument('--cwd', help='工作目录')
    
    # stop 命令
    stop_parser = subparsers.add_parser('stop', help='停止进程')
    stop_parser.add_argument('name', help='进程名称')
    stop_parser.add_argument('--force', action='store_true', help='强制终止')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有进程')
    
    # wait-healthy 命令
    health_parser = subparsers.add_parser('wait-healthy', help='等待端口就绪')
    health_parser.add_argument('port', type=int, help='端口号')
    health_parser.add_argument('--timeout', type=int, default=30, help='超时时间（秒）')
    health_parser.add_argument('--host', default='localhost', help='主机地址')
    
    # cleanup 命令
    subparsers.add_parser('cleanup', help='清理所有进程')
    
    # init 命令
    subparsers.add_parser('init', help='初始化 Kiro 项目的 Steering 配置')
    
    return parser


def main():
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = ProcessManager()
    
    try:
        if args.command == 'start':
            success = manager.start_process(args.name, args.cmd, args.cwd)
            sys.exit(0 if success else 1)
            
        elif args.command == 'stop':
            success = manager.stop_process(args.name, args.force)
            sys.exit(0 if success else 1)
            
        elif args.command == 'list':
            manager.list_processes()
            
        elif args.command == 'wait-healthy':
            success = manager.wait_healthy(args.port, args.timeout, args.host)
            sys.exit(0 if success else 1)
            
        elif args.command == 'cleanup':
            manager.cleanup_all()
            
        elif args.command == 'init':
            success = manager.init_kiro_project()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n[INFO] 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()