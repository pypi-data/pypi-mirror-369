class UiDictionary:
    """界面字典类，用于获取界面元素的文本内容"""
    def __init__(self, txt_file):
        self._init_default_values()
        if txt_file:
            self._load_dict(txt_file)
    
    def _init_default_values(self):
        """初始化默认值"""
        self.dict = {
            # Main window related texts
            "error_title": "Error",
            "warning_title": "Warning",
            "category_label": "Category",
            "function_label": "Function",
            "description_label": "Description",
            "open_button": "Open Function",
            "status_format": "Total Categories: {0} | Total Functions: {1}",
            "config_file_not_found": "Configuration file not found",
            "config_format_error": "Configuration file format error",
            "create_sub_window_error": "Failed to create subwindow",
            "no_description": "No description",
            
            # Subwindow related texts
            "back_button": "Back to Main Menu",
            "parameter_group": "Parameter Configuration",
            "log_group": "Execution Log",
            "load_config_button": "Load Configuration",
            "save_config_button": "Save Configuration",
            "run_script_button": "Run Script",
            "notes_label": "Notes",
            "task_running_warning": "A task is already running",
            "execution_start": "Starting execution: {0} - {1}",
            "execution_success": "Task completed successfully! Duration: {0}",
            "execution_failure": "Task failed! Exit code: {0} Duration: {1}",
            "execution_error": "An error occurred during execution: {0}",
            "select_file": "Select File",
            "save_file": "Save File",
            "select_directory": "Select Directory",
            "config_file_label": "Configuration File",
            "load_success": "Configuration loaded successfully!",
            "load_failure": "Failed to load configuration:{0}",
            "save_success": "Configuration saved successfully!",
            "save_failure": "Failed to save configuration:{0}",
            
            # Dialog related texts
            "add_item_title": "Add Item",
            "add_item_prompt": "Enter new item value",
        }
    
    def _load_dict(self, txt_file):
        """加载字典文件"""
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                # 每行以最左侧的:为分隔符，左侧为键，右侧为值。当一行中有多个:时，只分割最左侧的。
                lines = f.readlines()
                for line in lines:
                    if line.startswith("#") or ":" not in line:
                        continue
                    key, value = line.split(":", 1)
                    key = key.strip()
                    if key not in self.dict:  # 忽略字典中不存在的键
                        continue
                    self.dict[key] = value.strip()
        except Exception as e:
            print(f"Failed to load dictionary from {txt_file}, use default values instead. Error: {e}")

    def get(self, key):
        """获取界面元素的文本内容"""
        return self.dict.get(key, key)