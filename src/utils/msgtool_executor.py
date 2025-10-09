"""
Msg-tool命令执行器
处理msg-tool工具的命令构建和执行
"""

import os
from typing import Optional, Callable, List
from .command_executor import CommandExecutor, ExecutionResult
from platform import system


ENCODING_CP_MAP = {
    'gb2312': 936,
    'gbk': 936,
    'shift-jis': 932,
    'jis': 932,
    'cp932': 932,
    'utf8': 65001,
}


class MsgToolExecutor(CommandExecutor):
    """Msg-tool专用执行器"""
    
    def __init__(self, msgtool_dir: str = "msg_tool"):
        """
        初始化MsgTool执行器
        
        Args:
            msgtool_dir: msg-tool工具所在目录
        """
        super().__init__(working_dir=msgtool_dir)
        self.msgtool_dir = msgtool_dir
        self.executable = "msg_tool.exe"
    
    def check_tool_available(self) -> bool:
        """检查msg-tool工具是否可用"""
        tool_path = os.path.join(self.msgtool_dir, self.executable)
        available = os.path.exists(tool_path) and os.access(tool_path, os.X_OK)
        
        # 输出检查结果用于调试
        if not available:
            print(f"工具检查: {tool_path} {'not found' if not os.path.exists(tool_path) else 'not executable'}")
        
        return available
    
    def get_encodings(self) -> List[str]:
        """获取支持的编码列表"""
        encodings = [
            "默认编码",
            "gb2312",  # 简体中文
            "cp932",   # 日文
            "utf8",    # UTF-8
            "自动检测（不推荐）"
        ]
        return encodings
    
    def get_patched_encodings(self) -> List[str]:
        """获取支持的注入编码列表"""
        encodings = [
            "默认编码",
            "gb2312",  # 简体中文
            "cp932",   # 日文
            "utf8",    # UTF-8
        ]
        return encodings

    def get_code_page(self, encoding: str) -> Optional[int]:
        """根据编码名称获取对应的代码页
        
        Args:
            encoding: 编码名称
            
        Returns:
            对应的代码页，找不到时返回None
        """
        enc = ENCODING_CP_MAP.get(encoding, None)
        if enc:
            return enc
        encoding = encoding.lower().replace("-", "")
        enc = ENCODING_CP_MAP.get(encoding, None)
        if enc:
            return enc
        encoding = encoding.strip('cp')
        if encoding.isdigit():
            return int(encoding)
        return None
    
    def get_supported_engines(self) -> List[str]:
        """获取支持的引擎列表
        
        Returns:
            支持的引擎类型列表，按系列分组
        """
        engines = [
            "自动检测",
            # Artemis系列
            "artemis - AST文件",
            "artemis-asb - ASB/IET文件", 
            "artemis-txt - Artemis Engine TXT",
            # BGI/Ethornell系列
            "bgi - BGI通用脚本",
            "bgi-bp - BP脚本",
            # CatSystem2系列
            "cat-system - CST场景脚本",
            "cat-system-cstl - I18N文件",
            # 其他引擎
            "circus - MES脚本文件",
            "entis-gls - Entis GLS engine XML脚本",
            "escude - BIN脚本文件",
            "ex-hibit - RLD脚本文件",
            "favorite - DAT脚本文件",
            "innocent-grey - TXT脚本",
            "kirikiri - KS脚本文件"
        ]
        return engines
    
    def _escape_path(self, path: str) -> str:
        """转义路径中的空格和特殊字符"""
        if " " in path or any(char in path for char in ['"', "'", "&", "|"]):
            return f'"{path}"'
        return path
    
    def _get_script_type_param(self, engine: str) -> Optional[str]:
        """根据引擎名称获取script-type参数"""
        if engine == "自动检测":
            return None
        
        # 提取引擎类型（去掉描述部分）
        engine_type = engine.split(" - ")[0].strip()
        return engine_type
    
    def extract(
        self,
        script_folder: str,
        json_folder: str,
        engine: Optional[str] = None,
        encoding: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ExecutionResult:
        """提取脚本到JSON
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: JSON保存文件夹路径  
            engine: 指定的引擎类型
            encoding: 指定的文件编码
            output_callback: 实时输出回调函数
            
        Returns:
            ExecutionResult: 执行结果
        """
        # 转义路径
        script_path = self._escape_path(script_folder)
        json_path = self._escape_path(json_folder)
        
        # 构建基础命令
        cmd_parts = [
            f".\\{self.executable}",
            "export", 
            "--recursive"
        ]
        
        # 添加引擎类型参数
        script_type = self._get_script_type_param(engine) if engine else None
        if script_type:
            cmd_parts.extend(["--script-type", script_type])

        # 添加编码参数
        if encoding and encoding != "默认编码":
            if encoding == "自动检测（不推荐）":
                encoding = "auto"
            if system() == "Windows" and self.get_code_page(encoding):
                cmd_parts.extend(["--code-page", str(self.get_code_page(encoding))])
            else:
                cmd_parts.extend(["--encoding", encoding])
        
        # 添加路径参数
        cmd_parts.extend([script_path, json_path])
        
        # 构建完整命令
        command = " ".join(cmd_parts)
        
        # 输出命令用于调试
        if output_callback:
            output_callback(f"正在执行: {command}")
        
        return self.execute(command, timeout=300, output_callback=output_callback)
    
    def inject(
        self,
        script_folder: str,
        json_folder: str,
        output_folder: str,
        engine: Optional[str] = None,
        encoding: Optional[str] = None,
        patched_encoding: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ExecutionResult:
        """注入JSON回脚本
        
        Args:
            script_folder: 原始日文脚本文件夹路径
            json_folder: 译文JSON文件夹路径
            output_folder: 输出脚本文件夹路径
            engine: 指定的引擎类型
            encoding: 指定的文件编码
            patched_encoding: 指定的注入编码
            output_callback: 实时输出回调函数
            
        Returns:
            ExecutionResult: 执行结果
        """
        # 转义路径
        script_path = self._escape_path(script_folder)
        json_path = self._escape_path(json_folder)
        output_path = self._escape_path(output_folder)
        
        # 构建基础命令
        cmd_parts = [
            f".\\{self.executable}",
            "import",
            "--recursive"
        ]
        
        # 添加引擎类型参数
        script_type = self._get_script_type_param(engine) if engine else None
        if script_type:
            cmd_parts.extend(["--script-type", script_type])
        
        # 添加编码参数
        if encoding and encoding != "默认编码":
            if encoding == "自动检测（不推荐）":
                encoding = "auto"
            if system() == "Windows" and self.get_code_page(encoding):
                cmd_parts.extend(["--code-page", str(self.get_code_page(encoding))])
            else:
                cmd_parts.extend(["--encoding", encoding])
        if patched_encoding and patched_encoding != "默认编码":
            # Windows 下优先使用Windows API进行字符转换，以避免潜在的Private Use Area字符问题
            if system() == "Windows" and self.get_code_page(patched_encoding):
                cmd_parts.extend(["--patched-code-page", str(self.get_code_page(patched_encoding))])
            else:
                cmd_parts.extend(["--patched-encoding", patched_encoding])
        
        # 添加路径参数
        cmd_parts.extend([script_path, json_path, output_path])
        
        # 构建完整命令
        command = " ".join(cmd_parts)
        
        # 输出命令用于调试
        if output_callback:
            output_callback(f"正在执行: {command}")
        
        return self.execute(command, timeout=600, output_callback=output_callback)
    
    def get_version(self) -> ExecutionResult:
        """获取msg-tool版本信息"""
        command = f".\\{self.executable} --version"
        return self.execute(command, timeout=10)
    
    def get_help(self) -> ExecutionResult:
        """获取msg-tool帮助信息"""
        command = f".\\{self.executable} --help"
        return self.execute(command, timeout=10)