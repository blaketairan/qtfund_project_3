"""
Gunicorn配置文件

用于生产环境部署，支持长时间查询（10分钟超时）
"""

import os
import multiprocessing

# 服务器绑定
bind = "0.0.0.0:8000"

# 工作进程数（推荐：CPU核心数 × 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1
max_workers = 8  # 最大工作进程数
if workers > max_workers:
    workers = max_workers

# 工作进程类型
worker_class = "sync"  # 同步工作进程（适合CPU密集型任务）

# 超时配置（支持长时间查询）
timeout = 600  # 10分钟请求超时
graceful_timeout = 630  # 优雅关闭超时（稍长于timeout）
keepalive = 5  # 保持连接时间

# 日志配置
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

accesslog = os.path.join(log_dir, 'gunicorn_access.log')
errorlog = os.path.join(log_dir, 'gunicorn_error.log')
loglevel = 'info'

# 进程命名
proc_name = 'qtfund_api'

# 守护进程
daemon = False  # 不作为守护进程运行（便于调试）

# 性能优化
worker_connections = 1000  # 每个工作进程的最大连接数
max_requests = 1000  # 工作进程处理请求数上限后重启（防止内存泄漏）
max_requests_jitter = 50  # 随机抖动，避免所有进程同时重启

# 启动前回调
def on_starting(server):
    """服务器启动前执行"""
    print(f"Gunicorn正在启动...")
    print(f"绑定地址: {bind}")
    print(f"工作进程数: {workers}")
    print(f"请求超时: {timeout}秒")

# 工作进程启动后回调
def post_worker_init(worker):
    """工作进程启动后执行"""
    print(f"工作进程 {worker.pid} 已启动")

