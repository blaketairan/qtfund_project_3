#!/usr/bin/env bash
#
# 启动股票数据查询服务
# 端口: 8000
# 兼容: Linux, macOS
#

set -e  # 遇到错误立即退出

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 启动股票数据查询服务...${NC}"
echo ""

# 检查端口是否被占用（兼容Linux和macOS）
PORT_CHECK=$(command -v lsof >/dev/null 2>&1 && lsof -Pi :8000 -sTCP:LISTEN -t 2>/dev/null || netstat -tuln 2>/dev/null | grep ':8000 ' || true)
if [ -n "$PORT_CHECK" ]; then
    echo -e "${YELLOW}⚠️  警告: 端口 8000 已被占用${NC}"
    echo "   请先停止现有服务: ./bin/stop.sh"
    exit 1
fi

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ 检测到虚拟环境，正在激活...${NC}"
    source .venv/bin/activate
fi

# 检查依赖
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${RED}❌ 缺少依赖包，请先安装: pip install -r requirements.txt${NC}"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动服务（使用Gunicorn以支持长时间查询）
echo -e "${GREEN}📍 启动查询服务 (端口 8000, 超时10分钟)...${NC}"

# 检查是否安装Gunicorn
if python -c "import gunicorn" 2>/dev/null; then
    echo "   使用 Gunicorn 启动（支持长时间查询）"
    nohup gunicorn -c config/gunicorn_config.py start_flask_app:app > logs/query_service.log 2>&1 &
    PID=$!
else
    echo -e "${YELLOW}   Gunicorn未安装，使用开发服务器（不支持10分钟超时）${NC}"
    nohup python start_flask_app.py > logs/query_service.log 2>&1 &
    PID=$!
fi

# 保存PID到文件（使用不同的文件名避免冲突）
echo $PID > logs/query_service.pid

# 等待服务启动
echo "   等待服务启动..."
sleep 3

# 检查服务是否成功启动（兼容Linux和macOS）
if kill -0 $PID 2>/dev/null; then
    echo ""
    echo -e "${GREEN}✅ 查询服务启动成功！${NC}"
    echo ""
    echo "📋 服务信息:"
    echo "   PID: $PID"
    echo "   端口: 8000"
    echo "   地址: http://localhost:8000"
    echo ""
    echo "📝 日志文件:"
    echo "   主日志: logs/query_service.log"
    echo "   详细日志: logs/flask_server.log"
    echo ""
    echo "🔍 查看实时日志:"
    echo "   tail -f logs/query_service.log"
    echo ""
    echo "🛑 停止服务:"
    echo "   ./bin/stop.sh"
    echo ""
    echo "💚 健康检查:"
    echo "   ./bin/health.sh"
    echo ""
else
    echo -e "${RED}❌ 服务启动失败，请查看日志: logs/query_service.log${NC}"
    exit 1
fi

