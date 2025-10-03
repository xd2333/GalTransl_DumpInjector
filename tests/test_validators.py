"""
测试验证器功能
"""

import unittest
import tempfile
import os

from src.utils.validators import (
    PathValidator, RegexValidator, EncodingValidator,
    VNTextPatchValidator, ValidationSummary
)


class TestValidators(unittest.TestCase):
    """验证器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        # 创建测试文件夹
        self.test_folder = os.path.join(self.temp_dir, "test_folder")
        os.makedirs(self.test_folder)
        
        # 创建测试文件
        self.test_file = os.path.join(self.test_folder, "test.txt")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("test content")
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_path_validator(self):
        """测试路径验证器"""
        # 测试存在的文件夹
        result = PathValidator.validate_folder_path(self.test_folder, must_exist=True)
        self.assertTrue(result.is_valid)
        
        # 测试不存在的文件夹
        non_exist_folder = os.path.join(self.temp_dir, "non_exist")
        result = PathValidator.validate_folder_path(non_exist_folder, must_exist=True)
        self.assertFalse(result.is_valid)
        
        # 测试存在的文件
        result = PathValidator.validate_file_path(self.test_file, must_exist=True)
        self.assertTrue(result.is_valid)
        
        # 测试空路径
        result = PathValidator.validate_folder_path("", must_exist=False)
        self.assertFalse(result.is_valid)
    
    def test_regex_validator(self):
        """测试正则表达式验证器"""
        # 测试有效的正则表达式
        result = RegexValidator.validate_regex(r"test_(.*?)_end")
        self.assertTrue(result.is_valid)
        
        # 测试无效的正则表达式
        result = RegexValidator.validate_regex(r"test_[")
        self.assertFalse(result.is_valid)
        
        # 测试空正则表达式
        result = RegexValidator.validate_regex("")
        self.assertFalse(result.is_valid)
        
        # 测试没有捕获组的正则表达式
        result = RegexValidator.validate_regex(r"test_pattern")
        # 应该返回警告但仍然有效
        self.assertTrue(result.is_valid)
    
    def test_encoding_validator(self):
        """测试编码验证器"""
        # 测试支持的编码
        result = EncodingValidator.validate_encoding("utf-8")
        self.assertTrue(result.is_valid)
        
        result = EncodingValidator.validate_encoding("gbk")
        self.assertTrue(result.is_valid)
        
        result = EncodingValidator.validate_encoding("sjis")
        self.assertTrue(result.is_valid)
        
        # 测试不支持的编码
        result = EncodingValidator.validate_encoding("invalid_encoding")
        self.assertFalse(result.is_valid)
        
        # 测试空编码
        result = EncodingValidator.validate_encoding("")
        self.assertFalse(result.is_valid)
    
    def test_vntext_validator(self):
        """测试VNTextPatch验证器"""
        # 测试提取参数验证
        results = VNTextPatchValidator.validate_extract_params(
            self.test_folder, self.test_folder, "自动判断"
        )
        
        # 应该有两个验证结果（script_folder 和 json_folder）
        self.assertEqual(len(results), 2)
        
        # 验证都应该通过
        for result in results:
            if result.field_name in ["script_folder", "json_folder"]:
                self.assertTrue(result.is_valid)
    
    def test_validation_summary(self):
        """测试验证结果汇总"""
        from src.utils.validators import ValidationResult, ValidationLevel
        
        # 创建测试结果
        results = [
            ValidationResult(True, ValidationLevel.INFO, "测试成功"),
            ValidationResult(True, ValidationLevel.WARNING, "测试警告"),
            ValidationResult(False, ValidationLevel.ERROR, "测试错误")
        ]
        
        is_valid, message = ValidationSummary.summarize_results(results)
        
        # 因为有错误，应该返回False
        self.assertFalse(is_valid)
        self.assertIn("错误", message)


if __name__ == '__main__':
    unittest.main()