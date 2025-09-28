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
import pandas as pd
from datetime import datetime

from .image_analyzer import ImageAnalyzer
from .probability_calculator import ProbabilityCalculator

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
        
        # 概率计算器
        self.probability_calculator = ProbabilityCalculator()
        
        # 概率相关变量
        self.generation_var = tk.StringVar(value="6")
        self.judgment_count_var = tk.StringVar(value="1")
        self.current_title_var = tk.StringVar(value="平平无奇")
        self.current_probability_var = tk.StringVar(value="0.00%")
        
        # 设置窗口属性
        self.root.title("Shining Hunter - 闪光猎手")
        self.root.geometry("1000x960")  # 800 * 1.2 = 960
        self.root.minsize(800, 720)     # 600 * 1.2 = 720
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口图标
        try:
            self.root.iconbitmap('configs/icons/app_icon.ico')
        except:
            # 如果ICO文件不存在，尝试使用PNG
            try:
                from PIL import Image, ImageTk
                icon_image = Image.open('configs/icons/app_icon.png')
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
            except:
                # 如果图标文件都不存在，使用默认图标
                pass
        
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
        
        # 定义现代化颜色 - 更现代的配色方案
        self.colors = {
            'primary': '#2563EB',      # 主色调 - 现代蓝
            'secondary': '#7C3AED',    # 次要色调 - 现代紫
            'success': '#059669',      # 成功色 - 现代绿
            'warning': '#DC2626',      # 警告色 - 现代红
            'info': '#0891B2',         # 信息色 - 现代青
            'light': '#F8FAFC',        # 浅色背景
            'dark': '#1E293B',         # 深色文字
            'border': '#E2E8F0',       # 边框色
            'surface': '#FFFFFF',      # 表面色
            'accent': '#F59E0B'        # 强调色 - 现代橙
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
        
        # 配置按钮样式 - 更现代化的设计
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(12, 6))
        style.map('Modern.TButton',
                  background=[('active', self.colors['secondary']),
                            ('pressed', self.colors['dark'])])
        
        # 配置成功按钮样式
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(12, 6))
        style.map('Success.TButton',
                  background=[('active', '#047857'),
                            ('pressed', '#065F46')])
        
        # 配置警告按钮样式
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(12, 6))
        style.map('Warning.TButton',
                  background=[('active', '#B91C1C'),
                            ('pressed', '#991B1B')])
        
        # 配置信息按钮样式
        style.configure('Info.TButton',
                       background=self.colors['info'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(12, 6))
        style.map('Info.TButton',
                  background=[('active', '#0E7490'),
                            ('pressed', '#155E75')])
        
        # 配置强调按钮样式
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(12, 6))
        style.map('Accent.TButton',
                  background=[('active', '#D97706'),
                            ('pressed', '#B45309')])
        
        # 配置进度条样式
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['border'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
        # 配置输入框样式 - 更现代化
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['surface'],
                       borderwidth=1,
                       relief='solid',
                       insertcolor=self.colors['primary'],
                       font=('Segoe UI', 9))
        style.map('Modern.TEntry',
                  focuscolor=[('!focus', self.colors['border']),
                            ('focus', self.colors['primary'])],
                  bordercolor=[('!focus', self.colors['border']),
                             ('focus', self.colors['primary'])])
        
        # 配置下拉框样式
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['surface'],
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9))
        style.map('Modern.TCombobox',
                  focuscolor=[('!focus', self.colors['border']),
                            ('focus', self.colors['primary'])],
                  bordercolor=[('!focus', self.colors['border']),
                             ('focus', self.colors['primary'])])
        
        # 配置标签样式
        style.configure('Modern.TLabel',
                       background=self.colors['light'],
                       foreground=self.colors['dark'],
                       font=('Segoe UI', 9))
        
        # 配置强调标签样式
        style.configure('Accent.TLabel',
                       background=self.colors['light'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 9, 'bold'))
    
    def create_interface(self):
        """创建主界面"""
        self.root.title("Shining Hunter - 闪光猎手")
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
        
        # 重置按钮
        ttk.Button(keyboard_frame, text="Ctrl+R - 重置",
                  command=self.reset_action).pack(side=tk.LEFT, padx=5, pady=5)
        
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
        
        ttk.Button(control_buttons_frame, text="暂停刷闪", 
                  command=self.pause_auto_hunt, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_buttons_frame, text="停止自动刷闪", 
                  command=self.stop_auto_hunt, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        
        # 文件夹导入功能
        folder_import_frame = ttk.LabelFrame(auto_frame, text="选择文件夹导入(支持多图片)", style='Modern.TLabelframe')
        folder_import_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 第一行：选择文件夹导入按钮和路径显示
        import_control_frame = ttk.Frame(folder_import_frame)
        import_control_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(import_control_frame, text="选择文件夹导入", 
                  command=self.folder_import_config, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        self.folder_path_var = tk.StringVar(value="未选择文件夹")
        folder_path_label = ttk.Label(import_control_frame, textvariable=self.folder_path_var, 
                                     style='Modern.TLabel')
        folder_path_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 第二行：提示信息
        help_label = ttk.Label(folder_import_frame, 
                              text="💡 提示: 文件夹导入会自动导入文件夹下的所有图片文件作为参考图像", 
                              style='Info.TLabel')
        help_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 第三行：导入状态显示
        self.import_status_var = tk.StringVar(value="请选择文件夹导入配置")
        import_status_label = ttk.Label(folder_import_frame, textvariable=self.import_status_var, 
                                      foreground='blue', font=('Arial', 9))
        import_status_label.pack(fill=tk.X, padx=5, pady=2)
        import_status_label.pack(pady=2)
        
        # 时间轴和分析重试配置按钮
        config_button_frame = ttk.Frame(auto_frame)
        config_button_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(config_button_frame, text="⚙️ 时间轴配置 & 分析重试配置", 
                  command=self.show_config_dialog, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        # 初始化默认时间轴（稍后在status_text创建后初始化）
        self.timeline_actions = []
        self.is_paused = False  # 是否处于暂停状态
        
        # 初始化重试配置变量
        self.retry_count_var = tk.StringVar(value="2")
        self.retry_interval_var = tk.StringVar(value="2.0")
        
        # 自定义键位设置
        key_config_frame = ttk.LabelFrame(auto_frame, text="自定义键位设置", style='Modern.TLabelframe')
        key_config_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 键位配置网格
        key_grid_frame = ttk.Frame(key_config_frame)
        key_grid_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 重置键
        ttk.Label(key_grid_frame, text="重置键:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.reset_key_var = tk.StringVar(value="ctrl+r")
        reset_key_entry = ttk.Entry(key_grid_frame, textvariable=self.reset_key_var, width=8, style='Modern.TEntry')
        reset_key_entry.grid(row=0, column=1, padx=2)
        
        # 快速读取键
        ttk.Label(key_grid_frame, text="快速读取键:").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.quick_load_key_var = tk.StringVar(value="f1")
        quick_load_key_entry = ttk.Entry(key_grid_frame, textvariable=self.quick_load_key_var, width=5, style='Modern.TEntry')
        quick_load_key_entry.grid(row=0, column=3, padx=2)
        
        # 确认键
        ttk.Label(key_grid_frame, text="确认键:").grid(row=0, column=4, sticky=tk.W, padx=2)
        self.confirm_key_var = tk.StringVar(value="x")
        confirm_key_entry = ttk.Entry(key_grid_frame, textvariable=self.confirm_key_var, width=5, style='Modern.TEntry')
        confirm_key_entry.grid(row=0, column=5, padx=2)
        
        # 应用键位设置按钮
        ttk.Button(key_grid_frame, text="应用键位设置", 
                  command=self.apply_key_settings, style='Modern.TButton').grid(row=1, column=0, columnspan=6, pady=5)
        
        
        # 概率统计配置
        probability_config_frame = ttk.LabelFrame(auto_frame, text="概率统计配置", style='Modern.TLabelframe')
        probability_config_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 概率配置网格
        prob_config_grid_frame = ttk.Frame(probability_config_frame)
        prob_config_grid_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 世代选择
        ttk.Label(prob_config_grid_frame, text="世代:").grid(row=0, column=0, sticky=tk.W, padx=2)
        generation_combo = ttk.Combobox(prob_config_grid_frame, textvariable=self.generation_var, 
                                       values=self.probability_calculator.get_available_generations(),
                                       width=8, state='readonly', style='Modern.TCombobox')
        generation_combo.grid(row=0, column=1, padx=2)
        generation_combo.bind('<<ComboboxSelected>>', self._update_probability_display)
        
        # 判定数输入
        ttk.Label(prob_config_grid_frame, text="判定数:").grid(row=0, column=2, sticky=tk.W, padx=2)
        judgment_entry = ttk.Entry(prob_config_grid_frame, textvariable=self.judgment_count_var, 
                                  width=8, style='Modern.TEntry')
        judgment_entry.grid(row=0, column=3, padx=2)
        judgment_entry.bind('<KeyRelease>', self._update_probability_display)
        
        # 累积概率显示
        ttk.Label(prob_config_grid_frame, text="累积概率:", style='Modern.TLabel').grid(row=0, column=4, sticky=tk.W, padx=2)
        prob_label = ttk.Label(prob_config_grid_frame, textvariable=self.current_probability_var, 
                              style='Accent.TLabel')
        prob_label.grid(row=0, column=5, padx=2)
        
        # 概率配置管理按钮
        prob_buttons_frame = ttk.Frame(probability_config_frame)
        prob_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(prob_buttons_frame, text="保存概率配置", 
                  command=self.save_probability_config, style='Info.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(prob_buttons_frame, text="加载概率配置", 
                  command=self.load_probability_config, style='Info.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(prob_buttons_frame, text="重置概率配置", 
                  command=self.reset_probability_config, style='Warning.TButton').pack(side=tk.LEFT, padx=2)
        
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
        
        # 初始化概率显示
        self._update_probability_display()
        
        # 状态显示
        status_frame = ttk.LabelFrame(control_frame, text="状态信息")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = tk.Text(status_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始化默认时间轴
        self.reset_timeline_default()
    
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
        
        # 截图清理控制
        cleanup_frame = ttk.LabelFrame(screenshot_frame, text="截图清理")
        cleanup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 清理设置
        cleanup_settings_frame = ttk.Frame(cleanup_frame)
        cleanup_settings_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(cleanup_settings_frame, text="保留时间(小时):").pack(side=tk.LEFT)
        self.cleanup_age_var = tk.StringVar(value="24")
        ttk.Entry(cleanup_settings_frame, textvariable=self.cleanup_age_var, width=10).pack(side=tk.LEFT, padx=5)
        
        self.keep_shiny_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cleanup_settings_frame, text="保留闪光图片", 
                        variable=self.keep_shiny_var).pack(side=tk.LEFT, padx=10)
        
        # 清理按钮
        cleanup_button_frame = ttk.Frame(cleanup_frame)
        cleanup_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(cleanup_button_frame, text="立即清理", 
                  command=self.cleanup_screenshots).pack(side=tk.LEFT, padx=5)
        ttk.Button(cleanup_button_frame, text="标记闪光图片", 
                  command=self.mark_shiny_images).pack(side=tk.LEFT, padx=5)
        
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
                 orient=tk.HORIZONTAL, command=self._update_threshold_display).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.color_sim_label = ttk.Label(threshold_frame, text="0.80")
        self.color_sim_label.grid(row=0, column=2, padx=5, pady=5)
        
        # 结构相似度阈值
        ttk.Label(threshold_frame, text="结构相似度阈值:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.ssim_var = tk.DoubleVar(value=0.7)
        ttk.Scale(threshold_frame, from_=0.0, to=1.0, variable=self.ssim_var, 
                 orient=tk.HORIZONTAL, command=self._update_threshold_display).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.ssim_label = ttk.Label(threshold_frame, text="0.70")
        self.ssim_label.grid(row=1, column=2, padx=5, pady=5)
        
        # 颜色差异阈值
        ttk.Label(threshold_frame, text="颜色差异阈值:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.color_diff_var = tk.DoubleVar(value=30.0)
        ttk.Scale(threshold_frame, from_=0.0, to=100.0, variable=self.color_diff_var, 
                 orient=tk.HORIZONTAL, command=self._update_threshold_display).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.color_diff_label = ttk.Label(threshold_frame, text="30.00")
        self.color_diff_label.grid(row=2, column=2, padx=5, pady=5)
        
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
    
    def reset_action(self):
        """重置操作"""
        success = self.app.keyboard_controller.reset_action()
        self.log_message(f"重置操作: {'成功' if success else '失败'}")
    
    def apply_key_settings(self):
        """应用键位设置"""
        try:
            # 获取键位设置
            reset_key = self.reset_key_var.get().strip().lower()
            quick_load_key = self.quick_load_key_var.get().strip().lower()
            confirm_key = self.confirm_key_var.get().strip().lower()
            
            # 验证键位设置
            if not reset_key or not quick_load_key or not confirm_key:
                messagebox.showerror("错误", "所有键位都必须设置")
                return
            
            # 应用键位设置
            self.app.keyboard_controller.set_custom_key('reset', reset_key)
            self.app.keyboard_controller.set_custom_key('quick_load', quick_load_key)
            self.app.keyboard_controller.set_custom_key('confirm', confirm_key)
            
            self.log_message(f"键位设置已应用: 重置={reset_key.upper()}, 快速读取={quick_load_key.upper()}, 确认={confirm_key.upper()}")
            
        except Exception as e:
            messagebox.showerror("错误", f"应用键位设置失败: {e}")
            self.log_message(f"应用键位设置失败: {e}")
    
    def start_auto_hunt(self):
        """开始自动刷闪"""
        # 验证时间轴配置
        if not self.timeline_actions:
            messagebox.showerror("错误", "时间轴配置不能为空")
            return
        
        # 检查是否处于暂停状态
        if self.is_paused:
            # 暂停状态，不清零刷闪次数
            self.log_message("从暂停状态继续刷闪，保持当前刷闪次数")
        else:
            # 非暂停状态，清零刷闪次数
            self.app.auto_hunter.reset_counter()
            self.hunt_count_var.set("0")
            self.log_message("开始新的刷闪，刷闪次数已清零")
        
        # 验证重试配置
        try:
            retry_count = int(self.retry_count_var.get())
            retry_interval = float(self.retry_interval_var.get())
        except ValueError:
            messagebox.showerror("错误", "重试配置格式错误，请检查输入值")
            return
        
        if retry_count < 0 or retry_count > 5:
            messagebox.showerror("错误", "重试次数必须在0-5次之间")
            return
        if retry_interval < 0.5 or retry_interval > 10.0:
            messagebox.showerror("错误", "重试间隔必须在0.5-10.0秒之间")
            return
        
        # 设置配置
        config = {
            'timeline_actions': self.timeline_actions,
            'retry_count': retry_count,
            'retry_interval': retry_interval,
            'reference_image': None
        }
        
        # 设置参考图像
        reference_list = self.app.image_analyzer.get_reference_list()
        if reference_list:
            config['reference_image'] = reference_list[0]
        
        self.app.auto_hunter.set_config(config)
        self.log_message(f"配置已更新: 时间轴动作数={len(self.timeline_actions)}, 重试次数={retry_count}次, 重试间隔={retry_interval}s")
        
        # 设置回调函数
        self.app.auto_hunter.set_callbacks(
            on_hunt_start=self.on_hunt_start,
            on_hunt_stop=self.on_hunt_stop,
            on_hunt_progress=self.on_hunt_progress,
            on_hunt_result=self.on_hunt_result,
            on_countdown=self.start_countdown,
            on_analysis_progress=self.on_analysis_progress
        )
        
        # 开始自动刷闪
        if self.app.auto_hunter.start_hunting():
            # 清除暂停标志
            self.is_paused = False
            self.log_message("开始自动刷闪")
        else:
            self.log_message("自动刷闪启动失败")
    
    def pause_auto_hunt(self):
        """暂停自动刷闪并保存状态"""
        if not self.app.auto_hunter or not self.app.auto_hunter.is_hunting:
            messagebox.showwarning("警告", "当前没有正在进行的自动刷闪")
            return
        
        try:
            # 暂停刷闪
            self.app.auto_hunter.pause_hunting()
            
            # 设置暂停标志
            self.is_paused = True
            
            # 保存当前状态到可导入的文件夹
            self._save_pause_state()
            
            self.log_message("已暂停自动刷闪并保存状态")
            messagebox.showinfo("暂停成功", "已暂停自动刷闪并保存当前状态到可导入的文件夹")
            
        except Exception as e:
            self.logger.error(f"暂停刷闪失败: {e}")
            messagebox.showerror("错误", f"暂停刷闪失败: {e}")
    
    def _save_pause_state(self):
        """保存暂停状态到可导入的文件夹"""
        try:
            import json
            from datetime import datetime
            
            # 创建暂停状态文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pause_dir = f"configs/pause_{timestamp}"
            os.makedirs(pause_dir, exist_ok=True)
            
            # 1. 保存刷闪次数
            hunt_count = int(self.hunt_count_var.get())
            hunt_data = {
                "hunt_count": hunt_count,
                "pause_time": timestamp,
                "description": f"暂停于第{hunt_count}轮刷闪"
            }
            
            with open(os.path.join(pause_dir, "hunt_count.json"), 'w', encoding='utf-8') as f:
                json.dump(hunt_data, f, ensure_ascii=False, indent=2)
            
            # 2. 保存参考图像
            reference_images = self.app.image_analyzer.get_reference_list()
            if reference_images:
                import shutil
                for ref_name in reference_images:
                    ref_data = self.app.image_analyzer.reference_images[ref_name]
                    ref_path = ref_data['path']
                    if os.path.exists(ref_path):
                        # 复制参考图像
                        shutil.copy2(ref_path, os.path.join(pause_dir, f"{ref_name}.png"))
            
            # 3. 保存阈值设置
            thresholds = self.app.image_analyzer.get_thresholds()
            with open(os.path.join(pause_dir, "threshold.json"), 'w', encoding='utf-8') as f:
                json.dump(thresholds, f, ensure_ascii=False, indent=2)
            
            # 4. 保存截图区域
            regions = []
            for region in self.app.screenshot_manager.screenshot_regions:
                regions.append({
                    "name": region['name'],
                    "region": region['region'],
                    "enabled": True
                })
            
            screenshot_config = {"regions": regions}
            with open(os.path.join(pause_dir, "screenshootposition.json"), 'w', encoding='utf-8') as f:
                json.dump(screenshot_config, f, ensure_ascii=False, indent=2)
            
            # 5. 保存时间轴配置
            timeline_config = {
                "timeline_actions": self.timeline_actions,
                "retry_count": int(self.retry_count_var.get()),
                "retry_interval": float(self.retry_interval_var.get())
            }
            with open(os.path.join(pause_dir, "timeline.json"), 'w', encoding='utf-8') as f:
                json.dump(timeline_config, f, ensure_ascii=False, indent=2)
            
            # 6. 保存概率配置
            gen_config = {
                "generation": self.generation_var.get(),
                "judgment_count": int(self.judgment_count_var.get())
            }
            with open(os.path.join(pause_dir, "gen.json"), 'w', encoding='utf-8') as f:
                json.dump(gen_config, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"暂停状态已保存到: {pause_dir}")
            
        except Exception as e:
            self.logger.error(f"保存暂停状态失败: {e}")
            raise e
    
    def stop_auto_hunt(self):
        """停止自动刷闪"""
        self.app.auto_hunter.stop_hunting()
        self.stop_countdown()
        # 清除暂停标志
        self.is_paused = False
        self.log_message("停止自动刷闪")
    
    def reset_hunt_count(self):
        """重置刷闪计数"""
        self.app.auto_hunter.reset_counter()
        self.hunt_count_var.set("0")
        self.log_message("刷闪计数已重置")
    
    
    
    
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
        self._update_probability_display()  # 更新概率显示
        if message:
            self.log_message(message)
    
    def on_analysis_progress(self, analysis_results, attempt):
        """处理实时分析进度"""
        # 更新图像分析页面的结果显示
        self.display_analysis_results(analysis_results)
        self.log_message(f"第{attempt}次分析完成，共{len(analysis_results)}个区域")
    
    def on_hunt_result(self, result):
        """自动刷闪结果回调"""
        failed_regions = result.get('failed_regions', [])
        success_count = result.get('success_count', 0)
        attempt_count = result.get('attempt_count', 1)
        
        if failed_regions:
            # 显示自定义结果对话框
            self._show_shiny_result_dialog(result)
        else:
            self.log_message(f"本轮成功: {success_count} 个区域 (第{attempt_count}次分析)")
    
    def _show_shiny_result_dialog(self, result):
        """显示闪光检测结果对话框"""
        failed_regions = result.get('failed_regions', [])
        success_count = result.get('success_count', 0)
        total_regions = result.get('total_regions', 0)
        attempt_count = result.get('attempt_count', 1)
        failed_images = result.get('failed_images', [])
        
        # 创建结果对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("闪光检测结果")
        dialog.geometry("800x700")  # 增加高度和宽度
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # 添加关闭事件处理，等同于错判
        def on_dialog_close():
            # 停止BGM播放
            self._stop_bgm()
            # 处理为错判
            self._handle_misjudge(dialog, result)
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # 主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果信息
        info_frame = ttk.LabelFrame(main_frame, text="检测结果")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 计算当前称号
        try:
            generation = int(self.generation_var.get())
            judgment_count = int(self.judgment_count_var.get())
            hunt_count = int(self.hunt_count_var.get())
            title, probability = self.probability_calculator.get_title_by_hunt_count(
                generation, hunt_count, judgment_count
            )
        except:
            title = "未知"
            probability = 0.0
        
        info_text = f"""刷闪次数: {self.hunt_count_var.get()}
成功区域: {success_count}/{total_regions}
失败区域: {', '.join(failed_regions)}
分析尝试次数: {attempt_count}
当前称号: {title}
累积概率: {probability:.2f}%

经过多次重试分析，确认检测到闪光宝可梦！"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # 失败图像显示
        if failed_images:
            images_frame = ttk.LabelFrame(main_frame, text="识别失败的图像")
            images_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 创建滚动区域
            canvas = tk.Canvas(images_frame)
            scrollbar = ttk.Scrollbar(images_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 使用网格布局显示失败图像
            cols = 3  # 每行显示3个图像
            for i, (region_name, image_path) in enumerate(failed_images):
                try:
                    # 加载并缩放图像
                    img = Image.open(image_path)
                    img.thumbnail((120, 120), Image.Resampling.LANCZOS)  # 稍微缩小图像
                    photo = ImageTk.PhotoImage(img)
                    
                    # 计算网格位置
                    row = i // cols
                    col = i % cols
                    
                    # 创建图像显示框架
                    img_frame = ttk.Frame(scrollable_frame)
                    img_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    # 区域名称标签
                    name_label = ttk.Label(img_frame, text=f"{region_name}", 
                                         font=('Arial', 9, 'bold'), anchor="center")
                    name_label.pack(pady=(0, 2))
                    
                    # 图像标签
                    img_label = ttk.Label(img_frame, image=photo, anchor="center")
                    img_label.image = photo  # 保持引用
                    img_label.pack()
                    
                except Exception as e:
                    self.logger.error(f"加载失败图像 {image_path} 失败: {e}")
            
            # 配置网格权重，确保每列等宽
            for i in range(cols):
                scrollable_frame.grid_columnconfigure(i, weight=1)
            
            # 如果最后一行没有填满，添加空的占位框架
            total_images = len(failed_images)
            last_row = (total_images - 1) // cols
            last_row_items = total_images % cols
            if last_row_items > 0:  # 最后一行没有填满
                for col in range(last_row_items, cols):
                    empty_frame = ttk.Frame(scrollable_frame)
                    empty_frame.grid(row=last_row, column=col, padx=5, pady=5, sticky="nsew")
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 错判按钮
        misjudge_btn = ttk.Button(button_frame, text="这是错判，继续刷闪", 
                                 command=lambda: self._handle_misjudge(dialog, result),
                                 style='Warning.TButton')
        misjudge_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 确认按钮
        confirm_btn = ttk.Button(button_frame, text="确认闪光，停止刷闪", 
                                command=lambda: self._handle_confirm_shiny(dialog),
                                style='Success.TButton')
        confirm_btn.pack(side=tk.LEFT)
    
    def _handle_misjudge(self, dialog, result):
        """处理错判"""
        # 停止BGM播放
        self._stop_bgm()
        
        failed_regions = result.get('failed_regions', [])
        failed_images = result.get('failed_images', [])
        success_count = result.get('success_count', 0)
        total_regions = result.get('total_regions', 0)
        
        # 关闭当前对话框
        dialog.destroy()
        
        # 如果有失败图像，询问是否加入参考图像
        if failed_images:
            self._ask_add_to_reference(failed_images, result)
        else:
            # 没有失败图像，直接处理错判
            self._process_misjudge_without_images(failed_regions)
    
    def _ask_add_to_reference(self, failed_images, result):
        """询问是否将错判图像加入参考图像"""
        # 创建选择对话框
        choice_dialog = tk.Toplevel(self.root)
        choice_dialog.title("错判处理选择")
        choice_dialog.geometry("600x600")  # 增加高度以显示所有内容
        choice_dialog.attributes('-topmost', True)
        choice_dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(choice_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 说明文本
        info_text = """检测到错判情况，您可以选择：

1. 将错判图像加入参考图像库，提高未来识别准确性
2. 仅处理错判，不修改参考图像库

选择将错判图像加入参考图像库后，这些图像将作为新的参考图像，
帮助系统在未来更好地识别类似情况。"""
        
        ttk.Label(main_frame, text=info_text, justify=tk.LEFT, 
                 font=('Arial', 10)).pack(pady=(0, 20))
        
        # 显示错判图像预览
        if failed_images:
            preview_frame = ttk.LabelFrame(main_frame, text="错判图像预览")
            preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            # 创建滚动区域
            canvas = tk.Canvas(preview_frame)
            scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 显示图像预览
            cols = 3
            for i, (region_name, image_path) in enumerate(failed_images):
                try:
                    # 加载并缩放图像
                    img = Image.open(image_path)
                    img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # 计算网格位置
                    row = i // cols
                    col = i % cols
                    
                    # 创建图像显示框架
                    img_frame = ttk.Frame(scrollable_frame)
                    img_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    # 区域名称标签
                    name_label = ttk.Label(img_frame, text=f"{region_name}", 
                                         font=('Arial', 8), anchor="center")
                    name_label.pack(pady=(0, 2))
                    
                    # 图像标签
                    img_label = ttk.Label(img_frame, image=photo, anchor="center")
                    img_label.image = photo  # 保持引用
                    img_label.pack()
                    
                except Exception as e:
                    self.logger.error(f"加载错判图像 {image_path} 失败: {e}")
            
            # 配置网格权重
            for i in range(cols):
                scrollable_frame.grid_columnconfigure(i, weight=1)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 加入参考图像按钮
        add_btn = ttk.Button(button_frame, text="加入参考图像库", 
                           command=lambda: self._add_misjudge_to_reference(choice_dialog, failed_images, result),
                           style='Success.TButton')
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 仅处理错判按钮
        skip_btn = ttk.Button(button_frame, text="仅处理错判", 
                            command=lambda: self._process_misjudge_without_images(choice_dialog, result),
                            style='Warning.TButton')
        skip_btn.pack(side=tk.LEFT)
    
    def _add_misjudge_to_reference(self, dialog, failed_images, result):
        """将错判图像加入参考图像库"""
        try:
            added_count = 0
            
            for region_name, image_path in failed_images:
                if image_path and os.path.exists(image_path):
                    # 生成参考图像名称（使用英文避免编码问题）
                    timestamp = int(time.time())
                    # 将区域名中的中文字符替换为英文
                    safe_region_name = region_name.replace("区域", "region").replace("第", "attempt").replace("次判断", "judgment")
                    ref_name = f"misjudge_{safe_region_name}_{timestamp}"
                    
                    # 复制图像到configs目录
                    configs_dir = "configs"
                    if not os.path.exists(configs_dir):
                        os.makedirs(configs_dir)
                    
                    # 生成目标路径
                    ref_image_path = os.path.join(configs_dir, f"{ref_name}.png")
                    
                    # 复制图像文件
                    shutil.copy2(image_path, ref_image_path)
                    
                    # 加载为参考图像
                    self.app.image_analyzer.load_reference_image(ref_name, ref_image_path)
                    added_count += 1
            
            # 更新参考图像列表显示
            self.update_reference_list()
            
            # 关闭对话框
            dialog.destroy()
            
            # 处理错判逻辑
            self._process_misjudge_without_images(result)
            
            self.log_message(f"已将{added_count}个错判图像加入参考图像库")
            messagebox.showinfo("成功", f"已将{added_count}个错判图像加入参考图像库")
            
        except Exception as e:
            self.logger.error(f"加入参考图像失败: {e}")
            messagebox.showerror("错误", f"加入参考图像失败: {e}")
            dialog.destroy()
    
    def _process_misjudge_without_images(self, dialog_or_result, result=None):
        """处理错判（不加入参考图像）"""
        if result is None:
            result = dialog_or_result
        else:
            dialog = dialog_or_result
            dialog.destroy()
        
        failed_regions = result.get('failed_regions', [])
        
        # 更新刷闪次数：维持当前次数，加上失败区域数（这些是错判的案例）
        current_count = int(self.hunt_count_var.get())
        failed_count = len(failed_regions)  # 失败区域数量
        new_count = current_count + failed_count
        self.hunt_count_var.set(str(new_count))
        
        # 更新概率显示
        self._update_probability_display()
        
        # 继续自动刷闪
        if hasattr(self.app, 'auto_hunter') and self.app.auto_hunter:
            self.app.auto_hunter.continue_hunting()
        
        self.log_message(f"错判处理：维持刷闪次数 {current_count}，加上错判区域 {failed_count}，继续刷闪")
    
    def _handle_confirm_shiny(self, dialog):
        """确认闪光"""
        # 停止BGM播放
        self._stop_bgm()
        
        # 标记闪光图片并移动到shining文件夹
        try:
            # 获取最新的截图文件
            screenshot_files = self._get_latest_screenshots()
            for file_path in screenshot_files:
                if file_path:
                    self.app.screenshot_manager.mark_as_shiny(file_path)
                    # 移动到shining文件夹
                    self._move_to_shining_folder(file_path)
        except Exception as e:
            self.logger.error(f"处理闪光图片失败: {e}")
        
        # 保存历史记录到Excel
        self._save_shiny_history()
        
        dialog.destroy()
        self.log_message("确认检测到闪光宝可梦，自动刷闪已停止！")
    
    def _move_to_shining_folder(self, file_path):
        """将闪光图片移动到shining文件夹"""
        try:
            import shutil
            from pathlib import Path
            
            # 创建shining文件夹
            shining_dir = Path("screenshots/shining")
            shining_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取文件名
            file_name = Path(file_path).name
            
            # 目标路径
            target_path = shining_dir / file_name
            
            # 如果目标文件已存在，添加时间戳
            if target_path.exists():
                timestamp = int(time.time())
                name_parts = file_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    new_name = f"{file_name}_{timestamp}"
                target_path = shining_dir / new_name
            
            # 移动文件
            shutil.move(file_path, target_path)
            self.log_message(f"闪光图片已移动到: {target_path}")
            
        except Exception as e:
            self.logger.error(f"移动闪光图片失败: {e}")
    
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
                        self.log_message("播放闪光BGM音乐")
                    else:
                        self.log_message(f"BGM音乐文件不存在: {music_path}")
                        
                except Exception as e:
                    self.logger.error(f"播放BGM失败: {e}")
            
            # 在后台线程中播放音乐，避免阻塞UI
            music_thread = threading.Thread(target=play_music, daemon=True)
            music_thread.start()
            
        except ImportError:
            self.log_message("pygame未安装，无法播放BGM音乐")
        except Exception as e:
            self.logger.error(f"播放BGM失败: {e}")
    
    def _stop_bgm(self):
        """停止BGM音乐播放"""
        try:
            import pygame
            
            # 停止音乐播放
            pygame.mixer.music.stop()
            self.log_message("已停止BGM音乐播放")
            
        except ImportError:
            pass  # pygame未安装，忽略
        except Exception as e:
            self.logger.error(f"停止BGM失败: {e}")
    
    def _ask_cleanup_screenshots(self):
        """询问用户是否清理screenshots文件夹"""
        try:
            from pathlib import Path
            
            # 检查screenshots文件夹是否存在
            screenshots_dir = Path("screenshots")
            if not screenshots_dir.exists():
                return
            
            # 统计图片文件数量
            image_files = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
            if len(image_files) == 0:
                return
            
            # 询问用户是否清理
            result = messagebox.askyesno(
                "清理截图文件夹", 
                f"screenshots文件夹中有 {len(image_files)} 个图片文件。\n\n"
                "是否要清理这些图片文件？\n"
                "（闪光图片会被保留在shining文件夹中）"
            )
            
            if result:
                # 执行清理
                self.app.screenshot_manager.cleanup_screenshots(keep_shiny=True, max_age_hours=0)
                self.log_message(f"已清理screenshots文件夹，删除了 {len(image_files)} 个图片文件")
                messagebox.showinfo("清理完成", f"已清理screenshots文件夹，删除了 {len(image_files)} 个图片文件")
            else:
                self.log_message("用户选择不清理screenshots文件夹")
                
        except Exception as e:
            self.logger.error(f"清理提醒失败: {e}")
    
    def show_config_dialog(self):
        """显示时间轴配置和分析重试配置对话框"""
        # 创建配置对话框
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("时间轴配置 & 分析重试配置")
        config_dialog.geometry("880x600")  # 增加宽度以显示所有按钮
        config_dialog.attributes('-topmost', True)
        config_dialog.grab_set()
        
        # 保存原始配置用于关闭时恢复
        original_retry_count = self.retry_count_var.get()
        original_retry_interval = self.retry_interval_var.get()
        original_timeline_actions = self.timeline_actions.copy()
        
        def on_dialog_close():
            # 恢复原始配置
            self.retry_count_var.set(original_retry_count)
            self.retry_interval_var.set(original_retry_interval)
            self.timeline_actions = original_timeline_actions.copy()
            self.update_timeline_display()
            self.log_message("已取消更改")
            config_dialog.destroy()
        
        config_dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # 主框架
        main_frame = ttk.Frame(config_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 时间轴配置区域
        timeline_frame = ttk.LabelFrame(main_frame, text="时间轴配置", style='Modern.TLabelframe')
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 时间轴列表
        timeline_list_frame = ttk.Frame(timeline_frame)
        timeline_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建时间轴Treeview
        timeline_columns = ('序号', '动作', '延迟(秒)', '描述')
        timeline_tree = ttk.Treeview(timeline_list_frame, columns=timeline_columns, show='headings', height=8)
        
        for col in timeline_columns:
            timeline_tree.heading(col, text=col)
            timeline_tree.column(col, width=150)
        
        # 时间轴滚动条
        timeline_scrollbar = ttk.Scrollbar(timeline_list_frame, orient=tk.VERTICAL, command=timeline_tree.yview)
        timeline_tree.configure(yscrollcommand=timeline_scrollbar.set)
        
        timeline_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        timeline_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 时间轴控制按钮
        timeline_control_frame = ttk.Frame(timeline_frame)
        timeline_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(timeline_control_frame, text="添加动作", 
                  command=lambda: self._dialog_add_timeline_action(timeline_tree), style='Success.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="编辑动作", 
                  command=lambda: self._dialog_edit_timeline_action(timeline_tree), style='Info.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="删除动作", 
                  command=lambda: self._dialog_remove_timeline_action(timeline_tree), style='Warning.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="上移", 
                  command=lambda: self._dialog_move_timeline_up(timeline_tree), style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="下移", 
                  command=lambda: self._dialog_move_timeline_down(timeline_tree), style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="重置为默认", 
                  command=lambda: self._dialog_reset_timeline_default(timeline_tree), style='Info.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="导出时间轴", 
                  command=lambda: self._dialog_export_timeline_config(timeline_tree), style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(timeline_control_frame, text="导入时间轴", 
                  command=lambda: self._dialog_import_timeline_config(timeline_tree), style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        # 分析重试配置区域
        retry_frame = ttk.LabelFrame(main_frame, text="分析重试配置", style='Modern.TLabelframe')
        retry_frame.pack(fill=tk.X, padx=5, pady=5)
        
        retry_grid_frame = ttk.Frame(retry_frame)
        retry_grid_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 重试次数
        ttk.Label(retry_grid_frame, text="重试次数:").grid(row=0, column=0, sticky=tk.W, padx=2)
        retry_count_var = tk.StringVar(value=self.retry_count_var.get())
        retry_count_entry = ttk.Entry(retry_grid_frame, textvariable=retry_count_var, width=10, style='Modern.TEntry')
        retry_count_entry.grid(row=0, column=1, padx=2)
        ttk.Label(retry_grid_frame, text="(0-5)").grid(row=0, column=2, sticky=tk.W, padx=2)
        
        # 重试间隔
        ttk.Label(retry_grid_frame, text="重试间隔(秒):").grid(row=0, column=3, sticky=tk.W, padx=2)
        retry_interval_var = tk.StringVar(value=self.retry_interval_var.get())
        retry_interval_entry = ttk.Entry(retry_grid_frame, textvariable=retry_interval_var, width=10, style='Modern.TEntry')
        retry_interval_entry.grid(row=0, column=4, padx=2)
        ttk.Label(retry_grid_frame, text="(0.5-10.0)").grid(row=0, column=5, sticky=tk.W, padx=2)
        
        # 对话框按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        
        def save_and_close():
            # 保存配置
            self.retry_count_var.set(retry_count_var.get())
            self.retry_interval_var.set(retry_interval_var.get())
            # 更新时间轴显示
            self.update_timeline_display()
            self.log_message("配置已保存")
            config_dialog.destroy()
        
        def cancel_changes():
            # 恢复原始配置
            self.retry_count_var.set(original_retry_count)
            self.retry_interval_var.set(original_retry_interval)
            self.timeline_actions = original_timeline_actions.copy()
            self.update_timeline_display()
            self.log_message("已取消更改")
            config_dialog.destroy()
        
        ttk.Button(button_frame, text="保存并关闭", 
                  command=save_and_close, style='Success.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="取消", 
                  command=cancel_changes, style='Warning.TButton').pack(side=tk.RIGHT, padx=5)
        
        # 初始化时间轴显示
        self._dialog_update_timeline_display(timeline_tree)
    
    def _dialog_update_timeline_display(self, timeline_tree):
        """更新对话框中的时间轴显示"""
        # 清空现有项目
        for item in timeline_tree.get_children():
            timeline_tree.delete(item)
        
        # 添加时间轴项目
        for i, action in enumerate(self.timeline_actions):
            timeline_tree.insert('', 'end', values=(
                i + 1,
                action['action'],
                action['delay'],
                action['description']
            ))
    
    def _dialog_add_timeline_action(self, timeline_tree):
        """在对话框中添加时间轴动作"""
        # 创建添加动作对话框
        add_dialog = tk.Toplevel()
        add_dialog.title("添加时间轴动作")
        add_dialog.geometry("400x300")
        add_dialog.attributes('-topmost', True)
        add_dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(add_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 动作类型选择
        ttk.Label(main_frame, text="动作类型:").pack(anchor=tk.W, pady=2)
        action_var = tk.StringVar(value="analysis")
        action_combo = ttk.Combobox(main_frame, textvariable=action_var, 
                                   values=["initial_delay", "reset", "quick_load", "confirm", "analysis"], 
                                   state="readonly", width=20)
        action_combo.pack(fill=tk.X, pady=2)
        
        # 延迟时间
        ttk.Label(main_frame, text="延迟时间(秒):").pack(anchor=tk.W, pady=2)
        delay_var = tk.StringVar(value="1.0")
        delay_entry = ttk.Entry(main_frame, textvariable=delay_var, width=20)
        delay_entry.pack(fill=tk.X, pady=2)
        
        # 描述
        ttk.Label(main_frame, text="描述:").pack(anchor=tk.W, pady=2)
        description_var = tk.StringVar(value="区域分析")
        description_entry = ttk.Entry(main_frame, textvariable=description_var, width=20)
        description_entry.pack(fill=tk.X, pady=2)
        
        # 插入位置
        ttk.Label(main_frame, text="插入位置:").pack(anchor=tk.W, pady=2)
        position_var = tk.StringVar(value="end")
        position_combo = ttk.Combobox(main_frame, textvariable=position_var, 
                                     values=["beginning", "end", "after_selected"], 
                                     state="readonly", width=20)
        position_combo.pack(fill=tk.X, pady=2)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def add_action():
            try:
                delay = float(delay_var.get())
                if delay < 0:
                    messagebox.showerror("错误", "延迟时间不能为负数")
                    return
                
                new_action = {
                    'action': action_var.get(),
                    'delay': delay,
                    'description': description_var.get()
                }
                
                position = position_var.get()
                if position == 'beginning':
                    self.timeline_actions.insert(0, new_action)
                elif position == 'end':
                    self.timeline_actions.append(new_action)
                elif position == 'after_selected':
                    selected = timeline_tree.selection()
                    if selected:
                        index = timeline_tree.index(selected[0])
                        self.timeline_actions.insert(index + 1, new_action)
                    else:
                        self.timeline_actions.append(new_action)
                
                self._dialog_update_timeline_display(timeline_tree)
                add_dialog.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "延迟时间必须是数字")
        
        ttk.Button(button_frame, text="添加", command=add_action, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=add_dialog.destroy, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
    
    def _dialog_edit_timeline_action(self, timeline_tree):
        """在对话框中编辑时间轴动作"""
        selection = timeline_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的动作")
            return
        
        index = timeline_tree.index(selection[0])
        if index >= len(self.timeline_actions):
            messagebox.showerror("错误", "选中的动作不存在")
            return
        
        # 获取当前动作
        current_action = self.timeline_actions[index]
        
        # 创建编辑动作对话框
        edit_dialog = tk.Toplevel()
        edit_dialog.title("编辑时间轴动作")
        edit_dialog.geometry("400x300")
        edit_dialog.attributes('-topmost', True)
        edit_dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(edit_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 动作类型选择
        ttk.Label(main_frame, text="动作类型:").pack(anchor=tk.W, pady=2)
        action_var = tk.StringVar(value=current_action['action'])
        action_combo = ttk.Combobox(main_frame, textvariable=action_var, 
                                   values=["initial_delay", "reset", "quick_load", "confirm", "analysis"], 
                                   state="readonly", width=20)
        action_combo.pack(fill=tk.X, pady=2)
        
        # 延迟时间
        ttk.Label(main_frame, text="延迟时间(秒):").pack(anchor=tk.W, pady=2)
        delay_var = tk.StringVar(value=str(current_action['delay']))
        delay_entry = ttk.Entry(main_frame, textvariable=delay_var, width=20)
        delay_entry.pack(fill=tk.X, pady=2)
        
        # 描述
        ttk.Label(main_frame, text="描述:").pack(anchor=tk.W, pady=2)
        description_var = tk.StringVar(value=current_action['description'])
        description_entry = ttk.Entry(main_frame, textvariable=description_var, width=20)
        description_entry.pack(fill=tk.X, pady=2)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_edit():
            try:
                delay = float(delay_var.get())
                if delay < 0:
                    messagebox.showerror("错误", "延迟时间不能为负数")
                    return
                
                # 更新动作
                self.timeline_actions[index] = {
                    'action': action_var.get(),
                    'delay': delay,
                    'description': description_var.get()
                }
                
                self._dialog_update_timeline_display(timeline_tree)
                edit_dialog.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "延迟时间必须是数字")
        
        ttk.Button(button_frame, text="保存", command=save_edit, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=edit_dialog.destroy, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
    
    def _dialog_remove_timeline_action(self, timeline_tree):
        """在对话框中删除时间轴动作"""
        selection = timeline_tree.selection()
        if selection:
            index = timeline_tree.index(selection[0])
            if 0 <= index < len(self.timeline_actions):
                del self.timeline_actions[index]
                self._dialog_update_timeline_display(timeline_tree)
    
    def _dialog_move_timeline_up(self, timeline_tree):
        """在对话框中上移时间轴动作"""
        selection = timeline_tree.selection()
        if selection:
            index = timeline_tree.index(selection[0])
            if index > 0:
                self.timeline_actions[index], self.timeline_actions[index-1] = self.timeline_actions[index-1], self.timeline_actions[index]
                self._dialog_update_timeline_display(timeline_tree)
                timeline_tree.selection_set(timeline_tree.get_children()[index-1])
    
    def _dialog_move_timeline_down(self, timeline_tree):
        """在对话框中下移时间轴动作"""
        selection = timeline_tree.selection()
        if selection:
            index = timeline_tree.index(selection[0])
            if index < len(self.timeline_actions) - 1:
                self.timeline_actions[index], self.timeline_actions[index+1] = self.timeline_actions[index+1], self.timeline_actions[index]
                self._dialog_update_timeline_display(timeline_tree)
                timeline_tree.selection_set(timeline_tree.get_children()[index+1])
    
    def _dialog_reset_timeline_default(self, timeline_tree):
        """在对话框中重置时间轴为默认"""
        self.reset_timeline_default()
        self._dialog_update_timeline_display(timeline_tree)
    
    def _dialog_export_timeline_config(self, timeline_tree):
        """在对话框中导出时间轴配置"""
        self.export_timeline_config()
    
    def _dialog_import_timeline_config(self, timeline_tree):
        """在对话框中导入时间轴配置"""
        self.import_timeline_config()
        self._dialog_update_timeline_display(timeline_tree)
    
    def _save_shiny_history(self):
        """保存出闪历史记录到Excel文件"""
        try:
            # 获取当前数据
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hunt_count = int(self.hunt_count_var.get())
            generation = int(self.generation_var.get())
            judgment_count = int(self.judgment_count_var.get())
            
            # 计算概率和称号
            title, probability = self.probability_calculator.get_title_by_hunt_count(
                generation, hunt_count, judgment_count
            )
            
            # 获取最新的截图文件路径
            screenshot_paths = self._get_latest_screenshots()
            
            # 检查history.xlsx是否存在
            history_file = "history.xlsx"
            if os.path.exists(history_file):
                # 读取现有文件
                df = pd.read_excel(history_file)
            else:
                # 创建新的DataFrame
                df = pd.DataFrame(columns=[
                    '时间', '刷闪次数', '世代', '判定数', '累积概率(%)', '称号', '截图路径'
                ])
            
            # 添加新记录
            new_record = {
                '时间': current_time,
                '刷闪次数': hunt_count,
                '世代': generation,
                '判定数': judgment_count,
                '累积概率(%)': round(probability, 2),
                '称号': title,
                '截图路径': '; '.join(screenshot_paths) if screenshot_paths else ''
            }
            
            # 添加新行
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            
            # 保存到Excel文件
            df.to_excel(history_file, index=False, engine='openpyxl')
            
            self.log_message(f"出闪历史记录已保存到 {history_file}")
            
        except Exception as e:
            self.log_message(f"保存出闪历史记录失败: {e}")
            self.logger.error(f"保存出闪历史记录失败: {e}")
    
    def _get_latest_screenshots(self):
        """获取最新的截图文件路径"""
        try:
            screenshots_dir = "screenshots"
            if not os.path.exists(screenshots_dir):
                return []
            
            # 获取所有截图文件
            screenshot_files = []
            for file in os.listdir(screenshots_dir):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(screenshots_dir, file)
                    screenshot_files.append(file_path)
            
            # 按修改时间排序，获取最新的文件
            screenshot_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # 返回最新的几个文件（最多5个）
            return screenshot_files[:5]
            
        except Exception as e:
            self.logger.error(f"获取最新截图失败: {e}")
            return []
    
    # 时间轴管理方法
    def reset_timeline_default(self):
        """重置为默认时间轴"""
        self.timeline_actions = [
            {'action': 'initial_delay', 'delay': 5.0, 'description': '初始冷却'},
            {'action': 'reset', 'delay': 0.5, 'description': '按下重置键'},
            {'action': 'quick_load', 'delay': 0.5, 'description': '按下快速读取键'},
            {'action': 'confirm', 'delay': 0.8, 'description': '第一次确认'},
            {'action': 'confirm', 'delay': 0.8, 'description': '第二次确认'},
            {'action': 'analysis', 'delay': 4.0, 'description': '开始分析'}
        ]
        self.update_timeline_display()
        # 只有在界面完全初始化后才记录日志
        if hasattr(self, 'status_text'):
            self.log_message("时间轴已重置为默认配置")
    
    def update_timeline_display(self):
        """更新时间轴显示"""
        # 检查timeline_tree是否存在（可能不在主界面中）
        if not hasattr(self, 'timeline_tree'):
            return
        
        # 清空现有项目
        for item in self.timeline_tree.get_children():
            self.timeline_tree.delete(item)
        
        # 添加动作项目
        for i, action in enumerate(self.timeline_actions):
            self.timeline_tree.insert('', 'end', values=(
                i + 1,
                action['action'],
                action['delay'],
                action['description']
            ))
    
    def add_timeline_action(self):
        """添加时间轴动作"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加时间轴动作")
        dialog.geometry("400x300")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 动作选择
        ttk.Label(main_frame, text="动作类型:").pack(anchor=tk.W, pady=2)
        action_var = tk.StringVar(value="reset")
        action_combo = ttk.Combobox(main_frame, textvariable=action_var, 
                                   values=['initial_delay', 'reset', 'quick_load', 'confirm', 'analysis', 'custom_delay'],
                                   state='readonly')
        action_combo.pack(fill=tk.X, pady=2)
        
        # 延迟时间
        ttk.Label(main_frame, text="延迟时间(秒):").pack(anchor=tk.W, pady=2)
        delay_var = tk.StringVar(value="1.0")
        delay_entry = ttk.Entry(main_frame, textvariable=delay_var)
        delay_entry.pack(fill=tk.X, pady=2)
        
        # 描述
        ttk.Label(main_frame, text="描述:").pack(anchor=tk.W, pady=2)
        description_var = tk.StringVar(value="")
        description_entry = ttk.Entry(main_frame, textvariable=description_var)
        description_entry.pack(fill=tk.X, pady=2)
        
        # 插入位置
        ttk.Label(main_frame, text="插入位置:").pack(anchor=tk.W, pady=2)
        position_var = tk.StringVar(value="end")
        position_combo = ttk.Combobox(main_frame, textvariable=position_var,
                                     values=['start', 'end', 'after_selected'],
                                     state='readonly')
        position_combo.pack(fill=tk.X, pady=2)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def add_action():
            try:
                action = action_var.get()
                delay = float(delay_var.get())
                description = description_var.get() or f"{action}动作"
                position = position_var.get()
                
                new_action = {
                    'action': action,
                    'delay': delay,
                    'description': description
                }
                
                if position == 'start':
                    self.timeline_actions.insert(0, new_action)
                elif position == 'end':
                    self.timeline_actions.append(new_action)
                elif position == 'after_selected':
                    selected = self.timeline_tree.selection()
                    if selected:
                        index = self.timeline_tree.index(selected[0])
                        self.timeline_actions.insert(index + 1, new_action)
                    else:
                        self.timeline_actions.append(new_action)
                
                self.update_timeline_display()
                dialog.destroy()
                self.log_message(f"已添加时间轴动作: {description}")
                
            except ValueError:
                messagebox.showerror("错误", "延迟时间必须是数字")
            except Exception as e:
                messagebox.showerror("错误", f"添加动作失败: {e}")
        
        ttk.Button(button_frame, text="添加", command=add_action, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, style='Modern.TButton').pack(side=tk.LEFT, padx=5)
    
    def remove_timeline_action(self):
        """删除选中的时间轴动作"""
        if not hasattr(self, 'timeline_tree'):
            messagebox.showinfo("提示", "请使用配置对话框来管理时间轴")
            return
            
        selected = self.timeline_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的动作")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的动作吗？"):
            index = self.timeline_tree.index(selected[0])
            removed_action = self.timeline_actions.pop(index)
            self.update_timeline_display()
            self.log_message(f"已删除时间轴动作: {removed_action['description']}")
    
    def move_timeline_up(self):
        """上移选中的时间轴动作"""
        if not hasattr(self, 'timeline_tree'):
            messagebox.showinfo("提示", "请使用配置对话框来管理时间轴")
            return
            
        selected = self.timeline_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要移动的动作")
            return
        
        index = self.timeline_tree.index(selected[0])
        if index > 0:
            # 交换位置
            self.timeline_actions[index], self.timeline_actions[index - 1] = \
                self.timeline_actions[index - 1], self.timeline_actions[index]
            self.update_timeline_display()
            # 重新选中移动后的项目
            self.timeline_tree.selection_set(self.timeline_tree.get_children()[index - 1])
            self.log_message("动作已上移")
    
    def move_timeline_down(self):
        """下移选中的时间轴动作"""
        if not hasattr(self, 'timeline_tree'):
            messagebox.showinfo("提示", "请使用配置对话框来管理时间轴")
            return
            
        selected = self.timeline_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要移动的动作")
            return
        
        index = self.timeline_tree.index(selected[0])
        if index < len(self.timeline_actions) - 1:
            # 交换位置
            self.timeline_actions[index], self.timeline_actions[index + 1] = \
                self.timeline_actions[index + 1], self.timeline_actions[index]
            self.update_timeline_display()
            # 重新选中移动后的项目
            self.timeline_tree.selection_set(self.timeline_tree.get_children()[index + 1])
            self.log_message("动作已下移")
    
    def export_timeline_config(self):
        """导出时间轴配置"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="导出时间轴配置",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir="configs"
            )
            
            if file_path:
                config = {
                    'timeline_actions': self.timeline_actions,
                    'retry_count': int(self.retry_count_var.get()),
                    'retry_interval': float(self.retry_interval_var.get()),
                    'export_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'description': f"时间轴配置 - {len(self.timeline_actions)}个动作, 重试{int(self.retry_count_var.get())}次"
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                self.log_message(f"时间轴配置已导出: {file_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出时间轴配置失败: {e}")
            self.log_message(f"导出时间轴配置失败: {e}")
    
    def import_timeline_config(self):
        """导入时间轴配置"""
        try:
            file_path = filedialog.askopenfilename(
                title="导入时间轴配置",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir="configs"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 验证配置格式
                if 'timeline_actions' not in config:
                    messagebox.showerror("错误", "配置文件格式错误：缺少timeline_actions字段")
                    return
                
                # 验证时间轴动作格式
                timeline_actions = config['timeline_actions']
                if not isinstance(timeline_actions, list):
                    messagebox.showerror("错误", "配置文件格式错误：timeline_actions必须是数组")
                    return
                
                for i, action in enumerate(timeline_actions):
                    if not isinstance(action, dict):
                        messagebox.showerror("错误", f"配置文件格式错误：第{i+1}个动作格式错误")
                        return
                    
                    required_fields = ['action', 'delay', 'description']
                    for field in required_fields:
                        if field not in action:
                            messagebox.showerror("错误", f"配置文件格式错误：第{i+1}个动作缺少{field}字段")
                            return
                    
                    # 验证delay是数字
                    try:
                        float(action['delay'])
                    except (ValueError, TypeError):
                        messagebox.showerror("错误", f"配置文件格式错误：第{i+1}个动作的delay必须是数字")
                        return
                
                # 确认导入
                if messagebox.askyesno("确认导入", f"将导入{len(timeline_actions)}个时间轴动作，是否继续？"):
                    self.timeline_actions = timeline_actions
                    self.update_timeline_display()
                    
                    # 导入重试配置
                    if 'retry_count' in config:
                        self.retry_count_var.set(str(config['retry_count']))
                    if 'retry_interval' in config:
                        self.retry_interval_var.set(str(config['retry_interval']))
                    
                    export_time = config.get('export_time', '未知时间')
                    description = config.get('description', '无描述')
                    retry_count = config.get('retry_count', '未设置')
                    retry_interval = config.get('retry_interval', '未设置')
                    self.log_message(f"时间轴配置已导入: {len(timeline_actions)}个动作, 重试{retry_count}次/{retry_interval}s (导出时间: {export_time})")
                
        except json.JSONDecodeError:
            messagebox.showerror("错误", "配置文件格式错误：不是有效的JSON文件")
        except Exception as e:
            messagebox.showerror("错误", f"导入时间轴配置失败: {e}")
            self.log_message(f"导入时间轴配置失败: {e}")
    
    def save_probability_config(self):
        """保存概率配置"""
        try:
            config = {
                'generation': int(self.generation_var.get()),
                'judgment_count': int(self.judgment_count_var.get()),
                'timestamp': time.time()
            }
            
            filepath = filedialog.asksaveasfilename(
                title="保存概率配置",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir="configs"
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.log_message(f"概率配置已保存到: {filepath}")
                
        except Exception as e:
            self.logger.error(f"保存概率配置失败: {e}")
            messagebox.showerror("错误", f"保存概率配置失败: {e}")
    
    def load_probability_config(self):
        """加载概率配置"""
        try:
            filepath = filedialog.askopenfilename(
                title="加载概率配置",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir="configs"
            )
            
            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 更新界面显示
                self.generation_var.set(str(config.get('generation', 6)))
                self.judgment_count_var.set(str(config.get('judgment_count', 1)))
                
                # 更新概率显示
                self._update_probability_display()
                
                self.log_message(f"概率配置已加载: {filepath}")
                
        except Exception as e:
            self.logger.error(f"加载概率配置失败: {e}")
            messagebox.showerror("错误", f"加载概率配置失败: {e}")
    
    def reset_probability_config(self):
        """重置概率配置"""
        self.generation_var.set("6")
        self.judgment_count_var.set("1")
        self._update_probability_display()
        self.log_message("概率配置已重置为默认值")
    
    def _update_threshold_display(self, value=None):
        """更新阈值显示（保留两位小数）"""
        self.color_sim_label.config(text=f"{self.color_sim_var.get():.2f}")
        self.ssim_label.config(text=f"{self.ssim_var.get():.2f}")
        self.color_diff_label.config(text=f"{self.color_diff_var.get():.2f}")
    
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
            # 显示动作描述，精度到小数点后2位
            self.countdown_var.set(f"{self.countdown_remaining:.2f}秒后: {self.countdown_action}")
            # 进度条也使用高精度
            progress_value = self.countdown_total - self.countdown_remaining
            self.countdown_progress['value'] = progress_value
            self.countdown_remaining -= 0.01  # 每10毫秒更新一次，提高精度
            self.countdown_timer = self.root.after(10, self._update_countdown)  # 10毫秒更新
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
        
        # 为重试配置输入框添加验证
        self.retry_count_var.trace('w', lambda *args: self._validate_input(
            self.retry_count_var, 0, 5, "重试次数", is_int=True))
        self.retry_interval_var.trace('w', lambda *args: self._validate_input(
            self.retry_interval_var, 0.5, 10.0, "重试间隔"))
    
    def _update_probability_display(self, event=None):
        """更新概率显示"""
        try:
            generation = int(self.generation_var.get())
            judgment_count = int(self.judgment_count_var.get())
            hunt_count = int(self.hunt_count_var.get())
            
            # 计算称号和概率
            title, probability = self.probability_calculator.get_title_by_hunt_count(
                generation, hunt_count, judgment_count
            )
            
            # 更新显示
            self.current_title_var.set(title)
            self.current_probability_var.set(f"{probability:.2f}%")
            
            # 检查是否为欧皇中皇
            if self.probability_calculator.is_ultra_lucky(generation, hunt_count, judgment_count):
                self.current_title_var.set("欧皇中皇")
                self.logger.info(f"检测到欧皇中皇！世代{generation}，刷闪{hunt_count}次，判定数{judgment_count}")
                
        except (ValueError, TypeError) as e:
            self.logger.warning(f"概率计算失败: {e}")
            self.current_title_var.set("计算错误")
            self.current_probability_var.set("0.00%")
    
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
    
    def folder_import_config(self):
        """从文件夹批量导入配置"""
        try:
            # 选择文件夹
            folder_path = filedialog.askdirectory(
                title="选择配置文件夹",
                initialdir="configs"
            )
            
            if not folder_path:
                return
            
            self.folder_path_var.set(folder_path)
            
            imported_items = []
            
            # 清除现有的参考图像
            self.app.image_analyzer.clear_references()
            self.log_message("已清除现有参考图像")
            
            # 1. 导入文件夹下的所有图片作为参考图像
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']
            image_files = []
            
            # 扫描文件夹下的所有图片文件（不包括子文件夹）
            for file_name in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, file_name)):
                    file_ext = os.path.splitext(file_name)[1].lower()
                    if file_ext in image_extensions:
                        image_files.append(file_name)
            
            if image_files:
                # 确保configs目录存在
                configs_dir = "configs"
                if not os.path.exists(configs_dir):
                    os.makedirs(configs_dir)
                
                imported_count = 0
                for image_file in image_files:
                    try:
                        # 构建完整路径
                        source_path = os.path.join(folder_path, image_file)
                        
                        # 生成参考图像名称（去掉扩展名）
                        base_name = os.path.splitext(image_file)[0]
                        ref_image_name = f"{os.path.basename(folder_path)}_{base_name}"
                        ref_image_path = os.path.join(configs_dir, f"{ref_image_name}.png")
                        
                        # 复制图片文件
                        shutil.copy2(source_path, ref_image_path)
                        
                        # 加载参考图像
                        self.app.image_analyzer.load_reference_image(ref_image_name, ref_image_path)
                        imported_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"导入图片失败 {image_file}: {e}")
                        continue
                
                if imported_count > 0:
                    # 更新参考图像列表显示
                    self.update_reference_list()
                    imported_items.append(f"参考图像({imported_count}个)")
            
            # 2. 导入截图位置
            screenshot_path = os.path.join(folder_path, "screenshootposition.json")
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
                
                # 更新截图区域列表显示
                self.update_region_list()
                imported_items.append("截图位置")
            
            # 3. 导入时间轴设置
            timeline_path = os.path.join(folder_path, "timeline.json")
            if os.path.exists(timeline_path):
                with open(timeline_path, 'r', encoding='utf-8') as f:
                    timeline_config = json.load(f)
                
                # 加载时间轴配置
                if 'timeline_actions' in timeline_config:
                    self.timeline_actions = timeline_config['timeline_actions']
                    self.update_timeline_display()
                
                # 加载重试配置
                self.retry_count_var.set(str(timeline_config.get('retry_count', 2)))
                self.retry_interval_var.set(str(timeline_config.get('retry_interval', 2.0)))
                
                imported_items.append("时间轴设置")
            
            # 4. 导入暂停信息
            hunt_count_path = os.path.join(folder_path, "hunt_count.json")
            if os.path.exists(hunt_count_path):
                with open(hunt_count_path, 'r', encoding='utf-8') as f:
                    hunt_data = json.load(f)
                
                # 加载刷闪次数
                if 'hunt_count' in hunt_data:
                    self.hunt_count_var.set(str(hunt_data['hunt_count']))
                    self.app.auto_hunter.hunt_count = hunt_data['hunt_count']
                    self.log_message(f"已导入暂停信息: 刷闪次数 {hunt_data['hunt_count']}")
                    imported_items.append("暂停信息")
            
            # 5. 导入阈值设置
            threshold_path = os.path.join(folder_path, "threshold.json")
            if os.path.exists(threshold_path):
                with open(threshold_path, 'r', encoding='utf-8') as f:
                    threshold_config = json.load(f)
                
                # 应用阈值设置
                self.app.image_analyzer.set_color_similarity_threshold(threshold_config.get('color_similarity', 0.8))
                self.app.image_analyzer.set_ssim_threshold(threshold_config.get('ssim_threshold', 0.3))
                self.app.image_analyzer.set_color_difference_threshold(threshold_config.get('color_difference', 30.0))
                
                # 更新阈值设置界面显示
                thresholds = self.app.image_analyzer.get_thresholds()
                self.color_sim_var.set(thresholds['color_similarity'])
                self.ssim_var.set(thresholds['ssim_threshold'])
                self.color_diff_var.set(thresholds['color_difference'])
                self._update_threshold_display()
                
                imported_items.append("阈值设置")
            
            # 5. 导入概率配置
            gen_path = os.path.join(folder_path, "gen.json")
            if os.path.exists(gen_path):
                with open(gen_path, 'r', encoding='utf-8') as f:
                    gen_config = json.load(f)
                
                # 更新概率配置
                self.generation_var.set(str(gen_config.get('generation', 6)))
                self.judgment_count_var.set(str(gen_config.get('judgment_count', 1)))
                self._update_probability_display()
                
                imported_items.append("概率配置")
            
            # 更新状态显示
            if imported_items:
                self.import_status_var.set(f"成功导入: {', '.join(imported_items)}")
                self.log_message(f"文件夹导入配置成功: {', '.join(imported_items)}")
                
                # 提醒用户清理screenshots文件夹
                self._ask_cleanup_screenshots()
            else:
                self.import_status_var.set("未找到可导入的配置文件")
                self.log_message(f"文件夹 '{folder_path}' 中未找到可导入的配置文件")
                
        except Exception as e:
            self.import_status_var.set(f"导入失败: {e}")
            self.log_message(f"文件夹导入配置失败: {e}")
    
    
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
    
    def cleanup_screenshots(self):
        """清理截图文件"""
        try:
            age_hours = int(self.cleanup_age_var.get())
            keep_shiny = self.keep_shiny_var.get()
            
            if messagebox.askyesno("确认清理", 
                                 f"将清理超过{age_hours}小时的截图文件\n"
                                 f"保留闪光图片: {'是' if keep_shiny else '否'}\n"
                                 f"是否继续？"):
                
                deleted, kept = self.app.screenshot_manager.cleanup_screenshots(
                    keep_shiny=keep_shiny, 
                    max_age_hours=age_hours
                )
                
                self.log_message(f"截图清理完成: 删除{deleted}个文件, 保留{kept}个文件")
                messagebox.showinfo("清理完成", f"删除{deleted}个文件, 保留{kept}个文件")
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的保留时间（小时）")
        except Exception as e:
            self.logger.error(f"清理截图失败: {e}")
            messagebox.showerror("错误", f"清理失败: {e}")
    
    def mark_shiny_images(self):
        """标记闪光图片"""
        try:
            # 选择要标记为闪光的图片文件
            file_paths = filedialog.askopenfilenames(
                title="选择闪光图片",
                filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
                initialdir="screenshots"
            )
            
            if file_paths:
                for file_path in file_paths:
                    self.app.screenshot_manager.mark_as_shiny(file_path)
                
                self.log_message(f"已标记{len(file_paths)}个图片为闪光图片")
                messagebox.showinfo("标记完成", f"已标记{len(file_paths)}个图片为闪光图片")
                
        except Exception as e:
            self.logger.error(f"标记闪光图片失败: {e}")
            messagebox.showerror("错误", f"标记失败: {e}")
    
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
        
        # 使用多参考图像进行分析
        analysis_results = []
        for result in results:
            analysis = self.app.image_analyzer.analyze_image_multi_reference(result['image'])
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
            self._update_threshold_display()  # 更新显示标签
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
