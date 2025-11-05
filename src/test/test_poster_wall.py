"""
poster_wall 测试模块

本模块包含对poster_wall模块中所有组件的单元测试，测试内容包括：
- RatingLabel: 评分标签测试
- ResolutionLabel: 分辨率标签测试
- MoviePoster: 电影海报组件测试
- PosterWall: 海报墙容器测试

使用unittest框架和PySide6进行测试，创建临时文件和模拟数据。
"""

import unittest
import sys
import os
from pathlib import Path
from unittest import mock

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import Qt, QTimer

# 导入被测试模块
from src.poster_wall import RatingLabel, ResolutionLabel, MoviePoster, PosterWall


class TestRatingLabel(unittest.TestCase):
    """RatingLabel类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_initialization_with_float(self):
        """测试使用浮点数初始化评分标签"""
        label = RatingLabel(8.5)
        
        # 验证文本格式化为一位小数
        self.assertEqual(label.text(), "8.5")

    def test_initialization_with_string(self):
        """测试使用字符串初始化评分标签"""
        label = RatingLabel("7.8")
        
        # 验证文本格式化为一位小数
        self.assertEqual(label.text(), "7.8")

    def test_initialization_with_integer(self):
        """测试使用整数初始化评分标签"""
        label = RatingLabel(9)
        
        # 验证文本格式化为一位小数
        self.assertEqual(label.text(), "9.0")

    def test_initialization_with_invalid_rating(self):
        """测试使用无效评分初始化"""
        label = RatingLabel("invalid")
        
        # 应该直接使用字符串
        self.assertEqual(label.text(), "invalid")

    def test_alignment(self):
        """测试对齐方式"""
        label = RatingLabel(8.5)
        
        # 验证居中对齐
        self.assertEqual(label.alignment(), Qt.AlignmentFlag.AlignCenter)

    def test_style_applied(self):
        """测试样式是否已应用"""
        label = RatingLabel(8.5)
        
        # 验证样式表已设置
        self.assertNotEqual(label.styleSheet(), '')
        self.assertIn('QLabel', label.styleSheet())

    def test_high_precision_rating(self):
        """测试高精度评分"""
        label = RatingLabel(8.567)
        
        # 应该格式化为一位小数
        self.assertEqual(label.text(), "8.6")

    def test_zero_rating(self):
        """测试零评分"""
        label = RatingLabel(0)
        
        self.assertEqual(label.text(), "0.0")


class TestResolutionLabel(unittest.TestCase):
    """ResolutionLabel类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_initialization(self):
        """测试初始化分辨率标签"""
        label = ResolutionLabel("1080p")
        
        # 验证文本设置正确
        self.assertEqual(label.text(), "1080p")

    def test_different_resolutions(self):
        """测试不同的分辨率文本"""
        resolutions = ["720p", "1080p", "4K", "2160p", "HD"]
        
        for res in resolutions:
            label = ResolutionLabel(res)
            self.assertEqual(label.text(), res)

    def test_alignment(self):
        """测试对齐方式"""
        label = ResolutionLabel("1080p")
        
        # 验证居中对齐
        self.assertEqual(label.alignment(), Qt.AlignmentFlag.AlignCenter)

    def test_style_applied(self):
        """测试样式是否已应用"""
        label = ResolutionLabel("1080p")
        
        # 验证样式表已设置
        self.assertNotEqual(label.styleSheet(), '')
        self.assertIn('QLabel', label.styleSheet())

    def test_empty_text(self):
        """测试空文本"""
        label = ResolutionLabel("")
        
        self.assertEqual(label.text(), "")


class TestMoviePoster(unittest.TestCase):
    """MoviePoster类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        # 创建测试目录
        cls.test_dir = Path(__file__).parent / "test_poster_data"
        cls.test_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
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
        # Mock配置管理器
        self.mock_config_manager = mock.MagicMock()
        self.mock_config_manager.load_config.return_value = {
            'player_path': '',
            'movie_folders': []
        }
        
        # 创建测试海报图片
        self.test_poster_path = self.test_dir / "test_poster.png"
        self._create_test_poster(self.test_poster_path)
        
        # 基本电影信息
        self.basic_movie_info = {
            'title': '测试电影',
            'year': '2024',
            'rating': '8.5',
            'resolution': '1080p',
            'poster_path': str(self.test_poster_path),
            'video_path': '/path/to/video.mp4',
            'director': '张艺谋',
            'actor': '章子怡'
        }

    def tearDown(self):
        """每个测试用例执行后的清理"""
        if self.test_poster_path.exists():
            try:
                self.test_poster_path.unlink()
            except:
                pass

    def _create_test_poster(self, path):
        """创建测试海报图片"""
        image = QImage(400, 600, QImage.Format.Format_RGB32)
        image.fill(QColor(100, 150, 200))
        painter = QPainter(image)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(150, 300, "Test Poster")
        painter.end()
        image.save(str(path))

    def test_initialization(self):
        """测试海报组件初始化"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 验证组件大小
        self.assertEqual(poster.width(), 220)
        self.assertEqual(poster.height(), 380)
        
        # 验证电影信息已保存
        self.assertEqual(poster.movie_info, self.basic_movie_info)

    def test_ui_components_created(self):
        """测试UI组件是否正确创建"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 验证海报容器存在
        self.assertIsNotNone(poster.poster_container)
        self.assertEqual(poster.poster_container.width(), 208)
        self.assertEqual(poster.poster_container.height(), 312)
        
        # 验证海报标签存在
        self.assertIsNotNone(poster.poster_label)
        
        # 验证标题标签存在
        self.assertIsNotNone(poster.title_label)
        self.assertEqual(poster.title_label.text(), '测试电影')
        
        # 验证年份标签存在
        self.assertIsNotNone(poster.year_label)
        self.assertEqual(poster.year_label.text(), '2024')
        
        # 验证播放按钮存在
        self.assertIsNotNone(poster.play_button)
        self.assertEqual(poster.play_button.text(), '播放')

    def test_rating_label_created(self):
        """测试评分标签创建"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 验证评分标签存在
        self.assertIsNotNone(poster.rating_label)
        if poster.rating_label:
            self.assertEqual(poster.rating_label.text(), '8.5')

    def test_rating_label_not_created_when_missing(self):
        """测试缺少评分时不创建评分标签"""
        movie_info = self.basic_movie_info.copy()
        del movie_info['rating']
        
        poster = MoviePoster(movie_info, self.mock_config_manager)
        
        # 验证评分标签为None
        self.assertIsNone(poster.rating_label)

    def test_resolution_label_created(self):
        """测试分辨率标签创建"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 验证分辨率标签存在
        self.assertIsNotNone(poster.res_label)
        if poster.res_label:
            self.assertEqual(poster.res_label.text(), '1080p')

    def test_resolution_label_not_created_when_missing(self):
        """测试缺少分辨率时不创建分辨率标签"""
        movie_info = self.basic_movie_info.copy()
        del movie_info['resolution']
        
        poster = MoviePoster(movie_info, self.mock_config_manager)
        
        # 验证分辨率标签为None
        self.assertIsNone(poster.res_label)

    def test_load_poster_success(self):
        """测试成功加载海报"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 手动调用加载海报
        poster.load_poster()
        
        # 验证海报已加载
        pixmap = poster.poster_label.pixmap()
        self.assertIsNotNone(pixmap)

    def test_load_poster_with_nonexistent_file(self):
        """测试加载不存在的海报"""
        movie_info = self.basic_movie_info.copy()
        movie_info['poster_path'] = '/nonexistent/poster.png'
        
        poster = MoviePoster(movie_info, self.mock_config_manager)
        poster.load_poster()
        
        # 应该显示"无海报"
        self.assertEqual(poster.poster_label.text(), '无海报')

    def test_load_poster_with_empty_path(self):
        """测试空海报路径"""
        movie_info = self.basic_movie_info.copy()
        movie_info['poster_path'] = ''
        
        poster = MoviePoster(movie_info, self.mock_config_manager)
        poster.load_poster()
        
        # 应该显示"无海报"
        self.assertEqual(poster.poster_label.text(), '无海报')

    def test_show_no_poster(self):
        """测试显示无海报状态"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        poster.show_no_poster()
        
        # 验证显示"无海报"
        self.assertEqual(poster.poster_label.text(), '无海报')

    @mock.patch('src.poster_wall.MovieInfoDialog')
    def test_mouse_press_left_button(self, mock_dialog_class):
        """测试左键点击海报"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        mock_dialog = mock.MagicMock()
        mock_dialog_class.return_value = mock_dialog
        
        # 模拟左键点击
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QPointF
        
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(10, 10),
            QPointF(10, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        poster.mousePressEvent(event)
        
        # 验证对话框被创建
        mock_dialog_class.assert_called_once_with(self.basic_movie_info)
        mock_dialog.exec.assert_called_once()

    @mock.patch('src.poster_wall.subprocess.Popen')
    def test_play_movie_success(self, mock_popen):
        """测试成功播放电影"""
        # 创建临时播放器和视频文件
        test_player = self.test_dir / "player.exe"
        test_video = self.test_dir / "video.mp4"
        test_player.touch()
        test_video.touch()
        
        self.mock_config_manager.load_config.return_value = {
            'player_path': str(test_player)
        }
        
        movie_info = self.basic_movie_info.copy()
        movie_info['video_path'] = str(test_video)
        
        poster = MoviePoster(movie_info, self.mock_config_manager)
        
        # 执行播放
        poster.play_movie()
        
        # 验证播放器被调用
        mock_popen.assert_called_once_with([str(test_player), str(test_video)])
        
        # 清理
        test_player.unlink()
        test_video.unlink()

    def test_play_movie_no_player_configured(self):
        """测试未配置播放器"""
        self.mock_config_manager.load_config.return_value = {
            'player_path': ''
        }
        
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 不应该抛出异常
        poster.play_movie()

    def test_play_movie_nonexistent_player(self):
        """测试播放器不存在"""
        self.mock_config_manager.load_config.return_value = {
            'player_path': '/nonexistent/player.exe'
        }
        
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 不应该抛出异常
        poster.play_movie()

    def test_director_label_created(self):
        """测试导演标签创建"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 验证导演标签存在
        self.assertIsNotNone(poster.director_label)
        self.assertEqual(poster.director_label.text(), '张艺谋')

    def test_actor_label_created(self):
        """测试演员标签创建"""
        poster = MoviePoster(self.basic_movie_info, self.mock_config_manager)
        
        # 验证演员标签存在
        self.assertIsNotNone(poster.actor_label)
        self.assertEqual(poster.actor_label.text(), '章子怡')


class TestPosterWall(unittest.TestCase):
    """PosterWall类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """每个测试用例执行前的设置"""
        # Mock配置管理器
        self.mock_config_manager = mock.MagicMock()
        self.mock_config_manager.load_config.return_value = {
            'player_path': '',
            'movie_folders': []
        }
        
        # 测试电影列表
        self.test_movies = [
            {'title': '电影1', 'year': '2024', 'rating': '8.5'},
            {'title': '电影2', 'year': '2023', 'rating': '7.8'},
            {'title': '电影3', 'year': '2022', 'rating': '9.0'}
        ]

    def test_initialization(self):
        """测试海报墙初始化"""
        wall = PosterWall(self.mock_config_manager)
        
        # 验证配置管理器已保存
        self.assertEqual(wall.config_manager, self.mock_config_manager)
        
        # 验证电影列表初始化为空
        self.assertEqual(wall.current_movies, [])
        
        # 验证定时器已创建
        self.assertIsNotNone(wall.resize_timer)

    def test_ui_components_created(self):
        """测试UI组件是否正确创建"""
        wall = PosterWall(self.mock_config_manager)
        
        # 验证内容容器存在
        self.assertIsNotNone(wall.content)
        
        # 验证网格布局存在
        self.assertIsNotNone(wall.grid_layout)

    def test_style_applied(self):
        """测试样式是否已应用"""
        wall = PosterWall(self.mock_config_manager)
        
        # 验证样式表已设置
        self.assertNotEqual(wall.styleSheet(), '')
        self.assertIn('QScrollArea', wall.styleSheet())

    def test_calculate_layout_wide_window(self):
        """测试宽窗口的布局计算"""
        wall = PosterWall(self.mock_config_manager)
        
        # 设置窗口大小
        wall.resize(1200, 800)
        
        # 计算布局
        cols = wall.calculate_layout()
        
        # 宽窗口应该有多列
        self.assertGreater(cols, 1)

    def test_calculate_layout_narrow_window(self):
        """测试窄窗口的布局计算"""
        wall = PosterWall(self.mock_config_manager)
        
        # 设置窗口大小
        wall.resize(300, 800)
        
        # 计算布局
        cols = wall.calculate_layout()
        
        # 至少应该有1列
        self.assertGreaterEqual(cols, 1)

    def test_update_posters(self):
        """测试更新海报显示"""
        wall = PosterWall(self.mock_config_manager)
        
        # 更新海报
        wall.update_posters(self.test_movies)
        
        # 验证电影列表已保存
        self.assertEqual(wall.current_movies, self.test_movies)
        
        # 验证布局中有组件
        self.assertGreater(wall.grid_layout.count(), 0)

    def test_update_posters_empty_list(self):
        """测试更新为空列表"""
        wall = PosterWall(self.mock_config_manager)
        
        # 先添加一些海报
        wall.update_posters(self.test_movies)
        
        # 然后更新为空列表
        wall.update_posters([])
        
        # 验证电影列表为空
        self.assertEqual(wall.current_movies, [])
        
        # 验证布局被清空
        self.assertEqual(wall.grid_layout.count(), 0)

    def test_clear_posters(self):
        """测试清除海报"""
        wall = PosterWall(self.mock_config_manager)
        
        # 先添加一些海报
        wall.update_posters(self.test_movies)
        
        # 清除海报
        wall.clear_posters()
        
        # 验证电影列表为空
        self.assertEqual(wall.current_movies, [])
        
        # 验证布局被清空
        self.assertEqual(wall.grid_layout.count(), 0)

    def test_clear_posters_when_empty(self):
        """测试清除空海报墙"""
        wall = PosterWall(self.mock_config_manager)
        
        # 清除空海报墙不应该出错
        wall.clear_posters()
        
        # 验证电影列表为空
        self.assertEqual(wall.current_movies, [])

    def test_resize_event_triggers_delayed_resize(self):
        """测试窗口大小改变触发延迟重排"""
        wall = PosterWall(self.mock_config_manager)
        wall.current_movies = self.test_movies
        
        # Mock delayed_resize方法
        with mock.patch.object(wall, 'delayed_resize') as mock_delayed:
            # 改变窗口大小
            wall.resize(1000, 800)
            
            # 处理事件
            QApplication.processEvents()
            
            # 等待定时器触发
            QTimer.singleShot(200, lambda: None)
            QApplication.processEvents()

    def test_delayed_resize_with_movies(self):
        """测试有电影时的延迟重排"""
        wall = PosterWall(self.mock_config_manager)
        wall.current_movies = self.test_movies
        
        # Mock update_posters
        with mock.patch.object(wall, 'update_posters') as mock_update:
            wall.delayed_resize()
            
            # 验证update_posters被调用
            mock_update.assert_called_once_with(self.test_movies)

    def test_delayed_resize_without_movies(self):
        """测试没有电影时的延迟重排"""
        wall = PosterWall(self.mock_config_manager)
        wall.current_movies = []
        
        # Mock update_posters
        with mock.patch.object(wall, 'update_posters') as mock_update:
            wall.delayed_resize()
            
            # 验证update_posters未被调用
            mock_update.assert_not_called()

    def test_multiple_updates(self):
        """测试多次更新海报"""
        wall = PosterWall(self.mock_config_manager)
        
        # 第一次更新
        wall.update_posters(self.test_movies[:2])
        self.assertEqual(len(wall.current_movies), 2)
        
        # 第二次更新
        wall.update_posters(self.test_movies)
        self.assertEqual(len(wall.current_movies), 3)

    def test_grid_layout_spacing(self):
        """测试网格布局间距"""
        wall = PosterWall(self.mock_config_manager)
        
        # 验证间距设置
        self.assertEqual(wall.grid_layout.spacing(), 16)

    def test_widget_resizable(self):
        """测试滚动区域可调整大小"""
        wall = PosterWall(self.mock_config_manager)
        
        # 验证widgetResizable属性
        self.assertTrue(wall.widgetResizable())


if __name__ == '__main__':
    unittest.main()
