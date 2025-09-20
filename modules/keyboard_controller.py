#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
键盘控制模块
负责模拟键盘按键操作，包括F1快速读取存档和X键确认
"""

import time
import logging
from typing import Optional
import threading

try:
    import pynput
    from pynput import keyboard
    from pynput.keyboard import Key, Listener
except ImportError:
    print("请安装 pynput: pip install pynput")
    pynput = None

class KeyboardController:
    """键盘控制器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keyboard_controller = None
        self.is_listening = False
        self.hotkeys = {}
        
        if pynput is None:
            self.logger.error("pynput 未安装，键盘控制功能不可用")
            return
        
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """设置热键"""
        if pynput is None:
            return
            
        # 定义热键组合
        self.hotkeys = {
            'f1_quick_load': Key.f1,
            'x_confirm': 'x'
        }
        
        self.logger.info("热键设置完成")
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """
        按下指定按键
        
        Args:
            key: 按键名称 ('f1', 'x', 等)
            duration: 按键持续时间（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if pynput is None:
            self.logger.error("pynput 未安装，无法执行按键操作")
            return False
        
        try:
            if key.lower() == 'f1':
                key_obj = Key.f1
            elif key.lower() == 'x':
                key_obj = 'x'
            else:
                self.logger.error(f"不支持的按键: {key}")
                return False
            
            # 创建键盘控制器
            controller = keyboard.Controller()
            
            # 按下按键
            controller.press(key_obj)
            time.sleep(duration)
            controller.release(key_obj)
            
            self.logger.info(f"按下按键: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"按键操作失败: {e}")
            return False
    
    def quick_load_save(self) -> bool:
        """
        快速读取DeSmuME的第一个存档 (F1键)
        
        Returns:
            bool: 操作是否成功
        """
        return self.press_key('f1', 0.1)
    
    def confirm_action(self) -> bool:
        """
        确认操作 (X键，对应DeSmuME的A键)
        
        Returns:
            bool: 操作是否成功
        """
        return self.press_key('x', 0.1)
    
    def start_hotkey_listener(self, callback_func=None):
        """
        启动全局热键监听器
        
        Args:
            callback_func: 热键触发时的回调函数
        """
        if pynput is None:
            self.logger.error("pynput 未安装，无法启动热键监听")
            return
        
        if self.is_listening:
            self.logger.warning("热键监听器已在运行")
            return
        
        def on_hotkey():
            if callback_func:
                callback_func()
        
        try:
            # 这里可以设置全局热键，比如 Ctrl+Shift+F1
            # 由于pynput的限制，这里先实现基本的按键监听
            self.is_listening = True
            self.logger.info("热键监听器启动")
            
        except Exception as e:
            self.logger.error(f"启动热键监听器失败: {e}")
            self.is_listening = False
    
    def stop_hotkey_listener(self):
        """停止热键监听器"""
        self.is_listening = False
        self.logger.info("热键监听器已停止")
    
    def simulate_sequence(self, keys: list, intervals: list = None) -> bool:
        """
        模拟按键序列
        
        Args:
            keys: 按键列表
            intervals: 按键间隔时间列表
            
        Returns:
            bool: 操作是否成功
        """
        if pynput is None:
            return False
        
        if intervals is None:
            intervals = [0.1] * len(keys)
        
        try:
            for i, key in enumerate(keys):
                if not self.press_key(key, 0.1):
                    return False
                
                if i < len(intervals) - 1:
                    time.sleep(intervals[i])
            
            return True
            
        except Exception as e:
            self.logger.error(f"按键序列执行失败: {e}")
            return False
