"""
Flask主应用 - 股票数据查询服务

提供纯净的数据库查询API接口
"""

from flask import Flask
from flask_cors import CORS
from config.settings import db_config, app_config
from config.logging_config import setup_flask_logging
import logging

logger = logging.getLogger(__name__)


def create_app():
    """创建Flask应用工厂函数"""
    app = Flask(__name__)
    
    # 配置日志系统 - 自动输出到文件
    setup_flask_logging(app)
    
    # 配置CORS
    CORS(app, 
         origins=["*"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # 应用配置
    app.config.update({
        'SECRET_KEY': app_config.secret_key,  # 从配置文件读取，支持环境变量
        'JSON_AS_ASCII': False,  # 支持中文JSON响应
        'JSONIFY_PRETTYPRINT_REGULAR': True,  # 美化JSON输出
        'DATABASE_URL': db_config.database_url,
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB最大请求大小
    })
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 应用启动时初始化
    with app.app_context():
        init_app_context(app)
    
    return app


def register_blueprints(app):
    """注册蓝图"""
    # 导入并注册各个模块的蓝图
    from app.routes.stock_price import stock_price_bp
    from app.routes.stock_info import stock_info_bp
    from app.routes.health import health_bp
    from app.routes.custom_calculation import custom_calculation_bp
    
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(stock_price_bp, url_prefix='/api/stock-price')
    app.register_blueprint(stock_info_bp, url_prefix='/api/stock-info')
    app.register_blueprint(custom_calculation_bp, url_prefix='/api/custom-calculations')


def register_error_handlers(app):
    """注册全局错误处理器"""
    from app.utils.responses import create_error_response
    
    @app.errorhandler(400)
    def bad_request(error):
        return create_error_response(400, "请求参数错误", str(error))
    
    @app.errorhandler(404)
    def not_found(error):
        return create_error_response(404, "资源未找到", "请求的资源不存在")
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return create_error_response(405, "方法不允许", "请求方法不被允许")
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return create_error_response(500, "服务器内部错误", "请稍后重试")


def init_app_context(app):
    """初始化应用上下文"""
    logger.info("初始化股票数据查询API应用...")
    
    # 测试数据库连接
    try:
        from database.connection import db_manager
        if db_manager.test_connection():
            logger.info("✅ 数据库连接正常")
        else:
            logger.warning("⚠️ 数据库连接失败")
    except Exception as e:
        logger.error(f"❌ 数据库连接错误: {e}")
    
    # 加载股票清单
    try:
        from constants.stock_lists_loader import load_stock_lists
        if load_stock_lists():
            logger.info("✅ 股票清单加载成功")
        else:
            logger.warning("⚠️ 股票清单加载失败")
    except Exception as e:
        logger.error(f"❌ 股票清单加载错误: {e}")
    
    # 自动运行数据库迁移（创建 custom_scripts 表）
    try:
        from database.migrations.run_migrations import create_custom_scripts_table
        create_custom_scripts_table()
    except Exception as e:
        logger.warning(f"⚠️ 数据库迁移跳过: {e}")
    
    logger.info("🚀 股票数据查询API应用初始化完成")


# 创建应用实例
app = create_app()


@app.route('/')
def index():
    """根路径 - API服务信息"""
    from app.utils.responses import create_success_response
    
    api_info = {
        "name": "股票数据查询服务",
        "version": "1.0.0",
        "description": "纯净的数据库查询服务",
        "endpoints": {
            "健康检查": "/api/health",
            "版本信息": "/api/version",
            "股票行情查询": {
                "查询行情数据": "/api/stock-price/query",
                "获取股票信息": "/api/stock-price/info/<symbol>",
                "列出所有股票": "/api/stock-price/list"
            },
            "股票信息查询": {
                "本地JSON查询": "/api/stock-info/local",
                "统计信息": "/api/stock-info/statistics"
            }
        },
        "note": "本服务仅提供查询功能，数据同步请使用同步服务(端口7777)"
    }
    
    return create_success_response(data=api_info, message="股票数据查询服务运行中")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

