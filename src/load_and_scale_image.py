"""
图片加载和缩放工具模块

本模块提供图片加载和缩放功能，使用LRU缓存机制提高性能。
主要用于电影海报图片的加载和适配UI显示需求。

主要功能：
- 支持多种图片格式的加载（JPG、PNG等）
- 保持宽高比的智能缩放
- LRU缓存机制减少重复加载
- 高质量图像变换算法

Author: LocalPosterWall Team
Version: 0.0.1
"""

import time
from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QSize

from loguru import logger


@lru_cache(maxsize=100)
def load_and_scale_image(image_path, width, height):
    """
    加载并缩放图片（带缓存）
    
    使用PySide6的QImage和QPixmap加载图片文件，并缩放到指定尺寸。
    应用LRU缓存机制，缓存最近使用的100个图片结果，提高重复访问的性能。
    图片缩放时保持宽高比，使用平滑变换算法保证图片质量。
    
    Args:
        image_path (str/Path): 图片文件路径
        width (int): 目标宽度
        height (int): 目标高度
        
    Returns:
        QPixmap/None: 缩放后的图片对象，如果加载失败则返回None
        
    Note:
        - 函数使用@lru_cache装饰器，自动缓存最近100个图片结果
        - 图片路径和尺寸组合作为缓存键
        - 如果图片文件不存在或损坏，返回None
        - 缩放时保持宽高比，超出目标尺寸的部分会被裁剪
    """
    logger.debug(f"开始加载和缩放图片: {image_path}")
    start_time = time.time()
    
    try:
        # 检查图片文件路径
        if not image_path:
            logger.warning("图片路径为空")
            return None
            
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            logger.warning(f"图片文件不存在: {image_path}")
            return None
            
        if not image_path_obj.is_file():
            logger.warning(f"路径不是文件: {image_path}")
            return None
        
        logger.debug(f"图片文件路径验证通过: {image_path_obj}")
        logger.debug(f"目标尺寸: {width}x{height}")
        
        # 加载图片
        logger.debug("开始使用QImage加载图片")
        image = QImage(str(image_path_obj))
        
        # 检查图片是否成功加载
        if image.isNull():
            logger.warning(f"图片加载失败，文件可能损坏: {image_path}")
            return None
            
        logger.debug(f"图片加载成功，原始尺寸: {image.width()}x{image.height()}")
        
        # 创建目标尺寸对象
        target_size = QSize(width, height)
        logger.debug(f"目标尺寸对象创建: {target_size}")
        
        # 执行缩放操作
        logger.debug("开始图片缩放，保持宽高比")
        scaled_image = image.scaled(
            target_size,
            Qt.KeepAspectRatio,      # 保持宽高比
            Qt.SmoothTransformation  # 使用平滑变换算法
        )
        
        logger.debug(f"图片缩放完成，缩放后尺寸: {scaled_image.width()}x{scaled_image.height()}")
        
        # 转换为QPixmap格式（更适合在Qt中使用）
        logger.debug("转换为QPixmap格式")
        result_pixmap = QPixmap.fromImage(scaled_image)
        
        if result_pixmap.isNull():
            logger.warning("转换为QPixmap失败")
            return None
            
        # 记录性能统计
        load_time = time.time() - start_time
        logger.info(f"图片加载和缩放完成: {image_path}")
        logger.debug(f"处理耗时: {load_time:.3f}秒")
        logger.debug(f"尺寸变化: {image.width()}x{image.height()} -> {scaled_image.width()}x{scaled_image.height()}")
        
        return result_pixmap
        
    except Exception as e:
        logger.exception(f"加载和缩放图片失败 {image_path}: {str(e)}")
        return None


def clear_image_cache():
    """
    清除图片加载缓存
    
    手动清除LRU缓存中的所有缓存项，释放内存。
    在内存使用量较大或需要强制重新加载图片时调用。
    """
    logger.info("清除图片加载缓存")
    
    try:
        # 获取缓存信息
        cache_info = load_and_scale_image.cache_info()
        logger.debug(f"缓存统计: {cache_info}")
        
        # 清除缓存
        load_and_scale_image.cache_clear()
        
        logger.info("图片加载缓存清除完成")
        
    except Exception as e:
        logger.exception(f"清除图片缓存失败: {str(e)}")


def get_image_cache_info():
    """
    获取图片加载缓存信息
    
    Returns:
        dict: 包含缓存统计信息的字典
    """
    logger.debug("获取图片缓存信息")
    
    try:
        cache_info = load_and_scale_image.cache_info()
        
        info = {
            'hits': cache_info.hits,
            'misses': cache_info.misses,
            'maxsize': cache_info.maxsize,
            'currsize': cache_info.currsize,
            'hit_rate': cache_info.hits / max(cache_info.hits + cache_info.misses, 1)
        }
        
        logger.debug(f"缓存统计信息: {info}")
        return info
        
    except Exception as e:
        logger.exception(f"获取缓存信息失败: {str(e)}")
        return {}


def preload_image(image_path, width, height):
    """
    预加载图片到缓存
    
    主动加载指定图片并将其存储在LRU缓存中，
    适用于需要提前准备某些图片的场景。
    
    Args:
        image_path (str/Path): 图片文件路径
        width (int): 目标宽度
        height (int): 目标高度
        
    Returns:
        QPixmap/None: 预加载的图片对象，如果失败则返回None
    """
    logger.info(f"预加载图片: {image_path}")
    start_time = time.time()
    
    try:
        # 检查文件是否存在
        if not Path(image_path).exists():
            logger.warning(f"预加载失败，文件不存在: {image_path}")
            return None
        
        # 加载图片（这会自动将其放入缓存）
        result = load_and_scale_image(image_path, width, height)
        
        if result:
            preload_time = time.time() - start_time
            logger.info(f"图片预加载成功: {image_path}")
            logger.debug(f"预加载耗时: {preload_time:.3f}秒")
        else:
            logger.warning(f"图片预加载失败: {image_path}")
        
        return result
        
    except Exception as e:
        logger.exception(f"预加载图片失败 {image_path}: {str(e)}")
        return None
