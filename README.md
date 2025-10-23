# 股票数据查询服务

纯净的数据库读写访问应用，提供股票行情和信息的查询API接口。

## 项目简介

本服务是从 `qtfund_project_2` 拆分出来的查询服务，专注于提供数据查询功能。数据同步功能由另一个服务（端口7777）负责。

## 功能特性

- ✅ 股票行情数据查询 (TimescaleDB)
- ✅ 股票基础信息查询 (数据库 + 本地JSON)
- ✅ 健康检查和版本信息
- ✅ RESTful API设计
- ✅ 完整的日志系统

## 快速开始

### 1. 一键设置环境（推荐）

使用自动化脚本设置虚拟环境和依赖：

```bash
./bin/setup.sh
```

该脚本会自动：
- ✅ 检查Python版本
- ✅ 创建虚拟环境 `.venv`
- ✅ 激活虚拟环境
- ✅ 升级pip到最新版本
- ✅ 安装所有依赖包
- ✅ 创建必要的目录

### 2. 手动安装（可选）

如果您希望手动设置：

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制配置模板并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# Flask应用密钥（必须修改！）
SECRET_KEY=your-super-secret-random-key-here

# 数据库连接
DB_HOST=localhost
DB_PORT=5432
DB_NAME=securities_data
DB_USER=your_username
DB_PASSWORD=your_password
```

**生成随机SECRET_KEY命令：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 启动服务

**使用启动脚本（推荐）：**
```bash
./bin/start.sh
```

启动脚本会自动：
- 检测并激活虚拟环境（如果存在 `.venv`）
- 检查端口占用情况
- 检查依赖是否安装
- 后台启动服务并记录PID

**手动启动：**
```bash
# 激活虚拟环境（如果使用虚拟环境）
source .venv/bin/activate

# 前台启动
python start_flask_app.py

# 后台启动
nohup python start_flask_app.py > logs/flask.log 2>&1 &
```

服务将在 **http://localhost:8000** 启动

## API接口

### 健康检查

```bash
GET /api/health
GET /api/version
```

### 股票行情查询

```bash
# 查询股票行情数据
GET /api/stock-price/query?symbol=SH.600519&limit=10
POST /api/stock-price/query
{
    "symbol": "SH.600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "limit": 100
}

# 获取股票基础信息
GET /api/stock-price/info/SH.600519

# 列出所有股票
GET /api/stock-price/list?market_code=SH&limit=100
```

### 股票信息查询

```bash
# 从本地JSON查询
GET /api/stock-info/local?exchange_code=XSHG&limit=100

# 获取统计信息
GET /api/stock-info/statistics
```

## 项目结构

```
qtfund_project_3/
├── app/                          # Flask应用
│   ├── routes/                   # API路由
│   │   ├── health.py            # 健康检查
│   │   ├── stock_price.py       # 股票行情查询
│   │   └── stock_info.py        # 股票信息查询
│   ├── services/                # 业务逻辑
│   │   ├── stock_data_service.py    # 行情数据服务
│   │   └── stock_info_service.py    # 股票信息服务
│   ├── utils/                   # 工具函数
│   │   └── responses.py         # 响应格式化
│   └── main.py                  # Flask主应用
├── config/                      # 配置
│   ├── settings.py             # 数据库配置
│   └── logging_config.py       # 日志配置
├── database/                    # 数据库连接
│   └── connection.py           # 数据库管理器
├── models/                      # 数据模型
│   └── stock_data.py           # 股票数据模型
├── constants/                   # 常量
│   ├── stock_lists/            # 股票清单JSON
│   └── stock_lists_loader.py   # 清单加载器
├── logs/                        # 日志文件
├── start_flask_app.py          # 启动脚本
├── requirements.txt            # 依赖包
└── README.md                   # 本文件
```

## 与同步服务的关系

- **本服务 (端口8000)**: 纯净的查询服务
- **同步服务 (端口7777)**: 负责数据同步和写入

两个服务共享同一个TimescaleDB数据库，但职责明确分离。

## 常用命令

```bash
# 一键设置环境
./bin/setup.sh

# 启动服务
./bin/start.sh

# 查看服务状态
./bin/health.sh

# 停止服务
./bin/stop.sh

# 查看日志
tail -f logs/query_service.log
tail -f logs/flask_server.log
```

## 虚拟环境管理

本项目推荐使用Python虚拟环境来隔离依赖：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 在虚拟环境中安装新包
pip install package_name
pip freeze > requirements.txt  # 更新依赖列表
```

**注意：** `.venv` 目录已在 `.gitignore` 中配置，不会被提交到仓库。

## 注意事项

1. **推荐使用虚拟环境**：运行 `./bin/setup.sh` 自动创建
2. 本服务仅提供查询功能，不包含数据同步
3. 数据同步请使用端口7777的同步服务
4. 确保数据库连接正确配置
5. 生产环境必须修改 `.env` 中的 `SECRET_KEY`
6. 建议配合同步服务一起使用

## 许可证

本项目仅供学习和研究使用。

