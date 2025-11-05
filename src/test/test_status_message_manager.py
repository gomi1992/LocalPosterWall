"""
StatusMessageManager 测试模块

本模块包含对StatusMessageManager类的单元测试，测试内容包括：
- 单例模式测试
- 线程安全测试
- 状态消息显示测试
- 消息历史记录测试
- 消息类型和样式测试
- 状态栏集成测试
- 异常处理测试

使用unittest框架进行测试，模拟状态栏组件。
"""

import unittest
import time
import threading
from unittest import mock

# 导入被测试模块
from src.status_message_manager import StatusMessageManager


class TestStatusMessageManager(unittest.TestCase):
    """StatusMessageManager类的单元测试"""

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 清除单例实例，确保每个测试独立
        if hasattr(StatusMessageManager, '_instance'):
            delattr(StatusMessageManager, '_instance')
        
        # 创建mock状态栏
        self.mock_status_bar = mock.MagicMock()
        self.mock_status_bar.showMessage = mock.MagicMock()
        self.mock_status_bar.clearMessage = mock.MagicMock()
        self.mock_status_bar.setStyleSheet = mock.MagicMock()

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 清除单例实例
        if hasattr(StatusMessageManager, '_instance'):
            delattr(StatusMessageManager, '_instance')

    def test_initialization(self):
        """测试管理器初始化"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 验证状态栏已保存
        self.assertEqual(manager.status_bar, self.mock_status_bar)
        
        # 验证消息历史已初始化
        self.assertIsInstance(manager.message_history, list)
        self.assertEqual(len(manager.message_history), 0)
        
        # 验证当前消息为None
        self.assertIsNone(manager.current_message)
        self.assertIsNone(manager.current_message_type)

    def test_initialization_without_status_bar(self):
        """测试不带状态栏的初始化"""
        manager = StatusMessageManager()
        
        # 验证状态栏为None
        self.assertIsNone(manager.status_bar)
        
        # 验证其他属性已初始化
        self.assertIsInstance(manager.message_history, list)

    def test_singleton_pattern(self):
        """测试单例模式"""
        # 第一次获取实例
        instance1 = StatusMessageManager.instance(self.mock_status_bar)
        
        # 第二次获取实例
        instance2 = StatusMessageManager.instance()
        
        # 验证是同一个实例
        self.assertIs(instance1, instance2)

    def test_singleton_thread_safety(self):
        """测试单例模式的线程安全性"""
        instances = []
        
        def create_instance():
            instance = StatusMessageManager.instance(self.mock_status_bar)
            instances.append(instance)
        
        # 创建多个线程同时获取实例
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有实例都是同一个
        self.assertEqual(len(instances), 10)
        for instance in instances:
            self.assertIs(instance, instances[0])

    def test_set_status_bar(self):
        """测试设置状态栏"""
        manager = StatusMessageManager()
        
        # 设置状态栏
        manager.set_status_bar(self.mock_status_bar)
        
        # 验证状态栏已设置
        self.assertEqual(manager.status_bar, self.mock_status_bar)

    def test_set_status_bar_with_current_message(self):
        """测试有当前消息时设置状态栏"""
        manager = StatusMessageManager()
        
        # 先设置一条消息（不会显示，因为没有状态栏）
        manager.show_message("测试消息", "info")
        
        # 然后设置状态栏
        manager.set_status_bar(self.mock_status_bar)
        
        # 验证消息被重新显示
        self.mock_status_bar.showMessage.assert_called()

    def test_show_message(self):
        """测试显示消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 显示消息
        manager.show_message("测试消息", "info", 1000)
        
        # 验证状态栏方法被调用
        self.mock_status_bar.showMessage.assert_called_once_with("测试消息", 1000)
        
        # 验证当前消息已保存
        self.assertEqual(manager.current_message, "测试消息")
        self.assertEqual(manager.current_message_type, "info")

    def test_show_message_without_status_bar(self):
        """测试无状态栏时显示消息"""
        manager = StatusMessageManager()
        
        # 显示消息（不应该抛出异常）
        manager.show_message("测试消息", "info")
        
        # 验证消息被记录
        self.assertEqual(manager.current_message, "测试消息")
        self.assertEqual(len(manager.message_history), 1)

    def test_show_info_message(self):
        """测试显示信息消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_info_message("信息消息", 1000)
        
        # 验证消息类型为info
        self.assertEqual(manager.current_message_type, "info")
        self.mock_status_bar.showMessage.assert_called_once()

    def test_show_warning_message(self):
        """测试显示警告消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_warning_message("警告消息", 1000)
        
        # 验证消息类型为warning
        self.assertEqual(manager.current_message_type, "warning")
        self.mock_status_bar.showMessage.assert_called_once()

    def test_show_error_message(self):
        """测试显示错误消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_error_message("错误消息", 1000)
        
        # 验证消息类型为error
        self.assertEqual(manager.current_message_type, "error")
        self.mock_status_bar.showMessage.assert_called_once()

    def test_show_success_message(self):
        """测试显示成功消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_success_message("成功消息", 1000)
        
        # 验证消息类型为success
        self.assertEqual(manager.current_message_type, "success")
        self.mock_status_bar.showMessage.assert_called_once()

    def test_message_history(self):
        """测试消息历史记录"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 显示多条消息
        manager.show_message("消息1", "info")
        manager.show_message("消息2", "warning")
        manager.show_message("消息3", "error")
        
        # 验证历史记录
        history = manager.get_message_history()
        self.assertEqual(len(history), 3)
        
        # 验证历史记录内容
        self.assertEqual(history[0]['message'], "消息1")
        self.assertEqual(history[0]['type'], "info")
        self.assertEqual(history[1]['message'], "消息2")
        self.assertEqual(history[1]['type'], "warning")
        self.assertEqual(history[2]['message'], "消息3")
        self.assertEqual(history[2]['type'], "error")

    def test_message_history_timestamp(self):
        """测试消息历史记录包含时间戳"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_message("测试消息", "info")
        
        history = manager.get_message_history()
        
        # 验证包含时间戳字段
        self.assertIn('timestamp', history[0])
        self.assertIn('time_str', history[0])
        self.assertIsInstance(history[0]['timestamp'], float)
        self.assertIsInstance(history[0]['time_str'], str)

    def test_message_history_max_length(self):
        """测试消息历史记录最大长度限制"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 添加超过100条消息
        for i in range(150):
            manager.show_message(f"消息{i}", "info")
        
        # 验证历史记录不超过100条
        history = manager.get_message_history()
        self.assertEqual(len(history), 100)
        
        # 验证保留的是最新的100条
        self.assertEqual(history[0]['message'], "消息50")
        self.assertEqual(history[99]['message'], "消息149")

    def test_get_message_history_returns_copy(self):
        """测试获取消息历史返回副本"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_message("测试消息", "info")
        
        history = manager.get_message_history()
        
        # 修改返回的历史记录
        history.append({'message': '新消息', 'type': 'info'})
        
        # 验证原始历史记录未被修改
        original_history = manager.get_message_history()
        self.assertEqual(len(original_history), 1)

    def test_get_current_message(self):
        """测试获取当前消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 初始时无当前消息
        self.assertIsNone(manager.get_current_message())
        
        # 显示消息
        manager.show_message("测试消息", "info")
        
        # 获取当前消息
        current = manager.get_current_message()
        self.assertIsNotNone(current)
        if current:
            self.assertEqual(current[0], "测试消息")
            self.assertEqual(current[1], "info")

    def test_clear_message(self):
        """测试清除当前消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 显示消息
        manager.show_message("测试消息", "info")
        
        # 清除消息
        manager.clear_message()
        
        # 验证当前消息已清除
        self.assertIsNone(manager.current_message)
        self.assertIsNone(manager.current_message_type)
        
        # 验证状态栏清除方法被调用
        self.mock_status_bar.clearMessage.assert_called_once()

    def test_clear_message_without_status_bar(self):
        """测试无状态栏时清除消息"""
        manager = StatusMessageManager()
        
        manager.show_message("测试消息", "info")
        
        # 不应该抛出异常
        manager.clear_message()
        
        # 验证当前消息已清除
        self.assertIsNone(manager.current_message)

    def test_clear_history(self):
        """测试清除历史记录"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 添加一些消息
        manager.show_message("消息1", "info")
        manager.show_message("消息2", "warning")
        
        # 清除历史
        manager.clear_history()
        
        # 验证历史已清除
        self.assertEqual(len(manager.message_history), 0)

    def test_get_message_style_info(self):
        """测试获取info类型消息样式"""
        manager = StatusMessageManager()
        
        style = manager._get_message_style("info")
        
        # 验证样式包含预期内容
        self.assertIn("QStatusBar", style)
        self.assertIsInstance(style, str)

    def test_get_message_style_warning(self):
        """测试获取warning类型消息样式"""
        manager = StatusMessageManager()
        
        style = manager._get_message_style("warning")
        
        self.assertIn("QStatusBar", style)

    def test_get_message_style_error(self):
        """测试获取error类型消息样式"""
        manager = StatusMessageManager()
        
        style = manager._get_message_style("error")
        
        self.assertIn("QStatusBar", style)

    def test_get_message_style_success(self):
        """测试获取success类型消息样式"""
        manager = StatusMessageManager()
        
        style = manager._get_message_style("success")
        
        self.assertIn("QStatusBar", style)

    def test_get_message_style_unknown_type(self):
        """测试获取未知类型消息样式"""
        manager = StatusMessageManager()
        
        # 未知类型应该返回默认info样式
        style = manager._get_message_style("unknown")
        
        self.assertIn("QStatusBar", style)

    def test_update_status_bar_calls_methods(self):
        """测试更新状态栏调用正确方法"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager._update_status_bar("测试消息", "info", 1000)
        
        # 验证showMessage被调用
        self.mock_status_bar.showMessage.assert_called_once_with("测试消息", 1000)
        
        # 验证setStyleSheet被调用
        self.mock_status_bar.setStyleSheet.assert_called_once()

    def test_update_status_bar_without_show_message_method(self):
        """测试状态栏没有showMessage方法"""
        # 创建没有showMessage的mock对象
        mock_bar = mock.MagicMock(spec=[])
        manager = StatusMessageManager(mock_bar)
        
        # 不应该抛出异常
        manager._update_status_bar("测试消息", "info", 1000)

    def test_add_to_history_structure(self):
        """测试添加到历史记录的结构"""
        manager = StatusMessageManager()
        
        manager._add_to_history("测试消息", "info")
        
        # 验证历史记录结构
        self.assertEqual(len(manager.message_history), 1)
        entry = manager.message_history[0]
        
        # 验证字段
        self.assertIn('timestamp', entry)
        self.assertIn('message', entry)
        self.assertIn('type', entry)
        self.assertIn('time_str', entry)
        
        self.assertEqual(entry['message'], "测试消息")
        self.assertEqual(entry['type'], "info")

    def test_multiple_messages_update_current(self):
        """测试多条消息更新当前消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_message("消息1", "info")
        self.assertEqual(manager.current_message, "消息1")
        
        manager.show_message("消息2", "warning")
        self.assertEqual(manager.current_message, "消息2")
        self.assertEqual(manager.current_message_type, "warning")

    def test_show_message_with_zero_duration(self):
        """测试显示持续时间为0的消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_message("测试消息", "info", 0)
        
        # 验证duration参数为0
        self.mock_status_bar.showMessage.assert_called_once_with("测试消息", 0)

    def test_show_message_default_duration(self):
        """测试默认持续时间"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        # 不指定duration，默认为0
        manager.show_message("测试消息", "info")
        
        self.mock_status_bar.showMessage.assert_called_once_with("测试消息", 0)

    def test_exception_handling_in_show_message(self):
        """测试show_message中的异常处理"""
        # 创建会抛出异常的mock
        mock_bar = mock.MagicMock()
        mock_bar.showMessage.side_effect = Exception("Test error")
        
        manager = StatusMessageManager(mock_bar)
        
        # 不应该抛出异常
        manager.show_message("测试消息", "info")
        
        # 消息仍应被记录到历史
        self.assertEqual(len(manager.message_history), 1)

    def test_exception_handling_in_clear_message(self):
        """测试clear_message中的异常处理"""
        mock_bar = mock.MagicMock()
        mock_bar.clearMessage.side_effect = Exception("Test error")
        
        manager = StatusMessageManager(mock_bar)
        manager.show_message("测试消息", "info")
        
        # 不应该抛出异常
        manager.clear_message()
        
        # 当前消息应该被清除
        self.assertIsNone(manager.current_message)

    def test_chinese_message_support(self):
        """测试中文消息支持"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        chinese_message = "正在扫描电影文件夹..."
        manager.show_message(chinese_message, "info")
        
        # 验证中文消息正确保存
        self.assertEqual(manager.current_message, chinese_message)
        self.mock_status_bar.showMessage.assert_called_with(chinese_message, 0)

    def test_empty_message(self):
        """测试空消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        manager.show_message("", "info")
        
        # 空消息应该被接受
        self.assertEqual(manager.current_message, "")

    def test_long_message(self):
        """测试长消息"""
        manager = StatusMessageManager(self.mock_status_bar)
        
        long_message = "测试" * 100
        manager.show_message(long_message, "info")
        
        # 长消息应该被接受
        self.assertEqual(manager.current_message, long_message)


if __name__ == '__main__':
    unittest.main()
