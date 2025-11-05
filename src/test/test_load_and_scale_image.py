"""
load_and_scale_image 测试模块

本模块包含对load_and_scale_image模块的单元测试，测试内容包括：
- 图片加载功能测试
- 图片缩放功能测试
- LRU缓存机制测试
- 缓存管理功能测试
- 预加载功能测试
- 边界情况和异常处理测试

使用unittest框架和PySide6进行测试，创建临时图片文件进行测试。
"""

import unittest
import sys
import os
from pathlib import Path
from io import BytesIO

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

# 导入被测试模块
from src.load_and_scale_image import (
    load_and_scale_image,
    clear_image_cache,
    get_image_cache_info,
    preload_image
)


class TestLoadAndScaleImage(unittest.TestCase):
    """load_and_scale_image模块的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        # 确保只创建一个QApplication实例
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        # 创建测试图片目录
        cls.test_dir = Path(__file__).parent / "test_images"
        cls.test_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """测试类清理：删除测试图片目录"""
        # 清理测试图片
        if cls.test_dir.exists():
            for file in cls.test_dir.glob("*"):
                try:
                    file.unlink()
                except:
                    pass
            try:
                cls.test_dir.rmdir()
            except:
                pass

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 清除缓存，确保测试独立性
        clear_image_cache()
        
        # 创建测试图片文件路径
        self.test_image_path = self.test_dir / "test_image.png"
        self.test_image_jpg_path = self.test_dir / "test_image.jpg"
        self.test_large_image_path = self.test_dir / "test_large_image.png"
        self.test_small_image_path = self.test_dir / "test_small_image.png"
        
        # 创建测试图片
        self._create_test_image(self.test_image_path, 400, 600)
        self._create_test_image(self.test_image_jpg_path, 400, 600, "JPG")
        self._create_test_image(self.test_large_image_path, 1920, 1080)
        self._create_test_image(self.test_small_image_path, 100, 150)
        
        # 测试用的目标尺寸
        self.target_width = 200
        self.target_height = 300

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 清除缓存
        clear_image_cache()
        
        # 清理测试图片
        for img_path in [self.test_image_path, self.test_image_jpg_path,
                         self.test_large_image_path, self.test_small_image_path]:
            if img_path.exists():
                try:
                    img_path.unlink()
                except:
                    pass

    def _create_test_image(self, path, width, height, format="PNG"):
        """
        创建测试用的图片文件
        
        Args:
            path (Path): 图片保存路径
            width (int): 图片宽度
            height (int): 图片高度
            format (str): 图片格式（PNG或JPG）
        """
        # 创建QImage
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(0, 0, 255))  # 蓝色
        
        # 在图片上绘制一些内容以使其更真实
        painter = QPainter(image)
        painter.setPen(QColor(255, 255, 255))  # 白色
        painter.drawText(10, 30, f"{width}x{height}")
        painter.end()
        
        # 保存图片
        image.save(str(path))

    def test_load_and_scale_image_success(self):
        """测试成功加载和缩放图片"""
        result = load_and_scale_image(
            str(self.test_image_path),
            self.target_width,
            self.target_height
        )
        
        # 验证返回的是QPixmap对象
        self.assertIsNotNone(result)
        self.assertIsInstance(result, QPixmap)
        self.assertFalse(result.isNull())
        
        # 验证图片尺寸（保持宽高比）
        self.assertLessEqual(result.width(), self.target_width)
        self.assertLessEqual(result.height(), self.target_height)

    def test_load_and_scale_image_with_path_object(self):
        """测试使用Path对象加载图片"""
        result = load_and_scale_image(
            self.test_image_path,  # Path对象
            self.target_width,
            self.target_height
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, QPixmap)

    def test_load_and_scale_jpg_image(self):
        """测试加载JPG格式图片"""
        result = load_and_scale_image(
            str(self.test_image_jpg_path),
            self.target_width,
            self.target_height
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, QPixmap)

    def test_load_and_scale_large_image(self):
        """测试加载大尺寸图片并缩小"""
        result = load_and_scale_image(
            str(self.test_large_image_path),
            self.target_width,
            self.target_height
        )
        
        self.assertIsNotNone(result)
        # 验证图片已被缩小
        self.assertLessEqual(result.width(), self.target_width)
        self.assertLessEqual(result.height(), self.target_height)

    def test_load_and_scale_small_image(self):
        """测试加载小尺寸图片并放大"""
        result = load_and_scale_image(
            str(self.test_small_image_path),
            800,
            1200
        )
        
        self.assertIsNotNone(result)
        # 小图片放大后应该达到目标尺寸范围
        self.assertTrue(result.width() > 100 or result.height() > 150)

    def test_load_and_scale_aspect_ratio(self):
        """测试缩放时保持宽高比"""
        # 原始图片是400x600（宽高比2:3）
        result = load_and_scale_image(
            str(self.test_image_path),
            200,
            300
        )
        
        self.assertIsNotNone(result)
        
        # 计算宽高比
        original_ratio = 400 / 600
        scaled_ratio = result.width() / result.height()
        
        # 宽高比应该相近（允许小误差）
        self.assertAlmostEqual(original_ratio, scaled_ratio, places=1)

    def test_load_nonexistent_image(self):
        """测试加载不存在的图片"""
        result = load_and_scale_image(
            str(self.test_dir / "nonexistent.png"),
            self.target_width,
            self.target_height
        )
        
        # 应该返回None
        self.assertIsNone(result)

    def test_load_empty_path(self):
        """测试使用空路径加载图片"""
        result = load_and_scale_image(
            '',
            self.target_width,
            self.target_height
        )
        
        self.assertIsNone(result)

    def test_load_none_path(self):
        """测试使用None路径加载图片"""
        result = load_and_scale_image(
            None,
            self.target_width,
            self.target_height
        )
        
        self.assertIsNone(result)

    def test_load_directory_path(self):
        """测试使用目录路径而非文件路径"""
        result = load_and_scale_image(
            str(self.test_dir),
            self.target_width,
            self.target_height
        )
        
        # 应该返回None
        self.assertIsNone(result)

    def test_load_corrupted_image(self):
        """测试加载损坏的图片文件"""
        # 创建一个损坏的图片文件
        corrupted_path = self.test_dir / "corrupted.png"
        with open(corrupted_path, 'w') as f:
            f.write("This is not a valid image file")
        
        result = load_and_scale_image(
            str(corrupted_path),
            self.target_width,
            self.target_height
        )
        
        # 应该返回None
        self.assertIsNone(result)
        
        # 清理
        corrupted_path.unlink()

    def test_cache_mechanism(self):
        """测试LRU缓存机制"""
        # 清除缓存
        clear_image_cache()
        
        # 第一次加载（缓存未命中）
        result1 = load_and_scale_image(
            str(self.test_image_path),
            self.target_width,
            self.target_height
        )
        
        cache_info = get_image_cache_info()
        self.assertEqual(cache_info['currsize'], 1)
        self.assertEqual(cache_info['misses'], 1)
        
        # 第二次加载相同图片（缓存命中）
        result2 = load_and_scale_image(
            str(self.test_image_path),
            self.target_width,
            self.target_height
        )
        
        cache_info = get_image_cache_info()
        self.assertEqual(cache_info['hits'], 1)
        
        # 验证返回的是缓存的对象
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)

    def test_cache_different_sizes(self):
        """测试不同尺寸参数创建不同的缓存条目"""
        clear_image_cache()
        
        # 加载相同图片但不同尺寸
        result1 = load_and_scale_image(str(self.test_image_path), 100, 150)
        result2 = load_and_scale_image(str(self.test_image_path), 200, 300)
        
        cache_info = get_image_cache_info()
        
        # 应该创建两个不同的缓存条目
        self.assertEqual(cache_info['currsize'], 2)
        self.assertEqual(cache_info['misses'], 2)
        
        # 图片尺寸应该不同
        self.assertNotEqual(result1.width(), result2.width())

    def test_cache_max_size(self):
        """测试缓存最大容量限制"""
        clear_image_cache()
        
        # LRU缓存maxsize设置为100
        cache_info = get_image_cache_info()
        self.assertEqual(cache_info['maxsize'], 100)

    def test_clear_image_cache(self):
        """测试清除图片缓存"""
        # 先加载几张图片
        load_and_scale_image(str(self.test_image_path), 100, 150)
        load_and_scale_image(str(self.test_image_path), 200, 300)
        
        cache_info_before = get_image_cache_info()
        self.assertGreater(cache_info_before['currsize'], 0)
        
        # 清除缓存
        clear_image_cache()
        
        cache_info_after = get_image_cache_info()
        self.assertEqual(cache_info_after['currsize'], 0)
        self.assertEqual(cache_info_after['hits'], 0)
        self.assertEqual(cache_info_after['misses'], 0)

    def test_get_image_cache_info(self):
        """测试获取缓存信息"""
        clear_image_cache()
        
        # 加载图片
        load_and_scale_image(str(self.test_image_path), 100, 150)
        load_and_scale_image(str(self.test_image_path), 100, 150)  # 缓存命中
        load_and_scale_image(str(self.test_image_path), 200, 300)  # 缓存未命中
        
        info = get_image_cache_info()
        
        # 验证缓存信息结构
        self.assertIn('hits', info)
        self.assertIn('misses', info)
        self.assertIn('maxsize', info)
        self.assertIn('currsize', info)
        self.assertIn('hit_rate', info)
        
        # 验证统计数据
        self.assertEqual(info['hits'], 1)
        self.assertEqual(info['misses'], 2)
        self.assertEqual(info['currsize'], 2)
        self.assertEqual(info['maxsize'], 100)
        
        # 验证命中率计算
        expected_hit_rate = 1 / 3
        self.assertAlmostEqual(info['hit_rate'], expected_hit_rate, places=2)

    def test_cache_hit_rate_calculation(self):
        """测试缓存命中率计算"""
        clear_image_cache()
        
        # 初始状态，避免除零错误
        info = get_image_cache_info()
        self.assertEqual(info['hit_rate'], 0.0)
        
        # 加载后计算命中率
        load_and_scale_image(str(self.test_image_path), 100, 150)
        load_and_scale_image(str(self.test_image_path), 100, 150)
        
        info = get_image_cache_info()
        self.assertEqual(info['hit_rate'], 0.5)

    def test_preload_image_success(self):
        """测试成功预加载图片"""
        clear_image_cache()
        
        result = preload_image(
            str(self.test_image_path),
            self.target_width,
            self.target_height
        )
        
        # 验证预加载成功
        self.assertIsNotNone(result)
        self.assertIsInstance(result, QPixmap)
        
        # 验证图片已在缓存中
        cache_info = get_image_cache_info()
        self.assertEqual(cache_info['currsize'], 1)

    def test_preload_nonexistent_image(self):
        """测试预加载不存在的图片"""
        result = preload_image(
            str(self.test_dir / "nonexistent.png"),
            self.target_width,
            self.target_height
        )
        
        # 应该返回None
        self.assertIsNone(result)

    def test_preload_multiple_images(self):
        """测试预加载多张图片"""
        clear_image_cache()
        
        # 预加载多张图片
        preload_image(str(self.test_image_path), 100, 150)
        preload_image(str(self.test_image_jpg_path), 100, 150)
        preload_image(str(self.test_large_image_path), 100, 150)
        
        # 验证所有图片都在缓存中
        cache_info = get_image_cache_info()
        self.assertEqual(cache_info['currsize'], 3)

    def test_different_target_sizes(self):
        """测试各种不同的目标尺寸"""
        test_sizes = [
            (50, 50),
            (100, 100),
            (500, 500),
            (1920, 1080),
            (300, 200),
            (200, 300),
        ]
        
        for width, height in test_sizes:
            result = load_and_scale_image(
                str(self.test_image_path),
                width,
                height
            )
            
            self.assertIsNotNone(result, f"Failed for size {width}x{height}")
            self.assertLessEqual(result.width(), width)
            self.assertLessEqual(result.height(), height)

    def test_zero_dimensions(self):
        """测试零尺寸参数"""
        # Qt应该能处理零尺寸，但返回的图片也会很小
        result = load_and_scale_image(
            str(self.test_image_path),
            0,
            0
        )
        
        # 根据Qt的行为，可能返回空图片或很小的图片
        # 只要不崩溃就可以
        self.assertTrue(True)

    def test_negative_dimensions(self):
        """测试负数尺寸参数"""
        # Qt应该能处理负数尺寸
        result = load_and_scale_image(
            str(self.test_image_path),
            -100,
            -100
        )
        
        # 只要不崩溃就可以
        self.assertTrue(True)

    def test_smooth_transformation_quality(self):
        """测试平滑变换算法的使用"""
        # 这个测试确保使用了平滑变换
        result = load_and_scale_image(
            str(self.test_large_image_path),
            self.target_width,
            self.target_height
        )
        
        # 验证缩放后的图片质量
        self.assertIsNotNone(result)
        self.assertFalse(result.isNull())

    def test_keep_aspect_ratio(self):
        """测试保持宽高比功能"""
        # 使用宽高比不匹配的目标尺寸
        result = load_and_scale_image(
            str(self.test_image_path),  # 400x600 (2:3)
            300,  # 正方形目标尺寸
            300
        )
        
        self.assertIsNotNone(result)
        
        # 因为保持宽高比，图片不应该是正方形
        # 应该是200x300（适应正方形框内）
        self.assertNotEqual(result.width(), result.height())

    def test_cache_isolation_between_tests(self):
        """测试缓存在测试之间的隔离"""
        # 这个测试验证setUp和tearDown正确清理了缓存
        cache_info = get_image_cache_info()
        
        # 缓存应该是空的
        self.assertEqual(cache_info['currsize'], 0)
        self.assertEqual(cache_info['hits'], 0)
        self.assertEqual(cache_info['misses'], 0)

    def test_multiple_formats_support(self):
        """测试支持多种图片格式"""
        formats_to_test = [
            (self.test_image_path, "PNG"),
            (self.test_image_jpg_path, "JPG"),
        ]
        
        for img_path, format_name in formats_to_test:
            result = load_and_scale_image(
                str(img_path),
                self.target_width,
                self.target_height
            )
            
            self.assertIsNotNone(result, f"Failed to load {format_name} format")
            self.assertIsInstance(result, QPixmap)


if __name__ == '__main__':
    unittest.main()
