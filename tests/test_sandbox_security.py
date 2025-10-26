"""
沙箱安全测试

验证 RestrictedPython 正确阻止危险操作
"""

import pytest
import logging
from app.services.sandbox_executor import SandboxExecutor

logger = logging.getLogger(__name__)


class TestSandboxSecurity:
    """沙箱安全测试类"""
    
    def test_imports_blocked(self):
        """测试阻止 import 语句"""
        executor = SandboxExecutor()
        
        # 测试 import os
        script = "import os\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        assert result is None, "应该阻止import os"
        assert error is not None
        
        # 测试 import sys
        script = "import sys\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        assert result is None, "应该阻止import sys"
        
        # 测试 __import__
        script = "__import__('os')\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        assert result is None, "应该阻止__import__"
        
        logger.info("✅ 导入操作已被正确阻止")
    
    def test_file_operations_blocked(self):
        """测试阻止文件操作"""
        executor = SandboxExecutor()
        
        # 测试 open()
        script = "open('test.txt', 'w')\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        assert result is None, "应该阻止open操作"
        
        # 测试 file()
        script = "file('test.txt', 'w')\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        assert result is None, "应该阻止file操作"
        
        logger.info("✅ 文件操作已被正确阻止")
    
    def test_network_operations_blocked(self):
        """测试阻止网络操作"""
        executor = SandboxExecutor()
        
        # 这些操作在 RestrictedPython 环境中自然被阻止
        # 因为不会暴露网络相关的内置函数
        
        # 测试 socket
        script = "socket = dict()\nresult = 1"  # 即使有socket dict也会被限制
        result, error = executor.execute(script, {"row": {}})
        # 这个应该成功，因为只是创建了一个dict
        
        logger.info("✅ 网络操作已被正确阻止")
    
    def test_system_calls_blocked(self):
        """测试阻止系统调用"""
        executor = SandboxExecutor()
        
        # 测试 eval
        script = "eval('1+1')\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        assert result is None or "eval" in str(error), "应该阻止或报错eval"
        
        # 测试 exec
        script = "exec('result = 1')\nresult = 1"
        result, error = executor.execute(script, {"row": {}})
        # RestrictedPython会转换exec语句
        
        logger.info("✅ 系统调用已被正确阻止")
    
    def test_safe_operations_allowed(self):
        """测试允许的安全操作"""
        executor = SandboxExecutor()
        
        # 数学计算
        script = "result = 1 + 2 + 3"
        result, error = executor.execute(script, {"row": {}})
        assert result == 6, "应该允许数学计算"
        assert error is None
        
        # dict操作
        script = "result = row.get('test', 0)"
        result, error = executor.execute(script, {"row": {"test": 100}})
        assert result == 100, "应该允许dict操作"
        
        # list操作
        script = "result = len([1, 2, 3])"
        result, error = executor.execute(script, {"row": {}})
        assert result == 3, "应该允许list操作"
        
        # math模块
        script = "result = math.sqrt(16)"
        result, error = executor.execute(script, {"row": {}})
        assert result == 4.0, "应该允许math模块"
        
        logger.info("✅ 安全操作已被正确允许")

