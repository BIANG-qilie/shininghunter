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
        self.custom_keys = {
            'reset': 'ctrl+r',  # 重置键，默认Ctrl+R
            'confirm': 'x',  # 确认键，默认X
            'quick_load': 'f1'  # 快速读取键，默认F1
        }
        
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
    
    def set_custom_key(self, action: str, key: str) -> bool:
        """
        设置自定义键位
        
        Args:
            action: 动作名称 ('reset', 'confirm', 'quick_load')
            key: 按键名称
            
        Returns:
            bool: 设置是否成功
        """
        if action in self.custom_keys:
            self.custom_keys[action] = key.lower()
            self.logger.info(f"设置 {action} 键为: {key}")
            return True
        else:
            self.logger.error(f"不支持的动作: {action}")
            return False
    
    def get_custom_key(self, action: str) -> str:
        """
        获取自定义键位
        
        Args:
            action: 动作名称
            
        Returns:
            str: 按键名称
        """
        return self.custom_keys.get(action, '')
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """
        按下指定按键
        
        Args:
            key: 按键名称 ('f1', 'x', 'r', 'ctrl+r', 等)
            duration: 按键持续时间（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if pynput is None:
            self.logger.error("pynput 未安装，无法执行按键操作")
            return False
        
        try:
            # 检查是否是组合键
            if '+' in key.lower():
                return self._press_combo_key(key, duration)
            
            key_lower = key.lower()
            if key_lower == 'f1':
                key_obj = Key.f1
            elif key_lower == 'f2':
                key_obj = Key.f2
            elif key_lower == 'f3':
                key_obj = Key.f3
            elif key_lower == 'f4':
                key_obj = Key.f4
            elif key_lower == 'f5':
                key_obj = Key.f5
            elif key_lower == 'f6':
                key_obj = Key.f6
            elif key_lower == 'f7':
                key_obj = Key.f7
            elif key_lower == 'f8':
                key_obj = Key.f8
            elif key_lower == 'f9':
                key_obj = Key.f9
            elif key_lower == 'f10':
                key_obj = Key.f10
            elif key_lower == 'f11':
                key_obj = Key.f11
            elif key_lower == 'f12':
                key_obj = Key.f12
            elif len(key_lower) == 1 and key_lower.isalpha():
                key_obj = key_lower
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
    
    def _press_combo_key(self, combo_key: str, duration: float = 0.1) -> bool:
        """
        按下组合键
        
        Args:
            combo_key: 组合键名称 ('ctrl+r', 'alt+f4', 等)
            duration: 按键持续时间（秒）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            parts = combo_key.lower().split('+')
            if len(parts) != 2:
                self.logger.error(f"不支持的组合键格式: {combo_key}")
                return False
            
            modifier = parts[0].strip()
            key = parts[1].strip()
            
            # 解析修饰键
            if modifier == 'ctrl':
                modifier_obj = Key.ctrl
            elif modifier == 'alt':
                modifier_obj = Key.alt
            elif modifier == 'shift':
                modifier_obj = Key.shift
            else:
                self.logger.error(f"不支持的修饰键: {modifier}")
                return False
            
            # 解析主键
            if key == 'f1':
                key_obj = Key.f1
            elif key == 'f2':
                key_obj = Key.f2
            elif key == 'f3':
                key_obj = Key.f3
            elif key == 'f4':
                key_obj = Key.f4
            elif key == 'f5':
                key_obj = Key.f5
            elif key == 'f6':
                key_obj = Key.f6
            elif key == 'f7':
                key_obj = Key.f7
            elif key == 'f8':
                key_obj = Key.f8
            elif key == 'f9':
                key_obj = Key.f9
            elif key == 'f10':
                key_obj = Key.f10
            elif key == 'f11':
                key_obj = Key.f11
            elif key == 'f12':
                key_obj = Key.f12
            elif len(key) == 1 and key.isalpha():
                key_obj = key
            else:
                self.logger.error(f"不支持的按键: {key}")
                return False
            
            # 创建键盘控制器
            controller = keyboard.Controller()
            
            # 按下组合键
            controller.press(modifier_obj)
            controller.press(key_obj)
            time.sleep(duration)
            controller.release(key_obj)
            controller.release(modifier_obj)
            
            self.logger.info(f"按下组合键: {combo_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"组合键操作失败: {e}")
            return False
    
    def quick_load_save(self) -> bool:
        """
        快速读取DeSmuME的第一个存档
        
        Returns:
            bool: 操作是否成功
        """
        key = self.get_custom_key('quick_load')
        return self.press_key(key, 0.1)
    
    def confirm_action(self) -> bool:
        """
        确认操作 (对应DeSmuME的A键)
        
        Returns:
            bool: 操作是否成功
        """
        key = self.get_custom_key('confirm')
        return self.press_key(key, 0.1)
    
    def reset_action(self) -> bool:
        """
        重置操作
        
        Returns:
            bool: 操作是否成功
        """
        key = self.get_custom_key('reset')
        return self.press_key(key, 0.1)
    
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
