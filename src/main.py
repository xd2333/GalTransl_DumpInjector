"""
GalTransl DumpInjector 应用入口点
重构版本 - 模块化的游戏翻译文本提取和注入工具
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.gui.main_window import MainWindow
    from src import __version__
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖都已正确安装")
    sys.exit(1)


def setup_logging():
    """设置日志记录"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_dependencies():
    """检查依赖"""
    try:
        import tkinter
        import ttkbootstrap
        import chardet
        return True
    except ImportError as e:
        print(f"缺少必要的依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def main():
    """主函数"""
    print(f"GalTransl DumpInjector v{__version__} - 重构版本")
    print("正在启动应用程序...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 创建并运行主窗口
        logger.info("启动主窗口...")
        app = MainWindow()
        
        # 添加菜单栏
        app.create_menu_bar()
        
        logger.info("应用程序启动成功")
        app.run()
        
    except Exception as e:
        logger.error(f"应用程序运行时出现错误: {e}", exc_info=True)
        print(f"错误: {e}")
        sys.exit(1)
    
    finally:
        logger.info("应用程序已退出")


if __name__ == "__main__":
    main()