# Kiro Process Manager

[![PyPI version](https://badge.fury.io/py/kiro-process-manager.svg)](https://badge.fury.io/py/kiro-process-manager)
[![Python Support](https://img.shields.io/pypi/pyversions/kiro-process-manager.svg)](https://pypi.org/project/kiro-process-manager/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

非阻塞后台进程管理工具，专为解决 Kiro IDE 中启动长期运行服务时的阻塞问题而设计。

## 问题背景

在使用 Kiro IDE 时，当需要启动长期运行的后台服务（如 uvicorn、redis-server 等）并随后运行测试时，Kiro 会因为同步等待进程退出而无限阻塞，导致后续命令无法执行。

## 解决方案

Kiro Process Manager 提供了一个简单而有效的解决方案，可以在 Kiro 中实现非阻塞的后台服务管理。

## 安装

```bash
pip install kiro-process-manager
```

## 快速开始

### 1. 初始化 Kiro 项目（推荐）

如果你在 Kiro 项目中使用，建议先运行初始化命令：

```bash
kiro-pm init
```

这会在当前目录创建 `.kiro/steering/process-manager-tool.md` 文件，让 Kiro 自动识别这个工具。

### 2. 基本用法

```bash
# 启动后台服务
kiro-pm start myapp "uvicorn main:app --port 8000"

# 等待服务就绪
kiro-pm wait-healthy 8000

# 查看运行的进程
kiro-pm list

# 停止服务
kiro-pm stop myapp
```

### 完整工作流（解决原始问题）

在 Kiro 中执行：

```bash
kiro-pm start api "uvicorn main:app --host 0.0.0.0 --port 8000" && kiro-pm wait-healthy 8000 30 && pytest tests/integration/ && kiro-pm stop api
```

### 高级用法

```bash
# 并行运行多个服务
kiro-pm start api "uvicorn main:app --port 8000"
kiro-pm start redis "redis-server --port 6379"
kiro-pm wait-healthy 8000
kiro-pm wait-healthy 6379

# 运行测试
pytest tests/integration/

# 清理所有服务
kiro-pm cleanup
```

## 功能特性

- ✅ **非阻塞启动**: 后台服务不会阻塞后续命令
- ✅ **健康检查**: 等待端口就绪后再执行测试
- ✅ **进程管理**: 启动、停止、列表、清理功能
- ✅ **跨平台**: 支持 Windows/Linux/macOS
- ✅ **持久化**: 进程信息保存到文件，支持会话恢复
- ✅ **错误处理**: 完善的异常处理和超时机制

## 命令参考

```bash
# 初始化 Kiro 项目
kiro-pm init

# 启动进程
kiro-pm start <name> <command>

# 停止进程
kiro-pm stop <name> [--force]

# 列出所有进程
kiro-pm list

# 等待端口就绪
kiro-pm wait-healthy <port> [--timeout SECONDS] [--host HOST]

# 清理所有进程
kiro-pm cleanup
```

## 使用场景

1. **Web 应用测试**: 启动 FastAPI/Django 应用，运行集成测试
2. **微服务测试**: 同时启动多个服务，运行端到端测试
3. **数据库测试**: 启动 Redis/PostgreSQL，运行数据相关测试
4. **前端开发**: 同时启动前后端服务进行开发调试

## 技术原理

- 使用 `subprocess.Popen` 非阻塞启动进程
- 进程信息持久化到 JSON 文件
- 通过 socket 连接检查端口健康状态
- 支持优雅停止和强制终止
- 跨平台进程管理（Windows 使用 taskkill，Unix 使用 signal）

## 开发

### 本地安装

```bash
git clone https://github.com/yourusername/kiro-process-manager.git
cd kiro-process-manager
pip install -e .
```

### 运行测试

```bash
# 测试基本功能
kiro-pm start test "python -m http.server 8080"
kiro-pm wait-healthy 8080
kiro-pm list
kiro-pm stop test
```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个解决方案。

## 许可证

MIT License