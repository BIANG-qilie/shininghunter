#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动刷闪模块
实现完整的自动刷闪流程
"""

import time
import threading
import logging
import os
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
            'timeline_actions': [],    # 时间轴动作列表
            'retry_count': 2,          # 分析重试次数
            'retry_interval': 2.0,     # 重试间隔时间（秒）
            'reference_image': None,   # 参考图像名称
        }
    
    def set_config(self, config: Dict):
        """设置配置参数"""
        self.config.update(config)
        self.logger.info(f"更新自动刷闪配置: {config}")
    
    def set_callbacks(self, on_hunt_start=None, on_hunt_stop=None, 
                     on_hunt_progress=None, on_hunt_result=None, on_countdown=None, on_analysis_progress=None):
        """设置回调函数"""
        self.on_hunt_start = on_hunt_start
        self.on_hunt_stop = on_hunt_stop
        self.on_hunt_progress = on_hunt_progress
        self.on_hunt_result = on_hunt_result
        self.on_countdown = on_countdown
        self.on_analysis_progress = on_analysis_progress
    
    def start_hunting(self):
        """开始自动刷闪"""
        if self.is_hunting:
            self.logger.warning("自动刷闪已在运行")
            return False
        
        # 检查必要条件
        if not self._check_requirements():
            return False
        
        # 不自动重置计数器，由GUI控制
        # self.hunt_count = 0  # 注释掉自动重置
        self.is_hunting = True
        
        # 启动刷闪线程
        self.hunt_thread = threading.Thread(target=self._hunt_loop, daemon=True)
        self.hunt_thread.start()
        
        self.logger.info("开始自动刷闪")
        if self.on_hunt_start:
            self.on_hunt_start()
        
        return True
    
    def pause_hunting(self):
        """暂停自动刷闪"""
        if not self.is_hunting:
            self.logger.warning("自动刷闪未在运行")
            return
        
        self.is_hunting = False
        self.logger.info("暂停自动刷闪")
    
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
    
    def continue_hunting(self):
        """继续自动刷闪（用于错判处理）"""
        if not self.is_hunting:
            self.logger.info("继续自动刷闪")
            self.is_hunting = True
            self.hunt_thread = threading.Thread(target=self._hunt_loop, daemon=True)
            self.hunt_thread.start()
    
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
            timeline_actions = self.config.get('timeline_actions', [])
            if not timeline_actions:
                self._handle_error("时间轴配置为空")
                return
            
            while self.is_hunting:
                # 执行时间轴动作序列
                for i, action in enumerate(timeline_actions):
                    if not self.is_hunting:
                        break
                    
                    action_type = action['action']
                    delay = action['delay']
                    description = action['description']
                    
                    self._log_progress(f"步骤{i+1}: {description}")
                    
                    # 执行动作
                    if action_type == 'initial_delay':
                        self._wait_with_cancel(delay, f"开始刷闪 - {description}")
                    elif action_type == 'reset':
                        if not self.keyboard_controller.reset_action():
                            self._handle_error("重置键失败")
                            return
                        self._wait_with_cancel(delay, f"重置后等待 - {description}")
                    elif action_type == 'quick_load':
                        if not self.keyboard_controller.quick_load_save():
                            self._handle_error("快速读取键失败")
                            return
                        self._wait_with_cancel(delay, f"快速读取后等待 - {description}")
                    elif action_type == 'confirm':
                        if not self.keyboard_controller.confirm_action():
                            self._handle_error("确认键失败")
                            return
                        self._wait_with_cancel(delay, f"{description}")
                    elif action_type == 'analysis':
                        # 进行区域截图分析
                        analysis_result = self._analyze_regions()
                        
                        if analysis_result['has_failure']:
                            # 存在分析失败，停止循环
                            self._handle_analysis_failure(analysis_result)
                            return
                        else:
                            # 所有区域分析成功，继续下一轮
                            success_count = analysis_result['success_count']
                            self.hunt_count += success_count
                            self._log_progress(f"第{self.hunt_count}次刷闪完成，继续下一轮")
                            
                            if self.on_hunt_progress:
                                self.on_hunt_progress(self.hunt_count, success_count)
                    elif action_type == 'custom_delay':
                        self._wait_with_cancel(delay, description)
        
        except Exception as e:
            self.logger.error(f"自动刷闪出错: {e}")
            self._handle_error(f"自动刷闪出错: {e}")
        
        finally:
            self.is_hunting = False
    
    def _wait_with_cancel(self, seconds: float, action: str = ""):
        """等待指定时间，支持取消和倒计时显示"""
        if self.on_countdown and action:
            self.on_countdown(seconds, action)
        
        start_time = time.time()
        while time.time() - start_time < seconds and self.is_hunting:
            time.sleep(0.1)
    
    def _analyze_regions(self) -> Dict:
        """分析所有区域（带重试机制）"""
        try:
            # 检查是否有参考图像
            reference_names = self.image_analyzer.get_reference_list()
            if not reference_names:
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
                failed_images = []  # 收集失败图像
                success_count = 0
                all_success = True
                
                # 收集所有分析结果用于实时显示
                realtime_analysis_results = []
                
                for result in results:
                    analysis = self.image_analyzer.analyze_image_multi_reference(result['image'])
                    analysis['region_name'] = result['name']
                    realtime_analysis_results.append(analysis)
                    
                    if analysis.get('is_match', False):
                        success_count += 1
                        best_ref = analysis.get('best_reference', '未知')
                        self.logger.info(f"区域 {result['name']} 分析成功 (最佳匹配: {best_ref})")
                    else:
                        # 标记失败区域和第几次判断
                        failed_region_info = f"{result['name']} (第{attempt + 1}次判断)"
                        failed_regions.append(failed_region_info)
                        # 保存失败图像
                        if 'image_path' in result:
                            failed_images.append((failed_region_info, result['image_path']))
                        all_success = False
                        self.logger.info(f"区域 {result['name']} 分析失败 (第{attempt + 1}次判断)")
                
                # 实时显示分析结果到GUI
                if hasattr(self, 'on_analysis_progress') and callable(self.on_analysis_progress):
                    self.on_analysis_progress(realtime_analysis_results, attempt + 1)
                
                # 如果所有区域都分析成功，直接返回成功
                if all_success:
                    self.logger.info(f"所有区域分析成功（第 {attempt + 1} 次尝试）")
                    return {
                        'has_failure': False,
                        'success_count': success_count,
                        'failed_regions': [],
                        'failed_images': [],
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
                'failed_images': failed_images,
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
        
        # 播放BGM音乐（检测到闪光）
        self._play_shiny_bgm()
        
        # 显示结果对话框
        self._show_result_dialog(analysis_result)
        
        # 调用回调
        if self.on_hunt_result:
            self.on_hunt_result(analysis_result)
    
    def _play_shiny_bgm(self):
        """播放闪光BGM音乐"""
        try:
            import pygame
            import threading
            
            def play_music():
                try:
                    # 初始化pygame mixer
                    pygame.mixer.init()
                    
                    # 音乐文件路径
                    music_path = "configs/music/Édith Piaf - Non, je ne regrette rien_EM.flac"
                    
                    if os.path.exists(music_path):
                        # 加载并播放音乐
                        pygame.mixer.music.load(music_path)
                        pygame.mixer.music.play()
                        self.logger.info("播放闪光BGM音乐")
                    else:
                        self.logger.warning(f"BGM音乐文件不存在: {music_path}")
                        
                except Exception as e:
                    self.logger.error(f"播放BGM失败: {e}")
            
            # 在后台线程中播放音乐，避免阻塞UI
            music_thread = threading.Thread(target=play_music, daemon=True)
            music_thread.start()
            
        except ImportError:
            self.logger.warning("pygame未安装，无法播放BGM音乐")
        except Exception as e:
            self.logger.error(f"播放BGM失败: {e}")
    
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
