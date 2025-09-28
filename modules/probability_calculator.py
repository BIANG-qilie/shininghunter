#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
概率计算模块
负责计算刷闪概率和称号系统
"""

import csv
import logging
from typing import Dict, List, Tuple, Optional

class ProbabilityCalculator:
    """概率计算器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.generation_probabilities = {}  # 世代概率表
        self.titles = {}  # 称号表
        self.load_probability_data()
        self.load_title_data()
    
    def load_probability_data(self):
        """加载概率数据"""
        try:
            with open('configs/概率.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                
                for row in reader:
                    if len(row) >= 2 and row[0] and row[1]:
                        generation = int(row[0])
                        denominator = int(row[1])
                        self.generation_probabilities[generation] = denominator
                        
            self.logger.info(f"加载了 {len(self.generation_probabilities)} 个世代的概率数据")
        except Exception as e:
            self.logger.error(f"加载概率数据失败: {e}")
            # 默认数据
            self.generation_probabilities = {
                3: 8192, 4: 8192, 5: 8192, 6: 4096, 7: 4096
            }
    
    def load_title_data(self):
        """加载称号数据"""
        try:
            with open('configs/称号.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                
                for row in reader:
                    if len(row) >= 2 and row[0] and row[1]:
                        title = row[0]
                        probability = float(row[1])
                        self.titles[probability] = title
                        
            self.logger.info(f"加载了 {len(self.titles)} 个称号")
        except Exception as e:
            self.logger.error(f"加载称号数据失败: {e}")
            # 默认数据
            self.titles = {
                0.1: "欧皇中皇", 1: "欧皇", 5: "非同一般欧洲狗",
                10: "不可小觑欧洲人", 20: "欧洲人", 50: "平平无奇",
                70: "小非酋", 80: "非洲酋长", 90: "月见黑", 99: "大阴阳师"
            }
    
    def get_available_generations(self) -> List[int]:
        """获取可用的世代列表"""
        return sorted(self.generation_probabilities.keys())
    
    def calculate_single_probability(self, generation: int, judgment_count: int = 1) -> float:
        """
        计算单次出闪概率
        
        Args:
            generation: 世代
            judgment_count: 判定数（分子）
            
        Returns:
            单次出闪概率（百分比）
        """
        if generation not in self.generation_probabilities:
            self.logger.error(f"未知的世代: {generation}")
            return 0.0
        
        denominator = self.generation_probabilities[generation]
        probability = (judgment_count / denominator) * 100
        return probability
    
    def calculate_cumulative_probability(self, generation: int, hunt_count: int, judgment_count: int = 1) -> float:
        """
        计算累积出闪概率
        
        Args:
            generation: 世代
            hunt_count: 刷闪次数
            judgment_count: 判定数（分子）
            
        Returns:
            累积出闪概率（百分比）
        """
        single_prob = self.calculate_single_probability(generation, judgment_count) / 100
        cumulative_prob = 1 - (1 - single_prob) ** hunt_count
        return cumulative_prob * 100
    
    def get_title_by_probability(self, probability: float) -> str:
        """
        根据概率获取称号
        
        Args:
            probability: 概率（百分比）
            
        Returns:
            称号名称
        """
        # 按概率从低到高排序
        sorted_titles = sorted(self.titles.items())
        
        for prob_threshold, title in sorted_titles:
            if probability <= prob_threshold:
                return title
        
        # 如果概率超过最高阈值，返回最高称号
        return sorted_titles[-1][1]
    
    def get_title_by_hunt_count(self, generation: int, hunt_count: int, judgment_count: int = 1) -> Tuple[str, float]:
        """
        根据刷闪次数获取称号和概率
        
        Args:
            generation: 世代
            hunt_count: 刷闪次数
            judgment_count: 判定数（分子）
            
        Returns:
            (称号名称, 累积概率)
        """
        cumulative_prob = self.calculate_cumulative_probability(generation, hunt_count, judgment_count)
        title = self.get_title_by_probability(cumulative_prob)
        return title, cumulative_prob
    
    def is_ultra_lucky(self, generation: int, hunt_count: int, judgment_count: int = 1) -> bool:
        """
        判断是否为欧皇中皇（概率低于0.1%）
        
        Args:
            generation: 世代
            hunt_count: 刷闪次数
            judgment_count: 判定数（分子）
            
        Returns:
            是否为欧皇中皇
        """
        cumulative_prob = self.calculate_cumulative_probability(generation, hunt_count, judgment_count)
        return cumulative_prob < 0.1
