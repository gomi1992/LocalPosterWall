"""
CacheManager 测试模块

本模块包含对CacheManager类的单元测试，测试内容包括：
- 初始化功能测试
- 缓存读写测试
- Base64编解码测试
- 缓存清理测试
- 异常处理测试

使用unittest框架进行测试，模拟文件操作，避免实际的文件系统写入。
"""

import unittest
import json
import base64
import os
from pathlib import Path
from unittest import mock

# 导入被测试模块
from src.cache_manager import CacheManager


class TestCacheManager(unittest.TestCase):
    """CacheManager类的单元测试"""

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 创建一个临时路径用于测试
        self.test_cache_path = Path(__file__).parent / "test_cache.json"
        # 确保测试前不存在该文件
        if self.test_cache_path.exists():
            self.test_cache_path.unlink()
        # 创建一个CacheManager实例，使用临时路径
        self.cache_manager = CacheManager(str(self.test_cache_path))
        # 用于测试的示例数据
        self.sample_data = [
            {"title": "测试电影1", "year": 2022, "path": "/test/path1"},
            {"title": "测试电影2", "year": 2023, "path": "/test/path2"}
        ]

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 测试完成后删除临时文件
        if self.test_cache_path.exists():
            self.test_cache_path.unlink()

    def test_initialization_default_path(self):
        """测试默认路径初始化"""
        # 不指定路径初始化
        manager = CacheManager()
        # 验证默认路径是否正确设置为用户主目录下的.movie_wall_cache.json
        expected_path = Path.home() / '.movie_wall_cache.json'
        self.assertEqual(manager.cache_file, expected_path)

    def test_initialization_custom_path(self):
        """测试自定义路径初始化"""
        # 验证自定义路径是否正确设置
        self.assertEqual(self.cache_manager.cache_file, self.test_cache_path)

    def test_ensure_cache_directory(self):
        """测试确保缓存目录存在的功能"""
        # 使用嵌套目录路径
        nested_path = self.test_cache_path.parent / "nested" / "dir" / "cache.json"
        manager = CacheManager(str(nested_path))
        
        # 调用私有方法确保目录存在
        manager._ensure_cache_directory()
        
        # 验证目录是否创建成功
        self.assertTrue(nested_path.parent.exists())
        
        # 清理创建的目录
        nested_path.parent.rmdir()
        nested_path.parent.parent.rmdir()

    def test_b64encode_decode(self):
        """测试Base64编码和解码功能"""
        test_string = "测试字符串"
        
        # 编码
        encoded = self.cache_manager.b64encode(test_string)
        # 验证结果是否为字符串且不为空
        self.assertIsInstance(encoded, str)
        self.assertTrue(len(encoded) > 0)
        
        # 解码
        decoded = self.cache_manager.b64decode(encoded)
        # 验证解码结果是否与原始字符串一致
        self.assertEqual(decoded, test_string)

    def test_set_and_get_cache(self):
        """测试缓存的设置和获取功能"""
        # 设置缓存
        self.cache_manager.set_cache(self.sample_data)
        
        # 验证缓存文件是否创建
        self.assertTrue(self.test_cache_path.exists())
        
        # 获取缓存
        retrieved_data = self.cache_manager.get_cache()
        
        # 验证获取的数据是否与原始数据一致
        self.assertEqual(retrieved_data, self.sample_data)

    def test_get_cache_nonexistent_file(self):
        """测试获取不存在的缓存文件"""
        # 确保文件不存在
        if self.test_cache_path.exists():
            self.test_cache_path.unlink()
        
        # 获取不存在的缓存文件应返回空列表
        retrieved_data = self.cache_manager.get_cache()
        self.assertEqual(retrieved_data, [])

    def test_get_cache_empty_file(self):
        """测试获取空缓存文件"""
        # 创建空文件
        self.test_cache_path.touch()
        
        # 获取空缓存文件应返回空列表
        retrieved_data = self.cache_manager.get_cache()
        self.assertEqual(retrieved_data, [])

    def test_clear_cache(self):
        """测试清除缓存功能"""
        # 先设置缓存
        self.cache_manager.set_cache(self.sample_data)
        self.assertTrue(self.test_cache_path.exists())
        
        # 清除缓存
        self.cache_manager.clear_cache()
        
        # 验证缓存文件是否被删除
        self.assertFalse(self.test_cache_path.exists())

    def test_clear_cache_nonexistent(self):
        """测试清除不存在的缓存文件"""
        # 确保文件不存在
        if self.test_cache_path.exists():
            self.test_cache_path.unlink()
        
        # 清除不存在的缓存不应抛出异常
        try:
            self.cache_manager.clear_cache()
            # 如果执行到这里，表示没有抛出异常，测试通过
            cleared = True
        except Exception:
            cleared = False
        
        self.assertTrue(cleared)

    def test_get_cache_info(self):
        """测试获取缓存信息功能"""
        # 获取不存在的缓存文件信息
        info = self.cache_manager.get_cache_info()
        self.assertEqual(info['cache_file'], str(self.test_cache_path))
        self.assertFalse(info['exists'])
        self.assertEqual(info['size'], 0)
        self.assertIsNone(info['modified_time'])
        self.assertFalse(info['readable'])
        
        # 设置缓存后再次获取信息
        self.cache_manager.set_cache(self.sample_data)
        info = self.cache_manager.get_cache_info()
        self.assertTrue(info['exists'])
        self.assertTrue(info['size'] > 0)
        self.assertIsNotNone(info['modified_time'])
        self.assertTrue(info['readable'])

    def test_backup_cache(self):
        """测试备份缓存功能"""
        # 先设置缓存
        self.cache_manager.set_cache(self.sample_data)
        
        # 执行备份
        backup_path = self.cache_manager.backup_cache()
        
        # 验证备份文件是否创建成功
        self.assertIsNotNone(backup_path)
        self.assertTrue(Path(backup_path).exists())
        
        # 清理备份文件
        if Path(backup_path).exists():
            Path(backup_path).unlink()

    def test_backup_nonexistent_cache(self):
        """测试备份不存在的缓存文件"""
        # 确保文件不存在
        if self.test_cache_path.exists():
            self.test_cache_path.unlink()
        
        # 备份不存在的缓存
        backup_path = self.cache_manager.backup_cache()
        
        # 应返回None
        self.assertIsNone(backup_path)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_set_cache_with_invalid_data(self, mock_file):
        """测试使用无效数据设置缓存"""
        # 尝试使用非列表数据设置缓存
        invalid_data = {"not": "a list"}
        self.cache_manager.set_cache(invalid_data)
        
        # 验证文件没有被写入
        mock_file.assert_not_called()

    @mock.patch('json.loads')
    def test_json_decode_error_handling(self, mock_loads):
        """测试JSON解码错误处理"""
        # 模拟JSON解码错误
        mock_loads.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        
        # 创建一个包含无效JSON的文件
        with open(self.test_cache_path, 'w', encoding='utf-8') as f:
            f.write(base64.b64encode("invalid json".encode('utf-8')).decode('utf-8'))
        
        # 读取缓存应返回空列表
        retrieved_data = self.cache_manager.get_cache()
        self.assertEqual(retrieved_data, [])


if __name__ == '__main__':
    unittest.main()