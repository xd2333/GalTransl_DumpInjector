"""
正则表达式模式标签页
正则表达式模式的用户界面逻辑
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .widgets.file_selector import FileSelector
from .widgets.output_display import RealTimeOutputDisplay
from ..core.regex_processor import RegexProcessor
from ..models.config import Config


class RegexTab:
    """正则表达式模式标签页"""
    
    def __init__(self, parent: ttk.Notebook, config: Config):
        """
        Args:
            parent: 父级Notebook组件
            config: 配置管理器
        """
        self.parent = parent
        self.config = config
        self.processor = RegexProcessor()
        
        # 创建标签页
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="正则表达式模式")
        
        # 当前操作状态
        self._is_processing = False
        
        # 创建界面
        self._create_widgets()
        self._setup_layout()
        self._load_config()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 文件选择器
        self.script_jp_selector = FileSelector(
            self.frame,
            "日文脚本文件夹",
            width=50,
            selection_type="folder"
        )
        
        self.json_jp_selector = FileSelector(
            self.frame,
            "日文JSON保存文件夹",
            width=50,
            selection_type="folder"
        )
        
        # 正则表达式输入
        self.regex_frame = ttk.Frame(self.frame)
        
        # 消息正则表达式
        self.message_regex_label = ttk.Label(self.regex_frame, text="正文提取正则")
        self.message_regex_var = tk.StringVar()
        self.message_regex_entry = ttk.Entry(
            self.regex_frame,
            textvariable=self.message_regex_var,
            width=50
        )
        
        # 人名正则表达式
        self.name_regex_label = ttk.Label(self.regex_frame, text="人名提取正则")
        self.name_regex_var = tk.StringVar()
        self.name_regex_entry = ttk.Entry(
            self.regex_frame,
            textvariable=self.name_regex_var,
            width=50
        )
        
        # 编码选择和提取按钮
        self.extract_frame = ttk.Frame(self.frame)
        
        self.jp_encoding_label = ttk.Label(self.extract_frame, text="日文脚本编码")
        self.jp_encoding_var = tk.StringVar(value="sjis")
        self.jp_encoding_combo = ttk.Combobox(
            self.extract_frame,
            textvariable=self.jp_encoding_var,
            values=self.processor.get_supported_encodings(),
            state="readonly",
            width=15
        )
        
        self.extract_button = ttk.Button(
            self.extract_frame,
            text="提取脚本到JSON",
            command=self._extract_text
        )
        
        # 注入部分
        self.json_cn_selector = FileSelector(
            self.frame,
            "译文JSON文件夹",
            width=50,
            selection_type="folder"
        )
        
        self.script_cn_selector = FileSelector(
            self.frame,
            "译文脚本保存文件夹",
            width=50,
            selection_type="folder"
        )
        
        # 注入选项
        self.inject_frame = ttk.Frame(self.frame)
        
        self.cn_encoding_label = ttk.Label(self.inject_frame, text="中文脚本编码")
        self.cn_encoding_var = tk.StringVar(value="gbk")
        self.cn_encoding_combo = ttk.Combobox(
            self.inject_frame,
            textvariable=self.cn_encoding_var,
            values=self.processor.get_supported_encodings(),
            state="readonly",
            width=15
        )
        
        self.inject_button = ttk.Button(
            self.inject_frame,
            text="注入JSON回脚本",
            command=self._inject_text
        )
        
        # SJIS替换选项
        self.sjis_frame = ttk.Frame(self.frame)
        self.sjis_replace_var = tk.BooleanVar(value=False)
        self.sjis_replace_check = ttk.Checkbutton(
            self.sjis_frame,
            text="SJIS替换模式注入",
            variable=self.sjis_replace_var,
            command=self._toggle_sjis_options
        )
        
        self.sjis_char_var = tk.StringVar()
        self.sjis_char_entry = ttk.Entry(
            self.sjis_frame,
            textvariable=self.sjis_char_var,
            width=10,
            state="disabled"
        )
        self.sjis_char_label = ttk.Label(
            self.sjis_frame,
            text="👆要替换的字符(空为全量替换)"
        )
        
        # 测试按钮
        self.test_frame = ttk.Frame(self.frame)
        self.test_regex_button = ttk.Button(
            self.test_frame,
            text="测试正则表达式",
            command=self._test_regex
        )
        
        # 输出显示
        self.output_display = RealTimeOutputDisplay(
            self.frame,
            height=10,
            width=50
        )
        
        # 状态栏
        self.status_frame = ttk.Frame(self.frame)
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var
        )
        
        self.cancel_button = ttk.Button(
            self.status_frame,
            text="取消操作",
            command=self._cancel_operation,
            state="disabled"
        )
    
    def _setup_layout(self):
        """设置布局"""
        row = 0
        
        # 文件选择器
        self.script_jp_selector.grid(row=row, column=0, columnspan=3, 
                                   sticky="ew", padx=5, pady=5)
        row += 1
        
        self.json_jp_selector.grid(row=row, column=0, columnspan=3, 
                                 sticky="ew", padx=5, pady=5)
        row += 1
        
        # 正则表达式输入
        self.regex_frame.grid(row=row, column=0, columnspan=3, 
                            sticky="ew", padx=5, pady=5)
        
        self.message_regex_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.message_regex_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.name_regex_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_regex_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.regex_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 编码选择和提取
        self.extract_frame.grid(row=row, column=0, columnspan=3, 
                              sticky="ew", padx=5, pady=5)
        
        self.jp_encoding_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.jp_encoding_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.extract_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        self.extract_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 注入文件选择器
        self.json_cn_selector.grid(row=row, column=0, columnspan=3, 
                                 sticky="ew", padx=5, pady=5)
        row += 1
        
        self.script_cn_selector.grid(row=row, column=0, columnspan=3, 
                                   sticky="ew", padx=5, pady=5)
        row += 1
        
        # 注入选项
        self.inject_frame.grid(row=row, column=0, columnspan=3, 
                             sticky="ew", padx=5, pady=5)
        
        self.cn_encoding_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cn_encoding_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.inject_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        self.inject_frame.columnconfigure(1, weight=1)
        row += 1
        
        # SJIS替换选项
        self.sjis_frame.grid(row=row, column=0, columnspan=3, 
                           sticky="ew", padx=5, pady=5)
        
        self.sjis_replace_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sjis_char_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.sjis_char_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.sjis_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 测试按钮
        self.test_frame.grid(row=row, column=0, columnspan=3, 
                           sticky="ew", padx=5, pady=5)
        self.test_regex_button.pack(side=tk.LEFT, padx=5)
        row += 1
        
        # 输出显示
        self.output_display.grid(row=row, column=0, columnspan=3, 
                               sticky="ew", padx=5, pady=5)
        row += 1
        
        # 状态栏
        self.status_frame.grid(row=row, column=0, columnspan=3, 
                             sticky="ew", padx=5, pady=5)
        self.status_label.pack(side=tk.LEFT, padx=5)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 配置主框架的列权重
        self.frame.columnconfigure(0, weight=1)
    
    def _toggle_sjis_options(self):
        """切换SJIS选项的启用状态"""
        enabled = self.sjis_replace_var.get()
        state = "normal" if enabled else "disabled"
        self.sjis_char_entry.config(state=state)
    
    def _load_config(self):
        """从配置加载界面值"""
        self.script_jp_selector.set_path(self.config.script_jp_folder)
        self.json_jp_selector.set_path(self.config.json_jp_folder)
        self.json_cn_selector.set_path(self.config.json_cn_folder)
        self.script_cn_selector.set_path(self.config.script_cn_folder)
        
        self.message_regex_var.set(self.config.message_regex)
        self.name_regex_var.set(self.config.name_regex)
        self.jp_encoding_var.set(self.config.japanese_encoding)
        self.cn_encoding_var.set(self.config.chinese_encoding)
        
        self.sjis_replace_var.set(self.config.sjis_replacement)
        self._toggle_sjis_options()
    
    def _save_config(self):
        """保存界面值到配置"""
        self.config.script_jp_folder = self.script_jp_selector.get_path()
        self.config.json_jp_folder = self.json_jp_selector.get_path()
        self.config.json_cn_folder = self.json_cn_selector.get_path()
        self.config.script_cn_folder = self.script_cn_selector.get_path()
        
        self.config.message_regex = self.message_regex_var.get()
        self.config.name_regex = self.name_regex_var.get()
        self.config.japanese_encoding = self.jp_encoding_var.get()
        self.config.chinese_encoding = self.cn_encoding_var.get()
        
        self.config.sjis_replacement = self.sjis_replace_var.get()
        
        self.config.save_config()
    
    def _extract_text(self):
        """提取文本"""
        if self._is_processing:
            return
        
        # 获取参数
        script_folder = self.script_jp_selector.get_path()
        json_folder = self.json_jp_selector.get_path()
        message_pattern = self.message_regex_var.get()
        name_pattern = self.name_regex_var.get()
        encoding = self.jp_encoding_var.get()
        
        # 验证参数
        if not script_folder:
            messagebox.showerror("错误", "请选择日文脚本目录")
            return
        
        if not json_folder:
            messagebox.showerror("错误", "请选择日文JSON保存目录")
            return
        
        if not message_pattern:
            messagebox.showerror("错误", "请输入正文提取正则表达式")
            return
        
        # 开始处理
        self._set_processing_state(True, "正在提取文本...")
        self.output_display.clear()
        
        # 创建输出回调
        output_callback = self.output_display.create_output_callback()
        
        # 异步执行提取
        import threading
        def extract_worker():
            try:
                result = self.processor.extract_with_regex(
                    script_folder, json_folder, message_pattern,
                    name_pattern if name_pattern else None,
                    encoding, output_callback
                )
                
                # 在主线程中更新界面
                self.frame.after(0, lambda: self._on_extract_complete(result))
            except Exception as e:
                self.frame.after(0, lambda: self._on_operation_error(str(e)))
        
        thread = threading.Thread(target=extract_worker, daemon=True)
        thread.start()
    
    def _inject_text(self):
        """注入文本"""
        if self._is_processing:
            return
        
        # 获取参数
        script_folder = self.script_jp_selector.get_path()
        json_jp_folder = self.json_jp_selector.get_path()
        json_cn_folder = self.json_cn_selector.get_path()
        output_folder = self.script_cn_selector.get_path()
        message_pattern = self.message_regex_var.get()
        name_pattern = self.name_regex_var.get()
        jp_encoding = self.jp_encoding_var.get()
        cn_encoding = self.cn_encoding_var.get()
        sjis_replacement = self.sjis_replace_var.get()
        sjis_chars = self.sjis_char_var.get()
        
        # 验证参数
        if not script_folder:
            messagebox.showerror("错误", "请选择日文脚本目录")
            return
        
        if not json_jp_folder:
            messagebox.showerror("错误", "请选择日文JSON目录")
            return
        
        if not json_cn_folder:
            messagebox.showerror("错误", "请选择译文JSON目录")
            return
        
        if not output_folder:
            messagebox.showerror("错误", "请选择译文脚本保存目录")
            return
        
        if not message_pattern:
            messagebox.showerror("错误", "请输入正文替换正则表达式")
            return
        
        # 开始处理
        self._set_processing_state(True, "正在注入文本...")
        self.output_display.clear()
        
        # 创建输出回调
        output_callback = self.output_display.create_output_callback()
        
        # 异步执行注入
        import threading
        def inject_worker():
            try:
                result = self.processor.inject_with_regex(
                    script_folder, json_jp_folder, json_cn_folder, output_folder,
                    message_pattern, name_pattern if name_pattern else None,
                    jp_encoding, cn_encoding, sjis_replacement, sjis_chars,
                    output_callback
                )
                
                # 在主线程中更新界面
                self.frame.after(0, lambda: self._on_inject_complete(result))
            except Exception as e:
                self.frame.after(0, lambda: self._on_operation_error(str(e)))
        
        thread = threading.Thread(target=inject_worker, daemon=True)
        thread.start()
    
    def _test_regex(self):
        """测试正则表达式"""
        message_pattern = self.message_regex_var.get()
        name_pattern = self.name_regex_var.get()
        
        if not message_pattern:
            messagebox.showerror("错误", "请输入正文提取正则表达式")
            return
        
        # 验证正则表达式
        result = self.processor.validate_regex_patterns(message_pattern, name_pattern)
        
        if result.success:
            self.output_display.add_success_text("正则表达式验证通过")
            self.output_display.add_info_text(result.message)
        else:
            self.output_display.add_error_text(f"正则表达式验证失败: {result.message}")
    
    def _on_extract_complete(self, result):
        """提取完成回调"""
        self._set_processing_state(False, "提取完成")
        
        if result.success:
            self.output_display.add_success_text(result.message)
            self._save_config()  # 保存配置
        else:
            self.output_display.add_error_text(f"提取失败: {result.message}")
    
    def _on_inject_complete(self, result):
        """注入完成回调"""
        self._set_processing_state(False, "注入完成")
        
        if result.success:
            self.output_display.add_success_text(result.message)
            
            # 显示SJIS配置信息
            if result.sjis_config:
                self.output_display.add_info_text(result.sjis_config)
            
            self._save_config()  # 保存配置
        else:
            self.output_display.add_error_text(f"注入失败: {result.message}")
    
    def _on_operation_error(self, error_message: str):
        """操作错误回调"""
        self._set_processing_state(False, "操作失败")
        self.output_display.add_error_text(f"操作异常: {error_message}")
    
    def _cancel_operation(self):
        """取消当前操作"""
        if self._is_processing:
            self._set_processing_state(False, "操作已取消")
            self.output_display.add_warning_text("操作已被用户取消")
    
    def _set_processing_state(self, processing: bool, status_text: str = ""):
        """设置处理状态"""
        self._is_processing = processing
        
        # 更新状态文本
        if status_text:
            self.status_var.set(status_text)
        
        # 更新按钮状态
        button_state = "disabled" if processing else "normal"
        self.extract_button.config(state=button_state)
        self.inject_button.config(state=button_state)
        self.test_regex_button.config(state=button_state)
        
        # 取消按钮状态相反
        cancel_state = "normal" if processing else "disabled"
        self.cancel_button.config(state=cancel_state)
        
        # 显示/隐藏进度条
        if processing:
            self.output_display.show_progress(True)
            self.output_display.update_progress(0, status_text)
        else:
            self.output_display.show_progress(False)
    
    def get_current_patterns(self) -> dict:
        """获取当前正则表达式"""
        return {
            "message_regex": self.message_regex_var.get(),
            "name_regex": self.name_regex_var.get(),
            "japanese_encoding": self.jp_encoding_var.get(),
            "chinese_encoding": self.cn_encoding_var.get()
        }
    
    def set_patterns(self, patterns: dict):
        """设置正则表达式"""
        if "message_regex" in patterns:
            self.message_regex_var.set(patterns["message_regex"])
        if "name_regex" in patterns:
            self.name_regex_var.set(patterns["name_regex"])
        if "japanese_encoding" in patterns:
            self.jp_encoding_var.set(patterns["japanese_encoding"])
        if "chinese_encoding" in patterns:
            self.cn_encoding_var.set(patterns["chinese_encoding"])
    
    def cleanup(self):
        """清理资源"""
        if self._is_processing:
            self._cancel_operation()
        
        self.output_display.stop_output_monitoring()
        self._save_config()