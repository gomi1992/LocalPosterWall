"""
MovieInfo 测试模块

本模块包含对MovieInfo类的单元测试，测试内容包括：
- 对象初始化测试
- 字符串表示方法测试
- 字典转换功能测试
- 文件有效性检查测试
- 显示信息获取测试
- 数据完整性测试
- 边界情况和异常处理测试

使用unittest框架进行测试，创建临时文件验证文件检查功能。
"""

import unittest
import os
from pathlib import Path

# 导入被测试模块
from src.movie_info import MovieInfo


class TestMovieInfo(unittest.TestCase):
    """MovieInfo类的单元测试"""

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 创建测试文件目录
        self.test_dir = Path(__file__).parent / "test_movie_files"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件路径
        self.test_video_path = self.test_dir / "test_movie.mp4"
        self.test_poster_path = self.test_dir / "poster.jpg"
        self.test_nfo_path = self.test_dir / "movie.nfo"
        
        # 创建测试文件
        self.test_video_path.touch()
        self.test_poster_path.touch()
        self.test_nfo_path.touch()
        
        # 基本电影信息参数
        self.basic_params = {
            'title': '测试电影',
            'year': '2024',
            'rating': '8.5',
            'poster_path': str(self.test_poster_path),
            'video_path': str(self.test_video_path),
            'resolution': '1080p',
            'nfo_path': str(self.test_nfo_path),
            'director': '张艺谋',
            'actors': ['章子怡', '巩俐']
        }

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 清理测试文件
        for file_path in [self.test_video_path, self.test_poster_path, self.test_nfo_path]:
            if file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass
        
        # 删除测试目录
        if self.test_dir.exists():
            try:
                self.test_dir.rmdir()
            except:
                pass

    def test_initialization_with_all_parameters(self):
        """测试使用所有参数初始化"""
        movie = MovieInfo(**self.basic_params)
        
        # 验证所有属性已正确设置
        self.assertEqual(movie.title, '测试电影')
        self.assertEqual(movie.year, '2024')
        self.assertEqual(movie.rating, '8.5')
        self.assertEqual(movie.poster_path, str(self.test_poster_path))
        self.assertEqual(movie.video_path, str(self.test_video_path))
        self.assertEqual(movie.resolution, '1080p')
        self.assertEqual(movie.nfo_path, str(self.test_nfo_path))
        self.assertEqual(movie.director, '张艺谋')
        self.assertEqual(movie.actors, ['章子怡', '巩俐'])

    def test_initialization_without_optional_parameters(self):
        """测试不使用可选参数初始化"""
        movie = MovieInfo(
            title='简单电影',
            year='2023',
            rating='7.0',
            poster_path='/path/to/poster.jpg',
            video_path='/path/to/video.mp4',
            resolution='720p',
            nfo_path='/path/to/nfo.nfo'
        )
        
        # 验证必需参数已设置
        self.assertEqual(movie.title, '简单电影')
        self.assertEqual(movie.year, '2023')
        
        # 验证可选参数为None或默认值
        self.assertIsNone(movie.director)
        self.assertEqual(movie.actors, [])

    def test_initialization_with_none_actors(self):
        """测试使用None作为actors参数"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo',
            director='导演',
            actors=None
        )
        
        # actors应该是空列表而非None
        self.assertEqual(movie.actors, [])
        self.assertIsInstance(movie.actors, list)

    def test_initialization_with_empty_actors_list(self):
        """测试使用空演员列表初始化"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo',
            actors=[]
        )
        
        self.assertEqual(movie.actors, [])

    def test_initialization_with_numeric_year(self):
        """测试使用数字年份初始化"""
        movie = MovieInfo(
            title='电影',
            year=2024,  # 数字而非字符串
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo'
        )
        
        # 年份应该被接受（可以是字符串或数字）
        self.assertEqual(movie.year, 2024)

    def test_initialization_with_numeric_rating(self):
        """测试使用数字评分初始化"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating=8.5,  # 数字而非字符串
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo'
        )
        
        # 评分应该被接受（可以是字符串或数字）
        self.assertEqual(movie.rating, 8.5)

    def test_to_dict(self):
        """测试转换为字典"""
        movie = MovieInfo(**self.basic_params)
        
        result = movie.to_dict()
        
        # 验证返回的是字典
        self.assertIsInstance(result, dict)
        
        # 验证所有字段都在字典中
        self.assertEqual(result['title'], '测试电影')
        self.assertEqual(result['year'], '2024')
        self.assertEqual(result['rating'], '8.5')
        self.assertEqual(result['poster_path'], str(self.test_poster_path))
        self.assertEqual(result['video_path'], str(self.test_video_path))
        self.assertEqual(result['resolution'], '1080p')
        self.assertEqual(result['nfo_path'], str(self.test_nfo_path))
        self.assertEqual(result['director'], '张艺谋')
        self.assertEqual(result['actors'], ['章子怡', '巩俐'])

    def test_from_dict(self):
        """测试从字典创建对象"""
        data = {
            'title': '字典电影',
            'year': '2023',
            'rating': '7.5',
            'poster_path': '/path/to/poster.jpg',
            'video_path': '/path/to/video.mp4',
            'resolution': '4K',
            'nfo_path': '/path/to/nfo.nfo',
            'director': '克里斯托弗·诺兰',
            'actors': ['马修·麦康纳', '安妮·海瑟薇']
        }
        
        movie = MovieInfo.from_dict(data)
        
        # 验证所有属性已正确设置
        self.assertEqual(movie.title, '字典电影')
        self.assertEqual(movie.year, '2023')
        self.assertEqual(movie.rating, '7.5')
        self.assertEqual(movie.poster_path, '/path/to/poster.jpg')
        self.assertEqual(movie.video_path, '/path/to/video.mp4')
        self.assertEqual(movie.resolution, '4K')
        self.assertEqual(movie.nfo_path, '/path/to/nfo.nfo')
        self.assertEqual(movie.director, '克里斯托弗·诺兰')
        self.assertEqual(movie.actors, ['马修·麦康纳', '安妮·海瑟薇'])

    def test_from_dict_with_missing_fields(self):
        """测试从缺少字段的字典创建对象"""
        data = {
            'title': '不完整电影',
            'year': '2024'
        }
        
        movie = MovieInfo.from_dict(data)
        
        # 验证必需字段使用了默认值
        self.assertEqual(movie.title, '不完整电影')
        self.assertEqual(movie.year, '2024')
        self.assertEqual(movie.rating, '')
        self.assertEqual(movie.poster_path, '')
        self.assertEqual(movie.video_path, '')
        self.assertEqual(movie.resolution, '')
        self.assertEqual(movie.nfo_path, '')
        self.assertIsNone(movie.director)
        self.assertEqual(movie.actors, [])

    def test_from_dict_with_empty_dict(self):
        """测试从空字典创建对象"""
        movie = MovieInfo.from_dict({})
        
        # 验证所有字段使用了默认值
        self.assertEqual(movie.title, '')
        self.assertEqual(movie.year, '')
        self.assertEqual(movie.rating, '')
        self.assertEqual(movie.poster_path, '')
        self.assertEqual(movie.video_path, '')
        self.assertEqual(movie.resolution, '')
        self.assertEqual(movie.nfo_path, '')
        self.assertIsNone(movie.director)
        self.assertEqual(movie.actors, [])

    def test_to_dict_and_from_dict_roundtrip(self):
        """测试字典转换的往返一致性"""
        original_movie = MovieInfo(**self.basic_params)
        
        # 转换为字典再转回对象
        dict_data = original_movie.to_dict()
        restored_movie = MovieInfo.from_dict(dict_data)
        
        # 验证所有字段一致
        self.assertEqual(restored_movie.title, original_movie.title)
        self.assertEqual(restored_movie.year, original_movie.year)
        self.assertEqual(restored_movie.rating, original_movie.rating)
        self.assertEqual(restored_movie.poster_path, original_movie.poster_path)
        self.assertEqual(restored_movie.video_path, original_movie.video_path)
        self.assertEqual(restored_movie.resolution, original_movie.resolution)
        self.assertEqual(restored_movie.nfo_path, original_movie.nfo_path)
        self.assertEqual(restored_movie.director, original_movie.director)
        self.assertEqual(restored_movie.actors, original_movie.actors)

    def test_get_display_info(self):
        """测试获取显示信息"""
        movie = MovieInfo(**self.basic_params)
        
        display_info = movie.get_display_info()
        
        # 验证返回的是字典
        self.assertIsInstance(display_info, dict)
        
        # 验证包含显示所需的字段
        self.assertIn('title', display_info)
        self.assertIn('year', display_info)
        self.assertIn('rating', display_info)
        self.assertIn('resolution', display_info)
        self.assertIn('director', display_info)
        self.assertIn('actors', display_info)
        
        # 验证值正确
        self.assertEqual(display_info['title'], '测试电影')
        self.assertEqual(display_info['year'], '2024')
        self.assertEqual(display_info['rating'], '8.5')
        self.assertEqual(display_info['resolution'], '1080p')
        self.assertEqual(display_info['director'], '张艺谋')
        self.assertEqual(display_info['actors'], ['章子怡', '巩俐'])

    def test_has_valid_files_all_exist(self):
        """测试所有文件都存在时的有效性检查"""
        movie = MovieInfo(**self.basic_params)
        
        result = movie.has_valid_files()
        
        # 所有关键文件存在，应该返回True
        self.assertTrue(result)

    def test_has_valid_files_missing_video(self):
        """测试视频文件缺失时的有效性检查"""
        # 删除视频文件
        self.test_video_path.unlink()
        
        movie = MovieInfo(**self.basic_params)
        
        result = movie.has_valid_files()
        
        # 视频文件不存在，应该返回False
        self.assertFalse(result)

    def test_has_valid_files_missing_poster(self):
        """测试海报文件缺失时的有效性检查"""
        # 删除海报文件
        self.test_poster_path.unlink()
        
        movie = MovieInfo(**self.basic_params)
        
        result = movie.has_valid_files()
        
        # 海报是可选的，视频存在即可
        self.assertTrue(result)

    def test_has_valid_files_missing_nfo(self):
        """测试NFO文件缺失时的有效性检查"""
        # 删除NFO文件
        self.test_nfo_path.unlink()
        
        movie = MovieInfo(**self.basic_params)
        
        result = movie.has_valid_files()
        
        # NFO是可选的，视频存在即可
        self.assertTrue(result)

    def test_has_valid_files_with_empty_paths(self):
        """测试使用空路径时的有效性检查"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating='8.0',
            poster_path='',
            video_path='',
            resolution='1080p',
            nfo_path=''
        )
        
        result = movie.has_valid_files()
        
        # 所有路径为空，应该返回False
        self.assertFalse(result)

    def test_has_valid_files_with_nonexistent_paths(self):
        """测试使用不存在的路径时的有效性检查"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating='8.0',
            poster_path='/nonexistent/poster.jpg',
            video_path='/nonexistent/video.mp4',
            resolution='1080p',
            nfo_path='/nonexistent/nfo.nfo'
        )
        
        result = movie.has_valid_files()
        
        # 文件不存在，应该返回False
        self.assertFalse(result)

    def test_has_valid_files_exception_handling(self):
        """测试文件检查时的异常处理"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo'
        )
        
        # 不应该抛出异常
        try:
            result = movie.has_valid_files()
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"has_valid_files raised exception: {e}")

    def test_chinese_character_support(self):
        """测试中文字符支持"""
        chinese_params = {
            'title': '我和我的祖国',
            'year': '2019',
            'rating': '7.8',
            'poster_path': str(self.test_poster_path),
            'video_path': str(self.test_video_path),
            'resolution': '1080p',
            'nfo_path': str(self.test_nfo_path),
            'director': '陈凯歌',
            'actors': ['黄渤', '张译', '刘昊然']
        }
        
        movie = MovieInfo(**chinese_params)
        
        # 验证中文字符正确存储
        self.assertEqual(movie.title, '我和我的祖国')
        self.assertEqual(movie.director, '陈凯歌')
        self.assertEqual(movie.actors, ['黄渤', '张译', '刘昊然'])

    def test_special_characters_in_title(self):
        """测试标题中的特殊字符"""
        movie = MovieInfo(
            title='Test: Movie & "Special" Characters!',
            year='2024',
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo'
        )
        
        # 特殊字符应该被正确存储
        self.assertEqual(movie.title, 'Test: Movie & "Special" Characters!')

    def test_empty_string_values(self):
        """测试空字符串值"""
        movie = MovieInfo(
            title='',
            year='',
            rating='',
            poster_path='',
            video_path='',
            resolution='',
            nfo_path=''
        )
        
        # 空字符串应该被接受
        self.assertEqual(movie.title, '')
        self.assertEqual(movie.year, '')
        self.assertEqual(movie.rating, '')

    def test_long_string_values(self):
        """测试长字符串值"""
        long_title = 'A' * 1000
        long_director = 'B' * 500
        
        movie = MovieInfo(
            title=long_title,
            year='2024',
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo',
            director=long_director
        )
        
        # 长字符串应该被正确存储
        self.assertEqual(len(movie.title), 1000)
        self.assertIsNotNone(movie.director)
        if movie.director:
            self.assertEqual(len(movie.director), 500)

    def test_actors_list_with_many_actors(self):
        """测试包含多个演员的列表"""
        many_actors = [f'演员{i}' for i in range(100)]
        
        movie = MovieInfo(
            title='大卡司电影',
            year='2024',
            rating='9.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo',
            actors=many_actors
        )
        
        # 验证演员列表正确存储
        self.assertEqual(len(movie.actors), 100)
        self.assertEqual(movie.actors[0], '演员0')
        self.assertEqual(movie.actors[99], '演员99')

    def test_different_resolution_formats(self):
        """测试不同的分辨率格式"""
        resolutions = ['720p', '1080p', '4K', '2160p', 'HD', 'UHD', '1920x1080']
        
        for res in resolutions:
            movie = MovieInfo(
                title='电影',
                year='2024',
                rating='8.0',
                poster_path='/path/poster.jpg',
                video_path='/path/video.mp4',
                resolution=res,
                nfo_path='/path/nfo.nfo'
            )
            
            self.assertEqual(movie.resolution, res)

    def test_different_rating_formats(self):
        """测试不同的评分格式"""
        ratings = ['8.5', '9', '7.23', '10.0', '0', '5.5']
        
        for rating in ratings:
            movie = MovieInfo(
                title='电影',
                year='2024',
                rating=rating,
                poster_path='/path/poster.jpg',
                video_path='/path/video.mp4',
                resolution='1080p',
                nfo_path='/path/nfo.nfo'
            )
            
            self.assertEqual(movie.rating, rating)

    def test_path_formats(self):
        """测试不同的路径格式"""
        # Windows路径
        windows_path = r'C:\Users\Movies\poster.jpg'
        # Unix路径
        unix_path = '/home/user/movies/poster.jpg'
        # 相对路径
        relative_path = '../movies/poster.jpg'
        
        for path in [windows_path, unix_path, relative_path]:
            movie = MovieInfo(
                title='电影',
                year='2024',
                rating='8.0',
                poster_path=path,
                video_path=path,
                resolution='1080p',
                nfo_path=path
            )
            
            self.assertEqual(movie.poster_path, path)
            self.assertEqual(movie.video_path, path)

    def test_actors_list_modification(self):
        """测试演员列表的可修改性"""
        movie = MovieInfo(
            title='电影',
            year='2024',
            rating='8.0',
            poster_path='/path/poster.jpg',
            video_path='/path/video.mp4',
            resolution='1080p',
            nfo_path='/path/nfo.nfo',
            actors=['演员1', '演员2']
        )
        
        # 修改演员列表
        movie.actors.append('演员3')
        
        # 验证修改成功
        self.assertEqual(len(movie.actors), 3)
        self.assertIn('演员3', movie.actors)

    def test_attribute_modification(self):
        """测试属性的可修改性"""
        movie = MovieInfo(**self.basic_params)
        
        # 修改属性
        movie.title = '修改后的标题'
        movie.year = '2025'
        movie.rating = '9.5'
        movie.director = '新导演'
        
        # 验证修改成功
        self.assertEqual(movie.title, '修改后的标题')
        self.assertEqual(movie.year, '2025')
        self.assertEqual(movie.rating, '9.5')
        self.assertEqual(movie.director, '新导演')


if __name__ == '__main__':
    unittest.main()
