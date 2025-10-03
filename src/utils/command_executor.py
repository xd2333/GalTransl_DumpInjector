"""
命令执行工具类
安全执行外部命令并处理输出
"""

import subprocess
import threading
import time
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """执行结果数据类"""
    status: ExecutionStatus
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: str
    error_message: Optional[str] = None


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = working_dir
        self._process: Optional[subprocess.Popen] = None
        self._cancelled = False
    
    def execute(
        self, 
        command: str, 
        timeout: Optional[float] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ExecutionResult:
        """执行命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            output_callback: 实时输出回调函数
        
        Returns:
            ExecutionResult: 执行结果
        """
        start_time = time.time()
        self._cancelled = False
        
        try:
            # 创建进程
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=self.working_dir,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # 实时读取输出
            if output_callback:
                stdout_thread = threading.Thread(
                    target=self._read_output_stream,
                    args=(self._process.stdout, stdout_lines, output_callback)
                )
                stderr_thread = threading.Thread(
                    target=self._read_output_stream,
                    args=(self._process.stderr, stderr_lines, None)
                )
                
                stdout_thread.start()
                stderr_thread.start()
                
                # 等待进程完成
                try:
                    return_code = self._process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    self.cancel()
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        return_code=-1,
                        stdout="",
                        stderr="",
                        execution_time=time.time() - start_time,
                        command=command,
                        error_message="命令执行超时"
                    )
                
                # 等待输出线程完成
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
            else:
                # 简单执行，不需要实时输出
                try:
                    stdout, stderr = self._process.communicate(timeout=timeout)
                    return_code = self._process.returncode
                    stdout_lines = [stdout] if stdout else []
                    stderr_lines = [stderr] if stderr else []
                except subprocess.TimeoutExpired:
                    self.cancel()
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        return_code=-1,
                        stdout="",
                        stderr="",
                        execution_time=time.time() - start_time,
                        command=command,
                        error_message="命令执行超时"
                    )
            
            execution_time = time.time() - start_time
            
            if self._cancelled:
                status = ExecutionStatus.CANCELLED
            elif return_code == 0:
                status = ExecutionStatus.COMPLETED
            else:
                status = ExecutionStatus.FAILED
            
            return ExecutionResult(
                status=status,
                return_code=return_code,
                stdout="".join(stdout_lines),
                stderr="".join(stderr_lines),
                execution_time=execution_time,
                command=command
            )
        
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr="",
                execution_time=time.time() - start_time,
                command=command,
                error_message=f"执行异常: {str(e)}"
            )
    
    def _read_output_stream(
        self, 
        stream, 
        lines_list: List[str], 
        callback: Optional[Callable[[str], None]]
    ):
        """读取输出流"""
        try:
            for line in iter(stream.readline, ''):
                if self._cancelled:
                    break
                
                lines_list.append(line)
                if callback:
                    callback(line.rstrip())
        except Exception:
            pass  # 忽略读取异常
    
    def cancel(self):
        """取消执行"""
        self._cancelled = True
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                # 等待进程结束
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 强制杀死进程
                    self._process.kill()
            except Exception:
                pass  # 忽略取消异常


class VNTextPatchExecutor(CommandExecutor):
    """VNTextPatch专用执行器"""
    
    def __init__(self, vntextpatch_dir: str = ".\\VNTextPatch"):
        super().__init__(working_dir=vntextpatch_dir)
        self.vntextpatch_dir = vntextpatch_dir
    
    def extract(
        self,
        script_folder: str,
        json_folder: str,
        engine: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ExecutionResult:
        """提取脚本到JSON"""
        # 处理路径中的空格
        if " " in script_folder:
            script_folder = f'"{script_folder}"'
        if " " in json_folder:
            json_folder = f'"{json_folder}"'
        
        # 构建命令
        base_cmd = ".\\VNTextPatch.exe extractlocal"
        if engine and engine != "自动判断":
            cmd = f"{base_cmd} {script_folder} {json_folder} --format={engine}"
        else:
            cmd = f"{base_cmd} {script_folder} {json_folder}"
        
        return self.execute(cmd, timeout=300, output_callback=output_callback)
    
    def inject(
        self,
        script_folder: str,
        json_folder: str,
        output_folder: str,
        engine: Optional[str] = None,
        use_gbk: bool = False,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ExecutionResult:
        """注入JSON回脚本"""
        # 处理路径中的空格
        if " " in script_folder:
            script_folder = f'"{script_folder}"'
        if " " in json_folder:
            json_folder = f'"{json_folder}"'
        if " " in output_folder:
            output_folder = f'"{output_folder}"'
        
        # 选择执行文件
        exe_name = ".\\VNTextPatchGBK.exe" if use_gbk else ".\\VNTextPatch.exe"
        
        # 构建命令
        base_cmd = f"{exe_name} insertlocal"
        if engine and engine != "自动判断":
            cmd = f"{base_cmd} {script_folder} {json_folder} {output_folder} --format={engine}"
        else:
            cmd = f"{base_cmd} {script_folder} {json_folder} {output_folder}"
        
        return self.execute(cmd, timeout=600, output_callback=output_callback)


class AsyncCommandExecutor:
    """异步命令执行器"""
    
    def __init__(self):
        self._running_tasks: Dict[str, threading.Thread] = {}
        self._results: Dict[str, ExecutionResult] = {}
    
    def execute_async(
        self,
        task_id: str,
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[float] = None,
        output_callback: Optional[Callable[[str], None]] = None,
        completion_callback: Optional[Callable[[str, ExecutionResult], None]] = None
    ):
        """异步执行命令"""
        if task_id in self._running_tasks:
            raise ValueError(f"任务 {task_id} 已在运行中")
        
        def run_command():
            executor = CommandExecutor(working_dir)
            result = executor.execute(command, timeout, output_callback)
            self._results[task_id] = result
            
            # 清理运行任务
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            
            # 调用完成回调
            if completion_callback:
                completion_callback(task_id, result)
        
        thread = threading.Thread(target=run_command, daemon=True)
        self._running_tasks[task_id] = thread
        thread.start()
    
    def is_running(self, task_id: str) -> bool:
        """检查任务是否在运行"""
        return task_id in self._running_tasks
    
    def get_result(self, task_id: str) -> Optional[ExecutionResult]:
        """获取任务结果"""
        return self._results.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self._running_tasks:
            # 注意：线程无法直接取消，这里只是从列表中移除
            del self._running_tasks[task_id]
            return True
        return False
    
    def get_running_tasks(self) -> List[str]:
        """获取正在运行的任务列表"""
        return list(self._running_tasks.keys())