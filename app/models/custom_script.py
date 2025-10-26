"""
自定义脚本模型

提供CRUD操作管理用户保存的计算脚本
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone, timedelta
from database.connection import Base
import logging

logger = logging.getLogger(__name__)


# 中国时区 UTC+8
CHINA_TZ = timezone(timedelta(hours=8))


def get_china_time() -> datetime:
    """获取中国时区当前时间"""
    return datetime.now(CHINA_TZ)


class CustomScript(Base):
    """自定义脚本模型
    
    存储用户创建的计算脚本供重复使用
    """
    
    __tablename__ = 'custom_scripts'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 脚本名称
    name = Column(String(100), nullable=False, comment='脚本名称')
    
    # 脚本描述
    description = Column(Text, nullable=True, comment='脚本描述')
    
    # Python脚本代码
    code = Column(Text, nullable=False, comment='Python脚本代码')
    
    # 时间戳
    created_at = Column(DateTime, default=get_china_time, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=get_china_time, onupdate=get_china_time, nullable=False, comment='更新时间')
    
    # 索引
    __table_args__ = (
        Index('idx_custom_scripts_name', 'name'),
        Index('idx_custom_scripts_created_at', 'created_at'),
        {'comment': '存储用户自定义Python计算脚本'}
    )
    
    def __repr__(self) -> str:
        return f"<CustomScript(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomScriptService:
    """自定义脚本服务类"""
    
    @staticmethod
    def save(name: str, code: str, description: str = None) -> 'CustomScript':
        """
        保存新脚本
        
        Args:
            name: 脚本名称
            code: 脚本代码
            description: 脚本描述
            
        Returns:
            CustomScript: 保存的脚本对象
        """
        from database.connection import db_manager
        
        with db_manager.get_session() as session:
            script = CustomScript(
                name=name,
                code=code,
                description=description
            )
            session.add(script)
            session.commit()
            session.refresh(script)
            return script
    
    @staticmethod
    def get_by_id(script_id: int) -> 'CustomScript':
        """
        根据ID获取脚本
        
        Args:
            script_id: 脚本ID
            
        Returns:
            CustomScript: 脚本对象，不存在则返回None
        """
        from database.connection import db_manager
        
        with db_manager.get_session() as session:
            return session.query(CustomScript).filter(
                CustomScript.id == script_id
            ).first()
    
    @staticmethod
    def get_all() -> list:
        """
        获取所有脚本
        
        Returns:
            List[CustomScript]: 脚本列表
        """
        from database.connection import db_manager
        
        with db_manager.get_session() as session:
            return session.query(CustomScript).order_by(
                CustomScript.created_at.desc()
            ).all()
    
    @staticmethod
    def update(script_id: int, name: str = None, code: str = None, description: str = None) -> 'CustomScript':
        """
        更新脚本
        
        Args:
            script_id: 脚本ID
            name: 新名称
            code: 新代码
            description: 新描述
            
        Returns:
            CustomScript: 更新后的脚本对象
        """
        from database.connection import db_manager
        
        with db_manager.get_session() as session:
            script = session.query(CustomScript).filter(
                CustomScript.id == script_id
            ).first()
            
            if not script:
                return None
            
            if name:
                script.name = name
            if code:
                script.code = code
            if description is not None:
                script.description = description
            
            script.updated_at = get_china_time()
            session.commit()
            session.refresh(script)
            return script
    
    @staticmethod
    def delete(script_id: int) -> bool:
        """
        删除脚本
        
        Args:
            script_id: 脚本ID
            
        Returns:
            bool: 是否删除成功
        """
        from database.connection import db_manager
        
        with db_manager.get_session() as session:
            script = session.query(CustomScript).filter(
                CustomScript.id == script_id
            ).first()
            
            if not script:
                return False
            
            session.delete(script)
            session.commit()
            return True

