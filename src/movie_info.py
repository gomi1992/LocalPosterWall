"""
电影信息数据类模块

本模块定义了电影信息的数据结构类，用于封装电影的详细信息。
该类是一个简单的数据容器，用于存储和管理电影的各种属性信息。

主要属性：
- title: 电影标题
- year: 发行年份
- rating: 电影评分
- poster_path: 海报图片路径
- video_path: 视频文件路径
- resolution: 视频分辨率
- nfo_path: NFO信息文件路径

Author: LocalPosterWall Team
Version: 0.0.1
"""

from loguru import logger


class MovieInfo:
    """
    电影信息数据类
    
    用于存储和管理电影的详细信息，包括标题、年份、评分、
    媒体文件路径等关键属性。
    
    这个类是一个简单的数据容器，不包含复杂的业务逻辑，
    主要用于在不同模块间传递电影信息。
    """
    
    def __init__(self, title, year, rating, poster_path, video_path, resolution, nfo_path):
        """
        初始化电影信息对象
        
        Args:
            title (str): 电影标题
            year (str/int): 发行年份
            rating (str/float): 电影评分
            poster_path (str): 海报图片文件路径
            video_path (str): 视频文件路径
            resolution (str): 视频分辨率信息
            nfo_path (str): NFO信息文件路径
        """
        logger.debug(f"创建电影信息对象: {title} ({year})")
        
        # 电影标题
        self.title = title
        logger.debug(f"设置电影标题: {title}")
        
        # 发行年份
        self.year = year
        logger.debug(f"设置发行年份: {year}")
        
        # 电影评分
        self.rating = rating
        logger.debug(f"设置电影评分: {rating}")
        
        # 海报图片路径
        self.poster_path = poster_path
        logger.debug(f"设置海报路径: {poster_path}")
        
        # 视频文件路径
        self.video_path = video_path
        logger.debug(f"设置视频路径: {video_path}")
        
        # 视频分辨率
        self.resolution = resolution
        logger.debug(f"设置视频分辨率: {resolution}")
        
        # NFO文件路径
        self.nfo_path = nfo_path
        logger.debug(f"设置NFO文件路径: {nfo_path}")
        
        logger.info(f"电影信息对象创建完成: {title}")
    
    def __str__(self):
        """
        返回电影信息的字符串表示
        
        Returns:
            str: 格式化的电影信息字符串
        """
        return f"{self.title} ({self.year}) - 评分: {self.rating}"
    
    def __repr__(self):
        """
        返回电影信息的完整字符串表示
        
        Returns:
            str: 包含所有属性的完整字符串表示
        """
        return (f"MovieInfo(title='{self.title}', year='{self.year}', "
                f"rating={self.rating}, poster_path='{self.poster_path}', "
                f"video_path='{self.video_path}', resolution='{self.resolution}', "
                f"nfo_path='{self.nfo_path}')")
    
    def to_dict(self):
        """
        将电影信息转换为字典格式
        
        Returns:
            dict: 包含所有电影信息的字典
        """
        logger.debug(f"转换电影信息为字典: {self.title}")
        
        return {
            'title': self.title,
            'year': self.year,
            'rating': self.rating,
            'poster_path': self.poster_path,
            'video_path': self.video_path,
            'resolution': self.resolution,
            'nfo_path': self.nfo_path
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        从字典创建电影信息对象
        
        Args:
            data (dict): 包含电影信息的字典
            
        Returns:
            MovieInfo: 创建的电影信息对象
        """
        logger.debug(f"从字典创建电影信息对象: {data.get('title', 'Unknown')}")
        
        try:
            movie_info = cls(
                title=data.get('title', ''),
                year=data.get('year', ''),
                rating=data.get('rating', ''),
                poster_path=data.get('poster_path', ''),
                video_path=data.get('video_path', ''),
                resolution=data.get('resolution', ''),
                nfo_path=data.get('nfo_path', '')
            )
            
            logger.info(f"从字典创建电影信息成功: {movie_info.title}")
            return movie_info
            
        except Exception as e:
            logger.exception(f"从字典创建电影信息失败: {str(e)}")
            raise
    
    def get_display_info(self):
        """
        获取用于显示的电影信息摘要
        
        Returns:
            dict: 包含显示所需信息的字典
        """
        logger.debug(f"获取电影显示信息: {self.title}")
        
        return {
            'title': self.title,
            'year': self.year,
            'rating': self.rating,
            'resolution': self.resolution
        }
    
    def has_valid_files(self):
        """
        检查电影文件是否有效
        
        检查视频文件、海报文件等关键文件是否存在。
        
        Returns:
            bool: 如果关键文件存在返回True，否则返回False
        """
        import os
        from pathlib import Path
        
        logger.debug(f"检查电影文件有效性: {self.title}")
        
        try:
            # 检查视频文件
            if self.video_path and Path(self.video_path).exists():
                video_valid = True
                logger.debug(f"视频文件存在: {self.video_path}")
            else:
                video_valid = False
                logger.warning(f"视频文件不存在或路径为空: {self.video_path}")
            
            # 检查海报文件（可选）
            if self.poster_path and Path(self.poster_path).exists():
                poster_valid = True
                logger.debug(f"海报文件存在: {self.poster_path}")
            else:
                poster_valid = False
                logger.debug(f"海报文件不存在或路径为空: {self.poster_path}")
            
            # NFO文件检查（可选）
            if self.nfo_path and Path(self.nfo_path).exists():
                nfo_valid = True
                logger.debug(f"NFO文件存在: {self.nfo_path}")
            else:
                nfo_valid = False
                logger.debug(f"NFO文件不存在或路径为空: {self.nfo_path}")
            
            is_valid = video_valid
            logger.info(f"电影文件有效性检查结果: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.exception(f"检查电影文件有效性时出错: {str(e)}")
            return False
