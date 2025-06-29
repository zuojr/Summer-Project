# 使用官方 Dev Container Python 镜像
FROM mcr.microsoft.com/vscode/devcontainers/python:3.10
WORKDIR /workspace
# 先复制依赖文件并安装
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# 默认启动命令
CMD ["/bin/bash"]