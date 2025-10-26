"""
沙箱执行器模块

使用 RestrictedPython 提供安全的 Python 脚本执行环境
阻止危险操作：文件访问、导入、系统调用
"""

import math
import signal
import logging
from typing import Any, Dict, Optional, Tuple
from RestrictedPython import compile_restricted, safe_globals

logger = logging.getLogger(__name__)


class SandboxExecutor:
    """沙箱执行器 - 安全执行用户Python脚本"""
    
    # 超时限制（秒）
    TIMEOUT_SECONDS = 10
    
    def __init__(self):
        """初始化沙箱执行器"""
        self._configure_safe_globals()
    
    def _configure_safe_globals(self):
        """配置安全的内置函数和模块"""
        # 基础类型和函数
        safe = safe_globals.copy()
        
        # 添加数学模块
        safe['math'] = math
        
        # 添加基础内置函数
        safe['abs'] = abs
        safe['min'] = min
        safe['max'] = max
        safe['sum'] = sum
        safe['round'] = round
        safe['len'] = len
        safe['range'] = range
        safe['zip'] = zip
        safe['enumerate'] = enumerate
        safe['reversed'] = reversed
        safe['sorted'] = sorted
        
        # 添加基础类型
        safe['dict'] = dict
        safe['list'] = list
        safe['tuple'] = tuple
        safe['set'] = set
        safe['str'] = str
        safe['int'] = int
        safe['float'] = float
        safe['bool'] = bool
        
        # 添加必要的内置函数（供脚本使用）
        safe['globals'] = lambda: safe  # Allow globals() access in scripts
        
        # 添加历史数据访问函数
        safe['get_history'] = self._get_history_function
        
        self._safe_globals = safe
    
    def _get_history_function(self, symbol: str, days: int) -> list:
        """
        获取股票历史价格数据（提供给脚本调用）
        
        Args:
            symbol: 股票代码（如 'SH.600519'）
            days: 获取交易天数（最多1000天）
            
        Returns:
            历史价格数据列表，每个元素包含 close_price, trade_date, volume, price_change_pct
        """
        # 输入验证
        if not symbol or not isinstance(symbol, str):
            return []
        
        if not isinstance(days, int) or days < 1 or days > 1000:
            days = 250  # 默认250天
        
        try:
            from database.connection import db_manager
            from models.stock_data import StockDailyData
            from sqlalchemy import desc
            
            with db_manager.get_session() as session:
                query = session.query(StockDailyData).filter(
                    StockDailyData.symbol == symbol
                ).order_by(desc(StockDailyData.trade_date)).limit(days)
                
                results = query.all()
                
                # 格式化返回数据
                return [{
                    'close_price': float(r.close_price) if r.close_price else None,
                    'trade_date': r.trade_date.strftime('%Y-%m-%d') if r.trade_date else None,
                    'volume': int(r.volume) if r.volume else 0,
                    'price_change_pct': float(r.price_change_pct) if r.price_change_pct else None
                } for r in results]
                
        except Exception as e:
            logger.error(f"Error retrieving history for {symbol}: {e}")
            return []
    
    def execute(self, script_code: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        """
        执行Python脚本
        
        Args:
            script_code: Python脚本代码（必须包含result=...语句）
            context: 传递给脚本的上下文变量（默认包含'row'数据）
            
        Returns:
            Tuple[result, error_message]:
                - result: 计算结果（如果成功）
                - error_message: 错误消息（如果失败）
        """
        try:
            # 准备执行上下文
            exec_globals = self._safe_globals.copy()
            
            if context:
                exec_globals.update(context)
                logger.info(f"Script execution context keys: {list(context.keys())}")
                if 'row' in context:
                    logger.info(f"Row data keys: {list(context['row'].keys()) if isinstance(context['row'], dict) else 'not a dict'}")
            
            # 编译脚本（使用RestrictedPython）
            compile_result = compile_restricted(
                script_code,
                filename='<inline-script>',
                mode='exec'
            )
            
            # 处理不同的返回值格式
            # 新版本可能返回tuple: (code, errors, warnings)
            # 旧版本返回对象，有.code和.errors属性
            if isinstance(compile_result, tuple):
                byte_code, errors, warnings = compile_result[:3] if len(compile_result) >= 3 else (compile_result, None, None)
                if errors:
                    return None, self._format_compile_errors(errors)
            else:
                # 旧版本API
                byte_code = compile_result
                if hasattr(byte_code, 'errors') and byte_code.errors:
                    return None, self._format_compile_errors(byte_code.errors)
                # 旧版本可能需要访问.code属性
                if hasattr(byte_code, 'code'):
                    byte_code = byte_code.code
            
            # 执行脚本
            try:
                exec(byte_code, exec_globals)
                
                # 尝试获取返回值
                result = exec_globals.get('result', None)
                
                logger.info(f"Script execution result: {result}, type: {type(result).__name__}")
                
                # 允许 result 为 None（表示数据不足等情况）
                # 如果 result 有值，验证类型
                if result is not None and not isinstance(result, (int, float, bool, type(None))):
                    logger.error(f"Invalid return type: {type(result).__name__}, value: {result}")
                    return None, f"Return value must be a number, bool, or None, got {type(result).__name__}"
                
                # 返回 result（可能是 None）和 None 错误
                if result is None:
                    logger.warning("Script returned None")
                
                return result, None
                
            except Exception as e:
                logger.error(f"Script execution runtime error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None, self._format_runtime_error(e)
                
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            return None, f"Execution failed: {str(e)}"
    
    def _format_compile_errors(self, errors) -> str:
        """格式化编译错误"""
        if not errors:
            return "Unknown compilation error"
        
        # RestrictedPython 错误格式
        error_str = str(errors)
        
        # 尝试提取行号
        if "line" in error_str.lower():
            return error_str
        
        return f"Compilation error: {error_str}"
    
    def _format_runtime_error(self, exception: Exception) -> str:
        """格式化运行时错误"""
        error_type = type(exception).__name__
        error_message = str(exception)
        
        return f"{error_type}: {error_message}"
    
    def validate_syntax(self, script_code: str) -> Tuple[bool, Optional[str]]:
        """
        验证脚本语法
        
        Args:
            script_code: Python脚本代码
            
        Returns:
            Tuple[is_valid, error_message]
        """
        try:
            logger.info(f"开始验证脚本语法，脚本长度={len(script_code)}")
            
            compile_result = compile_restricted(
                script_code,
                filename='<inline-script>',
                mode='exec'
            )
            
            # 处理不同的返回值格式
            if isinstance(compile_result, tuple):
                code, errors, warnings = compile_result[:3] if len(compile_result) >= 3 else (compile_result, None, None)
                if errors:
                    error_msg = self._format_compile_errors(errors)
                    logger.error(f"语法验证失败: {error_msg}")
                    return False, error_msg
            else:
                # 旧版本API
                if hasattr(compile_result, 'errors') and compile_result.errors:
                    error_msg = self._format_compile_errors(compile_result.errors)
                    logger.error(f"语法验证失败: {error_msg}")
                    return False, error_msg
            
            logger.info("语法验证通过")
            return True, None
            
        except Exception as e:
            logger.error(f"语法验证异常: {e}")
            return False, f"Syntax validation failed: {str(e)}"

