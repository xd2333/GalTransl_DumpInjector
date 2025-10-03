"""
编码转换工具类
处理各种字符编码转换、检测和二进制文件解析
"""

import struct
import chardet
from typing import Optional, Tuple, List, Union


class EncodingUtils:
    """编码工具类"""
    
    @staticmethod
    def detect_encoding(file_path: str) -> Optional[str]:
        """自动检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # 使用chardet检测编码
            result = chardet.detect(raw_data)
            if result and result['confidence'] > 0.7:
                return result['encoding']
            
            # 如果检测失败，尝试常见编码
            common_encodings = ['utf-8', 'gbk', 'sjis', 'cp932']
            for encoding in common_encodings:
                try:
                    raw_data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def read_file_with_encoding(file_path: str, encoding: Optional[str] = None) -> Tuple[str, str]:
        """读取文件内容，自动处理编码
        
        Returns:
            Tuple[str, str]: (文件内容, 使用的编码)
        """
        if encoding is None:
            encoding = EncodingUtils.detect_encoding(file_path)
            if encoding is None:
                encoding = 'utf-8'  # 默认使用UTF-8
        
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            return content, encoding
        except Exception as e:
            # 如果指定编码失败，尝试用UTF-8
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return content, 'utf-8'
            except Exception:
                raise RuntimeError(f"无法读取文件 {file_path}: {e}")
    
    @staticmethod
    def write_file_with_encoding(file_path: str, content: str, encoding: str = 'utf-8'):
        """使用指定编码写入文件"""
        try:
            with open(file_path, 'w', encoding=encoding, errors='ignore') as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError(f"无法写入文件 {file_path}: {e}")
    
    @staticmethod
    def convert_encoding(text: str, from_encoding: str, to_encoding: str) -> str:
        """转换文本编码"""
        try:
            # 先编码为字节，再用目标编码解码
            encoded_bytes = text.encode(from_encoding, errors='ignore')
            return encoded_bytes.decode(to_encoding, errors='ignore')
        except Exception as e:
            raise RuntimeError(f"编码转换失败 {from_encoding} -> {to_encoding}: {e}")
    
    @staticmethod
    def is_valid_encoding(text: str, encoding: str) -> bool:
        """检查文本是否可以用指定编码正确编解码"""
        try:
            text.encode(encoding).decode(encoding)
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False


class SJISExtUtils:
    """SJIS扩展字符处理工具"""
    
    @staticmethod
    def read_sjis_ext_bin(file_path: str) -> str:
        """读取sjis_ext.bin文件并返回字符串"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            
            chars = []
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    char_code = struct.unpack("<H", data[i:i + 2])[0]
                    chars.append(chr(char_code))
            
            return "".join(chars)
        except Exception as e:
            raise RuntimeError(f"读取SJIS扩展文件失败 {file_path}: {e}")
    
    @staticmethod
    def write_sjis_ext_bin(file_path: str, text: str):
        """将文本写入sjis_ext.bin文件"""
        try:
            with open(file_path, "wb") as f:
                for char in text:
                    char_code = ord(char)
                    f.write(struct.pack("<H", char_code))
        except Exception as e:
            raise RuntimeError(f"写入SJIS扩展文件失败 {file_path}: {e}")
    
    @staticmethod
    def parse_sjis_ext_chars(text: str) -> List[int]:
        """解析文本中的字符为SJIS扩展字符码"""
        return [ord(char) for char in text]


class EncodingValidator:
    """编码验证器"""
    
    SUPPORTED_ENCODINGS = ['utf-8', 'gbk', 'sjis', 'cp932', 'shift_jis']
    
    @staticmethod
    def validate_encoding_name(encoding: str) -> bool:
        """验证编码名称是否支持"""
        return encoding.lower() in [enc.lower() for enc in EncodingValidator.SUPPORTED_ENCODINGS]
    
    @staticmethod
    def normalize_encoding_name(encoding: str) -> str:
        """标准化编码名称"""
        encoding_lower = encoding.lower()
        
        # 处理常见的编码别名
        encoding_map = {
            'shift_jis': 'sjis',
            'cp932': 'sjis',
            'shift-jis': 'sjis',
            'utf8': 'utf-8',
            'gb2312': 'gbk',
            'chinese': 'gbk'
        }
        
        return encoding_map.get(encoding_lower, encoding_lower)
    
    @staticmethod
    def get_safe_encoding(encoding: str) -> str:
        """获取安全的编码名称，如果不支持则返回默认编码"""
        normalized = EncodingValidator.normalize_encoding_name(encoding)
        if EncodingValidator.validate_encoding_name(normalized):
            return normalized
        return 'utf-8'  # 默认编码