"""
文件选择器组件
可复用的文件/文件夹选择界面组件
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, Callable


class FileSelector:
    """文件选择器组件"""
    
    def __init__(
        self,
        parent: tk.Widget,
        label_text: str,
        width: int = 50,
        selection_type: str = "folder",  # "folder", "file"
        file_types: Optional[list] = None
    ):
        """
        Args:
            parent: 父组件
            label_text: 标签文本
            width: 输入框宽度
            selection_type: 选择类型 ("folder" 或 "file")
            file_types: 文件类型过滤器 (仅在selection_type="file"时使用)
        """
        self.parent = parent
        self.label_text = label_text
        self.width = width
        self.selection_type = selection_type
        self.file_types = file_types or [("所有文件", "*.*")]
        
        # 回调函数
        self.on_path_changed: Optional[Callable[[str], None]] = None
        
        # 创建组件
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        self.frame = ttk.Frame(self.parent)
        
        # 标签
        self.label = ttk.Label(self.frame, text=self.label_text)
        
        # 路径输入框
        self.path_var = tk.StringVar()
        self.path_var.trace_add('write', self._on_path_var_changed)
        self.entry = ttk.Entry(
            self.frame, 
            textvariable=self.path_var,
            width=self.width
        )
        
        # 浏览按钮
        self.browse_button = ttk.Button(
            self.frame,
            text="浏览",
            command=self._browse_path
        )
    
    def grid(self, row: int, column: int = 0, **kwargs):
        """网格布局"""
        self.frame.grid(row=row, column=column, **kwargs)
        
        # 布局内部组件
        self.label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="e")
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # 配置列权重
        self.frame.columnconfigure(1, weight=1)
    
    def pack(self, **kwargs):
        """包装布局"""
        self.frame.pack(**kwargs)
        
        # 布局内部组件
        self.label.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        self.entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.browse_button.pack(side=tk.LEFT, padx=(5, 0), pady=5)
    
    def _browse_path(self):
        """浏览路径"""
        if self.selection_type == "folder":
            path = filedialog.askdirectory()
        else:  # file
            path = filedialog.askopenfilename(filetypes=self.file_types)
        
        if path:
            self.set_path(path)
    
    def _on_path_var_changed(self, *args):
        """路径变量变化回调"""
        if self.on_path_changed:
            self.on_path_changed(self.get_path())
    
    def get_path(self) -> str:
        """获取当前路径"""
        return self.path_var.get()
    
    def set_path(self, path: str):
        """设置路径"""
        self.path_var.set(path)
    
    def clear_path(self):
        """清空路径"""
        self.path_var.set("")
    
    def set_enabled(self, enabled: bool):
        """设置启用状态"""
        state = "normal" if enabled else "disabled"
        self.entry.config(state=state)
        self.browse_button.config(state=state)
    
    def set_label_text(self, text: str):
        """设置标签文本"""
        self.label.config(text=text)
    
    def bind_path_changed(self, callback: Callable[[str], None]):
        """绑定路径变化回调"""
        self.on_path_changed = callback


class MultiFileSelector:
    """多文件选择器组件"""
    
    def __init__(
        self,
        parent: tk.Widget,
        selectors_config: list,
        auto_sync: bool = True
    ):
        """
        Args:
            parent: 父组件
            selectors_config: 选择器配置列表
            auto_sync: 是否自动同步相同类型的路径
        """
        self.parent = parent
        self.auto_sync = auto_sync
        self.selectors: dict[str, FileSelector] = {}
        
        # 创建选择器
        for config in selectors_config:
            self._create_selector(config)
    
    def _create_selector(self, config: dict):
        """创建单个选择器"""
        selector_id = config["id"]
        selector = FileSelector(
            parent=self.parent,
            label_text=config["label"],
            width=config.get("width", 50),
            selection_type=config.get("type", "folder"),
            file_types=config.get("file_types")
        )
        
        # 如果启用自动同步，绑定回调
        if self.auto_sync:
            selector.bind_path_changed(
                lambda path, sid=selector_id: self._on_selector_changed(sid, path)
            )
        
        self.selectors[selector_id] = selector
    
    def _on_selector_changed(self, changed_id: str, path: str):
        """选择器变化回调"""
        # 根据需要实现自动同步逻辑
        # 这里可以根据具体需求定制同步规则
        pass
    
    def get_selector(self, selector_id: str) -> Optional[FileSelector]:
        """获取指定的选择器"""
        return self.selectors.get(selector_id)
    
    def get_path(self, selector_id: str) -> str:
        """获取指定选择器的路径"""
        selector = self.selectors.get(selector_id)
        return selector.get_path() if selector else ""
    
    def set_path(self, selector_id: str, path: str):
        """设置指定选择器的路径"""
        selector = self.selectors.get(selector_id)
        if selector:
            selector.set_path(path)
    
    def get_all_paths(self) -> dict[str, str]:
        """获取所有选择器的路径"""
        return {sid: selector.get_path() for sid, selector in self.selectors.items()}
    
    def set_all_paths(self, paths: dict[str, str]):
        """设置所有选择器的路径"""
        for selector_id, path in paths.items():
            self.set_path(selector_id, path)
    
    def clear_all_paths(self):
        """清空所有路径"""
        for selector in self.selectors.values():
            selector.clear_path()
    
    def grid_all(self, start_row: int = 0, **kwargs):
        """网格布局所有选择器"""
        for i, selector in enumerate(self.selectors.values()):
            selector.grid(row=start_row + i, **kwargs)
    
    def pack_all(self, **kwargs):
        """包装布局所有选择器"""
        for selector in self.selectors.values():
            selector.pack(**kwargs)


class PathSyncManager:
    """路径同步管理器"""
    
    def __init__(self):
        self.sync_groups: dict[str, list[FileSelector]] = {}
    
    def add_sync_group(self, group_name: str, selectors: list[FileSelector]):
        """添加同步组"""
        self.sync_groups[group_name] = selectors
        
        # 为每个选择器绑定同步回调
        for selector in selectors:
            selector.bind_path_changed(
                lambda path, group=group_name, s=selector: self._sync_group(group, s, path)
            )
    
    def _sync_group(self, group_name: str, changed_selector: FileSelector, new_path: str):
        """同步组内路径"""
        selectors = self.sync_groups.get(group_name, [])
        
        for selector in selectors:
            if selector != changed_selector:
                # 临时取消回调，避免循环触发
                old_callback = selector.on_path_changed
                selector.on_path_changed = None
                selector.set_path(new_path)
                selector.on_path_changed = old_callback
    
    def remove_sync_group(self, group_name: str):
        """移除同步组"""
        if group_name in self.sync_groups:
            # 清除选择器的回调
            for selector in self.sync_groups[group_name]:
                selector.on_path_changed = None
            
            del self.sync_groups[group_name]