"""
翻译数据模型类
用于表示翻译数据的结构和相关操作
"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import json


@dataclass
class TranslationEntry:
    """单个翻译条目"""
    message: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {"message": self.message}
        if self.name is not None:
            result["name"] = self.name
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationEntry':
        """从字典创建实例"""
        return cls(
            message=data["message"],
            name=data.get("name")
        )


class TranslationData:
    """翻译数据容器类"""
    
    def __init__(self):
        self.entries: List[TranslationEntry] = []
    
    def add_entry(self, message: str, name: Optional[str] = None):
        """添加翻译条目"""
        entry = TranslationEntry(message=message, name=name)
        self.entries.append(entry)
    
    def clear(self):
        """清空所有条目"""
        self.entries.clear()
    
    def __len__(self) -> int:
        """返回条目数量"""
        return len(self.entries)
    
    def __getitem__(self, index: int) -> TranslationEntry:
        """获取指定索引的条目"""
        return self.entries[index]
    
    def __iter__(self):
        """迭代所有条目"""
        return iter(self.entries)
    
    def to_json_list(self) -> List[Dict[str, Any]]:
        """转换为JSON列表格式"""
        return [entry.to_dict() for entry in self.entries]
    
    @classmethod
    def from_json_list(cls, data: List[Dict[str, Any]]) -> 'TranslationData':
        """从JSON列表创建实例"""
        translation_data = cls()
        for item in data:
            translation_data.entries.append(TranslationEntry.from_dict(item))
        return translation_data
    
    def save_to_file(self, file_path: str):
        """保存到JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json_list(), f, ensure_ascii=False, indent=4)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'TranslationData':
        """从JSON文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_json_list(data)


class TranslationMapping:
    """翻译映射管理类"""
    
    def __init__(self):
        self.message_dict: Dict[str, str] = {}
        self.name_dict: Dict[str, str] = {}
    
    def add_mapping(self, jp_data: TranslationData, cn_data: TranslationData):
        """添加日文到中文的映射"""
        if len(jp_data) != len(cn_data):
            raise ValueError("日文和中文数据长度不匹配")
        
        for jp_entry, cn_entry in zip(jp_data, cn_data):
            # 添加消息映射
            self.message_dict[jp_entry.message] = cn_entry.message
            
            # 添加人名映射（如果存在）
            if jp_entry.name and cn_entry.name:
                if jp_entry.name not in self.name_dict:
                    self.name_dict[jp_entry.name] = cn_entry.name
    
    def get_message_translation(self, jp_message: str) -> Optional[str]:
        """获取消息的翻译"""
        return self.message_dict.get(jp_message)
    
    def get_name_translation(self, jp_name: str) -> Optional[str]:
        """获取人名的翻译"""
        return self.name_dict.get(jp_name)
    
    def clear(self):
        """清空所有映射"""
        self.message_dict.clear()
        self.name_dict.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """获取映射统计信息"""
        return {
            "message_count": len(self.message_dict),
            "name_count": len(self.name_dict)
        }