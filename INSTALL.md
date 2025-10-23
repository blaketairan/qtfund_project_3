# 安装指南

本文档提供详细的安装说明和常见问题解决方案。

## 📋 系统要求

- **Python**: 3.9 或更高版本
- **操作系统**: Linux (Ubuntu, CentOS, Rocky Linux), macOS
- **数据库**: PostgreSQL 12+ with TimescaleDB extension

---

## 🚀 快速安装

### 方法一：自动安装（推荐）

```bash
# 1. 克隆项目
git clone git@github.com:blaketairan/qtfund_project_3.git
cd qtfund_project_3

# 2. 运行自动设置脚本
./bin/setup.sh

# 3. 配置环境变量
cp .env.example .env
# 编辑.env文件，设置SECRET_KEY和数据库配置

# 4. 启动服务
./bin/start.sh
```

### 方法二：手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 升级pip
pip install --upgrade pip

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑.env文件

# 5. 启动服务
python start_flask_app.py
```

---

## 🔧 Rocky Linux 9 / CentOS / RHEL 安装指南

### 常见问题1: 找不到特定版本的包

**错误信息：**
```
ERROR: Could not find a version that satisfies the requirement sqlalchemy==2.0.23
ERROR: No matching distribution found for sqlalchemy==2.0.23
```

**原因：**
- Rocky Linux 9的默认Python版本可能较旧
- PyPI镜像源同步延迟或限制
- 网络连接问题

**解决方案：**

#### 方案1: 使用国内镜像源（推荐）

```bash
# 清华大学镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或使用中科大镜像源
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
```

#### 方案2: 永久配置pip镜像源

```bash
# 创建pip配置文件
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 然后正常安装
pip install -r requirements.txt
```

#### 方案3: 升级pip和setuptools

```bash
# 激活虚拟环境
source .venv/bin/activate

# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 重试安装
pip install -r requirements.txt
```

#### 方案4: 逐个安装依赖（调试用）

```bash
# 分别安装每个包，找出问题所在
pip install psycopg2-binary
pip install sqlalchemy
pip install python-dotenv
pip install pydantic
pip install pydantic-settings
pip install flask
pip install flask-cors
pip install loguru
```

---

### 常见问题2: Python版本过低

**检查Python版本：**
```bash
python3 --version
```

**如果版本低于3.9，需要升级Python：**

```bash
# Rocky Linux 9 安装Python 3.9+
sudo dnf install python3.9 python3.9-devel

# 使用指定版本创建虚拟环境
python3.9 -m venv .venv
source .venv/bin/activate
```

---

### 常见问题3: 缺少编译工具

某些包（如psycopg2）需要编译，如果缺少编译工具会报错。

**安装必要的开发工具：**

```bash
# Rocky Linux 9 / CentOS
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel postgresql-devel

# Ubuntu / Debian
sudo apt-get install build-essential python3-dev libpq-dev
```

---

## 🌐 网络问题解决

### 配置全局pip镜像源

**Linux/macOS (~/.pip/pip.conf):**
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

**Windows (%APPDATA%\pip\pip.ini):**
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

### 临时使用镜像源

```bash
# 单次使用
pip install package_name -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装requirements.txt
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📦 依赖包说明

### 核心依赖

| 包名 | 版本要求 | 用途 |
|------|---------|------|
| psycopg2-binary | >=2.9.0 | PostgreSQL数据库驱动 |
| sqlalchemy | >=2.0.0 | ORM框架 |
| flask | >=3.0.0 | Web框架 |
| flask-cors | >=4.0.0 | CORS支持 |
| pydantic | >=2.0.0 | 数据验证 |
| pydantic-settings | >=2.0.0 | 配置管理 |
| python-dotenv | >=1.0.0 | 环境变量加载 |
| loguru | >=0.7.0 | 日志工具 |

### 版本兼容性

requirements.txt已调整为使用版本范围（`>=x.x.x,<y.0.0`）而非固定版本，以提高在不同系统上的兼容性。

---

## 🔍 验证安装

安装完成后，验证环境：

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 检查Python版本
python --version
# 应显示: Python 3.9.x 或更高

# 3. 检查已安装的包
pip list

# 4. 验证关键包
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"

# 5. 运行测试（如果有）
# python -m pytest
```

---

## 📞 获取帮助

如果遇到其他问题：

1. **查看日志：**
   ```bash
   tail -f logs/flask_server.log
   ```

2. **检查服务状态：**
   ```bash
   ./bin/health.sh
   ```

3. **查看详细错误信息：**
   ```bash
   # 使用-v标志安装，查看详细信息
   pip install -r requirements.txt -v
   ```

4. **清理并重新安装：**
   ```bash
   # 删除虚拟环境
   rm -rf .venv
   
   # 重新运行setup
   ./bin/setup.sh
   ```

---

## 🎯 推荐的国内镜像源

| 镜像源 | URL | 特点 |
|--------|-----|------|
| 清华大学 | https://pypi.tuna.tsinghua.edu.cn/simple | 速度快，更新及时 |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ | 稳定可靠 |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ | 教育网优化 |
| 豆瓣 | https://pypi.douban.com/simple/ | 老牌镜像 |

---

## ✅ 最佳实践

1. **始终使用虚拟环境** - 隔离项目依赖
2. **配置镜像源** - 加速包下载（特别是在中国大陆）
3. **保持pip最新** - `pip install --upgrade pip`
4. **记录依赖版本** - 有新包时更新 `requirements.txt`
5. **定期更新** - 但在生产环境要谨慎测试

---

## 📝 版本历史

- **v1.1** - 2025-10-24
  - 调整依赖版本为范围版本，提高兼容性
  - 添加Rocky Linux支持
  - 改进setup.sh错误处理
  
- **v1.0** - 2025-10-23
  - 初始版本
  - 基础依赖配置

