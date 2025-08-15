import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import os
import time
import threading
import subprocess
import re
import json
from .tooltip import ToolTip
from .config_manager import ConfigManager
from .utils import format_elapsed_time
from .ui_dict import UiDictionary

class SubWindow:
    def __init__(self, root: tk.Tk, function: dict, ui_dict: UiDictionary, back_callback):
        self.root = root
        self.ud = ui_dict
        self.function = function
        self.back_callback = back_callback
        self.param_vars = {}
        self.param_types = {}
        self.param_widgets = {}
        self.group_frames = {}
        self.dependent_params = {}  # 依赖关系字典
        self.is_running = False
        
        # 配置管理器
        self.config_manager = ConfigManager(function["config_file"])
        
        # 创建子窗口界面
        self.create_ui()
        
        # 加载参数默认值
        self.load_parameters()
        
        # 更新所有依赖参数的状态
        for param_name in self.dependent_params.keys():
            self.update_dependent_state(param_name)
        
        # 更新布局确保正确渲染
        self.root.update_idletasks()
        
    def load_ui_config(self):
        with open(self.function["ui_config_file"], "r", encoding='utf-8') as f:
            ui_config = json.load(f)
        return ui_config
    
    def create_ui(self):
        """创建子窗口界面"""
        # 加载UI配置文件
        ui_config = self.load_ui_config()
        # 返回按钮
        back_btn = ttk.Button(self.root, text=self.ud.get("back_button"), 
                            command=self.back_callback)
        back_btn.pack(anchor="nw", padx=10, pady=5)
        
        # 标题
        ttk.Label(self.root, text=self.function["name"], 
                font=("Arial", 12)).pack(pady=(0,5))
        
        # 描述和注意事项
        desc_frame = ttk.LabelFrame(self.root, text=self.ud.get("description_label"))
        desc_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(desc_frame, text=self.function["description"], 
                wraplength=800).pack(padx=10, pady=5, anchor="w")
        
        if "notes" in ui_config:
            ttk.Label(desc_frame, text=self.ud.get("notes_label") + ":", 
                    font=("Arial", 10, "bold")).pack(padx=10, pady=(10,0), anchor="w")
            ttk.Label(desc_frame, text=ui_config["notes"], 
                    wraplength=800).pack(padx=10, pady=(0,5), anchor="w")
        
        # 主内容区（水平分割）
        main_content = ttk.Frame(self.root)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,10))

        # 左侧参数区
        param_container = ttk.LabelFrame(main_content, text=self.ud.get("parameter_group"))
        param_container.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        
        # 创建带滚动条的Canvas
        param_canvas = tk.Canvas(param_container)
        param_scrollbar = ttk.Scrollbar(param_container, orient="vertical", command=param_canvas.yview)
        scroll_frame = ttk.Frame(param_canvas)
        
        # 配置滚动区域
        scroll_frame.bind("<Configure>", lambda e: param_canvas.configure(scrollregion=param_canvas.bbox("all")))
        param_canvas_id = param_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        param_canvas.configure(yscrollcommand=param_scrollbar.set)
        
        # 布局组件
        param_canvas.pack(side="left", fill="both", expand=True)
        param_scrollbar.pack(side="right", fill="y")

        param_canvas.bind("<Configure>", lambda e: param_canvas.itemconfig(param_canvas_id, width=param_canvas.winfo_width()))
        param_canvas.bind("<Enter>", lambda e: param_canvas.bind_all("<MouseWheel>", lambda evt: param_canvas.yview_scroll(int(-1*(evt.delta/120)), "units")))
        param_canvas.bind("<Leave>", lambda e: param_canvas.unbind_all("<MouseWheel>"))
        
        # === 右侧：日志和按钮区 ===
        right_panel = ttk.Frame(main_content)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(right_panel, text=self.ud.get("log_group"))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 运行按钮区域
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(fill=tk.X, pady=(10,0))
        
        # 添加加载配置按钮
        self.load_btn = ttk.Button(
            btn_frame, 
            text=self.ud.get("load_config_button"),
            command=self.load_config_from_file,
            state=tk.NORMAL
        )
        self.load_btn.pack(side="left", padx=(0, 5))
        
        # 添加保存配置按钮（改为另存为功能）
        self.save_btn = ttk.Button(
            btn_frame, 
            text=self.ud.get("save_config_button"),
            command=self.save_parameters_as,  # 修改为另存为功能
            state=tk.NORMAL
        )
        self.save_btn.pack(side="left", padx=(0, 5))
        
        self.run_btn = ttk.Button(
            btn_frame, 
            text=self.ud.get("run_script_button"),
            command=self.run_script,
            state=tk.NORMAL
        )
        self.run_btn.pack(side="right")
        
        # 设置网格权重确保自适应
        main_content.columnconfigure(0, weight=3, minsize=400)  # 参数区占3/4，最小400px
        main_content.columnconfigure(1, weight=1, minsize=150)  # 日志区占1/4，最小150px
        main_content.rowconfigure(0, weight=1)
        
        # 创建参数控件
        self.create_parameter_controls(scroll_frame, ui_config["groups"])
    
    def create_parameter_controls(self, parent_frame, grouped_params):
        """创建参数输入控件"""
        
        # 为每个分组创建框架
        for group_obj in grouped_params:
            group_name = group_obj["name"]
            params = group_obj["parameters"]
            group_frame = ttk.LabelFrame(parent_frame, text=group_name)
            group_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
            self.group_frames[group_name] = group_frame
            
            for param in params:
                # 记录参数类型
                self.param_types[param["name"]] = param["type"]

                # 为每个参数创建框架
                param_frame = ttk.Frame(group_frame)
                param_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
                
                # 创建标签并添加提示
                label = ttk.Label(param_frame, text=param["label"] + ":", width=15, anchor="e")
                label.pack(side="left", padx=(0,10))
                
                # 添加工具提示
                if "tip" in param:
                    ToolTip(label, param["tip"])
                
                # 根据参数类型创建不同的控件
                if param["type"] == "boolean":
                    # 布尔类型参数 - 使用复选框
                    var = tk.BooleanVar()
                    checkbox = ttk.Checkbutton(param_frame, variable=var)
                    checkbox.pack(side="left", anchor="w")
                    self.param_vars[param["name"]] = var
                    self.param_widgets[param["name"]] = param_frame
                    
                    # 绑定复选框状态变化事件
                    var.trace_add("write", lambda *args, pname=param["name"]: self.update_dependent_state(pname))
                    
                elif param["type"] == "choice":
                    # 选择类型参数 - 使用下拉框
                    var = tk.StringVar()
                    combobox = ttk.Combobox(param_frame, textvariable=var, state="readonly")
                    combobox['values'] = param["choices"]
                    combobox.pack(side="left", fill=tk.X, expand=True)
                    self.param_vars[param["name"]] = var
                    self.param_widgets[param["name"]] = param_frame
                    
                    # 绑定下拉框选择事件
                    var.trace_add("write", lambda *args, pname=param["name"]: self.update_dependent_state(pname))
                    
                elif param["type"] == "array":
                    # 数组类型参数
                    array_frame = ttk.Frame(param_frame)
                    array_frame.pack(fill=tk.X, expand=True, side="left")
                    
                    listbox = tk.Listbox(array_frame, height=4)
                    listbox.pack(side="left", fill=tk.X, expand=True, padx=(0,5))
                    
                    btn_frame = ttk.Frame(array_frame)
                    btn_frame.pack(side="left")
                    
                    add_btn = ttk.Button(btn_frame, text="+", width=3,
                            command=lambda lb=listbox, pt=param: self.add_array_item(lb, pt))
                    add_btn.pack()
                    
                    remove_btn = ttk.Button(btn_frame, text="-", width=3,
                            command=lambda lb=listbox: self.remove_array_item(lb))
                    remove_btn.pack()
                    
                    self.param_vars[param["name"]] = listbox
                    self.param_widgets[param["name"]] = param_frame
                    
                    # 存储按钮以便后续禁用
                    param_frame.add_btn = add_btn
                    param_frame.remove_btn = remove_btn
                    
                elif param["type"] == "file" or param["type"] == "directory" or param["type"] == "save":
                    # 文件/目录路径参数
                    path_frame = ttk.Frame(param_frame)
                    path_frame.pack(fill=tk.X, expand=True, side="left")
                    
                    entry = ttk.Entry(path_frame)
                    entry.pack(side="left", fill=tk.X, expand=True, padx=(0,5))
                    
                    browse_text = (self.ud.get("select_directory") if param["type"] == "directory" else (
                        self.ud.get("select_file") if param["type"] == "file" else self.ud.get("save_file"))
                    )
                    browse_btn = ttk.Button(
                        path_frame, 
                        text=browse_text,
                        width=10,
                        command=lambda e=entry, pt=param: self.browse_path(e, pt)
                    )
                    browse_btn.pack(side="left")
                    
                    self.param_vars[param["name"]] = entry
                    self.param_widgets[param["name"]] = param_frame
                    
                    # 存储按钮以便后续禁用
                    param_frame.browse_btn = browse_btn
                    
                else:
                    # 普通类型参数（字符串/数字）
                    var = tk.StringVar()
                    if param["type"] == "number":
                        entry = ttk.Entry(param_frame, textvariable=var, validate="key")
                        entry.configure(validatecommand=(entry.register(self.validate_number), '%P'))
                    if param["type"] == "integer":
                        entry = ttk.Entry(param_frame, textvariable=var, validate="key")
                        entry.configure(validatecommand=(entry.register(self.validate_integer), '%P'))
                    else:
                        entry = ttk.Entry(param_frame, textvariable=var)
                        
                    entry.pack(side="left", fill=tk.X, expand=True)
                    self.param_vars[param["name"]] = var
                    self.param_widgets[param["name"]] = param_frame
                
                # 处理依赖关系
                if "depends_on" in param:
                    depends_on = param["depends_on"]
                    # 初始禁用依赖参数
                    self.set_param_frame_state(param_frame, 'disabled')
                    
                    # 添加到依赖关系字典
                    if depends_on not in self.dependent_params:
                        self.dependent_params[depends_on] = []
                    self.dependent_params[depends_on].append(param["name"])

    def collect_parameters(self):
        """收集所有参数值并转换为正确类型"""
        config_data = {}
        for param_name, widget in self.param_vars.items():
            param_type = self.param_types.get(param_name, "string")
            
            if isinstance(widget, tk.Listbox):  # 数组类型
                config_data[param_name] = list(widget.get(0, tk.END))
            elif isinstance(widget, tk.BooleanVar):  # 布尔类型
                config_data[param_name] = widget.get()
            elif isinstance(widget, tk.StringVar):  # 字符串变量
                value = widget.get()
                # 根据参数类型转换
                if param_type == "integer":
                    try:
                        config_data[param_name] = int(value) if value else 0
                    except ValueError:
                        config_data[param_name] = value
                elif param_type == "number":
                    try:
                        config_data[param_name] = float(value) if value else 0.0
                    except ValueError:
                        config_data[param_name] = value
                else:
                    config_data[param_name] = value
            else:  # Entry控件（文件/目录路径等）
                value = widget.get()
                # 根据参数类型转换
                if param_type == "integer":
                    try:
                        config_data[param_name] = int(value) if value else 0
                    except ValueError:
                        config_data[param_name] = value
                elif param_type == "number":
                    try:
                        config_data[param_name] = float(value) if value else 0.0
                    except ValueError:
                        config_data[param_name] = value
                else:
                    config_data[param_name] = value
        return config_data    
    def set_param_frame_state(self, frame, state):
        """设置参数框架的状态（禁用/启用）"""
        # 设置框架内所有子控件的状态
        for child in frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Combobox, ttk.Button, ttk.Checkbutton)):
                child.configure(state=state)
            elif isinstance(child, tk.Listbox):
                child.config(state=state)
            elif isinstance(child, tk.Entry):
                child.config(state=state)
            # 递归处理子框架
            if isinstance(child, (ttk.Frame, tk.Frame)):
                self.set_param_frame_state(child, state)
        
        # 处理特殊按钮（在数组和文件类型中存储的按钮）
        if hasattr(frame, 'add_btn'):
            frame.add_btn.configure(state=state)
        if hasattr(frame, 'remove_btn'):
            frame.remove_btn.configure(state=state)
        if hasattr(frame, 'browse_btn'):
            frame.browse_btn.configure(state=state)
    
    def update_dependent_state(self, param_name):
        """更新依赖参数的状态（禁用/启用）"""
        if param_name in self.dependent_params:
            # 获取依赖参数的值
            if param_name in self.param_vars:
                var = self.param_vars[param_name]
                
                # 根据变量类型获取值
                if isinstance(var, tk.BooleanVar):
                    value = var.get()
                elif isinstance(var, tk.StringVar):
                    value = var.get() != "" and var.get() != "False"
                else:
                    value = False
                
                # 更新所有依赖于此参数的控件
                for dependent_name in self.dependent_params[param_name]:
                    if dependent_name in self.param_widgets:
                        widget = self.param_widgets[dependent_name]
                        # 根据条件设置状态
                        state = 'normal' if value else 'disabled'
                        self.set_param_frame_state(widget, state)
    
    def validate_number(self, value):
        """验证数字输入"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def validate_integer(self, value):
        """验证整数输入"""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def browse_path(self, entry_widget, param):
        """打开文件/目录选择对话框"""
        if param["type"] == "directory":
            path = filedialog.askdirectory(title=self.ud.get("select_directory"))
        else:
            # 创建单一文件类型，包含所有指定的扩展名
            filetypes = []
            extensions = []
            
            # 收集所有扩展名
            for ext in param.get("extensions", ["*"]):
                # 支持逗号分隔的多个扩展名
                if "," in ext:
                    extensions.extend([e.strip() for e in ext.split(",")])
                # 支持竖线分隔的多个扩展名
                elif "|" in ext:
                    extensions.extend([e.strip() for e in ext.split("|")])
                else:
                    extensions.append(ext.strip())
            
            # 创建单一文件类型
            patterns = []
            for ext in extensions:
                if ext == "*":
                    patterns.append("*.*")
                else:
                    patterns.append(f"*.{ext}")
            
            # 创建显示名称
            display_name = "; ".join(patterns)
            
            # 创建文件类型
            filetypes.append((display_name, display_name))
            
            # 添加"所有文件"选项
            filetypes.append(("*.*", "*.*"))
            
            if param["type"] == "file":
                path = filedialog.askopenfilename(
                    title=self.ud.get("select_file"),
                    filetypes=filetypes
                )
            else: # param["type"] == "save"
                path = filedialog.asksaveasfilename(
                    title=self.ud.get("select_file"),
                    filetypes=filetypes,
                    defaultextension=filetypes[0][1]
                )
        
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
    
    def add_array_item(self, listbox, param):
        """添加数组项目"""
        if param.get("item_type") == "file":
            # 创建单一文件类型，包含所有指定的扩展名
            filetypes = []
            extensions = []
            
            # 收集所有扩展名
            for ext in param.get("extensions", ["*"]):
                # 支持逗号分隔的多个扩展名
                if "," in ext:
                    extensions.extend([e.strip() for e in ext.split(",")])
                # 支持竖线分隔的多个扩展名
                elif "|" in ext:
                    extensions.extend([e.strip() for e in ext.split("|")])
                else:
                    extensions.append(ext.strip())
            
            # 创建单一文件类型
            patterns = []
            for ext in extensions:
                if ext == "*":
                    patterns.append("*.*")
                else:
                    patterns.append(f"*.{ext}")
            
            # 创建显示名称
            display_name = "; ".join(patterns)
            
            # 创建文件类型
            filetypes.append((display_name, display_name))
            
            # 添加"所有文件"选项
            filetypes.append(("*.*", "*.*"))
            
            items = filedialog.askopenfilenames(
                title=self.ud.get("select_file")    ,
                filetypes=filetypes
            )
        else:
            item = simpledialog.askstring(self.ud.get("add_item_title"), self.ud.get("add_item_prompt"))
            items = [item] if item else []
        
        for item in items:
            listbox.insert(tk.END, item)
    
    def remove_array_item(self, listbox):
        """移除选中的数组项目"""
        selected = listbox.curselection()
        if selected:
            listbox.delete(selected[0])
    
    def load_parameters(self):
        """从配置文件加载参数值"""
        config_data = self.config_manager.load_config()
        if config_data is None:
            return
        
        for param_name, widget in self.param_vars.items():
            if param_name in config_data:
                if isinstance(widget, tk.Listbox):  # 数组类型
                    widget.delete(0, tk.END)
                    for item in config_data[param_name]:
                        widget.insert(tk.END, item)
                elif isinstance(widget, (tk.BooleanVar, tk.StringVar)):  # 布尔或字符串变量
                    widget.set(config_data[param_name])
                else:  # 其他类型
                    widget.delete(0, tk.END)
                    widget.insert(0, str(config_data[param_name]))
    
    def load_config_from_file(self):
        """从用户选择的JSON文件加载配置"""
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(
            title=self.ud.get("load_config_button"),
            filetypes=[(self.ud.get("config_file_label"), "*.json")]
        )
        
        if not file_path:
            return
            
        # 加载配置
        config_data = self.config_manager.load_config_from_file(file_path)
        if config_data is None:
            self.log_message(self.ud.get("load_failure").format(self.config_manager.last_error))
            return
        
        # 应用配置到界面
        for param_name, widget in self.param_vars.items():
            if param_name in config_data:
                if isinstance(widget, tk.Listbox):  # 数组类型
                    widget.delete(0, tk.END)
                    for item in config_data[param_name]:
                        widget.insert(tk.END, item)
                elif isinstance(widget, (tk.BooleanVar, tk.StringVar)):  # 布尔或字符串变量
                    widget.set(config_data[param_name])
                else:  # 其他类型
                    widget.delete(0, tk.END)
                    widget.insert(0, str(config_data[param_name]))
        
        # 更新依赖状态
        for param_name in self.dependent_params.keys():
            self.update_dependent_state(param_name)
        
        self.log_message(self.ud.get("load_success"))
    
    def save_parameters(self):
        """保存参数到默认配置文件"""
        if self.save_btn['state'] == tk.DISABLED:
            return
            
        # 临时禁用保存按钮防止重复点击
        self.save_btn.configure(state=tk.DISABLED)
        
        config_data = self.collect_parameters()
        
        success = self.config_manager.save_config(config_data)
        if success:
            self.log_message(self.ud.get("save_success"))
        else:
            self.log_message(self.ud.get("save_failure").format(self.config_manager.last_error))
        
        self.save_btn.configure(state=tk.NORMAL)
    
    def save_parameters_as(self):
        """另存为配置文件"""
        if self.save_btn['state'] == tk.DISABLED:
            return
            
        # 临时禁用保存按钮防止重复点击
        self.save_btn.configure(state=tk.DISABLED)
        
        # 收集参数数据
        config_data = self.collect_parameters()
        
        # 弹出文件保存对话框
        file_path = filedialog.asksaveasfilename(
            title=self.ud.get("save_config_button"),
            filetypes=[(self.ud.get("config_file_label"), "*.json")],
            defaultextension=".json"
        )
        
        if not file_path:
            self.save_btn.configure(state=tk.NORMAL)
            return
        
        # 保存到指定文件
        success = self.config_manager.save_config_as(file_path, config_data)
        if success:
            self.log_message(self.ud.get("save_success"))
        else:
            self.log_message(self.ud.get("save_failure").format(self.config_manager.last_error))
        
        self.save_btn.configure(state=tk.NORMAL)
    
    def log_message(self, message):
        """在日志区域显示消息"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def clear_log(self):
        """清空日志区域"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def run_script(self):
        """执行脚本"""
        if self.is_running:
            messagebox.showwarning(self.ud.get("warning_title"), self.ud.get("task_running_warning"))
            return
            
        # 保存配置
        self.save_parameters()
            
        self.is_running = True
        self.run_btn.configure(state=tk.DISABLED)
        self.save_btn.configure(state=tk.DISABLED)
        self.load_btn.configure(state=tk.DISABLED)
        
        # 清空日志并记录开始时间
        self.clear_log()
        self.start_time = time.time()
        self.log_message("="*50)
        self.log_message(self.ud.get("execution_start").format(self.function['name'], time.strftime('%Y-%m-%d %H:%M:%S')))
        self.log_message("-"*50)
        
        # 在新线程中执行脚本
        threading.Thread(
            target=self.execute_script_thread,
            daemon=True
        ).start()
    
    def execute_script_thread(self):
        """脚本执行线程"""
        try:
            # 根据脚本后缀选择运行命令
            script_name = self.function["script"]
            script_ext = os.path.splitext(script_name)[1]
            if script_ext == ".py":
                cmd = ["python", self.function["script"]]
            elif script_ext == ".js":
                cmd = ["node", self.function["script"]]
            else: # 其他后缀统一当命令行处理
                cmd = [self.function["script"]]
            cmd.extend(["--config", self.config_manager.get_absolute_path()])
            if self.function.get("args"):
                cmd.extend(self.function["args"])
                
            # 设置环境变量确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
                
            # 执行脚本
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env
            )
            
            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # 过滤ANSI转义序列
                    clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
                    self.root.after(0, self.log_message, clean_output.strip())
            
            # 计算执行时间
            elapsed = time.time() - self.start_time
            time_str = format_elapsed_time(elapsed)
            
            # 检查退出码
            return_code = process.poll()
            if return_code == 0:
                self.root.after(0, self.log_message, "-"*50)
                self.root.after(0, self.log_message, self.ud.get("execution_success").format(time_str))
            else:
                self.root.after(0, self.log_message, "-"*50)
                self.root.after(0, self.log_message, self.ud.get("execution_failure").format(return_code, time_str))
                
        except Exception as e:
            self.root.after(0, self.log_message, self.ud.get("execution_error").format(str(e)))
        finally:
            self.root.after(0, lambda: self.run_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.save_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.load_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: setattr(self, "is_running", False))