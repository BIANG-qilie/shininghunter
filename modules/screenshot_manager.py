#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图管理模块
负责完整屏幕截图和多区域选择功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageTk
import numpy as np
import threading
import time
from pathlib import Path
import json

try:
    import mss
    import cv2
except ImportError:
    print("请安装必要的依赖: pip install mss opencv-python pillow")
    mss = None
    cv2 = None

class FullScreenRegionSelector:
    """基于完整屏幕截图的区域选择器"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        
        # 选择状态
        self.is_selecting = False
        self.start_point = None
        self.end_point = None
        self.current_region = None
        self.regions = []  # 存储所有选择的区域
        self.region_counter = 1
        
        # 先截取完整屏幕，再创建界面
        self.capture_full_screen_first()
    
    def create_selector_window(self):
        """创建区域选择窗口"""
        self.selector_window = tk.Toplevel(self.parent)
        self.selector_window.title("区域选择器 - 在完整截图上选择区域")
        self.selector_window.attributes('-topmost', True)
        
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.selector_window.winfo_screenwidth()
        screen_height = self.selector_window.winfo_screenheight()
        
        # 设置窗口大小为屏幕的90%，并居中显示
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.selector_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.selector_window.minsize(800, 600)  # 设置最小尺寸
        
        # 创建主框架
        main_frame = ttk.Frame(self.selector_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 说明标签
        info_label = ttk.Label(main_frame, text="在下方截图上拖拽选择区域，可以添加多个区域")
        info_label.pack(pady=(0, 5))
        
        # 创建画布框架 - 占据大部分空间
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布和滚动条
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局 - 画布占据主要空间
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # 绑定窗口大小变化事件
        self.selector_window.bind("<Configure>", self.on_window_resize)
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 左侧按钮
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="重新截图", command=self.re_capture_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="清除所有区域", command=self.clear_all_regions).pack(side=tk.LEFT, padx=5)
        
        # 右侧按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="确认并保存", command=self.confirm_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_buttons, text="取消", command=self.cancel_selection).pack(side=tk.LEFT, padx=5)
        
        # 区域列表框架 - 更紧凑的布局
        list_frame = ttk.LabelFrame(main_frame, text="已选择的区域")
        list_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 创建区域列表 - 减少高度
        self.region_listbox = tk.Listbox(list_frame, height=3)
        self.region_listbox.pack(fill=tk.X, padx=5, pady=3)
        
        # 绑定双击删除事件
        self.region_listbox.bind('<Double-1>', self.delete_selected_region)
    
    def capture_full_screen_first(self):
        """先截取完整屏幕，再创建界面"""
        if mss is None:
            messagebox.showerror("错误", "mss库未安装，无法截图")
            return
        
        try:
            with mss.mss() as sct:
                # 获取主显示器
                monitor = sct.monitors[1]  # 主显示器
                screenshot = sct.grab(monitor)
                
                # 转换为PIL图像
                self.original_image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                self.original_size = self.original_image.size
                
                self.logger.info("完整屏幕截图成功")
                
                # 截图完成后创建界面
                self.create_selector_window()
                
                # 延迟显示图像，确保窗口完全创建
                self.selector_window.after(100, self.display_captured_image)
                
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            messagebox.showerror("错误", f"截图失败: {e}")
    
    def display_captured_image(self):
        """显示已截取的图像"""
        if hasattr(self, 'original_image'):
            self.display_image(self.original_image)
    
    def re_capture_screen(self):
        """重新截图（保持界面打开）"""
        if mss is None:
            messagebox.showerror("错误", "mss库未安装，无法截图")
            return
        
        try:
            with mss.mss() as sct:
                # 获取主显示器
                monitor = sct.monitors[1]  # 主显示器
                screenshot = sct.grab(monitor)
                
                # 转换为PIL图像
                self.original_image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                self.original_size = self.original_image.size
                
                self.logger.info("重新截图成功")
                
                # 重新显示图像
                self.display_image(self.original_image)
                
        except Exception as e:
            self.logger.error(f"重新截图失败: {e}")
            messagebox.showerror("错误", f"重新截图失败: {e}")
    
    def capture_full_screen(self):
        """截取完整屏幕"""
        if mss is None:
            messagebox.showerror("错误", "mss库未安装，无法截图")
            return
        
        try:
            with mss.mss() as sct:
                # 获取主显示器
                monitor = sct.monitors[1]  # 主显示器
                screenshot = sct.grab(monitor)
                
                # 转换为PIL图像
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # 调整图像大小以适应窗口
                self.display_image(img)
                
                self.logger.info("完整屏幕截图成功")
                
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            messagebox.showerror("错误", f"截图失败: {e}")
    
    def display_image(self, img: Image.Image):
        """在画布上显示图像"""
        # 获取画布的实际可用尺寸
        self.selector_window.update_idletasks()  # 确保窗口尺寸已更新
        
        # 获取画布框架的尺寸
        canvas_frame = self.canvas.master
        available_width = canvas_frame.winfo_width()
        available_height = canvas_frame.winfo_height()
        
        # 如果尺寸为1，说明还没有正确计算，使用默认值
        if available_width <= 1 or available_height <= 1:
            available_width = 1000
            available_height = 700
        
        img_width, img_height = img.size
        
        # 计算缩放比例，让图像尽可能大地显示在可用空间内
        scale_x = available_width / img_width
        scale_y = available_height / img_height
        self.scale = min(scale_x, scale_y)  # 保持宽高比，适应可用空间
        
        # 缩放图像
        new_width = int(img_width * self.scale)
        new_height = int(img_height * self.scale)
        self.display_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 转换为PhotoImage
        self.photo = ImageTk.PhotoImage(self.display_img)
        
        # 清除画布并显示图像
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # 设置画布尺寸以匹配图像
        self.canvas.configure(width=new_width, height=new_height)
        
        # 更新滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # 保存原始图像用于后续截图
        self.original_image = img
        self.original_size = (img_width, img_height)
        
        # 重新绘制已选择的区域
        self.draw_all_regions()
    
    def on_window_resize(self, event):
        """窗口大小变化事件处理"""
        # 只有当窗口大小真正改变时才重新显示图像
        if event.widget == self.selector_window and hasattr(self, 'original_image'):
            # 延迟重新显示，避免频繁更新
            if hasattr(self, '_resize_timer') and self._resize_timer is not None:
                try:
                    self.selector_window.after_cancel(self._resize_timer)
                except:
                    pass  # 忽略取消失败的错误
            self._resize_timer = self.selector_window.after(200, self.refresh_display)
    
    def refresh_display(self):
        """刷新显示"""
        if hasattr(self, 'original_image'):
            self.display_image(self.original_image)
    
    def on_click(self, event):
        """鼠标点击事件"""
        self.start_point = (event.x, event.y)
        self.is_selecting = True
    
    def on_drag(self, event):
        """鼠标拖拽事件"""
        if not self.is_selecting:
            return
        
        self.end_point = (event.x, event.y)
        self.draw_current_selection()
    
    def on_release(self, event):
        """鼠标释放事件"""
        if not self.is_selecting:
            return
        
        self.end_point = (event.x, event.y)
        self.is_selecting = False
        
        # 计算实际区域坐标
        if self.start_point and self.end_point:
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            
            # 确保坐标正确
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y2, y2)
            
            # 转换为原始图像坐标
            orig_x1 = int(x1 / self.scale)
            orig_y1 = int(y1 / self.scale)
            orig_x2 = int(x2 / self.scale)
            orig_y2 = int(y2 / self.scale)
            
            # 确保坐标在图像范围内
            orig_x1 = max(0, min(orig_x1, self.original_size[0]))
            orig_y1 = max(0, min(orig_y1, self.original_size[1]))
            orig_x2 = max(0, min(orig_x2, self.original_size[0]))
            orig_y2 = max(0, min(orig_y2, self.original_size[1]))
            
            if orig_x2 > orig_x1 and orig_y2 > orig_y1:
                region = (orig_x1, orig_y1, orig_x2, orig_y2)
                self.add_region(region)
        
        self.draw_current_selection()
    
    def draw_current_selection(self):
        """绘制当前选择区域"""
        # 清除当前选择框
        self.canvas.delete("current_selection")
        
        if self.start_point and self.end_point:
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            
            # 确保坐标正确
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # 绘制选择框
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='red', width=2, tags="current_selection"
            )
    
    def add_region(self, region: Tuple[int, int, int, int]):
        """添加区域到列表"""
        region_name = f"区域_{self.region_counter}"
        self.region_counter += 1
        
        region_info = {
            'name': region_name,
            'region': region,
            'enabled': True
        }
        
        self.regions.append(region_info)
        self.update_region_list()
        self.draw_all_regions()
        
        self.logger.info(f"添加区域: {region_name} - {region}")
    
    def update_region_list(self):
        """更新区域列表显示"""
        self.region_listbox.delete(0, tk.END)
        for region_info in self.regions:
            status = "✓" if region_info['enabled'] else "✗"
            self.region_listbox.insert(tk.END, f"{status} {region_info['name']}: {region_info['region']}")
    
    def draw_all_regions(self):
        """绘制所有已选择的区域"""
        # 清除所有区域框
        self.canvas.delete("region_box")
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        for i, region_info in enumerate(self.regions):
            region = region_info['region']
            color = colors[i % len(colors)]
            
            # 转换为显示坐标
            x1 = region[0] * self.scale
            y1 = region[1] * self.scale
            x2 = region[2] * self.scale
            y2 = region[3] * self.scale
            
            # 绘制区域框
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=color, width=2, tags="region_box"
            )
            
            # 绘制区域标签
            self.canvas.create_text(
                x1, y1-10, text=region_info['name'],
                fill=color, tags="region_box", anchor=tk.W
            )
    
    def delete_selected_region(self, event):
        """删除选中的区域"""
        selection = self.region_listbox.curselection()
        if selection:
            index = selection[0]
            region_info = self.regions.pop(index)
            self.update_region_list()
            self.draw_all_regions()
            self.logger.info(f"删除区域: {region_info['name']}")
    
    def clear_all_regions(self):
        """清除所有区域"""
        self.regions.clear()
        self.region_counter = 1
        self.update_region_list()
        self.draw_all_regions()
        self.logger.info("清除所有区域")
    
    def confirm_selection(self):
        """确认选择并返回区域列表"""
        if not self.regions:
            messagebox.showwarning("警告", "请至少选择一个区域")
            return
        
        if self.callback:
            self.callback(self.regions.copy())
        
        self.selector_window.destroy()
    
    def cancel_selection(self):
        """取消选择"""
        self.selector_window.destroy()

class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.screenshot_regions = []  # 存储截图区域
        self.is_capturing = False
        self.capture_thread = None
        self.shiny_images = set()  # 存储闪光图片路径
        
        # 创建截图目录
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
        if mss is None:
            self.logger.error("mss 未安装，截图功能不可用")
    
    def open_region_selector(self, parent, callback=None):
        """打开区域选择器"""
        def on_regions_selected(regions):
            self.screenshot_regions = regions
            if callback:
                callback(regions)
        
        selector = FullScreenRegionSelector(parent, on_regions_selected)
    
    def add_regions_from_selector(self, regions: List[Dict]):
        """从选择器添加区域"""
        self.screenshot_regions = regions
        self.logger.info(f"添加了 {len(regions)} 个截图区域")
    
    def add_region(self, name: str, x1: int, y1: int, x2: int, y2: int):
        """添加单个区域"""
        region_info = {
            'name': name,
            'region': (x1, y1, x2, y2),
            'enabled': True
        }
        self.screenshot_regions.append(region_info)
        self.logger.info(f"添加区域: {name} ({x1}, {y1}, {x2}, {y2})")
    
    def capture_region(self, region: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        截取指定区域
        
        Args:
            region: 区域坐标 (x1, y1, x2, y2)
            
        Returns:
            numpy数组格式的图像数据
        """
        if mss is None:
            self.logger.error("mss 未安装，无法截图")
            return None
        
        try:
            x1, y1, x2, y2 = region
            width = x2 - x1
            height = y2 - y1
            
            with mss.mss() as sct:
                monitor = {
                    "top": y1,
                    "left": x1,
                    "width": width,
                    "height": height
                }
                
                screenshot = sct.grab(monitor)
                # 转换为numpy数组
                img_array = np.array(screenshot)
                # 转换颜色格式 (BGRA -> RGB)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)
                
                return img_array
                
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return None
    
    def capture_all_regions(self) -> List[Dict]:
        """
        截取所有启用的区域
        
        Returns:
            包含截图数据的列表
        """
        if mss is None:
            return []
        
        results = []
        timestamp = time.time()
        
        for region_info in self.screenshot_regions:
            if not region_info['enabled']:
                continue
            
            region = region_info['region']
            img_array = self.capture_region(region)
            
            if img_array is not None:
                # 保存图像到文件
                image_path = self._save_region_image(img_array, region_info['name'], timestamp)
                
                result = {
                    'name': region_info['name'],
                    'region': region,
                    'image': img_array,
                    'image_path': image_path,
                    'timestamp': timestamp,
                    'enabled': region_info['enabled']
                }
                results.append(result)
        
        self.logger.info(f"完成 {len(results)} 个区域的截图")
        return results
    
    def _save_region_image(self, img_array: np.ndarray, region_name: str, timestamp: float) -> str:
        """保存区域图像到文件"""
        try:
            # 生成文件名
            time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(timestamp))
            filename = f"screenshot_{time_str}_{region_name}.png"
            filepath = self.screenshot_dir / filename
            
            # 直接保存，保持原色（MSS已经提供RGB格式）
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                # 确保是RGB格式（MSS已经提供RGB）
                img_pil = Image.fromarray(img_array, 'RGB')
                img_pil.save(filepath)
            else:
                # 灰度图像
                img_pil = Image.fromarray(img_array)
                img_pil.save(filepath)
            
            return str(filepath)
        except Exception as e:
            self.logger.error(f"保存区域图像失败: {e}")
            return ""
    
    def save_screenshot(self, image_data: np.ndarray, filename: str) -> bool:
        """
        保存截图到文件
        
        Args:
            image_data: 图像数据
            filename: 文件名
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 转换为PIL图像
            img = Image.fromarray(image_data)
            
            # 保存文件
            filepath = self.screenshot_dir / filename
            img.save(filepath)
            
            self.logger.info(f"截图已保存: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存截图失败: {e}")
            return False
    
    def mark_as_shiny(self, image_path: str):
        """标记图像为闪光图片（不会被清理）"""
        self.shiny_images.add(str(image_path))
        self.logger.info(f"标记为闪光图片: {image_path}")
    
    def cleanup_screenshots(self, keep_shiny: bool = True, max_age_hours: int = 24):
        """
        清理screenshots文件夹
        
        Args:
            keep_shiny: 是否保留闪光图片
            max_age_hours: 保留时间（小时）
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            kept_count = 0
            
            for file_path in self.screenshot_dir.glob("*.png"):
                # 检查是否为闪光图片
                if keep_shiny and str(file_path) in self.shiny_images:
                    kept_count += 1
                    continue
                
                # 检查文件年龄
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()  # 删除文件
                        deleted_count += 1
                        self.logger.info(f"删除过期截图: {file_path.name}")
                    except Exception as e:
                        self.logger.error(f"删除文件失败 {file_path}: {e}")
                else:
                    kept_count += 1
            
            self.logger.info(f"截图清理完成: 删除{deleted_count}个, 保留{kept_count}个")
            return deleted_count, kept_count
            
        except Exception as e:
            self.logger.error(f"清理截图失败: {e}")
            return 0, 0
    
    def save_all_screenshots(self, results: List[Dict], prefix: str = "screenshot") -> List[str]:
        """
        保存所有截图
        
        Args:
            results: 截图结果列表
            prefix: 文件名前缀
            
        Returns:
            保存的文件路径列表
        """
        saved_files = []
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        for i, result in enumerate(results):
            filename = f"{prefix}_{timestamp}_{i+1}_{result['name']}.png"
            if self.save_screenshot(result['image'], filename):
                saved_files.append(str(self.screenshot_dir / filename))
        
        return saved_files
    
    def start_scheduled_capture(self, interval: float = 1.0, callback=None, auto_save: bool = False):
        """
        开始定时截图
        
        Args:
            interval: 截图间隔（秒）
            callback: 截图完成后的回调函数
            auto_save: 是否自动保存截图
        """
        if self.is_capturing:
            self.logger.warning("定时截图已在运行")
            return
        
        if not self.screenshot_regions:
            self.logger.error("没有设置截图区域")
            return
        
        self.is_capturing = True
        
        def capture_loop():
            while self.is_capturing:
                try:
                    results = self.capture_all_regions()
                    
                    if auto_save and results:
                        saved_files = self.save_all_screenshots(results)
                        self.logger.info(f"自动保存了 {len(saved_files)} 个截图")
                    
                    if callback:
                        callback(results)
                    
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"定时截图出错: {e}")
                    break
        
        # 在单独线程中运行
        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        
        self.logger.info(f"开始定时截图，间隔: {interval}秒")
    
    def stop_scheduled_capture(self):
        """停止定时截图"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        self.logger.info("停止定时截图")
    
    def get_region_list(self) -> List[Dict]:
        """获取区域列表"""
        return self.screenshot_regions.copy()
    
    def toggle_region(self, index: int):
        """切换区域的启用状态"""
        if 0 <= index < len(self.screenshot_regions):
            self.screenshot_regions[index]['enabled'] = not self.screenshot_regions[index]['enabled']
            status = "启用" if self.screenshot_regions[index]['enabled'] else "禁用"
            self.logger.info(f"{status}区域: {self.screenshot_regions[index]['name']}")
    
    def clear_regions(self):
        """清除所有区域"""
        self.screenshot_regions.clear()
        self.logger.info("清除所有截图区域")
    
    def save_regions_config(self, filepath: str):
        """保存区域配置到文件"""
        try:
            config = {
                'regions': self.screenshot_regions,
                'timestamp': time.time()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"区域配置已保存: {filepath}")
        except Exception as e:
            self.logger.error(f"保存区域配置失败: {e}")
    
    def load_regions_config(self, filepath: str):
        """从文件加载区域配置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.screenshot_regions = config.get('regions', [])
            self.logger.info(f"区域配置已加载: {filepath}")
        except Exception as e:
            self.logger.error(f"加载区域配置失败: {e}")