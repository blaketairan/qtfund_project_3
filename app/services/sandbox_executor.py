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
from RestrictedPython.transformer import RestrictingNodeTransformer
from RestrictedPython._compat import IS_PY38_OR_GREATER

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
        
        self._safe_globals = safe
    
    def execute(self, script_code: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        """
        执行Python脚本
        
        Args:
            script_code: Python脚本代码
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
            
            # 编译脚本（使用RestrictedPython）
            byte_code = compile_restricted(
                script_code,
                filename='<inline-script>',
                mode='exec'
            )
            
            if byte_code.errors:
                return None, self._format_compile_errors(byte_code.errors)
            
            # 执行脚本
            try:
                exec(byte_code.code, exec_globals)
                
                # 尝试获取返回值
                result = exec_globals.get('result', None)
                if result is None:
                    return None, "Script must set 'result' variable with return value"
                
                # 验证返回类型
                if not isinstance(result, (int, float, bool)):
                    return None, f"Return value must be a number, got {type(result).__name__}"
                
                return result, None
                
            except Exception as e:
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
            byte_code = compile_restricted(
                script_code,
                filename='<inline-script>',
                mode='exec'
            )
            
            if byte_code.errors:
                return False, self._format_compile_errors(byte_code.errors)
            
            return True, None
            
        except Exception as e:
            return False, f"Syntax validation failed: {str(e)}"

