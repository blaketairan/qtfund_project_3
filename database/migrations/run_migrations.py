"""
数据库迁移脚本

自动创建 custom_scripts 表（如果不存在）
"""

import logging
from sqlalchemy import inspect, text
from database.connection import db_manager, Base
from app.models.custom_script import CustomScript

logger = logging.getLogger(__name__)


def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    with db_manager.get_session() as session:
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        return table_name in tables


def create_custom_scripts_table():
    """创建 custom_scripts 表"""
    try:
        # 检查表是否已存在
        if check_table_exists('custom_scripts'):
            logger.info("✅ custom_scripts 表已存在，跳过创建")
            return True
        
        logger.info("🔄 开始创建 custom_scripts 表...")
        
        # 读取 SQL 文件
        sql_file = 'database/migrations/create_custom_scripts_table.sql'
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except FileNotFoundError:
            logger.warning(f"SQL文件未找到: {sql_file}")
            # 使用 SQLAlchemy 直接创建表
            return create_table_via_sqlalchemy()
        
        # 执行 SQL
        with db_manager.get_session() as session:
            # 分割SQL语句并执行
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            for stmt in statements:
                if stmt:
                    session.execute(text(stmt))
            session.commit()
        
        logger.info("✅ custom_scripts 表创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建 custom_scripts 表失败: {e}")
        return False


def create_table_via_sqlalchemy():
    """使用 SQLAlchemy 创建表（备用方法）"""
    try:
        logger.info("🔄 使用 SQLAlchemy 创建 custom_scripts 表...")
        
        # 创建表
        CustomScript.__table__.create(db_manager.engine, checkfirst=True)
        
        logger.info("✅ custom_scripts 表创建成功（通过SQLAlchemy）")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建 custom_scripts 表失败: {e}")
        return False


if __name__ == '__main__':
    """直接运行此脚本以创建表"""
    from config.logging_config import setup_logging
    
    # 设置日志
    setup_logging()
    
    # 创建表
    success = create_custom_scripts_table()
    
    if success:
        print("✅ 数据库迁移完成")
    else:
        print("❌ 数据库迁移失败")
        exit(1)

