from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    try:
        with open("README.md", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Kiro 进程管理器 - 非阻塞后台进程管理工具"

setup(
    name="kiro-process-manager",
    version="1.1.1",
    author="Kiro Process Manager Contributors",
    author_email="kevin3627713@gmail.com",
    description="非阻塞后台进程管理工具，解决 Kiro IDE 中服务启动阻塞问题",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Kevin589981/process-manager-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "kiro-pm=kiro_process_manager.cli:main",
        ],
    },
    keywords="kiro ide process manager background service uvicorn fastapi development tools",
    project_urls={
        "Bug Reports": "https://github.com/Kevin589981/process-manager-tool/issues",
        "Source": "https://github.com/Kevin589981/process-manager-tool",
        "Documentation": "https://github.com/Kevin589981/process-manager-tool#readme",
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    license_files=("LICENSE",),
)