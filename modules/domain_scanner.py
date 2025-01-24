import dns.resolver
import socket
import threading
import queue
import logging
import ssl

class DomainScanner:
    def __init__(self, domain, subdomain_dict_path="dict/subdomains.txt"):
        self.domain = domain
        self.subdomain_dict_path = subdomain_dict_path
        self.results = queue.Queue()
        self.stop_event = threading.Event()  # 用于停止扫描

    def scan_subdomain(self, subdomain):
        """扫描子域名"""
        try:
            full_domain = f"{subdomain}.{self.domain}"
            answers = dns.resolver.resolve(full_domain)
            for rdata in answers:
                self.results.put(f"发现子域名: {full_domain} -> {rdata.address}")
        except:
            pass

    def scan_port(self, port):
        """扫描端口"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.domain, port))
            if result == 0:
                self.results.put(f"端口 {port} 开放")
            sock.close()
        except:
            pass

    def dns_query(self, subdomain):
        """DNS查询"""
        self.scan_subdomain(subdomain)

    def ssl_certificate_query(self, domain):
        """证书查询"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    self.results.put(f"证书信息: {domain} -> {cert}")
        except Exception as e:
            self.results.put(f"证书查询错误: {domain} -> {str(e)}")

    def scan(self, scan_type):
        """开始扫描"""
        threads = []

        if scan_type == "字典爆破":
            # 从文件加载子域名字典
            try:
                with open(self.subdomain_dict_path, "r") as f:
                    subdomains = f.read().splitlines()
            except FileNotFoundError:
                self.results.put(f"错误: 子域名字典文件 {self.subdomain_dict_path} 未找到")
                return
            except Exception as e:
                self.results.put(f"错误: 读取子域名字典文件时出错: {str(e)}")
                return

            for subdomain in subdomains:
                if self.stop_event.is_set():
                    break
                t = threading.Thread(target=self.scan_subdomain, args=(subdomain,))
                threads.append(t)
                t.start()

        elif scan_type == "DNS查询":
            # 从文件加载子域名字典
            try:
                with open(self.subdomain_dict_path, "r") as f:
                    subdomains = f.read().splitlines()
            except FileNotFoundError:
                self.results.put(f"错误: 子域名字典文件 {self.subdomain_dict_path} 未找到")
                return
            except Exception as e:
                self.results.put(f"错误: 读取子域名字典文件时出错: {str(e)}")
                return

            for subdomain in subdomains:
                if self.stop_event.is_set():
                    break
                t = threading.Thread(target=self.dns_query, args=(subdomain,))
                threads.append(t)
                t.start()

        elif scan_type == "证书查询":
            # 扫描主域名的证书
            t = threading.Thread(target=self.ssl_certificate_query, args=(self.domain,))
            threads.append(t)
            t.start()

        elif scan_type == "综合扫描":
            # 从文件加载子域名字典
            try:
                with open(self.subdomain_dict_path, "r") as f:
                    subdomains = f.read().splitlines()
            except FileNotFoundError:
                self.results.put(f"错误: 子域名字典文件 {self.subdomain_dict_path} 未找到")
                return
            except Exception as e:
                self.results.put(f"错误: 读取子域名字典文件时出错: {str(e)}")
                return

            for subdomain in subdomains:
                if self.stop_event.is_set():
                    break
                t = threading.Thread(target=self.dns_query, args=(subdomain,))
                threads.append(t)
                t.start()

            # 扫描主域名的证书
            t = threading.Thread(target=self.ssl_certificate_query, args=(self.domain,))
            threads.append(t)
            t.start()

            # 扫描端口
            for port in range(1, 1025):  # 扫描常见端口
                if self.stop_event.is_set():
                    break
                t = threading.Thread(target=self.scan_port, args=(port,))
                threads.append(t)
                t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 返回结果
        while not self.results.empty():
            yield self.results.get()