"""
Msg-tool处理器
处理msg-tool模式的核心业务逻辑
"""

import os
import threading
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

from ..utils.msgtool_executor import MsgToolExecutor
from ..utils.command_executor import ExecutionResult, ExecutionStatus, AsyncCommandExecutor
from ..utils.validators import MsgToolValidator, ValidationSummary
from ..core.sjis_handler import SJISHandler, SJISExtBinaryHandler
from ..core.file_operations import FileOperations


@dataclass
class MsgToolProcessResult:
    """Msg-tool处理结果"""
    success: bool
    message: str
    execution_result: Optional[ExecutionResult] = None
    sjis_ext_content: Optional[str] = None
    sjis_config: Optional[str] = None


class MsgToolProcessor:
    """Msg-tool处理器"""
    
    def __init__(self, msgtool_dir: str = "msg_tool"):
        """
        初始化Msg-tool处理器
        
        Args:
            msgtool_dir: msg-tool工具所在目录
        """
        self.msgtool_dir = msgtool_dir
        self.executor = MsgToolExecutor(msgtool_dir)
        self.sjis_handler = SJISHandler()
        self.async_executor = AsyncCommandExecutor()
        self._current_task_id = None
    
    def is_tool_available(self) -> bool:
        """检查msg-tool工具是否可用"""
        return self.executor.check_tool_available()
    
    def get_supported_engines(self) -> list:
        """获取支持的引擎列表"""
        return self.executor.get_supported_engines()
    
    def get_tool_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        info = {
            "available": self.is_tool_available(),
            "directory": self.msgtool_dir,
            "executable": self.executor.executable
        }
        
        if info["available"]:
            try:
                version_result = self.executor.get_version()
                if version_result.status == ExecutionStatus.COMPLETED:
                    info["version"] = version_result.stdout.strip()
                else:
                    info["version"] = "版本信息获取失败"
            except Exception:
                info["version"] = "版本信息获取异常"
        else:
            info["version"] = "工具不可用"
        
        return info
    
    def extract_text(
        self,
        script_folder: str,
        json_folder: str,
        engine: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> MsgToolProcessResult:
        """提取脚本文本到JSON
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: JSON保存文件夹路径
            engine: 指定的引擎（可选）
            output_callback: 实时输出回调函数
        
        Returns:
            MsgToolProcessResult: 处理结果
        """
        try:
            # 检查工具可用性
            if not self.is_tool_available():
                return MsgToolProcessResult(
                    success=False,
                    message="msg-tool工具不可用，请确保msg-tool.exe位于指定目录中"
                )
            
            # 验证输入参数
            validation_results = MsgToolValidator.validate_extract_params(
                script_folder, json_folder, engine or "自动检测"
            )
            
            is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
            if not is_valid:
                return MsgToolProcessResult(
                    success=False,
                    message=f"参数验证失败:\n{validation_message}"
                )
            
            # 确保输出目录存在
            FileOperations.ensure_dir_exists(json_folder)
            
            # 执行提取命令
            result = self.executor.extract(
                script_folder, json_folder, engine, output_callback
            )
            
            # 分析执行结果
            if result.status == ExecutionStatus.COMPLETED:
                return MsgToolProcessResult(
                    success=True,
                    message="文本提取成功",
                    execution_result=result
                )
            elif result.status == ExecutionStatus.CANCELLED:
                return MsgToolProcessResult(
                    success=False,
                    message="提取操作被取消",
                    execution_result=result
                )
            else:
                error_msg = result.stderr or result.error_message or "未知错误"
                return MsgToolProcessResult(
                    success=False,
                    message=f"文本提取失败: {error_msg}",
                    execution_result=result
                )
        
        except Exception as e:
            return MsgToolProcessResult(
                success=False,
                message=f"提取过程异常: {str(e)}"
            )
    
    def inject_text(
        self,
        script_folder: str,
        json_folder: str,
        output_folder: str,
        engine: Optional[str] = None,
        use_gbk_encoding: bool = False,
        sjis_replacement: bool = False,
        sjis_replace_chars: str = "",
        output_callback: Optional[Callable[[str], None]] = None
    ) -> MsgToolProcessResult:
        """注入JSON文本回脚本
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: 译文JSON文件夹路径
            output_folder: 输出脚本文件夹路径
            engine: 指定的引擎（可选）
            use_gbk_encoding: 是否使用GBK编码注入（cp932）
            sjis_replacement: 是否启用SJIS替换模式
            sjis_replace_chars: SJIS替换字符
            output_callback: 实时输出回调函数
        
        Returns:
            MsgToolProcessResult: 处理结果
        """
        try:
            # 检查工具可用性
            if not self.is_tool_available():
                return MsgToolProcessResult(
                    success=False,
                    message="msg-tool工具不可用，请确保msg-tool.exe位于指定目录中"
                )
            
            # 验证输入参数
            validation_results = MsgToolValidator.validate_inject_params(
                script_folder, json_folder, output_folder, engine or "自动检测"
            )
            
            is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
            if not is_valid:
                return MsgToolProcessResult(
                    success=False,
                    message=f"参数验证失败:\n{validation_message}"
                )
            
            # 确保输出目录存在
            FileOperations.ensure_dir_exists(output_folder)
            
            # 处理SJIS替换
            actual_json_folder = json_folder
            sjis_config = None
            
            if sjis_replacement:
                try:
                    sjis_result = self.sjis_handler.process_json_folder(
                        json_folder, sjis_replace_chars
                    )
                    actual_json_folder = sjis_result.replaced_folder
                    sjis_config = sjis_result.config_string
                    
                    if output_callback:
                        output_callback(f"SJIS替换完成，替换了 {sjis_result.replacement_count} 个字符")
                
                except Exception as e:
                    return MsgToolProcessResult(
                        success=False,
                        message=f"SJIS字符替换失败: {str(e)}"
                    )
            
            # 清理可能存在的sjis_ext.bin文件
            SJISExtBinaryHandler.process_sjis_ext_output(output_folder)
            
            # 执行注入命令
            result = self.executor.inject(
                script_folder, actual_json_folder, output_folder, 
                engine, use_gbk_encoding, output_callback
            )
            
            # 检查sjis_ext.bin文件
            sjis_ext_content = SJISExtBinaryHandler.get_sjis_ext_content(output_folder)
            
            # 分析执行结果
            if result.status == ExecutionStatus.COMPLETED:
                success_message = "文本注入成功"
                if sjis_ext_content:
                    success_message += f"\nsjis_ext.bin包含文字：{sjis_ext_content}"
                
                return MsgToolProcessResult(
                    success=True,
                    message=success_message,
                    execution_result=result,
                    sjis_ext_content=sjis_ext_content,
                    sjis_config=sjis_config
                )
            elif result.status == ExecutionStatus.CANCELLED:
                return MsgToolProcessResult(
                    success=False,
                    message="注入操作被取消",
                    execution_result=result
                )
            else:
                error_msg = result.stderr or result.error_message or "未知错误"
                return MsgToolProcessResult(
                    success=False,
                    message=f"文本注入失败: {error_msg}",
                    execution_result=result
                )
        
        except Exception as e:
            return MsgToolProcessResult(
                success=False,
                message=f"注入过程异常: {str(e)}"
            )
    
    def extract_text_async(
        self,
        script_folder: str,
        json_folder: str,
        engine: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None,
        completion_callback: Optional[Callable[[MsgToolProcessResult], None]] = None
    ) -> str:
        """异步提取脚本文本到JSON
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: JSON保存文件夹路径
            engine: 指定的引擎（可选）
            output_callback: 实时输出回调函数
            completion_callback: 完成回调函数
        
        Returns:
            str: 任务ID
        """
        import uuid
        task_id = f"extract_{uuid.uuid4().hex[:8]}"
        self._current_task_id = task_id
        
        def run_extract():
            """在后台线程中执行提取"""
            try:
                result = self.extract_text(
                    script_folder, json_folder, engine, output_callback
                )
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                error_result = MsgToolProcessResult(
                    success=False,
                    message=f"异步提取异常: {str(e)}"
                )
                if completion_callback:
                    completion_callback(error_result)
            finally:
                if self._current_task_id == task_id:
                    self._current_task_id = None
        
        thread = threading.Thread(target=run_extract, daemon=True)
        thread.start()
        
        return task_id
    
    def inject_text_async(
        self,
        script_folder: str,
        json_folder: str,
        output_folder: str,
        engine: Optional[str] = None,
        use_gbk_encoding: bool = False,
        sjis_replacement: bool = False,
        sjis_replace_chars: str = "",
        output_callback: Optional[Callable[[str], None]] = None,
        completion_callback: Optional[Callable[[MsgToolProcessResult], None]] = None
    ) -> str:
        """异步注入JSON文本回脚本
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: 译文JSON文件夹路径
            output_folder: 输出脚本文件夹路径
            engine: 指定的引擎（可选）
            use_gbk_encoding: 是否使用GBK编码注入（cp932）
            sjis_replacement: 是否启用SJIS替换模式
            sjis_replace_chars: SJIS替换字符
            output_callback: 实时输出回调函数
            completion_callback: 完成回调函数
        
        Returns:
            str: 任务ID
        """
        import uuid
        task_id = f"inject_{uuid.uuid4().hex[:8]}"
        self._current_task_id = task_id
        
        def run_inject():
            """在后台线程中执行注入"""
            try:
                result = self.inject_text(
                    script_folder, json_folder, output_folder,
                    engine, use_gbk_encoding, sjis_replacement,
                    sjis_replace_chars, output_callback
                )
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                error_result = MsgToolProcessResult(
                    success=False,
                    message=f"异步注入异常: {str(e)}"
                )
                if completion_callback:
                    completion_callback(error_result)
            finally:
                if self._current_task_id == task_id:
                    self._current_task_id = None
        
        thread = threading.Thread(target=run_inject, daemon=True)
        thread.start()
        
        return task_id
    
    def cancel_current_task(self):
        """取消当前任务"""
        if self._current_task_id:
            try:
                self.executor.cancel()
            except Exception as e:
                print(f"取消任务失败: {e}")
            finally:
                self._current_task_id = None
    
    def is_running(self) -> bool:
        """检查是否有任务在运行"""
        return self._current_task_id is not None