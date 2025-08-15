import json
import os

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.last_error = None
    
    def load_config(self):
        """从配置文件加载参数值"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.last_error = str(e)
            return None
    
    def load_config_from_file(self, file_path):
        """从指定文件加载配置"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.last_error = str(e)
            return None
    
    def save_config(self, config_data):
        """保存参数到配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def save_config_as(self, file_path, config_data):
        """另存为配置文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
        
    def get_absolute_path(self):
        """获取当前配置文件的绝对路径"""
        return os.path.abspath(self.config_file)