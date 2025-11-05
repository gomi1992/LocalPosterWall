"""
ConfigManager 测试模块

本模块包含对ConfigManager类的单元测试，测试内容包括：
- 初始化功能测试
- 配置加载和保存测试
- 配置验证和修复测试
- 配置更新测试
- 配置备份测试
- 默认配置重置测试
- 兼容性处理测试
- 异常处理测试

使用unittest框架进行测试，模拟文件操作，避免实际修改用户配置。
"""

import unittest
import json
import os
from pathlib import Path
from unittest import mock

# 导入被测试模块
from src.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """ConfigManager类的单元测试"""

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 创建一个临时路径用于测试
        self.test_config_path = Path(__file__).parent / "test_config.json"
        # 确保测试前不存在该文件
        if self.test_config_path.exists():
            self.test_config_path.unlink()
        
        # 保存原始Path.home函数，用于后续模拟
        self.original_path_home = Path.home
        # 模拟Path.home返回测试目录，避免修改实际用户配置
        Path.home = classmethod(lambda cls: self.test_config_path.parent)
        
        # 创建一个ConfigManager实例，会自动使用模拟的home目录
        self.config_manager = ConfigManager()
        # 用于测试的示例配置
        self.sample_config = {
            'movie_folders': ['/test/path1', '/test/path2'],
            'player_path': '/usr/bin/mpv',
            'last_position': {'x': 100, 'y': 100, 'width': 800, 'height': 600}
        }
        # 旧版本配置示例
        self.old_version_config = {
            'movie_folder': '/test/old/path',
            'player_path': '/usr/bin/vlc'
        }

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 恢复原始Path.home函数
        Path.home = self.original_path_home
        # 测试完成后删除临时文件
        if self.test_config_path.exists():
            self.test_config_path.unlink()

    def test_initialization(self):
        """测试配置管理器初始化"""
        # 验证配置文件路径是否正确设置
        expected_path = self.test_config_path
        self.assertEqual(self.config_manager.config_file, expected_path)
        
        # 验证默认配置是否已设置
        default_config = {
            'movie_folders': [],
            'player_path': '',
            'last_position': None
        }
        self.assertEqual(self.config_manager.default_config, default_config)

    def test_save_and_load_config(self):
        """测试配置的保存和加载功能"""
        # 保存配置
        self.config_manager.save_config(self.sample_config)
        
        # 验证配置文件是否创建
        self.assertTrue(self.test_config_path.exists())
        
        # 加载配置
        loaded_config = self.config_manager.load_config()
        
        # 验证加载的数据是否与原始数据一致
        self.assertEqual(loaded_config, self.sample_config)

    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        # 确保文件不存在
        if self.test_config_path.exists():
            self.test_config_path.unlink()
        
        # 加载不存在的配置文件应返回默认配置
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config, self.config_manager.default_config)

    def test_validate_and_fix_config(self):
        """测试配置验证和修复功能"""
        # 创建一个不完整且有错误的配置
        invalid_config = {
            'movie_folders': 'not a list',  # 类型错误
            'player_path': None,           # 类型错误
            # 缺少last_position
        }
        
        # 使用内部方法验证和修复配置
        fixed_config = self.config_manager._validate_and_fix_config(invalid_config)
        
        # 验证修复后的配置
        self.assertIsInstance(fixed_config['movie_folders'], list)
        self.assertEqual(fixed_config['movie_folders'], [])
        self.assertIsInstance(fixed_config['player_path'], str)
        self.assertEqual(fixed_config['player_path'], '')
        self.assertIn('last_position', fixed_config)

    def test_update_config(self):
        """测试配置更新功能"""
        # 先保存初始配置
        initial_config = self.config_manager.default_config.copy()
        self.config_manager.save_config(initial_config)
        
        # 准备更新内容
        updates = {
            'movie_folders': ['/new/path'],
            'player_path': '/new/player'
        }
        
        # 更新配置
        self.config_manager.update_config(updates)
        
        # 加载更新后的配置
        updated_config = self.config_manager.load_config()
        
        # 验证更新是否成功
        self.assertEqual(updated_config['movie_folders'], updates['movie_folders'])
        self.assertEqual(updated_config['player_path'], updates['player_path'])
        # 验证未更新的字段保持不变
        self.assertEqual(updated_config['last_position'], initial_config['last_position'])

    def test_get_config_path(self):
        """测试获取配置文件路径功能"""
        config_path = self.config_manager.get_config_path()
        self.assertEqual(config_path, str(self.test_config_path))

    def test_backup_config(self):
        """测试配置备份功能"""
        # 先保存配置
        self.config_manager.save_config(self.sample_config)
        
        # 执行备份
        backup_path = self.config_manager.backup_config()
        
        # 验证备份文件是否创建成功
        self.assertIsNotNone(backup_path)
        self.assertTrue(Path(backup_path).exists())
        
        # 清理备份文件
        if Path(backup_path).exists():
            Path(backup_path).unlink()

    def test_backup_nonexistent_config(self):
        """测试备份不存在的配置文件"""
        # 确保文件不存在
        if self.test_config_path.exists():
            self.test_config_path.unlink()
        
        # 备份不存在的配置
        backup_path = self.config_manager.backup_config()
        
        # 应返回None
        self.assertIsNone(backup_path)

    def test_reset_to_default(self):
        """测试重置为默认配置功能"""
        # 先保存非默认配置
        self.config_manager.save_config(self.sample_config)
        
        # 重置为默认配置
        self.config_manager.reset_to_default()
        
        # 加载配置并验证是否为默认配置
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config, self.config_manager.default_config)

    def test_config_compatibility(self):
        """测试配置兼容性处理功能"""
        # 保存旧版本配置
        with open(self.test_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.old_version_config, f, ensure_ascii=False)
        
        # 创建新的ConfigManager实例，会触发兼容性检查
        new_manager = ConfigManager()
        
        # 加载更新后的配置
        updated_config = new_manager.load_config()
        
        # 验证旧配置是否成功迁移
        self.assertIn('movie_folders', updated_config)
        self.assertEqual(updated_config['movie_folders'], [self.old_version_config['movie_folder']])
        self.assertNotIn('movie_folder', updated_config)  # 旧字段应被移除
        self.assertEqual(updated_config['player_path'], self.old_version_config['player_path'])

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_save_config_with_invalid_data(self, mock_file):
        """测试使用无效数据保存配置"""
        # 尝试使用非字典数据保存配置
        invalid_data = "not a dict"
        self.config_manager.save_config(invalid_data)
        
        # 验证文件没有被写入
        mock_file.assert_not_called()

    @mock.patch('json.load')
    def test_json_decode_error_handling(self, mock_load):
        """测试JSON解码错误处理"""
        # 模拟JSON解码错误
        mock_load.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        
        # 创建一个包含无效JSON的文件
        with open(self.test_config_path, 'w', encoding='utf-8') as f:
            f.write("invalid json")
        
        # 读取配置应返回默认配置
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config, self.config_manager.default_config)

    def test_ensure_config_file_creates_default(self):
        """测试确保配置文件存在功能"""
        # 确保文件不存在
        if self.test_config_path.exists():
            self.test_config_path.unlink()
        
        # 调用_ensure_config_file方法
        self.config_manager._ensure_config_file()
        
        # 验证默认配置文件是否创建
        self.assertTrue(self.test_config_path.exists())
        
        # 验证内容是否为默认配置
        with open(self.test_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.assertEqual(config, self.config_manager.default_config)


if __name__ == '__main__':
    unittest.main()