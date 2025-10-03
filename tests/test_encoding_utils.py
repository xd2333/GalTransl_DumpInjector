"""
测试编码工具功能
"""

import unittest
import tempfile
import os

from src.utils.encoding_utils import EncodingUtils, EncodingValidator


class TestEncodingUtils(unittest.TestCase):
    """编码工具测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_read_write_file(self):
        """测试文件读写"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "测试内容\nTest content"
        
        # 写入文件
        EncodingUtils.write_file_with_encoding(test_file, test_content, "utf-8")
        
        # 读取文件
        content, encoding = EncodingUtils.read_file_with_encoding(test_file, "utf-8")
        
        self.assertEqual(content, test_content)
        self.assertEqual(encoding, "utf-8")
    
    def test_encoding_validation(self):
        """测试编码验证"""
        self.assertTrue(EncodingValidator.validate_encoding_name("utf-8"))
        self.assertTrue(EncodingValidator.validate_encoding_name("gbk"))
        self.assertTrue(EncodingValidator.validate_encoding_name("sjis"))
        self.assertFalse(EncodingValidator.validate_encoding_name("invalid_encoding"))
    
    def test_encoding_normalization(self):
        """测试编码名称标准化"""
        self.assertEqual(EncodingValidator.normalize_encoding_name("UTF8"), "utf-8")
        self.assertEqual(EncodingValidator.normalize_encoding_name("shift_jis"), "sjis")
        self.assertEqual(EncodingValidator.normalize_encoding_name("CP932"), "sjis")
    
    def test_safe_encoding(self):
        """测试安全编码获取"""
        self.assertEqual(EncodingValidator.get_safe_encoding("utf-8"), "utf-8")
        self.assertEqual(EncodingValidator.get_safe_encoding("invalid"), "utf-8")


if __name__ == '__main__':
    unittest.main()