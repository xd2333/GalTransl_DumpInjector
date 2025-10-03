"""
文件操作工具类
封装安全的文件系统操作
"""

import os
import shutil
import json
from typing import List, Dict, Any, Optional, Generator, Tuple
from pathlib import Path


class FileOperations:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir_exists(dir_path: str) -> bool:
        """确保目录存在，如果不存在则创建"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            raise RuntimeError(f"创建目录失败 {dir_path}: {e}")
    
    @staticmethod
    def copy_file(src_path: str, dst_path: str, create_dirs: bool = True) -> bool:
        """复制文件"""
        try:
            if create_dirs:
                dst_dir = os.path.dirname(dst_path)
                if dst_dir:
                    FileOperations.ensure_dir_exists(dst_dir)
            
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            raise RuntimeError(f"复制文件失败 {src_path} -> {dst_path}: {e}")
    
    @staticmethod
    def copy_directory(src_dir: str, dst_dir: str) -> bool:
        """复制目录"""
        try:
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            return True
        except Exception as e:
            raise RuntimeError(f"复制目录失败 {src_dir} -> {dst_dir}: {e}")
    
    @staticmethod
    def move_file(src_path: str, dst_path: str, create_dirs: bool = True) -> bool:
        """移动文件"""
        try:
            if create_dirs:
                dst_dir = os.path.dirname(dst_path)
                if dst_dir:
                    FileOperations.ensure_dir_exists(dst_dir)
            
            shutil.move(src_path, dst_path)
            return True
        except Exception as e:
            raise RuntimeError(f"移动文件失败 {src_path} -> {dst_path}: {e}")
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            raise RuntimeError(f"删除文件失败 {file_path}: {e}")
    
    @staticmethod
    def delete_directory(dir_path: str) -> bool:
        """删除目录"""
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            return True
        except Exception as e:
            raise RuntimeError(f"删除目录失败 {dir_path}: {e}")
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """列出目录中的文件"""
        try:
            path = Path(directory)
            if not path.exists():
                return []
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            return [str(f) for f in files if f.is_file()]
        except Exception as e:
            raise RuntimeError(f"列出文件失败 {directory}: {e}")
    
    @staticmethod
    def list_directories(directory: str, recursive: bool = False) -> List[str]:
        """列出目录中的子目录"""
        try:
            path = Path(directory)
            if not path.exists():
                return []
            
            if recursive:
                dirs = list(path.rglob("*"))
            else:
                dirs = list(path.glob("*"))
            
            return [str(d) for d in dirs if d.is_dir()]
        except Exception as e:
            raise RuntimeError(f"列出目录失败 {directory}: {e}")
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            raise RuntimeError(f"获取文件大小失败 {file_path}: {e}")
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_file": os.path.isfile(file_path),
                "is_dir": os.path.isdir(file_path),
                "exists": os.path.exists(file_path)
            }
        except Exception as e:
            raise RuntimeError(f"获取文件信息失败 {file_path}: {e}")
    
    @staticmethod
    def find_files_by_extension(directory: str, extensions: List[str], recursive: bool = True) -> List[str]:
        """根据扩展名查找文件"""
        try:
            path = Path(directory)
            if not path.exists():
                return []
            
            files = []
            extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
            
            if recursive:
                all_files = path.rglob("*")
            else:
                all_files = path.glob("*")
            
            for file in all_files:
                if file.is_file() and file.suffix.lower() in extensions:
                    files.append(str(file))
            
            return files
        except Exception as e:
            raise RuntimeError(f"查找文件失败 {directory}: {e}")
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """生成安全的文件名"""
        # 替换不安全的字符
        unsafe_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # 去除首尾空格和点
        safe_name = safe_name.strip(' .')
        
        # 确保不为空
        if not safe_name:
            safe_name = "untitled"
        
        return safe_name
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".bak") -> str:
        """备份文件"""
        try:
            backup_path = file_path + backup_suffix
            counter = 1
            
            # 如果备份文件已存在，添加数字后缀
            while os.path.exists(backup_path):
                backup_path = f"{file_path}{backup_suffix}.{counter}"
                counter += 1
            
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise RuntimeError(f"备份文件失败 {file_path}: {e}")


class JSONFileOperations:
    """JSON文件操作类"""
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"JSON格式错误 {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"读取JSON文件失败 {file_path}: {e}")
    
    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any], indent: int = 4, create_dirs: bool = True) -> bool:
        """写入JSON文件"""
        try:
            if create_dirs:
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    FileOperations.ensure_dir_exists(dir_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception as e:
            raise RuntimeError(f"写入JSON文件失败 {file_path}: {e}")
    
    @staticmethod
    def merge_json_files(input_files: List[str], output_file: str) -> bool:
        """合并多个JSON文件"""
        try:
            merged_data = []
            
            for file_path in input_files:
                if os.path.exists(file_path):
                    data = JSONFileOperations.read_json(file_path)
                    if isinstance(data, list):
                        merged_data.extend(data)
                    else:
                        merged_data.append(data)
            
            JSONFileOperations.write_json(output_file, merged_data)
            return True
        except Exception as e:
            raise RuntimeError(f"合并JSON文件失败: {e}")


class ScriptFileIterator:
    """脚本文件迭代器"""
    
    def __init__(self, script_dir: str, extensions: List[str] = None):
        self.script_dir = script_dir
        self.extensions = extensions or ['.txt', '.ks', '.scr', '.dat']
    
    def __iter__(self) -> Generator[Tuple[str, str], None, None]:
        """迭代脚本文件，返回(文件名, 完整路径)"""
        try:
            files = FileOperations.find_files_by_extension(
                self.script_dir, 
                self.extensions, 
                recursive=False
            )
            
            for file_path in files:
                filename = os.path.basename(file_path)
                yield filename, file_path
        except Exception as e:
            raise RuntimeError(f"迭代脚本文件失败: {e}")
    
    def get_file_count(self) -> int:
        """获取文件数量"""
        try:
            files = FileOperations.find_files_by_extension(
                self.script_dir, 
                self.extensions, 
                recursive=False
            )
            return len(files)
        except Exception:
            return 0


class TempFileManager:
    """临时文件管理器"""
    
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = temp_dir
        self.temp_files: List[str] = []
        self.temp_dirs: List[str] = []
    
    def create_temp_file(self, suffix: str = "", prefix: str = "tmp") -> str:
        """创建临时文件"""
        try:
            FileOperations.ensure_dir_exists(self.temp_dir)
            
            import tempfile
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.temp_dir)
            os.close(fd)  # 关闭文件描述符
            
            self.temp_files.append(path)
            return path
        except Exception as e:
            raise RuntimeError(f"创建临时文件失败: {e}")
    
    def create_temp_dir(self, prefix: str = "tmp") -> str:
        """创建临时目录"""
        try:
            FileOperations.ensure_dir_exists(self.temp_dir)
            
            import tempfile
            path = tempfile.mkdtemp(prefix=prefix, dir=self.temp_dir)
            
            self.temp_dirs.append(path)
            return path
        except Exception as e:
            raise RuntimeError(f"创建临时目录失败: {e}")
    
    def cleanup(self):
        """清理所有临时文件和目录"""
        # 清理临时文件
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # 忽略清理错误
        
        # 清理临时目录
        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
            except Exception:
                pass  # 忽略清理错误
        
        self.temp_files.clear()
        self.temp_dirs.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()