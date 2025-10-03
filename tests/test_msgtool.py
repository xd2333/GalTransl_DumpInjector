"""
msg-tool模式单元测试
测试msg-tool相关功能的正确性
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

from src.utils.msgtool_executor import MsgToolExecutor
from src.core.msgtool_processor import MsgToolProcessor
from src.utils.validators import MsgToolValidator
from src.utils.command_executor import ExecutionResult, ExecutionStatus


class TestMsgToolExecutor(unittest.TestCase):
    """测试MsgToolExecutor"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.executor = MsgToolExecutor(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_supported_engines(self):
        """测试获取支持的引擎列表"""
        engines = self.executor.get_supported_engines()
        
        self.assertIsInstance(engines, list)
        self.assertIn("自动检测", engines)
        self.assertIn("artemis - AST文件", engines)
        self.assertIn("bgi/ethornell - 通用脚本", engines)
    
    def test_escape_path(self):
        """测试路径转义"""
        # 不含空格的路径
        normal_path = "C:\\test\\folder"
        self.assertEqual(self.executor._escape_path(normal_path), normal_path)
        
        # 含空格的路径
        space_path = "C:\\test folder\\subfolder"
        expected = '"C:\\test folder\\subfolder"'
        self.assertEqual(self.executor._escape_path(space_path), expected)
    
    def test_get_script_type_param(self):
        """测试引擎类型参数提取"""
        # 自动检测
        self.assertIsNone(self.executor._get_script_type_param("自动检测"))
        
        # 带描述的引擎
        engine_with_desc = "artemis - AST文件"
        self.assertEqual(self.executor._get_script_type_param(engine_with_desc), "artemis")
        
        # 不带描述的引擎
        engine_no_desc = "bgi/ethornell"
        self.assertEqual(self.executor._get_script_type_param(engine_no_desc), "bgi/ethornell")
    
    def test_check_tool_available(self):
        """测试工具可用性检查"""
        # 工具不存在时
        self.assertFalse(self.executor.check_tool_available())
        
        # 创建虚拟工具文件
        tool_path = os.path.join(self.temp_dir, "msg-tool.exe")
        with open(tool_path, 'w') as f:
            f.write("dummy")
        os.chmod(tool_path, 0o755)
        
        # 工具存在时
        self.assertTrue(self.executor.check_tool_available())


class TestMsgToolProcessor(unittest.TestCase):
    """测试MsgToolProcessor"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = MsgToolProcessor(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.core.msgtool_processor.MsgToolExecutor')
    def test_extract_text_tool_unavailable(self, mock_executor_class):
        """测试工具不可用时的提取操作"""
        mock_executor = Mock()
        mock_executor.check_tool_available.return_value = False
        mock_executor_class.return_value = mock_executor
        
        processor = MsgToolProcessor()
        processor.executor = mock_executor
        
        result = processor.extract_text("/test/script", "/test/json")
        
        self.assertFalse(result.success)
        self.assertIn("msg-tool工具不可用", result.message)
    
    @patch('src.core.msgtool_processor.MsgToolValidator')
    @patch('src.core.msgtool_processor.FileOperations')
    def test_extract_text_validation_failure(self, mock_file_ops, mock_validator):
        """测试参数验证失败时的提取操作"""
        # 模拟工具可用
        self.processor.executor.check_tool_available = Mock(return_value=True)
        
        # 模拟验证失败
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.message = "测试验证错误"
        mock_validator.validate_extract_params.return_value = [mock_validation_result]
        
        from src.utils.validators import ValidationSummary
        with patch.object(ValidationSummary, 'summarize_results', return_value=(False, "验证失败")):
            result = self.processor.extract_text("/test/script", "/test/json")
        
        self.assertFalse(result.success)
        self.assertIn("参数验证失败", result.message)
    
    def test_get_tool_info(self):
        """测试获取工具信息"""
        info = self.processor.get_tool_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn("available", info)
        self.assertIn("directory", info)
        self.assertIn("executable", info)
        self.assertIn("version", info)
    
    def test_get_supported_engines(self):
        """测试获取支持的引擎列表"""
        engines = self.processor.get_supported_engines()
        
        self.assertIsInstance(engines, list)
        self.assertTrue(len(engines) > 0)


class TestMsgToolValidator(unittest.TestCase):
    """测试MsgToolValidator"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试目录
        self.script_dir = os.path.join(self.temp_dir, "script")
        self.json_dir = os.path.join(self.temp_dir, "json")
        self.output_dir = os.path.join(self.temp_dir, "output")
        
        os.makedirs(self.script_dir)
        os.makedirs(self.json_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_extract_params_success(self):
        """测试提取参数验证成功"""
        results = MsgToolValidator.validate_extract_params(
            self.script_dir, self.json_dir, "自动检测"
        )
        
        # 检查验证结果
        error_results = [r for r in results if not r.is_valid]
        self.assertEqual(len(error_results), 0)
    
    def test_validate_extract_params_invalid_script_folder(self):
        """测试无效脚本文件夹的验证"""
        results = MsgToolValidator.validate_extract_params(
            "/nonexistent/folder", self.json_dir, "自动检测"
        )
        
        # 应该有错误结果
        error_results = [r for r in results if not r.is_valid]
        self.assertGreater(len(error_results), 0)
        
        # 检查错误消息
        script_errors = [r for r in error_results if r.field_name == "script_folder"]
        self.assertGreater(len(script_errors), 0)
    
    def test_validate_inject_params_success(self):
        """测试注入参数验证成功"""
        results = MsgToolValidator.validate_inject_params(
            self.script_dir, self.json_dir, self.output_dir, "自动检测"
        )
        
        # 检查验证结果（输出目录不存在是允许的）
        error_results = [r for r in results if not r.is_valid]
        self.assertEqual(len(error_results), 0)
    
    def test_validate_unknown_engine(self):
        """测试未知引擎的验证"""
        results = MsgToolValidator.validate_extract_params(
            self.script_dir, self.json_dir, "unknown-engine - 未知引擎"
        )
        
        # 应该有警告
        warning_results = [r for r in results if r.level.value == "warning"]
        self.assertGreater(len(warning_results), 0)


class TestMsgToolIntegration(unittest.TestCase):
    """msg-tool模式集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试目录结构
        self.script_dir = os.path.join(self.temp_dir, "script")
        self.json_dir = os.path.join(self.temp_dir, "json")
        self.output_dir = os.path.join(self.temp_dir, "output")
        
        os.makedirs(self.script_dir)
        os.makedirs(self.json_dir)
        
        # 创建测试脚本文件
        test_script = os.path.join(self.script_dir, "test.ks")
        with open(test_script, 'w', encoding='utf-8') as f:
            f.write('测试脚本内容')
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.core.msgtool_processor.MsgToolExecutor')
    def test_extract_workflow(self, mock_executor_class):
        """测试完整的提取工作流程"""
        # 模拟执行器
        mock_executor = Mock()
        mock_executor.check_tool_available.return_value = True
        mock_executor.extract.return_value = ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            return_code=0,
            stdout="提取成功",
            stderr="",
            execution_time=1.0,
            command="msg-tool export"
        )
        mock_executor_class.return_value = mock_executor
        
        processor = MsgToolProcessor()
        processor.executor = mock_executor
        
        result = processor.extract_text(self.script_dir, self.json_dir)
        
        self.assertTrue(result.success)
        self.assertIn("提取成功", result.message)
        mock_executor.extract.assert_called_once()
    
    @patch('src.core.msgtool_processor.MsgToolExecutor')
    @patch('src.core.msgtool_processor.SJISHandler')
    def test_inject_workflow_with_sjis(self, mock_sjis_handler_class, mock_executor_class):
        """测试带SJIS替换的注入工作流程"""
        # 模拟执行器
        mock_executor = Mock()
        mock_executor.check_tool_available.return_value = True
        mock_executor.inject.return_value = ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            return_code=0,
            stdout="注入成功",
            stderr="",
            execution_time=2.0,
            command="msg-tool import"
        )
        mock_executor_class.return_value = mock_executor
        
        # 模拟SJIS处理器
        mock_sjis_handler = Mock()
        mock_sjis_result = Mock()
        mock_sjis_result.replaced_folder = "/temp/sjis"
        mock_sjis_result.config_string = "测试配置"
        mock_sjis_result.replacement_count = 5
        mock_sjis_handler.process_json_folder.return_value = mock_sjis_result
        mock_sjis_handler_class.return_value = mock_sjis_handler
        
        processor = MsgToolProcessor()
        processor.executor = mock_executor
        processor.sjis_handler = mock_sjis_handler
        
        result = processor.inject_text(
            self.script_dir, 
            self.json_dir, 
            self.output_dir,
            sjis_replacement=True,
            sjis_replace_chars="测试"
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.sjis_config, "测试配置")
        mock_sjis_handler.process_json_folder.assert_called_once()
        mock_executor.inject.assert_called_once()


if __name__ == '__main__':
    unittest.main()