import tkinter as tk
from tkinter import ttk
import threading
import queue
import json
import logging
from datetime import datetime
from tkinter import filedialog
import tkinter.messagebox as tm
from modules.password_cracker import PasswordCracker
import csv
import pdb
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='security_tool.log'
)
# 设置全局样式
STYLE = {
    'bg_color': '#f5f6fa',  # 更柔和的背景色
    'button_color': '#3498db',  # 更现代的按钮颜色
    'button_hover': '#2980b9',  # 按钮悬停颜色
    'button_text_color': 'white',
    'label_color': '#2c3e50',  # 更深的文字颜色
    'entry_bg': 'white',
    'text_bg': 'white',
    'border_color': '#bdc3c7',  # 边框颜色
    'font': ('Microsoft YaHei UI', 10),  # 默认字体
    'title_font': ('Microsoft YaHei UI', 12, 'bold')  # 标题字体
}

def configure_style():
    """配置ttk样式"""
    style = ttk.Style()
    
    # 配置Notebook样式
    style.configure('TNotebook', 
        background=STYLE['bg_color'],
        padding=5)
    style.configure('TNotebook.Tab', 
        padding=[10, 5],
        font=STYLE['font'])
    
    # 配置Frame样式
    style.configure('TFrame',
        background=STYLE['bg_color'])
    
    # 配置Label样式
    style.configure('TLabel',
        font=STYLE['font'],
        padding=5,
        foreground=STYLE['label_color'])
    
    # 配置Entry样式    
    style.configure('TEntry',
        fieldbackground=STYLE['entry_bg'],
        padding=5,
        font=STYLE['font'])
    
    # 配置Button样式
    style.configure('TButton',
        font=STYLE['font'],
        padding=[15, 8],
        background=STYLE['button_color'],
        foreground=STYLE['button_text_color'])

def create_custom_button(parent, **kwargs):
    """创建自定义按钮"""
    button = tk.Button(parent,
        bg=STYLE['button_color'],
        fg=STYLE['button_text_color'],
        font=STYLE['font'],
        relief='flat',
        padx=15,
        pady=8,
        cursor='hand2',
        activebackground=STYLE['button_hover'],
        activeforeground=STYLE['button_text_color'],
        **kwargs)
    return button

def create_custom_entry(parent, **kwargs):
    """创建自定义输入框"""
    entry = tk.Entry(parent,
        bg=STYLE['entry_bg'],
        font=STYLE['font'],
        relief='solid',
        bd=1,
        highlightthickness=1,
        highlightcolor=STYLE['button_color'],
        **kwargs)
    return entry

def create_custom_text(parent, **kwargs):
    """创建自定义文本框"""
    text = tk.Text(parent,
        bg=STYLE['text_bg'],
        font=STYLE['font'],
        relief='solid',
        bd=1,
        padx=8,
        pady=8,
        highlightthickness=1,
        highlightcolor=STYLE['button_color'],
        **kwargs)
    return text
class SecurityToolGUI:
    def __init__(self, root):
        """初始化安全工具GUI"""
        self.root = root
        self.root.title("安全工具集")
        self.root.geometry("900x700")
        self.root.configure(bg=STYLE['bg_color'])
        
        # 配置全局样式
        configure_style()
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # 创建各个功能的标签页
        self.password_frame = ttk.Frame(self.notebook)
        self.domain_frame = ttk.Frame(self.notebook)
        self.proxy_frame = ttk.Frame(self.notebook)
        
        # 添加标签页到notebook
        self.notebook.add(self.password_frame, text='密码爆破')
        self.notebook.add(self.domain_frame, text='域名扫描')
        self.notebook.add(self.proxy_frame, text='代理IP池')
        
        # 初始化各个标签页的内容
        self.setup_password_frame()
        self.setup_domain_frame()
        self.setup_proxy_frame()
        
        # 创建状态栏
        self.status_bar = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化队列用于线程通信
        self.result_queue = queue.Queue()
        
        # 启动结果处理线程
        self.process_results()
    def setup_password_frame(self):
        """设置密码爆破界面"""
        main_container = ttk.Frame(self.password_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 配置权重
        self.password_frame.grid_columnconfigure(0, weight=1)
        self.password_frame.grid_rowconfigure(0, weight=1)

        # 配置选项组
        settings_frame = ttk.LabelFrame(main_container, text="配置选项", padding=10)
        settings_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # 配置文件开关和选择（放在最上方）
        config_frame = ttk.Frame(settings_frame)
        config_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.use_config = tk.BooleanVar(value=False)
        tk.Checkbutton(config_frame, 
                       text="使用配置文件", 
                       variable=self.use_config,
                       command=self.toggle_config_mode).grid(row=0, column=0, padx=5)

        tk.Label(config_frame, text="配置文件:").grid(row=0, column=1, padx=5)
        self.config_path = create_custom_entry(config_frame, width=30)
        self.config_path.grid(row=0, column=2, padx=5, sticky="ew")
        create_custom_button(config_frame, text="选择配置", 
                            command=self.select_config).grid(row=0, column=3, padx=5)

        # 目标URL
        tk.Label(settings_frame, text="目标URL:").grid(row=1, column=0, padx=5, pady=5)
        self.target_entry = create_custom_entry(settings_frame)
        self.target_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # 用户名
        tk.Label(settings_frame, text="用户名:").grid(row=2, column=0, padx=5, pady=5)
        self.username_entry = create_custom_entry(settings_frame)
        self.username_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # 字典选择
        tk.Label(settings_frame, text="密码字典:").grid(row=3, column=0, padx=5, pady=5)
        self.dict_path = create_custom_entry(settings_frame)
        self.dict_path.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        create_custom_button(settings_frame, text="选择字典", command=self.select_dict).grid(row=3, column=2, padx=5, pady=5)

        # 破解模式选择
        tk.Label(settings_frame, text="破解模式:").grid(row=4, column=0, padx=5, pady=5)
        modes_frame = ttk.Frame(settings_frame)
        modes_frame.grid(row=4, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        self.mode_vars = []
        modes = [("字典攻击", "dict"), ("纯数字攻击", "numeric"), ("暴力破解", "brute")]
        for i, (text, mode) in enumerate(modes):
            var = tk.BooleanVar()
            self.mode_vars.append((mode, var))
            tk.Checkbutton(modes_frame, text=text, variable=var).grid(row=0, column=i, padx=5)

        # 线程数设置
        tk.Label(settings_frame, text="线程数:").grid(row=5, column=0, padx=5, pady=5)
        self.thread_count = ttk.Spinbox(settings_frame, from_=1, to=20, width=5)
        self.thread_count.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.thread_count.set("5")

        # 代理设置
        proxy_label_frame = ttk.LabelFrame(settings_frame, text="代理设置", padding=5)
        proxy_label_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        # 代理模式选择
        proxy_mode_frame = ttk.Frame(proxy_label_frame)
        proxy_mode_frame.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.proxy_mode = tk.StringVar(value="不使用代理")
        modes = ["不使用代理", "使用代理池", "单个代理"]
        for i, mode in enumerate(modes):
            tk.Radiobutton(proxy_mode_frame, text=mode, 
                          variable=self.proxy_mode, 
                          value=mode, 
                          command=self.on_proxy_mode_change).grid(row=0, column=i, padx=5)

        # 代理设置区域
        self.proxy_settings_frame = ttk.Frame(proxy_label_frame)
        self.proxy_settings_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # 单个代理设置
        self.single_proxy_frame = ttk.Frame(self.proxy_settings_frame)
        tk.Label(self.single_proxy_frame, text="代理地址:").grid(row=0, column=0, padx=5)
        self.proxy_entry = create_custom_entry(self.single_proxy_frame, width=30)
        self.proxy_entry.grid(row=0, column=1, padx=5)
        self.proxy_entry.insert(0, "http://proxy:port")

        # 代理池设置
        self.proxy_pool_frame = ttk.Frame(self.proxy_settings_frame)
        tk.Label(self.proxy_pool_frame, text="代理来源:").grid(row=0, column=0, padx=5)
        self.proxy_source = ttk.Combobox(self.proxy_pool_frame, 
                                        values=["免费代理", "付费API"], 
                                        state="readonly", 
                                        width=15)
        self.proxy_source.grid(row=0, column=1, padx=5)
        self.proxy_source.set("免费代理")

        create_custom_button(self.proxy_pool_frame, 
                            text="更新代理池", 
                            command=self.update_proxy_pool).grid(row=0, column=2, padx=5)

        # 代理测试结果
        self.proxy_result = create_custom_text(proxy_label_frame, height=3, width=40)
        self.proxy_result.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # 初始化代理模式显示
        self.on_proxy_mode_change()

        # 结果显示
        result_frame = ttk.LabelFrame(main_container, text="破解结果", padding=10)
        result_frame.grid(row=1, column=0, sticky="nsew")

        self.pwd_result = create_custom_text(result_frame, height=600, width=60)
        self.pwd_result.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 添加滚动条
        scrollbar_result = ttk.Scrollbar(result_frame, orient="vertical", command=self.pwd_result.yview)
        scrollbar_result.grid(row=0, column=1, sticky="ns")
        self.pwd_result.configure(yscrollcommand=scrollbar_result.set)

        # 控制按钮
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=2, column=0, pady=10)

        create_custom_button(button_frame, text="加载配置", command=self.load_config).grid(row=0, column=0, padx=5)
        create_custom_button(button_frame, text="保存配置", command=self.save_config).grid(row=0, column=1, padx=5)
        create_custom_button(button_frame, text="开始爆破", command=self.start_crack).grid(row=0, column=2, padx=5)
        create_custom_button(button_frame, text="停止", command=self.stop_crack).grid(row=0, column=3, padx=5)

        # 配置权重
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)

    """def setup_password_frame(self):
        # 创建主容器
        main_container = ttk.Frame(self.password_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 配置权重
        self.password_frame.grid_columnconfigure(0, weight=1)
        self.password_frame.grid_rowconfigure(0, weight=1)

        # 配置选项组
        settings_frame = ttk.LabelFrame(main_container, text="配置选项", padding=10)
        settings_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # 配置文件开关和选择（放在最上方）
        config_frame = ttk.Frame(settings_frame)
        config_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.use_config = tk.BooleanVar(value=False)
        tk.Checkbutton(config_frame, 
                       text="使用配置文件", 
                       variable=self.use_config,
                       command=self.toggle_config_mode).grid(row=0, column=0, padx=5)

        tk.Label(config_frame, text="配置文件:").grid(row=0, column=1, padx=5)
        self.config_path = create_custom_entry(config_frame, width=30)
        self.config_path.grid(row=0, column=2, padx=5, sticky="ew")
        create_custom_button(config_frame, text="选择配置", 
                            command=self.select_config).grid(row=0, column=3, padx=5)

        # 分隔线
        ttk.Separator(settings_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)

        # 主要配置区域
        main_settings = ttk.Frame(settings_frame)
        main_settings.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        # 目标URL
        tk.Label(main_settings, text="目标URL:").grid(row=0, column=0, padx=5, pady=5)
        self.target_entry = create_custom_entry(main_settings)
        self.target_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # 用户名
        tk.Label(main_settings, text="用户名:").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = create_custom_entry(main_settings)
        self.username_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # 字典选择
        tk.Label(main_settings, text="密码字典:").grid(row=2, column=0, padx=5, pady=5)
        self.dict_path = create_custom_entry(main_settings)
        self.dict_path.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        create_custom_button(main_settings, text="选择字典", 
                            command=self.select_dict).grid(row=2, column=2, padx=5, pady=5)

        # 破解模式选择
        tk.Label(main_settings, text="破解模式:").grid(row=3, column=0, padx=5, pady=5)
        self.crack_mode = ttk.Combobox(main_settings, 
                                      values=["字典攻击", "纯数字", "暴力"], 
                                      state="readonly",
                                      width=10)
        self.crack_mode.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.crack_mode.set("字典攻击")
        
        # 结果显示
        result_frame = ttk.LabelFrame(main_container, text="破解结果", padding=10)
        result_frame.grid(row=1, column=0, sticky="nsew")
        
        self.pwd_result = create_custom_text(result_frame, height=20, width=60)
        self.pwd_result.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 控制按钮
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=2, column=0, pady=10)
        
        create_custom_button(button_frame, text="开始爆破", command=self.start_crack).grid(row=0, column=0, padx=5)
        create_custom_button(button_frame, text="停止", command=self.stop_crack).grid(row=0, column=1, padx=5)
        
        # 配置权重
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)"""

    def setup_domain_frame(self):
        """设置域名扫描界面"""
        # 创建主容器
        main_container = ttk.Frame(self.domain_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 配置权重
        self.domain_frame.grid_columnconfigure(0, weight=1)
        self.domain_frame.grid_rowconfigure(0, weight=1)

        # 扫描配置区域
        settings_frame = ttk.LabelFrame(main_container, text="扫描配置", padding=10)
        settings_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # 目标域名
        tk.Label(settings_frame, text="目标域名:").grid(row=0, column=0, padx=5, pady=5)
        self.domain_entry = create_custom_entry(settings_frame)
        self.domain_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        tk.Label(settings_frame, text="例如: example.com").grid(row=0, column=3, padx=5, pady=5)

        # 扫描方式
        tk.Label(settings_frame, text="扫描方式:").grid(row=1, column=0, padx=5, pady=5)
        self.scan_mode = ttk.Combobox(settings_frame, 
                                     values=["字典爆破", "DNS查询", "证书查询", "综合扫描"],
                                     state="readonly",
                                     width=10)
        self.scan_mode.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.scan_mode.set("字典爆破")

        # 字典选择（仅字典爆破模式可用）
        tk.Label(settings_frame, text="子域名字典:").grid(row=2, column=0, padx=5, pady=5)
        self.subdomain_dict = create_custom_entry(settings_frame)
        self.subdomain_dict.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        create_custom_button(settings_frame, text="选择字典", 
                            command=self.select_subdomain_dict).grid(row=2, column=2, padx=5, pady=5)

        # 高级选项
        advanced_frame = ttk.LabelFrame(settings_frame, text="高级选项", padding=5)
        advanced_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

        # 线程数
        tk.Label(advanced_frame, text="线程数:").grid(row=0, column=0, padx=5, pady=5)
        self.thread_count = ttk.Spinbox(advanced_frame, from_=1, to=50, width=5)
        self.thread_count.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.thread_count.set("10")

        # DNS服务器
        tk.Label(advanced_frame, text="DNS服务器:").grid(row=0, column=2, padx=5, pady=5)
        self.dns_server = create_custom_entry(advanced_frame, width=15)
        self.dns_server.grid(row=0, column=3, padx=5, pady=5)
        self.dns_server.insert(0, "8.8.8.8")

        # 超时设置
        tk.Label(advanced_frame, text="超时(秒):").grid(row=0, column=4, padx=5, pady=5)
        self.timeout = ttk.Spinbox(advanced_frame, from_=1, to=10, width=5)
        self.timeout.grid(row=0, column=5, sticky="w", padx=5, pady=5)
        self.timeout.set("3")

        # 结果显示
        result_frame = ttk.LabelFrame(main_container, text="扫描结果", padding=10)
        result_frame.grid(row=1, column=0, sticky="nsew")

        # 创建表格显示结果
        columns = ("子域名", "IP地址", "状态码", "标题")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings")

        # 设置列
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=100)

        self.result_tree.grid(row=0, column=0, sticky="nsew")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_tree.configure(yscrollcommand=scrollbar.set)

        # 控制按钮
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=2, column=0, pady=10)

        create_custom_button(button_frame, text="开始扫描", 
                            command=self.start_scan).grid(row=0, column=0, padx=5)
        create_custom_button(button_frame, text="停止扫描", 
                            command=self.stop_scan).grid(row=0, column=1, padx=5)
        create_custom_button(button_frame, text="导出结果", 
                            command=self.export_results).grid(row=0, column=2, padx=5)

        # 配置权重
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)

    def setup_proxy_frame(self):
        """设置代理IP池界面"""
        # 创建主容器
        main_container = ttk.Frame(self.proxy_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 配置权重
        self.proxy_frame.grid_columnconfigure(0, weight=1)
        self.proxy_frame.grid_rowconfigure(0, weight=1)

        # 代理添加区域
        input_frame = ttk.LabelFrame(main_container, text="添加代理", padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # 代理类型选择
        tk.Label(input_frame, text="代理类型:").grid(row=0, column=0, padx=5, pady=5)
        self.proxy_type = ttk.Combobox(input_frame, 
                                      values=["HTTP", "SOCKS4", "SOCKS5"],
                                      state="readonly",
                                      width=8)
        self.proxy_type.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.proxy_type.set("HTTP")

        # IP地址输入
        tk.Label(input_frame, text="IP地址:").grid(row=0, column=2, padx=5, pady=5)
        self.proxy_ip = create_custom_entry(input_frame, width=15)
        self.proxy_ip.grid(row=0, column=3, padx=5, pady=5)

        # 端口输入
        tk.Label(input_frame, text="端口:").grid(row=0, column=4, padx=5, pady=5)
        self.proxy_port = create_custom_entry(input_frame, width=6)
        self.proxy_port.grid(row=0, column=5, padx=5, pady=5)

        # 用户名输入（可选）
        tk.Label(input_frame, text="用户名:").grid(row=1, column=0, padx=5, pady=5)
        self.proxy_username = create_custom_entry(input_frame, width=15)
        self.proxy_username.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # 密码输入（可选）
        tk.Label(input_frame, text="密码:").grid(row=1, column=3, padx=5, pady=5)
        self.proxy_password = create_custom_entry(input_frame, width=15, show="*")
        self.proxy_password.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

        # 添加按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)

        create_custom_button(button_frame, text="添加代理", 
                            command=self.add_proxy).grid(row=0, column=0, padx=5)
        create_custom_button(button_frame, text="测试代理", 
                            command=self.test_proxy).grid(row=0, column=1, padx=5)
        create_custom_button(button_frame, text="导入代理", 
                            command=self.import_proxies).grid(row=0, column=2, padx=5)

        # 代理列表
        list_frame = ttk.LabelFrame(main_container, text="代理列表", padding=10)
        list_frame.grid(row=1, column=0, sticky="nsew")

        # 创建代理列表
        columns = ("类型", "IP地址", "端口", "用户名", "状态", "延迟")
        self.proxy_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        # 设置列
        for col in columns:
            self.proxy_tree.heading(col, text=col)
            width = 100 if col not in ["IP地址", "用户名"] else 150
            self.proxy_tree.column(col, width=width)

        self.proxy_tree.grid(row=0, column=0, sticky="nsew")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.proxy_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.proxy_tree.configure(yscrollcommand=scrollbar.set)

        # 控制按钮
        control_frame = ttk.Frame(main_container)
        control_frame.grid(row=2, column=0, pady=10)

        create_custom_button(control_frame, text="删除选中", 
                            command=self.delete_proxy).grid(row=0, column=0, padx=5)
        create_custom_button(control_frame, text="清空列表", 
                            command=self.clear_proxies).grid(row=0, column=1, padx=5)
        create_custom_button(control_frame, text="导出代理", 
                            command=self.export_proxies).grid(row=0, column=2, padx=5)

        # 配置权重
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

    def add_proxy(self):
        """添加代理到列表"""
        try:
            # 获取输入
            proxy_type = self.proxy_type.get()
            ip = self.proxy_ip.get().strip()
            port = self.proxy_port.get().strip()
            username = self.proxy_username.get().strip()
            password = self.proxy_password.get().strip()

            # 验证输入
            if not ip or not port:
                self.show_message("请输入IP地址和端口")
                return

            # 验证端口
            try:
                port = int(port)
                if not (0 <= port <= 65535):
                    raise ValueError()
            except ValueError:
                self.show_message("请输入有效的端口号(0-65535)")
                return

            # 添加到列表
            self.proxy_tree.insert("", "end", values=(
                proxy_type,
                ip,
                port,
                username if username else "-",
                "未测试",
                "-"
            ))

            # 清空输入框
            self.proxy_ip.delete(0, tk.END)
            self.proxy_port.delete(0, tk.END)
            self.proxy_username.delete(0, tk.END)
            self.proxy_password.delete(0, tk.END)

            self.show_message("代理添加成功")

        except Exception as e:
            self.show_message(f"添加代理时出错: {str(e)}")

    def test_proxy(self):
        """测试选中的代理"""
        selected = self.proxy_tree.selection()
        if not selected:
            self.show_message("请先选择要测试的代理")
            return

        def test_task():
            for item in selected:
                values = self.proxy_tree.item(item)['values']
                try:
                    # 这里添加实际的代理测试逻辑
                    # 模拟测试结果
                    import time
                    time.sleep(1)  # 模拟测试延迟
                    status = "可用"
                    delay = "200ms"

                    # 更新状态
                    self.proxy_tree.set(item, "状态", status)
                    self.proxy_tree.set(item, "延迟", delay)

                except Exception as e:
                    self.proxy_tree.set(item, "状态", "不可用")
                    self.proxy_tree.set(item, "延迟", "-")

        # 在新线程中执行测试
        threading.Thread(target=test_task, daemon=True).start()
    def process_results(self):
        """处理结果队列"""
        try:
            while True:
                pdb.set_trace()
                result = self.result_queue.get_nowait()
                if result['type'] == 'password':
                    self.pwd_result.insert(tk.END, f"{result['message']}\n")
                elif result['type'] == 'domain':
                    # 假设 result['message'] 是形如 "发现子域名: example.com -> 192.168.1.1" 的字符串
                    parts = result['message'].split(" -> ")
                    if len(parts) == 2:
                        subdomain, ip = parts
                        self.result_tree.insert("", "end", values=(subdomain, ip, "", ""))
                elif result['type'] == 'proxy':
                    self.proxy_list.insert("", tk.END, values=result['data'])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_results)
    def import_proxies(self):
        """从文件导入代理"""
        filename = filedialog.askopenfilename(
            title='导入代理',
            filetypes=[
                ('文本文件', '*.txt'),
                ('CSV 文件', '*.csv'),
                ('所有文件', '*.*')
            ]
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # 解析代理格式（假设格式为：类型,IP,端口,用户名,密码）
                    parts = line.split(',')
                    if len(parts) >= 3:
                        proxy_type = parts[0] if len(parts) > 0 else "HTTP"
                        ip = parts[1]
                        port = parts[2]
                        username = parts[3] if len(parts) > 3 else "-"

                        self.proxy_tree.insert("", "end", values=(
                            proxy_type,
                            ip,
                            port,
                            username,
                            "未测试",
                            "-"
                        ))

            self.show_message(f"成功导入代理")

        except Exception as e:
            self.show_message(f"导入代理时出错: {str(e)}")

    def delete_proxy(self):
        """删除选中的代理"""
        selected = self.proxy_tree.selection()
        if not selected:
            self.show_message("请先选择要删除的代理")
            return

        for item in selected:
            self.proxy_tree.delete(item)

        self.show_message(f"已删除 {len(selected)} 个代理")

    def clear_proxies(self):
        """清空代理列表"""
        if tm.askyesno("确认", "确定要清空所有代理吗？"):
            for item in self.proxy_tree.get_children():
                self.proxy_tree.delete(item)
            self.show_message("代理列表已清空")

    def export_proxies(self):
        """导出代理列表"""
        filename = filedialog.asksaveasfilename(
            title='导出代理',
            defaultextension='.csv',
            filetypes=[
                ('CSV 文件', '*.csv'),
                ('文本文件', '*.txt'),
                ('所有文件', '*.*')
            ]
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(["类型", "IP地址", "端口", "用户名", "状态", "延迟"])
                # 写入数据
                for item in self.proxy_tree.get_children():
                    writer.writerow(self.proxy_tree.item(item)['values'])

            self.show_message(f"代理列表已导出到: {filename}")

        except Exception as e:
            self.show_message(f"导出代理时出错: {str(e)}")
    def select_subdomain_dict(self):
        """选择子域名字典文件"""
        filename = filedialog.askopenfilename(
            title='选择子域名字典',
            filetypes=[
                ('文本文件', '*.txt'),
                ('所有文件', '*.*')
            ],
            initialdir='./'  # 默认打开当前目录
        )

        if filename:
            self.subdomain_dict.delete(0, tk.END)
            self.subdomain_dict.insert(0, filename)
            self.show_message(f"已选择子域名字典: {filename}")
    def stop_scan(self):
        """停止域名扫描"""
        try:
            # 更新界面状态
            self.show_message("正在停止扫描...")
    
            # 禁用停止按钮，启用开始按钮
            for child in self.domain_frame.winfo_children():
                if isinstance(child, tk.Button):
                    if child['text'] == "开始扫描":
                        child['state'] = 'normal'
                    elif child['text'] == "停止扫描":
                        child['state'] = 'disabled'
    
            # 通知扫描器停止
            if hasattr(self, 'current_scanner'):
                self.current_scanner.stop_event.set()
    
            # 清理资源
            if hasattr(self, 'scan_thread') and self.scan_thread.is_alive():
                self.scan_thread.join(timeout=2)  # 等待线程结束，最多等待2秒
    
            self.show_message("扫描已停止")
        
        except Exception as e:
            self.show_message(f"停止扫描时出错: {str(e)}")

    def export_results(self):
        """导出扫描结果"""
        try:
            # 获取保存文件路径
            filename = filedialog.asksaveasfilename(
                title='导出结果',
                defaultextension='.csv',
                filetypes=[
                    ('CSV 文件', '*.csv'),
                    ('文本文件', '*.txt'),
                    ('所有文件', '*.*')
                ]
            )

            if not filename:
                return

            # 获取表格中的所有数据
            results = []
            for item in self.result_tree.get_children():
                results.append(self.result_tree.item(item)['values'])

            # 写入文件
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(["子域名", "IP地址", "状态码", "标题"])
                # 写入数据
                writer.writerows(results)

            self.show_message(f"结果已导出到: {filename}")

        except Exception as e:
            self.show_message(f"导出结果时出错: {str(e)}")
    def toggle_config_mode(self):
        """切换配置文件模式"""
        if self.use_config.get():
            # 启用配置文件模式
            self.config_path.configure(state='normal')
            # 如果有配置文件路径，自动加载配置
            if self.config_path.get():
                self.load_config()
        else:
            # 禁用配置文件模式
            self.config_path.configure(state='disabled')
            self.config_path.delete(0, tk.END)
    def stop_crack(self):
        """停止密码破解进程"""
        try:
            # 更新界面状态
            self.show_message("正在停止破解...")

            # 禁用开始按钮，启用停止按钮
            for child in self.password_frame.winfo_children():
                if isinstance(child, tk.Button):
                    if child['text'] == "开始爆破":
                        child['state'] = 'normal'
                    elif child['text'] == "停止":
                        child['state'] = 'disabled'

            # 通知破解器停止
            if hasattr(self, 'current_cracker'):
                self.current_cracker.stop()

            # 清理资源
            if hasattr(self, 'crack_thread') and self.crack_thread.is_alive():
                self.crack_thread.join(timeout=2)  # 等待线程结束，最多等待2秒

            self.show_message("破解已停止")

            # 在结果区域显示停止信息
            self.pwd_result.insert(tk.END, "\n破解过程已手动停止\n")
            self.pwd_result.see(tk.END)  # 滚动到最底部

        except Exception as e:
            self.show_message(f"停止破解时出错: {str(e)}")
        def select_config(self):
            """选择配置文件"""
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if filename:
                self.config_path.delete(0, tk.END)
                self.config_path.insert(0, filename)

    def load_config(self):
        """加载配置文件"""
        if not self.use_config.get():
            self.show_message("请先启用配置文件模式")
            return

        config_file = self.config_path.get()
        if not config_file:
            self.show_message("请选择配置文件")
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 更新界面
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, config.get("url", ""))

            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, config.get("username", ""))

            self.dict_path.delete(0, tk.END)
            self.dict_path.insert(0, config.get("dictionary_file", ""))

            self.thread_count.delete(0, tk.END)
            self.thread_count.insert(0, str(config.get("thread_count", 5)))

            # 更新模式选择
            mode_map = {1: "dict", 2: "numeric", 3: "brute"}
            selected_modes = [mode_map.get(m) for m in config.get("modes", [1])]
            for mode, var in self.mode_vars:
                var.set(mode in selected_modes)

            self.show_message("配置加载成功")
        except Exception as e:
            self.show_message(f"加载配置失败: {str(e)}")

    def save_config(self):
        """保存当前配置"""
        if not self.use_config.get():
            self.show_message("请先启用配置文件模式")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not filename:
            return

        config = {
            "url": self.target_entry.get(),
            "username": self.username_entry.get(),
            "dictionary_file": self.dict_path.get(),
            "thread_count": int(self.thread_count.get()),
            "modes": []
        }

        # 收集选中的模式
        mode_map = {"dict": 1, "numeric": 2, "brute": 3}
        for mode, var in self.mode_vars:
            if var.get():
                config["modes"].append(mode_map[mode])

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.show_message("配置保存成功")
        except Exception as e:
            self.show_message(f"保存配置失败: {str(e)}")
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    

    def select_dict(self):
        """选择密码字典文件"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename()
        if filename:
            self.dict_path.delete(0, tk.END)
            self.dict_path.insert(0, filename)
    def select_config(self):
        """选择配置文件"""
        try:
            filename = filedialog.askopenfilename(
                title='选择配置文件',
                filetypes=[
                    ('JSON文件', '*.json'),
                    ('所有文件', '*.*')
                ],
                initialdir='./'  # 默认打开当前目录
            )

            if filename:
                # 清除并更新配置文件路径
                self.config_path.delete(0, tk.END)
                self.config_path.insert(0, filename)

                # 自动加载选择的配置
                self.load_config()

                self.show_message(f"已选择配置文件: {filename}")

        except Exception as e:
            self.show_message(f"选择配置文件时出错: {str(e)}")
            logging.error(f"选择配置文件错误: {str(e)}")
    def start_crack(self):
        """开始密码爆破"""
        target = self.target_entry.get()
        dict_path = self.dict_path.get()
        # 根据配置模式获取参数
        if self.use_config.get() and not self.config_path.get():
            self.show_message("请选择配置文件")
            return
        if not target:
            self.show_message("请输入目标URL")
            return

        # 禁用开始按钮，启用停止按钮
        for child in self.password_frame.winfo_children():
            if isinstance(child, tk.Button):
                if child['text'] == "开始爆破":
                    child['state'] = 'disabled'
                elif child['text'] == "停止":
                    child['state'] = 'normal'
        proxy_source = self.proxy_mode.get()
        if proxy_source == "使用代理池":
            # 从代理池获取代理列表
            proxy_pool = []
            for item in self.proxy_list.get_children():
                values = self.proxy_list.item(item)['values']
                proxy_pool.append({
                    'address': f"{values[0]}:{values[1]}",
                    'type': values[2],
                    'speed': values[3]
                })
            self.current_cracker.set_proxy_pool(proxy_pool)
        elif proxy_source == "单个代理":
            proxy = self.proxy_entry.get()
            if proxy:
                self.current_cracker.set_proxy(proxy)
            # 创建新的破解器实例
            self.current_cracker = PasswordCracker(target, dict_path)

            # 启动破解线程
            self.crack_thread = threading.Thread(
                target=self.password_crack_thread,
                args=(target, dict_path)
            )
            self.crack_thread.start()

            self.show_message("密码爆破开始...")
        else:
            # 创建新的破解器实例
            self.current_cracker = PasswordCracker(target, dict_path)

            # 启动破解线程
            self.crack_thread = threading.Thread(
                target=self.password_crack_thread,
                args=(target, dict_path)
            )
            self.crack_thread.start()

            self.show_message("密码爆破开始...")
    def on_proxy_mode_change(self):
        """处理代理模式变化"""
        mode = self.proxy_mode.get()

        # 清除当前显示的代理设置
        for widget in self.proxy_settings_frame.winfo_children():
            widget.grid_remove()

        # 根据选择显示相应的设置
        if mode == "单个代理":
            self.single_proxy_frame.grid(row=0, column=0, sticky="w")
        elif mode == "使用代理池":
            self.proxy_pool_frame.grid(row=0, column=0, sticky="w")

    def update_proxy_pool(self):
        """更新代理池"""
        try:
            self.proxy_result.delete(1.0, tk.END)
            self.proxy_result.insert(tk.END, "正在更新代理池...\n")

            def update_task():
                try:
                    proxy_source = self.proxy_source.get()
                    # 这里添加实际的代理池更新逻辑
                    # 临时模拟代理获取
                    self.current_proxies = ["http://proxy1:8080", "http://proxy2:8080"]

                    self.proxy_result.delete(1.0, tk.END)
                    self.proxy_result.insert(tk.END, f"成功获取 {len(self.current_proxies)} 个可用代理\n")
                except Exception as e:
                    self.proxy_result.delete(1.0, tk.END)
                    self.proxy_result.insert(tk.END, f"更新代理池失败: {str(e)}\n")

            # 在新线程中执行更新任务
            threading.Thread(target=update_task, daemon=True).start()
        except Exception as e:
            self.show_message(f"更新代理池出错: {str(e)}")

    def start_scan(self):
        """开始域名扫描"""
        domain = self.domain_entry.get()
        scan_type = self.scan_mode.get()
        
        if not domain:
            self.show_message("请输入目标域名")
            return
            
        threading.Thread(target=self.domain_scan_thread, args=(domain, scan_type)).start()
        self.show_message("域名扫描开始...")

    def update_proxy(self):
        """更新代理池"""
        source = self.proxy_source.get()
        threading.Thread(target=self.proxy_update_thread, args=(source,)).start()
        self.show_message("正在更新代理池...")

    def show_message(self, message):
        """显示状态栏消息"""
        self.status_bar.config(text=message)


    def password_crack_thread(self, target, dict_path):
        """密码爆破线程"""
        try:
            for result in self.current_cracker.start():
                if result:
                    self.result_queue.put({
                        'type': 'password',
                        'message': result
                    })

                # 检查是否需要停止
                if hasattr(self.current_cracker, 'stop_event') and \
                   self.current_cracker.stop_event.is_set():
                    break

        except Exception as e:
            self.result_queue.put({
                'type': 'password',
                'message': f"错误: {str(e)}"
            })
        finally:
            # 恢复按钮状态
            self.root.after(0, self.reset_buttons)
    def reset_buttons(self):
        """重置按钮状态"""
        for child in self.password_frame.winfo_children():
            if isinstance(child, tk.Button):
                if child['text'] == "开始爆破":
                    child['state'] = 'normal'
                elif child['text'] == "停止":
                    child['state'] = 'disabled'

    def domain_scan_thread(self, domain, scan_type):
        """域名扫描线程"""
        from modules.domain_scanner import DomainScanner
        scanner = DomainScanner(domain)
        for result in scanner.scan(scan_type):
            self.result_queue.put({
                'type': 'domain',
                'message': result
            })

    def proxy_update_thread(self, source):
        """代理池更新线程"""
        from modules.proxy_pool import ProxyPool
        pool = ProxyPool()
        for proxy in pool.update(source):
            self.result_queue.put({
                'type': 'proxy',
                'data': proxy
            })

def main():
    root = tk.Tk()
    app = SecurityToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 