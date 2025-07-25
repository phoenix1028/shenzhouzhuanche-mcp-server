#!/bin/bash

# 神州专车MCP服务器启动脚本
echo "🚗 启动神州专车MCP服务器..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，请先安装uv:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

# 同步依赖
echo "📦 同步依赖..."
uv sync

# 设置环境变量（可选）
# export SHENZHOU_USERNAME="your_username"
# export SHENZHOU_PASSWORD="your_password"
# export SHENZHOU_INTERACTIVE="false"

# 启动服务器
echo "🚀 启动MCP服务器..."
uv run python server.py