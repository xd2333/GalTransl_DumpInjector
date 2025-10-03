"""
VNTextPatch模式标签页
VNTextPatch模式的用户界面逻辑
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .widgets.file_selector import FileSelector
from .widgets.output_display import RealTimeOutputDisplay
from ..core.vntext_processor import VNTextProcessor
from ..models.config import Config


class VNTextTab:
    """VNTextPatch模式标签页"""
    
    def __init__(self, parent: ttk.Notebook, config: Config):
        """
        Args:
            parent: 父级Notebook组件
            config: 配置管理器
        """
        self.parent = parent
        self.config = config
        self.processor = VNTextProcessor()
        
        # 创建标签页
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="VNTextPatch模式")
        
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
        
        # 引擎选择
        self.engine_frame = ttk.Frame(self.frame)
        self.engine_label = ttk.Label(self.engine_frame, text="指定引擎")
        self.engine_var = tk.StringVar(value="自动判断")
        self.engine_combo = ttk.Combobox(
            self.engine_frame,
            textvariable=self.engine_var,
            values=self.processor.get_supported_engines(),
            state="readonly",
            width=20
        )
        
        # 提取按钮
        self.extract_button = ttk.Button(
            self.engine_frame,
            text="提取脚本到JSON",
            command=self._extract_text
        )
        
        # 注入选项
        self.inject_options_frame = ttk.Frame(self.frame)
        
        # GBK编码选项
        self.gbk_encoding_var = tk.BooleanVar(value=False)
        self.gbk_encoding_check = ttk.Checkbutton(
            self.inject_options_frame,
            text="GBK编码注入",
            variable=self.gbk_encoding_var
        )
        
        # SJIS替换选项
        self.sjis_replace_frame = ttk.Frame(self.inject_options_frame)
        self.sjis_replace_var = tk.BooleanVar(value=False)
        self.sjis_replace_check = ttk.Checkbutton(
            self.sjis_replace_frame,
            text="SJIS替换模式注入",
            variable=self.sjis_replace_var,
            command=self._toggle_sjis_options
        )
        
        # SJIS替换字符输入
        self.sjis_char_var = tk.StringVar()
        self.sjis_char_entry = ttk.Entry(
            self.sjis_replace_frame,
            textvariable=self.sjis_char_var,
            width=10,
            state="disabled"
        )
        self.sjis_char_label = ttk.Label(
            self.sjis_replace_frame,
            text="👆要替换的字符(空为全量替换)"
        )
        
        # 注入按钮
        self.inject_button = ttk.Button(
            self.inject_options_frame,
            text="注入JSON回脚本",
            command=self._inject_text
        )
        
        # 输出显示
        self.output_display = RealTimeOutputDisplay(
            self.frame,
            height=14,
            width=50
        )
        
        # 状态栏
        self.status_frame = ttk.Frame(self.frame)
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var
        )
        
        # 取消按钮
        self.cancel_button = ttk.Button(
            self.status_frame,
            text="取消操作",
            command=self._cancel_operation,
            state="disabled"
        )
    
    def _setup_layout(self):
        """设置布局"""
        row = 0
        
        # 文件选择器布局
        self.script_jp_selector.grid(row=row, column=0, columnspan=3, 
                                   sticky="ew", padx=5, pady=5)
        row += 1
        
        self.json_jp_selector.grid(row=row, column=0, columnspan=3, 
                                 sticky="ew", padx=5, pady=5)
        row += 1
        
        # 引擎选择和提取按钮
        self.engine_frame.grid(row=row, column=0, columnspan=3, 
                             sticky="ew", padx=5, pady=5)
        self.engine_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.engine_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.extract_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # 配置引擎框架的列权重
        self.engine_frame.columnconfigure(1, weight=1)
        row += 1
        
        self.json_cn_selector.grid(row=row, column=0, columnspan=3, 
                                 sticky="ew", padx=5, pady=5)
        row += 1
        
        self.script_cn_selector.grid(row=row, column=0, columnspan=3, 
                                   sticky="ew", padx=5, pady=5)
        row += 1
        
        # 注入选项布局
        self.inject_options_frame.grid(row=row, column=0, columnspan=3, 
                                     sticky="ew", padx=5, pady=5)
        
        # GBK编码选项
        self.gbk_encoding_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # 注入按钮
        self.inject_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # SJIS替换选项
        self.sjis_replace_frame.grid(row=1, column=0, columnspan=3, 
                                   sticky="ew", padx=5, pady=5)
        self.sjis_replace_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sjis_char_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.sjis_char_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 配置注入选项框架的列权重
        self.inject_options_frame.columnconfigure(1, weight=1)
        self.sjis_replace_frame.columnconfigure(1, weight=1)
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
        
        self.gbk_encoding_var.set(self.config.gbk_encoding)
        self.sjis_replace_var.set(self.config.sjis_replacement)
        self._toggle_sjis_options()
    
    def _save_config(self):
        """保存界面值到配置"""
        self.config.script_jp_folder = self.script_jp_selector.get_path()
        self.config.json_jp_folder = self.json_jp_selector.get_path()
        self.config.json_cn_folder = self.json_cn_selector.get_path()
        self.config.script_cn_folder = self.script_cn_selector.get_path()
        
        self.config.gbk_encoding = self.gbk_encoding_var.get()
        self.config.sjis_replacement = self.sjis_replace_var.get()
        
        #self.config.save_config()
    
    def _extract_text(self):
        """提取文本"""
        if self._is_processing:
            return
        
        # 获取参数
        script_folder = self.script_jp_selector.get_path()
        json_folder = self.json_jp_selector.get_path()
        engine = self.engine_var.get()
        
        # 验证参数
        if not script_folder:
            messagebox.showerror("错误", "请选择日文脚本目录")
            return
        
        if not json_folder:
            messagebox.showerror("错误", "请选择日文JSON保存目录")
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
                result = self.processor.extract_text(
                    script_folder, json_folder, 
                    engine if engine != "自动判断" else None,
                    output_callback
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
        json_folder = self.json_cn_selector.get_path()
        output_folder = self.script_cn_selector.get_path()
        engine = self.engine_var.get()
        use_gbk = self.gbk_encoding_var.get()
        sjis_replacement = self.sjis_replace_var.get()
        sjis_chars = self.sjis_char_var.get()
        
        # 验证参数
        if not script_folder:
            messagebox.showerror("错误", "请选择日文脚本目录")
            return
        
        if not json_folder:
            messagebox.showerror("错误", "请选择译文JSON目录")
            return
        
        if not output_folder:
            messagebox.showerror("错误", "请选择译文脚本保存目录")
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
                result = self.processor.inject_text(
                    script_folder, json_folder, output_folder,
                    engine if engine != "自动判断" else None,
                    use_gbk, sjis_replacement, sjis_chars,
                    output_callback
                )
                
                # 在主线程中更新界面
                self.frame.after(0, lambda: self._on_inject_complete(result))
            except Exception as e:
                self.frame.after(0, lambda: self._on_operation_error(str(e)))
        
        thread = threading.Thread(target=inject_worker, daemon=True)
        thread.start()
    
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
            
            # 显示SJIS扩展信息
            if result.sjis_ext_content:
                self.output_display.add_info_text(
                    f"sjis_ext.bin包含文字：{result.sjis_ext_content}"
                )
            
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
            self.processor.cancel_current_operation()
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
        
        # 取消按钮状态相反
        cancel_state = "normal" if processing else "disabled"
        self.cancel_button.config(state=cancel_state)
        
        # 显示/隐藏进度条
        if processing:
            self.output_display.show_progress(True)
            self.output_display.update_progress(0, status_text)
        else:
            self.output_display.show_progress(False)
    
    def check_vntextpatch_status(self):
        """检查VNTextPatch工具状态"""
        result = self.processor.check_vntextpatch_availability()
        
        if result.success:
            self.output_display.add_success_text(result.message)
        else:
            self.output_display.add_error_text(result.message)
        
        return result.success
    
    def get_current_paths(self) -> dict:
        """获取当前所有路径"""
        return {
            "script_jp_folder": self.script_jp_selector.get_path(),
            "json_jp_folder": self.json_jp_selector.get_path(),
            "json_cn_folder": self.json_cn_selector.get_path(),
            "script_cn_folder": self.script_cn_selector.get_path(),
            "engine": self.engine_var.get()
        }
    
    def set_paths(self, paths: dict):
        """设置路径"""
        if "script_jp_folder" in paths:
            self.script_jp_selector.set_path(paths["script_jp_folder"])
        if "json_jp_folder" in paths:
            self.json_jp_selector.set_path(paths["json_jp_folder"])
        if "json_cn_folder" in paths:
            self.json_cn_selector.set_path(paths["json_cn_folder"])
        if "script_cn_folder" in paths:
            self.script_cn_selector.set_path(paths["script_cn_folder"])
        if "engine" in paths:
            self.engine_var.set(paths["engine"])
    
    def cleanup(self):
        """清理资源"""
        if self._is_processing:
            self._cancel_operation()
        
        self.output_display.stop_output_monitoring()
        self._save_config()