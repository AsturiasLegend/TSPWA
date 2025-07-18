#!/bin/bash

# 电化学工作站PWA项目部署脚本

set -e

echo "开始部署电化学工作站PWA项目..."

# 项目目录
PROJECT_DIR="/home/huang/pwa"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR/backend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印颜色消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的依赖
check_dependencies() {
    print_message "检查系统依赖..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 未安装，请先安装 pip3"
        exit 1
    fi
    
    print_message "所有必要依赖已安装"
}

# 部署前端
deploy_frontend() {
    print_message "开始部署前端..."
    
    cd "$FRONTEND_DIR"
    
    # 安装依赖
    print_message "安装前端依赖..."
    npm install
    
    # 构建生产版本
    print_message "构建前端生产版本..."
    npm run build
    
    print_message "前端构建完成"
}

# 部署后端
deploy_backend() {
    print_message "开始部署后端..."
    
    cd "$BACKEND_DIR"
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        print_message "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    print_message "安装后端依赖..."
    pip install -r requirements.txt
    
    # 复制环境配置文件
    if [ ! -f ".env" ]; then
        print_message "创建环境配置文件..."
        cp .env.example .env
        print_warning "请编辑 .env 文件配置正确的数据库和其他设置"
    fi
    
    # 运行数据库迁移
    print_message "运行数据库迁移..."
    python manage.py makemigrations
    python manage.py migrate
    
    # 收集静态文件
    print_message "收集静态文件..."
    python manage.py collectstatic --noinput
    
    print_message "后端部署完成"
}

# 配置Web服务器
configure_webserver() {
    print_message "配置Web服务器..."
    
    # 创建Apache虚拟主机配置
    cat > /tmp/electrochemical.conf << EOF
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot $FRONTEND_DIR/dist
    
    # 前端静态文件
    <Directory "$FRONTEND_DIR/dist">
        AllowOverride All
        Require all granted
    </Directory>
    
    # API代理到Django
    ProxyPass /api/ http://127.0.0.1:8000/api/
    ProxyPassReverse /api/ http://127.0.0.1:8000/api/
    
    # PWA文件
    <Files "sw.js">
        Header set Service-Worker-Allowed "/"
    </Files>
    
    # 启用压缩
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/plain
        AddOutputFilterByType DEFLATE text/html
        AddOutputFilterByType DEFLATE text/xml
        AddOutputFilterByType DEFLATE text/css
        AddOutputFilterByType DEFLATE application/xml
        AddOutputFilterByType DEFLATE application/xhtml+xml
        AddOutputFilterByType DEFLATE application/rss+xml
        AddOutputFilterByType DEFLATE application/javascript
        AddOutputFilterByType DEFLATE application/x-javascript
    </IfModule>
    
    # 缓存控制
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType text/css "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
        ExpiresByType image/jpg "access plus 1 year"
        ExpiresByType image/jpeg "access plus 1 year"
        ExpiresByType image/gif "access plus 1 year"
        ExpiresByType image/ico "access plus 1 year"
        ExpiresByType image/icon "access plus 1 year"
        ExpiresByType text/plain "access plus 1 month"
        ExpiresByType application/x-shockwave-flash "access plus 1 month"
        ExpiresByType text/css "access plus 1 month"
        ExpiresByType application/pdf "access plus 1 month"
        ExpiresByType text/javascript "access plus 1 month"
        ExpiresByType application/javascript "access plus 1 month"
        ExpiresByType text/html "access plus 600 seconds"
    </IfModule>
    
    ErrorLog \${APACHE_LOG_DIR}/electrochemical_error.log
    CustomLog \${APACHE_LOG_DIR}/electrochemical_access.log combined
</VirtualHost>
EOF
    
    print_message "Apache配置文件已创建: /tmp/electrochemical.conf"
    print_warning "请将配置文件复制到Apache sites-available目录并启用"
}

# 创建systemd服务文件
create_systemd_service() {
    print_message "创建systemd服务文件..."
    
    cat > /tmp/electrochemical.service << EOF
[Unit]
Description=Electrochemical Workstation Django Server
After=network.target

[Service]
Type=simple
User=huang
Group=huang
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/gunicorn --bind 127.0.0.1:8000 electrochemical.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    print_message "systemd服务文件已创建: /tmp/electrochemical.service"
    print_warning "请将服务文件复制到 /etc/systemd/system/ 目录"
}

# 主函数
main() {
    print_message "电化学工作站PWA项目部署开始"
    
    check_dependencies
    deploy_frontend
    deploy_backend
    configure_webserver
    create_systemd_service
    
    print_message "部署完成！"
    echo ""
    print_message "下一步操作："
    echo "1. 编辑 $BACKEND_DIR/.env 文件配置数据库等信息"
    echo "2. 将 /tmp/electrochemical.conf 复制到 Apache sites-available 目录"
    echo "3. 启用 Apache 站点: sudo a2ensite electrochemical"
    echo "4. 将 /tmp/electrochemical.service 复制到 /etc/systemd/system/"
    echo "5. 启用并启动服务: sudo systemctl enable electrochemical && sudo systemctl start electrochemical"
    echo "6. 重启 Apache: sudo systemctl restart apache2"
    echo ""
    print_message "访问地址: http://localhost"
}

# 运行主函数
main "$@"
