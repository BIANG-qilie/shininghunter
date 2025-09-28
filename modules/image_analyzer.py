#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像分析模块
负责图像相似度比较和颜色差异检测
"""

import logging
import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import json

try:
    import cv2
    from PIL import Image
    from skimage.metrics import structural_similarity as ssim
    from skimage import color
except ImportError:
    print("请安装必要的依赖: pip install opencv-python pillow scikit-image")
    cv2 = None

class ImageAnalyzer:
    """图像分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reference_images = {}  # 存储参考图像
        self.thresholds = {
            'color_similarity': 0.8,  # 颜色相似度阈值
            'ssim_threshold': 0.7,    # 结构相似度阈值
            'color_difference': 30    # 颜色差异阈值
        }
        
        if cv2 is None:
            self.logger.error("opencv 未安装，图像分析功能不可用")
    
    def load_reference_image(self, name: str, image_path: str) -> bool:
        """
        加载参考图像
        
        Args:
            name: 参考图像名称
            image_path: 图像文件路径
            
        Returns:
            bool: 加载是否成功
        """
        if cv2 is None:
            return False
        
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"无法读取图像: {image_path}")
                return False
            
            # 转换为RGB格式
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            self.reference_images[name] = {
                'image': image_rgb,
                'path': image_path,
                'histogram': self.calculate_color_histogram(image_rgb)
            }
            
            self.logger.info(f"加载参考图像: {name} - {image_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"加载参考图像失败: {e}")
            return False
    
    def calculate_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """
        计算颜色直方图
        
        Args:
            image: RGB图像数组
            
        Returns:
            颜色直方图
        """
        if cv2 is None:
            return None
        
        try:
            # 计算RGB三个通道的直方图
            hist_r = cv2.calcHist([image], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([image], [2], None, [256], [0, 256])
            
            # 合并直方图
            histogram = np.concatenate([hist_r, hist_g, hist_b])
            
            # 归一化
            histogram = histogram / np.sum(histogram)
            
            return histogram
            
        except Exception as e:
            self.logger.error(f"计算颜色直方图失败: {e}")
            return None
    
    def compare_color_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        比较两个图像的颜色相似度
        
        Args:
            img1: 第一个图像
            img2: 第二个图像
            
        Returns:
            相似度分数 (0-1)
        """
        if cv2 is None:
            return 0.0
        
        try:
            # 计算颜色直方图
            hist1 = self.calculate_color_histogram(img1)
            hist2 = self.calculate_color_histogram(img2)
            
            if hist1 is None or hist2 is None:
                return 0.0
            
            # 使用巴氏距离计算相似度
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            return max(0.0, correlation)
            
        except Exception as e:
            self.logger.error(f"颜色相似度比较失败: {e}")
            return 0.0
    
    def calculate_color_difference(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算两个图像的颜色差异
        
        Args:
            img1: 第一个图像
            img2: 第二个图像
            
        Returns:
            平均颜色差异值
        """
        if cv2 is None:
            return float('inf')
        
        try:
            # 确保图像尺寸相同
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 计算像素级差异
            diff = cv2.absdiff(img1, img2)
            
            # 计算平均差异
            mean_diff = np.mean(diff)
            
            return mean_diff
            
        except Exception as e:
            self.logger.error(f"颜色差异计算失败: {e}")
            return float('inf')
    
    def calculate_structural_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算结构相似度 (SSIM)
        
        Args:
            img1: 第一个图像
            img2: 第二个图像
            
        Returns:
            SSIM分数 (0-1)
        """
        try:
            # 转换为灰度图像
            gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            
            # 确保图像尺寸相同
            if gray1.shape != gray2.shape:
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
            
            # 计算SSIM
            similarity = ssim(gray1, gray2)
            
            return max(0.0, similarity)
            
        except Exception as e:
            self.logger.error(f"结构相似度计算失败: {e}")
            return 0.0
    
    def analyze_image(self, current_image: np.ndarray, reference_name: str) -> Dict:
        """
        分析当前图像与参考图像的相似度
        
        Args:
            current_image: 当前图像
            reference_name: 参考图像名称
            
        Returns:
            分析结果字典
        """
        if reference_name not in self.reference_images:
            self.logger.error(f"参考图像不存在: {reference_name}")
            return {}
        
        reference_image = self.reference_images[reference_name]['image']
        
        # 计算各种相似度指标
        color_similarity = self.compare_color_similarity(current_image, reference_image)
        color_difference = self.calculate_color_difference(current_image, reference_image)
        structural_similarity = self.calculate_structural_similarity(current_image, reference_image)
        
        # 综合评分
        overall_score = (color_similarity + structural_similarity) / 2
        
        # 判断是否匹配
        is_match = (
            color_similarity >= self.thresholds['color_similarity'] and
            structural_similarity >= self.thresholds['ssim_threshold'] and
            color_difference <= self.thresholds['color_difference']
        )
        
        result = {
            'reference_name': reference_name,
            'color_similarity': color_similarity,
            'color_difference': color_difference,
            'structural_similarity': structural_similarity,
            'overall_score': overall_score,
            'is_match': is_match,
            'thresholds': self.thresholds.copy()
        }
        
        return result
    
    def analyze_image_multi_reference(self, current_image: np.ndarray) -> Dict:
        """
        使用多个参考图像分析当前图像，取各项指标的最大值
        
        Args:
            current_image: 当前图像
            
        Returns:
            分析结果字典（各项指标为所有参考图像中的最大值）
        """
        if not self.reference_images:
            self.logger.error("没有可用的参考图像")
            return {}
        
        # 存储所有参考图像的分析结果
        all_results = []
        
        # 与每个参考图像进行比较
        for reference_name in self.reference_images.keys():
            result = self.analyze_image(current_image, reference_name)
            if result:  # 确保分析成功
                all_results.append(result)
        
        if not all_results:
            self.logger.error("所有参考图像分析都失败")
            return {}
        
        # 取各项指标的最大值
        max_color_similarity = max(r['color_similarity'] for r in all_results)
        max_structural_similarity = max(r['structural_similarity'] for r in all_results)
        max_overall_score = max(r['overall_score'] for r in all_results)
        
        # 颜色差异取最小值（越小越好）
        min_color_difference = min(r['color_difference'] for r in all_results)
        
        # 基于综合后的最佳指标进行匹配判断
        is_match = (
            max_color_similarity >= self.thresholds['color_similarity'] and
            max_structural_similarity >= self.thresholds['ssim_threshold'] and
            min_color_difference <= self.thresholds['color_difference']
        )
        
        # 找到最佳匹配的参考图像
        best_reference = max(all_results, key=lambda r: r['overall_score'])
        
        result = {
            'reference_name': f"多参考图像({len(all_results)}个)",
            'best_reference': best_reference['reference_name'],
            'color_similarity': max_color_similarity,
            'color_difference': min_color_difference,
            'structural_similarity': max_structural_similarity,
            'overall_score': max_overall_score,
            'is_match': is_match,
            'thresholds': self.thresholds.copy(),
            'all_results': all_results  # 包含所有参考图像的详细结果
        }
        
        self.logger.info(f"多参考图像分析完成: 最佳匹配={best_reference['reference_name']}, "
                        f"综合评分={max_overall_score:.3f}, 匹配={is_match}")
        
        return result
    
    def batch_analyze(self, current_images: List[np.ndarray], reference_name: str) -> List[Dict]:
        """
        批量分析多个图像
        
        Args:
            current_images: 当前图像列表
            reference_name: 参考图像名称
            
        Returns:
            分析结果列表
        """
        results = []
        
        for i, image in enumerate(current_images):
            result = self.analyze_image(image, reference_name)
            result['image_index'] = i
            results.append(result)
        
        return results
    
    def set_threshold(self, threshold_name: str, value: float):
        """
        设置阈值
        
        Args:
            threshold_name: 阈值名称
            value: 阈值数值
        """
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value
            self.logger.info(f"设置阈值 {threshold_name}: {value}")
        else:
            self.logger.error(f"未知的阈值名称: {threshold_name}")
    
    def set_color_similarity_threshold(self, value: float):
        """设置颜色相似度阈值"""
        self.thresholds['color_similarity'] = value
        self.logger.info(f"设置颜色相似度阈值: {value}")
    
    def set_ssim_threshold(self, value: float):
        """设置SSIM阈值"""
        self.thresholds['ssim_threshold'] = value
        self.logger.info(f"设置SSIM阈值: {value}")
    
    def set_color_difference_threshold(self, value: float):
        """设置颜色差异阈值"""
        self.thresholds['color_difference'] = value
        self.logger.info(f"设置颜色差异阈值: {value}")
    
    def get_thresholds(self) -> Dict:
        """获取当前阈值设置"""
        return self.thresholds.copy()
    
    def save_thresholds(self, filepath: str):
        """保存阈值设置到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.thresholds, f, indent=2, ensure_ascii=False)
            self.logger.info(f"阈值设置已保存: {filepath}")
        except Exception as e:
            self.logger.error(f"保存阈值设置失败: {e}")
    
    def load_thresholds(self, filepath: str):
        """从文件加载阈值设置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_thresholds = json.load(f)
            
            # 更新阈值
            for key, value in loaded_thresholds.items():
                if key in self.thresholds:
                    self.thresholds[key] = value
            
            self.logger.info(f"阈值设置已加载: {filepath}")
        except Exception as e:
            self.logger.error(f"加载阈值设置失败: {e}")
    
    def get_reference_list(self) -> List[str]:
        """获取参考图像列表"""
        return list(self.reference_images.keys())
    
    def remove_reference(self, name: str):
        """移除参考图像"""
        if name in self.reference_images:
            del self.reference_images[name]
            self.logger.info(f"移除参考图像: {name}")
    
    def clear_references(self):
        """清除所有参考图像"""
        self.reference_images.clear()
        self.logger.info("清除所有参考图像")
