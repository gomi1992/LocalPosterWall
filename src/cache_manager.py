"""
缓存管理器模块

本模块实现了电影信息的本地缓存功能，用于提高应用性能。
缓存管理器负责将电影扫描结果保存到本地文件，避免重复扫描，
并使用Base64编码和JSON格式进行数据存储。

主要功能：
- 电影列表缓存存储和读取
- Base64编码保护敏感数据
- JSON格式数据序列化/反序列化
- 自动创建和验证缓存文件
- 异常处理和错误恢复

技术特性：
- 缓存文件默认存储在用户主目录
- 数据使用Base64编码防止意外读取
- JSON格式保证数据可移植性
- 完善的异常处理机制

Author: LocalPosterWall Team
Version: 0.0.1
"""

import base64
import json
import time
from pathlib import Path

from loguru import logger


class CacheManager:
    """
    电影信息缓存管理器

    负责管理电影扫描结果的本地缓存，包括：
    - 缓存文件的创建和定位
    - 数据的序列化和反序列化
    - Base64编码保护数据安全
    - 异常处理和数据完整性检查
    """

    def __init__(self, cache_path=None):
        """
        初始化缓存管理器

        Args:
            cache_path (str/Path, optional): 自定义缓存文件路径，
                                          如果为None则使用默认路径
        """
        logger.info("初始化缓存管理器")

        if cache_path is None:
            # 默认缓存路径：用户主目录下的.movie_wall_cache.json
            self.cache_file = Path.home() / '.movie_wall_cache.json'
            logger.debug(f"使用默认缓存路径: {self.cache_file}")
        else:
            # 使用自定义缓存路径
            self.cache_file = Path(cache_path)
            logger.debug(f"使用自定义缓存路径: {self.cache_file}")

        logger.info(f"缓存管理器初始化完成，缓存文件: {self.cache_file}")

    def get_cache(self):
        """
        从缓存文件读取电影列表

        读取缓存文件，解码Base64数据，反序列化为Python对象。
        如果读取失败，返回空列表。

        Returns:
            list: 电影信息列表，如果缓存文件不存在或读取失败则返回空列表
        """
        logger.info("开始读取缓存数据")
        start_time = time.time()

        try:
            # 检查缓存文件是否存在
            if not self.cache_file.exists():
                logger.warning(f"缓存文件不存在: {self.cache_file}")
                logger.info("返回空缓存")
                return []

            if not self.cache_file.is_file():
                logger.error(f"缓存路径不是文件: {self.cache_file}")
                return []

            # 检查文件大小，如果为0则视为空缓存
            file_size = self.cache_file.stat().st_size
            logger.debug(f"缓存文件大小: {file_size} 字节")

            if file_size == 0:
                logger.info("缓存文件为空，返回空列表")
                return []

            # 读取缓存文件
            logger.debug("开始读取缓存文件")
            with open(self.cache_file, 'r', encoding="utf-8") as f:
                encoded_content = f.read()

            logger.debug(f"读取到编码内容，长度: {len(encoded_content)} 字符")

            # 解码Base64数据
            logger.debug("开始Base64解码")
            decoded_content = self.b64decode(encoded_content)
            logger.debug(f"解码后内容长度: {len(decoded_content)} 字符")

            # 反序列化JSON数据
            logger.debug("开始JSON反序列化")
            cache_data = json.loads(decoded_content)
            logger.info(f"缓存读取成功，共 {len(cache_data)} 条记录")

            # 记录性能统计
            read_time = time.time() - start_time
            logger.debug(f"缓存读取耗时: {read_time:.3f}秒")

            return cache_data

        except FileNotFoundError:
            logger.warning(f"缓存文件未找到: {self.cache_file}")
            return []
        except json.JSONDecodeError as e:
            logger.exception(f"缓存文件JSON格式错误: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"读取缓存文件失败: {str(e)}")
            return []

    def set_cache(self, cache):
        """
        将电影列表保存到缓存文件

        将电影列表数据序列化为JSON字符串，进行Base64编码后写入文件。

        Args:
            cache (list): 要缓存的电影信息列表
        """
        logger.info("开始保存缓存数据")
        start_time = time.time()

        try:
            # 检查输入数据
            if not isinstance(cache, list):
                logger.error(f"缓存数据必须是列表类型，实际类型: {type(cache)}")
                return

            logger.debug(f"要缓存的电影数量: {len(cache)}")

            # 序列化为JSON字符串
            logger.debug("开始JSON序列化")
            json_str = json.dumps(cache, ensure_ascii=False, indent=2)
            logger.debug(f"JSON序列化完成，内容长度: {len(json_str)} 字符")

            # Base64编码
            logger.debug("开始Base64编码")
            encoded_data = self.b64encode(json_str)
            logger.debug(f"Base64编码完成，编码后长度: {len(encoded_data)} 字符")

            # 确保缓存目录存在
            self._ensure_cache_directory()

            # 写入缓存文件
            logger.debug(f"写入缓存文件: {self.cache_file}")
            with open(self.cache_file, 'w', encoding="utf-8") as f:
                f.write(encoded_data)

            # 验证文件是否成功写入
            if self.cache_file.exists():
                file_size = self.cache_file.stat().st_size
                logger.info(f"缓存保存成功，文件大小: {file_size} 字节")
            else:
                logger.error("缓存文件保存后不存在")
                return

            # 记录性能统计
            save_time = time.time() - start_time
            logger.info(f"缓存保存完成，耗时: {save_time:.3f}秒")
            logger.info(f"成功缓存 {len(cache)} 条电影记录")

        except Exception as e:
            logger.exception(f"保存缓存失败: {str(e)}")

    def _ensure_cache_directory(self):
        """
        确保缓存目录存在

        如果缓存文件的父目录不存在，创建它。
        """
        logger.debug(f"确保缓存目录存在: {self.cache_file.parent}")

        try:
            # 创建父目录（如果不存在）
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            logger.debug("缓存目录创建/验证完成")

        except Exception as e:
            logger.exception(f"创建缓存目录失败: {str(e)}")
            raise

    def b64encode(self, data):
        """
        Base64编码数据

        将字符串数据使用Base64编码，通常用于数据存储前的加密处理。

        Args:
            data (str): 要编码的字符串数据

        Returns:
            str: Base64编码后的字符串
        """
        logger.debug(f"开始Base64编码，数据长度: {len(data)} 字符")

        try:
            # 转换为bytes并进行Base64编码
            encoded_bytes = base64.b64encode(data.encode("utf-8"))
            encoded_str = encoded_bytes.decode()

            logger.debug(f"Base64编码完成，输出长度: {len(encoded_str)} 字符")

            # 输出编码信息用于调试（避免输出敏感数据）
            logger.debug(
                f"Base64编码统计信息: 输入={len(data)}, 输出={len(encoded_str)}, 比率={len(encoded_str) / len(data):.2f}")

            return encoded_str

        except Exception as e:
            logger.exception(f"Base64编码失败: {str(e)}")
            raise

    def b64decode(self, encoded_string):
        """
        Base64解码数据

        将Base64编码的字符串解码为原始数据。

        Args:
            encoded_string (str): Base64编码的字符串

        Returns:
            str: 解码后的原始字符串
        """
        logger.debug(f"开始Base64解码，输入长度: {len(encoded_string)} 字符")

        try:
            # Base64解码并转换为字符串
            decoded_bytes = base64.b64decode(encoded_string)
            decoded_str = decoded_bytes.decode("utf-8")

            logger.debug(f"Base64解码完成，输出长度: {len(decoded_str)} 字符")

            return decoded_str

        except Exception as e:
            logger.exception(f"Base64解码失败: {str(e)}")
            raise

    def clear_cache(self):
        """
        清除所有缓存数据

        删除缓存文件并清理相关状态。
        """
        logger.info("开始清除缓存数据")

        try:
            if self.cache_file.exists():
                file_size = self.cache_file.stat().st_size
                self.cache_file.unlink()
                logger.info(f"缓存文件已删除，原文件大小: {file_size} 字节")
            else:
                logger.debug("缓存文件不存在，无需清除")

            logger.info("缓存清除完成")

        except Exception as e:
            logger.exception(f"清除缓存失败: {str(e)}")

    def get_cache_info(self):
        """
        获取缓存信息

        Returns:
            dict: 包含缓存文件信息的字典
        """
        logger.debug("获取缓存信息")

        try:
            info = {
                'cache_file': str(self.cache_file),
                'exists': self.cache_file.exists(),
                'size': 0,
                'modified_time': None,
                'readable': False
            }

            if self.cache_file.exists():
                stat = self.cache_file.stat()
                info['size'] = stat.st_size
                info['modified_time'] = stat.st_mtime
                info['readable'] = self.cache_file.is_file() and self.cache_file.stat().st_size > 0

            logger.debug(f"缓存信息: {info}")
            return info

        except Exception as e:
            logger.exception(f"获取缓存信息失败: {str(e)}")
            return {}

    def backup_cache(self, backup_path=None):
        """
        备份缓存文件

        Args:
            backup_path (str/Path, optional): 备份文件路径，如果为None则自动生成
        """
        logger.info("开始备份缓存文件")

        try:
            if not self.cache_file.exists():
                logger.warning("缓存文件不存在，无需备份")
                return None

            if backup_path is None:
                # 自动生成备份文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_path = self.cache_file.parent / f"{self.cache_file.stem}_backup_{timestamp}.json"
            else:
                backup_path = Path(backup_path)

            logger.debug(f"备份目标路径: {backup_path}")

            # 复制缓存文件
            import shutil
            shutil.copy2(self.cache_file, backup_path)

            logger.info(f"缓存备份完成: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.exception(f"缓存备份失败: {str(e)}")
            return None
