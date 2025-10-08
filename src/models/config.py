"""
配置数据模型类
用于管理应用配置数据的加载、保存和访问
"""

import configparser
import os
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.default_config_path = os.path.join(config_dir, "default_config.ini")
        self.user_config_path = os.path.join(config_dir, "user_config.ini")
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件，优先级：用户配置 > 默认配置"""
        # 首先加载默认配置
        if os.path.exists(self.default_config_path):
            self.config.read(self.default_config_path, encoding='utf-8')
        
        # 然后加载用户配置（覆盖默认配置）
        if os.path.exists(self.user_config_path):
            self.config.read(self.user_config_path, encoding='utf-8')
    
    def save_config(self):
        """保存配置到用户配置文件"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.user_config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, fallback: str = "") -> str:
        """获取配置值"""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str):
        """设置配置值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """获取布尔型配置值"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def set_bool(self, section: str, key: str, value: bool):
        """设置布尔型配置值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value).lower())
    
    # 快捷访问属性
    @property
    def script_jp_folder(self) -> str:
        return self.get("Paths", "script_jp_folder")
    
    @script_jp_folder.setter
    def script_jp_folder(self, value: str):
        self.set("Paths", "script_jp_folder", value)
    
    @property
    def json_jp_folder(self) -> str:
        return self.get("Paths", "json_jp_folder")
    
    @json_jp_folder.setter
    def json_jp_folder(self, value: str):
        self.set("Paths", "json_jp_folder", value)
    
    @property
    def json_cn_folder(self) -> str:
        return self.get("Paths", "json_cn_folder")
    
    @json_cn_folder.setter
    def json_cn_folder(self, value: str):
        self.set("Paths", "json_cn_folder", value)
    
    @property
    def script_cn_folder(self) -> str:
        return self.get("Paths", "script_cn_folder")
    
    @script_cn_folder.setter
    def script_cn_folder(self, value: str):
        self.set("Paths", "script_cn_folder", value)
    
    @property
    def message_regex(self) -> str:
        return self.get("RegexSettings", "message_regex")
    
    @message_regex.setter
    def message_regex(self, value: str):
        self.set("RegexSettings", "message_regex", value)
    
    @property
    def name_regex(self) -> str:
        return self.get("RegexSettings", "name_regex")
    
    @name_regex.setter
    def name_regex(self, value: str):
        self.set("RegexSettings", "name_regex", value)
    
    @property
    def japanese_encoding(self) -> str:
        return self.get("Encoding", "japanese_encoding", "sjis")
    
    @japanese_encoding.setter
    def japanese_encoding(self, value: str):
        self.set("Encoding", "japanese_encoding", value)
    
    @property
    def chinese_encoding(self) -> str:
        return self.get("Encoding", "chinese_encoding", "gbk")
    
    @chinese_encoding.setter
    def chinese_encoding(self, value: str):
        self.set("Encoding", "chinese_encoding", value)
    
    @property
    def theme(self) -> str:
        return self.get("UI", "theme", "auto")
    
    @theme.setter
    def theme(self, value: str):
        self.set("UI", "theme", value)
    
    @property
    def window_size(self) -> str:
        return self.get("UI", "window_size", "584x659")
    
    @window_size.setter
    def window_size(self, value: str):
        self.set("UI", "window_size", value)
    
    @property
    def sjis_replacement(self) -> bool:
        return self.get_bool("Advanced", "sjis_replacement")
    
    @sjis_replacement.setter
    def sjis_replacement(self, value: bool):
        self.set_bool("Advanced", "sjis_replacement", value)
    
    @property
    def gbk_encoding(self) -> bool:
        return self.get_bool("Advanced", "gbk_encoding")
    
    @gbk_encoding.setter
    def gbk_encoding(self, value: bool):
        self.set_bool("Advanced", "gbk_encoding", value)
    
    # Msg-tool专用配置项
    @property
    def msgtool_script_jp_folder(self) -> str:
        return self.get("MsgToolPaths", "msgtool_script_jp_folder")
    
    @msgtool_script_jp_folder.setter
    def msgtool_script_jp_folder(self, value: str):
        self.set("MsgToolPaths", "msgtool_script_jp_folder", value)
    
    @property
    def msgtool_json_jp_folder(self) -> str:
        return self.get("MsgToolPaths", "msgtool_json_jp_folder")
    
    @msgtool_json_jp_folder.setter
    def msgtool_json_jp_folder(self, value: str):
        self.set("MsgToolPaths", "msgtool_json_jp_folder", value)
    
    @property
    def msgtool_json_cn_folder(self) -> str:
        return self.get("MsgToolPaths", "msgtool_json_cn_folder")
    
    @msgtool_json_cn_folder.setter
    def msgtool_json_cn_folder(self, value: str):
        self.set("MsgToolPaths", "msgtool_json_cn_folder", value)
    
    @property
    def msgtool_script_cn_folder(self) -> str:
        return self.get("MsgToolPaths", "msgtool_script_cn_folder")
    
    @msgtool_script_cn_folder.setter
    def msgtool_script_cn_folder(self, value: str):
        self.set("MsgToolPaths", "msgtool_script_cn_folder", value)
    
    @property
    def msgtool_selected_engine(self) -> str:
        return self.get("MsgToolSettings", "msgtool_selected_engine", "自动检测")
    
    @msgtool_selected_engine.setter
    def msgtool_selected_engine(self, value: str):
        self.set("MsgToolSettings", "msgtool_selected_engine", value)

    @property
    def msgtool_encoding(self) -> str:
        return self.get("MsgToolSettings", "msgtool_encoding", "默认编码")

    @msgtool_encoding.setter
    def msgtool_encoding(self, value: str):
        self.set("MsgToolSettings", "msgtool_encoding", value)
    
    @property
    def msgtool_patched_encoding(self) -> str:
        return self.get("MsgToolSettings", "msgtool_patched_encoding", "默认编码")
    
    @msgtool_patched_encoding.setter
    def msgtool_patched_encoding(self, value: str):
        self.set("MsgToolSettings", "msgtool_patched_encoding", value)
    
    @property
    def msgtool_sjis_replacement(self) -> bool:
        return self.get_bool("MsgToolSettings", "msgtool_sjis_replacement")
    
    @msgtool_sjis_replacement.setter
    def msgtool_sjis_replacement(self, value: bool):
        self.set_bool("MsgToolSettings", "msgtool_sjis_replacement", value)
    
    @property
    def msgtool_sjis_chars(self) -> str:
        return self.get("MsgToolSettings", "msgtool_sjis_chars")
    
    @msgtool_sjis_chars.setter
    def msgtool_sjis_chars(self, value: str):
        self.set("MsgToolSettings", "msgtool_sjis_chars", value)