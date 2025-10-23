# 服务管理脚本

这个目录包含了管理股票数据查询服务的便捷脚本。

## 📋 脚本列表

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start.sh` | 启动服务 | 后台启动查询服务（端口8000） |
| `health.sh` | 健康检查 | 检查服务运行状态和健康状况 |
| `stop.sh` | 停止服务 | 优雅停止服务，清理进程 |

## 🚀 使用方法

### 启动服务
```bash
./bin/start.sh
```

功能：
- ✅ 自动检查端口占用
- ✅ 激活虚拟环境（如果存在）
- ✅ 检查依赖包
- ✅ 后台启动服务
- ✅ 保存PID到文件（query_service.pid）
- ✅ 显示服务信息和日志位置

### 健康检查
```bash
./bin/health.sh
```

检查内容：
- ✅ 进程是否运行
- ✅ 端口是否监听（8000）
- ✅ API健康检查
- ✅ 数据库连接状态
- ✅ 服务版本信息

### 停止服务
```bash
./bin/stop.sh
```

停止方式（多重保险）：
- 🛑 通过PID文件停止（query_service.pid）
- 🛑 通过端口8000查找并停止
- 🛑 通过项目路径精确匹配
- 🛑 强制停止未响应的进程
- ⚠️ **不会影响同步服务（7777端口）**

## 🔒 安全隔离机制

为了确保查询服务和同步服务互不干扰，采用了以下隔离措施：

### 1. 独立的PID文件
- 查询服务（project_3）: `logs/query_service.pid`
- 同步服务（project_2）: `logs/sync_service.pid`

### 2. 端口区分
- 查询服务: 8000
- 同步服务: 7777

### 3. 精确的进程匹配
stop.sh使用以下方式精确识别进程：

```bash
# 方法1: 通过项目路径匹配
pgrep -f "qtfund_project_3.*start_flask_app.py"

# 方法2: 通过端口确认
lsof -p $pid | grep ':8000'

# 方法3: 双重验证
ps -p $pid -o args= | grep "qtfund_project_3"
```

### 4. 测试验证
```bash
# 启动两个服务
cd /Users/terrell/qt/qtfund_project_2 && ./bin/start.sh
cd /Users/terrell/qt/qtfund_project_3 && ./bin/start.sh

# 停止查询服务，验证同步服务不受影响
cd /Users/terrell/qt/qtfund_project_3 && ./bin/stop.sh
curl http://localhost:7777/api/health  # 应该仍然正常

# 停止同步服务，验证查询服务不受影响
cd /Users/terrell/qt/qtfund_project_2 && ./bin/stop.sh
curl http://localhost:8000/api/health  # 应该仍然正常
```

## 📝 使用示例

### 完整流程
```bash
# 1. 启动服务
./bin/start.sh

# 2. 检查服务状态
./bin/health.sh

# 3. 查看实时日志（可选）
tail -f logs/query_service.log

# 4. 停止服务
./bin/stop.sh
```

### 快速重启
```bash
./bin/stop.sh && ./bin/start.sh
```

### 与同步服务协同使用
```bash
# 终端1: 启动同步服务
cd /Users/terrell/qt/qtfund_project_2
./bin/start.sh

# 终端2: 启动查询服务
cd /Users/terrell/qt/qtfund_project_3
./bin/start.sh

# 验证两个服务都正常
curl http://localhost:7777/api/health  # 同步服务
curl http://localhost:8000/api/health  # 查询服务
```

## 📊 日志文件

启动后会生成以下日志文件：

| 文件 | 内容 |
|------|------|
| `logs/query_service.pid` | 服务进程ID |
| `logs/query_service.log` | 服务启动日志 |
| `logs/flask_server.log` | Flask详细日志 |

## 🔍 故障排查

### 服务无法启动
```bash
# 检查端口占用
lsof -i :8000

# 查看启动日志
cat logs/query_service.log

# 检查依赖
pip install -r requirements.txt
```

### 服务无法停止
```bash
# 查找所有相关进程
ps aux | grep qtfund_project_3 | grep start_flask_app

# 手动强制停止
kill -9 <PID>

# 释放端口
lsof -ti:8000 | xargs kill -9
```

### 误杀同步服务？
如果担心误杀，可以先检查：
```bash
# 查看8000端口的进程
lsof -i :8000

# 查看7777端口的进程
lsof -i :7777

# 确认进程的工作目录
ps -p <PID> -o args=
```

## ⚠️ 注意事项

1. **工作目录**: 脚本会自动切换到项目根目录，可以从任意位置调用
2. **虚拟环境**: 如果存在 `.venv` 目录，会自动激活
3. **PID文件**: 服务停止后会自动清理PID文件
4. **进程隔离**: stop.sh只会停止查询服务，不会影响同步服务
5. **多重确认**: 在停止进程前会验证端口和路径，确保不误杀

## 🎯 高级用法

### 查看服务信息
```bash
# 查看PID
cat logs/query_service.pid

# 查看进程详情
ps -p $(cat logs/query_service.pid) -f

# 查看端口占用
lsof -i :8000
```

### 监控服务
```bash
# 实时监控日志
tail -f logs/query_service.log

# 监控进程资源使用
top -pid $(cat logs/query_service.pid)

# 监控端口连接
watch -n 1 'lsof -i :8000'
```

### 同时管理两个服务
```bash
# 创建统一管理脚本
cat > /tmp/manage_both.sh << 'EOF'
#!/bin/bash
case "$1" in
  start)
    cd /Users/terrell/qt/qtfund_project_2 && ./bin/start.sh
    cd /Users/terrell/qt/qtfund_project_3 && ./bin/start.sh
    ;;
  stop)
    cd /Users/terrell/qt/qtfund_project_3 && ./bin/stop.sh
    cd /Users/terrell/qt/qtfund_project_2 && ./bin/stop.sh
    ;;
  health)
    echo "=== 同步服务(7777) ==="
    cd /Users/terrell/qt/qtfund_project_2 && ./bin/health.sh
    echo ""
    echo "=== 查询服务(8000) ==="
    cd /Users/terrell/qt/qtfund_project_3 && ./bin/health.sh
    ;;
  *)
    echo "Usage: $0 {start|stop|health}"
    ;;
esac
EOF
chmod +x /tmp/manage_both.sh

# 使用
/tmp/manage_both.sh start
/tmp/manage_both.sh health
/tmp/manage_both.sh stop
```

## 📞 支持

如有问题，请查看：
- 项目文档: `../README.md`
- 兼容性说明: `COMPATIBILITY.md`
- 同步服务脚本: `/Users/terrell/qt/qtfund_project_2/bin/`

