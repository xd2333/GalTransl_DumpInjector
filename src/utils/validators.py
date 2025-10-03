"""
输入验证工具类
用于验证用户输入的各种数据
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """验证级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    level: ValidationLevel
    message: str
    field_name: Optional[str] = None


class PathValidator:
    """路径验证器"""
    
    @staticmethod
    def validate_folder_path(path: str, must_exist: bool = True) -> ValidationResult:
        """验证文件夹路径"""
        if not path or not path.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="路径不能为空"
            )
        
        path = path.strip()
        
        # 检查路径格式
        if not PathValidator._is_valid_path_format(path):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="路径格式无效"
            )
        
        # 检查是否存在
        if must_exist and not os.path.exists(path):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"路径不存在: {path}"
            )
        
        # 检查是否为目录
        if must_exist and not os.path.isdir(path):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"路径不是有效的目录: {path}"
            )
        
        # 检查权限
        if must_exist:
            if not os.access(path, os.R_OK):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"没有读取权限: {path}"
                )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="路径有效"
        )
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> ValidationResult:
        """验证文件路径"""
        if not path or not path.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="文件路径不能为空"
            )
        
        path = path.strip()
        
        # 检查路径格式
        if not PathValidator._is_valid_path_format(path):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="文件路径格式无效"
            )
        
        # 检查是否存在
        if must_exist and not os.path.exists(path):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"文件不存在: {path}"
            )
        
        # 检查是否为文件
        if must_exist and not os.path.isfile(path):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"路径不是有效的文件: {path}"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="文件路径有效"
        )
    
    @staticmethod
    def _is_valid_path_format(path: str) -> bool:
        """检查路径格式是否有效"""
        try:
            # 基本的路径字符检查
            invalid_chars = ['<', '>', '|', '*', '?']
            for char in invalid_chars:
                if char in path:
                    return False
            
            # 检查是否为绝对路径或相对路径
            return bool(path and len(path.strip()) > 0)
        except Exception:
            return False


class RegexValidator:
    """正则表达式验证器"""
    
    @staticmethod
    def validate_regex(pattern: str) -> ValidationResult:
        """验证正则表达式"""
        if not pattern or not pattern.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="正则表达式不能为空"
            )
        
        try:
            re.compile(pattern)
        except re.error as e:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"正则表达式语法错误: {str(e)}"
            )
        
        # 检查是否包含捕获组
        if '(' not in pattern or ')' not in pattern:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="正则表达式应包含捕获组 () 来提取内容"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="正则表达式有效"
        )
    
    @staticmethod
    def validate_regex_with_test(pattern: str, test_text: str) -> ValidationResult:
        """使用测试文本验证正则表达式"""
        # 首先验证语法
        syntax_result = RegexValidator.validate_regex(pattern)
        if not syntax_result.is_valid:
            return syntax_result
        
        try:
            matches = re.findall(pattern, test_text)
            if not matches:
                return ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message="正则表达式在测试文本中没有找到匹配项"
                )
            
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"正则表达式有效，找到 {len(matches)} 个匹配项"
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"正则表达式测试失败: {str(e)}"
            )


class EncodingValidator:
    """编码验证器"""
    
    SUPPORTED_ENCODINGS = ['utf-8', 'gbk', 'sjis', 'cp932', 'shift_jis']
    
    @staticmethod
    def validate_encoding(encoding: str) -> ValidationResult:
        """验证编码名称"""
        if not encoding or not encoding.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="编码不能为空"
            )
        
        encoding = encoding.strip().lower()
        
        # 标准化编码名称
        encoding_map = {
            'shift_jis': 'sjis',
            'cp932': 'sjis',
            'shift-jis': 'sjis',
            'utf8': 'utf-8',
            'gb2312': 'gbk',
            'chinese': 'gbk'
        }
        
        normalized_encoding = encoding_map.get(encoding, encoding)
        
        if normalized_encoding not in [enc.lower() for enc in EncodingValidator.SUPPORTED_ENCODINGS]:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"不支持的编码: {encoding}，支持的编码: {', '.join(EncodingValidator.SUPPORTED_ENCODINGS)}"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"编码有效: {normalized_encoding}"
        )


class VNTextPatchValidator:
    """VNTextPatch模式验证器"""
    
    @staticmethod
    def validate_extract_params(script_folder: str, json_folder: str, engine: str) -> List[ValidationResult]:
        """验证提取参数"""
        results = []
        
        # 验证脚本文件夹
        script_result = PathValidator.validate_folder_path(script_folder, must_exist=True)
        script_result.field_name = "script_folder"
        results.append(script_result)
        
        # 验证JSON保存文件夹
        json_result = PathValidator.validate_folder_path(json_folder, must_exist=False)
        json_result.field_name = "json_folder"
        results.append(json_result)
        
        # 验证引擎选择
        if engine and engine != "自动判断":
            valid_engines = ['artemistxt', 'ethornell', 'kirikiriks', 'reallive', 'tmrhiroadvsystemtext', 'whale']
            if engine not in valid_engines:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"未知引擎: {engine}",
                    field_name="engine"
                ))
        
        return results
    
    @staticmethod
    def validate_inject_params(
        script_folder: str, 
        json_folder: str, 
        output_folder: str, 
        engine: str
    ) -> List[ValidationResult]:
        """验证注入参数"""
        results = []
        
        # 验证脚本文件夹
        script_result = PathValidator.validate_folder_path(script_folder, must_exist=True)
        script_result.field_name = "script_folder"
        results.append(script_result)
        
        # 验证JSON文件夹
        json_result = PathValidator.validate_folder_path(json_folder, must_exist=True)
        json_result.field_name = "json_folder"
        results.append(json_result)
        
        # 验证输出文件夹
        output_result = PathValidator.validate_folder_path(output_folder, must_exist=False)
        output_result.field_name = "output_folder"
        results.append(output_result)
        
        # 验证引擎选择
        if engine and engine != "自动判断":
            valid_engines = ['artemistxt', 'ethornell', 'kirikiriks', 'reallive', 'tmrhiroadvsystemtext', 'whale']
            if engine not in valid_engines:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"未知引擎: {engine}",
                    field_name="engine"
                ))
        
        return results


class RegexModeValidator:
    """正则表达式模式验证器"""
    
    @staticmethod
    def validate_extract_params(
        script_folder: str,
        json_folder: str,
        message_regex: str,
        name_regex: str,
        japanese_encoding: str
    ) -> List[ValidationResult]:
        """验证正则模式提取参数"""
        results = []
        
        # 验证脚本文件夹
        script_result = PathValidator.validate_folder_path(script_folder, must_exist=True)
        script_result.field_name = "script_folder"
        results.append(script_result)
        
        # 验证JSON保存文件夹
        json_result = PathValidator.validate_folder_path(json_folder, must_exist=False)
        json_result.field_name = "json_folder"
        results.append(json_result)
        
        # 验证消息正则表达式
        msg_regex_result = RegexValidator.validate_regex(message_regex)
        msg_regex_result.field_name = "message_regex"
        results.append(msg_regex_result)
        
        # 验证人名正则表达式（可选）
        if name_regex and name_regex.strip():
            name_regex_result = RegexValidator.validate_regex(name_regex)
            name_regex_result.field_name = "name_regex"
            results.append(name_regex_result)
        
        # 验证日文编码
        jp_encoding_result = EncodingValidator.validate_encoding(japanese_encoding)
        jp_encoding_result.field_name = "japanese_encoding"
        results.append(jp_encoding_result)
        
        return results
    
    @staticmethod
    def validate_inject_params(
        script_folder: str,
        json_jp_folder: str,
        json_cn_folder: str,
        output_folder: str,
        message_regex: str,
        name_regex: str,
        japanese_encoding: str,
        chinese_encoding: str
    ) -> List[ValidationResult]:
        """验证正则模式注入参数"""
        results = []
        
        # 验证所有路径
        path_fields = [
            ("script_folder", script_folder, True),
            ("json_jp_folder", json_jp_folder, True),
            ("json_cn_folder", json_cn_folder, True),
            ("output_folder", output_folder, False)
        ]
        
        for field_name, path, must_exist in path_fields:
            path_result = PathValidator.validate_folder_path(path, must_exist)
            path_result.field_name = field_name
            results.append(path_result)
        
        # 验证正则表达式
        msg_regex_result = RegexValidator.validate_regex(message_regex)
        msg_regex_result.field_name = "message_regex"
        results.append(msg_regex_result)
        
        if name_regex and name_regex.strip():
            name_regex_result = RegexValidator.validate_regex(name_regex)
            name_regex_result.field_name = "name_regex"
            results.append(name_regex_result)
        
        # 验证编码
        jp_encoding_result = EncodingValidator.validate_encoding(japanese_encoding)
        jp_encoding_result.field_name = "japanese_encoding"
        results.append(jp_encoding_result)
        
        cn_encoding_result = EncodingValidator.validate_encoding(chinese_encoding)
        cn_encoding_result.field_name = "chinese_encoding"
        results.append(cn_encoding_result)
        
        return results


class ValidationSummary:
    """验证结果汇总"""
    
    @staticmethod
    def summarize_results(results: List[ValidationResult]) -> Tuple[bool, str]:
        """汇总验证结果
        
        Returns:
            Tuple[bool, str]: (是否全部有效, 汇总消息)
        """
        errors = [r for r in results if not r.is_valid and r.level == ValidationLevel.ERROR]
        warnings = [r for r in results if r.level == ValidationLevel.WARNING]
        
        if errors:
            error_messages = [f"- {r.message}" for r in errors]
            return False, f"发现 {len(errors)} 个错误:\n" + "\n".join(error_messages)
        
        if warnings:
            warning_messages = [f"- {r.message}" for r in warnings]
            return True, f"发现 {len(warnings)} 个警告:\n" + "\n".join(warning_messages)
        
        return True, "所有验证通过"