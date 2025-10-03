"""
主窗口控制器
管理主窗口布局和标签页切换
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
from ttkbootstrap import Style

from .vntext_tab import VNTextTab
from .regex_tab import RegexTab
from .msgtool_tab import MsgToolTab
from ..models.config import Config
from .. import __version__


class MainWindow:
    """主窗口控制器"""
    
    def __init__(self):
        """初始化主窗口"""
        # 初始化配置
        self.config = Config()
        
        # 初始化ttkbootstrap主题
        self._setup_theme()
        
        # 创建主窗口
        self.root = self.style.master
        self._setup_window()
        
        # 创建标签页
        self._create_notebook()
        self._create_tabs()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _setup_theme(self):
        """设置主题"""
        self.style = Style()
        
        # 从配置获取主题，如果是auto则随机选择
        theme = self.config.theme
        if theme == "auto":
            theme = self._get_random_theme()
        
        try:
            self.style.theme_use(theme)
        except Exception:
            # 如果主题不存在，使用默认主题
            self.style.theme_use("cosmo")
    
    def _get_random_theme(self) -> str:
        """获取随机主题"""
        themes = [
            "cosmo", "flatly", "litera", "minty", "lumen",
            "sandstone", "yeti", "pulse", "united", "journal"
        ]
        return random.choice(themes)
    
    def _setup_window(self):
        """设置窗口属性"""
        self.root.title(f"GalTransl 提取注入工具v{__version__} by cx2333")
        
        # 从配置获取窗口大小
        window_size = self.config.window_size
        try:
            width, height = map(int, window_size.split('x'))
        except:
            width, height = 584, 659
        
        # 计算窗口位置（居中）
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.config(padx=20, pady=20)
        
        # 设置最小窗口大小
        self.root.minsize(500, 600)
    
    def _create_notebook(self):
        """创建标签页容器"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_tabs(self):
        """创建标签页"""
        # VNTextPatch模式标签页
        self.vntext_tab = VNTextTab(self.notebook, self.config)
        
        # msg-tool模式标签页
        self.msgtool_tab = MsgToolTab(self.notebook, self.config)
        
        # 正则表达式模式标签页
        self.regex_tab = RegexTab(self.notebook, self.config)
        
        # 存储标签页引用
        self.tabs = {
            "vntext": self.vntext_tab,
            "msgtool": self.msgtool_tab,
            "regex": self.regex_tab
        }
    
    def _on_tab_changed(self, event):
        """标签页切换事件处理"""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # 可以在这里添加标签页切换时的逻辑
        # 例如刷新当前标签页的状态等
        pass
    
    def _on_window_close(self):
        """窗口关闭事件处理"""
        try:
            # 保存当前窗口大小到配置
            geometry = self.root.geometry()
            size_part = geometry.split('+')[0]  # 提取尺寸部分
            self.config.window_size = size_part
            # 保存配置
            self.config.save_config()
            # # 清理标签页资源
            # for tab in self.tabs.values():
            #     if hasattr(tab, 'cleanup'):
            #         tab.cleanup()
            

            
        except Exception as e:
            print(f"保存配置时出错: {e}")
        finally:
            # 销毁窗口
            self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        # 检查VNTextPatch工具状态
        self._check_vntextpatch_status()
        
        # 检查msg-tool工具状态
        self._check_msgtool_status()
        
        # 启动主循环
        self.root.mainloop()
    
    def _check_vntextpatch_status(self):
        """检查VNTextPatch工具状态"""
        try:
            # 检查VNTextPatch工具是否可用
            if hasattr(self.vntext_tab, 'check_vntextpatch_status'):
                self.vntext_tab.check_vntextpatch_status()
        except Exception as e:
            print(f"检查VNTextPatch状态时出错: {e}")
    
    def _check_msgtool_status(self):
        """检查msg-tool工具状态"""
        try:
            # 检查msg-tool工具是否可用
            if hasattr(self.msgtool_tab, 'check_msgtool_status'):
                self.msgtool_tab.check_msgtool_status()
        except Exception as e:
            print(f"检查msg-tool状态时出错: {e}")
    
    def get_current_tab(self) -> str:
        """获取当前活动的标签页"""
        try:
            selected_tab = self.notebook.select()
            tab_text = self.notebook.tab(selected_tab, "text")
            
            if "VNTextPatch" in tab_text:
                return "vntext"
            elif "msg-tool" in tab_text:
                return "msgtool"
            elif "正则表达式" in tab_text:
                return "regex"
            else:
                return "unknown"
        except:
            return "unknown"
    
    def switch_to_tab(self, tab_name: str):
        """切换到指定标签页"""
        tab_map = {
            "vntext": 0,
            "msgtool": 1,
            "regex": 2
        }
        
        if tab_name in tab_map:
            self.notebook.select(tab_map[tab_name])
    
    def show_about_dialog(self):
        """显示关于对话框"""
        about_text = f"""GalTransl 提取注入工具 v{__version__}
        
作者: cx2333

这是一个用于游戏翻译文本提取和注入的工具，支持：
• VNTextPatch模式 - 使用VNTextPatch工具进行提取和注入
• msg-tool模式 - 使用msg-tool工具支持更多游戏引擎
• 正则表达式模式 - 使用自定义正则表达式进行处理
• SJIS字符替换 - 支持汉字到日文汉字的映射替换
• 多种编码支持 - 支持UTF-8、GBK、SJIS等编码

重构版本特性：
• 模块化架构，提高代码可维护性
• 分离GUI逻辑与业务逻辑
• 完善的错误处理和用户反馈
• 配置管理和状态保存
"""
        
        messagebox.showinfo("关于", about_text)
    
    def show_help_dialog(self):
        """显示帮助对话框"""
        help_text = """使用帮助：

VNTextPatch模式：
1. 选择日文脚本文件夹和JSON保存文件夹
2. 选择引擎（或保持自动判断）
3. 点击“提取脚本到JSON”
4. 翻译JSON文件
5. 选择译文JSON文件夹和输出文件夹
6. 根据需要启用GBK编码或SJIS替换模式
7. 点击“注入JSON回脚本”

msg-tool模式：
1. 选择日文脚本文件夹和JSON保存文件夹
2. 选择引擎（或保持自动检测）
3. 点击“提取脚本到JSON”
4. 翻译JSON文件
5. 选择译文JSON文件夹和输出文件夹
6. 根据需要启用GBK编码或SJIS替换模式
7. 点击“注入JSON回脚本”

正则表达式模式：
1. 选择日文脚本文件夹和JSON保存文件夹
2. 输入正文提取和人名提取的正则表达式
3. 选择日文脚本编码
4. 点击“提取脚本到JSON”
5. 翻译JSON文件
6. 选择译文JSON文件夹和输出文件夹
7. 选择中文脚本编码
8. 根据需要启用SJIS替换模式
9. 点击“注入JSON回脚本”

提示：
• 正则表达式必须包含捕获组 () 来提取内容
• 建议先用“测试正则表达式”功能验证正则
• SJIS替换模式适用于需要汉字映射的场景
• msg-tool支持更多游戏引擎，包括Artemis、BGI、CatSystem2等
"""
        
        messagebox.showinfo("帮助", help_text)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self._on_window_close)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="检查VNTextPatch状态", 
                              command=self._check_vntextpatch_status)
        tools_menu.add_command(label="检查msg-tool状态", 
                              command=self._check_msgtool_status)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用帮助", command=self.show_help_dialog)
        help_menu.add_command(label="关于", command=self.show_about_dialog)
    
    def set_theme(self, theme_name: str):
        """设置主题"""
        try:
            self.style.theme_use(theme_name)
            self.config.theme = theme_name
            self.config.save_config()
            messagebox.showinfo("主题", f"主题已切换为: {theme_name}")
        except Exception as e:
            messagebox.showerror("错误", f"切换主题失败: {str(e)}")
    
    def get_available_themes(self) -> list:
        """获取可用主题列表"""
        return self.style.theme_names()
    
    def export_config(self, file_path: str):
        """导出配置"""
        try:
            import shutil
            shutil.copy(self.config.user_config_path, file_path)
            messagebox.showinfo("导出", "配置导出成功")
        except Exception as e:
            messagebox.showerror("错误", f"导出配置失败: {str(e)}")
    
    def import_config(self, file_path: str):
        """导入配置"""
        try:
            import shutil
            shutil.copy(file_path, self.config.user_config_path)
            self.config._load_config()  # 重新加载配置
            messagebox.showinfo("导入", "配置导入成功，请重启应用以应用新配置")
        except Exception as e:
            messagebox.showerror("错误", f"导入配置失败: {str(e)}")