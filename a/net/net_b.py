import os
import pymsgbox

try:
    import paramiko
except ImportError:
    os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
    os.system("pip install paramiko")
    import paramiko    
import stat

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, PhotoImage
import threading
import time
from datetime import datetime
import configparser

import sys
import traceback

from PIL import Image, ImageTk  # 添加PIL支持

class ImageManager:
    """图像管理器"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.img_dir = os.path.join(base_dir, "img")
        self.images = {}
        
    def load_all_images(self):
        """加载所有图像"""
        # 确保图像目录存在
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
            print(f"创建图像目录: {self.img_dir}")
            return False
            
        image_files = {
            'upload': 'upload.png',
            'download': 'download.png',
            'newfolder': 'newfolder.png',
            'rename': 'rename.png',
            'delete': 'delete.png',
            'refresh': 'refresh.png',
            'up': 'up.png',
            'home': 'home.png',
            'trash': 'trash.png',
            'restore': 'restore.png'
        }
        
        for key, filename in image_files.items():
            filepath = os.path.join(self.img_dir, filename)
            try:
                if os.path.exists(filepath):
                    # 使用PIL加载图像并调整大小
                    pil_image = Image.open(filepath)
                    pil_image = pil_image.resize((18, 18), Image.Resampling.LANCZOS)  # 统一大小
                    self.images[key] = ImageTk.PhotoImage(pil_image)
                    print(f"加载图像: {filename}")
                else:
                    print(f"警告: 图像文件不存在: {filepath}")
                    self.images[key] = None
            except Exception as e:
                print(f"加载图像 {filename} 时出错: {e}")
                self.images[key] = None
                
        return True
    
    def get_image(self, key):
        """获取图像"""
        return self.images.get(key)
    
    def create_default_images(self):
        """创建默认的占位图像（如果图像文件不存在）"""
        # 这里可以添加代码来创建简单的默认图像
        print("请将图像文件放入 img 目录中")
        return False

class ini:
    def __init__(self, a):
        if os.path.exists(f"{a}\\config.ini"):
            self.config = configparser.ConfigParser()
            self.config.read(f'{a}\\config.ini')
            keys = self.config.options("host")
            for ggvg in keys:
                print(self.get(ggvg))
        else:
            messagebox.showerror("", "文件不存在")
            sys.exit()
    
    def get(self, key: str):
        try:
            keys = self.config.options("host")
            if key in keys:
                m = self.config.get("host", key)
                return m
        except:
            return None
        
    def getint(self, key: str):
        try:
            keys = self.config.options("host")
            if key in keys:
                m = self.config.getint("host", key)
                return m
        except:
            return None


def count_local_files(local_path):
    """计算本地目录中的文件数量"""
    file_count = 0
    try:
        for root, dirs, files in os.walk(local_path):
            file_count += len(files)
    except Exception as e:
        print(f"计算本地目录文件数量时出错: {e}")
    return file_count


class net:
    def __init__(self, host, port=22, username="", password=""):

        try:

            self.asf = paramiko.Transport((host, port))
            self.asf.connect(username=username, password=password)
            self.sftp = paramiko.SFTPClient.from_transport(self.asf) 
            print(self.sftp.listdir("/"))

            self.file_list = KeyValueTable()
            self.file_lista = [""]
            self.getfile_list()
            self.download = int(0)
            self.total = int(0)
            self.jndex = False
            # 目录传输相关变量
            self.dir_transferred = 0
            self.dir_total = 0
            self.dir_jndex = False
            self.dir_file_count = 0
            self.dir_current_file = 0
            self.dir_progress_callback = None
            self.upload_dir_transferred = 0
            self.upload_dir_total = 0
            self.upload_dir_jndex = False
            self.upload_dir_file_count = 0
            self.upload_dir_current_file = 0
            self.upload_dir_progress_callback = None
        except paramiko.ssh_exception.AuthenticationException as e:
            print(e)
            messagebox.showerror("登录错误", "密码或用户名错误")
            sys.exit()
        except paramiko.ssh_exception.NoValidConnectionsError:
            messagebox.showerror("服务器不存在", "服务器不存在或连接超时")
            sys.exit()
        except paramiko.ssh_exception.SSHException:
            messagebox.showerror("ssh错误", "服务器未启动ssh或sftp")
            sys.exit()
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"连接失败: {str(e)}")

    def upload_directory_with_progress(self, local_path, remote_path, progress_callback=None):
        """上传目录并显示总进度"""
        try:
            # 计算本地目录文件数量
            self.upload_dir_file_count = count_local_files(local_path)
            self.upload_dir_transferred = 0
            self.upload_dir_current_file = 0
            self.upload_dir_jndex = True
            self.upload_dir_progress_callback = progress_callback

            print(f"开始上传目录: {local_path}, 文件数量: {self.upload_dir_file_count}")

            # 开始上传
            success = self._upload_directory_recursive(local_path, remote_path)
            self.upload_dir_jndex = False
            return success
        except Exception as e:
            print(f"上传目录时出错: {e}")
            self.upload_dir_jndex = False
            return False

    def _upload_directory_recursive(self, local_path, remote_path):
        """递归上传目录"""
        # 创建远程目录
        if not self.exists(remote_path):
            self.md(remote_path)

        # 获取本地目录内容
        items = os.listdir(local_path)

        for item in items:
            local_item_path = os.path.join(local_path, item)
            remote_item_path = f"{remote_path}/{item}"

            if os.path.isdir(local_item_path):
                # 递归上传子目录
                if not self._upload_directory_recursive(local_item_path, remote_item_path):
                    return False
            else:
                # 上传文件
                if not self._upload_file_with_progress(local_item_path, remote_item_path):
                    return False

        return True

    def _upload_file_with_progress(self, local_path, remote_path):
        """上传文件并更新总进度"""

        def custom_callback(transferred, total):
            # 更新当前文件进度
            self.download = transferred
            self.total = total
            self.jndex = True

            # 如果这是目录传输，更新总进度
            if self.upload_dir_jndex and self.upload_dir_file_count > 0:
                # 当前文件完成百分比
                file_progress = transferred / total if total > 0 else 0

                # 计算总进度：已完成文件数 + 当前文件进度
                total_progress = (self.upload_dir_current_file + file_progress) / self.upload_dir_file_count

                # 更新总进度
                if self.upload_dir_progress_callback:
                    self.upload_dir_progress_callback(total_progress)

                print(
                    f"文件进度: {file_progress * 100:.1f}%, 总进度: {total_progress * 100:.1f}%, 文件: {os.path.basename(local_path)}")

        try:
            # 确保远程目录存在
            remote_dir = os.path.dirname(remote_path)
            if remote_dir and not self.exists(remote_dir):
                self.md(remote_dir)

            self.sftp.put(local_path, remote_path, custom_callback)

            # 文件上传完成，增加已完成文件计数
            if self.upload_dir_jndex:
                self.upload_dir_current_file += 1
                # 更新总进度
                if self.upload_dir_progress_callback:
                    total_progress = self.upload_dir_current_file / self.upload_dir_file_count
                    self.upload_dir_progress_callback(total_progress)

            return True
        except Exception as e:
            print(f"上传文件 {local_path} 时出错: {e}")
            return False

    def disconnect(self):
        if hasattr(self, 'sftp'):
            self.sftp.close()
        if hasattr(self, 'ssh'):
            self.ssh.close()
        
    def is_dir(self, path):
        try:
            attr = self.sftp.stat(path)
            return stat.S_ISDIR(attr.st_mode)
        except IOError:
            return False

    def is_file(self, path):
        try:
            attr = self.sftp.stat(path)
            return stat.S_ISREG(attr.st_mode)
        except IOError:
            return False
        
    def exists(self, path):
        if self.is_dir(path=path) or self.is_file(path=path):
            return True
        else:
            return False
        
    def getfile_list(self):
        try:
            file_list = self.sftp.listdir('/')
            if file_list == self.file_lista:
                self.file_list.clear()
                for path in file_list:
                    if self.is_dir(path):
                        self.file_list.add(path, "dir")
                    elif self.is_file(path):
                        self.file_list.add(path, "file")
            self.file_lista = file_list
            return file_list
        except Exception as e:
            print(f"获取文件列表失败: {e}")
                
    def download_file(self, remote_path, local_path):
        try:
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            self.sftp.get(remote_path, local_path, self.progress_callback)
            print(f"已下载: {remote_path} -> {local_path}")
            self.jndex = False
            return True
        except FileNotFoundError:
            print(f"远程文件不存在: {remote_path}")
            return False
        except PermissionError:
            print(f"权限错误: 没有权限下载文件 {remote_path}")
            return False
        except Exception as e:
            print(f"下载文件时出错: {e}")
            return False
        
    def updata_file(self, fromfile, tofile):
        if not os.path.exists(fromfile):
            print("文件不存在")
            return False
            
        remote_dir = os.path.dirname(tofile)
        if remote_dir and not self.is_dir(remote_dir):
            self.md(remote_dir)
            
        try:
            self.sftp.put(fromfile, tofile, self.progress_callback)
            self.jndex = False
            return True
        except PermissionError:
            print(f"权限错误: 没有权限上传文件到 {tofile}")
            return False
        except Exception as e:
            print(f"上传文件时出错: {e}")
            return False
        
    def progress_callback(self, transferred, total):
        if total > 0:
            percent = 100 * transferred / total
            print(f"已传输: {transferred}/{total} 字节 ({percent:.2f}%)")
        else:
            print(f"已传输: {transferred} 字节 (总大小未知)")
        self.download = transferred
        self.total = total
        self.jndex = True
        
    def get_sskk(self):
        return self.download, self.total
        
    def md(self, path):
        try:
            if "." in path:
                print("路径中不能包含 '.'")
                return False
            self.sftp.mkdir(path)
            print(f"目录 '{path}' 创建成功")
            return True
        except PermissionError:
            print(f"权限错误: 没有权限在 {path} 创建目录")
            return False
        except IOError as e:
            print(f"创建目录 '{path}' 失败: {e}")
            return False
            
    def check_write_permission(self, path):
        """检查是否有写权限"""
        try:
            # 尝试创建一个临时文件来测试写权限
            test_file = f"{path}/.write_test_{int(time.time())}"
            self.sftp.open(test_file, 'w').close()
            self.sftp.remove(test_file)
            return True
        except (IOError, PermissionError):
            return False
            
    def check_read_permission(self, path):
        """检查是否有读权限"""
        try:
            # 尝试列出目录内容来测试读权限
            self.sftp.listdir(path)
            return True
        except (IOError, PermissionError):
            return False
            
    def count_files_in_directory(self, path):
        """计算目录中的文件数量"""
        file_count = 0
        try:
            items = self.sftp.listdir_attr(path)
            for item in items:
                remote_item_path = f"{path}/{item.filename}"
                if stat.S_ISDIR(item.st_mode):
                    file_count += self.count_files_in_directory(remote_item_path)
                else:
                    file_count += 1
        except Exception as e:
            print(f"计算目录文件数量时出错: {e}")
        return file_count
        
    def download_directory_with_progress(self, remote_path, local_path, progress_callback=None):
        """下载目录并显示总进度"""
        try:
            # 计算远程目录文件数量
            self.dir_file_count = self.count_files_in_directory(remote_path)
            self.dir_transferred = 0
            self.dir_current_file = 0
            self.dir_jndex = True
            self.dir_progress_callback = progress_callback
            
            print(f"开始下载目录: {remote_path}, 文件数量: {self.dir_file_count}")
            
            # 开始下载
            success = self._download_directory_recursive(remote_path, local_path)
            self.dir_jndex = False
            return success
        except Exception as e:
            print(f"下载目录时出错: {e}")
            self.dir_jndex = False
            return False

    def rename(self, oldpath:str, newpath):
        try:
            if "." in newpath or "." in oldpath:
                print("路径中不能包含 '.'")
                return False
            self.sftp.rename(oldpath, newpath)
            print(f"已重命名: {oldpath} -> {newpath}")
            return True
        except FileNotFoundError:
            print(f"文件不存在: {oldpath}")
            return False
        except PermissionError:
            print(f"权限错误: 没有权限重命名 {oldpath}")
            return False
        except Exception as e:
            print(f"重命名文件时出错: {e}")
            return False
            
    def move_file(self, source_path, target_path):
        """移动文件或目录到新位置"""
        try:
            # 检查源文件是否存在
            if not self.exists(source_path):
                print(f"源文件不存在: {source_path}")
                return False
                
            # 确保目标目录存在
            target_dir = os.path.dirname(target_path)
            if target_dir and not self.exists(target_dir):
                self._create_remote_directory_recursive(target_dir)
                
            # 使用 rename 方法移动文件
            self.sftp.rename(source_path, target_path)
            print(f"已移动: {source_path} -> {target_path}")
            return True
        except FileNotFoundError:
            print(f"源文件不存在: {source_path}")
            return False
        except PermissionError:
            print(f"权限错误: 没有权限移动文件 {source_path}")
            return False
        except IOError as e:
            print(f"移动文件时出错: {e}")
            return False
        except Exception as e:
            print(f"移动文件时发生未知错误: {e}")
            return False
            
    def _create_remote_directory_recursive(self, path):
        """递归创建远程目录"""
        if path == "" or path == "/":
            return True
            
        parent_dir = os.path.dirname(path)
        if parent_dir and parent_dir != "/" and not self.exists(parent_dir):
            self._create_remote_directory_recursive(parent_dir)
        
        if not self.exists(path):
            return self.md(path)
        return True
            
    def _download_directory_recursive(self, remote_path, local_path):
        """递归下载目录"""
        # 创建本地目录
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        
        # 获取远程目录内容
        items = self.sftp.listdir_attr(remote_path)
        
        for item in items:
            remote_item_path = f"{remote_path}/{item.filename}"
            local_item_path = os.path.join(local_path, item.filename)
            
            if stat.S_ISDIR(item.st_mode):
                # 递归下载子目录
                if not self._download_directory_recursive(remote_item_path, local_item_path):
                    return False
            else:
                # 下载文件
                if not self._download_file_with_progress(remote_item_path, local_item_path):
                    return False
                    
        return True
        
    def _download_file_with_progress(self, remote_path, local_path):
        """下载文件并更新总进度"""
        def custom_callback(transferred, total):
            # 更新当前文件进度
            self.download = transferred
            self.total = total
            self.jndex = True
            
            # 如果这是目录传输，更新总进度
            if self.dir_jndex and self.dir_file_count > 0:
                # 当前文件完成百分比
                file_progress = transferred / total if total > 0 else 0
                
                # 计算总进度：已完成文件数 + 当前文件进度
                total_progress = (self.dir_current_file + file_progress) / self.dir_file_count
                
                # 更新总进度
                if self.dir_progress_callback:
                    self.dir_progress_callback(total_progress)
                
                print(f"文件进度: {file_progress*100:.1f}%, 总进度: {total_progress*100:.1f}%, 文件: {os.path.basename(remote_path)}")
        
        try:
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
                
            self.sftp.get(remote_path, local_path, custom_callback)
            
            # 文件下载完成，增加已完成文件计数
            if self.dir_jndex:
                self.dir_current_file += 1
                # 更新总进度
                if self.dir_progress_callback:
                    total_progress = self.dir_current_file / self.dir_file_count
                    self.dir_progress_callback(total_progress)
            
            return True
        except Exception as e:
            print(f"下载文件 {remote_path} 时出错: {e}")
            return False

    def list_files_recursive(self, path="/", indent=0):
        try:
            files = self.sftp.listdir_attr(path)
            result = []
            
            for file_attr in files:
                if file_attr.filename in ['.', '.']:
                    continue
                    
                full_path = os.path.join(path, file_attr.filename).replace('\\', '/')
                
                result.append(('  ' * indent + file_attr.filename, 
                              '目录' if stat.S_ISDIR(file_attr.st_mode) else '文件',
                              file_attr.st_size,
                              self.format_permissions(file_attr.st_mode)))
                
                if stat.S_ISDIR(file_attr.st_mode):
                    result.extend(self.list_files_recursive(full_path, indent + 1))
                    
            return result
        except Exception as e:
            print(f"访问路径 {path} 时出错: {e}")
            return [('  ' * indent + f"错误: {e}", "错误", 0, "---------")]
    
    @staticmethod
    def format_permissions(mode):
        perms = ['r' if mode & stat.S_IRUSR else '-', 'w' if mode & stat.S_IWUSR else '-',
                 'x' if mode & stat.S_IXUSR else '-', 'r' if mode & stat.S_IRGRP else '-',
                 'w' if mode & stat.S_IWGRP else '-', 'x' if mode & stat.S_IXGRP else '-',
                 'r' if mode & stat.S_IROTH else '-', 'w' if mode & stat.S_IWOTH else '-',
                 'x' if mode & stat.S_IXOTH else '-']
        return ''.join(perms)

class KeyValueTable:
    def __init__(self):
        self.table = {}
    
    def add(self, key, value):
        self.table[key] = value
        print(f"已添加: {key} -> {value}")
    
    def get(self, key):
        if key in self.table:
            return self.table[key]
        else:
            return None
    
    def remove(self, key):
        if key in self.table:
            value = self.table.pop(key)
            print(f"已删除: {key} -> {value}")
        else:
            print(f"键 '{key}' 不存在")
    
    def display(self):
        if not self.table:
            print("键值表为空")
        else:
            print("键值表内容:")
            for key, value in self.table.items():
                print(f"  {key}: {value}")
    
    def keys(self):
        return list(self.table.keys())
    
    def is_file(self, key):
        a = self.get(key)
        if a == "file":
            return True
        else:
            return False

    def is_dir(self, key):
        a = self.get(key)
        if a == "dir":
            return True
        else:
            return False
    
    def exists(self, key):
        a = self.get(key)
        if a is None:
            return False
        else:
            return True
    
    def values(self):
        return list(self.table.values())
    
    def clear(self):
        self.table.clear()
        print("键值表已清空")


def format_size(size):
    if size == 0:
        return "0 B"
    sizes = ["B", "KB", "MB", "GB"]
    i = 0
    while size >= 1024 and i < len(sizes)-1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {sizes[i]}"


class ServerFileExplorer:
    def anana(self):
        file_list = self.net.sftp.listdir(self.current_path)
        while self.event.is_set():
            time.sleep(1)
            if not self.net.sftp.listdir(self.current_path) == file_list:
                self.refresh()
                file_list = self.net.sftp.listdir(self.current_path)

    def __init__(self, root: tk.Tk, net_instance: net, rootdir="/"):
        
        self.anan = None
        self.restore_button = None
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        try:
            a = os.path.dirname(os.path.dirname(__file__))
            b = a.replace('\\', '/')
            cddddd = b + "/other/network.ico"
            self.root.iconbitmap(cddddd)
        except:
            pass
        self.root.title("服务器文件浏览器")
        self.root.minsize(950, 700)
        self.root.geometry("950x700")
        self.server_stop = False
        self.net = net_instance
        self.rootdir = rootdir.rstrip('/')
        self.current_path = rootdir
        self.selected_item = None
        self.last_transfer_time = None
        self.dir_last_transfer_time = None
        
        # 初始化图像管理器
        self.image_manager = ImageManager(os.path.dirname(__file__))
        images_loaded = self.image_manager.load_all_images()
        if not images_loaded:
            print("警告: 无法加载图像文件，按钮将不显示图像")
        
        self.set_windows_style()
        self.set_treeview_style()
        self.set_button_style()
        self.set_progress_style()
        
        self.skip = ""
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 路径显示和导航
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        self.event = threading.Event()
        self.event.set()
        ttk.Label(path_frame, text="当前路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="/")
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side=tk.LEFT, padx=5)
        
        # 创建导航按钮（带图像）
        self.create_navigation_buttons(path_frame)
        
        # 操作按钮框架
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # 创建操作按钮（带图像）
        self.create_action_buttons()
        
        # 进度条框架
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="传输进度:", style="TLabel").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(side=tk.RIGHT)
        
        # 文件列表
        ttk.Label(main_frame, text="文件列表:").pack(anchor=tk.E, pady=(10, 5))
        
        # 创建树形视图
        columns = ("类型", "大小", "权限")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="tree headings")
        
        # 设置列属性
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("类型", width=100, minwidth=80)
        self.tree.column("大小", width=100, minwidth=80)
        self.tree.column("权限", width=100, minwidth=80)

        # 设置列标题
        self.tree.heading("#0", text="名称")
        self.tree.heading("类型", text="类型")
        self.tree.heading("大小", text="大小")
        self.tree.heading("权限", text="权限")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.FLAT, anchor=tk.W, style="TLabel")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_progress_thread()
        
        # 初始加载文件列表
        self.refresh()
        threading.Thread(target=self.anana,daemon=True).start()

    def create_navigation_buttons(self, path_frame):
        """创建带图像的导航按钮"""
        ttk.Button(path_frame, 
                  text="刷新", 
                  command=self.refresh, 
                  style="TButton",
                  image=self.image_manager.get_image('refresh'),
                  compound="left").pack(side=tk.LEFT, padx=2)
        
        ttk.Button(path_frame, 
                  text="上级目录", 
                  command=self.go_up, 
                  style="TButton",
                  image=self.image_manager.get_image('up'),
                  compound="left").pack(side=tk.LEFT, padx=2)
        
        ttk.Button(path_frame, 
                  text="根目录", 
                  command=self.go_root, 
                  style="TButton",
                  image=self.image_manager.get_image('home'),
                  compound="left").pack(side=tk.LEFT, padx=2)
        
        ttk.Button(path_frame, 
                  text="回收站", 
                  command=self.go_trash, 
                  style="TButton",
                  image=self.image_manager.get_image('trash'),
                  compound="left").pack(side=tk.LEFT, padx=2)

    def create_action_buttons(self):
        """创建带图像的操作按钮"""
        self.upload_button = ttk.Button(
            self.button_frame, 
            text="上传", 
            command=self.ifdo_upload, 
            style="TButton",
            image=self.image_manager.get_image('upload'),
            compound="left"
        )
        
        self.downloadbutton = ttk.Button(
            self.button_frame,
            text="下载", 
            command=self.download_file,
            style="TButton",
            image=self.image_manager.get_image('download'),
            compound="left"
        )
        
        self.newfolder_button = ttk.Button(
            self.button_frame,
            text="新建文件夹", 
            command=self.create_directory,
            style="TButton",
            image=self.image_manager.get_image('newfolder'),
            compound="left"
        )
        
        self.rename_button = ttk.Button(
            self.button_frame,
            text="重命名", 
            command=self.rename_item,
            style="TButton",
            image=self.image_manager.get_image('rename'),
            compound="left"
        )
        
        self.delete_button = ttk.Button(
            self.button_frame,
            text="删除", 
            command=self.delete_item,
            style="Danger.TButton",
            image=self.image_manager.get_image('delete'),
            compound="left"
        )
        
        # 打包按钮
        self.upload_button.pack(side=tk.LEFT, padx=2)
        self.downloadbutton.pack(side=tk.LEFT, padx=2)
        self.newfolder_button.pack(side=tk.LEFT, padx=2)
        self.rename_button.pack(side=tk.LEFT, padx=2)
        self.delete_button.pack(side=tk.LEFT, padx=2)

    def reset_button(self):
        """重置按钮布局到默认状态"""
        # 移除所有按钮
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()
        
        # 重新添加默认按钮
        self.upload_button.pack(side=tk.LEFT, padx=2)
        self.downloadbutton.pack(side=tk.LEFT, padx=2)
        self.newfolder_button.pack(side=tk.LEFT, padx=2)
        self.rename_button.pack(side=tk.LEFT, padx=2)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        
        # 恢复删除按钮文本
        self.delete_button.configure(text="删除")
        
        # 隐藏还原按钮
        if hasattr(self, 'restore_button') and self.restore_button:
            try:
                self.restore_button.pack_forget()
            except:
                pass

    def is_path_within_rootdir(self, path):
        """检查路径是否在rootdir范围内"""
        normalized_path = path.rstrip('/')
        normalized_rootdir = self.rootdir.rstrip('/')
        
        # 检查路径是否以rootdir开头
        return normalized_path.startswith(normalized_rootdir)
        
    def get_display_path(self, path):
        """获取用于显示的路径（相对于rootdir）"""
        if path == self.rootdir:
            return "/"
        else:
            # 移除rootdir前缀，并确保以/开头
            display_path = path.replace(self.rootdir, "", 1)
            if not display_path.startswith("/"):
                display_path = "/" + display_path
            return display_path
        
    def get_absolute_path(self, display_path):
        """将显示路径转换为绝对路径"""
        if display_path == "/":
            return self.rootdir
        else:
            return self.rootdir + display_path
        
    def check_write_permission(self, path):
        """检查当前目录是否有写权限"""
        if not self.net.check_write_permission(path):
            messagebox.showerror("权限错误", f"没有权限在 '{self.get_display_path(path)}' 目录中写入文件")
            return False
        return True

    def rename_item(self):
        """重命名选中的文件或文件夹"""
        if not self.selected_item:
            messagebox.showwarning("未选择", "请先选择一个文件或文件夹")
            return
        
        old_name = self.tree.item(self.selected_item, "text")
        old_path = f"{self.current_path}/{old_name}"
        
        # 让用户输入新名称
        new_name = simpledialog.askstring("重命名", "请输入新名称:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        
        new_path = f"{self.current_path}/{new_name}"
        
        # 检查写权限
        if not self.check_write_permission(self.current_path):
            return
        
        try:
            self.net.rename(old_path, new_path)
            self.refresh()
            self.status_var.set(f"已重命名 '{old_name}' 为 '{new_name}'")
        except Exception as e:
            messagebox.showerror("错误", f"无法重命名: {str(e)}")
            self.status_var.set("错误: " + str(e))
    
    def check_read_permission(self, path):
        """检查当前目录是否有读权限"""
        if not self.net.check_read_permission(path):
            messagebox.showerror("权限错误", f"没有权限读取 '{self.get_display_path(path)}' 目录中的文件")
            return False
        return True

    def refresh(self):
        self.tree.tag_configure('directory', background='#FFFFFF', foreground="#0400FF")
        self.tree.tag_configure('textfile', background='#FFFFFF', foreground="#000000")
        self.tree.tag_configure('codefile', background='#FFFFFF', foreground='#228b22')
        self.tree.tag_configure('imagefile', background='#FFFFFF', foreground="#8c00ff")
        self.tree.tag_configure('playfile', background='#FFFFFF', foreground="#AA0085")
        self.tree.tag_configure('otherfile', background='#FFFFFF', foreground='#666666')
        self.tree.tag_configure('zipfile', background='#FFFFFF', foreground="#FF0000")
        self.tree.tag_configure('nullfile', background="#FFFFFF", foreground="#FFFFFF")
        self.tree.tag_configure('lnk', background='#FFFFFF', foreground="#180070")
        self.tree.tag_configure('storefile', background='#FFFFFF', foreground="#FFE600")
        """刷新当前目录的文件列表"""
        # 确保当前路径在rootdir范围内
        if not self.is_path_within_rootdir(self.current_path):
            self.current_path = self.rootdir
            
        # 更新显示路径
        self.path_var.set(self.get_display_path(self.current_path))
            
        self.status_var.set("正在加载.")
        self.tree.delete(*self.tree.get_children())

        try:
            # 检查读权限
            if not self.check_read_permission(self.current_path):
                self.status_var.set("错误: 没有读取权限")
                return
                
            # 获取当前目录下的文件和文件夹
            files = self.net.sftp.listdir_attr(self.current_path)
            for a in files:
                name = a.filename
                if name == "stop.skip" and self.current_path == self.rootdir:
                    """这里不用管"""
                    self.server_stop = True
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('directory',))
                    self.server_stop = True
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('textfile',))
                    self.server_stop = True
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('codefile',))
                    self.server_stop = True
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('imagefile',))
                    self.server_stop = True
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('playfile',))
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('otherfile',))
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('zipfile',))
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('nullfile',))
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('lnk',))
                    item = self.tree.insert("", "end", text="服务被禁用", values=("","",""
                    ), tags=('storefile',))
                    
                    return
                else:
                    self.server_stop = False
                
            # 先添加文件夹
            for file_attr in files:
                mode = file_attr.st_mode
                
                if stat.S_ISDIR(file_attr.st_mode):
                    
                    name = file_attr.filename
                    if name == ".1.2.3.trash":
                        continue
                        
                    else:
                        item = self.tree.insert("", "end", text=name, values=(
                        "目录", format_size(file_attr.st_size),
                        self.format_permissions(file_attr.st_mode)
                        ), tags=('directory',))

            for file_attr in files:
                if stat.S_ISLNK(file_attr.st_mode):
                    name = file_attr.filename
                    print(name)
                    if not (stat.S_ISDIR(file_attr.st_mode) or stat.S_ISLNK(file_attr.st_mode)):
                        name = file_attr.filename
                        ext = os.path.splitext(name)[1].lower()
                        if ext in [".lnk"]:
                            tag = "lnk"
                    item = self.tree.insert("", "end", text=name, values=(
                        "符号链接", format_size(file_attr.st_size),
                        self.format_permissions(file_attr.st_mode)
                    ), tags=('lnk',))
            # 再添加文件
            for file_attr in files:
                if not (stat.S_ISDIR(file_attr.st_mode) or stat.S_ISLNK(file_attr.st_mode)):
                    name = file_attr.filename
                    ext = os.path.splitext(name)[1].lower()
                    if ext in ['.txt', '.md', '.log','.ini','.cfg','.conf','.json','.xml','.yaml','.yml','.csv']:
                        tag = 'textfile'
                    elif ext in ['.py', '.java', '.cpp', '.c', '.h', '.js', '.html', '.css', '.php', '.rb', '.go', '.rs', '.sh', '.bat', '.pl', '.swift', '.ts', '.jsx', '.tsx', '.java','.cs','.vb']:
                        tag = 'codefile'
                    elif ext in ['.jpg', '.png', '.gif', '.bmp', '.jpeg', '.tiff', '.svg', '.webp', '.ico', '.heic', '.jfif']:
                        tag = 'imagefile'
                    elif ext in [".zip", ".7z", ".rar",".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2", ".zipx", ".z", ".lz", ".lzma", ".lzo", ".cab", ".arj", ".ace", ".uue", ".xxe", ".jar", ".war", ".ear"]:
                        tag = "zipfile"
                    elif ext in [".iso",".img",".vhdx",".vhd",".vdi",".vhdk",".qcow2",".dmg",".nrg",".mdf",".mds",".cso",".isz",".bin",".cue",".toast",".xci",".xcz"]:
                        tag = "storefile"
                    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mpg", ".mpeg", ".3gp", ".webm", ".vob", ".ogv", ".m4v", ".rmvb", ".rm", ".ts", ".mts", ".m2ts", ".divx", ".xvid", ".f4v", ".asf", ".m2v", ".mpe", ".mpv", ".svi", ".viv", ".dv", ".dif", ".drc",".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".alac", ".aiff", ".pcm", ".aif", ".aifc", ".au", ".snd", ".mid", ".midi", ".rmi", ".kar", ".mp2", ".mka", ".ac3", ".dts", ".amr", ".ra", ".rm", ".opus"]:
                        tag = "playfile"
                    elif ext in [".thisfileisnull"]:
                        continue
                    elif ext in [".lnk"]:
                        tag = "lnk"
                    
                    else:
                        tag = 'otherfile'

                    self.tree.insert("", "end", text=name, values=(
                        "文件", format_size(file_attr.st_size),
                        self.format_permissions(file_attr.st_mode)
                    ), tags=(tag,))

            for file_attr in files:
                name = file_attr.filename
                ext = os.path.splitext(name)[1].lower()
                if ext in "" :
                    print(name)
                    self.tree.insert("", "end", text=name, values=(
                        "文件", format_size(file_attr.st_size),
                        self.format_permissions(file_attr.st_mode)
                    ), tags=("nullfile",))

            # 统一背景色方案
            print(self.tree.get_children())
            self.status_var.set(f"已加载 {len(files)} 个项目")
            print("sss")
        except Exception as e:
            messagebox.showerror("错误", f"无法读取目录: {str(e)}")
            traceback.print_exc()
            self.status_var.set("错误: " + str(e))

    def go_up(self):
        """返回上级目录，但不能超出rootdir范围，并检查是否需要恢复按钮布局"""
        if self.current_path != self.rootdir:
            parent_path = os.path.dirname(self.current_path)
            # 确保父级目录仍然在rootdir范围内
            if self.is_path_within_rootdir(parent_path):
                self.current_path = parent_path
                if self.current_path == "":
                    self.current_path = self.rootdir

                # 如果离开回收站，恢复按钮布局
                if not self.current_path.endswith("/.1.2.3.trash"):
                    self.go_root()  # 这会恢复按钮布局
                else:
                    self.refresh()
            else:
                # 如果父级目录超出范围，则保持在rootdir
                self.current_path = self.rootdir
                self.go_root()  # 这会恢复按钮布局

    def go_root(self):
        """返回根目录（配置的rootdir）并恢复按钮布局"""
        # 恢复按钮布局
        self.reset_button()
        
        # 隐藏还原按钮
        if hasattr(self, 'restore_button') and self.restore_button:
            try:
                self.restore_button.pack_forget()
            except:
                pass
        self.anan = False
        self.current_path = self.rootdir
        self.refresh()

    def go_trash(self):
        """进入回收站目录，如果不存在则创建，并调整按钮布局"""
        trash_path = self.rootdir + "/.1.2.3.trash"

        try:
            # 检查回收站目录是否存在
            if not self.net.exists(trash_path):
                # 如果不存在，询问用户是否创建
                if messagebox.askyesno("回收站不存在", "回收站目录不存在，是否创建？"):
                    if self.net.md(trash_path):
                        messagebox.showinfo("成功", "回收站目录创建成功！")
                    else:
                        messagebox.showerror("错误", "无法创建回收站目录，请检查权限")
                        return
                else:
                    return

            # 检查是否有读取回收站的权限
            if not self.net.check_read_permission(trash_path):
                messagebox.showerror("权限错误", "没有权限访问回收站目录")
                return

            # 切换到回收站目录
            self.current_path = trash_path

            # 隐藏常规操作按钮，显示还原按钮
            self.upload_button.pack_forget()
            self.downloadbutton.pack_forget()
            self.newfolder_button.pack_forget()
            self.rename_button.pack_forget()

            # 修改删除按钮为彻底删除
            self.delete_button.configure(text="彻底删除")

            # 添加还原按钮（如果尚未添加）
            if self.restore_button is None:
                self.restore_button = ttk.Button(
                    self.button_frame, 
                    text="还原", 
                    command=self.restore_item,
                    style="TButton",
                    image=self.image_manager.get_image('restore'),
                    compound="left"
                )
            
            # 显示还原按钮（确保只显示一次）
            if not self.anan:
                self.restore_button.pack(side=tk.LEFT, padx=2)
                self.anan = True

            self.refresh()
            self.status_var.set("已进入回收站 - 可选择文件进行还原")

        except Exception as e:
            messagebox.showerror("错误", f"访问回收站失败: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")

    def restore_item(self):
        """还原选中的项目"""
        if not self.selected_item:
            messagebox.showinfo("提示", "请先选择一个文件或目录进行还原")
            return

        name = self.tree.item(self.selected_item, "text")
        values = self.tree.item(self.selected_item, "values")
        
        if not values:
            return
            
        item_type = values[0]

        # 构建回收站中的完整路径
        trash_item_path = f"{self.current_path}/{name}"

        # 检查项目是否存在于回收站
        if not self.net.exists(trash_item_path):
            messagebox.showerror("错误", f"项目 '{name}' 在回收站中不存在")
            return

        # 让用户输入还原路径
        restore_path = simpledialog.askstring(
            "还原项目",
            f"请输入还原路径 (相对于根目录):",
            initialvalue=f"/{name}"
        )

        if not restore_path:
            return

        # 确保路径以/开头
        if not restore_path.startswith("/"):
            restore_path = f"/{restore_path}"

        # 构建完整路径
        full_restore_path = f"{self.rootdir}{restore_path}"
        
        # 检查目标路径是否已存在
        if self.net.exists(full_restore_path):
            if not messagebox.askyesno("确认覆盖", f"目标路径 '{restore_path}' 已存在，是否覆盖？"):
                return

        try:
            # 确保目标目录存在
            target_dir = os.path.dirname(full_restore_path)
            if target_dir and not self.net.exists(target_dir):
                if not messagebox.askyesno("创建目录", f"目标目录不存在，是否创建 '{os.path.dirname(restore_path)}'？"):
                    return
                # 递归创建目录
                self._create_remote_directory_recursive(target_dir)

            # 执行还原操作 - 使用 paramiko 的 rename 方法移动文件
            if self.net.rename(trash_item_path, full_restore_path):
                messagebox.showinfo("成功", f"项目已还原到: {restore_path}")
                self.status_var.set(f"已还原: {name} -> {restore_path}")
                self.refresh()
            else:
                messagebox.showerror("错误", "还原失败，请检查目标路径是否有权限")
        except Exception as e:
            messagebox.showerror("错误", f"还原失败: {str(e)}")
            self.status_var.set(f"还原失败: {str(e)}")

    def _create_remote_directory_recursive(self, path):
        """递归创建远程目录"""
        if path == self.rootdir or not path:
            return True
            
        parent_dir = os.path.dirname(path)
        if parent_dir and parent_dir != self.rootdir and not self.net.exists(parent_dir):
            self._create_remote_directory_recursive(parent_dir)
        
        if not self.net.exists(path):
            return self.net.md(path)
        return True

    def on_item_double_click(self, event):
        """处理双击事件"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        name = self.tree.item(item, "text")
        values = self.tree.item(item, "values")
        
        if not values:
            return
            
        item_type = values[0]
        
        if item_type == "目录":
            # 进入目录
            if self.current_path == "/":
                new_path = f"/{name}"
            else:
                new_path = f"{self.current_path}/{name}"
            
            # 确保新路径在rootdir范围内
            if self.is_path_within_rootdir(new_path):
                self.current_path = new_path
                self.refresh()
    
    def on_item_select(self, event):
        """处理选择事件"""
        selected_items = self.tree.selection()
        if selected_items:
            self.selected_item = selected_items[0]
        else:
            self.selected_item = None

    def ifdo_upload(self):
        if self.server_stop:
            messagebox.showerror('',"服务被禁用")
            return
        a = pymsgbox.confirm(title="upload", buttons=("上传文件", "上传目录"))
        if a == "上传文件":
            self.upload_file()
        else:
            self.upload_directory()

    def set_windows_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.configure(bg="#1E1EEB")
        style.configure("TFrame", background="#1E1EEB", relief="flat")
        style.configure("TLabel", background="#1E1EEB", foreground="#E1E114")

    @staticmethod
    def set_progress_style():
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Horizontal.TProgressbar",
                background="#FF5722",
                troughcolor="#424242",
                bordercolor="#616161",
                lightcolor="#ff8a65",
                darkcolor="#d84315",
                thickness=20)

    @staticmethod
    def set_button_style():
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                    background="#FF8000",
                    foreground="white",
                    font=('Arial', 10, 'bold'),
                    padding=(10, 5),
                    borderwidth=1,
                    relief="raised")
        style.map("TButton", background=[('active', "#45a049")], relief=[('pressed', 'sunken')])
        style.configure("Danger.TButton",
                    background="#f44336",
                    foreground="white",
                    font=('Arial', 10, 'bold'),
                    padding=(10, 5),
                    borderwidth=1,
                    relief="raised")
        style.map("Danger.TButton", background=[('active', "#d32f2f")], relief=[('pressed', 'sunken')])

    @staticmethod
    def set_treeview_style():
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#FFFFFF",
                        foreground="#333333",
                        rowheight=20,
                        fieldbackground="#FFFFFF",
                        borderwidth=1,
                        relief="flat")
        style.map("Treeview", background=[('selected', "#00ff0d")], foreground=[('selected', 'white')])
        style.configure("Treeview.Heading",
                    background="#e0e0e0",
                    foreground="#000000",
                    relief="flat",
                    padding=(10, 5),
                    font=('Arial', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', "#1EFF00")])
        style.configure("Treeview.Separator", background="#c0c0c0")

    def upload_file(self):
        """上传文件到服务器"""
        # 检查写权限
        if not self.check_write_permission(self.current_path):
            return
            
        if not self.selected_item:
            remote_dir = self.current_path
        else:
            name = self.tree.item(self.selected_item, "text")
            values = self.tree.item(self.selected_item, "values")
            if not values or values[0] != "目录":
                messagebox.showinfo("提示", "请选择一个目录进行上传")
                return
            if self.current_path == "/":
                remote_dir = f"/{name}"
            else:
                remote_dir = f"{self.current_path}/{name}"

        local_path = filedialog.askopenfilename(title="选择要上传的文件")
        if os.path.basename(local_path) == "stop.skip":
            messagebox.showerror('',"不能上传stop.skip文件")
            return
        
        if not local_path:
            return

        remote_filename = os.path.basename(local_path)
        if remote_dir == "/":
            remote_path = f"/{remote_filename}"
        else:
            remote_path = f"{remote_dir}/{remote_filename}"

        threading.Thread(target=self.do_upload, args=(local_path, remote_path), daemon=True).start()

    def do_upload(self, local_path, remote_path):
        try:
            self.status_var.set("正在上传文件.")
            success = self.net.updata_file(local_path, remote_path)
            if success:
                self.status_var.set("文件上传完成")
                self.last_transfer_time = datetime.now()
                self.root.after(100, self.refresh)
            else:
                self.status_var.set("文件上传失败")
                messagebox.showerror("错误", "文件上传失败，请检查权限")
        except Exception as e:
            self.status_var.set(f"上传失败: {str(e)}")
            messagebox.showerror("错误", f"上传文件失败: {str(e)}")

    def download_file(self):
        if self.server_stop:
            messagebox.showerror('',"服务被禁用")
            return
        if not self.selected_item:
            messagebox.showinfo("提示", "请先选择一个文件或目录")
            return
            
        name = self.tree.item(self.selected_item, "text")
        values = self.tree.item(self.selected_item, "values")
        
        if not values:
            return
            
        item_type = values[0]
        
        # 检查读权限
        if not self.check_read_permission(self.current_path):
            return
            
        aaaaa = pymsgbox.confirm("下载至", "下载", ["下载至download", "下载至video", "下载至music", "下载到其他位置"])
        if aaaaa == "下载至download":
            original_string = str(os.path.dirname(os.path.dirname(__file__)))
            new_string = original_string.replace('\\', '/')
            sb = new_string + "/download"
            if not os.path.exists(sb):
                os.makedirs(sb)
            local_path = sb + "/" + name
        elif aaaaa == "下载至video":
            original_string = str(os.path.dirname(os.path.dirname(__file__)))
            new_string = original_string.replace('\\', '/')
            sb = new_string + "/video"
            if not os.path.exists(sb):
                os.makedirs(sb)
            local_path = sb + "/" + name
        elif aaaaa == "下载至music":
            original_string = str(os.path.dirname(os.path.dirname(__file__)))
            new_string = original_string.replace('\\', '/')
            sb = new_string + "/music"
            if not os.path.exists(sb):
                os.makedirs(sb)
            local_path = sb + "/" + name
        elif aaaaa == "下载到其他位置":
            if item_type == "目录":
                local_path = filedialog.askdirectory(title="选择保存目录")
                if not local_path:
                    return
                local_path = os.path.join(local_path, name)
            else:
                local_path = filedialog.asksaveasfilename(
                    title="保存文件", 
                    initialfile=name,
                    defaultextension=""
                )
                if not local_path:
                    return
        else:
            original_string = str(os.path.dirname(os.path.dirname(__file__)))
            new_string = original_string.replace('\\', '/')
            sb = new_string + "/download"
            if not os.path.exists(sb):
                os.makedirs(sb)
            local_path = sb + "/" + name
        
        if self.current_path == "/":
            remote_path = f"/{name}"
        else:
            remote_path = f"{self.current_path}/{name}"
            
        if item_type == "目录":
            threading.Thread(target=self.do_download_dir, args=(remote_path, local_path), daemon=True).start()
        else:
            threading.Thread(target=self.do_download_file, args=(remote_path, local_path), daemon=True).start()

    def do_download_file(self, remote_path, local_path):
        try:
            self.status_var.set("正在下载文件.")
            success = self.net.download_file(remote_path, local_path)
            if success:
                self.status_var.set("文件下载完成")
                self.last_transfer_time = datetime.now()
            else:
                self.status_var.set("文件下载失败")
                messagebox.showerror("错误", "文件下载失败，请检查权限")
        except Exception as e:
            self.status_var.set(f"下载失败: {str(e)}")
            messagebox.showerror("错误", f"下载文件失败: {str(e)}")

    def do_download_dir(self, remote_path, local_path):
        """执行目录下载操作"""
        try:
            self.status_var.set("正在计算目录文件数量.")
            
            # 使用新的目录下载方法
            def progress_callback(progress):
                # 更新进度条
                percent = progress * 100
                self.progress_var.set(percent)
                self.progress_label.config(text=f"{percent:.1f}%")
                self.status_var.set(f"正在下载目录. {percent:.1f}%")
                # 强制更新界面
                self.root.update_idletasks()
                
            success = self.net.download_directory_with_progress(remote_path, local_path, progress_callback)
            
            if success:
                self.status_var.set("目录下载完成")
                self.dir_last_transfer_time = datetime.now()
                # 确保进度条显示100%
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
            else:
                self.status_var.set("目录下载失败")
                messagebox.showerror("错误", "目录下载失败，请检查权限")
        except Exception as e:
            self.status_var.set(f"下载失败: {str(e)}")
            messagebox.showerror("错误", f"下载目录失败: {str(e)}")

    def create_directory(self):
        if self.server_stop:
            messagebox.showerror('',"服务被禁用")
            return
        """创建新目录"""
        # 检查写权限
        if not self.check_write_permission(self.current_path):
            return
            
        if not self.selected_item:
            base_remote_path = self.current_path
            default_name = "新文件夹"
        else:
            name = self.tree.item(self.selected_item, "text")
            values = self.tree.item(self.selected_item, "values")
            if not values or values[0] != "目录":
                messagebox.showinfo("提示", "请选择一个目录来创建子目录")
                return
            if self.current_path == "/":
                base_remote_path = f"/{name}"
            else:
                base_remote_path = f"{self.current_path}/{name}"
            default_name = "新文件夹"
        
        # 生成唯一的目录名
        dir_name = default_name
        counter = 1
        while self.net.exists(f"{base_remote_path}/{dir_name}"):
            dir_name = f"{default_name}{counter}"
            counter += 1
        
        # 让用户输入目录名
        user_input = simpledialog.askstring("新建目录", "请输入目录名称:", initialvalue=dir_name)
        if user_input == "stop.skip":
            messagebox.showerror('',"不能创建stop.skip目录")
            return
        elif user_input == "赛博灯泡":
            messagebox.showinfo('',"兄弟们,今天吃个赛博灯泡")
            user_input = "stop.skip"
            
        if not user_input:
            return
        
        # 构建完整的远程路径
        remote_path = f"{base_remote_path}/{user_input}"
        
        try:
            success = self.net.md(remote_path)
            if success:
                self.status_var.set(f"目录 '{user_input}' 创建成功")
                self.root.after(100, self.refresh)
            else:
                self.status_var.set(f"创建目录失败")
                messagebox.showerror("错误", "创建目录失败，请检查权限")
        except Exception as e:
            self.status_var.set(f"创建目录失败: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("错误", f"创建目录失败: {str(e)}")

    def delete_item(self):
        if self.server_stop:
            messagebox.showerror('',"服务被禁用")
            return
        if not self.selected_item:
            messagebox.showinfo("提示", "请先选择一个文件或目录")
            return
            
        name = self.tree.item(self.selected_item, "text")
        values = self.tree.item(self.selected_item, "values")
        if name == "":
            name = self.skip
        if values == ("","",""):
            values = ("文件","","")
            

        if not values:
            return
            
        item_type = values[0]
        
        # 构建完整路径
        if self.current_path == "/":
            remote_path = f"/{name}"
        else:
            remote_path = f"{self.current_path}/{name}"
            
        # 检查当前是否在回收站
        if self.current_path.endswith("/.1.2.3.trash"):
            # 在回收站中，执行彻底删除
            if not messagebox.askyesno("确认彻底删除", f"确定要彻底删除 {name} 吗？此操作不可恢复！"):
                return
                
            try:
                if item_type == "目录":
                    self._delete_directory_permanently(remote_path)
                else:
                    self.net.sftp.remove(remote_path)
                    
                self.status_var.set(f"{name} 已彻底删除")
                self.root.after(100, self.refresh)
            except Exception as e:
                self.status_var.set(f"彻底删除失败: {str(e)}")
                messagebox.showerror("错误", f"彻底删除失败: {str(e)}")
        else:
            # 不在回收站，移动到回收站
            if not messagebox.askyesno("确认删除", f"确定要删除 {name} 吗？文件将移动到回收站。"):
                return
                
            # 构建回收站路径
            trash_path = f"{self.rootdir}/.1.2.3.trash"
            
            # 检查回收站是否存在，如果不存在则创建
            if not self.net.exists(trash_path):
                if not self.net.md(trash_path):
                    messagebox.showerror("错误", "无法创建回收站目录，请检查权限")
                    return
            
            # 构建目标路径（在回收站中）
            target_path = f"{trash_path}/{name}"
            
            # 处理重名文件
            counter = 1
            original_target = target_path
            while self.net.exists(target_path):
                # 如果文件已存在，添加序号
                base_name = name
                if '.' in base_name:
                    name_part, ext_part = base_name.rsplit('.', 1)
                    target_path = f"{trash_path}/{name_part}_{counter}.{ext_part}"
                else:
                    target_path = f"{trash_path}/{base_name}_{counter}"
                counter += 1
            
            try:
                # 使用移动操作将文件移动到回收站
                if self.net.move_file(remote_path, target_path):
                    self.status_var.set(f"已移动到回收站: {name}")
                    self.root.after(100, self.refresh)
                else:
                    messagebox.showerror("错误", "移动到回收站失败")
            except Exception as e:
                self.status_var.set(f"删除失败: {str(e)}")
                messagebox.showerror("错误", f"删除失败: {str(e)}")

    def _delete_directory_permanently(self, remote_path):
        """彻底删除目录（递归删除）"""
        try:
            items = self.net.sftp.listdir(remote_path)
            
            for item in items:
                item_path = f"{remote_path}/{item}"
                item_attr = self.net.sftp.stat(item_path)
                
                if stat.S_ISDIR(item_attr.st_mode):
                    self._delete_directory_permanently(item_path)
                else:
                    self.net.sftp.remove(item_path)
            
            self.net.sftp.rmdir(remote_path)
            return True
        except Exception as e:
            print(f"彻底删除目录时出错: {e}")
            return False

    def update_progress_thread(self):
        def update():
            while True:
                try:
                    # 检查文件传输进度
                    transferred, total = self.net.get_sskk()

                    # 检查是否有传输完成且已经过了10秒
                    if self.last_transfer_time and (datetime.now() - self.last_transfer_time).seconds >= 10:
                        self.progress_var.set(0)
                        self.progress_label.config(text="0%")
                        # 重置net实例中的传输状态
                        self.net.download = 0
                        self.net.total = 0
                        self.last_transfer_time = None
                    elif total > 0:
                        percent = 100 * transferred / total
                        self.progress_var.set(percent)
                        self.progress_label.config(text=f"{percent:.1f}%")
                    else:
                        # 检查目录传输进度（下载和上传）
                        if self.net.dir_jndex or self.net.upload_dir_jndex:
                            # 目录传输中，显示目录传输进度
                            # 进度已经在回调函数中更新，这里不需要额外处理
                            pass
                        elif self.dir_last_transfer_time and (
                                datetime.now() - self.dir_last_transfer_time).seconds >= 10:
                            # 目录传输完成且已经过了10秒
                            self.progress_var.set(0)
                            self.progress_label.config(text="0%")
                            self.net.dir_transferred = 0
                            self.net.dir_total = 0
                            self.net.upload_dir_transferred = 0
                            self.net.upload_dir_total = 0
                            self.dir_last_transfer_time = None
                        else:
                            self.progress_var.set(0)
                            self.progress_label.config(text="0%")
                except:
                    pass
                time.sleep(0.1)

        thread = threading.Thread(target=update, daemon=True)
        thread.start()

    @staticmethod
    def format_permissions(mode):
        perms = ['r' if mode & stat.S_IRUSR else '-', 'w' if mode & stat.S_IWUSR else '-',
                 'x' if mode & stat.S_IXUSR else '-', 'r' if mode & stat.S_IRGRP else '-',
                 'w' if mode & stat.S_IWGRP else '-', 'x' if mode & stat.S_IXGRP else '-',
                 'r' if mode & stat.S_IROTH else '-', 'w' if mode & stat.S_IWOTH else '-',
                 'x' if mode & stat.S_IXOTH else '-']
        return ''.join(perms)
        
    def on_closing(self):
        """修复关闭方法，确保所有线程正确退出"""
        # 设置停止标志
        self.server_stop = True

        # 清除事件，让anana线程退出
        if hasattr(self, 'event'):
            self.event.clear()

                # 检查是否有传输任务
        if hasattr(self, 'net') and self.net and (self.net.jndex or self.net.dir_jndex or self.net.upload_dir_jndex):
            response = messagebox.askyesnocancel(
                "传输进行中", 
                    "当前有文件正在传输中。\n是否等待传输完成？\n(选择'否'将中断传输并退出)"
        )

            if response is None:
                return
            elif response:
                self.status_var.set("等待传输完成.")
                # 设置超时机制，避免无限等待
                start_time = time.time()
                while (self.net.jndex or self.net.dir_jndex or self.net.upload_dir_jndex) and (time.time() - start_time < 30):
                    self.root.update()
                    time.sleep(0.1)
    
        if messagebox.askokcancel("退出", "确定要退出应用程序吗？"):
            try:
                if hasattr(self, 'net') and self.net:
                    self.net.disconnect()
                    print("SSH连接已关闭")
            except Exception as e:
                print(f"关闭连接时出错: {e}")
            finally:
                # 确保完全退出
                self.root.quit()
                self.root.destroy()
                os._exit(0)  # 强制退出，确保所有线程终止

    def upload_directory(self):
        if not self.selected_item:
            remote_dir = self.current_path
        else:
            name = self.tree.item(self.selected_item, "text")
            values = self.tree.item(self.selected_item, "values")
            if not values or values[0] != "目录":
                messagebox.showinfo("提示", "请选择一个目录进行上传")
                return
            if self.current_path == "/":
                remote_dir = f"/{name}"
            else:
                remote_dir = f"{self.current_path}/{name}"

        local_path = filedialog.askdirectory(title="选择要上传的目录")
        if os.path.basename(local_path) == "stop.skip":
            messagebox.showerror('',"不能上传stop.skip目录")
            return
        if not local_path:
            return

        dir_name = os.path.basename(local_path)
        if remote_dir == "/":
            remote_path = f"/{dir_name}"
        else:
            remote_path = f"{remote_dir}/{dir_name}"

        threading.Thread(target=self.do_upload_directory, args=(local_path, remote_path), daemon=True).start()

    def do_upload_directory(self, local_path, remote_path):
        """执行目录上传操作"""
        try:
            self.status_var.set("正在计算目录文件数量.")

            # 使用新的目录上传方法
            def progress_callback(progress):
                # 更新进度条
                percent = progress * 100
                self.progress_var.set(percent)
                self.progress_label.config(text=f"{percent:.1f}%")
                self.status_var.set(f"正在上传目录.{percent:.1f}%")
                # 强制更新界面
                self.root.update_idletasks()

            success = self.net.upload_directory_with_progress(local_path, remote_path, progress_callback)

            if success:
                self.status_var.set("目录上传完成")
                self.dir_last_transfer_time = datetime.now()
                # 确保进度条显示100%
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
            else:
                self.status_var.set("目录上传失败")
                messagebox.showerror("错误", "目录上传失败，请检查权限")
        except Exception as e:
            self.status_var.set(f"上传失败: {str(e)}")
            messagebox.showerror("错误", f"上传目录失败: {str(e)}")

    def upload_directory_recursive(self, local_path, remote_path):
        try:
            if not self.net.exists(remote_path):
                self.net.md(remote_path)

            for item in os.listdir(local_path):
                local_item_path = os.path.join(local_path, item)
                remote_item_path = f"{remote_path}/{item}"

                if os.path.isdir(local_item_path):
                    self.upload_directory_recursive(local_item_path, remote_item_path)
                else:
                    self.net.updata_file(local_item_path, remote_item_path)

            return True
        except Exception as e:
            print(f"上传目录时出错: {e}")
            return False

def main(ip="127.0.0.1", port=22, username="", password="", rootdir="/"):
    root = tk.Tk()
    root.configure(bg="#000000")
    try:
        net_instance = net(ip, port, username, password)
        explorer = ServerFileExplorer(root, net_instance, rootdir)
        root.mainloop()
        net_instance.disconnect()
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("连接错误", f"无法连接到服务器: {str(e)}")

if __name__ == "__main__":
    a = os.path.dirname(__file__)
    a = ini(a=a)
    b = a.get("ip")
    if b is None:
        b = "127.0.0.1"
    c = a.getint("port")
    if c is None:
        c = 22
    d = a.get("username")
    if d is None:
        d = "ftp"
    kl = a.get("password")
    if kl is None:
        kl = "1234"
    kla = a.get("rootdir")
    if kla is None:
        kla = "/"
    main(ip=b, port=c, username=d, password=kl, rootdir=kla)