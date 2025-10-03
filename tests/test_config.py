"""
测试配置管理功能
"""

import unittest
import tempfile
import os
from pathlib import Path

from src.models.config import Config


class TestConfig(unittest.TestCase):
    """配置管理测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_values(self):
        """测试默认值"""
        self.assertEqual(self.config.japanese_encoding, "sjis")
        self.assertEqual(self.config.chinese_encoding, "gbk")
        self.assertEqual(self.config.theme, "auto")
        self.assertFalse(self.config.sjis_replacement)
        self.assertFalse(self.config.gbk_encoding)
    
    def test_set_get_values(self):
        """测试设置和获取值"""
        self.config.script_jp_folder = "/test/jp"
        self.config.json_jp_folder = "/test/json_jp"
        self.config.japanese_encoding = "utf-8"
        self.config.sjis_replacement = True
        
        self.assertEqual(self.config.script_jp_folder, "/test/jp")
        self.assertEqual(self.config.json_jp_folder, "/test/json_jp")
        self.assertEqual(self.config.japanese_encoding, "utf-8")
        self.assertTrue(self.config.sjis_replacement)
    
    def test_save_load_config(self):
        """测试保存和加载配置"""
        # 设置一些值
        self.config.script_jp_folder = "/test/save_load"
        self.config.message_regex = r"test_regex_(.*?)"
        self.config.gbk_encoding = True
        
        # 保存配置
        self.config.save_config()
        
        # 创建新的配置实例
        new_config = Config(self.temp_dir)
        
        # 验证值是否正确加载
        self.assertEqual(new_config.script_jp_folder, "/test/save_load")
        self.assertEqual(new_config.message_regex, r"test_regex_(.*?)")
        self.assertTrue(new_config.gbk_encoding)


if __name__ == '__main__':
    unittest.main()