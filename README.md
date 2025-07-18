# 电化学工作站PWA项目

这是一个基于Vue.js + Django的电化学工作站移动端PWA应用，用于与MSP430蓝牙设备通信，进行电化学实验数据采集、可视化和分析。

## 项目特性

- 🔵 **蓝牙通信**: 使用Web Bluetooth API与MSP430设备通信
- 📊 **数据可视化**: 基于ECharts的实时数据图表展示
- 💾 **本地存储**: 使用IndexedDB进行离线数据存储
- 🔄 **PWA支持**: 支持离线使用和安装到主屏幕
- 📱 **响应式设计**: 完美适配移动设备
- 🔬 **多种实验类型**: 支持CV、LSV、SWV等电化学实验
- 📈 **数据分析**: 峰值检测、统计分析等功能
- ☁️ **云端同步**: 可选的云端数据同步功能

## 技术栈

### 前端
- Vue.js 3.x
- Element Plus UI组件库
- ECharts 数据可视化
- Dexie.js IndexedDB操作
- Axios HTTP客户端
- Web Bluetooth API

### 后端
- Django 4.2
- Django REST Framework
- MySQL数据库
- Celery异步任务
- Redis缓存
- NumPy/SciPy数据分析

## 项目结构

```
/home/huang/pwa/
├── frontend/                 # Vue.js前端
│   ├── public/
│   │   ├── manifest.json    # PWA清单
│   │   ├── sw.js           # Service Worker
│   │   └── index.html      # 主页面
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── store/         # Vuex状态管理
│   │   ├── router/        # 路由配置
│   │   ├── bluetooth/     # 蓝牙通信模块
│   │   ├── charts/        # 图表组件
│   │   └── storage/       # 本地存储
│   └── package.json
├── backend/                 # Django后端
│   ├── electrochemical/    # 项目配置
│   ├── api/               # 基础API
│   ├── experiments/       # 实验管理
│   ├── analysis/          # 数据分析
│   ├── manage.py
│   └── requirements.txt
├── deploy.sh              # 部署脚本
├── dev.sh                # 开发环境启动脚本
└── README.md             # 项目说明
```

## 快速开始

### 环境要求

- Node.js 16+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### 开发环境设置

1. **克隆项目**
```bash
cd /home/huang/pwa
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

3. **设置后端环境**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **配置数据库**
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE electrochemical CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接信息
```

5. **运行数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **启动开发服务器**
```bash
# 使用开发脚本
./dev.sh

# 或手动启动
# 后端
cd backend && python manage.py runserver 127.0.0.1:8000

# 前端
cd frontend && npm run serve
```

### 生产环境部署

1. **运行部署脚本**
```bash
./deploy.sh
```

2. **配置Web服务器**
```bash
# 复制Apache配置
sudo cp /tmp/electrochemical.conf /etc/apache2/sites-available/
sudo a2ensite electrochemical
sudo a2enmod proxy proxy_http headers deflate expires

# 复制systemd服务文件
sudo cp /tmp/electrochemical.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable electrochemical
sudo systemctl start electrochemical

# 重启Apache
sudo systemctl restart apache2
```

## 功能说明

### 1. 设备连接
- 支持Web Bluetooth API自动扫描和连接MSP430设备
- 实时监控设备连接状态
- 自动重连机制

### 2. 实验控制
- 支持多种电化学实验类型（CV、LSV、SWV等）
- 实时参数配置
- 实验状态监控和控制

### 3. 数据可视化
- 实时数据图表展示
- 支持缩放、拖拽、数据点悬浮
- 多实验数据对比
- 图表导出功能

### 4. 数据管理
- 本地IndexedDB存储
- 实验数据分类和检索
- 数据导入导出
- 云端同步（可选）

### 5. 数据分析
- 峰值检测和分析
- 统计分析
- 基线校正
- 实验对比分析

## API 文档

### 认证 API
- `POST /api/auth/` - 用户登录/注册
- `GET /api/profile/` - 获取用户信息
- `PUT /api/profile/` - 更新用户信息

### 实验管理 API
- `GET /api/experiments/` - 获取实验列表
- `POST /api/experiments/` - 创建实验
- `GET /api/experiments/{id}/` - 获取实验详情
- `POST /api/experiments/{id}/start/` - 开始实验
- `POST /api/experiments/{id}/stop/` - 停止实验
- `POST /api/experiments/{id}/add_data_points/` - 添加数据点

### 数据分析 API
- `GET /api/analysis/methods/` - 获取分析方法
- `POST /api/analysis/peak-analysis/analyze_experiment/` - 峰值分析
- `POST /api/analysis/statistical-analysis/analyze_experiment/` - 统计分析

## 蓝牙通信协议

### 设备连接
- Service UUID: `12345678-1234-1234-1234-123456789abc`
- Write Characteristic: `12345678-1234-1234-1234-123456789abd`
- Read Characteristic: `12345678-1234-1234-1234-123456789abe`

### 命令格式
```json
{
  "type": "START_EXPERIMENT",
  "experimentType": "CV",
  "parameters": {
    "startVoltage": 0,
    "endVoltage": 1,
    "scanRate": 100,
    "cycles": 1
  }
}
```

### 数据格式
```json
{
  "type": "DATA_POINT",
  "timestamp": "2024-01-01T12:00:00Z",
  "voltage": 0.5,
  "current": 0.001,
  "cycle": 1
}
```

## 开发指南

### 前端开发
1. 组件位于 `frontend/src/components/`
2. 页面视图位于 `frontend/src/views/`
3. 状态管理使用Vuex，模块位于 `frontend/src/store/modules/`
4. 蓝牙通信逻辑位于 `frontend/src/bluetooth/`

### 后端开发
1. API视图位于各应用的 `views.py`
2. 数据模型位于各应用的 `models.py`
3. 序列化器位于各应用的 `serializers.py`
4. 异步任务使用Celery

### 添加新的实验类型
1. 在 `experiments/models.py` 中添加新的实验类型
2. 更新前端的实验类型选择组件
3. 在蓝牙通信模块中添加对应的命令处理

## 注意事项

1. **HTTPS要求**: Web Bluetooth API需要HTTPS环境，开发时可使用localhost
2. **浏览器支持**: 需要支持Web Bluetooth API的浏览器（Chrome, Edge等）
3. **iOS限制**: iOS Safari对Web Bluetooth API支持有限
4. **设备兼容性**: 确保MSP430设备使用正确的蓝牙服务UUID

## 故障排除

### 常见问题
1. **蓝牙连接失败**: 检查设备是否在范围内，浏览器是否支持Web Bluetooth
2. **数据不显示**: 检查数据格式是否正确，图表组件是否正确加载
3. **API请求失败**: 检查后端服务是否启动，CORS设置是否正确

### 日志查看
```bash
# 前端日志
浏览器开发者工具 -> Console

# 后端日志
tail -f backend/logs/django.log

# 系统服务日志
sudo journalctl -u electrochemical -f
```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请联系项目维护者。
