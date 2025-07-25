#!/bin/bash

# 神州专车MCP服务器启动脚本 - 改进版
set -e

echo "🚗 启动神州专车MCP服务器..."

# 设置uv路径
export PATH="/home/s980499184/.local/bin:$PATH"

# 检查uv是否可用
if ! command -v uv &> /dev/null; then
    echo "❌ uv未找到，请确保uv已安装并在PATH中"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

# 显示当前目录
echo "📂 项目目录: $(pwd)"

# 同步依赖
echo "📦 同步依赖..."
uv sync

# 显示可选的环境变量配置
echo ""
echo "🔐 可选认证配置:"
echo "   export SHENZHOU_USERNAME='your_username'"
echo "   export SHENZHOU_PASSWORD='your_password'"
echo "   export SHENZHOU_INTERACTIVE='false'"
echo ""

# 启动服务器
echo "🚀 启动MCP服务器..."
echo "服务器将在 http://127.0.0.1:8000 上运行"
echo "按 Ctrl+C 停止服务器"
echo ""

uv run python server.py