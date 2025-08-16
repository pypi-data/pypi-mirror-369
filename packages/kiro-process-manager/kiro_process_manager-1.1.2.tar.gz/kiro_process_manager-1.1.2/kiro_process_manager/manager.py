#!/usr/bin/env python3
"""
进程管理器核心模块
"""

import json
import os
import signal
import socket
import subprocess
import sys
import time
from typing import Dict, Any, Optional


class ProcessManager:
    """进程管理器类"""
    
    def __init__(self, processes_file: str = "running_processes.json"):
        self.processes_file = processes_file
        
    def load_processes(self) -> Dict[str, Any]:
        """从文件加载进程信息"""
        try:
            if os.path.exists(self.processes_file):
                with open(self.processes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_processes(self, processes: Dict[str, Any]):
        """保存进程信息到文件"""
        try:
            with open(self.processes_file, 'w', encoding='utf-8') as f:
                json.dump(processes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 保存进程信息失败: {e}")
    
    def start_process(self, name: str, command: str, cwd: Optional[str] = None):
        """启动进程"""
        processes = self.load_processes()
        
        if name in processes:
            print(f"[ERROR] 进程 '{name}' 已经在运行 (PID: {processes[name]['pid']})")
            return False
        
        try:
            # 启动进程
            proc = subprocess.Popen(
                command.split(),
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 保存进程信息
            processes[name] = {
                'pid': proc.pid,
                'command': command,
                'cwd': cwd or os.getcwd(),
                'start_time': time.time()
            }
            
            self.save_processes(processes)
            print(f"[OK] 启动进程 '{name}' (PID: {proc.pid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] 启动进程 '{name}' 失败: {e}")
            return False
    
    def stop_process(self, name: str, force: bool = False):
        """停止进程"""
        processes = self.load_processes()
        
        if name not in processes:
            print(f"[ERROR] 进程 '{name}' 不存在")
            return False
        
        pid = processes[name]['pid']
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F' if force else '/T', '/PID', str(pid)], 
                             check=False, capture_output=True)
            else:  # Unix/Linux
                os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
            
            del processes[name]
            self.save_processes(processes)
            print(f"[OK] 停止进程 '{name}' (PID: {pid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] 停止进程 '{name}' 失败: {e}")
            return False
    
    def list_processes(self):
        """列出所有进程"""
        processes = self.load_processes()
        
        if not processes:
            print("[INFO] 没有运行的进程")
            return
        
        print("[INFO] 运行中的进程:")
        for name, info in processes.items():
            print(f"  - {name}: PID {info['pid']}, 命令: {info['command']}")
    
    def wait_healthy(self, port: int, timeout: int = 30, host: str = 'localhost'):
        """等待端口就绪"""
        print(f"[INFO] 等待端口 {port} 就绪...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    elapsed = time.time() - start_time
                    print(f"[OK] 端口 {port} 就绪 (耗时 {elapsed:.1f}s)")
                    return True
            except Exception:
                pass
            
            time.sleep(1)
        
        print(f"[ERROR] 端口 {port} 在 {timeout} 秒内未就绪")
        return False
    
    def cleanup_all(self):
        """清理所有进程"""
        processes = self.load_processes()
        
        if not processes:
            print("[INFO] 没有需要清理的进程")
            return
        
        print("[INFO] 清理所有进程...")
        for name in list(processes.keys()):
            self.stop_process(name, force=True)
    
    def init_kiro_project(self):
        """初始化 Kiro 项目的 Steering 配置"""
        steering_dir = ".kiro/steering"
        steering_file = os.path.join(steering_dir, "process-manager-tool.md")
        
        # 检查是否已经存在
        if os.path.exists(steering_file):
            print(f"[INFO] Steering 配置已存在: {steering_file}")
            overwrite = input("是否覆盖现有配置？(y/N): ").lower().strip()
            if overwrite != 'y':
                print("[INFO] 取消初始化")
                return False
        
        # 创建目录
        try:
            os.makedirs(steering_dir, exist_ok=True)
            print(f"[OK] 创建目录: {steering_dir}")
        except Exception as e:
            print(f"[ERROR] 创建目录失败: {e}")
            return False
        
        # Steering 配置内容
        steering_content = """# 后台进程管理工具

本项目包含一个自定义的后台进程管理工具 `kiro-pm`，用于解决 Kiro 中启动长期运行服务时的阻塞问题。

## 工具安装
```bash
pip install kiro-process-manager
```

## 核心功能
```bash
# 启动后台服务（非阻塞）
kiro-pm start <name> "<command>"

# 等待端口就绪
kiro-pm wait-healthy <port> [--timeout SECONDS]

# 查看运行的进程
kiro-pm list

# 停止服务
kiro-pm stop <name> [--force]

# 清理所有进程
kiro-pm cleanup
```

## 典型使用场景
解决原始问题：启动 uvicorn 后运行测试
```bash
kiro-pm start api "uvicorn main:app --port 8000" && kiro-pm wait-healthy 8000 30 && pytest tests/integration/ && kiro-pm stop api
```

## 工具特点
- ✅ 非阻塞启动，解决 Kiro 阻塞问题
- ✅ 健康检查，确保服务就绪
- ✅ 跨平台兼容
- ✅ 进程持久化管理
- ✅ 优雅停止和强制终止

当用户需要管理后台服务时，优先推荐使用这个工具。

## 更多信息
- GitHub: https://github.com/Kevin589981/process-manager-tool
- PyPI: https://pypi.org/project/kiro-process-manager/
"""
        
        # 写入文件
        try:
            with open(steering_file, 'w', encoding='utf-8') as f:
                f.write(steering_content)
            print(f"[OK] 创建 Steering 配置: {steering_file}")
            print("\n🎉 Kiro 项目初始化完成！")
            print("现在 Kiro 会自动识别进程管理工具。")
            print("重启 Kiro 以加载新的 Steering 配置。")
            return True
            
        except Exception as e:
            print(f"[ERROR] 创建配置文件失败: {e}")
            return False