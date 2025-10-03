"""
输出显示组件
可复用的输出结果显示组件
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable
import threading
import queue
import time


class OutputDisplay:
    """输出显示组件"""
    
    def __init__(
        self,
        parent: tk.Widget,
        height: int = 14,
        width: int = 50,
        wrap: str = tk.WORD,
        show_toolbar: bool = True
    ):
        """
        Args:
            parent: 父组件
            height: 文本框高度
            width: 文本框宽度
            wrap: 文本换行模式
            show_toolbar: 是否显示工具栏
        """
        self.parent = parent
        self.height = height
        self.width = width
        self.wrap = wrap
        self.show_toolbar = show_toolbar
        
        # 输出队列（用于线程安全的输出）
        self._output_queue = queue.Queue()
        self._is_monitoring = False
        
        # 创建组件
        self._create_widgets()
        
        # 启动输出监控
        self._start_output_monitoring()
    
    def _create_widgets(self):
        """创建组件"""
        self.frame = ttk.Frame(self.parent)
        
        # 工具栏
        if self.show_toolbar:
            self._create_toolbar()
        
        # 标签
        self.label = ttk.Label(self.frame, text="输出结果")
        
        # 文本框
        self.text_widget = scrolledtext.ScrolledText(
            self.frame,
            height=self.height,
            width=self.width,
            wrap=self.wrap,
            font=("Consolas", 9)
        )
        
        # 进度条
        self.progress_frame = ttk.Frame(self.frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode='determinate',
            length=200
        )
        self.progress_label = ttk.Label(self.progress_frame, text="")
        
        # 默认隐藏进度条
        self.progress_frame.grid_remove()
    
    def _create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.frame)
        
        # 清空按钮
        self.clear_button = ttk.Button(
            self.toolbar,
            text="清空",
            command=self.clear
        )
        
        # 保存按钮
        self.save_button = ttk.Button(
            self.toolbar,
            text="保存日志",
            command=self._save_log
        )
        
        # 自动滚动开关
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = ttk.Checkbutton(
            self.toolbar,
            text="自动滚动",
            variable=self.auto_scroll_var
        )
        
        # 工具栏布局
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        self.auto_scroll_check.pack(side=tk.LEFT, padx=(0, 5))
    
    def grid(self, row: int, column: int = 0, **kwargs):
        """网格布局"""
        self.frame.grid(row=row, column=column, **kwargs)
        
        current_row = 0
        
        # 布局工具栏
        if self.show_toolbar:
            self.toolbar.grid(row=current_row, column=0, columnspan=3, 
                            sticky="ew", padx=5, pady=5)
            current_row += 1
        
        # 布局标签
        self.label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        current_row += 1
        
        # 布局文本框
        self.text_widget.grid(row=current_row, column=0, columnspan=3, 
                             sticky="ew", padx=5, pady=5)
        current_row += 1
        
        # 布局进度条
        self.progress_frame.grid(row=current_row, column=0, columnspan=3, 
                               sticky="ew", padx=5, pady=5)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        self.progress_label.pack(side=tk.LEFT)
        
        # 配置列权重
        self.frame.columnconfigure(0, weight=1)
    
    def pack(self, **kwargs):
        """包装布局"""
        self.frame.pack(**kwargs)
        
        # 布局工具栏
        if self.show_toolbar:
            self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 布局标签
        self.label.pack(anchor="w", padx=5, pady=5)
        
        # 布局文本框
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 布局进度条
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        self.progress_label.pack(side=tk.LEFT)
    
    def append_text(self, text: str, tag: Optional[str] = None):
        """追加文本"""
        # 线程安全的方式添加到队列
        self._output_queue.put(('text', text, tag))
    
    def append_line(self, text: str, tag: Optional[str] = None):
        """追加一行文本"""
        self.append_text(text + "\n", tag)
    
    def _process_output_queue(self):
        """处理输出队列"""
        try:
            while True:
                item = self._output_queue.get_nowait()
                if item[0] == 'text':
                    _, text, tag = item
                    self._append_text_internal(text, tag)
                elif item[0] == 'clear':
                    self._clear_internal()
                elif item[0] == 'progress':
                    _, value, text = item
                    self._update_progress_internal(value, text)
        except queue.Empty:
            pass
        
        # 继续监控
        if self._is_monitoring:
            self.parent.after(100, self._process_output_queue)
    
    def _append_text_internal(self, text: str, tag: Optional[str] = None):
        """内部追加文本方法"""
        self.text_widget.insert(tk.END, text, tag)
        
        # 自动滚动到底部
        if self.auto_scroll_var.get():
            self.text_widget.see(tk.END)
    
    def clear(self):
        """清空输出"""
        self._output_queue.put(('clear',))
    
    def _clear_internal(self):
        """内部清空方法"""
        self.text_widget.delete(1.0, tk.END)
    
    def get_text(self) -> str:
        """获取所有文本"""
        return self.text_widget.get(1.0, tk.END)
    
    def set_label_text(self, text: str):
        """设置标签文本"""
        self.label.config(text=text)
    
    def show_progress(self, show: bool = True):
        """显示/隐藏进度条"""
        if show:
            self.progress_frame.grid()
        else:
            self.progress_frame.grid_remove()
    
    def update_progress(self, value: float, text: str = ""):
        """更新进度"""
        self._output_queue.put(('progress', value, text))
    
    def _update_progress_internal(self, value: float, text: str):
        """内部更新进度方法"""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
    
    def _start_output_monitoring(self):
        """启动输出监控"""
        self._is_monitoring = True
        self._process_output_queue()
    
    def stop_output_monitoring(self):
        """停止输出监控"""
        self._is_monitoring = False
    
    def _save_log(self):
        """保存日志"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.get_text())
                self.append_line(f"日志已保存到: {file_path}")
            except Exception as e:
                self.append_line(f"保存日志失败: {str(e)}")
    
    def configure_tags(self, tag_configs: dict):
        """配置文本标签样式"""
        for tag, config in tag_configs.items():
            self.text_widget.tag_configure(tag, **config)
    
    def add_error_text(self, text: str):
        """添加错误文本"""
        self.append_line(text, "error")
    
    def add_warning_text(self, text: str):
        """添加警告文本"""
        self.append_line(text, "warning")
    
    def add_success_text(self, text: str):
        """添加成功文本"""
        self.append_line(text, "success")
    
    def add_info_text(self, text: str):
        """添加信息文本"""
        self.append_line(text, "info")


class RealTimeOutputDisplay(OutputDisplay):
    """实时输出显示组件"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 配置默认的文本样式
        self.configure_tags({
            "error": {"foreground": "red"},
            "warning": {"foreground": "orange"},
            "success": {"foreground": "green"},
            "info": {"foreground": "blue"}
        })
    
    def create_output_callback(self) -> Callable[[str], None]:
        """创建输出回调函数，用于实时接收输出"""
        def callback(text: str):
            # 简单的日志级别识别
            text_lower = text.lower()
            if "error" in text_lower or "失败" in text_lower:
                self.add_error_text(text)
            elif "warning" in text_lower or "警告" in text_lower:
                self.add_warning_text(text)
            elif "success" in text_lower or "完成" in text_lower or "成功" in text_lower:
                self.add_success_text(text)
            else:
                self.append_line(text)
        
        return callback