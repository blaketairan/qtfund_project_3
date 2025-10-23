#!/usr/bin/env bash
#
# 停止股票数据查询服务
# 兼容: Linux, macOS
# 注意: 只停止查询服务(端口8000)，不影响同步服务(端口7777)
#

set +e  # 允许命令失败，因为我们要尝试多种停止方式

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 停止股票数据查询服务...${NC}"
echo ""

# 方法1: 通过PID文件停止（使用查询服务专用的PID文件）
PID_FILE="logs/query_service.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "📍 找到PID文件 (PID: $PID)"
    
    # 使用kill -0检查进程是否存在（兼容Linux和macOS）
    if kill -0 $PID 2>/dev/null; then
        echo "   正在停止进程..."
        kill $PID 2>/dev/null
        
        # 等待进程结束
        for i in $(seq 1 10); do
            if ! kill -0 $PID 2>/dev/null; then
                echo -e "   ${GREEN}✅ 进程已停止${NC}"
                rm -f "$PID_FILE"
                break
            fi
            sleep 1
        done
        
        # 如果进程还在运行，强制停止
        if kill -0 $PID 2>/dev/null; then
            echo "   进程未响应，强制停止..."
            kill -9 $PID 2>/dev/null
            sleep 1
            if ! kill -0 $PID 2>/dev/null; then
                echo -e "   ${GREEN}✅ 进程已强制停止${NC}"
                rm -f "$PID_FILE"
            else
                echo -e "   ${RED}❌ 无法停止进程${NC}"
                exit 1
            fi
        fi
    else
        echo -e "   ${YELLOW}⚠️  进程不存在，清理PID文件${NC}"
        rm -f "$PID_FILE"
    fi
else
    echo -e "${YELLOW}⚠️  未找到PID文件${NC}"
fi

echo ""

# 方法2: 通过端口查找并停止（只针对8000端口，避免误杀7777）
echo "📍 检查端口 8000..."
PORT_PID=""

# 尝试使用lsof
if command -v lsof >/dev/null 2>&1; then
    PORT_PID=$(lsof -ti:8000 2>/dev/null || true)
# 如果没有lsof，尝试使用fuser（Linux）
elif command -v fuser >/dev/null 2>&1; then
    PORT_PID=$(fuser 8000/tcp 2>/dev/null | tr -d ' ' || true)
# 如果没有fuser，尝试使用ss（现代Linux）
elif command -v ss >/dev/null 2>&1; then
    PORT_PID=$(ss -tlnp 2>/dev/null | grep ':8000 ' | grep -oP 'pid=\K[0-9]+' || true)
fi

if [ -n "$PORT_PID" ]; then
    echo "   发现占用端口的进程 (PID: $PORT_PID)"
    echo "   正在停止..."
    
    for pid in $PORT_PID; do
        kill $pid 2>/dev/null || true
    done
    sleep 2
    
    # 检查是否停止
    PORT_CHECK=false
    if command -v lsof >/dev/null 2>&1; then
        lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 && PORT_CHECK=true
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln 2>/dev/null | grep -q ':8000 ' && PORT_CHECK=true
    fi
    
    if [ "$PORT_CHECK" = true ]; then
        echo "   进程未响应，强制停止..."
        for pid in $PORT_PID; do
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
    fi
    
    # 再次检查
    PORT_CHECK=false
    if command -v lsof >/dev/null 2>&1; then
        lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 && PORT_CHECK=true
    fi
    
    if [ "$PORT_CHECK" = false ]; then
        echo -e "   ${GREEN}✅ 端口已释放${NC}"
    else
        echo -e "   ${RED}❌ 端口仍被占用${NC}"
    fi
else
    echo "   端口未被占用"
fi

echo ""

# 方法3: 通过项目路径精确查找进程（避免误杀同步服务）
echo "📍 检查查询服务相关进程..."
PYTHON_PIDS=""

# 使用更精确的匹配：包含qtfund_project_3路径的进程
if command -v pgrep >/dev/null 2>&1; then
    # 查找包含当前项目路径的start_flask_app.py进程
    PYTHON_PIDS=$(pgrep -f "qtfund_project_3.*start_flask_app.py" 2>/dev/null || true)
else
    # fallback: 使用ps和grep，但要更精确
    PYTHON_PIDS=$(ps aux | grep "[s]tart_flask_app.py" | grep "qtfund_project_3" | awk '{print $2}' || true)
fi

if [ -n "$PYTHON_PIDS" ]; then
    echo "   发现查询服务相关进程:"
    for pid in $PYTHON_PIDS; do
        if kill -0 $pid 2>/dev/null; then
            # 再次确认是8000端口的进程，不是7777
            if command -v lsof >/dev/null 2>&1; then
                if lsof -p $pid 2>/dev/null | grep -q ':8000'; then
                    echo "   - PID: $pid (确认是查询服务)"
                else
                    echo "   - PID: $pid (跳过，不是查询服务)"
                    continue
                fi
            else
                echo "   - PID: $pid"
            fi
        fi
    done
    
    echo "   正在停止查询服务相关进程..."
    for pid in $PYTHON_PIDS; do
        if kill -0 $pid 2>/dev/null; then
            # 双重确认：检查是否使用8000端口
            IS_QUERY_SERVICE=false
            if command -v lsof >/dev/null 2>&1; then
                if lsof -p $pid 2>/dev/null | grep -q ':8000'; then
                    IS_QUERY_SERVICE=true
                fi
            else
                # 如果没有lsof，检查进程路径
                if ps -p $pid -o args= 2>/dev/null | grep -q "qtfund_project_3"; then
                    IS_QUERY_SERVICE=true
                fi
            fi
            
            if [ "$IS_QUERY_SERVICE" = true ]; then
                kill $pid 2>/dev/null || true
            fi
        fi
    done
    sleep 2
    
    # 检查是否还有进程
    REMAINING=""
    if command -v pgrep >/dev/null 2>&1; then
        REMAINING=$(pgrep -f "qtfund_project_3.*start_flask_app.py" 2>/dev/null || true)
    else
        REMAINING=$(ps aux | grep "[s]tart_flask_app.py" | grep "qtfund_project_3" | awk '{print $2}' || true)
    fi
    
    if [ -n "$REMAINING" ]; then
        echo "   强制停止残留的查询服务进程..."
        for pid in $REMAINING; do
            # 再次确认后强制停止
            if ps -p $pid -o args= 2>/dev/null | grep -q "qtfund_project_3"; then
                kill -9 $pid 2>/dev/null || true
            fi
        done
    fi
    
    echo -e "   ${GREEN}✅ 查询服务进程已清理${NC}"
else
    echo "   未发现查询服务相关进程"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ 查询服务已完全停止${NC}"
echo ""
echo "ℹ️  注意: 此脚本只停止查询服务(8000)，同步服务(7777)不受影响"
echo ""
echo "🚀 重新启动服务:"
echo "   ./bin/start.sh"
echo ""

