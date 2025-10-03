"""
Msg-tool模式标签页
Msg-tool模式的用户界面逻辑
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from typing import Optional

from .widgets.file_selector import FileSelector
from .widgets.output_display import RealTimeOutputDisplay
from ..core.msgtool_processor import MsgToolProcessor
from ..models.config import Config


class MsgToolTab:
    """Msg-tool模式标签页"""
    
    def __init__(self, parent: ttk.Notebook, config: Config):
        """
        Args:
            parent: 父级Notebook组件
            config: 配置管理器
        """
        self.parent = parent
        self.config = config
        self.processor = MsgToolProcessor()
        
        # 创建标签页
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="msg-tool模式")
        
        # 当前操作状态
        self._is_processing = False
        
        # 创建界面
        self._create_widgets()
        self._setup_layout()
        self._load_config()
    
    def _create_widgets(self):
        """创建界面组件"""
        # msg-tool介绍
        self.intro_frame = ttk.Frame(self.frame)
        self.intro_label = ttk.Label(
            self.intro_frame,
            text="msg-tool是一个强大的多引擎脚本处理工具，作者lifegpc",
            foreground="blue",
            cursor="hand2",
            wraplength=800
        )
        
        # 绑定点击事件打开链接
        self.intro_label.bind("<Button-1>", self._open_msgtool_link)
        
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
        self.engine_var = tk.StringVar(value="自动检测")
        self.engine_combo = ttk.Combobox(
            self.engine_frame,
            textvariable=self.engine_var,
            values=self.processor.get_supported_engines(),
            state="readonly",
            width=30
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
            text="GBK编码注入 (--encoding cp932)",
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
        
        # 工具状态标签
        self.tool_status_label = ttk.Label(
            self.status_frame,
            text="",
            foreground="gray"
        )
    
    def _setup_layout(self):
        """设置布局"""
        row = 0
        
        # msg-tool介绍布局
        self.intro_frame.grid(row=row, column=0, columnspan=3, 
                             sticky="ew", padx=5, pady=5)
        self.intro_label.pack(pady=5)
        row += 1
        
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
        self.gbk_encoding_check.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # SJIS替换选项
        self.sjis_replace_frame.grid(row=1, column=0, columnspan=3, 
                                   sticky="ew", padx=5, pady=2)
        self.sjis_replace_check.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.sjis_char_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.sjis_char_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        
        # 注入按钮
        self.inject_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        row += 1
        
        # 输出显示
        self.output_display.grid(row=row, column=0, columnspan=3, 
                               sticky="ew", padx=5, pady=5)
        row += 1
        
        # 状态栏
        self.status_frame.grid(row=row, column=0, columnspan=3, 
                             sticky="ew", padx=5, pady=5)
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cancel_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.tool_status_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # 配置状态框架的列权重
        self.status_frame.columnconfigure(0, weight=1)
        
        # 配置主框架的列权重
        self.frame.columnconfigure(0, weight=1)
    
    def _open_msgtool_link(self, event):
        """打开msg-tool链接"""
        try:
            webbrowser.open("https://github.com/msg-tool/msg-tool")
        except Exception:
            pass
    
    def _toggle_sjis_options(self):
        """切换SJIS选项状态"""
        if self.sjis_replace_var.get():
            self.sjis_char_entry.config(state="normal")
        else:
            self.sjis_char_entry.config(state="disabled")
    
    def _load_config(self):
        """加载配置"""
        try:
            # 加载路径配置
            self.script_jp_selector.set_path(self.config.msgtool_script_jp_folder)
            self.json_jp_selector.set_path(self.config.msgtool_json_jp_folder)
            self.json_cn_selector.set_path(self.config.msgtool_json_cn_folder)
            self.script_cn_selector.set_path(self.config.msgtool_script_cn_folder)
            
            # 加载引擎选择
            self.engine_var.set(self.config.msgtool_selected_engine)
            
            # 加载选项配置
            self.gbk_encoding_var.set(self.config.msgtool_use_gbk_encoding)
            self.sjis_replace_var.set(self.config.msgtool_sjis_replacement)
            self.sjis_char_var.set(self.config.msgtool_sjis_chars)
            
            # 更新SJIS选项状态
            self._toggle_sjis_options()
            
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def _save_config(self):
        """保存配置"""
        try:
            # 保存路径配置
            self.config.msgtool_script_jp_folder = self.script_jp_selector.get_path()
            self.config.msgtool_json_jp_folder = self.json_jp_selector.get_path()
            self.config.msgtool_json_cn_folder = self.json_cn_selector.get_path()
            self.config.msgtool_script_cn_folder = self.script_cn_selector.get_path()
            
            # 保存引擎选择
            self.config.msgtool_selected_engine = self.engine_var.get()
            
            # 保存选项配置
            self.config.msgtool_use_gbk_encoding = self.gbk_encoding_var.get()
            self.config.msgtool_sjis_replacement = self.sjis_replace_var.get()
            self.config.msgtool_sjis_chars = self.sjis_char_var.get()
            
            # 保存配置文件
            self.config.save_config()
            
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def _set_processing_state(self, is_processing: bool):
        """设置处理状态"""
        self._is_processing = is_processing
        
        # 禁用/启用按钮
        state = "disabled" if is_processing else "normal"
        self.extract_button.config(state=state)
        self.inject_button.config(state=state)
        
        # 取消按钮状态
        cancel_state = "normal" if is_processing else "disabled"
        self.cancel_button.config(state=cancel_state)
    
    def _extract_text(self):
        """提取文本到JSON"""
        if self._is_processing:
            return
        
        try:
            # 获取参数
            script_folder = self.script_jp_selector.get_path()
            json_folder = self.json_jp_selector.get_path()
            engine = self.engine_var.get()
            
            if not script_folder or not json_folder:
                messagebox.showerror("错误", "请选择脚本文件夹和JSON保存文件夹")
                return
            
            # 设置处理状态
            self._set_processing_state(True)
            self.status_var.set("正在提取文本...")
            self.output_display.clear()
            
            def on_completion(result):
                """异步完成回调"""
                # 使用after方法在主线程中更新GUI
                self.frame.after(0, self._handle_extract_completion, result)
            
            # 异步执行提取
            self.processor.extract_text_async(
                script_folder,
                json_folder,
                engine if engine != "自动检测" else None,
                self.output_display.append_line,  # 使用append_line确保换行
                on_completion
            )
            
        except Exception as e:
            self.status_var.set("提取异常")
            error_msg = f"提取过程异常: {str(e)}"
            self.output_display.append_text(f"\n✗ {error_msg}")
            messagebox.showerror("异常", error_msg)
            self._set_processing_state(False)
    
    def _handle_extract_completion(self, result):
        """处理提取完成结果"""
        try:
            # 显示结果
            if result.success:
                self.status_var.set("提取完成")
                self.output_display.append_text(f"\n✓ {result.message}")
                messagebox.showinfo("成功", result.message)
                self._save_config()
            else:
                self.status_var.set("提取失败")
                self.output_display.append_text(f"\n✗ {result.message}")
                messagebox.showerror("错误", result.message)
        
        except Exception as e:
            self.status_var.set("提取异常")
            error_msg = f"处理结果异常: {str(e)}"
            self.output_display.append_text(f"\n✗ {error_msg}")
            messagebox.showerror("异常", error_msg)
        
        finally:
            self._set_processing_state(False)
    
    def _inject_text(self):
        """注入JSON回脚本"""
        if self._is_processing:
            return
        
        try:
            # 获取参数
            script_folder = self.script_jp_selector.get_path()
            json_folder = self.json_cn_selector.get_path()
            output_folder = self.script_cn_selector.get_path()
            engine = self.engine_var.get()
            use_gbk = self.gbk_encoding_var.get()
            sjis_replacement = self.sjis_replace_var.get()
            sjis_chars = self.sjis_char_var.get()
            
            if not script_folder or not json_folder or not output_folder:
                messagebox.showerror("错误", "请选择所有必需的文件夹")
                return
            
            # 设置处理状态
            self._set_processing_state(True)
            self.status_var.set("正在注入文本...")
            self.output_display.clear()
            
            def on_completion(result):
                """异步完成回调"""
                # 使用after方法在主线程中更新GUI
                self.frame.after(0, self._handle_inject_completion, result)
            
            # 异步执行注入
            self.processor.inject_text_async(
                script_folder,
                json_folder,
                output_folder,
                engine if engine != "自动检测" else None,
                use_gbk,
                sjis_replacement,
                sjis_chars,
                self.output_display.append_line,  # 使用append_line确保换行
                on_completion
            )
            
        except Exception as e:
            self.status_var.set("注入异常")
            error_msg = f"注入过程异常: {str(e)}"
            self.output_display.append_text(f"\n✗ {error_msg}")
            messagebox.showerror("异常", error_msg)
            self._set_processing_state(False)
    
    def _handle_inject_completion(self, result):
        """处理注入完成结果"""
        try:
            # 显示结果
            if result.success:
                self.status_var.set("注入完成")
                self.output_display.append_text(f"\n✓ {result.message}")
                
                # 显示详细结果
                success_msg = result.message
                if result.sjis_config:
                    success_msg += f"\n\nSJIS替换配置:\n{result.sjis_config}"
                
                messagebox.showinfo("成功", success_msg)
                self._save_config()
            else:
                self.status_var.set("注入失败")
                self.output_display.append_text(f"\n✗ {result.message}")
                messagebox.showerror("错误", result.message)
        
        except Exception as e:
            self.status_var.set("注入异常")
            error_msg = f"处理结果异常: {str(e)}"
            self.output_display.append_text(f"\n✗ {error_msg}")
            messagebox.showerror("异常", error_msg)
        
        finally:
            self._set_processing_state(False)
    
    def _cancel_operation(self):
        """取消当前操作"""
        if self._is_processing:
            try:
                self.processor.cancel_current_task()
                self.status_var.set("操作已取消")
                self.output_display.append_text("\n⚠ 操作被用户取消")
            except Exception as e:
                print(f"取消操作失败: {e}")
            finally:
                self._set_processing_state(False)
    
    def check_msgtool_status(self):
        """检查msg-tool工具状态"""
        try:
            tool_info = self.processor.get_tool_info()
            
            if tool_info["available"]:
                status_text = f"msg-tool可用 - {tool_info['version']}"
                self.tool_status_label.config(text=status_text, foreground="green")
                self.output_display.append_text(f"✓ {status_text}")
            else:
                status_text = "msg-tool不可用"
                self.tool_status_label.config(text=status_text, foreground="red")
                self.output_display.append_text(f"✗ {status_text}")
                self.output_display.append_text("请确保msg-tool.exe位于项目目录中")
        
        except Exception as e:
            error_text = f"检查工具状态失败: {str(e)}"
            self.tool_status_label.config(text="状态检查失败", foreground="red")
            self.output_display.append_text(f"✗ {error_text}")
    
    def cleanup(self):
        """清理资源"""
        if self._is_processing:
            self._cancel_operation()