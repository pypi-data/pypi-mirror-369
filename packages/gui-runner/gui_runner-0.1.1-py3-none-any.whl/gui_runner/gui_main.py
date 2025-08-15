import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from .gui_subwindow import SubWindow
from .ui_dict import UiDictionary

class ConfigurableGUI:
    """
    基于Tkinter的可配置化GUI运行器
    """
    def __init__(self, root: tk.Tk, dict_file: str, config_file: str):
        """
        初始化GUI

        :param root: Tkinter的根窗口对象
        :param dict_file: UI字典文件
        :param config_file: UI配置文件
        """
        # 加载配置文件
        self.load_config(config_file)
        
        # 初始化GUI
        self.root = root
        self.ud = UiDictionary(dict_file)
        self.root.title(self.config["main_title"])
        self.root.geometry("1280x720")
        self.root.resizable(True, True)
        
        # 创建主界面
        self.create_main_frame()
        
        # 当前任务状态
        self.is_running = False
        
    def load_config(self, ui_config):
        """加载UI配置文件"""
        try:
            with open(ui_config, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
        except FileNotFoundError:
            # 创建默认配置结构
            self.config = {
                "main_title": "GUI Runner",
                "categories": [
                    {
                        "name": "Sample Category",
                        "description": "This is a sample category, you need to edit configuration file to add functions.",
                        "functions": []
                    }
                ]
            }
            # 自动保存默认配置
            with open(ui_config, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except json.JSONDecodeError:
            messagebox.showerror(self.ud.get("error_title"), self.ud.get("config_format_error"))
            exit(1)
    
    def create_main_frame(self):
        """创建主功能选择界面（树状结构）"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_container, text=self.config["main_title"], 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(5, 10))
        
        # 树状视图容器
        tree_container = ttk.Frame(main_container)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建树状视图
        self.tree = ttk.Treeview(tree_container, show="tree", selectmode="browse")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加分类和功能
        for cat_idx, category in enumerate(self.config["categories"]):
            category_id = self.tree.insert("", "end", text=category["name"], 
                                         values=["category", str(cat_idx)])
            self.tree.item(category_id, open=True)
            
            for func_idx, function in enumerate(category["functions"]):
                self.tree.insert(category_id, "end", text=function["name"], 
                               values=["function", f"{cat_idx},{func_idx}"])
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.open_selected_function)
        
        # 描述面板
        desc_frame = ttk.LabelFrame(main_container, text=self.ud.get("description_label"))
        desc_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=6, state=tk.DISABLED)
        self.desc_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 底部按钮
        btn_frame = ttk.Frame(main_container, name="btn_frame")
        btn_frame.pack(fill=tk.X, pady=(5, 0), padx=10)
        
        self.open_btn = ttk.Button(btn_frame, text=self.ud.get("open_button"), state=tk.DISABLED,
                                  command=self.open_selected_function)
        self.open_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 状态栏
        status_bar = ttk.Frame(main_container)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        total_functions = sum(len(cat["functions"]) for cat in self.config["categories"])
        status_text = self.ud.get("status_format").format(
            len(self.config['categories']), total_functions
        )
        ttk.Label(status_bar, text=status_text, font=("Arial", 9)).pack(side=tk.LEFT)
        
        # 保存当前选择状态
        self.last_selected_item = None
        
    def on_tree_select(self, event):
        """树状视图选择事件处理"""
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, "values")
        if not values or len(values) < 2:
            return
            
        item_type, item_ref = values
        
        # 更新描述面板
        self.desc_text.configure(state=tk.NORMAL)
        self.desc_text.delete(1.0, tk.END)
        
        if item_type == "category":
            try:
                cat_idx = int(item_ref)
                category = self.config["categories"][cat_idx]
                self.desc_text.insert(tk.END, category.get("description", ""))
                
                # 更新按钮状态
                self.open_btn.configure(state=tk.DISABLED, text=self.ud.get("open_button"))
            except (ValueError, IndexError):
                self.desc_text.insert(tk.END, self.ud.get("no_description"))
        
        elif item_type == "function":
            try:
                cat_idx, func_idx = map(int, item_ref.split(','))
                function = self.config["categories"][cat_idx]["functions"][func_idx]
                self.desc_text.insert(tk.END, function.get("description", ""))
                
                # 更新按钮状态
                self.open_btn.configure(state=tk.NORMAL, text=f"{self.ud.get('open_button')}")
            except (ValueError, IndexError):
                self.desc_text.insert(tk.END, self.ud.get("no_description"))
        
        self.desc_text.configure(state=tk.DISABLED)
        
        # 保存当前选择状态
        self.last_selected_item = selected_item
    
    def open_selected_function(self, event=None):
        """打开选中的功能"""
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, "values")
        if not values or len(values) < 2:
            return
            
        item_type, item_ref = values
        
        if item_type == "function":
            try:
                cat_idx, func_idx = map(int, item_ref.split(','))
                function = self.config["categories"][cat_idx]["functions"][func_idx]
                self.create_sub_window(function)
            except (ValueError, IndexError):
                messagebox.showerror(self.ud.get("error_title"), self.ud.get("create_sub_window_error"))

    def create_sub_window(self, function):
        """创建功能子界面"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        # 创建子窗口
        self.sub_window = SubWindow(self.root, function, self.ud, self.create_main_frame)