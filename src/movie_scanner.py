"""
电影扫描器模块

本模块实现了电影文件夹扫描和解析功能，负责：
- 扫描本地电影文件夹
- 解析电影信息（标题、年份、评分、海报等）
- 识别视频文件和分辨率
- 解析NFO文件获取详细信息
- 将扫描结果缓存到本地

主要功能：
- 深度扫描电影文件夹（支持嵌套文件夹）
- 智能识别视频文件格式
- 自动匹配海报文件
- 解析NFO文件获取评分和详细信息
- 识别视频分辨率和质量信息
- 缓存机制提高重复扫描性能

Author: LocalPosterWall Team
Version: 0.0.1
"""

import os
import time
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from cache_manager import CacheManager
from movie_info import MovieInfo
from status_message_manager import StatusMessageManager
from loguru import logger


class MovieScanner:
    """
    电影文件夹扫描器
    
    负责扫描指定的电影文件夹，解析电影信息并返回结构化的数据。
    支持多种视频格式、NFO文件解析、海报识别等功能。
    """
    
    def __init__(self):
        """
        初始化电影扫描器
        
        设置视频文件扩展名、海报文件名模式、分辨率识别规则等。
        """
        logger.info("初始化电影扫描器")
        
        # 支持的视频文件扩展名集合
        self.video_extensions = {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.m4v',
            '.flv', '.rmvb', '.rm', '.ts', '.webm'
        }
        logger.debug(f"支持的视频格式: {sorted(self.video_extensions)}")
        
        # 海报文件名匹配规则
        self.poster_names = {'poster', 'poster.jpg', 'poster.png', 'folder.jpg'}
        logger.debug(f"海报文件名模式: {sorted(self.poster_names)}")
        
        # 分辨率识别正则表达式模式
        # 每个元组包含 (正则表达式模式, 分辨率标签)
        self.resolution_patterns = [
            (r'2160[pP]|4[kK]', '4K'),
            (r'1080[pP]|1920x1080', '1080P'),
            (r'720[pP]|1280x720', '720P'),
            (r'[Bb]lu[Rr]ay|[Bb][Rr][Rr]ip', 'BluRay'),
            (r'[Ww][Ee][Bb]-?[Dd][Ll]|[Ww][Ee][Bb][Rr]ip', 'WEB-DL')
        ]
        logger.debug(f"分辨率识别模式: {len(self.resolution_patterns)} 条规则")
        
        # 需要忽略的系统文件夹名称
        self.ignore_folders = {
            'System Volume Information',
            '$RECYCLE.BIN',
            'Config.Msi',
            'Recovery',
            'Documents and Settings'
        }
        logger.debug(f"忽略的文件夹: {sorted(self.ignore_folders)}")
        
        # 初始化缓存管理器
        self.cache_manager = CacheManager()
        logger.debug("缓存管理器初始化完成")
        
        # 初始化状态消息管理器
        self.status_bar = StatusMessageManager.instance()
        logger.debug("状态消息管理器初始化完成")
        
        logger.info("电影扫描器初始化完成")

    def _get_nfo_files(self, folder_path):
        """
        获取文件夹中的NFO文件
        
        查找指定文件夹中的所有.nfo文件。
        
        Args:
            folder_path (Path): 文件夹路径
            
        Returns:
            list: NFO文件路径列表，如果不存在则返回None
        """
        logger.debug(f"查找NFO文件: {folder_path}")
        
        try:
            # 查找所有.nfo文件
            nfo_files = list(folder_path.glob('*.nfo'))
            logger.debug(f"在 {folder_path} 中找到 {len(nfo_files)} 个NFO文件")
            
            if not nfo_files:
                logger.debug("未找到NFO文件")
                return None
                
            return nfo_files
            
        except Exception as e:
            logger.exception(f"查找NFO文件失败 {folder_path}: {str(e)}")
            return None

    def _read_nfo_contents(self, nfo_files):
        """
        读取NFO文件内容
        
        读取第一个可读NFO文件的完整内容。
        
        Args:
            nfo_files (list): NFO文件路径列表
            
        Returns:
            str: NFO文件内容，如果读取失败则返回None
        """
        if not nfo_files:
            logger.debug("NFO文件列表为空")
            return None

        nfo_path = nfo_files[0]
        logger.debug(f"读取NFO文件: {nfo_path}")
        
        try:
            # 检查文件是否可读
            if not os.access(nfo_path, os.R_OK):
                logger.warning(f"NFO文件不可读: {nfo_path}")
                return None
            
            # 读取文件内容
            with open(nfo_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            logger.debug(f"NFO文件内容长度: {len(content)} 字符")
            return content
            
        except Exception as e:
            logger.exception(f"读取NFO文件失败 {nfo_path}: {str(e)}")
            return None

    def _read_nfo_rating(self, folder_path):
        """
        从NFO文件读取评分信息
        
        解析NFO文件XML格式，提取电影评分信息。
        优先使用themoviedb的评分，其次使用通用评分。
        
        Args:
            folder_path (Path): 电影文件夹路径
            
        Returns:
            str/None: 评分字符串，如果无法解析则返回None
        """
        logger.debug(f"从NFO文件读取评分: {folder_path}")
        
        try:
            # 查找NFO文件
            nfo_files = list(folder_path.glob('*.nfo'))
            if not nfo_files:
                logger.debug("未找到NFO文件，无法读取评分")
                return None

            # 读取第一个NFO文件
            nfo_path = nfo_files[0]
            logger.debug(f"解析NFO文件: {nfo_path}")
            
            if not os.access(nfo_path, os.R_OK):
                logger.warning(f"NFO文件不可读: {nfo_path}")
                return None

            # 解析XML
            logger.debug("开始解析XML")
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            logger.debug("XML解析完成")

            # 尝试读取直接评分标签
            rating_elem = root.find('rating')
            if rating_elem is not None and rating_elem.text:
                rating_value = rating_elem.text.strip()
                logger.info(f"找到直接评分: {rating_value}")
                return rating_value

            # 尝试读取ratings下的评分
            ratings = root.find('ratings')
            if ratings is not None:
                logger.debug("找到ratings标签，查找themoviedb评分")
                # 优先使用themoviedb的评分
                for rating in ratings.findall('rating'):
                    source = rating.get('name', '').lower()
                    if source == 'themoviedb':
                        value_elem = rating.find('value')
                        if value_elem is not None and value_elem.text:
                            rating_value = value_elem.text.strip()
                            logger.info(f"找到themoviedb评分: {rating_value}")
                            return rating_value

            logger.debug("NFO文件中未找到评分信息")
            return None
            
        except ET.ParseError as e:
            logger.exception(f"NFO文件XML解析失败: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"读取NFO评分失败: {str(e)}")
            return None

    def _read_nfo_credits(self, folder_path):
        """
        从NFO文件读取导演和演员信息
        
        解析NFO文件XML格式，提取电影导演和演员信息。
        
        Args:
            folder_path (Path): 电影文件夹路径
            
        Returns:
            dict: 包含director和actors的字典，如果无法解析则返回None
        """
        logger.debug(f"从NFO文件读取导演和演员信息: {folder_path}")
        
        try:
            # 查找NFO文件
            nfo_files = list(folder_path.glob('*.nfo'))
            if not nfo_files:
                logger.debug("未找到NFO文件，无法读取导演和演员信息")
                return None

            # 读取第一个NFO文件
            nfo_path = nfo_files[0]
            logger.debug(f"解析NFO文件: {nfo_path}")
            
            if not os.access(nfo_path, os.R_OK):
                logger.warning(f"NFO文件不可读: {nfo_path}")
                return None

            # 解析XML
            logger.debug("开始解析XML")
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            logger.debug("XML解析完成")

            # 读取导演信息
            directors = []
            director_elements = root.findall('.//director')
            for director_elem in director_elements:
                if director_elem.text and director_elem.text.strip():
                    director_name = director_elem.text.strip()
                    directors.append(director_name)
                    logger.debug(f"找到导演: {director_name}")

            # 读取演员信息
            actors = []
            # 查找actor标签下的name子标签
            actor_elements = root.findall('.//actor')
            for actor_elem in actor_elements:
                name_elem = actor_elem.find('name')
                if name_elem is not None and name_elem.text and name_elem.text.strip():
                    actor_name = name_elem.text.strip()
                    actors.append(actor_name)
                    logger.debug(f"找到演员: {actor_name}")
            
            # 如果没有找到name标签下的演员，尝试直接读取actor标签的文本
            if not actors:
                actor_elements = root.findall('.//actor')
                for actor_elem in actor_elements:
                    if actor_elem.text and actor_elem.text.strip():
                        actor_name = actor_elem.text.strip()
                        if actor_name not in actors:  # 避免重复
                            actors.append(actor_name)
                            logger.debug(f"找到演员(直接文本): {actor_name}")

            result = {
                'director': directors,
                'actors': actors
            }
            
            logger.info(f"成功解析导演和演员信息:")
            logger.info(f"  导演: {directors}")
            logger.info(f"  演员数量: {len(actors)}")
            
            return result
            
        except ET.ParseError as e:
            logger.exception(f"NFO文件XML解析失败: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"读取NFO导演和演员信息失败: {str(e)}")
            return None

    def scan_folder(self, folder_path):
        """
        扫描电影文件夹
        
        深度扫描指定文件夹及其子文件夹，查找所有电影文件夹，
        解析电影信息并返回结构化的电影列表。
        
        Args:
            folder_path (str/Path): 要扫描的电影文件夹路径
            
        Returns:
            list: 电影信息字典列表
        """
        logger.info("=" * 50)
        logger.info(f"开始扫描电影文件夹: {folder_path}")
        start_time = time.time()
        
        movies = []
        scanned_folders = 0
        processed_folders = 0
        
        try:
            # 转换路径为Path对象
            folder_path = Path(folder_path)
            logger.debug(f"目标文件夹路径: {folder_path}")
            logger.debug(f"文件夹是否存在: {folder_path.exists()}")
            logger.debug("是否为目录: {folder_path.is_dir()}")
            
            if not folder_path.exists():
                logger.error(f"文件夹不存在: {folder_path}")
                return []
            
            if not folder_path.is_dir():
                logger.error(f"路径不是文件夹: {folder_path}")
                return []
            
            # 使用栈进行深度优先搜索
            folder_stack = [folder_path]
            
            while folder_stack:
                current_folder = folder_stack.pop()
                scanned_folders += 1
                
                logger.debug(f"正在扫描第 {scanned_folders} 个文件夹: {current_folder}")
                
                try:
                    # 检查访问权限和文件夹有效性
                    if not (current_folder.is_dir() and 
                            os.access(current_folder, os.R_OK)):
                        logger.debug(f"跳过不可访问的文件夹: {current_folder}")
                        continue
                    
                    # 跳过系统文件夹和隐藏文件夹
                    folder_name = current_folder.name
                    if (folder_name in self.ignore_folders or 
                        folder_name.startswith('.')):
                        logger.debug(f"跳过系统/隐藏文件夹: {folder_name}")
                        continue
                    
                    # 解析电影文件夹
                    movie_info = self._parse_movie_folder(current_folder)
                    
                    if movie_info:
                        logger.info(f"找到电影: {movie_info['title']} ({movie_info['year']})")
                        movies.append(movie_info)
                        processed_folders += 1
                    else:
                        # 如果不是电影文件夹，继续搜索子文件夹
                        logger.debug(f"非电影文件夹，继续搜索子文件夹: {current_folder}")
                        try:
                            for sub_dir in current_folder.iterdir():
                                if sub_dir.is_dir():
                                    folder_stack.append(sub_dir)
                        except (PermissionError, OSError) as e:
                            logger.debug(f"访问子文件夹失败 {current_folder}: {str(e)}")
                            continue
                            
                except (PermissionError, OSError) as e:
                    logger.warning(f"访问文件夹失败 {current_folder}: {str(e)}")
                    continue
                except Exception as e:
                    logger.exception(f"扫描文件夹时发生错误 {current_folder}: {str(e)}")
                    continue
            
            # 按年份降序排序电影列表
            logger.info("对电影列表进行排序")
            movies.sort(
                key=lambda x: (x.get('year', '0000'), x.get('title', '')),
                reverse=True
            )
            logger.info(f"排序完成，共 {len(movies)} 部电影")
            
            # 保存到缓存
            logger.info("保存扫描结果到缓存")
            self.cache_manager.set_cache(movies)
            logger.debug("缓存保存完成")
            
            # 记录扫描统计信息
            scan_time = time.time() - start_time
            logger.info(f"扫描完成统计:")
            logger.info(f"  扫描文件夹数: {scanned_folders}")
            logger.info(f"  处理文件夹数: {processed_folders}")
            logger.info(f"  发现电影数: {len(movies)}")
            logger.info(f"  扫描耗时: {scan_time:.2f}秒")
            logger.info(f"  平均每部电影耗时: {scan_time/max(len(movies), 1):.3f}秒")
            
            logger.info("=" * 50)
            return movies
            
        except Exception as e:
            logger.exception(f"扫描文件夹失败 {folder_path}: {str(e)}")
            return []

    def _parse_movie_folder(self, folder_path):
        """
        解析单个电影文件夹
        
        从文件夹名称和内容中提取电影信息，包括标题、年份、评分等。
        
        Args:
            folder_path (Path): 电影文件夹路径
            
        Returns:
            dict/None: 电影信息字典，如果解析失败则返回None
        """
        logger.debug(f"解析电影文件夹: {folder_path}")
        
        try:
            # 从文件夹名称中提取电影信息
            folder_name = folder_path.name
            logger.debug(f"文件夹名称: {folder_name}")
            
            # 提取年份信息
            year_match = re.search(r'\((\d{4})\)', folder_name)
            year = year_match.group(1) if year_match else "1900"
            logger.debug(f"提取的年份: {year}")
            
            # 提取标题（去除年份括号）
            title = re.sub(r'\(\d{4}\)', '', folder_name).strip()
            logger.debug(f"提取的标题: {title}")
            
            # 查找NFO文件
            logger.debug("查找NFO文件")
            nfo_files = self._get_nfo_files(folder_path)
            
            if nfo_files is None:
                logger.debug(f"文件夹 {folder_path} 中未找到NFO文件，跳过")
                return None
            
            # 读取NFO文件内容
            nfo_contents = self._read_nfo_contents(nfo_files)
            nfo_path = nfo_files[0]
            logger.debug(f"NFO文件路径: {nfo_path}")
            
            # 从NFO文件读取评分
            logger.debug("从NFO文件读取评分")
            rating = self._read_nfo_rating(folder_path)
            if rating:
                logger.debug(f"获取到评分: {rating}")
            else:
                logger.debug("未获取到评分信息")
            
            # 从NFO文件读取导演和演员信息
            logger.debug("从NFO文件读取导演和演员信息")
            credits = self._read_nfo_credits(folder_path)
            if credits:
                logger.debug(f"获取到导演和演员信息: {credits}")
            else:
                logger.debug("未获取到导演和演员信息")
            
            # 查找海报文件
            logger.debug("查找海报文件")
            poster_path = self._find_poster_file(folder_path)
            if poster_path:
                logger.debug(f"找到海报文件: {poster_path}")
            else:
                logger.debug("未找到海报文件")
            
            # 查找视频文件和分辨率
            logger.debug("查找视频文件")
            video_info = self._find_video_file(folder_path)
            
            if not video_info['video_file']:
                logger.debug(f"文件夹 {folder_path} 中未找到视频文件")
                return None
            
            video_file = video_info['video_file']
            resolution = video_info['resolution']
            logger.debug(f"找到视频文件: {video_file}")
            logger.debug(f"识别到分辨率: {resolution}")
            
            # 构建电影信息字典
            movie_info = {
                'title': title,
                'year': year,
                'rating': rating,
                'director': credits['director'] if credits else [],
                'actors': credits['actors'] if credits else [],
                'poster_path': str(poster_path) if poster_path else None,
                'video_path': str(video_file),
                'resolution': resolution,
                'nfo_path': str(nfo_path) if nfo_path else None
                # 'nfo_contents': nfo_contents  # 暂时不包含NFO内容，节省内存
            }
            
            logger.info(f"电影文件夹解析成功: {title} ({year})")
            logger.debug(f"电影信息: {movie_info}")
            
            return movie_info
            
        except Exception as e:
            logger.exception(f"解析电影文件夹失败 {folder_path}: {str(e)}")
            return None

    def _find_poster_file(self, folder_path):
        """
        查找电影海报文件
        
        在指定文件夹中搜索符合命名规则的海报文件。
        
        Args:
            folder_path (Path): 电影文件夹路径
            
        Returns:
            Path/None: 海报文件路径，如果未找到则返回None
        """
        logger.debug(f"在 {folder_path} 中查找海报文件")
        
        try:
            # 首先尝试标准海报文件名
            for poster_name in self.poster_names:
                for ext in ['.jpg', '.png', '.jpeg']:
                    test_path = folder_path / f"{poster_name}{ext}"
                    if test_path.exists() and os.access(test_path, os.R_OK):
                        logger.debug(f"找到标准海报文件: {test_path}")
                        return test_path
            
            # 如果标准文件名都没找到，搜索包含"poster"的文件
            logger.debug("标准海报文件名未找到，搜索包含'poster'的文件")
            try:
                movie_files = os.listdir(folder_path)
                for movie_file in movie_files:
                    if "poster" in movie_file.lower():
                        poster_path = folder_path / movie_file
                        if poster_path.exists() and os.access(poster_path, os.R_OK):
                            logger.debug(f"找到poster文件: {poster_path}")
                            return poster_path
            except (PermissionError, OSError) as e:
                logger.debug(f"搜索poster文件时出错: {str(e)}")
            
            logger.debug("未找到海报文件")
            return None
            
        except Exception as e:
            logger.exception(f"查找海报文件失败 {folder_path}: {str(e)}")
            return None

    def _find_video_file(self, folder_path):
        """
        查找视频文件并识别分辨率
        
        在指定文件夹中搜索视频文件，并从文件名中提取分辨率信息。
        
        Args:
            folder_path (Path): 电影文件夹路径
            
        Returns:
            dict: 包含video_file和resolution的字典
        """
        logger.debug(f"在 {folder_path} 中查找视频文件")
        
        video_file = None
        resolution = None
        
        try:
            # 遍历文件夹中的所有文件
            for file in folder_path.iterdir():
                try:
                    # 检查是否为支持的视频文件格式
                    if file.suffix.lower() in self.video_extensions:
                        if not os.access(file, os.R_OK):
                            logger.debug(f"视频文件不可读: {file}")
                            continue
                        
                        logger.debug(f"找到视频文件: {file.name}")
                        video_file = file
                        
                        # 从文件名中提取分辨率信息
                        resolution = self._extract_resolution(file.name)
                        logger.debug(f"从文件名提取的分辨率: {resolution}")
                        
                        # 找到视频文件后就跳出循环
                        break
                        
                except (PermissionError, OSError) as e:
                    logger.debug(f"访问文件失败 {file}: {str(e)}")
                    continue
            
            if video_file:
                logger.info(f"视频文件识别成功: {video_file.name}")
            else:
                logger.debug("未找到视频文件")
                
            return {
                'video_file': video_file,
                'resolution': resolution
            }
            
        except Exception as e:
            logger.exception(f"查找视频文件失败 {folder_path}: {str(e)}")
            return {
                'video_file': None,
                'resolution': None
            }

    def _extract_resolution(self, filename):
        """
        从文件名中提取分辨率信息
        
        使用预定义的正则表达式模式匹配文件名中的分辨率信息。
        
        Args:
            filename (str): 文件名
            
        Returns:
            str/None: 分辨率标签，如果未匹配到则返回None
        """
        logger.debug(f"从文件名提取分辨率: {filename}")
        
        try:
            # 使用预定义的正则表达式模式匹配分辨率
            for pattern, res_label in self.resolution_patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    logger.debug(f"匹配到分辨率模式 '{pattern}': {res_label}")
                    return res_label
            
            logger.debug("文件名中未匹配到分辨率信息")
            return None
            
        except Exception as e:
            logger.exception(f"提取分辨率失败 {filename}: {str(e)}")
            return None
