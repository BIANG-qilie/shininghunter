#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动刷闪模块
实现完整的自动刷闪流程
"""

import time
import threading
import logging
from typing import List, Dict, Optional, Callable
from tkinter import messagebox

class AutoHunter:
    """自动刷闪控制器"""
    
    def __init__(self, keyboard_controller, screenshot_manager, image_analyzer):
        self.keyboard_controller = keyboard_controller
        self.screenshot_manager = screenshot_manager
        self.image_analyzer = image_analyzer
        self.logger = logging.getLogger(__name__)
        
        # 刷闪状态
        self.is_hunting = False
        self.hunt_count = 0
        self.hunt_thread = None
        
        # 回调函数
        self.on_hunt_start = None
        self.on_hunt_stop = None
        self.on_hunt_progress = None
        self.on_hunt_result = None
        self.on_countdown = None
        
        # 配置参数
        self.config = {
            'initial_delay': 5.0,      # 初始冷却时间（秒）
            'f1_delay': 0.5,           # F1后等待时间（秒）
            'first_a_delay': 0.8,      # 第一次A键后等待时间（秒）
            'analysis_delay': 4.0,     # 分析前等待时间（秒）
            'retry_count': 2,          # 分析重试次数
            'retry_interval': 2.0,     # 重试间隔时间（秒）
            'reference_image': None,   # 参考图像名称
        }
    
    def set_config(self, config: Dict):
        """设置配置参数"""
        self.config.update(config)
        self.logger.info(f"更新自动刷闪配置: {config}")
    
    def set_callbacks(self, on_hunt_start=None, on_hunt_stop=None, 
                     on_hunt_progress=None, on_hunt_result=None, on_countdown=None):
        """设置回调函数"""
        self.on_hunt_start = on_hunt_start
        self.on_hunt_stop = on_hunt_stop
        self.on_hunt_progress = on_hunt_progress
        self.on_hunt_result = on_hunt_result
        self.on_countdown = on_countdown
    
    def start_hunting(self):
        """开始自动刷闪"""
        if self.is_hunting:
            self.logger.warning("自动刷闪已在运行")
            return False
        
        # 检查必要条件
        if not self._check_requirements():
            return False
        
        # 重置计数器
        self.hunt_count = 0
        self.is_hunting = True
        
        # 启动刷闪线程
        self.hunt_thread = threading.Thread(target=self._hunt_loop, daemon=True)
        self.hunt_thread.start()
        
        self.logger.info("开始自动刷闪")
        if self.on_hunt_start:
            self.on_hunt_start()
        
        return True
    
    def stop_hunting(self):
        """停止自动刷闪"""
        if not self.is_hunting:
            self.logger.warning("自动刷闪未在运行")
            return
        
        self.is_hunting = False
        
        # 等待线程结束
        if self.hunt_thread and self.hunt_thread.is_alive():
            self.hunt_thread.join(timeout=2.0)
        
        self.logger.info(f"停止自动刷闪，总次数: {self.hunt_count}")
        if self.on_hunt_stop:
            self.on_hunt_stop(self.hunt_count)
    
    def _check_requirements(self) -> bool:
        """检查自动刷闪的必要条件"""
        # 检查截图区域
        if not self.screenshot_manager.screenshot_regions:
            messagebox.showerror("错误", "请先设置截图区域")
            return False
        
        # 检查参考图像
        if not self.image_analyzer.get_reference_list():
            messagebox.showerror("错误", "请先加载参考图像")
            return False
        
        # 检查键盘控制器
        if not self.keyboard_controller:
            messagebox.showerror("错误", "键盘控制器未初始化")
            return False
        
        return True
    
    def _hunt_loop(self):
        """自动刷闪主循环"""
        try:
            # 步骤1: 初始冷却
            self._log_progress("步骤1: 初始冷却5秒，请选择DeSmuME窗口")
            self._wait_with_cancel(self.config['initial_delay'], "开始刷闪")
            
            while self.is_hunting:
                # 步骤2: 按下F1读取存档
                self._log_progress("步骤2: 按下F1读取存档")
                if not self.keyboard_controller.quick_load_save():
                    self._handle_error("F1按键失败")
                    break
                
                self._wait_with_cancel(self.config['f1_delay'], "第一次确认")
                
                # 步骤3: 第一次按下A键
                self._log_progress("步骤3: 第一次按下A键")
                if not self.keyboard_controller.confirm_action():
                    self._handle_error("第一次A键失败")
                    break
                
                self._wait_with_cancel(self.config['first_a_delay'], "第二次确认")
                
                # 步骤4: 第二次按下A键
                self._log_progress("步骤4: 第二次按下A键")
                if not self.keyboard_controller.confirm_action():
                    self._handle_error("第二次A键失败")
                    break
                
                self._wait_with_cancel(self.config['analysis_delay'], "开始分析")
                
                # 步骤5: 区域截图分析
                self._log_progress("步骤5: 进行区域截图分析")
                analysis_result = self._analyze_regions()
                
                if analysis_result['has_failure']:
                    # 存在分析失败，停止循环
                    self._handle_analysis_failure(analysis_result)
                    break
                else:
                    # 所有区域分析成功，继续下一轮
                    success_count = analysis_result['success_count']
                    self.hunt_count += success_count
                    self._log_progress(f"第{self.hunt_count}次刷闪完成，继续下一轮")
                    
                    if self.on_hunt_progress:
                        self.on_hunt_progress(self.hunt_count, success_count)
        
        except Exception as e:
            self.logger.error(f"自动刷闪出错: {e}")
            self._handle_error(f"自动刷闪出错: {e}")
        
        finally:
            self.is_hunting = False
    
    def _wait_with_cancel(self, seconds: float, action: str = ""):
        """等待指定时间，支持取消和倒计时显示"""
        if self.on_countdown and action:
            self.on_countdown(int(seconds), action)
        
        start_time = time.time()
        while time.time() - start_time < seconds and self.is_hunting:
            time.sleep(0.1)
    
    def _analyze_regions(self) -> Dict:
        """分析所有区域（带重试机制）"""
        try:
            # 获取参考图像名称
            reference_name = self.config.get('reference_image')
            if not reference_name:
                reference_names = self.image_analyzer.get_reference_list()
                if reference_names:
                    reference_name = reference_names[0]
                else:
                    return {'has_failure': True, 'success_count': 0, 'failed_regions': ['无参考图像']}
            
            retry_count = self.config.get('retry_count', 2)
            retry_interval = self.config.get('retry_interval', 2.0)
            
            # 进行多次分析，直到成功或达到重试次数
            for attempt in range(retry_count + 1):  # +1 因为第一次不算重试
                if attempt > 0:
                    self.logger.info(f"第 {attempt + 1} 次分析尝试...")
                    self._wait_with_cancel(retry_interval, f"第{attempt + 1}次重试分析")
                
                # 截取所有区域
                results = self.screenshot_manager.capture_all_regions()
                if not results:
                    if attempt == retry_count:  # 最后一次尝试
                        return {'has_failure': True, 'success_count': 0, 'failed_regions': ['截图失败']}
                    continue
                
                # 分析每个区域
                failed_regions = []
                success_count = 0
                all_success = True
                
                for result in results:
                    analysis = self.image_analyzer.analyze_image(result['image'], reference_name)
                    
                    if analysis.get('is_match', False):
                        success_count += 1
                        self.logger.info(f"区域 {result['name']} 分析成功")
                    else:
                        failed_regions.append(result['name'])
                        all_success = False
                        self.logger.info(f"区域 {result['name']} 分析失败")
                
                # 如果所有区域都分析成功，直接返回成功
                if all_success:
                    self.logger.info(f"所有区域分析成功（第 {attempt + 1} 次尝试）")
                    return {
                        'has_failure': False,
                        'success_count': success_count,
                        'failed_regions': [],
                        'total_regions': len(results),
                        'attempt_count': attempt + 1
                    }
                
                # 如果不是最后一次尝试，继续重试
                if attempt < retry_count:
                    self.logger.info(f"第 {attempt + 1} 次分析有失败区域，{retry_interval}秒后重试...")
                    continue
            
            # 所有重试都失败，返回最终结果
            self.logger.info(f"经过 {retry_count + 1} 次尝试，仍有区域分析失败")
            return {
                'has_failure': True,
                'success_count': success_count,
                'failed_regions': failed_regions,
                'total_regions': len(results),
                'attempt_count': retry_count + 1
            }
            
        except Exception as e:
            self.logger.error(f"区域分析失败: {e}")
            return {'has_failure': True, 'success_count': 0, 'failed_regions': [f'分析出错: {e}']}
    
    def _handle_analysis_failure(self, analysis_result: Dict):
        """处理分析失败"""
        failed_regions = analysis_result['failed_regions']
        success_count = analysis_result['success_count']
        
        # 更新计数器
        self.hunt_count += success_count
        
        # 停止刷闪
        self.is_hunting = False
        
        # 显示结果对话框
        self._show_result_dialog(analysis_result)
        
        # 调用回调
        if self.on_hunt_result:
            self.on_hunt_result(analysis_result)
    
    def _show_result_dialog(self, analysis_result: Dict):
        """显示结果对话框"""
        failed_regions = analysis_result['failed_regions']
        success_count = analysis_result['success_count']
        total_regions = analysis_result['total_regions']
        attempt_count = analysis_result.get('attempt_count', 1)
        
        # 构建消息
        message = f"刷闪完成！\n\n"
        message += f"总刷闪次数: {self.hunt_count}\n"
        message += f"本次成功区域: {success_count}/{total_regions}\n"
        message += f"分析尝试次数: {attempt_count}\n\n"
        
        if failed_regions:
            message += f"失败区域: {', '.join(failed_regions)}\n\n"
            message += "经过多次重试分析，确认检测到闪光宝可梦，自动刷闪已停止！"
        else:
            message += "所有区域分析成功，继续刷闪中..."
        
        # 显示对话框
        messagebox.showinfo("刷闪结果", message)
    
    def _handle_error(self, error_message: str):
        """处理错误"""
        self.logger.error(error_message)
        self.is_hunting = False
        
        # 显示错误对话框
        messagebox.showerror("自动刷闪错误", error_message)
        
        # 调用停止回调
        if self.on_hunt_stop:
            self.on_hunt_stop(self.hunt_count)
    
    def _log_progress(self, message: str):
        """记录进度"""
        self.logger.info(message)
        if self.on_hunt_progress:
            self.on_hunt_progress(self.hunt_count, 0, message)
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            'is_hunting': self.is_hunting,
            'hunt_count': self.hunt_count,
            'config': self.config.copy()
        }
    
    def reset_counter(self):
        """重置计数器"""
        self.hunt_count = 0
        self.logger.info("刷闪计数器已重置")
