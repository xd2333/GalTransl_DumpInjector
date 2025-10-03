"""
正则表达式处理器
处理正则表达式模式的文本提取和注入
"""

import os
import re
import shutil
from typing import Optional, Callable, Dict, Any, List, Tuple
from dataclasses import dataclass

from ..utils.validators import RegexModeValidator, ValidationSummary
from ..utils.encoding_utils import EncodingUtils
from ..core.file_operations import FileOperations, ScriptFileIterator
from ..core.sjis_handler import SJISHandler
from ..models.translation_data import TranslationData, TranslationMapping


@dataclass
class RegexProcessResult:
    """正则表达式处理结果"""
    success: bool
    message: str
    processed_files: int = 0
    total_matches: int = 0
    sjis_config: Optional[str] = None
    execution_time: float = 0.0


class RegexProcessor:
    """正则表达式处理器"""
    
    def __init__(self):
        self.sjis_handler = SJISHandler()
        self._translation_mapping = TranslationMapping()
    
    def extract_with_regex(
        self,
        script_folder: str,
        json_folder: str,
        message_pattern: str,
        name_pattern: Optional[str] = None,
        encoding: str = "sjis",
        output_callback: Optional[Callable[[str], None]] = None
    ) -> RegexProcessResult:
        """使用正则表达式提取文本
        
        Args:
            script_folder: 脚本文件夹路径
            json_folder: JSON保存文件夹路径
            message_pattern: 消息提取正则表达式
            name_pattern: 人名提取正则表达式（可选）
            encoding: 脚本文件编码
            output_callback: 进度回调函数
        
        Returns:
            RegexProcessResult: 处理结果
        """
        import time
        start_time = time.time()
        
        try:
            # 验证输入参数
            validation_results = RegexModeValidator.validate_extract_params(
                script_folder, json_folder, message_pattern, 
                name_pattern or "", encoding
            )
            
            is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
            if not is_valid:
                return RegexProcessResult(
                    success=False,
                    message=f"参数验证失败:\n{validation_message}"
                )
            
            # 编译正则表达式
            try:
                message_regex = re.compile(message_pattern)
                name_regex = re.compile(name_pattern) if name_pattern else None
            except re.error as e:
                return RegexProcessResult(
                    success=False,
                    message=f"正则表达式编译失败: {str(e)}"
                )
            
            # 确保输出目录存在
            FileOperations.ensure_dir_exists(json_folder)
            
            # 处理脚本文件
            iterator = ScriptFileIterator(script_folder)
            processed_files = 0
            total_matches = 0
            
            for filename, file_path in iterator:
                if output_callback:
                    output_callback(f"处理文件: {filename}")
                
                try:
                    matches = self._extract_from_single_file(
                        file_path, message_regex, name_regex, encoding
                    )
                    
                    # 保存JSON文件
                    json_filename = os.path.splitext(filename)[0] + ".json"
                    json_path = os.path.join(json_folder, json_filename)
                    matches.save_to_file(json_path)
                    
                    processed_files += 1
                    total_matches += len(matches)
                
                except Exception as e:
                    if output_callback:
                        output_callback(f"处理文件 {filename} 时出错: {str(e)}")
                    continue
            
            execution_time = time.time() - start_time
            
            return RegexProcessResult(
                success=True,
                message=f"提取完成，处理了 {processed_files} 个文件，共提取 {total_matches} 条文本",
                processed_files=processed_files,
                total_matches=total_matches,
                execution_time=execution_time
            )
        
        except Exception as e:
            return RegexProcessResult(
                success=False,
                message=f"提取过程异常: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def inject_with_regex(
        self,
        script_folder: str,
        json_jp_folder: str,
        json_cn_folder: str,
        output_folder: str,
        message_pattern: str,
        name_pattern: Optional[str] = None,
        japanese_encoding: str = "sjis",
        chinese_encoding: str = "gbk",
        sjis_replacement: bool = False,
        sjis_replace_chars: str = "",
        output_callback: Optional[Callable[[str], None]] = None
    ) -> RegexProcessResult:
        """使用正则表达式注入文本
        
        Args:
            script_folder: 脚本文件夹路径
            json_jp_folder: 日文JSON文件夹路径
            json_cn_folder: 中文JSON文件夹路径
            output_folder: 输出文件夹路径
            message_pattern: 消息替换正则表达式
            name_pattern: 人名替换正则表达式（可选）
            japanese_encoding: 日文脚本编码
            chinese_encoding: 中文脚本编码
            sjis_replacement: 是否启用SJIS替换
            sjis_replace_chars: SJIS替换字符
            output_callback: 进度回调函数
        
        Returns:
            RegexProcessResult: 处理结果
        """
        import time
        start_time = time.time()
        
        try:
            # 验证输入参数
            validation_results = RegexModeValidator.validate_inject_params(
                script_folder, json_jp_folder, json_cn_folder, output_folder,
                message_pattern, name_pattern or "", japanese_encoding, chinese_encoding
            )
            
            is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
            if not is_valid:
                return RegexProcessResult(
                    success=False,
                    message=f"参数验证失败:\n{validation_message}"
                )
            
            # 编译正则表达式
            try:
                message_regex = re.compile(message_pattern)
                name_regex = re.compile(name_pattern) if name_pattern else None
            except re.error as e:
                return RegexProcessResult(
                    success=False,
                    message=f"正则表达式编译失败: {str(e)}"
                )
            
            # 确保输出目录存在
            FileOperations.ensure_dir_exists(output_folder)
            
            # 处理SJIS替换
            actual_json_cn_folder = json_cn_folder
            sjis_config = None
            
            if sjis_replacement:
                try:
                    sjis_result = self.sjis_handler.process_json_folder(
                        json_cn_folder, sjis_replace_chars
                    )
                    actual_json_cn_folder = sjis_result.replaced_folder
                    sjis_config = sjis_result.config_string
                    
                    if output_callback:
                        output_callback(f"SJIS替换完成，替换了 {sjis_result.replacement_count} 个字符")
                
                except Exception as e:
                    return RegexProcessResult(
                        success=False,
                        message=f"SJIS字符替换失败: {str(e)}"
                    )
            
            # 清空翻译映射
            self._translation_mapping.clear()
            
            # 处理脚本文件
            iterator = ScriptFileIterator(script_folder)
            processed_files = 0
            total_replacements = 0
            
            for filename, file_path in iterator:
                if output_callback:
                    output_callback(f"处理文件: {filename}")
                
                try:
                    replacements = self._inject_to_single_file(
                        file_path, filename, json_jp_folder, actual_json_cn_folder,
                        output_folder, message_regex, name_regex,
                        japanese_encoding, chinese_encoding
                    )
                    
                    processed_files += 1
                    total_replacements += replacements
                
                except Exception as e:
                    if output_callback:
                        output_callback(f"处理文件 {filename} 时出错: {str(e)}")
                    
                    # 复制原文件到输出目录
                    try:
                        output_path = os.path.join(output_folder, filename)
                        shutil.copy(file_path, output_path)
                    except Exception:
                        pass
                    continue
            
            execution_time = time.time() - start_time
            
            return RegexProcessResult(
                success=True,
                message=f"注入完成，处理了 {processed_files} 个文件，共替换 {total_replacements} 处文本",
                processed_files=processed_files,
                total_matches=total_replacements,
                sjis_config=sjis_config,
                execution_time=execution_time
            )
        
        except Exception as e:
            return RegexProcessResult(
                success=False,
                message=f"注入过程异常: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _extract_from_single_file(
        self,
        file_path: str,
        message_regex: re.Pattern,
        name_regex: Optional[re.Pattern],
        encoding: str
    ) -> TranslationData:
        """从单个文件提取文本"""
        # 读取文件内容
        content, actual_encoding = EncodingUtils.read_file_with_encoding(file_path, encoding)
        
        translation_data = TranslationData()
        
        # 提取消息
        message_matches = list(message_regex.finditer(content))
        last_start = 0
        
        for message_match in message_matches:
            try:
                message = message_match.group(1)
            except IndexError:
                continue  # 跳过没有捕获组的匹配
            
            start = message_match.start(1)
            name = ""
            
            # 在消息之前查找人名
            if name_regex:
                name_match = name_regex.search(content, last_start, start)
                if name_match:
                    try:
                        name = name_match.group(1)
                    except IndexError:
                        name = ""
            
            # 添加到翻译数据
            translation_data.add_entry(message, name if name else None)
            last_start = message_match.end(1)
        
        return translation_data
    
    def _inject_to_single_file(
        self,
        file_path: str,
        filename: str,
        json_jp_folder: str,
        json_cn_folder: str,
        output_folder: str,
        message_regex: re.Pattern,
        name_regex: Optional[re.Pattern],
        japanese_encoding: str,
        chinese_encoding: str
    ) -> int:
        """注入单个文件"""
        # 构建JSON文件路径
        json_base_name = os.path.splitext(filename)[0] + ".json"
        jp_json_path = os.path.join(json_jp_folder, json_base_name)
        cn_json_path = os.path.join(json_cn_folder, json_base_name)
        
        # 检查JSON文件是否存在
        if not os.path.exists(jp_json_path) or not os.path.exists(cn_json_path):
            # 如果JSON文件不存在，直接复制原文件
            output_path = os.path.join(output_folder, filename)
            shutil.copy(file_path, output_path)
            return 0
        
        # 加载翻译数据
        jp_data = TranslationData.load_from_file(jp_json_path)
        cn_data = TranslationData.load_from_file(cn_json_path)
        
        # 构建映射
        self._translation_mapping.add_mapping(jp_data, cn_data)
        
        # 读取脚本内容
        content, _ = EncodingUtils.read_file_with_encoding(file_path, japanese_encoding)
        
        # 替换消息
        replacement_count = 0
        content = message_regex.sub(
            lambda m: self._replace_message(m, replacement_count), content
        )
        replacement_count = len(message_regex.findall(content))
        
        # 替换人名
        if name_regex:
            content = name_regex.sub(self._replace_name, content)
        
        # 写入输出文件
        output_path = os.path.join(output_folder, filename)
        EncodingUtils.write_file_with_encoding(output_path, content, chinese_encoding)
        
        return replacement_count
    
    def _replace_message(self, match: re.Match, count_ref: List[int]) -> str:
        """替换消息回调函数"""
        try:
            original_message = match.group(1)
            translated = self._translation_mapping.get_message_translation(original_message)
            
            if translated:
                return match.group().replace(original_message, translated)
            else:
                return match.group()
        except (IndexError, AttributeError):
            return match.group()
    
    def _replace_name(self, match: re.Match) -> str:
        """替换人名回调函数"""
        try:
            original_name = match.group(1)
            translated = self._translation_mapping.get_name_translation(original_name)
            
            if translated:
                return match.group().replace(original_name, translated)
            else:
                return match.group()
        except (IndexError, AttributeError):
            return match.group()
    
    def validate_regex_patterns(
        self, 
        message_pattern: str, 
        name_pattern: Optional[str] = None
    ) -> RegexProcessResult:
        """验证正则表达式模式"""
        try:
            from ..utils.validators import RegexValidator
            
            # 验证消息正则表达式
            msg_result = RegexValidator.validate_regex(message_pattern)
            if not msg_result.is_valid:
                return RegexProcessResult(
                    success=False,
                    message=f"消息正则表达式无效: {msg_result.message}"
                )
            
            # 验证人名正则表达式（如果提供）
            if name_pattern:
                name_result = RegexValidator.validate_regex(name_pattern)
                if not name_result.is_valid:
                    return RegexProcessResult(
                        success=False,
                        message=f"人名正则表达式无效: {name_result.message}"
                    )
            
            return RegexProcessResult(
                success=True,
                message="正则表达式验证通过"
            )
        
        except Exception as e:
            return RegexProcessResult(
                success=False,
                message=f"正则表达式验证异常: {str(e)}"
            )
    
    def test_regex_on_sample(
        self,
        sample_text: str,
        message_pattern: str,
        name_pattern: Optional[str] = None
    ) -> RegexProcessResult:
        """在样本文本上测试正则表达式"""
        try:
            # 编译正则表达式
            message_regex = re.compile(message_pattern)
            name_regex = re.compile(name_pattern) if name_pattern else None
            
            # 查找匹配
            message_matches = message_regex.findall(sample_text)
            name_matches = name_regex.findall(sample_text) if name_regex else []
            
            result_message = f"消息匹配: {len(message_matches)} 个"
            if name_pattern:
                result_message += f"\n人名匹配: {len(name_matches)} 个"
            
            if message_matches:
                result_message += f"\n消息示例: {message_matches[:3]}"  # 显示前3个
            
            if name_matches:
                result_message += f"\n人名示例: {name_matches[:3]}"  # 显示前3个
            
            return RegexProcessResult(
                success=True,
                message=result_message,
                total_matches=len(message_matches) + len(name_matches)
            )
        
        except re.error as e:
            return RegexProcessResult(
                success=False,
                message=f"正则表达式错误: {str(e)}"
            )
        except Exception as e:
            return RegexProcessResult(
                success=False,
                message=f"测试异常: {str(e)}"
            )
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """获取翻译统计信息"""
        return self._translation_mapping.get_stats()
    
    def clear_translation_cache(self):
        """清除翻译缓存"""
        self._translation_mapping.clear()
    
    def get_supported_encodings(self) -> List[str]:
        """获取支持的编码列表"""
        from ..utils.encoding_utils import EncodingValidator
        return EncodingValidator.SUPPORTED_ENCODINGS