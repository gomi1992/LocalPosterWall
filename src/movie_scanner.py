import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from cache_manager import CacheManager
from movie_info import MovieInfo
from status_message_manager import StatusMessageManager


class MovieScanner:
    def __init__(self):
        self.video_extensions = {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.m4v',
            '.flv', '.rmvb', '.rm', '.ts', '.webm'
        }
        self.poster_names = {'poster', 'poster.jpg', 'poster.png', 'folder.jpg'}
        self.resolution_patterns = [
            (r'2160[pP]|4[kK]', '4K'),
            (r'1080[pP]|1920x1080', '1080P'),
            (r'720[pP]|1280x720', '720P'),
            (r'[Bb]lu[Rr]ay|[Bb][Rr][Rr]ip', 'BluRay'),
            (r'[Ww][Ee][Bb]-?[Dd][Ll]|[Ww][Ee][Bb][Rr]ip', 'WEB-DL')
        ]
        # 需要忽略的系统文件夹
        self.ignore_folders = {
            'System Volume Information',
            '$RECYCLE.BIN',
            'Config.Msi',
            'Recovery',
            'Documents and Settings'
        }

        self.cache_manager = CacheManager()
        self.status_bar = StatusMessageManager.instance()

    def _get_nfo_files(self, folder_path):
        nfo_files = list(folder_path.glob('*.nfo'))
        if not nfo_files:
            return None
        return nfo_files

    def _read_nfo_contents(self, nfo_files):
        if not nfo_files:
            return None

        nfo_path = nfo_files[0]
        if not os.access(nfo_path, os.R_OK):
            return None

        with open(nfo_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    def _read_nfo_rating(self, folder_path):
        """从 nfo 文件读取评分"""
        try:
            # 查找 nfo 文件
            nfo_files = list(folder_path.glob('*.nfo'))
            if not nfo_files:
                return None

            # 读取第一个 nfo 文件
            nfo_path = nfo_files[0]
            if not os.access(nfo_path, os.R_OK):
                return None

            # 解析 XML
            tree = ET.parse(nfo_path)
            root = tree.getroot()

            # 尝试读取评分
            rating_elem = root.find('rating')
            if rating_elem is not None and rating_elem.text:
                return rating_elem.text

            # 如果没有直接的评分标签，尝试读取 ratings 下的评分
            ratings = root.find('ratings')
            if ratings is not None:
                # 优先使用 themoviedb 的评分
                for rating in ratings.findall('rating'):
                    if rating.get('name') == 'themoviedb':
                        value = rating.find('value')
                        if value is not None and value.text:
                            return value.text

            return None
        except Exception:
            return None

    def scan_folder(self, folder_path):
        """扫描电影文件夹"""
        movies = []
        # folder_path = Path(folder_path)
        #
        # try:
        #     for item in folder_path.iterdir():
        #         try:
        #             if (item.is_dir() and
        #                     os.access(item, os.R_OK) and
        #                     item.name not in self.ignore_folders and
        #                     not item.name.startswith('.')):
        #                 movie_info = self._parse_movie_folder(item)
        #                 if movie_info:
        #                     movies.append(movie_info)
        #         except (PermissionError, OSError):
        #             continue  # 跳过无权限访问的文件夹
        # except Exception as e:
        #     print(f"Error scanning folder {folder_path}: {e}")
        #     return []

        folder_path = [Path(folder_path)]
        try:
            while folder_path:
                item = folder_path.pop()
                try:
                    if (item.is_dir() and
                            os.access(item, os.R_OK) and
                            item.name not in self.ignore_folders and
                            not item.name.startswith('.')):
                        movie_info = self._parse_movie_folder(item)
                        if movie_info:
                            movies.append(movie_info)
                        else:
                            for sub_dir in item.iterdir():
                                if sub_dir.is_dir():
                                    folder_path.append(sub_dir)
                except (PermissionError, OSError):
                    continue  # 跳过无权限访问的文件夹
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
            return []
        print(movies)
        # 按年份降序排序
        movies.sort(
            key=lambda x: (x.get('year', '0000'), x.get('title')),
            reverse=True
        )
        self.cache_manager.set_cache(movies)
        return movies

    def _parse_movie_folder(self, folder_path):
        # self.status_bar.status_bar.showMessage(str(folder_path), 3000)
        print(folder_path)
        """解析单个电影文件夹"""
        try:
            # 从文件夹名称中提取电影信息
            folder_name = folder_path.name
            year_match = re.search(r'\((\d{4})\)', folder_name)
            year = year_match.group(1) if year_match else "1900"

            # 提取标题（去除年份）
            title = re.sub(r'\(\d{4}\)', '', folder_name).strip()

            nfo_files = self._get_nfo_files(folder_path)
            if nfo_files is None:
                return None

            nfo_contents = self._read_nfo_contents(nfo_files)
            nfo_path = nfo_files[0]

            # 从 nfo 文件读取评分
            rating = self._read_nfo_rating(folder_path)

            # 查找海报
            poster_path = None
            for poster_name in self.poster_names:
                for ext in ['.jpg', '.png', '.jpeg']:
                    test_path = folder_path / f"{poster_name}{ext}"
                    if test_path.exists() and os.access(test_path, os.R_OK):
                        poster_path = test_path
                        break
                if poster_path:
                    break

            if poster_path is None:
                movie_files = os.listdir(folder_path)
                for movie_file in movie_files:
                    if "poster" in movie_file:
                        poster_path = folder_path / f"{movie_file}"
                        break

            # 查找视频文件
            video_file = None
            resolution = None

            # 遍历文件夹中的所有文件
            try:
                for file in folder_path.iterdir():
                    if (file.suffix.lower() in self.video_extensions and
                            os.access(file, os.R_OK)):
                        video_file = file
                        # 从文件名中提取分辨率信息
                        for pattern, res in self.resolution_patterns:
                            if re.search(pattern, file.name):
                                resolution = res
                                break
                        if resolution:
                            break
            except (PermissionError, OSError):
                return None

            if video_file:
                return {
                    'title': title,
                    'year': year,
                    'rating': rating,
                    'poster_path': str(poster_path) if poster_path else None,
                    'video_path': str(video_file),
                    'resolution': resolution,
                    'nfo_path': str(nfo_path) if nfo_path else None
                    # 'nfo_contents': nfo_contents
                }

        except Exception as e:
            print(f"Error parsing movie folder {folder_path}: {e}")
            return None

        return None
