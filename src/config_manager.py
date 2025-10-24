import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_file = Path.home() / '.movie_wall_config.json'
        self.default_config = {
            'movie_folders': [],
            'player_path': '',
            'last_position': None
        }
        self._ensure_config_file()

    def _ensure_config_file(self):
        """确保配置文件存在"""
        if not self.config_file.exists():
            self.save_config(self.default_config)
        else:
            # 兼容旧版本配置
            config = self.load_config()
            if 'movie_folder' in config:
                # 将旧的单文件夹配置转换为多文件夹
                folder = config.pop('movie_folder')
                if folder and folder not in config.get('movie_folders', []):
                    config.setdefault('movie_folders', []).append(folder)
                self.save_config(config)

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保 movie_folders 字段存在
                if 'movie_folders' not in config:
                    config['movie_folders'] = []
                return config
        except Exception:
            return self.default_config

    def save_config(self, config):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def update_config(self, updates):
        """更新配置"""
        config = self.load_config()
        config.update(updates)
        self.save_config(config)
