#!/bin/bash

# 开发环境启动脚本

set -e

PROJECT_DIR="/home/huang/pwa"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "启动电化学工作站PWA开发环境..."

# 启动后端服务
echo "启动Django后端服务..."
cd "$BACKEND_DIR"
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!

# 启动前端开发服务器
echo "启动Vue前端开发服务器..."
cd "$FRONTEND_DIR"
npm run serve &
FRONTEND_PID=$!

echo "开发环境已启动！"
echo "前端地址: http://localhost:8080"
echo "后端地址: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
