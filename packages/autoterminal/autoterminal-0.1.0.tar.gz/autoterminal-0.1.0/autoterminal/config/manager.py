import os
import json
from typing import Dict, Any

class ConfigManager:
    """配置管理器，支持配置的保存和验证"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # 将配置文件存储在用户主目录下的.autoterminal目录中
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".autoterminal")
            # 确保目录存在
            os.makedirs(config_dir, exist_ok=True)
            self.config_file = os.path.join(config_dir, "config.json")
        else:
            self.config_file = config_file
            
        self.required_keys = ['api_key', 'base_url', 'model']
        self.default_config = {
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-4o',
            'default_prompt': '你现在是一个终端助手,用户输入想要生成的命令,你来输出一个命令,不要任何多余的文本!'
        }
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file) if os.path.dirname(self.config_file) else '.', exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"错误: 无法保存配置文件 {self.config_file}: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否完整"""
        for key in self.required_keys:
            if not config.get(key):
                return False
        return True
    
    def initialize_config(self) -> Dict[str, Any]:
        """初始化配置向导"""
        print("欢迎使用AutoTerminal配置向导！")
        print("请提供以下信息以完成配置：")
        
        config = self.default_config.copy()
        
        # 获取API密钥
        api_key = input("请输入您的API密钥: ").strip()
        if not api_key:
            print("错误: API密钥不能为空")
            return {}
        config['api_key'] = api_key
        
        # 获取Base URL
        base_url = input(f"请输入Base URL (默认: {self.default_config['base_url']}): ").strip()
        if base_url:
            config['base_url'] = base_url
        
        # 获取模型名称
        model = input(f"请输入模型名称 (默认: {self.default_config['model']}): ").strip()
        if model:
            config['model'] = model
        
        # 保存配置
        if self.save_config(config):
            print(f"配置已保存到 {self.config_file}")
            return config
        else:
            print("配置保存失败")
            return {}
    
    def get_or_create_config(self) -> Dict[str, Any]:
        """获取现有配置或创建新配置"""
        # 尝试从文件加载配置
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 验证配置
                if self.validate_config(config):
                    print("已加载现有配置")
                    return config
                else:
                    print("现有配置不完整")
            except Exception as e:
                print(f"警告: 无法读取配置文件 {self.config_file}: {e}")
        
        # 如果配置不存在或不完整，启动初始化向导
        return self.initialize_config()
