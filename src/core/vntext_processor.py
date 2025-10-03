"""
VNTextPatch处理器
处理VNTextPatch模式的核心业务逻辑
"""

import os
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

from ..utils.command_executor import VNTextPatchExecutor, ExecutionResult, ExecutionStatus
from ..utils.validators import VNTextPatchValidator, ValidationSummary
from ..core.sjis_handler import SJISHandler, SJISExtBinaryHandler
from ..core.file_operations import FileOperations


@dataclass
class VNTextProcessResult:
    """VNTextPatch处理结果"""
    success: bool
    message: str
    execution_result: Optional[ExecutionResult] = None
    sjis_ext_content: Optional[str] = None
    sjis_config: Optional[str] = None


class VNTextProcessor:
    """VNTextPatch处理器"""
    
    def __init__(self, vntextpatch_dir: str = ".\\VNTextPatch"):
        self.vntextpatch_dir = vntextpatch_dir
        self.executor = VNTextPatchExecutor(vntextpatch_dir)
        self.sjis_handler = SJISHandler()
    
    def extract_text(
        self,
        script_folder: str,
        json_folder: str,
        engine: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> VNTextProcessResult:
        """提取脚本文本到JSON
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: JSON保存文件夹路径
            engine: 指定的引擎（可选）
            output_callback: 实时输出回调函数
        
        Returns:
            VNTextProcessResult: 处理结果
        """
        try:
            # 验证输入参数
            validation_results = VNTextPatchValidator.validate_extract_params(
                script_folder, json_folder, engine or "自动判断"
            )
            
            is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
            if not is_valid:
                return VNTextProcessResult(
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
                return VNTextProcessResult(
                    success=True,
                    message="文本提取成功",
                    execution_result=result
                )
            elif result.status == ExecutionStatus.CANCELLED:
                return VNTextProcessResult(
                    success=False,
                    message="提取操作被取消",
                    execution_result=result
                )
            else:
                error_msg = result.stderr or result.error_message or "未知错误"
                return VNTextProcessResult(
                    success=False,
                    message=f"文本提取失败: {error_msg}",
                    execution_result=result
                )
        
        except Exception as e:
            return VNTextProcessResult(
                success=False,
                message=f"提取过程异常: {str(e)}"
            )
    
    def inject_text(
        self,
        script_folder: str,
        json_folder: str,
        output_folder: str,
        engine: Optional[str] = None,
        use_gbk: bool = False,
        sjis_replacement: bool = False,
        sjis_replace_chars: str = "",
        output_callback: Optional[Callable[[str], None]] = None
    ) -> VNTextProcessResult:
        """注入JSON文本回脚本
        
        Args:
            script_folder: 日文脚本文件夹路径
            json_folder: 译文JSON文件夹路径
            output_folder: 输出脚本文件夹路径
            engine: 指定的引擎（可选）
            use_gbk: 是否使用GBK编码注入
            sjis_replacement: 是否启用SJIS替换模式
            sjis_replace_chars: SJIS替换字符
            output_callback: 实时输出回调函数
        
        Returns:
            VNTextProcessResult: 处理结果
        """
        try:
            # 验证输入参数
            validation_results = VNTextPatchValidator.validate_inject_params(
                script_folder, json_folder, output_folder, engine or "自动判断"
            )
            
            is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
            if not is_valid:
                return VNTextProcessResult(
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
                    return VNTextProcessResult(
                        success=False,
                        message=f"SJIS字符替换失败: {str(e)}"
                    )
            
            # 清理可能存在的sjis_ext.bin文件
            SJISExtBinaryHandler.process_sjis_ext_output(output_folder)
            
            # 执行注入命令
            result = self.executor.inject(
                script_folder, actual_json_folder, output_folder, 
                engine, use_gbk, output_callback
            )
            
            # 检查sjis_ext.bin文件
            sjis_ext_content = SJISExtBinaryHandler.get_sjis_ext_content(output_folder)
            
            # 分析执行结果
            if result.status == ExecutionStatus.COMPLETED:
                success_message = "文本注入成功"
                if sjis_ext_content:
                    success_message += f"\nsjis_ext.bin包含文字：{sjis_ext_content}"
                
                return VNTextProcessResult(
                    success=True,
                    message=success_message,
                    execution_result=result,
                    sjis_ext_content=sjis_ext_content,
                    sjis_config=sjis_config
                )
            elif result.status == ExecutionStatus.CANCELLED:
                return VNTextProcessResult(
                    success=False,
                    message="注入操作被取消",
                    execution_result=result
                )
            else:
                error_msg = result.stderr or result.error_message or "未知错误"
                return VNTextProcessResult(
                    success=False,
                    message=f"文本注入失败: {error_msg}",
                    execution_result=result
                )
        
        except Exception as e:
            return VNTextProcessResult(
                success=False,
                message=f"注入过程异常: {str(e)}"
            )
    
    def validate_paths(self, paths: Dict[str, str]) -> VNTextProcessResult:
        """验证路径有效性"""
        try:
            # 根据操作类型验证路径
            if "script_folder" in paths and "json_folder" in paths:
                if "output_folder" in paths:
                    # 注入操作验证
                    validation_results = VNTextPatchValidator.validate_inject_params(
                        paths["script_folder"],
                        paths["json_folder"],
                        paths["output_folder"],
                        paths.get("engine", "自动判断")
                    )
                else:
                    # 提取操作验证
                    validation_results = VNTextPatchValidator.validate_extract_params(
                        paths["script_folder"],
                        paths["json_folder"],
                        paths.get("engine", "自动判断")
                    )
                
                is_valid, validation_message = ValidationSummary.summarize_results(validation_results)
                
                return VNTextProcessResult(
                    success=is_valid,
                    message=validation_message
                )
            else:
                return VNTextProcessResult(
                    success=False,
                    message="缺少必要的路径参数"
                )
        
        except Exception as e:
            return VNTextProcessResult(
                success=False,
                message=f"路径验证异常: {str(e)}"
            )
    
    def get_supported_engines(self) -> list[str]:
        """获取支持的引擎列表"""
        return [
            "自动判断",
            "artemistxt",
            "ethornell", 
            "kirikiriks",
            "reallive",
            "tmrhiroadvsystemtext",
            "whale"
        ]
    
    def check_vntextpatch_availability(self) -> VNTextProcessResult:
        """检查VNTextPatch工具是否可用"""
        try:
            vntextpatch_exe = os.path.join(self.vntextpatch_dir, "VNTextPatch.exe")
            vntextpatch_gbk_exe = os.path.join(self.vntextpatch_dir, "VNTextPatchGBK.exe")
            
            exe_exists = os.path.exists(vntextpatch_exe)
            gbk_exe_exists = os.path.exists(vntextpatch_gbk_exe)
            
            if not exe_exists and not gbk_exe_exists:
                return VNTextProcessResult(
                    success=False,
                    message=f"VNTextPatch工具不存在，请检查路径: {self.vntextpatch_dir}"
                )
            
            status_messages = []
            if exe_exists:
                status_messages.append("VNTextPatch.exe ✓")
            else:
                status_messages.append("VNTextPatch.exe ✗")
            
            if gbk_exe_exists:
                status_messages.append("VNTextPatchGBK.exe ✓")
            else:
                status_messages.append("VNTextPatchGBK.exe ✗")
            
            return VNTextProcessResult(
                success=exe_exists or gbk_exe_exists,
                message="VNTextPatch工具状态:\n" + "\n".join(status_messages)
            )
        
        except Exception as e:
            return VNTextProcessResult(
                success=False,
                message=f"检查VNTextPatch工具时发生异常: {str(e)}"
            )
    
    def cancel_current_operation(self):
        """取消当前操作"""
        try:
            self.executor.cancel()
        except Exception:
            pass  # 忽略取消异常
    
    def get_operation_stats(self, result: VNTextProcessResult) -> Dict[str, Any]:
        """获取操作统计信息"""
        stats = {
            "success": result.success,
            "message": result.message
        }
        
        if result.execution_result:
            stats.update({
                "execution_time": result.execution_result.execution_time,
                "return_code": result.execution_result.return_code,
                "command": result.execution_result.command,
                "status": result.execution_result.status.value
            })
        
        if result.sjis_ext_content:
            stats["sjis_ext_chars"] = len(result.sjis_ext_content)
        
        if result.sjis_config:
            stats["sjis_replacement_applied"] = True
        
        return stats