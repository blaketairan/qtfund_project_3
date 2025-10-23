#!/usr/bin/env python3
"""
启动Flask股票数据查询服务器

日志说明：
- 服务器所有日志会自动保存到 logs/flask_server_*.log
- 同时也会在终端显示
- 最新日志链接: logs/flask_server_latest.log
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """主启动函数"""
    try:
        # 导入Flask应用
        from app import app
        
        logger.info("🚀 启动股票数据查询服务...")
        logger.info("📊 服务功能:")
        logger.info("   - 股票行情查询 (TimescaleDB)")
        logger.info("   - 股票信息查询 (数据库 + 本地JSON)")
        logger.info("   - 健康检查和版本信息")
        logger.info("")
        logger.info("🌐 访问地址:")
        logger.info("   - 主页: http://localhost:8000")
        logger.info("   - 健康检查: http://localhost:8000/api/health")
        logger.info("   - 版本信息: http://localhost:8000/api/version")
        logger.info("")
        logger.info("📝 日志文件:")
        logger.info("   - 所有服务器日志已自动保存到: logs/flask_server_*.log")
        logger.info("   - 查看最新日志: tail -f logs/flask_server.log")
        logger.info("")
        logger.info("⚠️  注意: 本服务仅提供查询功能，数据同步请使用端口7777的同步服务")
        logger.info("")
        
        # 启动Flask应用 (日志已在create_app中自动配置)
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        logger.error(f"❌ 导入错误: {e}")
        logger.error("请确保已安装所有依赖包: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

