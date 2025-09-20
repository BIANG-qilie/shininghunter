#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI界面模块
提供用户友好的图形界面，整合所有功能模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, List
from PIL import Image, ImageTk
import threading
import json
import time
import os
import shutil

from .image_analyzer import ImageAnalyzer

class MainGUI:
    """主界面类"""
    
    def __init__(self, root, app_instance):
        self.root = root
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
        
        # 设置现代化样式
        self._setup_modern_style()
        
        # 界面状态
        self.is_capturing = False
        self.analysis_results = []
        
        # 设置窗口属性
        self.root.title("ShiningHunter - 宝可梦闪光刷取工具")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg='#f0f0f0')
        
        # 创建界面
        self.create_interface()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_modern_style(self):
        """设置现代化样式"""
        # 创建自定义样式
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('clam')
        
        # 定义现代化颜色
        self.colors = {
            'primary': '#2E86AB',      # 主色调 - 蓝色
            'secondary': '#A23B72',    # 次要色调 - 紫红色
            'success': '#F18F01',      # 成功色 - 橙色
            'warning': '#C73E1D',      # 警告色 - 红色
            'info': '#7209B7',         # 信息色 - 紫色
            'light': '#F8F9FA',        # 浅色背景
            'dark': '#212529',         # 深色文字
            'border': '#DEE2E6'        # 边框色
        }
        
        # 配置LabelFrame样式
        style.configure('Modern.TLabelframe', 
                       background=self.colors['light'],
                       borderwidth=2,
                       relief='solid')
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['light'],
                       foreground=self.colors['primary'],
                       font=('Arial', 10, 'bold'))
        
        # 配置按钮样式
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 9, 'bold'))
        style.map('Modern.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['dark'])])
        
        # 配置成功按钮样式
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 9, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#E67E22'),
                           ('pressed', '#D35400')])
        
        # 配置警告按钮样式
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 9, 'bold'))
        style.map('Warning.TButton',
                 background=[('active', '#E74C3C'),
                           ('pressed', '#C0392B')])
        
        # 配置进度条样式
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['border'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
        # 配置输入框样式
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=2,
                       relief='solid',
                       insertcolor=self.colors['primary'])
        style.map('Modern.TEntry',
                 focuscolor=[('!focus', self.colors['border']),
                           ('focus', self.colors['primary'])])
    
    def create_interface(self):
        """创建主界面"""
        self.root.title("ShiningHunter - DeSmuME闪光刷取辅助工具")
        self.root.geometry("800x600")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个标签页
        self.create_control_tab()
        self.create_screenshot_tab()
        self.create_analysis_tab()
        self.create_settings_tab()
    
    def create_control_tab(self):
        """创建控制标签页"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="控制面板")
        
        # 键盘控制区域
        keyboard_frame = ttk.LabelFrame(control_frame, text="键盘控制")
        keyboard_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # F1快速读取存档
        ttk.Button(keyboard_frame, text="F1 - 快速读取存档", 
                  command=self.quick_load_save).pack(side=tk.LEFT, padx=5, pady=5)
        
        # X键确认
        ttk.Button(keyboard_frame, text="X - 确认操作", 
                  command=self.confirm_action).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 自动操作区域
        auto_frame = ttk.LabelFrame(control_frame, text="自动刷闪")
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 刷闪次数显示
        count_frame = ttk.Frame(auto_frame)
        count_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(count_frame, text="刷闪次数:").pack(side=tk.LEFT)
        self.hunt_count_var = tk.StringVar(value="0")
        self.hunt_count_label = ttk.Label(count_frame, textvariable=self.hunt_count_var, 
                                         font=('Arial', 12, 'bold'), foreground='blue')
        self.hunt_count_label.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(count_frame, text="重置计数", 
                  command=self.reset_hunt_count).pack(side=tk.RIGHT, padx=5)
        
        # 自动刷闪控制
        control_buttons_frame = ttk.Frame(auto_frame)
        control_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(control_buttons_frame, text="开始自动刷闪", 
                  command=self.start_auto_hunt, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_buttons_frame, text="停止自动刷闪", 
                  command=self.stop_auto_hunt, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        # 时间配置管理按钮
        config_buttons_frame = ttk.Frame(auto_frame)
        config_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(config_buttons_frame, text="保存时间配置", 
                  command=self.save_time_config, style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(config_buttons_frame, text="加载时间配置", 
                  command=self.load_time_config, style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(config_buttons_frame, text="重置为默认", 
                  command=self.reset_time_config, style='Warning.TButton').pack(side=tk.LEFT, padx=2)
        
        # 预设配置选择
        preset_frame = ttk.Frame(auto_frame)
        preset_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(preset_frame, text="预设配置:").pack(side=tk.LEFT, padx=2)
        
        ttk.Button(preset_frame, text="默认", 
                  command=lambda: self.load_preset_config("default"), style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(preset_frame, text="快速", 
                  command=lambda: self.load_preset_config("fast"), style='Success.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(preset_frame, text="安全", 
                  command=lambda: self.load_preset_config("safe"), style='Warning.TButton').pack(side=tk.LEFT, padx=2)
        
        # 批量导入功能
        batch_import_frame = ttk.LabelFrame(auto_frame, text="批量导入配置", style='Modern.TLabelframe')
        batch_import_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 导入输入框
        import_input_frame = ttk.Frame(batch_import_frame)
        import_input_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(import_input_frame, text="配置名称:").pack(side=tk.LEFT, padx=2)
        self.import_name_var = tk.StringVar(value="lugia")
        import_name_entry = ttk.Entry(import_input_frame, textvariable=self.import_name_var, width=15, style='Modern.TEntry')
        import_name_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(import_input_frame, text="批量导入", 
                  command=self.batch_import_config, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        # 导入状态显示
        self.import_status_var = tk.StringVar(value="")
        import_status_label = ttk.Label(batch_import_frame, textvariable=self.import_status_var, 
                                      foreground='blue')
        import_status_label.pack(pady=2)
        
        # 时间配置区域
        time_config_frame = ttk.LabelFrame(auto_frame, text="时间配置", style='Modern.TLabelframe')
        time_config_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 时间配置网格
        time_grid_frame = ttk.Frame(time_config_frame)
        time_grid_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 初始延迟
        ttk.Label(time_grid_frame, text="初始延迟(秒):").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.initial_delay_var = tk.StringVar(value="5.0")
        initial_delay_entry = ttk.Entry(time_grid_frame, textvariable=self.initial_delay_var, width=10, style='Modern.TEntry')
        initial_delay_entry.grid(row=0, column=1, padx=2)
        ttk.Label(time_grid_frame, text="(1.0-30.0)").grid(row=0, column=2, sticky=tk.W, padx=2)
        
        # F1后延迟
        ttk.Label(time_grid_frame, text="F1后延迟(秒):").grid(row=0, column=3, sticky=tk.W, padx=2)
        self.f1_delay_var = tk.StringVar(value="0.5")
        f1_delay_entry = ttk.Entry(time_grid_frame, textvariable=self.f1_delay_var, width=10, style='Modern.TEntry')
        f1_delay_entry.grid(row=0, column=4, padx=2)
        ttk.Label(time_grid_frame, text="(0.1-5.0)").grid(row=0, column=5, sticky=tk.W, padx=2)
        
        # 第一次A键后延迟
        ttk.Label(time_grid_frame, text="第一次A键后延迟(秒):").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.first_a_delay_var = tk.StringVar(value="0.8")
        first_a_delay_entry = ttk.Entry(time_grid_frame, textvariable=self.first_a_delay_var, width=10, style='Modern.TEntry')
        first_a_delay_entry.grid(row=1, column=1, padx=2)
        ttk.Label(time_grid_frame, text="(0.1-5.0)").grid(row=1, column=2, sticky=tk.W, padx=2)
        
        # 分析前延迟
        ttk.Label(time_grid_frame, text="分析前延迟(秒):").grid(row=1, column=3, sticky=tk.W, padx=2)
        self.analysis_delay_var = tk.StringVar(value="4.0")
        analysis_delay_entry = ttk.Entry(time_grid_frame, textvariable=self.analysis_delay_var, width=10, style='Modern.TEntry')
        analysis_delay_entry.grid(row=1, column=4, padx=2)
        ttk.Label(time_grid_frame, text="(1.0-20.0)").grid(row=1, column=5, sticky=tk.W, padx=2)
        
        # 分析重试配置
        retry_config_frame = ttk.LabelFrame(auto_frame, text="分析重试配置", style='Modern.TLabelframe')
        retry_config_frame.pack(fill=tk.X, padx=5, pady=2)
        
        retry_grid_frame = ttk.Frame(retry_config_frame)
        retry_grid_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 重试次数
        ttk.Label(retry_grid_frame, text="重试次数:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.retry_count_var = tk.StringVar(value="2")
        retry_count_entry = ttk.Entry(retry_grid_frame, textvariable=self.retry_count_var, width=10, style='Modern.TEntry')
        retry_count_entry.grid(row=0, column=1, padx=2)
        ttk.Label(retry_grid_frame, text="(0-5)").grid(row=0, column=2, sticky=tk.W, padx=2)
        
        # 重试间隔
        ttk.Label(retry_grid_frame, text="重试间隔(秒):").grid(row=0, column=3, sticky=tk.W, padx=2)
        self.retry_interval_var = tk.StringVar(value="2.0")
        retry_interval_entry = ttk.Entry(retry_grid_frame, textvariable=self.retry_interval_var, width=10, style='Modern.TEntry')
        retry_interval_entry.grid(row=0, column=4, padx=2)
        ttk.Label(retry_grid_frame, text="(0.5-10.0)").grid(row=0, column=5, sticky=tk.W, padx=2)
        
        # 状态显示
        self.hunt_status_var = tk.StringVar(value="就绪")
        self.hunt_status_label = ttk.Label(auto_frame, textvariable=self.hunt_status_var, 
                                          foreground='green')
        self.hunt_status_label.pack(pady=2)
        
        # 倒计时显示
        countdown_frame = ttk.LabelFrame(auto_frame, text="操作倒计时", style='Modern.TLabelframe')
        countdown_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.countdown_var = tk.StringVar(value="等待开始...")
        self.countdown_label = ttk.Label(countdown_frame, textvariable=self.countdown_var, 
                                        font=('Arial', 12, 'bold'), foreground='blue')
        self.countdown_label.pack(pady=5)
        
        # 倒计时进度条
        self.countdown_progress = ttk.Progressbar(countdown_frame, mode='determinate', 
                                                 length=200, style='Modern.Horizontal.TProgressbar')
        self.countdown_progress.pack(pady=2)
        
        # 倒计时相关变量
        self.countdown_timer = None
        self.countdown_remaining = 0
        self.countdown_total = 0
        self.countdown_action = ""
        
        # 为输入框添加验证
        self._setup_input_validation()
        
        # 状态显示
        status_frame = ttk.LabelFrame(control_frame, text="状态信息")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = tk.Text(status_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_screenshot_tab(self):
        """创建截图标签页"""
        screenshot_frame = ttk.Frame(self.notebook)
        self.notebook.add(screenshot_frame, text="截图管理")
        
        # 截图控制区域
        control_frame = ttk.LabelFrame(screenshot_frame, text="截图控制")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="添加截图区域", 
                  command=self.add_screenshot_region).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_frame, text="清除所有区域", 
                  command=self.clear_screenshot_regions).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_frame, text="开始定时截图", 
                  command=self.start_continuous_screenshot).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_frame, text="停止定时截图", 
                  command=self.stop_continuous_screenshot).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_frame, text="手动截图", 
                  command=self.manual_capture).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_frame, text="保存区域配置", 
                  command=self.save_regions_config).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(control_frame, text="加载区域配置", 
                  command=self.load_regions_config).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 区域列表
        list_frame = ttk.LabelFrame(screenshot_frame, text="截图区域列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview显示区域列表
        columns = ('名称', '坐标', '状态')
        self.region_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.region_tree.heading(col, text=col)
            self.region_tree.column(col, width=150)
        
        # 添加滚动条
        region_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.region_tree.yview)
        self.region_tree.configure(yscrollcommand=region_scrollbar.set)
        
        self.region_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        region_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.region_tree.bind('<Double-1>', self.toggle_region_status)
        
        # 右键菜单
        self.region_menu = tk.Menu(self.root, tearoff=0)
        self.region_menu.add_command(label="启用/禁用", command=self.toggle_region_status)
        self.region_menu.add_command(label="删除区域", command=self.delete_region)
        self.region_tree.bind('<Button-3>', self.show_region_menu)
    
    def create_analysis_tab(self):
        """创建分析标签页"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="图像分析")
        
        # 参考图像管理
        reference_frame = ttk.LabelFrame(analysis_frame, text="参考图像管理")
        reference_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(reference_frame, text="加载参考图像", 
                  command=self.load_reference_image).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(reference_frame, text="清除参考图像", 
                  command=self.clear_reference_images).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 参考图像列表
        self.reference_listbox = tk.Listbox(reference_frame, height=3)
        self.reference_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # 分析控制
        analysis_control_frame = ttk.LabelFrame(analysis_frame, text="分析控制")
        analysis_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(analysis_control_frame, text="开始分析", 
                  command=self.start_analysis).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(analysis_control_frame, text="停止分析", 
                  command=self.stop_analysis).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 分析结果显示
        result_frame = ttk.LabelFrame(analysis_frame, text="分析结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD)
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_settings_tab(self):
        """创建设置标签页"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="设置")
        
        # 阈值设置
        threshold_frame = ttk.LabelFrame(settings_frame, text="分析阈值设置")
        threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 颜色相似度阈值
        ttk.Label(threshold_frame, text="颜色相似度阈值:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.color_sim_var = tk.DoubleVar(value=0.8)
        ttk.Scale(threshold_frame, from_=0.0, to=1.0, variable=self.color_sim_var, 
                 orient=tk.HORIZONTAL).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(threshold_frame, textvariable=self.color_sim_var).grid(row=0, column=2, padx=5, pady=5)
        
        # 结构相似度阈值
        ttk.Label(threshold_frame, text="结构相似度阈值:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.ssim_var = tk.DoubleVar(value=0.7)
        ttk.Scale(threshold_frame, from_=0.0, to=1.0, variable=self.ssim_var, 
                 orient=tk.HORIZONTAL).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(threshold_frame, textvariable=self.ssim_var).grid(row=1, column=2, padx=5, pady=5)
        
        # 颜色差异阈值
        ttk.Label(threshold_frame, text="颜色差异阈值:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.color_diff_var = tk.DoubleVar(value=30.0)
        ttk.Scale(threshold_frame, from_=0.0, to=100.0, variable=self.color_diff_var, 
                 orient=tk.HORIZONTAL).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(threshold_frame, textvariable=self.color_diff_var).grid(row=2, column=2, padx=5, pady=5)
        
        # 保存/加载设置
        settings_control_frame = ttk.Frame(threshold_frame)
        settings_control_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=10)
        
        ttk.Button(settings_control_frame, text="应用设置", 
                  command=self.apply_threshold_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_control_frame, text="保存设置", 
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_control_frame, text="加载设置", 
                  command=self.load_settings).pack(side=tk.LEFT, padx=5)
        
        # 其他设置
        other_frame = ttk.LabelFrame(settings_frame, text="其他设置")
        other_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 截图间隔
        ttk.Label(other_frame, text="截图间隔(秒):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.capture_interval_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(other_frame, from_=0.1, to=10.0, increment=0.1, 
                   textvariable=self.capture_interval_var).grid(row=0, column=1, padx=5, pady=5)
    
    # 控制面板方法
    def quick_load_save(self):
        """快速读取存档"""
        success = self.app.keyboard_controller.quick_load_save()
        self.log_message(f"快速读取存档: {'成功' if success else '失败'}")
    
    def confirm_action(self):
        """确认操作"""
        success = self.app.keyboard_controller.confirm_action()
        self.log_message(f"确认操作: {'成功' if success else '失败'}")
    
    def start_auto_hunt(self):
        """开始自动刷闪"""
        # 从界面获取时间配置
        try:
            config = {
                'initial_delay': float(self.initial_delay_var.get()),
                'f1_delay': float(self.f1_delay_var.get()),
                'first_a_delay': float(self.first_a_delay_var.get()),
                'analysis_delay': float(self.analysis_delay_var.get()),
                'retry_count': int(self.retry_count_var.get()),
                'retry_interval': float(self.retry_interval_var.get()),
            }
        except ValueError:
            messagebox.showerror("错误", "配置格式错误，请检查输入值")
            return
        
        # 验证时间配置
        if config['initial_delay'] < 1.0 or config['initial_delay'] > 30.0:
            messagebox.showerror("错误", "初始延迟必须在1.0-30.0秒之间")
            return
        if config['f1_delay'] < 0.1 or config['f1_delay'] > 5.0:
            messagebox.showerror("错误", "F1后延迟必须在0.1-5.0秒之间")
            return
        if config['first_a_delay'] < 0.1 or config['first_a_delay'] > 5.0:
            messagebox.showerror("错误", "第一次A键后延迟必须在0.1-5.0秒之间")
            return
        if config['analysis_delay'] < 1.0 or config['analysis_delay'] > 20.0:
            messagebox.showerror("错误", "分析前延迟必须在1.0-20.0秒之间")
            return
        if config['retry_count'] < 0 or config['retry_count'] > 5:
            messagebox.showerror("错误", "重试次数必须在0-5次之间")
            return
        if config['retry_interval'] < 0.5 or config['retry_interval'] > 10.0:
            messagebox.showerror("错误", "重试间隔必须在0.5-10.0秒之间")
            return
        
        # 设置参考图像
        reference_list = self.app.image_analyzer.get_reference_list()
        if reference_list:
            config['reference_image'] = reference_list[0]
        
        self.app.auto_hunter.set_config(config)
        self.log_message(f"配置已更新: 初始延迟={config['initial_delay']}s, F1后延迟={config['f1_delay']}s, 第一次A键后延迟={config['first_a_delay']}s, 分析前延迟={config['analysis_delay']}s, 重试次数={config['retry_count']}次, 重试间隔={config['retry_interval']}s")
        
        # 设置回调函数
        self.app.auto_hunter.set_callbacks(
            on_hunt_start=self.on_hunt_start,
            on_hunt_stop=self.on_hunt_stop,
            on_hunt_progress=self.on_hunt_progress,
            on_hunt_result=self.on_hunt_result,
            on_countdown=self.start_countdown
        )
        
        # 开始自动刷闪
        if self.app.auto_hunter.start_hunting():
            self.log_message("开始自动刷闪")
        else:
            self.log_message("自动刷闪启动失败")
    
    def stop_auto_hunt(self):
        """停止自动刷闪"""
        self.app.auto_hunter.stop_hunting()
        self.stop_countdown()
        self.log_message("停止自动刷闪")
    
    def reset_hunt_count(self):
        """重置刷闪计数"""
        self.app.auto_hunter.reset_counter()
        self.hunt_count_var.set("0")
        self.log_message("刷闪计数已重置")
    
    def save_time_config(self):
        """保存时间配置"""
        try:
            config = {
                'initial_delay': float(self.initial_delay_var.get()),
                'f1_delay': float(self.f1_delay_var.get()),
                'first_a_delay': float(self.first_a_delay_var.get()),
                'analysis_delay': float(self.analysis_delay_var.get()),
                'retry_count': int(self.retry_count_var.get()),
                'retry_interval': float(self.retry_interval_var.get()),
            }
            
            file_path = filedialog.asksaveasfilename(
                title="保存时间配置",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir="configs"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.log_message(f"时间配置已保存: {file_path}")
                
        except ValueError:
            messagebox.showerror("错误", "时间配置格式错误，请检查输入值")
        except Exception as e:
            messagebox.showerror("错误", f"保存时间配置失败: {e}")
            self.log_message(f"保存时间配置失败: {e}")
    
    def load_time_config(self):
        """加载时间配置"""
        try:
            file_path = filedialog.askopenfilename(
                title="加载时间配置",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir="configs"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 更新界面显示
                self.initial_delay_var.set(str(config.get('initial_delay', 5.0)))
                self.f1_delay_var.set(str(config.get('f1_delay', 0.5)))
                self.first_a_delay_var.set(str(config.get('first_a_delay', 0.8)))
                self.analysis_delay_var.set(str(config.get('analysis_delay', 4.0)))
                self.retry_count_var.set(str(config.get('retry_count', 2)))
                self.retry_interval_var.set(str(config.get('retry_interval', 2.0)))
                
                self.log_message(f"时间配置已加载: {file_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载时间配置失败: {e}")
            self.log_message(f"加载时间配置失败: {e}")
    
    def reset_time_config(self):
        """重置为默认时间配置"""
        self.initial_delay_var.set("5.0")
        self.f1_delay_var.set("0.5")
        self.first_a_delay_var.set("0.8")
        self.analysis_delay_var.set("4.0")
        self.retry_count_var.set("2")
        self.retry_interval_var.set("2.0")
        self.log_message("时间配置已重置为默认值")
    
    def load_preset_config(self, preset_name):
        """加载预设配置"""
        try:
            config_file = f"configs/{preset_name}_time_config.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新界面显示
            self.initial_delay_var.set(str(config.get('initial_delay', 5.0)))
            self.f1_delay_var.set(str(config.get('f1_delay', 0.5)))
            self.first_a_delay_var.set(str(config.get('first_a_delay', 0.8)))
            self.analysis_delay_var.set(str(config.get('analysis_delay', 4.0)))
            self.retry_count_var.set(str(config.get('retry_count', 2)))
            self.retry_interval_var.set(str(config.get('retry_interval', 2.0)))
            
            description = config.get('description', '')
            self.log_message(f"已加载{preset_name}预设配置: {description}")
            
        except FileNotFoundError:
            messagebox.showerror("错误", f"预设配置文件不存在: {config_file}")
        except Exception as e:
            messagebox.showerror("错误", f"加载预设配置失败: {e}")
            self.log_message(f"加载预设配置失败: {e}")
    
    def on_hunt_start(self):
        """自动刷闪开始回调"""
        self.hunt_status_var.set("运行中...")
        self.hunt_status_label.configure(foreground='orange')
    
    def on_hunt_stop(self, final_count):
        """自动刷闪停止回调"""
        self.hunt_status_var.set("已停止")
        self.hunt_status_label.configure(foreground='red')
        self.hunt_count_var.set(str(final_count))
        self.log_message(f"自动刷闪已停止，总次数: {final_count}")
    
    def on_hunt_progress(self, total_count, current_success, message=None):
        """自动刷闪进度回调"""
        self.hunt_count_var.set(str(total_count))
        if message:
            self.log_message(message)
    
    def on_hunt_result(self, result):
        """自动刷闪结果回调"""
        failed_regions = result.get('failed_regions', [])
        success_count = result.get('success_count', 0)
        attempt_count = result.get('attempt_count', 1)
        
        if failed_regions:
            self.log_message(f"检测到闪光！失败区域: {', '.join(failed_regions)} (经过{attempt_count}次分析)")
        else:
            self.log_message(f"本轮成功: {success_count} 个区域 (第{attempt_count}次分析)")
    
    def start_countdown(self, seconds, action):
        """开始倒计时"""
        self.stop_countdown()  # 停止之前的倒计时
        self.countdown_total = seconds
        self.countdown_remaining = seconds
        self.countdown_action = action
        self.countdown_progress['maximum'] = seconds
        self.countdown_progress['value'] = 0
        self._update_countdown()
    
    def stop_countdown(self):
        """停止倒计时"""
        if self.countdown_timer:
            self.root.after_cancel(self.countdown_timer)
            self.countdown_timer = None
        self.countdown_var.set("等待开始...")
        self.countdown_progress['value'] = 0
    
    def _update_countdown(self):
        """更新倒计时显示"""
        if self.countdown_remaining > 0:
            self.countdown_var.set(f"{self.countdown_remaining}秒后: {self.countdown_action}")
            self.countdown_progress['value'] = self.countdown_total - self.countdown_remaining
            self.countdown_remaining -= 1
            self.countdown_timer = self.root.after(1000, self._update_countdown)
        else:
            self.countdown_var.set(f"正在执行: {self.countdown_action}")
            self.countdown_progress['value'] = self.countdown_total
    
    def _setup_input_validation(self):
        """设置输入框验证"""
        # 验证函数
        def validate_float(value, min_val, max_val):
            try:
                val = float(value)
                return min_val <= val <= max_val
            except ValueError:
                return False
        
        # 为每个输入框添加验证
        self.initial_delay_var.trace('w', lambda *args: self._validate_input(
            self.initial_delay_var, 1.0, 30.0, "初始延迟"))
        self.f1_delay_var.trace('w', lambda *args: self._validate_input(
            self.f1_delay_var, 0.1, 5.0, "F1后延迟"))
        self.first_a_delay_var.trace('w', lambda *args: self._validate_input(
            self.first_a_delay_var, 0.1, 5.0, "第一次A键后延迟"))
        self.analysis_delay_var.trace('w', lambda *args: self._validate_input(
            self.analysis_delay_var, 1.0, 20.0, "分析前延迟"))
        self.retry_count_var.trace('w', lambda *args: self._validate_input(
            self.retry_count_var, 0, 5, "重试次数", is_int=True))
        self.retry_interval_var.trace('w', lambda *args: self._validate_input(
            self.retry_interval_var, 0.5, 10.0, "重试间隔"))
    
    def _validate_input(self, var, min_val, max_val, name, is_int=False):
        """验证输入值"""
        try:
            value = var.get()
            if not value:  # 空值允许
                return
            
            if is_int:
                val = int(value)
            else:
                val = float(value)
            
            if not (min_val <= val <= max_val):
                # 值超出范围，显示警告但不阻止输入
                self.log_message(f"警告: {name}值 {val} 超出范围 ({min_val}-{max_val})")
                
        except ValueError:
            # 值格式错误，显示警告但不阻止输入
            self.log_message(f"警告: {name}值格式错误，请输入有效数字")
    
    def batch_import_config(self):
        """批量导入配置"""
        config_name = self.import_name_var.get().strip()
        if not config_name:
            self.import_status_var.set("请输入配置名称")
            return
        
        config_dir = f"configs/{config_name}"
        if not os.path.exists(config_dir):
            self.import_status_var.set(f"配置目录不存在: {config_dir}")
            return
        
        try:
            imported_items = []
            
            # 1. 导入参考图像
            image_path = os.path.join(config_dir, "image.png")
            if os.path.exists(image_path):
                # 复制到参考图像目录，使用英文文件名
                ref_image_path = os.path.join("configs", f"{config_name}_reference.png")
                import shutil
                shutil.copy2(image_path, ref_image_path)
                
                # 加载参考图像，使用英文名称
                self.app.image_analyzer.load_reference_image(f"{config_name}_reference", ref_image_path)
                imported_items.append("参考图像")
            
            # 2. 导入截图位置
            screenshot_path = os.path.join(config_dir, "screenshootposition.json")
            if os.path.exists(screenshot_path):
                with open(screenshot_path, 'r', encoding='utf-8') as f:
                    screenshot_config = json.load(f)
                
                # 清除现有区域
                self.app.screenshot_manager.clear_regions()
                
                # 添加新区域
                for region_data in screenshot_config.get('regions', []):
                    if region_data.get('enabled', True):
                        region = region_data['region']
                        name = region_data['name']
                        self.app.screenshot_manager.add_region(name, region[0], region[1], region[2], region[3])
                
                imported_items.append("截图位置")
            
            # 3. 导入定时设置
            timer_path = os.path.join(config_dir, "timer.json")
            if os.path.exists(timer_path):
                with open(timer_path, 'r', encoding='utf-8') as f:
                    timer_config = json.load(f)
                
                # 更新界面显示
                self.initial_delay_var.set(str(timer_config.get('initial_delay', 5.0)))
                self.f1_delay_var.set(str(timer_config.get('f1_delay', 0.5)))
                self.first_a_delay_var.set(str(timer_config.get('first_a_delay', 0.8)))
                self.analysis_delay_var.set(str(timer_config.get('analysis_delay', 4.0)))
                self.retry_count_var.set(str(timer_config.get('retry_count', 2)))
                self.retry_interval_var.set(str(timer_config.get('retry_interval', 2.0)))
                
                imported_items.append("定时设置")
            
            # 4. 导入阈值设置
            threshold_path = os.path.join(config_dir, "threshold.json")
            if os.path.exists(threshold_path):
                with open(threshold_path, 'r', encoding='utf-8') as f:
                    threshold_config = json.load(f)
                
                # 应用阈值设置
                self.app.image_analyzer.set_color_similarity_threshold(threshold_config.get('color_similarity', 0.8))
                self.app.image_analyzer.set_ssim_threshold(threshold_config.get('ssim_threshold', 0.3))
                self.app.image_analyzer.set_color_difference_threshold(threshold_config.get('color_difference', 30.0))
                
                imported_items.append("阈值设置")
            
            # 更新状态显示
            if imported_items:
                self.import_status_var.set(f"成功导入: {', '.join(imported_items)}")
                self.log_message(f"批量导入配置 '{config_name}' 成功: {', '.join(imported_items)}")
            else:
                self.import_status_var.set("未找到可导入的配置文件")
                self.log_message(f"配置目录 '{config_dir}' 中未找到可导入的配置文件")
                
        except Exception as e:
            self.import_status_var.set(f"导入失败: {e}")
            self.log_message(f"批量导入配置失败: {e}")
    
    
    # 截图管理方法
    def add_screenshot_region(self):
        """添加截图区域"""
        def on_regions_selected(regions):
            self.app.screenshot_manager.add_regions_from_selector(regions)
            self.update_region_list()
            self.log_message(f"添加了 {len(regions)} 个截图区域")
        
        # 打开完整屏幕区域选择器
        self.app.screenshot_manager.open_region_selector(self.root, on_regions_selected)
    
    def clear_screenshot_regions(self):
        """清除所有截图区域"""
        if messagebox.askyesno("确认", "确定要清除所有截图区域吗？"):
            self.app.screenshot_manager.clear_regions()
            self.update_region_list()
            self.log_message("清除所有截图区域")
    
    def update_region_list(self):
        """更新区域列表显示"""
        # 清空现有项目
        for item in self.region_tree.get_children():
            self.region_tree.delete(item)
        
        # 添加区域信息
        for region_info in self.app.screenshot_manager.get_region_list():
            status = "启用" if region_info['enabled'] else "禁用"
            self.region_tree.insert('', 'end', values=(
                region_info['name'],
                str(region_info['region']),
                status
            ))
    
    def toggle_region_status(self, event=None):
        """切换区域状态"""
        selection = self.region_tree.selection()
        if selection:
            item = self.region_tree.item(selection[0])
            index = self.region_tree.index(selection[0])
            self.app.screenshot_manager.toggle_region(index)
            self.update_region_list()
    
    def delete_region(self):
        """删除选中的区域"""
        selection = self.region_tree.selection()
        if selection:
            index = self.region_tree.index(selection[0])
            region_name = self.app.screenshot_manager.screenshot_regions[index]['name']
            if messagebox.askyesno("确认", f"确定要删除区域 '{region_name}' 吗？"):
                self.app.screenshot_manager.remove_region(index)
                self.update_region_list()
                self.log_message(f"删除区域: {region_name}")
    
    def show_region_menu(self, event):
        """显示区域右键菜单"""
        selection = self.region_tree.selection()
        if selection:
            self.region_menu.post(event.x_root, event.y_root)
    
    def start_continuous_screenshot(self):
        """开始连续截图"""
        if not self.app.screenshot_manager.screenshot_regions:
            messagebox.showwarning("警告", "请先添加截图区域")
            return
        
        interval = self.capture_interval_var.get()
        auto_save = messagebox.askyesno("自动保存", "是否自动保存截图？")
        
        self.app.screenshot_manager.start_scheduled_capture(
            interval, 
            self.on_screenshot_captured, 
            auto_save
        )
        self.log_message(f"开始定时截图，间隔: {interval}秒，自动保存: {auto_save}")
    
    def stop_continuous_screenshot(self):
        """停止连续截图"""
        self.app.screenshot_manager.stop_scheduled_capture()
        self.log_message("停止定时截图")
    
    def on_screenshot_captured(self, results):
        """截图完成回调"""
        self.log_message(f"完成 {len(results)} 个区域的截图")
        # 这里可以添加截图后的处理逻辑
    
    def manual_capture(self):
        """手动截图"""
        if not self.app.screenshot_manager.screenshot_regions:
            messagebox.showwarning("警告", "请先添加截图区域")
            return
        
        results = self.app.screenshot_manager.capture_all_regions()
        if results:
            # 询问是否保存
            if messagebox.askyesno("保存截图", f"成功截取了 {len(results)} 个区域，是否保存？"):
                saved_files = self.app.screenshot_manager.save_all_screenshots(results)
                self.log_message(f"手动截图已保存 {len(saved_files)} 个文件")
        else:
            self.log_message("手动截图失败")
    
    def save_regions_config(self):
        """保存区域配置"""
        if not self.app.screenshot_manager.screenshot_regions:
            messagebox.showwarning("警告", "没有区域配置可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存区域配置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            self.app.screenshot_manager.save_regions_config(file_path)
            self.log_message(f"区域配置已保存: {file_path}")
    
    def load_regions_config(self):
        """加载区域配置"""
        file_path = filedialog.askopenfilename(
            title="加载区域配置",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            self.app.screenshot_manager.load_regions_config(file_path)
            self.update_region_list()
            self.log_message(f"区域配置已加载: {file_path}")
    
    # 图像分析方法
    def load_reference_image(self):
        """加载参考图像"""
        file_path = filedialog.askopenfilename(
            title="选择参考图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            name = f"参考图像_{len(self.app.image_analyzer.get_reference_list()) + 1}"
            success = self.app.image_analyzer.load_reference_image(name, file_path)
            if success:
                self.update_reference_list()
                self.log_message(f"加载参考图像: {name}")
            else:
                messagebox.showerror("错误", "加载参考图像失败")
    
    def clear_reference_images(self):
        """清除所有参考图像"""
        if messagebox.askyesno("确认", "确定要清除所有参考图像吗？"):
            self.app.image_analyzer.clear_references()
            self.update_reference_list()
            self.log_message("清除所有参考图像")
    
    def update_reference_list(self):
        """更新参考图像列表"""
        self.reference_listbox.delete(0, tk.END)
        for name in self.app.image_analyzer.get_reference_list():
            self.reference_listbox.insert(tk.END, name)
    
    def start_analysis(self):
        """开始分析"""
        if not self.app.image_analyzer.get_reference_list():
            messagebox.showwarning("警告", "请先加载参考图像")
            return
        
        if not self.app.screenshot_manager.screenshot_regions:
            messagebox.showwarning("警告", "请先添加截图区域")
            return
        
        # 先截图，然后分析
        self.log_message("开始图像分析...")
        results = self.app.screenshot_manager.capture_all_regions()
        
        if not results:
            self.log_message("截图失败，无法进行分析")
            return
        
        # 获取第一个参考图像进行分析
        reference_name = self.app.image_analyzer.get_reference_list()[0]
        
        # 分析每个截图
        analysis_results = []
        for result in results:
            analysis = self.app.image_analyzer.analyze_image(result['image'], reference_name)
            analysis['region_name'] = result['name']
            analysis_results.append(analysis)
        
        # 显示分析结果
        self.display_analysis_results(analysis_results)
        self.log_message(f"完成 {len(analysis_results)} 个区域的分析")
    
    def stop_analysis(self):
        """停止分析"""
        self.log_message("停止图像分析")
        # 这里可以添加停止分析逻辑
    
    def display_analysis_results(self, results):
        """显示分析结果"""
        self.result_text.delete(1.0, tk.END)
        
        for result in results:
            region_name = result.get('region_name', '未知区域')
            is_match = result.get('is_match', False)
            color_sim = result.get('color_similarity', 0)
            ssim = result.get('structural_similarity', 0)
            color_diff = result.get('color_difference', 0)
            overall_score = result.get('overall_score', 0)
            
            status = "✓ 匹配" if is_match else "✗ 不匹配"
            
            result_text = f"""
区域: {region_name}
状态: {status}
颜色相似度: {color_sim:.3f}
结构相似度: {ssim:.3f}
颜色差异: {color_diff:.1f}
综合评分: {overall_score:.3f}
{'='*50}
"""
            self.result_text.insert(tk.END, result_text)
        
        # 滚动到顶部
        self.result_text.see(1.0)
    
    # 设置方法
    def apply_threshold_settings(self):
        """应用阈值设置"""
        self.app.image_analyzer.set_threshold('color_similarity', self.color_sim_var.get())
        self.app.image_analyzer.set_threshold('ssim_threshold', self.ssim_var.get())
        self.app.image_analyzer.set_threshold('color_difference', self.color_diff_var.get())
        self.log_message("应用阈值设置")
    
    def save_settings(self):
        """保存设置"""
        file_path = filedialog.asksaveasfilename(
            title="保存设置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            self.app.image_analyzer.save_thresholds(file_path)
            self.log_message(f"设置已保存: {file_path}")
    
    def load_settings(self):
        """加载设置"""
        file_path = filedialog.askopenfilename(
            title="加载设置",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            self.app.image_analyzer.load_thresholds(file_path)
            # 更新界面显示
            thresholds = self.app.image_analyzer.get_thresholds()
            self.color_sim_var.set(thresholds['color_similarity'])
            self.ssim_var.set(thresholds['ssim_threshold'])
            self.color_diff_var.set(thresholds['color_difference'])
            self.log_message(f"设置已加载: {file_path}")
    
    # 通用方法
    def log_message(self, message: str):
        """记录日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
        
        self.logger.info(message)
    
    def on_closing(self):
        """程序关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            # 停止所有运行中的任务
            self.app.screenshot_manager.stop_scheduled_capture()
            self.root.destroy()
