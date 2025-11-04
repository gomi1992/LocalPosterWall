"""
状态消息管理器模块

本模块实现应用程序状态消息的统一管理，采用单例模式确保全局唯一实例。
主要用于管理应用程序底部状态栏的消息显示，支持线程安全的消息更新。

设计特性：
- 单例模式：确保整个应用程序中只有一个状态消息管理器实例
- 线程安全：使用线程锁保护单例创建过程
- 统一管理：集中管理所有状态消息的显示和更新

主要功能：
- 全局状态消息的显示和更新
- 状态栏消息的统一管理
- 线程安全的状态消息操作
- 支持多种消息类型（信息、警告、错误等）

使用场景：
- 电影扫描进度提示
- 错误信息显示
- 操作结果反馈
- 系统状态通知

Author: LocalPosterWall Team
Version: 0.0.1
"""

import threading
import time
from typing import Optional, Any

from loguru import logger


class StatusMessageManager:
    """
    状态消息管理器
    
    负责管理应用程序的状态栏消息显示，采用单例模式确保全局唯一性。
    提供线程安全的状态消息更新机制，支持GUI应用的状态反馈需求。
    
    主要特性：
    - 单例模式：确保应用程序中只有一个实例
    - 线程安全：使用线程锁保护关键操作
    - 消息管理：统一管理所有状态消息
    - 状态栏集成：与Qt状态栏组件集成
    
    使用方法：
        manager = StatusMessageManager.instance()
        manager.show_message("扫描完成", "info")
    """
    
    # 线程锁，确保单例创建的线程安全
    _instance_lock = threading.Lock()
    
    def __init__(self, status_bar=None):
        """
        初始化状态消息管理器
        
        Args:
            status_bar: Qt状态栏组件，用于显示消息
        """
        logger.info("初始化状态消息管理器")
        start_time = time.time()
        
        # 保存状态栏引用
        self.status_bar = status_bar
        logger.debug(f"状态栏组件: {status_bar}")
        
        # 消息历史记录
        self.message_history = []
        logger.debug("消息历史记录已初始化")
        
        # 当前消息信息
        self.current_message = None
        self.current_message_type = None
        
        init_time = time.time() - start_time
        logger.info(f"状态消息管理器初始化完成，耗时: {init_time:.3f}秒")
    
    @classmethod
    def instance(cls, *args, **kwargs):
        """
        获取状态消息管理器单例实例
        
        线程安全的单例实现，使用双重检查锁定模式。
        确保在多线程环境下只能创建一个实例。
        
        Args:
            *args: 初始化参数
            **kwargs: 初始化关键字参数
            
        Returns:
            StatusMessageManager: 状态消息管理器单例实例
        """
        logger.debug("获取状态消息管理器单例实例")
        
        # 第一次检查：不加锁，快速判断
        if not hasattr(StatusMessageManager, "_instance"):
            logger.debug("单例实例不存在，获取创建锁")
            
            # 第二次检查：加锁后再次检查
            with StatusMessageManager._instance_lock:
                if not hasattr(StatusMessageManager, "_instance"):
                    logger.info("创建状态消息管理器单例实例")
                    StatusMessageManager._instance = cls(*args, **kwargs)
                    logger.info("状态消息管理器单例实例创建完成")
                else:
                    logger.debug("在锁获取过程中实例已被创建")
        else:
            logger.debug("单例实例已存在，直接返回")
        
        return StatusMessageManager._instance
    
    def set_status_bar(self, status_bar):
        """
        设置状态栏组件
        
        Args:
            status_bar: Qt状态栏组件
        """
        logger.debug(f"设置状态栏组件: {status_bar}")
        
        self.status_bar = status_bar
        
        # 如果有历史消息，尝试重新显示
        if self.current_message:
            self.show_message(self.current_message, self.current_message_type)
            logger.debug("重新显示当前状态消息")
    
    def show_message(self, message: str, message_type: str = "info", duration: int = 0):
        """
        显示状态消息
        
        Args:
            message (str): 要显示的消息内容
            message_type (str): 消息类型 ("info", "warning", "error", "success")
            duration (int): 显示时长（毫秒），0表示直到下次更新
        """
        logger.info(f"显示状态消息: {message} (类型: {message_type})")
        start_time = time.time()
        
        try:
            # 记录消息到历史
            self._add_to_history(message, message_type)
            
            # 保存当前消息信息
            self.current_message = message
            self.current_message_type = message_type
            
            # 如果有状态栏组件，更新状态栏
            if self.status_bar:
                logger.debug("更新状态栏消息")
                self._update_status_bar(message, message_type, duration)
            else:
                logger.warning("状态栏组件未设置，消息仅记录到历史")
            
            display_time = time.time() - start_time
            logger.debug(f"消息显示操作完成，耗时: {display_time:.3f}秒")
            
        except Exception as e:
            logger.exception(f"显示状态消息失败: {str(e)}")
    
    def _update_status_bar(self, message: str, message_type: str, duration: int):
        """
        更新状态栏显示
        
        Args:
            message (str): 消息内容
            message_type (str): 消息类型
            duration (int): 显示时长
        """
        logger.debug(f"更新状态栏显示: {message}")
        
        try:
            # 根据消息类型设置样式
            style = self._get_message_style(message_type)
            
            # 更新状态栏消息
            if hasattr(self.status_bar, 'showMessage'):
                self.status_bar.showMessage(message, duration)
                logger.debug(f"状态栏消息已更新: {message}")
            
            # 如果支持样式，设置样式
            if hasattr(self.status_bar, 'setStyleSheet'):
                self.status_bar.setStyleSheet(style)
                logger.debug(f"状态栏样式已更新: {message_type}")
            
        except Exception as e:
            logger.exception(f"更新状态栏失败: {str(e)}")
    
    def _get_message_style(self, message_type: str) -> str:
        """
        根据消息类型获取样式
        
        Args:
            message_type (str): 消息类型
            
        Returns:
            str: Qt样式表字符串
        """
        logger.debug(f"获取消息类型样式: {message_type}")
        
        styles = {
            "info": """
                QStatusBar {
                    background-color: #e3f2fd;
                    color: #1976d2;
                }
            """,
            "warning": """
                QStatusBar {
                    background-color: #fff3e0;
                    color: #f57c00;
                }
            """,
            "error": """
                QStatusBar {
                    background-color: #ffebee;
                    color: #d32f2f;
                }
            """,
            "success": """
                QStatusBar {
                    background-color: #e8f5e8;
                    color: #388e3c;
                }
            """
        }
        
        style = styles.get(message_type, styles["info"])
        logger.debug(f"消息样式: {message_type} -> {style.strip()}")
        return style
    
    def _add_to_history(self, message: str, message_type: str):
        """
        添加消息到历史记录
        
        Args:
            message (str): 消息内容
            message_type (str): 消息类型
        """
        try:
            # 记录时间戳和消息信息
            timestamp = time.time()
            history_entry = {
                'timestamp': timestamp,
                'message': message,
                'type': message_type,
                'time_str': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            }
            
            # 添加到历史列表（限制最大历史长度）
            self.message_history.append(history_entry)
            if len(self.message_history) > 100:  # 保留最近100条消息
                self.message_history.pop(0)
            
            logger.debug(f"消息已添加到历史记录: {message}")
            
        except Exception as e:
            logger.exception(f"添加消息到历史记录失败: {str(e)}")
    
    def clear_message(self):
        """清除当前状态消息"""
        logger.info("清除状态消息")
        
        try:
            self.current_message = None
            self.current_message_type = None
            
            if self.status_bar and hasattr(self.status_bar, 'clearMessage'):
                self.status_bar.clearMessage()
                logger.debug("状态栏消息已清除")
            
        except Exception as e:
            logger.exception(f"清除状态消息失败: {str(e)}")
    
    def get_message_history(self) -> list:
        """
        获取消息历史记录
        
        Returns:
            list: 消息历史记录列表
        """
        logger.debug(f"获取消息历史记录，共 {len(self.message_history)} 条")
        return self.message_history.copy()
    
    def get_current_message(self) -> Optional[tuple]:
        """
        获取当前消息信息
        
        Returns:
            tuple/None: (message, message_type) 元组，如果无当前消息则返回None
        """
        if self.current_message:
            logger.debug(f"获取当前消息: {self.current_message}")
            return (self.current_message, self.current_message_type)
        else:
            logger.debug("无当前消息")
            return None
    
    def show_info_message(self, message: str, duration: int = 0):
        """
        显示信息消息
        
        Args:
            message (str): 消息内容
            duration (int): 显示时长（毫秒）
        """
        logger.debug(f"显示信息消息: {message}")
        self.show_message(message, "info", duration)
    
    def show_warning_message(self, message: str, duration: int = 0):
        """
        显示警告消息
        
        Args:
            message (str): 消息内容
            duration (int): 显示时长（毫秒）
        """
        logger.debug(f"显示警告消息: {message}")
        self.show_message(message, "warning", duration)
    
    def show_error_message(self, message: str, duration: int = 0):
        """
        显示错误消息
        
        Args:
            message (str): 消息内容
            duration (int): 显示时长（毫秒）
        """
        logger.debug(f"显示错误消息: {message}")
        self.show_message(message, "error", duration)
    
    def show_success_message(self, message: str, duration: int = 0):
        """
        显示成功消息
        
        Args:
            message (str): 消息内容
            duration (int): 显示时长（毫秒）
        """
        logger.debug(f"显示成功消息: {message}")
        self.show_message(message, "success", duration)
    
    def clear_history(self):
        """清除消息历史记录"""
        logger.info("清除消息历史记录")
        
        try:
            history_count = len(self.message_history)
            self.message_history.clear()
            logger.info(f"已清除 {history_count} 条历史消息")
            
        except Exception as e:
            logger.exception(f"清除消息历史记录失败: {str(e)}")
    
    def __del__(self):
        """析构函数，记录管理器销毁"""
        try:
            logger.debug(f"状态消息管理器实例销毁，历史记录数: {len(self.message_history)}")
        except:
            pass  # 析构时忽略日志错误
