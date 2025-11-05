"""
MovieInfoDialog 测试模块

本模块包含对MovieInfoDialog类的单元测试，测试内容包括：
- 对话框初始化测试
- UI组件创建测试
- 海报加载功能测试
- NFO文件解析测试
- 延迟加载机制测试
- 信息显示测试
- 异常处理测试

使用unittest框架和PySide6进行测试，创建临时文件和模拟数据。
"""

import unittest
import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QTimer

# 导入被测试模块
from src.movie_info_dialog import MovieInfoDialog


class TestMovieInfoDialog(unittest.TestCase):
    """MovieInfoDialog类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        # 确保只创建一个QApplication实例
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        # 创建测试文件目录
        cls.test_dir = Path(__file__).parent / "test_movie_data"
        cls.test_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """测试类清理：删除测试文件目录"""
        # 清理测试文件
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
        # 创建测试文件路径
        self.test_poster_path = self.test_dir / "test_poster.png"
        self.test_nfo_path = self.test_dir / "test_movie.nfo"
        self.test_video_path = self.test_dir / "test_movie.mp4"
        
        # 创建测试海报图片
        self._create_test_poster(self.test_poster_path)
        
        # 创建测试NFO文件
        self._create_test_nfo(self.test_nfo_path)
        
        # 创建测试视频文件（空文件）
        self.test_video_path.touch()
        
        # 基本电影信息
        self.basic_movie_info = {
            'title': '测试电影',
            'year': '2024',
            'rating': '8.5',
            'resolution': '1080p',
            'poster_path': str(self.test_poster_path),
            'video_path': str(self.test_video_path),
            'nfo_path': str(self.test_nfo_path),
            'director': '张艺谋',
            'actor': '章子怡, 巩俐'
        }

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 清理测试文件
        for file_path in [self.test_poster_path, self.test_nfo_path, self.test_video_path]:
            if file_path.exists():
                try:
                    file_path.unlink()
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

    def _create_test_nfo(self, path, include_outline=True):
        """创建测试NFO文件"""
        root = ET.Element("movie")
        
        title = ET.SubElement(root, "title")
        title.text = "测试电影"
        
        year = ET.SubElement(root, "year")
        year.text = "2024"
        
        if include_outline:
            outline = ET.SubElement(root, "outline")
            outline.text = "这是一部测试电影的剧情简介。讲述了一个精彩的故事。"
        
        rating = ET.SubElement(root, "rating")
        rating.text = "8.5"
        
        tree = ET.ElementTree(root)
        tree.write(str(path), encoding='utf-8', xml_declaration=True)

    def test_initialization(self):
        """测试对话框初始化"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 验证窗口标题
        self.assertIn('测试电影', dialog.windowTitle())
        self.assertIn('影片详情', dialog.windowTitle())
        
        # 验证是否为模态对话框
        self.assertTrue(dialog.isModal())
        
        # 验证最小尺寸
        self.assertGreaterEqual(dialog.minimumWidth(), 500)
        self.assertGreaterEqual(dialog.minimumHeight(), 600)
        
        # 验证电影信息已保存
        self.assertEqual(dialog.movie_info, self.basic_movie_info)

    def test_initialization_with_unknown_title(self):
        """测试使用未知标题初始化"""
        movie_info = {}
        dialog = MovieInfoDialog(movie_info)
        
        # 窗口标题应包含"未知电影"
        self.assertIn('未知电影', dialog.windowTitle())

    def test_ui_components_created(self):
        """测试UI组件是否正确创建"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 验证滚动容器存在
        self.assertIsNotNone(dialog.scroll_container)
        self.assertIsNotNone(dialog.scroll)
        
        # 验证海报标签存在
        self.assertIsNotNone(dialog.poster_label)
        self.assertIsNotNone(dialog.poster_container)
        
        # 验证剧情简介标签存在
        self.assertIsNotNone(dialog.outline)

    def test_poster_label_size(self):
        """测试海报标签尺寸"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 验证海报标签尺寸
        self.assertEqual(dialog.poster_label.width(), 208)
        self.assertEqual(dialog.poster_label.height(), 312)
        
        # 验证海报容器尺寸
        self.assertEqual(dialog.poster_container.width(), 208)
        self.assertEqual(dialog.poster_container.height(), 312)

    @mock.patch('src.movie_info_dialog.QTimer.singleShot')
    def test_delayed_loading_setup(self, mock_timer):
        """测试延迟加载机制设置"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 验证QTimer.singleShot被调用了两次（海报和NFO）
        self.assertGreaterEqual(mock_timer.call_count, 2)

    def test_load_poster_success(self):
        """测试成功加载海报"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 手动调用加载海报
        dialog.load_poster()
        
        # 验证海报已设置
        pixmap = dialog.poster_label.pixmap()
        self.assertIsNotNone(pixmap)
        self.assertFalse(pixmap.isNull())

    def test_load_poster_with_nonexistent_file(self):
        """测试加载不存在的海报文件"""
        movie_info = self.basic_movie_info.copy()
        movie_info['poster_path'] = str(self.test_dir / "nonexistent.png")
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_poster()
        
        # 应该显示"暂无海报"
        self.assertEqual(dialog.poster_label.text(), "暂无海报")

    def test_load_poster_with_empty_path(self):
        """测试使用空路径加载海报"""
        movie_info = self.basic_movie_info.copy()
        movie_info['poster_path'] = ''
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_poster()
        
        # 应该显示"暂无海报"
        self.assertEqual(dialog.poster_label.text(), "暂无海报")

    def test_load_poster_with_none_path(self):
        """测试使用None路径加载海报"""
        movie_info = self.basic_movie_info.copy()
        del movie_info['poster_path']  # 移除键以模拟None
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_poster()
        
        # 应该显示"暂无海报"
        self.assertEqual(dialog.poster_label.text(), "暂无海报")

    def test_show_no_poster(self):
        """测试显示无海报状态"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        dialog.show_no_poster()
        
        # 验证显示"暂无海报"文本
        self.assertEqual(dialog.poster_label.text(), "暂无海报")
        
        # 验证对齐方式为居中
        self.assertEqual(dialog.poster_label.alignment(), Qt.AlignmentFlag.AlignCenter)

    def test_load_nfo_content_success(self):
        """测试成功加载NFO内容"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 手动调用加载NFO内容
        dialog.load_nfo_content()
        
        # 验证剧情简介已设置
        outline_text = dialog.outline.text()
        self.assertIn("剧情简介", outline_text)
        self.assertIn("测试电影的剧情简介", outline_text)

    def test_load_nfo_content_with_nonexistent_file(self):
        """测试加载不存在的NFO文件"""
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(self.test_dir / "nonexistent.nfo")
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_nfo_content()
        
        # 应该显示"暂无剧情简介"
        self.assertEqual(dialog.outline.text(), "暂无剧情简介")

    def test_load_nfo_content_with_empty_path(self):
        """测试使用空路径加载NFO"""
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = ''
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_nfo_content()
        
        # 应该显示"暂无剧情简介"
        self.assertEqual(dialog.outline.text(), "暂无剧情简介")

    def test_load_nfo_content_with_none_path(self):
        """测试使用None路径加载NFO"""
        movie_info = self.basic_movie_info.copy()
        del movie_info['nfo_path']  # 移除键以模拟None
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_nfo_content()
        
        # 应该显示"暂无剧情简介"
        self.assertEqual(dialog.outline.text(), "暂无剧情简介")

    def test_load_nfo_content_without_outline(self):
        """测试加载没有剧情简介的NFO文件"""
        # 创建没有outline的NFO文件
        nfo_path = self.test_dir / "no_outline.nfo"
        self._create_test_nfo(nfo_path, include_outline=False)
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(nfo_path)
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_nfo_content()
        
        # 应该显示"暂无剧情简介"
        self.assertEqual(dialog.outline.text(), "暂无剧情简介")
        
        # 清理
        nfo_path.unlink()

    def test_load_nfo_content_with_corrupted_xml(self):
        """测试加载损坏的NFO文件"""
        # 创建损坏的XML文件
        corrupted_nfo = self.test_dir / "corrupted.nfo"
        with open(corrupted_nfo, 'w', encoding='utf-8') as f:
            f.write("This is not valid XML content")
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(corrupted_nfo)
        
        dialog = MovieInfoDialog(movie_info)
        dialog.load_nfo_content()
        
        # 应该显示解析失败的消息
        self.assertEqual(dialog.outline.text(), "剧情简介解析失败")
        
        # 清理
        corrupted_nfo.unlink()

    def test_extract_outline_with_outline_tag(self):
        """测试从outline标签提取剧情简介"""
        nfo_path = self.test_dir / "outline_tag.nfo"
        
        root = ET.Element("movie")
        outline = ET.SubElement(root, "outline")
        outline.text = "这是通过outline标签的简介"
        
        tree = ET.ElementTree(root)
        tree.write(str(nfo_path), encoding='utf-8')
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(nfo_path)
        
        dialog = MovieInfoDialog(movie_info)
        result = dialog._extract_outline(ET.parse(nfo_path).getroot())
        
        self.assertEqual(result, "这是通过outline标签的简介")
        
        # 清理
        nfo_path.unlink()

    def test_extract_outline_with_plot_tag(self):
        """测试从plot标签提取剧情简介"""
        nfo_path = self.test_dir / "plot_tag.nfo"
        
        root = ET.Element("movie")
        plot = ET.SubElement(root, "plot")
        plot.text = "这是通过plot标签的简介"
        
        tree = ET.ElementTree(root)
        tree.write(str(nfo_path), encoding='utf-8')
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(nfo_path)
        
        dialog = MovieInfoDialog(movie_info)
        result = dialog._extract_outline(ET.parse(nfo_path).getroot())
        
        self.assertEqual(result, "这是通过plot标签的简介")
        
        # 清理
        nfo_path.unlink()

    def test_extract_outline_with_nested_tags(self):
        """测试从嵌套标签中提取剧情简介"""
        nfo_path = self.test_dir / "nested_tag.nfo"
        
        root = ET.Element("movie")
        info = ET.SubElement(root, "info")
        outline = ET.SubElement(info, "outline")
        outline.text = "这是嵌套在info下的简介"
        
        tree = ET.ElementTree(root)
        tree.write(str(nfo_path), encoding='utf-8')
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(nfo_path)
        
        dialog = MovieInfoDialog(movie_info)
        result = dialog._extract_outline(ET.parse(nfo_path).getroot())
        
        self.assertEqual(result, "这是嵌套在info下的简介")
        
        # 清理
        nfo_path.unlink()

    def test_extract_outline_with_empty_tag(self):
        """测试提取空的剧情简介标签"""
        nfo_path = self.test_dir / "empty_outline.nfo"
        
        root = ET.Element("movie")
        outline = ET.SubElement(root, "outline")
        outline.text = ""
        
        tree = ET.ElementTree(root)
        tree.write(str(nfo_path), encoding='utf-8')
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(nfo_path)
        
        dialog = MovieInfoDialog(movie_info)
        result = dialog._extract_outline(ET.parse(nfo_path).getroot())
        
        # 空文本应该返回None
        self.assertIsNone(result)
        
        # 清理
        nfo_path.unlink()

    def test_extract_outline_returns_none(self):
        """测试未找到剧情简介时返回None"""
        nfo_path = self.test_dir / "no_outline_tags.nfo"
        
        root = ET.Element("movie")
        title = ET.SubElement(root, "title")
        title.text = "测试电影"
        
        tree = ET.ElementTree(root)
        tree.write(str(nfo_path), encoding='utf-8')
        
        movie_info = self.basic_movie_info.copy()
        movie_info['nfo_path'] = str(nfo_path)
        
        dialog = MovieInfoDialog(movie_info)
        result = dialog._extract_outline(ET.parse(nfo_path).getroot())
        
        self.assertIsNone(result)
        
        # 清理
        nfo_path.unlink()

    def test_info_labels_display(self):
        """测试信息标签显示"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 通过查找QLabel组件验证信息显示
        labels = dialog.scroll_container.findChildren(QLabel)
        
        # 应该有多个标签（标题、年份、评分、分辨率、导演、演员、剧情简介、海报）
        self.assertGreater(len(labels), 5)

    def test_movie_info_with_missing_fields(self):
        """测试缺少字段的电影信息"""
        minimal_info = {
            'title': '极简电影'
        }
        
        dialog = MovieInfoDialog(minimal_info)
        
        # 应该能够正常创建对话框
        self.assertIsNotNone(dialog)
        self.assertIn('极简电影', dialog.windowTitle())

    def test_movie_info_with_all_fields(self):
        """测试包含所有字段的电影信息"""
        complete_info = {
            'title': '完整电影',
            'year': '2024',
            'rating': '9.5',
            'resolution': '4K',
            'poster_path': str(self.test_poster_path),
            'video_path': str(self.test_video_path),
            'nfo_path': str(self.test_nfo_path),
            'director': '克里斯托弗·诺兰',
            'actor': '马修·麦康纳, 安妮·海瑟薇'
        }
        
        dialog = MovieInfoDialog(complete_info)
        
        # 验证对话框创建成功
        self.assertIsNotNone(dialog)
        self.assertIn('完整电影', dialog.windowTitle())

    def test_dialog_style_applied(self):
        """测试对话框样式是否已应用"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 验证样式表已设置
        self.assertNotEqual(dialog.styleSheet(), '')
        self.assertIn('QDialog', dialog.styleSheet())
        self.assertIn('QScrollArea', dialog.styleSheet())

    def test_scroll_area_properties(self):
        """测试滚动区域属性"""
        dialog = MovieInfoDialog(self.basic_movie_info)
        
        # 验证滚动区域存在
        self.assertIsNotNone(dialog.scroll)
        self.assertIsNotNone(dialog.scroll_container)

    @mock.patch('src.movie_info_dialog.load_and_scale_image')
    def test_load_poster_with_failed_scaling(self, mock_load_scale):
        """测试海报缩放失败的情况"""
        mock_load_scale.return_value = None
        
        dialog = MovieInfoDialog(self.basic_movie_info)
        dialog.load_poster()
        
        # 应该显示无海报状态
        self.assertEqual(dialog.poster_label.text(), "暂无海报")

    @mock.patch('src.movie_info_dialog.load_and_scale_image')
    def test_load_poster_exception_handling(self, mock_load_scale):
        """测试加载海报时的异常处理"""
        mock_load_scale.side_effect = Exception("Test exception")
        
        dialog = MovieInfoDialog(self.basic_movie_info)
        dialog.load_poster()
        
        # 应该显示无海报状态
        self.assertEqual(dialog.poster_label.text(), "暂无海报")

    def test_load_nfo_content_exception_handling(self):
        """测试加载NFO内容时的异常处理"""
        movie_info = self.basic_movie_info.copy()
        
        dialog = MovieInfoDialog(movie_info)
        
        # 模拟异常
        with mock.patch('xml.etree.ElementTree.parse', side_effect=Exception("Test exception")):
            dialog.load_nfo_content()
            
            # 应该显示加载失败的消息
            self.assertEqual(dialog.outline.text(), "剧情简介加载失败")

    def test_chinese_character_support(self):
        """测试中文字符支持"""
        chinese_info = {
            'title': '我和我的祖国',
            'year': '2019',
            'rating': '7.8',
            'resolution': '1080p',
            'director': '陈凯歌, 张一白, 管虎',
            'actor': '黄渤, 张译, 刘昊然'
        }
        
        dialog = MovieInfoDialog(chinese_info)
        
        # 验证中文标题正确显示
        self.assertIn('我和我的祖国', dialog.windowTitle())

    def test_special_characters_in_title(self):
        """测试标题中的特殊字符"""
        special_info = {
            'title': 'Test: Movie & "Special" Characters!',
            'year': '2024',
            'rating': '8.0'
        }
        
        dialog = MovieInfoDialog(special_info)
        
        # 应该能够正常处理特殊字符
        self.assertIn('Test: Movie', dialog.windowTitle())


if __name__ == '__main__':
    unittest.main()
