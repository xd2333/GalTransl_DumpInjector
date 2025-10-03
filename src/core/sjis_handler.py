"""
SJIS字符替换处理器
处理SJIS字符集替换逻辑和汉字到日文汉字的映射
"""

import os
import shutil
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..core.file_operations import FileOperations, JSONFileOperations
from ..utils.encoding_utils import SJISExtUtils


@dataclass
class SJISReplacementResult:
    """SJIS替换结果"""
    replaced_folder: str
    hanzi_chars: List[str]
    kanji_chars: List[str]
    replacement_count: int
    config_string: str


class SJISCharacterMapper:
    """SJIS字符映射器"""
    
    def __init__(self, mapping_file: str = "resources/hanzi2kanji_table.txt"):
        self.mapping_file = mapping_file
        self._char_dict: Dict[str, str] = {}
        self._load_mapping()
    
    def _load_mapping(self):
        """加载字符映射表"""
        try:
            if not os.path.exists(self.mapping_file):
                raise FileNotFoundError(f"映射文件不存在: {self.mapping_file}")
            
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            orig_char, replace_char = parts[0], parts[1]
                            self._char_dict[orig_char] = replace_char
        except Exception as e:
            raise RuntimeError(f"加载字符映射失败: {e}")
    
    def get_mapping_dict(self, filter_chars: str = "") -> Dict[str, str]:
        """获取映射字典，可选择性过滤字符"""
        if not filter_chars:
            return self._char_dict.copy()
        
        filtered_dict = {}
        for orig_char, replace_char in self._char_dict.items():
            if orig_char in filter_chars:
                filtered_dict[orig_char] = replace_char
        
        return filtered_dict
    
    def get_replacement_for_char(self, char: str) -> Optional[str]:
        """获取单个字符的替换"""
        return self._char_dict.get(char)
    
    def get_mapping_stats(self) -> Dict[str, int]:
        """获取映射统计信息"""
        return {
            "total_mappings": len(self._char_dict),
            "unique_source_chars": len(set(self._char_dict.keys())),
            "unique_target_chars": len(set(self._char_dict.values()))
        }


class SJISHandler:
    """SJIS字符替换处理器"""
    
    def __init__(self, resources_dir: str = "resources"):
        self.resources_dir = resources_dir
        self.mapper = SJISCharacterMapper(
            os.path.join(resources_dir, "hanzi2kanji_table.txt")
        )
    
    def process_json_folder(
        self, 
        json_cn_folder: str, 
        replace_chars: str = ""
    ) -> SJISReplacementResult:
        """处理JSON文件夹，执行SJIS字符替换
        
        Args:
            json_cn_folder: 中文JSON文件夹路径
            replace_chars: 要替换的字符（空字符串表示全量替换）
        
        Returns:
            SJISReplacementResult: 替换结果
        """
        # 获取映射字典
        char_dict = self.mapper.get_mapping_dict(replace_chars)
        
        if not char_dict:
            raise ValueError("没有找到可用的字符映射")
        
        # 创建替换后的文件夹
        replaced_folder = json_cn_folder + "_replaced"
        
        try:
            # 清理并重新创建替换文件夹
            if os.path.exists(replaced_folder):
                FileOperations.delete_directory(replaced_folder)
            FileOperations.ensure_dir_exists(replaced_folder)
            
            hanzi_chars_list = []
            kanji_chars_list = []
            replacement_count = 0
            
            # 处理每个JSON文件
            json_files = FileOperations.find_files_by_extension(
                json_cn_folder, ['.json'], recursive=False
            )
            
            for json_file in json_files:
                filename = os.path.basename(json_file)
                output_file = os.path.join(replaced_folder, filename)
                
                # 处理单个文件
                file_hanzi, file_kanji, file_count = self._process_single_json_file(
                    json_file, output_file, char_dict
                )
                
                # 合并结果
                for hanzi, kanji in zip(file_hanzi, file_kanji):
                    if hanzi not in hanzi_chars_list:
                        hanzi_chars_list.append(hanzi)
                        kanji_chars_list.append(kanji)
                
                replacement_count += file_count
            
            # 生成配置字符串
            config_string = self._generate_config_string(hanzi_chars_list, kanji_chars_list)
            
            return SJISReplacementResult(
                replaced_folder=replaced_folder,
                hanzi_chars=hanzi_chars_list,
                kanji_chars=kanji_chars_list,
                replacement_count=replacement_count,
                config_string=config_string
            )
        
        except Exception as e:
            # 清理失败的输出文件夹
            if os.path.exists(replaced_folder):
                try:
                    FileOperations.delete_directory(replaced_folder)
                except Exception:
                    pass
            raise RuntimeError(f"SJIS字符替换失败: {e}")
    
    def _process_single_json_file(
        self, 
        input_file: str, 
        output_file: str, 
        char_dict: Dict[str, str]
    ) -> Tuple[List[str], List[str], int]:
        """处理单个JSON文件
        
        Returns:
            Tuple[List[str], List[str], int]: (汉字列表, 日文汉字列表, 替换数量)
        """
        try:
            # 读取文件内容
            with open(input_file, "r", encoding="utf-8") as f:
                input_content = f.read()
            
            output_content = ""
            hanzi_chars = []
            kanji_chars = []
            replacement_count = 0
            
            # 逐字符处理
            for char in input_content:
                if char in char_dict:
                    replacement_char = char_dict[char]
                    output_content += replacement_char
                    
                    if char not in hanzi_chars:
                        hanzi_chars.append(char)
                        kanji_chars.append(replacement_char)
                    
                    replacement_count += 1
                else:
                    output_content += char
            
            # 写入输出文件
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output_content)
            
            return hanzi_chars, kanji_chars, replacement_count
        
        except Exception as e:
            raise RuntimeError(f"处理文件失败 {input_file}: {e}")
    
    def _generate_config_string(self, hanzi_chars: List[str], kanji_chars: List[str]) -> str:
        """生成配置字符串"""
        source_chars = "".join(kanji_chars)
        target_chars = "".join(hanzi_chars)
        
        config_lines = [
            "SJIS替换模式配置:",
            f'"source_characters":"{source_chars}",',
            f'"target_characters":"{target_chars}"'
        ]
        
        return "\n".join(config_lines)
    
    def validate_replacement_chars(self, replace_chars: str) -> Tuple[bool, str]:
        """验证替换字符是否在映射表中"""
        if not replace_chars:
            return True, "将执行全量替换"
        
        missing_chars = []
        for char in replace_chars:
            if not self.mapper.get_replacement_for_char(char):
                missing_chars.append(char)
        
        if missing_chars:
            return False, f"以下字符不在映射表中: {''.join(missing_chars)}"
        
        return True, f"所有字符都有对应的映射 (共{len(replace_chars)}个字符)"
    
    def get_mapping_preview(self, replace_chars: str = "", limit: int = 10) -> List[Tuple[str, str]]:
        """获取映射预览"""
        char_dict = self.mapper.get_mapping_dict(replace_chars)
        items = list(char_dict.items())
        
        if limit > 0:
            items = items[:limit]
        
        return items


class SJISExtBinaryHandler:
    """SJIS扩展二进制文件处理器"""
    
    @staticmethod
    def read_sjis_ext_file(file_path: str) -> str:
        """读取sjis_ext.bin文件"""
        try:
            return SJISExtUtils.read_sjis_ext_bin(file_path)
        except Exception as e:
            raise RuntimeError(f"读取SJIS扩展文件失败: {e}")
    
    @staticmethod
    def write_sjis_ext_file(file_path: str, content: str):
        """写入sjis_ext.bin文件"""
        try:
            SJISExtUtils.write_sjis_ext_bin(file_path, content)
        except Exception as e:
            raise RuntimeError(f"写入SJIS扩展文件失败: {e}")
    
    @staticmethod
    def process_sjis_ext_output(script_cn_folder: str) -> Optional[str]:
        """处理输出目录中的sjis_ext.bin文件"""
        sjis_ext_path = os.path.join(script_cn_folder, "sjis_ext.bin")
        
        # 清理已存在的文件
        if os.path.exists(sjis_ext_path):
            try:
                os.remove(sjis_ext_path)
            except Exception:
                pass  # 忽略删除错误
        
        return sjis_ext_path
    
    @staticmethod
    def get_sjis_ext_content(script_cn_folder: str) -> Optional[str]:
        """获取sjis_ext.bin文件内容"""
        sjis_ext_path = os.path.join(script_cn_folder, "sjis_ext.bin")
        
        if os.path.exists(sjis_ext_path):
            try:
                return SJISExtBinaryHandler.read_sjis_ext_file(sjis_ext_path)
            except Exception:
                return None
        
        return None


class SJISReplacementValidator:
    """SJIS替换验证器"""
    
    @staticmethod
    def validate_input_folder(json_cn_folder: str) -> Tuple[bool, str]:
        """验证输入文件夹"""
        if not os.path.exists(json_cn_folder):
            return False, f"输入文件夹不存在: {json_cn_folder}"
        
        if not os.path.isdir(json_cn_folder):
            return False, f"路径不是目录: {json_cn_folder}"
        
        # 检查是否包含JSON文件
        json_files = FileOperations.find_files_by_extension(
            json_cn_folder, ['.json'], recursive=False
        )
        
        if not json_files:
            return False, f"文件夹中没有找到JSON文件: {json_cn_folder}"
        
        return True, f"找到 {len(json_files)} 个JSON文件"
    
    @staticmethod
    def validate_mapping_file(mapping_file: str) -> Tuple[bool, str]:
        """验证映射文件"""
        if not os.path.exists(mapping_file):
            return False, f"映射文件不存在: {mapping_file}"
        
        try:
            with open(mapping_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            valid_lines = 0
            for line in lines:
                line = line.strip()
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        valid_lines += 1
            
            if valid_lines == 0:
                return False, "映射文件中没有有效的映射条目"
            
            return True, f"映射文件有效，包含 {valid_lines} 个映射条目"
        
        except Exception as e:
            return False, f"读取映射文件失败: {e}"