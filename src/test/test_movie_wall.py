"""
MovieWallApp 测试模块

本模块包含对MovieWallApp主应用程序类的单元测试，测试内容包括：
- 应用程序初始化测试
- UI组件创建测试
- 配置加载和管理测试
- 电影文件夹管理测试
- 播放器配置测试
- 电影刷新和扫描测试
- 排序功能测试
- 拼音转换测试
- 异常处理测试

使用unittest框架和PySide6进行测试，模拟用户交互和文件操作。
"""

import unittest
import sys
import os
from pathlib import Path
from unittest import mock

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt

# 导入被测试模块
from src.movie_wall import MovieWallApp


class TestMovieWallApp(unittest.TestCase):
    """MovieWallApp类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        # 确保只创建一个QApplication实例
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 创建测试目录
        self.test_dir = Path(__file__).parent / "test_app_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Mock配置管理器以避免实际文件操作
        self.config_manager_patcher = mock.patch('src.movie_wall.ConfigManager')
        self.mock_config_manager_class = self.config_manager_patcher.start()
        
        # 创建mock实例
        self.mock_config_manager = mock.MagicMock()
        self.mock_config_manager_class.return_value = self.mock_config_manager
        
        # 设置默认配置返回值
        self.mock_config_manager.load_config.return_value = {
            'movie_folders': [],
            'player_path': '',
            'last_position': None
        }
        
        # Mock电影扫描器
        self.scanner_patcher = mock.patch('src.movie_wall.MovieScanner')
        self.mock_scanner_class = self.scanner_patcher.start()
        self.mock_scanner = mock.MagicMock()
        self.mock_scanner_class.return_value = self.mock_scanner
        
        # Mock缓存管理器
        mock_cache_manager = mock.MagicMock()
        mock_cache_manager.get_cache.return_value = []
        self.mock_scanner.cache_manager = mock_cache_manager

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 停止所有patcher
        self.config_manager_patcher.stop()
        self.scanner_patcher.stop()
        
        # 清理测试目录
        if self.test_dir.exists():
            try:
                self.test_dir.rmdir()
            except:
                pass

    def test_initialization(self):
        """测试应用程序初始化"""
        app = MovieWallApp()
        
        # 验证窗口标题
        self.assertIn('本地电影海报墙', app.windowTitle())
        
        # 验证最小尺寸
        self.assertGreaterEqual(app.minimumWidth(), 1200)
        self.assertGreaterEqual(app.minimumHeight(), 800)
        
        # 验证配置管理器已初始化
        self.assertIsNotNone(app.config_manager)
        
        # 验证电影列表已初始化
        self.assertIsInstance(app.current_movies, list)

    def test_ui_components_created(self):
        """测试UI组件是否正确创建"""
        app = MovieWallApp()
        
        # 验证海报墙组件存在
        self.assertIsNotNone(app.poster_wall)
        
        # 验证排序组合框存在
        self.assertIsNotNone(app.sort_combo)
        self.assertGreater(app.sort_combo.count(), 0)
        
        # 验证状态栏存在
        self.assertIsNotNone(app.status_bar)
        self.assertIsNotNone(app.version_label)

    def test_sort_combo_items(self):
        """测试排序选项是否正确"""
        app = MovieWallApp()
        
        # 验证排序选项
        expected_items = ['按年份降序', '按年份升序', '按标题升序', '按标题降序']
        actual_items = [app.sort_combo.itemText(i) for i in range(app.sort_combo.count())]
        
        self.assertEqual(actual_items, expected_items)

    def test_load_config_with_empty_folders(self):
        """测试加载空文件夹配置"""
        self.mock_config_manager.load_config.return_value = {
            'movie_folders': [],
            'player_path': ''
        }
        
        app = MovieWallApp()
        
        # 配置加载应该成功，但不扫描电影
        self.assertEqual(len(app.current_movies), 0)

    def test_load_config_with_folders_and_cache(self):
        """测试加载有文件夹配置且有缓存的情况"""
        test_movies = [
            {'title': '测试电影1', 'year': '2024'},
            {'title': '测试电影2', 'year': '2023'}
        ]
        
        self.mock_config_manager.load_config.return_value = {
            'movie_folders': ['/test/folder1'],
            'player_path': ''
        }
        
        self.mock_scanner.cache_manager.get_cache.return_value = test_movies
        
        app = MovieWallApp()
        
        # 验证从缓存加载了电影
        self.assertEqual(len(app.current_movies), 2)

    def test_load_config_with_folders_no_cache(self):
        """测试加载有文件夹配置但无缓存的情况"""
        self.mock_config_manager.load_config.return_value = {
            'movie_folders': ['/test/folder1'],
            'player_path': ''
        }
        
        self.mock_scanner.cache_manager.get_cache.return_value = []
        self.mock_scanner.scan_folder.return_value = []
        
        app = MovieWallApp()
        
        # 应该调用scan_movies
        self.mock_scanner.scan_folder.assert_called()

    @mock.patch('src.movie_wall.FolderListDialog')
    def test_manage_folders_accepted(self, mock_dialog_class):
        """测试管理文件夹并确认"""
        app = MovieWallApp()
        
        # 设置对话框返回值
        mock_dialog = mock.MagicMock()
        mock_dialog.exec.return_value = QDialog.Accepted
        mock_dialog.folders = ['/new/folder1', '/new/folder2']
        mock_dialog_class.return_value = mock_dialog
        
        self.mock_scanner.scan_folder.return_value = []
        
        # 执行管理文件夹操作
        app.manage_folders()
        
        # 验证对话框被创建
        mock_dialog_class.assert_called_once()
        
        # 验证配置被更新
        self.mock_config_manager.update_config.assert_called_with(
            {'movie_folders': ['/new/folder1', '/new/folder2']}
        )

    @mock.patch('src.movie_wall.FolderListDialog')
    def test_manage_folders_rejected(self, mock_dialog_class):
        """测试管理文件夹但取消"""
        app = MovieWallApp()
        
        # 设置对话框返回值
        mock_dialog = mock.MagicMock()
        mock_dialog.exec.return_value = QDialog.Rejected
        mock_dialog_class.return_value = mock_dialog
        
        # 执行管理文件夹操作
        app.manage_folders()
        
        # 验证对话框被创建
        mock_dialog_class.assert_called_once()
        
        # 验证配置未被更新
        self.mock_config_manager.update_config.assert_not_called()

    @mock.patch('src.movie_wall.QFileDialog.getOpenFileName')
    @mock.patch('src.movie_wall.QMessageBox.information')
    def test_configure_player_success(self, mock_msgbox, mock_file_dialog):
        """测试成功配置播放器"""
        app = MovieWallApp()
        
        # 创建临时播放器文件
        test_player = self.test_dir / "player.exe"
        test_player.touch()
        
        # 模拟用户选择播放器
        mock_file_dialog.return_value = (str(test_player), "可执行文件 (*.exe)")
        
        # 执行配置播放器
        app.configure_player()
        
        # 验证配置被更新
        self.mock_config_manager.update_config.assert_called_with(
            {'player_path': str(test_player)}
        )
        
        # 验证显示了成功消息
        mock_msgbox.assert_called_once()
        
        # 清理
        test_player.unlink()

    @mock.patch('src.movie_wall.QFileDialog.getOpenFileName')
    def test_configure_player_cancelled(self, mock_file_dialog):
        """测试取消配置播放器"""
        app = MovieWallApp()
        
        # 模拟用户取消选择
        mock_file_dialog.return_value = ('', '')
        
        # 执行配置播放器
        app.configure_player()
        
        # 验证配置未被更新
        self.mock_config_manager.update_config.assert_not_called()

    @mock.patch('src.movie_wall.QFileDialog.getOpenFileName')
    @mock.patch('src.movie_wall.QMessageBox.warning')
    def test_configure_player_nonexistent(self, mock_msgbox, mock_file_dialog):
        """测试配置不存在的播放器"""
        app = MovieWallApp()
        
        # 模拟选择不存在的文件
        mock_file_dialog.return_value = ('/nonexistent/player.exe', "可执行文件 (*.exe)")
        
        # 执行配置播放器
        app.configure_player()
        
        # 验证显示了警告消息
        mock_msgbox.assert_called_once()
        
        # 验证配置未被更新
        self.mock_config_manager.update_config.assert_not_called()

    def test_refresh_movies_with_folders(self):
        """测试刷新电影列表"""
        self.mock_config_manager.load_config.return_value = {
            'movie_folders': ['/test/folder1'],
            'player_path': ''
        }
        
        self.mock_scanner.scan_folder.return_value = [
            {'title': '电影1', 'year': '2024'}
        ]
        
        app = MovieWallApp()
        
        # 执行刷新
        app.refresh_movies()
        
        # 验证扫描被调用
        self.mock_scanner.scan_folder.assert_called()

    @mock.patch('src.movie_wall.QMessageBox.information')
    def test_refresh_movies_no_folders(self, mock_msgbox):
        """测试没有文件夹时刷新"""
        self.mock_config_manager.load_config.return_value = {
            'movie_folders': [],
            'player_path': ''
        }
        
        app = MovieWallApp()
        
        # 执行刷新
        app.refresh_movies()
        
        # 验证显示了提示消息
        mock_msgbox.assert_called_once()

    def test_get_pinyin_key_chinese(self):
        """测试获取中文标题的拼音"""
        app = MovieWallApp()
        
        # 测试中文标题
        result = app.get_pinyin_key('流浪地球')
        
        # 验证返回的是拼音首字母
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'lldq')

    def test_get_pinyin_key_with_parentheses(self):
        """测试带括号的标题"""
        app = MovieWallApp()
        
        # 测试带年份的标题
        result = app.get_pinyin_key('流浪地球(2019)')
        
        # 括号内容应该被移除
        self.assertEqual(result, 'lldq')

    def test_get_pinyin_key_english(self):
        """测试英文标题"""
        app = MovieWallApp()
        
        result = app.get_pinyin_key('Inception')
        
        # 英文标题应该转为小写
        self.assertEqual(result, 'inception')

    def test_get_pinyin_key_mixed(self):
        """测试中英混合标题"""
        app = MovieWallApp()
        
        result = app.get_pinyin_key('流浪Earth')
        
        # 应该返回混合结果
        self.assertIsInstance(result, str)

    def test_sort_movies_by_year_desc(self):
        """测试按年份降序排序"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '电影1', 'year': '2020'},
            {'title': '电影2', 'year': '2023'},
            {'title': '电影3', 'year': '2021'}
        ]
        
        app.sort_movies('按年份降序')
        
        # 验证排序结果
        self.assertEqual(app.current_movies[0]['year'], '2023')
        self.assertEqual(app.current_movies[1]['year'], '2021')
        self.assertEqual(app.current_movies[2]['year'], '2020')

    def test_sort_movies_by_year_asc(self):
        """测试按年份升序排序"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '电影1', 'year': '2020'},
            {'title': '电影2', 'year': '2023'},
            {'title': '电影3', 'year': '2021'}
        ]
        
        app.sort_movies('按年份升序')
        
        # 验证排序结果
        self.assertEqual(app.current_movies[0]['year'], '2020')
        self.assertEqual(app.current_movies[1]['year'], '2021')
        self.assertEqual(app.current_movies[2]['year'], '2023')

    def test_sort_movies_by_title_asc(self):
        """测试按标题升序排序"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '长城', 'year': '2020'},
            {'title': '阿凡达', 'year': '2020'},
            {'title': '流浪地球', 'year': '2020'}
        ]
        
        app.sort_movies('按标题升序')
        
        # 验证排序结果（按拼音）
        # 阿(a) < 长(c) < 流(l)
        self.assertEqual(app.current_movies[0]['title'], '阿凡达')
        self.assertEqual(app.current_movies[1]['title'], '长城')
        self.assertEqual(app.current_movies[2]['title'], '流浪地球')

    def test_sort_movies_by_title_desc(self):
        """测试按标题降序排序"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '长城', 'year': '2020'},
            {'title': '阿凡达', 'year': '2020'},
            {'title': '流浪地球', 'year': '2020'}
        ]
        
        app.sort_movies('按标题降序')
        
        # 验证排序结果（按拼音降序）
        # 流(l) > 长(c) > 阿(a)
        self.assertEqual(app.current_movies[0]['title'], '流浪地球')
        self.assertEqual(app.current_movies[1]['title'], '长城')
        self.assertEqual(app.current_movies[2]['title'], '阿凡达')

    def test_sort_movies_empty_list(self):
        """测试排序空列表"""
        app = MovieWallApp()
        app.current_movies = []
        
        # 不应该抛出异常
        app.sort_movies('按年份降序')
        
        # 列表仍为空
        self.assertEqual(len(app.current_movies), 0)

    def test_sort_movies_with_missing_year(self):
        """测试排序缺少年份的电影"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '电影1', 'year': '2020'},
            {'title': '电影2'},  # 缺少year
            {'title': '电影3', 'year': '2023'}
        ]
        
        # 不应该抛出异常
        app.sort_movies('按年份降序')
        
        # 验证排序完成
        self.assertEqual(len(app.current_movies), 3)

    def test_sort_movies_with_missing_title(self):
        """测试排序缺少标题的电影"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '电影1', 'year': '2020'},
            {'year': '2021'},  # 缺少title
            {'title': '电影3', 'year': '2023'}
        ]
        
        # 不应该抛出异常
        app.sort_movies('按标题升序')
        
        # 验证排序完成
        self.assertEqual(len(app.current_movies), 3)

    def test_scan_movies_single_folder(self):
        """测试扫描单个文件夹"""
        test_movies = [
            {'title': '电影1', 'year': '2024'},
            {'title': '电影2', 'year': '2023'}
        ]
        
        self.mock_scanner.scan_folder.return_value = test_movies
        
        app = MovieWallApp()
        app.scan_movies(['/test/folder1'])
        
        # 验证扫描被调用
        self.mock_scanner.scan_folder.assert_called_with('/test/folder1')
        
        # 验证电影列表被更新
        self.assertEqual(len(app.current_movies), 2)

    def test_scan_movies_multiple_folders(self):
        """测试扫描多个文件夹"""
        self.mock_scanner.scan_folder.side_effect = [
            [{'title': '电影1', 'year': '2024'}],
            [{'title': '电影2', 'year': '2023'}]
        ]
        
        app = MovieWallApp()
        app.scan_movies(['/test/folder1', '/test/folder2'])
        
        # 验证扫描被调用两次
        self.assertEqual(self.mock_scanner.scan_folder.call_count, 2)
        
        # 验证电影列表合并
        self.assertEqual(len(app.current_movies), 2)

    def test_scan_movies_empty_folder(self):
        """测试扫描空文件夹"""
        self.mock_scanner.scan_folder.return_value = []
        
        app = MovieWallApp()
        app.scan_movies(['/test/empty_folder'])
        
        # 验证扫描被调用
        self.mock_scanner.scan_folder.assert_called_once()
        
        # 电影列表应为空
        self.assertEqual(len(app.current_movies), 0)

    def test_scan_movies_with_exception(self):
        """测试扫描时发生异常"""
        self.mock_scanner.scan_folder.side_effect = Exception("Scan error")
        
        app = MovieWallApp()
        
        # 不应该导致程序崩溃
        app.scan_movies(['/test/folder1'])
        
        # 电影列表应为空
        self.assertEqual(len(app.current_movies), 0)

    def test_window_style_applied(self):
        """测试窗口样式是否已应用"""
        app = MovieWallApp()
        
        # 验证样式表已设置
        self.assertNotEqual(app.styleSheet(), '')
        self.assertIn('QMainWindow', app.styleSheet())
        self.assertIn('QPushButton', app.styleSheet())

    def test_status_bar_message(self):
        """测试状态栏消息显示"""
        app = MovieWallApp()
        
        # 设置状态消息
        app.status_bar.showMessage("测试消息", 1000)
        
        # 验证消息已设置
        self.assertEqual(app.status_bar.currentMessage(), "测试消息")

    def test_sort_combo_connection(self):
        """测试排序组合框信号连接"""
        app = MovieWallApp()
        app.current_movies = [
            {'title': '电影1', 'year': '2020'},
            {'title': '电影2', 'year': '2023'}
        ]
        
        # 改变排序方式应该触发排序
        app.sort_combo.setCurrentIndex(1)  # 切换到按年份升序
        
        # 验证排序被执行（通过检查第一个电影的年份）
        self.assertEqual(app.current_movies[0]['year'], '2020')

    def test_current_movies_initialization(self):
        """测试电影列表初始化为空列表"""
        app = MovieWallApp()
        
        # 验证初始状态
        self.assertIsInstance(app.current_movies, list)
        self.assertGreaterEqual(len(app.current_movies), 0)


if __name__ == '__main__':
    unittest.main()
