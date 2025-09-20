#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShiningHunter - DeSmuME多开宝可梦闪光刷取辅助工具
主程序入口
"""

import sys
import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path

# 导入自定义模块
from modules.keyboard_controller import KeyboardController
from modules.screenshot_manager import ScreenshotManager
from modules.image_analyzer import ImageAnalyzer
from modules.auto_hunter import AutoHunter
from modules.gui_interface import MainGUI

class ShiningHunter:
    """主应用程序类"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个模块
        self.keyboard_controller = KeyboardController()
        self.screenshot_manager = ScreenshotManager()
        self.image_analyzer = ImageAnalyzer()
        self.auto_hunter = AutoHunter(
            self.keyboard_controller,
            self.screenshot_manager,
            self.image_analyzer
        )
        
        # 初始化GUI
        self.root = tk.Tk()
        self.gui = MainGUI(self.root, self)
        
        self.logger.info("ShiningHunter 初始化完成")
    
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "shininghunter.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run(self):
        """运行主程序"""
        try:
            self.logger.info("启动 ShiningHunter")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("用户中断程序")
        except Exception as e:
            self.logger.error(f"程序运行出错: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("清理资源...")
        # 停止自动刷闪
        if hasattr(self, 'auto_hunter'):
            self.auto_hunter.stop_hunting()
        pass

if __name__ == "__main__":
    app = ShiningHunter()
    app.run()
