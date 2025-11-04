"""
配置管理器模块

本模块实现应用程序配置的集中管理，负责：
- 应用程序配置的加载和保存
- 配置文件的安全管理和备份
- 配置数据的验证和兼容性处理
- 默认配置的初始化

主要功能：
- JSON格式的配置文件管理
- 用户主目录下的隐藏配置文件
- 向后兼容性支持（从旧版本配置升级）
- 配置数据的完整性和有效性验证
- 自动创建和修复配置文件

配置项：
- movie_folders: 电影文件夹路径列表
- player_path: 默认播放器程序路径
- last_position: 窗口最后位置等状态信息

Author: LocalPosterWall Team
Version: 0.0.1
"""

import json
import os
import time
from pathlib import Path

from loguru import logger


class ConfigManager:
    """
    配置管理器
    
    负责应用程序的配置文件管理，包括：
    - 配置文件的创建和初始化
    - 配置数据的序列化和反序列化
    - 配置兼容性处理和升级
    - 配置数据的验证和错误恢复
    
    配置文件采用JSON格式存储在用户主目录下，
    支持中文内容并自动处理编码问题。
    """
    
    def __init__(self):
        """
        初始化配置管理器
        
        设置配置文件路径，创建默认配置，
        并确保配置文件存在且有效。
        """
        logger.info("=" * 40)
        logger.info("初始化配置管理器")
        start_time = time.time()
        
        try:
            # 设置配置文件路径
            self.config_file = Path.home() / '.movie_wall_config.json'
            logger.debug(f"配置文件路径: {self.config_file}")
            
            # 设置默认配置
            self._setup_default_config()
            logger.debug("默认配置设置完成")
            
            # 确保配置文件存在并有效
            self._ensure_config_file()
            logger.debug("配置文件验证完成")
            
            init_time = time.time() - start_time
            logger.info(f"配置管理器初始化完成，耗时: {init_time:.3f}秒")
            logger.info("=" * 40)
            
        except Exception as e:
            logger.exception(f"配置管理器初始化失败: {str(e)}")
            raise
    
    def _setup_default_config(self):
        """设置默认配置"""
        logger.debug("设置默认配置")
        
        self.default_config = {
            'movie_folders': [],  # 电影文件夹路径列表
            'player_path': '',    # 默认播放器程序路径
            'last_position': None # 窗口最后位置等状态信息
        }
        
        logger.debug(f"默认配置: {self.default_config}")
    
    def _ensure_config_file(self):
        """
        确保配置文件存在并且有效
        
        如果配置文件不存在，创建默认配置文件。
        如果存在但有兼容性问题，进行升级处理。
        """
        logger.debug("确保配置文件存在并有效")
        
        try:
            if not self.config_file.exists():
                logger.info("配置文件不存在，创建默认配置")
                self.save_config(self.default_config)
                logger.info("默认配置文件创建完成")
                return
            
            logger.debug("配置文件已存在，检查兼容性")
            # 配置文件存在，检查兼容性
            self._check_compatibility()
            
        except Exception as e:
            logger.exception(f"确保配置文件失败: {str(e)}")
            # 如果出错，尝试重新创建默认配置
            logger.warning("配置文件损坏，重新创建默认配置")
            self.save_config(self.default_config)
    
    def _check_compatibility(self):
        """
        检查和升级配置文件兼容性
        
        从旧版本配置升级到新版本，支持：
        - movie_folder -> movie_folders (单文件夹到多文件夹)
        - 其他可能的配置字段迁移
        """
        logger.debug("检查配置文件兼容性")
        
        try:
            # 加载当前配置
            config = self.load_config()
            logger.debug(f"当前配置: {config}")
            
            # 检查并处理兼容性
            modified = False
            
            # 处理旧版本的单文件夹配置
            if 'movie_folder' in config:
                logger.info("发现旧版本配置格式，进行升级")
                
                old_folder = config.pop('movie_folder')
                if old_folder:
                    # 将单文件夹转换为多文件夹列表
                    config.setdefault('movie_folders', []).append(old_folder)
                    logger.info(f"迁移旧文件夹配置: {old_folder}")
                    modified = True
                else:
                    logger.debug("旧文件夹配置为空，无需迁移")
            
            # 确保新版本必要字段存在
            if 'movie_folders' not in config:
                config['movie_folders'] = []
                logger.debug("添加movie_folders字段")
                modified = True
            
            # 保存升级后的配置
            if modified:
                logger.info("配置文件兼容性升级完成")
                self.save_config(config)
            else:
                logger.debug("配置文件兼容性检查通过，无需升级")
            
        except Exception as e:
            logger.exception(f"配置文件兼容性检查失败: {str(e)}")
            # 如果检查失败，使用默认配置
            logger.warning("使用默认配置")
            self.save_config(self.default_config)
    
    def load_config(self):
        """
        加载配置文件
        
        读取配置文件并解析为Python对象。
        如果加载失败或配置文件损坏，返回默认配置。
        
        Returns:
            dict: 配置字典，包含所有应用程序设置
        """
        logger.info("开始加载配置文件")
        start_time = time.time()
        
        try:
            # 检查配置文件是否存在
            if not self.config_file.exists():
                logger.warning(f"配置文件不存在: {self.config_file}")
                logger.info("返回默认配置")
                return self.default_config.copy()
            
            # 检查文件是否可以读取
            if not os.access(self.config_file, os.R_OK):
                logger.error(f"配置文件不可读: {self.config_file}")
                return self.default_config.copy()
            
            # 读取配置文件
            logger.debug(f"读取配置文件: {self.config_file}")
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.debug(f"配置文件内容大小: {len(str(config))} 字符")
            
            # 验证和修复配置
            config = self._validate_and_fix_config(config)
            
            load_time = time.time() - start_time
            logger.info(f"配置文件加载完成，耗时: {load_time:.3f}秒")
            logger.debug(f"加载的配置: {config}")
            
            return config
            
        except json.JSONDecodeError as e:
            logger.exception(f"配置文件JSON格式错误: {str(e)}")
            logger.warning("配置文件格式错误，使用默认配置")
            return self.default_config.copy()
        except Exception as e:
            logger.exception(f"加载配置文件失败: {str(e)}")
            logger.warning("配置文件加载失败，使用默认配置")
            return self.default_config.copy()
    
    def _validate_and_fix_config(self, config):
        """
        验证和修复配置数据
        
        检查配置数据的完整性和有效性，
        并自动修复缺失或错误的字段。
        
        Args:
            config (dict): 原始配置数据
            
        Returns:
            dict: 验证和修复后的配置数据
        """
        logger.debug("验证和修复配置数据")
        
        # 确保基本字段存在
        if 'movie_folders' not in config:
            config['movie_folders'] = []
            logger.debug("添加movie_folders字段")
        
        if 'player_path' not in config:
            config['player_path'] = ''
            logger.debug("添加player_path字段")
        
        if 'last_position' not in config:
            config['last_position'] = None
            logger.debug("添加last_position字段")
        
        # 验证字段类型和格式
        if not isinstance(config['movie_folders'], list):
            logger.warning(f"movie_folders字段类型错误: {type(config['movie_folders'])}")
            config['movie_folders'] = []
        
        if not isinstance(config['player_path'], str):
            logger.warning(f"player_path字段类型错误: {type(config['player_path'])}")
            config['player_path'] = ''
        
        logger.debug("配置数据验证和修复完成")
        return config
    
    def save_config(self, config):
        """
        保存配置到文件
        
        将配置数据序列化为JSON格式并写入配置文件。
        
        Args:
            config (dict): 要保存的配置数据
        """
        logger.info("开始保存配置文件")
        start_time = time.time()
        
        try:
            # 验证配置数据
            if not isinstance(config, dict):
                logger.error(f"配置数据必须是字典类型，实际类型: {type(config)}")
                return
            
            logger.debug(f"要保存的配置数据: {config}")
            
            # 确保配置文件目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            logger.debug("配置文件目录已确保存在")
            
            # 写入配置文件
            logger.debug(f"写入配置文件: {self.config_file}")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            # 验证文件是否成功写入
            if self.config_file.exists():
                file_size = self.config_file.stat().st_size
                logger.info(f"配置文件保存成功，文件大小: {file_size} 字节")
            else:
                logger.error("配置文件保存后不存在")
                return
            
            save_time = time.time() - start_time
            logger.info(f"配置文件保存完成，耗时: {save_time:.3f}秒")
            
        except Exception as e:
            logger.exception(f"保存配置文件失败: {str(e)}")
            raise
    
    def update_config(self, updates):
        """
        更新配置
        
        加载当前配置，合并更新内容，然后保存。
        
        Args:
            updates (dict): 要更新的配置项字典
        """
        logger.info("开始更新配置")
        logger.debug(f"更新内容: {updates}")
        start_time = time.time()
        
        try:
            # 加载当前配置
            current_config = self.load_config()
            logger.debug(f"当前配置: {current_config}")
            
            # 合并更新内容
            original_config = current_config.copy()
            current_config.update(updates)
            
            logger.info("配置更新内容已合并")
            logger.debug(f"更新后的配置: {current_config}")
            
            # 保存更新后的配置
            self.save_config(current_config)
            
            update_time = time.time() - start_time
            logger.info(f"配置更新完成，耗时: {update_time:.3f}秒")
            
        except Exception as e:
            logger.exception(f"更新配置失败: {str(e)}")
            raise
    
    def get_config_path(self):
        """
        获取配置文件路径
        
        Returns:
            str: 配置文件的完整路径字符串
        """
        logger.debug(f"获取配置文件路径: {self.config_file}")
        return str(self.config_file)
    
    def backup_config(self, backup_path=None):
        """
        备份配置文件
        
        Args:
            backup_path (str/Path, optional): 备份文件路径，如果为None则自动生成
        """
        logger.info("开始备份配置文件")
        
        try:
            if not self.config_file.exists():
                logger.warning("配置文件不存在，无法备份")
                return None
            
            if backup_path is None:
                # 自动生成备份文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_path = self.config_file.parent / f"{self.config_file.stem}_backup_{timestamp}.json"
            else:
                backup_path = Path(backup_path)
            
            logger.debug(f"备份目标路径: {backup_path}")
            
            # 复制配置文件
            import shutil
            shutil.copy2(self.config_file, backup_path)
            
            logger.info(f"配置文件备份完成: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.exception(f"配置文件备份失败: {str(e)}")
            return None
    
    def reset_to_default(self):
        """
        重置配置为默认值
        
        将所有配置恢复为默认设置。
        """
        logger.info("重置配置为默认值")
        
        try:
            self.save_config(self.default_config)
            logger.info("配置已重置为默认设置")
            
        except Exception as e:
            logger.exception(f"重置配置失败: {str(e)}")
            raise
