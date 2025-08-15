import os
import json
from typing import Dict, Optional

class ConfigLoader:
    """配置加载器，支持从文件加载配置"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # 从用户主目录下的.autoterminal目录中加载配置文件
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".autoterminal")
            self.config_file = os.path.join(config_dir, "config.json")
        else:
            self.config_file = config_file
    
    def load_from_file(self) -> Dict:
        """从配置文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告: 无法读取配置文件 {self.config_file}: {e}")
        return {}
    
    def get_config(self) -> Dict:
        """获取配置"""
        return self.load_from_file()
