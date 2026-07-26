a = True

if a:
    import os

    try:
        try:
            import pymsgbox
        except ImportError as e:
            print(f"缺少依赖 pymsgbox，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install pymsgbox")
            import pymsgbox
        try:
            import pygame
        except ImportError as e:
            print(f"缺少依赖 pygame，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install pygame")
            import pygame
        try:
            from mutagen.id3 import ID3, APIC
            from mutagen import File
            from mutagen.flac import FLAC
            from mutagen.mp3 import MP3
            from mutagen.oggvorbis import OggVorbis
            from mutagen.wave import WAVE
        except ImportError as e:
            print(f"缺少依赖 mutagen，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install mutagen")
            import mutagen
        try:
            import pyperclip
        except ImportError as e:
            print(f"缺少依赖 pyperclip，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install pyperclip")
            import pyperclip
        try:
            from bilibili_api import video
        except ImportError as e:
            print(f"缺少依赖 bilibili-api，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install bilibili-api")
            from bilibili_api import video
        try:
            os.environ['PYTHON_VLC_MODULE_PATH'] = f"./pvlc"
            import vlc
        except ImportError as e:
            print(f"缺少依赖 python-vlc，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install python-vlc")
            import vlc
        a = os.system("you-get")
        if a != 0:
            print(f"缺少依赖 you-get，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install you-get")
            a = os.system("you-get")
            if a != 0:
                print("无法安装 you-get，请手动安装后重试")
                exit(1)
        try:
            import aiohttp
        except ImportError as e:
            print(f"缺少依赖 aiohttp，正在安装..")
            os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
            os.system("pip install aiohttp")
            import aiohttp
    except Exception as e:
        print(f"初始化依赖时出错: {str(e)},重试中")
        import traceback

        traceback.print_exc()
        os.system("pip install --upgrade setuptools wheel")
        os.system("python -m  pip install pymsgbox pygame mutagen pyperclip bilibili-api python-vlc aiohttp")

        a = open("restart.bat", "w")
        a.write(f"""taskkill /f /im python.exe
    pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
    python -m  pip install pymsgbox pygame mutagen pyperclip bilibili-api python-vlc aiohttp
    python {__file__}""")
        a.flush()
        a.close()
        os.system("start restart.bat")
        import sys

        sys.exit()
    import glob

    import sys
    import time
    import shutil
    import hashlib
    import mimetypes
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import simpledialog as sdialog
    from tkinter import messagebox
    import threading
    import asyncio
    import subprocess
    import re

    import traceback
    from multiprocessing import *
    


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
    
    

                
    
class MusicPlayer:

        

        
    def fl(self):
        for a in self.videoplaylist:
            a = str(a)
            xxxx = os.path.basename(a).replace(".mp4","")
            temp_list = a.split("\\")
            list_alla = len(temp_list) -2
            if temp_list[list_alla] != (xxxx):
                try:
                    os.makedirs(f"video\\{xxxx}")
                    shutil.copy(f"{a}",f"video\\{xxxx}\\{xxxx}.mp4")
                    aaa = a.replace(".mp4",".ass")
                    if os.path.isfile(aaa):
                        shutil.copy(f"{aaa}",f"video\\{xxxx}\\{aaa}")
                        os.remove(a)
                        os.remove(aaa)
                    else:
                        os.remove(a)
                except Exception as ccv:
                    messagebox.showerror(title="错误", message=f"无法移动视频文件: {str(ccv)}")

        self.find_video_files()

    def log_message(self, message, title="提示"):
        """线程安全的日志消息显示"""
        def show_message():
            try:
                messagebox.showinfo(title=title, message=message)
            except Exception as e:
                print(f"无法显示消息框: {str(e)}")

        # 在主线程执行UI操作
        if threading.current_thread().name == 'MainThread':
            show_message()
        else:
            self.root.after(0, show_message)
        

    
                
        
    def draw_progress_bar(self,percent, downloaded, total, unit,speed,speed_unit):
        self.percent = float(percent)
        self.speedd = speed + speed_unit
        if int(float(total)) >= 1024:
            self.sdsd = f"{float(total)/1024:.2f}GB"
        else:
            self.sdsd = f"{total}{unit}"
        if int(float(downloaded)) >= 1024:
            self.downloaded = f"{float(downloaded)/1024:.2f}GB"
        else:
            self.downloaded =  f"{downloaded}{unit}"
        
        self.aaaa = True
       
        
    def bilibilidownload(self,cmd_string,aa=0,cookies=True):
        self.percent = 0.0
        try:
        
            
            if os.path.exists("./video/cache"):
                shutil.rmtree("./video/cache", ignore_errors=True)
            os.makedirs("./video/cache", exist_ok=True)
        
            if "bilibili.com" in cmd_string:
                
                bvid = re.search(r'BV[a-zA-Z0-9]{10}', cmd_string)
                if bvid:
                    bvid = bvid.group(0)
                else:
            
                    parts = cmd_string.split("/")
                    bvid = parts[-1] if parts[-1].startswith("BV") else parts[-2]
            else:   
                    
                bvid = cmd_string

            print(f"正在下载视频: {bvid}") 

    
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            v = video.Video(bvid=bvid)
            videoset = loop.run_until_complete(v.get_info())
            print(f"视频标题: {videoset['title']}")

            
            safe_title = re.sub(r'[\\/*?:"<>|]', "", videoset['title'])
            safe_title = safe_title.replace(" ", "_")
            if cookies:
                command = [
                    "you-get",
                    "-o", "video\\cache",
                    "-c", f"{str('.')}\\other\\cookies.sqlite",
                    "-O", safe_title,
                    "--debug",
                    f"https://www.bilibili.com/video/{bvid}"
                ]
            else:
                command = [
                    "you-get",
                    "-o", "video\\cache",
                    "-O", safe_title,
                    "--debug",
                    f"https://www.bilibili.com/video/{bvid}"
                ]

            print(f"执行命令: {' '.join(command)}")

        
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='replace',
                universal_newlines=True
            )
            self.aaaa = True
        
    
            pattern = r"""
            (\d+\.\d+)%                # 百分比：99.0%
            \s+                         # 空白分隔
            \(                          # 左括号
            \s*                         # 可能有的空格
            (\d+\.\d+)                  # 已下载大小：174.7
            \s*                         # 可能有的空格
            /                           # 斜杠分隔
            \s*                         # 可能有的空格
            (\d+\.\d+)                  # 总大小：176.5
            (\w{2})                     # 大小单位：MB
            \)                          # 右括号
            .*?                         # 进度条部分（跳过）
            (\d+(?:\.\d+)?)             # 下载速度数值（整数或小数）
            \s*                         # 允许空格（0个或多个）
            (\w+/\w+)                   # 下载速度单位：MB/s
        """
            compiled_pattern = re.compile(pattern, re.VERBOSE)
            try:
                while True:
                    output = process.stdout.readline()
                    if not output and process.poll() is not None:
                        break
                
                    
                    match = compiled_pattern.search(output)
                    if match:
                        percentage = match.group(1)         # 99.0
                        downloaded_size = match.group(2)    # 174.7
                        total_size = match.group(3)         # 176.5
                        size_unit = match.group(4)          # MB
                        speed_value = match.group(5)        # 6
                        speed_unit = match.group(6)  
                        self.draw_progress_bar(float(percentage), downloaded_size, total_size, size_unit,speed_value,speed_unit)
                    
                    print(output.strip(),end="\n")

                    
                    if not self.asddd: 
                        process.terminate()
                        print("\n下载被用户中断")
                        self.out == "下载被用户中断"
                        self.asddd = True
                        return

                
                print("\n下载完成！")
                self.out == "\n下载完成！"

            except KeyboardInterrupt:
                print("\n用户中断下载")
                self.out = "\n用户中断下载"
                process.terminate()
                self.aaaa = False
                if os.path.exists("./video/cache"):
                    shutil.rmtree("./video/cache", ignore_errors=True)
                return
            
        
            downloaded_files = glob.glob("video\\cache\\*.mp4")
            if downloaded_files:
               
                main_video = max(downloaded_files, key=os.path.getsize)
            
          
                os.makedirs(f"video\\{safe_title}")
                dest_path = f"video\\{safe_title}\\{safe_title}.mp4"
                shutil.copy(main_video, dest_path)

             
                self.videoplaylist.append(dest_path.replace("\\", "/"))
                print(f"视频已保存到: {dest_path}")
                xml_files = glob.glob("video\\cache\\*.xml")
                if xml_files:
                    print("尝试转换字幕..")
                    try:
                        xml_path = xml_files[0]
                        ass_path = dest_path.replace(".mp4", ".ass")
                    
                        a = subprocess.run(f"python.exe {str('.')}\\other\\main.pyw -o {ass_path} +l {str(aa)} \"{xml_path}\"")
                        if a.returncode == 0:
                            print(f"字幕已转换: {ass_path}")
                        else:self.out = ("执行错误")
                        
                    except Exception as e:
                        print(f"字幕转换失败: {str(e)}")
                        self.out = f"字幕转换失败: {str(e)}"
                else:
                    print("警告: 未找到下载的视频文件")
                    self.out = "警告: 未找到下载的视频文件"
                
        except Exception as e:
            print(f"下载过程中发生错误: {str(e)}")
            self.out = f"无法下载视频: {str(e)}"
            import traceback
            traceback.print_exc()
        

        finally:
            if os.path.exists("./video/cache"):
                shutil.rmtree("./video/cache", ignore_errors=True)
            self.percent = float(0)
            self.sdsd = ""
            self.downloaded =  ""
            self.aaaa =False
            self.alogstop = True
            loop.close()
            print("缓存已清理")


    def speed(self):
        try:
            if not self.video_playing or not self.video_player:
                    self.show_temp_message("没有正在播放的视频", 1500)
                    return

            options = [
                {'speed': 0.5, 'label': '0.5x (慢速)'},
                    {'speed': 1.0, 'label': '1.0x (正常)'},
                {'speed': 2.0, 'label': '2.0x (快速)'},
                {'speed': 3.0, 'label': '3.0x (高速)'},
                {'speed': 4.0, 'label': '4.0x (极速)'}
            ]   

            width, height = 300, 250
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill((40, 40, 70, 230))
            pygame.draw.rect(surface, (80, 80, 150), (0, 0, width, height), 3)

            title_font = pygame.font.Font(f"{str('.')}\\fonts\\simhei.ttf", 28)
            title = title_font.render("选择播放速度", True, (255, 255, 0))
            surface.blit(title, (width//2 - title.get_width()//2, 20))

            option_rects = []
            for i, option in enumerate(options):
                y_pos = 60 + i * 35
                rect = pygame.Rect(50, y_pos, width - 100, 30)
                pygame.draw.rect(surface, (60, 60, 100), rect)
            
                if abs(option['speed'] - self.current_speed) < 0.1:
                    pygame.draw.rect(surface, (90, 90, 150), rect, 3)
            
                text = title_font.render(option['label'], True, 
                                        (255, 200, 100) if abs(option['speed'] - self.current_speed) < 0.1 
                                        else (220, 220, 220))
                surface.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
                option_rects.append((option['speed'], rect))
        
            screen_rect = pygame.Rect(
                self.width//2 - width//2, 
                self.height//2 - height//2,
                width, height
            )
            self.window.blit(surface, screen_rect)
            pygame.display.flip()
        
            selecting = True
            while selecting:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        local_pos = (mouse_pos[0] - screen_rect.x, mouse_pos[1] - screen_rect.y)

                        for speed, rect in option_rects:
                            if rect.collidepoint(local_pos):
                                if self.set_video_speed(speed):
                                    self.show_temp_message(f"速度已设为: {speed}x")
                                selecting = False
                                break
                    
                        if selecting:
                            selecting = False

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            selecting = False
                    
                        elif event.key in (pygame.K_1, pygame.K_KP1) and len(options) > 0:
                            if self.set_video_speed(options[0]['speed']):
                                self.show_temp_message(f"速度已设为: {options[0]['speed']}x")
                            selecting = False
            
            pygame.time.delay(50)
            
        except Exception as e:
            self.log_message(f"设置速度时出错: {e}")
            import traceback
            traceback.print_exc()
    def set_video_speed(self, speed):
        with self.vlc_lock:
            if self.video_player and self.video_playing:
                try:
                    self.video_player.set_rate(speed)
                    self.current_speed = speed
                    return True
                except Exception as e:
                    self.log_message(f"设置倍速失败: {e}")
                    return False
        return False
    def show_temp_message(self, message, duration=2000):
        self.temp_message = message
        self.temp_message_time = pygame.time.get_ticks() + duration
            
    def list_tuple_range(self,v, s, sn, e, en):
        s = not s if sn < 0 else s
        e = not e if en < 0 else e
        sn = abs(sn); en = abs(en)
        if sn >= len(v) or en >= len(v):
            if type(v) == list:return []
        else: return ()
        if not s: sn = len(v) - sn - 1
        if not e: en = len(v) - en - 1
        if en <= sn: return v[en:sn+1]
        else: return v[sn:en+1]

    PLAY_MODE_NORMAL = 0
    PLAY_MODE_REPEAT_ONE = 1
    PLAY_MODE_REPEAT_ALL = 2
    def resource_path(self,relative_path):
            global base_path,a
            a = 0
            
            return os.path.join(str("."), relative_path)
    def __init__(self,asa=True):
        self.cmd_input_active = False
        self.running = True
        self.speedd = ""
        aaaaaaaaaaaaaaaaaa = os.path.abspath(__file__)
        self.aaa = os.path.dirname(aaaaaaaaaaaaaaaaaa) 
        self.ssl_context = None
        self.next_img = None
        self.next_img = None
        self.next_img = None
        self.prev_img = None
        self.resource_dir = self.resource_path("")
        self.root = tk.Tk()
        self.root.withdraw()
        self.logout = ""
        self.vlc_lock = threading.Lock()
        self.lock = threading.Lock()
        self.percent = 0.0
        self.sdsd = ""
        self.downloaded =  ""
        self.out = ""
        self.aaaa = False
        self.playlist = []
        self.videoplaylist = []
        self.current_track = -1
        self.track_start_time = 0
        self.track_duration = 0
        self.current_position = 0
        self.paused = False
        self.paused_time = 0
        self.cover_cache = {}
        self.current_mode = self.PLAY_MODE_NORMAL
        self.button_size = 80
        self.width, self.height = 1000, 600
        self.progress_bar_height = 20
        self.progress_bar_width = self.width - 100
        self.temp_dir = "temp"
        self.current_speed = 1.0  
        self.current_video_path = ""  
        self.axzzz = ""
        self.asddd = True
        self.vvvv = False
        self.ctrl = False
        self.clock = pygame.time.Clock()
        self.clock_tick = 60
        self.video_player = None
        self.video_playing = False
        self.video_paused = False
        self.video_start_time = 0
        self.video_path = ""
        self.video_instance = None
        self.video_media = None
        self.music_was_playing = False  
        self.video_duration = 0  
        self.temp_message = ""
        self.temp_message_time = 0
        self.video_current_position = 0  
        self.watchdog_timer = Value('i', 0)
        
        self.alogstop = False
        
        
        self.backspace_time = 0.2
        self.net_process = None
        
        if asa:
            self.initialize_temp_dir()

            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1)

            base_path = ""
            print(str("."))
        
            self.load_images()
            
            self.find_music_files()
            self.fl()
        
            self.print_file_info()
        
            self.set_button_positions()
        
            self.window = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("音乐播放器")
            if self.music_icon:
                pygame.display.set_icon(self.music_icon)
                
            
    
    def initialize_temp_dir(self):
        for _ in range(3):  
            try:
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                os.makedirs(self.temp_dir, exist_ok=True)
                return
            except Exception as e:
                self.log_message(f"无法初始化临时文件夹: {str(e)}")
                time.sleep(0.5)
        self.log_message("警告：无法创建临时文件夹，封面功能可能受限")
    
    def load_images(self):
        try:
            
        
            self.next_img = pygame.image.load(os.path.join("./img", "next.png"))
            self.prev_img = pygame.image.load(os.path.join("./img", "up.png"))
            self.stop_img = pygame.image.load(os.path.join("./img", "stop.png"))
            self.play_img = pygame.image.load(os.path.join("./img", "play.png"))
            self.repeat_one_img = pygame.image.load(os.path.join("./img", "r.png"))
            self.repeat_all_img = pygame.image.load(os.path.join("./img", "r1.png"))
            self.repeat_none_img = pygame.image.load(os.path.join("./img", "l.png"))
            self.music_icon = pygame.image.load(os.path.join("./img", "music.png"))
            self.list_icon = pygame.image.load(os.path.join("./img", "list.png"))
            self.add_img = pygame.image.load(os.path.join("./img", "add.png"))
            self.reset_img = pygame.image.load(os.path.join("./img", "reset.png"))
            self.mv_img = pygame.image.load(os.path.join("./img", "mv.png"))
            self.video_list_img = pygame.image.load(os.path.join("./img", "video_list.png"))
            
            
            self.next_img = pygame.transform.scale(self.next_img, (self.button_size, self.button_size))
            self.prev_img = pygame.transform.scale(self.prev_img, (self.button_size, self.button_size))
            self.stop_img = pygame.transform.scale(self.stop_img, (self.button_size, self.button_size))
            self.play_img = pygame.transform.scale(self.play_img, (self.button_size, self.button_size))
            self.repeat_one_img = pygame.transform.scale(self.repeat_one_img, (self.button_size, self.button_size))
            self.repeat_all_img = pygame.transform.scale(self.repeat_all_img, (self.button_size, self.button_size))
            self.repeat_none_img = pygame.transform.scale(self.repeat_none_img, (self.button_size, self.button_size))
            self.list_icon = pygame.transform.scale(self.list_icon, (self.button_size, self.button_size))
            self.add_img = pygame.transform.scale(self.add_img, (self.button_size, self.button_size))
            self.reset_img = pygame.transform.scale(self.reset_img, (self.button_size, self.button_size))
            self.mv_img = pygame.transform.scale(self.mv_img, (self.button_size, self.button_size))
            self.video_list_img = pygame.transform.scale(self.video_list_img, (self.button_size, self.button_size)) 
            self.network_img = pygame.image.load(os.path.join("./img", "network.png"))
            self.network_img = pygame.transform.scale(self.network_img, (self.button_size, self.button_size))
            
        except Exception as e:
            self.log_message(f"警告：无法加载图片: {str(e)}，使用替代按钮")
            self.create_alternative_button()
    
    def create_alternative_button(self):
        self.next_img = pygame.Surface((self.button_size, self.button_size))
        self.next_img.fill((0, 200, 0))
        pygame.draw.polygon(self.next_img, (255, 255, 255), [
            (self.button_size*0.25, self.button_size*0.25), 
            (self.button_size*0.75, self.button_size*0.5), 
            (self.button_size*0.25, self.button_size*0.75)
        ])
        
        self.prev_img = pygame.Surface((self.button_size, self.button_size))
        self.prev_img.fill((0, 200, 0))
        pygame.draw.polygon(self.prev_img, (255, 255, 255), [
            (self.button_size*0.75, self.button_size*0.25), 
            (self.button_size*0.25, self.button_size*0.5), 
            (self.button_size*0.75, self.button_size*0.75)
        ])
        
        self.stop_img = pygame.Surface((self.button_size, self.button_size))
        self.stop_img.fill((0, 200, 0))
        pygame.draw.rect(self.stop_img, (255, 255, 255), 
                   (self.button_size*0.35, self.button_size*0.35, 
                    self.button_size*0.3, self.button_size*0.3))
        
        self.play_img = pygame.Surface((self.button_size, self.button_size))
        self.play_img.fill((200, 0, 0))
        pygame.draw.polygon(self.play_img, (255, 255, 255), [
            (self.button_size*0.35, self.button_size*0.25), 
            (self.button_size*0.35, self.button_size*0.75), 
            (self.button_size*0.75, self.button_size*0.5)
        ])
        
        self.repeat_one_img = pygame.Surface((self.button_size, self.button_size))
        self.repeat_one_img.fill((100, 100, 200))
        pygame.draw.circle(self.repeat_one_img, (255, 255, 255), 
                        (self.button_size//2, self.button_size//2), self.button_size//3, 2)
        pygame.draw.circle(self.repeat_one_img, (255, 255, 255), 
                        (self.button_size//2, self.button_size//2), self.button_size//10)
        
        self.repeat_all_img = pygame.Surface((self.button_size, self.button_size))
        self.repeat_all_img.fill((100, 200, 100))
        pygame.draw.circle(self.repeat_all_img, (255, 255, 255), 
                        (self.button_size//2, self.button_size//2), self.button_size//3, 2)
        pygame.draw.circle(self.repeat_all_img, (255, 255, 255), 
                        (self.button_size//2, self.button_size//2), self.button_size//10)
        
        self.repeat_none_img = pygame.Surface((self.button_size, self.button_size))
        self.repeat_none_img.fill((200, 100, 100))
        pygame.draw.circle(self.repeat_none_img, (255, 255, 255), 
                        (self.button_size//2, self.button_size//2), self.button_size//3, 2)
        
        self.music_icon = pygame.Surface((64, 64))
        self.music_icon.fill((200, 200, 255))
        pygame.draw.circle(self.music_icon, (100, 100, 255), (32, 32), 20)
        
        self.list_icon = None
        self.add_img = None
        
        self.video_list_img = pygame.Surface((self.button_size, self.button_size))
        self.video_list_img.fill((100, 150, 200))
        pygame.draw.rect(self.video_list_img, (50, 50, 100), (20, 15, 40, 50))
        pygame.draw.rect(self.video_list_img, (200, 200, 255), (25, 20, 30, 40))
        pygame.draw.circle(self.video_list_img, (200, 200, 255), (40, 50), 5)
        
        # 网络按钮替代
        self.network_img = pygame.Surface((self.button_size, self.button_size))
        self.network_img.fill((100, 150, 200))
        pygame.draw.circle(self.network_img, (50, 50, 100), (self.button_size//2, self.button_size//2), 20)
        pygame.draw.line(self.network_img, (200, 200, 255), 
                       (self.button_size//4, self.button_size//2),
                       (self.button_size*3//4, self.button_size//2), 3)
        pygame.draw.line(self.network_img, (200, 200, 255), 
                       (self.button_size//2, self.button_size//4),
                       (self.button_size//2, self.button_size*3//4), 3)
    
    def set_button_positions(self):
        button_y = 450
        self.prev_button_rect = pygame.Rect(25, button_y, self.button_size, self.button_size)
        self.play_button_rect = pygame.Rect(185, button_y, self.button_size, self.button_size)
        self.next_button_rect = pygame.Rect(345, button_y, self.button_size, self.button_size)
        self.mode_button_rect = pygame.Rect(505, button_y, self.button_size, self.button_size)
        self.list_button_rect = pygame.Rect(725, button_y, self.button_size, self.button_size)
        self.add_button_rect = pygame.Rect(865, button_y, self.button_size, self.button_size)
        self.reset_button_rect = pygame.Rect(865, 25, self.button_size, self.button_size)
        self.mv_button_rect = pygame.Rect(865, 115, self.button_size, self.button_size)  
        self.video_list_button_rect = pygame.Rect(600, button_y, self.button_size, self.button_size)  
        self.speed_button_rect = pygame.Rect(800, 390, 96, 24)
        self.network_button_rect = pygame.Rect(725, 25, self.button_size, self.button_size)
    
    def find_music_files(self):
        self.playlist = []
        extensions = ["*.flac", "*.mp3", "*.wav", "*.ogg", "*.m4a", "*.aac", "*.wma", "*.alac", "*.aiff", "*.opus"]
        
        if not os.path.exists("./music"):
            os.makedirs("./music", exist_ok=True)
            messagebox.showerror(title="" ,message="创建了music目录，请添加音乐文件")
        
        for ext in extensions:
            self.playlist.extend(glob.glob(os.path.join("./music", ext)))
        
        print(f"找到 {len(self.playlist)} 首音乐文件")
    
    def find_video_files(self):
        self.videoplaylist = []
        extensions = ["*.mp4", "*.mkv", "*.mpeg", "*.mp2", "*.mov", "*.avi", "*.wmv", "*.flv", "*.mp3"]
        if not os.path.exists("./video"):
            os.makedirs("./video", exist_ok=True)
            self.log_message("创建了video目录，请添加视频文件")
        
        for ext in extensions:
            self.videoplaylist.extend(glob.glob(f"video/**/{ext}",recursive=True))
        print(f"找到 {len(self.videoplaylist)} 个视频文件")
    
    def print_file_info(self):
        for i, song in enumerate(self.playlist):
            print(f"{i+1}. {os.path.basename(song)}")
        
        for i, video in enumerate(self.videoplaylist):
            print(f"{i+1}. {os.path.basename(video)}")
    
    def file_type(self, path):
        if not os.path.exists(path) or not os.path.isfile(path):
            return None
        
        try:
            mime_type, _ = mimetypes.guess_type(path)
            return mime_type
        except Exception as e:
            self.log_message(f"文件类型检测错误: {str(e)}")
            return None
    
    def add_file_to_playlist(self, is_video=False):
        file_added = False
        
        try:
            while True:
                file_path = filedialog.askopenfilename()
                
                if not file_path:
                    break
                    
                file_type = self.file_type(file_path)
                if os.path.isfile(file_path):
                    
                    if file_type and file_type.split('/')[0] == "audio":
                        self.playlist.append(file_path)
                        file_added = True
                        
                        break
                    else:
                        choice = pymsgbox.confirm( 
                        title="信息", 
                        text="添加错误，原因：文件不是音乐文件", 
                        buttons=["重新选择", "取消", "我知道我在做什么！", "这是视频文件！"]
                        )
                        if choice is None:
                            break
                        if choice == "取消":
                            break
                        if choice == "我知道我在做什么！":
                            self.playlist.append(file_path)
                            file_added = True
                            
                            break
                        if choice == "这是视频文件！":
                            self.videoplaylist.append(file_path)
                            file_added = True
                            
                            break
                    
        except Exception as e:
            self.log_message(f"添加文件错误: {str(e)}")
            messagebox.showerror(
                title="信息", 
                message=f"添加错误，原因：{str(e)}", 
                
            )
        
        self.root.withdraw()  
        return file_added
    
    def play_video_vlc(self, file_path):
        self.current_video_path = file_path
        if self.video_playing:
            self.stop_video(False)
        
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.music_was_playing = True  
            
        else:
            self.music_was_playing = False
        
        try:
            params = [
                "--network-caching=3000",  
                "--avcodec-hw=any",       
                "--codec=avcodec",         
                "--verbose=-1"    
            ]
            self.video_instance = vlc.Instance(" ".join(params))
            self.video_player = self.video_instance.media_player_new()
            
            self.video_media = self.video_instance.media_new(file_path)
            self.video_media.add_option(":avcodec-threads=4")  
            self.video_media.add_option(":mjpeg-fixed-size=off")  

            self.video_player.set_media(self.video_media)
           
            self.video_player.set_fullscreen(False)  
            self.current_speed = 1.0
            self.video_player.play()
            self.video_playing = True
            self.video_paused = False
            self.video_path = file_path
            self.video_start_time = time.time()
            print(f"开始播放视频: {os.path.basename(file_path)}")
            self.set_video_speed(self.current_speed)
            self.video_duration = 0
            self.video_current_position = 0
            
            for _ in range(10):  
                length = self.video_player.get_length()
                if length > 0:
                    self.video_duration = length
                    
                    break
                time.sleep(0.1)
            
        except Exception as e:
            self.log_message(f"视频播放错误: {str(e)}")
            messagebox.showwarning(
                title="信息", 
                message=f"无法播放视频: {os.path.basename(file_path)}\n错误: {str(e)}")
            self.video_playing = False
            
            if self.music_was_playing and not pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.log_message("视频播放失败，恢复音乐")
            print(e)

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def stop_video(self, repeat=False):
        if self.video_player:
            try:
                if self.current_mode == self.PLAY_MODE_REPEAT_ONE and repeat:
                    if self.video_player:
                        self.video_player.set_rate(self.current_speed)
                    self.play_video_vlc(self.current_video_path)
                    return
                else:
                    self.video_player.stop()
                    self.video_player.release()
                    print(f"视频停止播放: {os.path.basename(self.video_path)}")
            except Exception as e:
                print(f"停止视频错误: {str(e)}")

        self.video_player = None
        self.video_media = None
        self.video_instance = None
        self.video_playing = False
        self.video_paused = False
        self.video_path = ""
        self.music_was_playing = False
        self.video_duration = 0
        self.video_current_position = 0
        
        if self.music_was_playing and not pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
            self.log_message("停止视频后恢复音乐")
    
    def pause_resume_video(self):
        if self.video_player:
            try:
                if self.video_paused:
                    self.video_player.play()
                    self.video_paused = False
                    
                else:
                    self.video_player.pause()
                    self.video_paused = True
                    
            except Exception as e:
                self.log_message(f"视频暂停/恢复错误: {str(e)}")
    
    def extract_cover(self, track_path):
        if track_path in self.cover_cache:
            return self.cover_cache[track_path]
        
        try:
            cover_data = None
            
            file_hash = ""
            try:
                with open(track_path, "rb") as f:
                    file_hash = hashlib.md5(f.read(4096)).hexdigest()
                    if file_hash in self.cover_cache:
                        return self.cover_cache[file_hash]
            except Exception as e:
                self.log_message(f"文件哈希计算错误: {str(e)}")
                file_hash = hashlib.md5(track_path.encode()).hexdigest()
                if file_hash in self.cover_cache:
                    return self.cover_cache[file_hash]
            
            if track_path.lower().endswith('.mp3'):
                try:
                    tags = ID3(track_path)
                    for tag in tags.values():
                        if isinstance(tag, APIC):
                            cover_data = tag.data
                            break
                    else:
                        audio = MP3(track_path)
                        if 'APIC:' in audio:
                            cover_data = audio['APIC:'].data
                        elif 'covr' in audio:
                            cover_data = audio['covr'].data[0]
                except Exception as e:
                    self.log_message(f"MP3封面提取错误: {str(e)}")
            
            elif track_path.lower().endswith('.flac'):
                try:
                    audio = FLAC(track_path)
                    if audio.pictures:
                        cover_data = audio.pictures[0].data
                except Exception as e:
                    self.log_message(f"FLAC封面提取错误: {str(e)}")
            
            elif track_path.lower().endswith('.ogg'):
                try:
                    audio = OggVorbis(track_path)
                    if 'metadata_block_picture' in audio:
                        cover_data = audio['metadata_block_picture'][0]
                except Exception as e:
                    self.log_message(f"OGG封面提取错误: {str(e)}")
            
            if cover_data:
                try:
                    if not file_hash:
                        file_hash = hashlib.md5(track_path.encode()).hexdigest()
                    
                    cover_path = os.path.join(self.temp_dir, f"cover_{file_hash}.png")
                    
                    with open(cover_path, 'wb') as f:
                        f.write(cover_data)
                    
                    img = pygame.image.load(cover_path)
                    cover_img = pygame.transform.scale(img, (200, 200))
                    
                    self.cover_cache[track_path] = cover_img
                    if file_hash:
                        self.cover_cache[file_hash] = cover_img
                    
                    return cover_img
                except Exception as e:
                    self.log_message(f"加载封面图像失败: {str(e)}")
        
        except Exception as e:
            self.log_message(f"封面提取失败: {str(e)}")
        
        return None
    
    def play_track(self, track_index):
        if not self.playlist or track_index < 0 or track_index >= len(self.playlist):
            self.log_message("无效的曲目索引")
            return

        if not self.playlist:
            return
        
        if self.video_playing:
            self.stop_video(False)
        
        track_index = max(0, min(track_index, len(self.playlist) - 1))
        self.current_track = track_index
        track_path = self.playlist[self.current_track]
        
        try:
            if track_path.lower().endswith('.mp3'):
                audio = MP3(track_path)
                self.track_duration = audio.info.length
            elif track_path.lower().endswith('.flac'):
                audio = FLAC(track_path)
                self.track_duration = audio.info.length
            elif track_path.lower().endswith('.ogg'):
                audio = OggVorbis(track_path)
                self.track_duration = audio.info.length
            elif track_path.lower().endswith('.wav'):
                audio = WAVE(track_path)
                self.track_duration = audio.info.length
            else:
                audio = File(track_path)
                if audio:
                    self.track_duration = audio.info.length
                else:
                    self.track_duration = 0  
        except Exception as e:
            self.log_message(f"无法获取歌曲时长: {str(e)}")
            self.track_duration = 0
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.track_start_time = time.time()
            self.paused = False
            self.current_position = 0
            self.paused_time = 0
            
            
            
            self.cover_img = self.extract_cover(track_path)
            
        except pygame.error as e:
            self.log_message(f"无法播放: {str(e)}")
            messagebox.showwarning(
                title="播放错误", 
                text=f"无法播放文件: {str(e)}"
            )
            if self.current_track > 0:
                new_track = self.current_track - 1
                self.play_track(new_track)
        except Exception as e:
            self.log_message(f"播放过程中发生错误: {str(e)}")
            messagebox.showwarning(
                title="播放错误", 
                text=f"播放错误: {str(e)}"
            )
    
    def display_list(self, display_list, title="播放列表", list_type="music"):
        list_width, list_height = 1000, 600
        list_window = pygame.display.set_mode((list_width, list_height))
        pygame.display.set_caption(title)
        
        try:
            list_font = pygame.font.SysFont("simhei", 20)
        except:
            list_font = pygame.font.Font(pygame.font.get_default_font(), 20)
        
        items_per_page = list_height // 30 - 2
        
        current_page = 0
        selected_index = self.current_track if self.current_track >= 0 and list_type == "music" else 0
        running_list = True
        
        last_click_time = 0
        last_click_index = -1
        
        while running_list:
            start_idx = current_page * items_per_page
            end_idx = min(start_idx + items_per_page, len(display_list))
            
            list_window.fill((40, 40, 60))
            
            title_text = list_font.render(f"{title} ({len(display_list)} 个项目)", True, (255, 255, 200))
            list_window.blit(title_text, (10, 10))
            
            item_rects = []  
            for i, idx in enumerate(range(start_idx, end_idx)):
                y_pos = 40 + i * 30
                item_name = os.path.basename(display_list[idx])
                if '.' in item_name:
                    item_name = item_name.rsplit('.', 1)[0]  
                
                display_name = item_name[:50] + ".." if len(item_name) > 50 else item_name
                
                if list_type == "music" and idx == self.current_track:
                    color = (100, 255, 100)
                    pygame.draw.rect(list_window, (30, 70, 30), (5, y_pos - 2, list_width - 10, 26))
                elif idx == selected_index:
                    color = (200, 200, 255)
                    pygame.draw.rect(list_window, (50, 50, 90), (5, y_pos - 2, list_width - 10, 26))
                else:
                    color = (200, 200, 200)
                
                text = list_font.render(f"{idx+1}. {display_name}", True, color)
                list_window.blit(text, (15, y_pos))
                
                item_rect = pygame.Rect(5, y_pos - 2, list_width - 10, 26)
                item_rects.append((idx, item_rect))
            
            page_info = list_font.render(f"第 {current_page+1}/{((len(display_list)-1)//items_per_page)+1} 页", True, (180, 180, 255))
            list_window.blit(page_info, (list_width - page_info.get_width() - 10, list_height - 30))
            
            controls_text = "↑↓: 选择  Enter: 播放  PgUp/PgDn: 翻页  Del: 删除  Esc: 退出"
            if list_type == "video":
                controls_text = "↑↓: 选择  Enter: 播放视频  PgUp/PgDn: 翻页  Del: 删除  Esc: 退出"
            
            controls = list_font.render(controls_text, True, (180, 180, 255))
            list_window.blit(controls, (10, list_height - 30))
            
            mouse_controls = list_font.render("鼠标: 左键选择 双击播放 右键删除 滚轮翻页", True, (180, 255, 180))
            list_window.blit(mouse_controls, (list_width - mouse_controls.get_width() - 10, 10))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_list = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running_list = False
                    
                    elif event.key == pygame.K_DELETE:
                        if display_list and 0 <= selected_index < len(display_list):
                            if list_type == "music" and selected_index == self.current_track:
                                pygame.mixer.music.stop()
                                self.current_track = -1
                            
                            removed_item = display_list.pop(selected_index)
                            self.log_message(f"已删除: {os.path.basename(removed_item)}")
                            
                            if list_type == "music":
                                if self.current_track > selected_index:
                                    self.current_track -= 1
                                elif self.current_track == selected_index:
                                    self.current_track = -1
                            
                            if selected_index >= len(display_list):
                                selected_index = max(0, len(display_list) - 1)
                            
                            if len(display_list) == 0:
                                running_list = False
                    
                    elif event.key == pygame.K_UP:
                        selected_index = max(0, selected_index - 1)
                        if selected_index < start_idx:
                            current_page = max(0, current_page - 1)
                    
                    elif event.key == pygame.K_DOWN:
                        selected_index = min(len(display_list) - 1, selected_index + 1)
                        if selected_index >= end_idx:
                            current_page = min((len(display_list) - 1) // items_per_page, current_page + 1)
                    
                    elif event.key == pygame.K_PAGEUP:
                        current_page = max(0, current_page - 1)
                        selected_index = current_page * items_per_page
                    
                    elif event.key == pygame.K_PAGEDOWN:
                        current_page = min((len(display_list) - 1) // items_per_page, current_page + 1)
                        selected_index = current_page * items_per_page
                    
                    elif event.key == pygame.K_RETURN:
                        if list_type == "music":
                            self.play_track(selected_index)
                        elif list_type == "video":
                            self.play_video_vlc(display_list[selected_index])
                        running_list = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if event.button == 4:  
                        current_page = max(0, current_page - 1)
                        selected_index = current_page * items_per_page
                    elif event.button == 5:  
                        max_page = (len(display_list) - 1) // items_per_page
                        current_page = min(max_page, current_page + 1)
                        selected_index = current_page * items_per_page
                    
                    elif event.button == 1:  
                        for idx, rect in item_rects:
                            if rect.collidepoint(mouse_pos):
                                current_time = pygame.time.get_ticks()
                                
                                if idx == last_click_index and (current_time - last_click_time) < 300:
                                    if list_type == "music":
                                        self.play_track(idx)
                                    elif list_type == "video":
                                        self.play_video_vlc(display_list[idx])
                                    running_list = False
                                    break
                                else:
                                    selected_index = idx
                                    last_click_index = idx
                                    last_click_time = current_time
                    
                    elif event.button == 3:  
                        for idx, rect in item_rects:
                            if rect.collidepoint(mouse_pos):
                                confirm = pymsgbox.confirm(
                                    title="确认删除", 
                                    text=f"确定要删除 '{os.path.basename(display_list[idx])}' 吗?",
                                    buttons=["是", "否"]
                                )
                                if confirm is None:
                                    continue
                                if confirm == "是":
                                    if list_type == "music" and idx == self.current_track:
                                        pygame.mixer.music.stop()
                                        self.current_track = -1
                                    
                                    removed_item = display_list.pop(idx)
                                    self.log_message(f"已删除: {os.path.basename(removed_item)}")
                                    
                                    if list_type == "music":
                                        if self.current_track > idx:
                                            self.current_track -= 1
                                        elif self.current_track == idx:
                                            self.current_track = -1
                                    
                                    if selected_index > idx:
                                        selected_index -= 1
                                    elif selected_index == idx:
                                        selected_index = min(selected_index, len(display_list) - 1)
                                    
                                    if len(display_list) == 0:
                                        running_list = False
                                    break
        
        pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("音乐播放器")
        
        return display_list
    
    def reset_player(self):
        self.log_message("重置播放器状态")
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        if self.video_playing:
            self.stop_video(False)
        
        self.load_images()
        self.find_music_files()
        self.fl()
        self.current_track = -1
        self.track_start_time = 0
        self.track_duration = 0
        self.current_position = 0
        self.paused = False
        self.paused_time = 0
        self.cover_img = None
        self.print_file_info()
    
    def play_matching_video(self):
        if not self.playlist or self.current_track < 0:
            messagebox.showwarning(
                title="提示", 
                message="没有正在播放的音乐", 
            )
            return
        
        music_name = os.path.basename(self.playlist[self.current_track])
        music_name = music_name.rsplit('.', 1)[0]  
        
        video_index = -1
        for i, video in enumerate(self.videoplaylist):
            video_name = os.path.basename(video)
            video_name = video_name.rsplit('.', 1)[0]  
            if video_name == music_name:
                video_index = i
                break
        
        if video_index >= 0:
            if self.video_playing:
                self.stop_video(False)
            
            self.play_video_vlc(self.videoplaylist[video_index])
        else:
            messagebox.showwarning(
                title="提示", 
                message="未找到匹配的视频文件"
            )
    
    
        
    def net_start(self):
        a = os.path.dirname(__file__) +'\\net'
        a = ini(a=a)
        b = a.get("ip")
        if b == None:
            b = "127.0.0.1"
        c = a.getint("port")
        if c == None:
            c = 22
        d = a.get("username")
        if d == None:
            d = "ftp"
        kl = a.get("password")
        if kl == None:
            kl = "1234"
        print(f"网络配置 - IP: {b}, 端口: {c}, 用户名: {d}, 密码: {kl}")
        self.net_process = Process(target=netmain,args=(b,c,d,kl),daemon=True)
        self.net_process.start()    
        
    
    #========================================================
  
    # ====================== 主运行循环 ======================
    def backspace(self):
        while self.running:
            pcid = pygame.key.get_pressed()
            if pcid[pygame.K_BACKSPACE] and self.cmd_input_active:
                self.cmd_string = self.cmd_string[:-1]
                print(f"命令输入: {self.cmd_string}")
            
            time.sleep(self.backspace_time)
    def run(self,z=False):
        print("aasssxcxx")

        running = True
        cmd_input_active = False 
        cmd_input_activeq = False
        self.cmd_string = ""
        
        self.backspaceaaaaa = threading.Thread(target=self.backspace,daemon=True)
        self.backspaceaaaaa.start()
        
        if not pygame.get_init():
            pygame.init()
            pygame.mixer.init()

        # 确保字体模块已初始化
        if not pygame.font.get_init():
            pygame.font.init()
        base_path = self.resource_path("")

        # 加载字体
        try:
            font_path = os.path.join(str("."), "fonts", "simhei.ttf")
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, 24)
                small_font = pygame.font.Font(font_path, 16)
            else:
                # 使用系统默认字体
                font = pygame.font.SysFont("simhei", 24)
                small_font = pygame.font.SysFont("simhei", 16)
        except Exception as e:
            # 回退到基本字体
            print(f"字体加载错误: {e}")
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 16)
        
        while running:
            
            current_time = time.time()
            mouse_pos = pygame.mouse.get_pos()
            
            if self.video_playing and self.video_player:
                state = self.video_player.get_state()
                if state == vlc.State.Ended:
                    self.stop_video(True)  
        
            if self.video_playing and self.video_player:
                current_pos = self.video_player.get_time()
                if current_pos > 0:
                    self.video_current_position = current_pos
                
                if self.video_duration <= 0:
                    length = self.video_player.get_length()
                    if length > 0:
                        self.video_duration = length
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    print("fenknfenjfkenm")
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = event.pos
                    if self.reset_button_rect.collidepoint(mouse):
                        self.reset_player()
                    
                    elif self.list_button_rect.collidepoint(mouse):
                        self.playlist = self.display_list(self.playlist, "音乐播放列表", "music")
                    
                    elif self.add_button_rect.collidepoint(mouse):
                        self.add_file_to_playlist()
                    
                    elif self.play_button_rect.collidepoint(mouse):
                        if self.video_playing:
                            self.pause_resume_video()
                        elif pygame.mixer.music.get_busy() and not self.paused:
                            pygame.mixer.music.pause()
                            self.paused = True
                            self.paused_time = current_time
                           
                        elif self.paused:
                            pygame.mixer.music.unpause()
                            self.paused = False
                            if self.paused_time > 0:
                                self.track_start_time += (current_time - self.paused_time)
                                self.paused_time = 0
                            
                        elif not pygame.mixer.music.get_busy() and self.playlist:
                            track_to_play = self.current_track if self.current_track >= 0 else 0
                            self.play_track(track_to_play)
                    
                    elif self.prev_button_rect.collidepoint(mouse):
                        if self.video_playing:
                            self.stop_video(False)
                            
                        if self.playlist:
                            if self.current_track > 0:
                                new_track = self.current_track - 1
                            elif self.current_mode == self.PLAY_MODE_REPEAT_ALL:
                                new_track = len(self.playlist) - 1
                            else:
                                new_track = self.current_track
                            self.play_track(new_track)
                    
                    elif self.next_button_rect.collidepoint(mouse):
                        if self.video_playing:
                            self.stop_video(False)
                            
                        if self.playlist:
                            if self.current_track < len(self.playlist) - 1:
                                new_track = self.current_track + 1
                            elif self.current_mode == self.PLAY_MODE_REPEAT_ALL:
                                new_track = 0
                            else:
                                new_track = self.current_track
                            self.play_track(new_track)
                    
                    elif self.mode_button_rect.collidepoint(mouse):
                        self.current_mode = (self.current_mode + 1) % 3
                        mode_names = ["正常播放", "单曲循环", "列表循环"]

                    elif self.mv_button_rect.collidepoint(mouse):
                        self.play_matching_video()
                    
                    elif self.video_list_button_rect.collidepoint(mouse):
                        self.display_list(self.videoplaylist, "视频列表", "video")
                    
                    elif self.speed_button_rect.collidepoint(mouse) and self.video_playing:
                        self.speed()
                    
                    elif self.network_button_rect.collidepoint(mouse):
                        self.net_start()
                            
                            
                elif event.type == pygame.TEXTINPUT:
                    self.cmd_string += event.text
                    if not cmd_input_activeq:
                        self.cmd_string = self.cmd_string[:-1]
                        cmd_input_activeq = True
                    print(f"命令输入: {self.cmd_string}")
                        
                elif event.type == pygame.KEYDOWN:
                    if cmd_input_active:
                        if pygame.key.get_mods() & (pygame.KMOD_CTRL):
                            if event.key == pygame.K_v:
                                if self.cmd_input_active:
                                    try:
                                        clipboard_text = pyperclip.paste()
                                        self.cmd_string += clipboard_text
                                        print(f"粘贴内容: {clipboard_text}")
                                    except Exception as e:
                                        print(f"粘贴失败: {e}")
                        
                        
                    if event.key == pygame.K_SLASH and not cmd_input_active:  
                        cmd_input_active = True
                        cmd_input_activeq = False
                        self.cmd_string = ""
                        print("进入命令输入模式")
                    if cmd_input_active:
                        if event.key == pygame.K_RETURN:
                            cmd_list = self.cmd_string.split(" ")                        
                            if cmd_list[0] == "python":
                                if len(cmd_list) > 1:
                                    aaaaaaa =  " ".join(cmd_list[1:])
                                    print(f"执行python命令: {aaaaaaa}")
                                    try:
                                        exec(aaaaaaa)
                                    except Exception as e:
                                        self.log_message(f"执行错误: {e}")
                                        print(f"执行错误: {e}")
                                        traceback.print_exc()
                            elif cmd_list[0] == "system":
                                if len(cmd_list) > 1:
                                    for i in range(1, len(cmd_list)):
                                        if i == 1:
                                            cmd_string = cmd_list[i]
                                        else:
                                            cmd_string += " " + cmd_list[i]
                                    print(f"执行系统命令: {cmd_string}")
                                    t = threading.Thread(target=os.system, args=(cmd_string,))
                                    t.start()
                            elif cmd_list[0] == "set_speed":
                                if len(cmd_list) > 1:
                                    try:
                                        speed_value = float(cmd_list[1])
                                        
                                        if self.set_video_speed(speed_value):
                                            self.current_speed = speed_value
                                            print(f"视频速度设置为: {speed_value}x")
                                        else:
                                            print("无法设置速度，视频未播放")
                                    except ValueError:
                                        print("无效的速度值") 
                            elif  cmd_list[0] == "add_video":
                                asm = filedialog.askopenfilenames(title="选择视频文件",filetypes=[("视频文件", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.wmv"),("所有文件", "*.*")])
                                if asm:
                                    for video_file in asm:
                                        if os.path.isfile(video_file):
                                            if video_file not in self.videoplaylist:
                                                self.videoplaylist.append(video_file)
                                                self.log_message(f"已添加视频: {os.path.basename(video_file)}")
                                                self.root.withdraw()
                            elif cmd_list[0] == "download":
                                aaa = 0
                                if len(cmd_list) > 1:
                                    cmd_sssstring = " ".join(cmd_list[1:])
                                    print(cmd_sssstring)
                                    try:
                                        if cmd_sssstring == "stop":
                                            self.asddd = False
                                            self.cmd_string = None
                                        elif cmd_sssstring == "no cookies":
                                            self.cmd_string = sdialog.askstring(title="a",prompt="请输入网址或者bvid号",initialvalue="https://www.bilibili.com/video/BV1e5hxzoEZf?t=5.0")
                                            if self.cmd_string != None:
                                                t = threading.Thread(target=self.bilibilidownload,args=(self.cmd_string,aaa, False))
                                                t.daemon = True
                                                t.start()
                                                self.cmd_string = None
                                        
                                        else:
                                            self.cmd_string = sdialog.askstring(title="a",prompt="请输入网址或者bvid号",initialvalue="https://www.bilibili.com/video/BV1e5hxzoEZf?t=5.0")
                                            if cmd_sssstring != "":
                                                aaa = int(cmd_sssstring)
                                    except Exception as aaa:
                                        print(aaa)
                                        aaa = 0
                                        self.cmd_string = sdialog.askstring(title="a",prompt="请输入网址或者bvid号",initialvalue="https://www.bilibili.com/video/BV1e5hxzoEZf?t=5.0")
                                else:
                                    self.cmd_string = sdialog.askstring(title="a",prompt="请输入网址或者bvid号",initialvalue="https://www.bilibili.com/video/BV1e5hxzoEZf?t=5.0")
                                if self.cmd_string != None:
                                    t = threading.Thread(target=self.bilibilidownload,args=(self.cmd_string,aaa))
                                    t.daemon = True
                                    t.start()
                                    self.cmd_string = None
                                aaa = 0
                                    
                            elif cmd_list[0] == "close_net":
                                try:
                                    if self.net_process is not None:
                                        if self.net_process.is_alive():
                                            self.net_process.terminate()
                                            def terminate_process(process):
                                                process.join(timeout=5)
                                                if process.is_alive():
                                                    process.kill()
                                            threading.Thread(target=terminate_process, args=(self.net_process,)).start()
                                
                                            self.log_message("已关闭网络服务")
                                    
                                        else:
                                            self.log_message("网络服务未运行")
                                    else:
                                        self.log_message("网络服务未运行")
                                except Exception as e:
                                    self.log_message(f"关闭网络服务错误: {str(e)}")
                            elif cmd_list[0] == "help":
                                print("帮助")
                                a = open("help.txt","w",encoding="utf-8")
                                temp_list = ["/help 帮助",
                                            "/system 执行系统指令",
                                            "/download 下载视频",
                                            "/download stop 停止下载",
                                            "/download no cookies 使用无cookie模式下载",
                                            "/download [数字] 限制弹幕行数下载",
                                            "/set_speed [数字] 设置视频播放速度",
                                            "/add_video 添加视频文件到播放列表",
                                            "/boom 使程序报错",
                                            "/kill pc 使你的电脑螺旋升天" ]
                                for temp in temp_list:
                                    a.write(temp)
                                    a.write("\n")
                                    a.flush()
                                a.close()
                                os.system("start notepad help.txt")
                                
                            elif cmd_list[0] == "boom":
                                cmd_list = a /  0
                            elif cmd_list[0] == "mouse":
                                print(mouse_pos)
                            elif cmd_list[0] == "kill":
                                if len(cmd_list) > 1:
                                    if cmd_list[1] == "pc":
                                        self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                        if self.aaaaaaaaa == True:
                                            self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                            if self.aaaaaaaaa == True:
                                                self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                if self.aaaaaaaaa == True:
                                                    self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                    if self.aaaaaaaaa == True:
                                                        self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                        if self.aaaaaaaaa == True:
                                                            self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                            if self.aaaaaaaaa == True:
                                                                self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                                if self.aaaaaaaaa == True:
                                                                    self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                                    if self.aaaaaaaaa == True:
                                                                        self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                                        if self.aaaaaaaaa == True:
                                                                            self.aaaaaaaaa = messagebox.askyesno(title="你要把电脑炸了吗?",message="你要把电脑炸了吗?") 
                                                                            if self.aaaaaaaaa == True:
                                                                                self.log_message("正在炸电脑..")
                                                                                messagebox.showinfo("你sb吧,这么闲?","你sb吧,这么闲?")
                                                                                sys.setrecursionlimit(2147483647)
                                                                                #j.kill_pc_process()
                                            
                                            
                                            
                                            
                            elif self.cmd_string == "net start":
                                self.net_start()
                                
                            else:
                                messagebox.showerror(message="错误的指令",title="错误")
                                
                            cmd_input_active = False
                            self.cmd_string = ""
                            
                        
                        
                        
                        
                        elif event.key == pygame.K_ESCAPE:
                            cmd_input_active = False
                            self.cmd_string = ""
                            print("退出命令输入模式")
                    
                    else:

                        if event.key == pygame.K_SPACE:
                            if self.video_playing:
                                self.pause_resume_video()
                            elif pygame.mixer.music.get_busy() and not self.paused:
                                pygame.mixer.music.pause()
                                self.paused = True
                                self.paused_time = current_time
                                
                            elif self.paused:
                                pygame.mixer.music.unpause()
                                self.paused = False
                                if self.paused_time > 0:
                                    self.track_start_time += (current_time - self.paused_time)
                                    self.paused_time = 0
                                
                            elif not pygame.mixer.music.get_busy() and self.playlist:
                                track_to_play = self.current_track if self.current_track >= 0 else 0
                                self.play_track(track_to_play)
                    
                        elif event.key == pygame.K_LEFT:
                            if self.video_playing:
                                self.stop_video(False)

                            if self.playlist:
                                if self.current_track > 0:
                                    new_track = self.current_track - 1
                                elif self.current_mode == self.PLAY_MODE_REPEAT_ALL:
                                    new_track = len(self.playlist) - 1
                                else:
                                    new_track = self.current_track
                                self.play_track(new_track)

                        elif event.key == pygame.K_RIGHT:
                            if self.video_playing:
                                self.stop_video(False)
                            
                            if self.playlist:
                                if self.current_track < len(self.playlist) - 1:
                                    new_track = self.current_track + 1
                                elif self.current_mode == self.PLAY_MODE_REPEAT_ALL:
                                    new_track = 0
                                else:
                                    new_track = self.current_track
                                self.play_track(new_track)
                            
                        elif event.key == pygame.K_ESCAPE:  
                            if self.video_playing:
                                self.stop_video(False)
            
            if not self.video_playing and not self.paused and not pygame.mixer.music.get_busy() and self.playlist and self.current_track >= 0:
                if self.current_mode == self.PLAY_MODE_REPEAT_ONE:
                    next_track = self.current_track
                elif self.current_track < len(self.playlist) - 1:
                    next_track = self.current_track + 1
                elif self.current_mode == self.PLAY_MODE_REPEAT_ALL:
                    next_track = 0
                else:
                    self.log_message("播放列表结束")
                    next_track = None
                
                if next_track is not None:
                    self.play_track(next_track)
            
            if not self.video_playing and not self.paused and pygame.mixer.music.get_busy() and self.track_duration > 0:
                if self.paused_time > 0:
                    self.track_start_time += (current_time - self.paused_time)
                    self.paused_time = 0
                self.current_position = current_time - self.track_start_time
                if self.current_position > self.track_duration:
                    self.current_position = self.track_duration
            
            self.window.fill((30, 30, 50))
            
            if self.playlist and self.current_track >= 0 and self.cover_img and not self.video_playing:
                self.window.blit(self.cover_img, (50, 50))
            else:
                default_cover = pygame.transform.scale(self.music_icon, (200, 200)) if self.music_icon else None
                if default_cover and not self.video_playing:
                    self.window.blit(default_cover, (50, 50))
            
            if not self.video_playing:
                pygame.draw.rect(self.window, (100, 100, 150), (45, 45, 210, 210), 2)
                cover_title = small_font.render("专辑封面", True, (180, 180, 255))
                self.window.blit(cover_title, (50, 260))
            
            if self.video_playing:
                video_name = os.path.basename(self.video_path)
                if '.' in video_name:
                    video_name = video_name.rsplit('.', 1)[0]
                display_name = video_name[:20] + ".." if len(video_name) > 20 else video_name
                
                text_surface = font.render(f"正在播放: {display_name}", True, (220, 220, 220))
                self.window.blit(text_surface, (300, 50))
                
                status = "已暂停" if self.video_paused else "播放中"
                status_text = font.render(f"视频状态: {status}", True, (180, 180, 255))
                self.window.blit(status_text, (300, 100))
            elif self.playlist and 0 <= self.current_track < len(self.playlist):
                track_name = os.path.basename(self.playlist[self.current_track])
                if '.' in track_name:
                    track_name = track_name.rsplit('.', 1)[0]
                display_name = track_name[:20] + ".." if len(track_name) > 20 else track_name
                
                text_surface = font.render(f"正在播放: {display_name}", True, (220, 220, 220))
                self.window.blit(text_surface, (300, 50))
            
            if self.playlist and self.current_track >= 0 and not self.video_playing:
                progress_text = font.render(f"曲目: {self.current_track + 1}/{len(self.playlist)}", True, (180, 180, 255))
                self.window.blit(progress_text, (300, 100))
            
            mode_text = font.render(f"播放模式: ", True, (180, 180, 255))
            self.window.blit(mode_text, (300, 150))
            
            if self.current_mode == self.PLAY_MODE_NORMAL:
                mode_name = "正常播放"
            elif self.current_mode == self.PLAY_MODE_REPEAT_ONE:
                mode_name = "单曲循环"
            else:
                mode_name = "列表循环"
            
            mode_name_text = font.render(mode_name, True, (220, 220, 100))
            self.window.blit(mode_name_text, (420, 150))
            
            progress_bar_y = 350
            
            pygame.draw.rect(self.window, (80, 80, 100), (50, progress_bar_y, self.progress_bar_width, self.progress_bar_height))
            
            if self.video_playing:
                if self.video_duration > 0:
                    progress_width = int(self.progress_bar_width * (self.video_current_position / self.video_duration))
                    pygame.draw.rect(self.window, (0, 100, 200), (50, progress_bar_y, progress_width, self.progress_bar_height))
                    
                    current_min = int(self.video_current_position // 60000)
                    current_sec = int((self.video_current_position % 60000) // 1000)
                    current_time_str = f"{current_min:02d}:{current_sec:02d}"
                    
                    total_min = int(self.video_duration // 60000)
                    total_sec = int((self.video_duration % 60000) // 1000)
                    total_time_str = f"{total_min:02d}:{total_sec:02d}"
                    
                    current_time_surface = small_font.render(current_time_str, True, (220, 220, 220))
                    total_time_surface = small_font.render(total_time_str, True, (220, 220, 220))
                    
                    self.window.blit(current_time_surface, (50, progress_bar_y + self.progress_bar_height + 5))
                    self.window.blit(total_time_surface, (50 + self.progress_bar_width - total_time_surface.get_width(), 
                                                progress_bar_y + self.progress_bar_height + 5))
                else:
                    anim_width = int(self.progress_bar_width * 0.5 + self.progress_bar_width * 0.3 * abs(pygame.time.get_ticks() % 2000 - 1000) / 1000)
                    pygame.draw.rect(self.window, (0, 150, 200), (50, progress_bar_y, anim_width, self.progress_bar_height))
            
            elif self.playlist and self.current_track >= 0:
                if self.track_duration > 0 and self.current_position < self.track_duration:
                    progress_width = int(self.progress_bar_width * (self.current_position / self.track_duration))
                    pygame.draw.rect(self.window, (0, 200, 100), (50, progress_bar_y, progress_width, self.progress_bar_height))
                elif self.track_duration > 0 and self.current_position >= self.track_duration:
                    pygame.draw.rect(self.window, (0, 200, 100), (50, progress_bar_y, self.progress_bar_width, self.progress_bar_height))
                elif self.playlist:
                    anim_width = int(self.progress_bar_width * 0.5 + self.progress_bar_width * 0.3 * abs(pygame.time.get_ticks() % 2000 - 1000) / 1000)
                    pygame.draw.rect(self.window, (0, 150, 200), (50, progress_bar_y, anim_width, self.progress_bar_height))
                
                if self.track_duration > 0:
                    current_min = int(self.current_position // 60)
                    current_sec = int(self.current_position % 60)
                    current_time_str = f"{current_min:02d}:{current_sec:02d}"
                    
                    total_min = int(self.track_duration // 60)
                    total_sec = int(self.track_duration % 60)
                    total_time_str = f"{total_min:02d}:{total_sec:02d}"
                    
                    current_time_surface = small_font.render(current_time_str, True, (220, 220, 220))
                    total_time_surface = small_font.render(total_time_str, True, (220, 220, 220))
                    
                    self.window.blit(current_time_surface, (50, progress_bar_y + self.progress_bar_height + 5))
                    self.window.blit(total_time_surface, (50 + self.progress_bar_width - total_time_surface.get_width(), 
                                                progress_bar_y + self.progress_bar_height + 5))
            
            pygame.draw.rect(self.window, (200, 200, 200), (50, progress_bar_y, self.progress_bar_width, self.progress_bar_height), 2)
            
            self.window.blit(self.prev_img, self.prev_button_rect)
            self.window.blit(self.next_img, self.next_button_rect)
            if pygame.time.get_ticks() < self.temp_message_time:
                msg_font = pygame.font.Font(f"{str('.')}\\fonts\\simhei.ttf", 30)
                msg_text = msg_font.render(self.temp_message, True, (255, 255, 0))
                msg_rect = msg_text.get_rect(center=(self.width//2, 50))
    
                pygame.draw.rect(self.window, (40, 40, 80), 
                    (msg_rect.x - 10, msg_rect.y - 5, 
                     msg_rect.width + 20, msg_rect.height + 10))
                pygame.draw.rect(self.window, (80, 80, 150), 
                    (msg_rect.x - 10, msg_rect.y - 5, 
                     msg_rect.width + 20, msg_rect.height + 10), 2)
    
                self.window.blit(msg_text, msg_rect)
            
            if self.list_icon:
                self.window.blit(self.mv_img, self.mv_button_rect)
                self.window.blit(self.video_list_img, self.video_list_button_rect)  
                self.window.blit(self.list_icon, self.list_button_rect)
                self.window.blit(self.add_img, self.add_button_rect)
                self.window.blit(self.reset_img, self.reset_button_rect)
                self.window.blit(self.network_img, self.network_button_rect)
            
            if self.video_playing:
                if self.video_paused:
                    self.window.blit(self.play_img, self.play_button_rect)
                else:
                    self.window.blit(self.stop_img, self.play_button_rect)
            elif self.paused or not pygame.mixer.music.get_busy():
                self.window.blit(self.play_img, self.play_button_rect)
            else:
                self.window.blit(self.stop_img, self.play_button_rect)
            
            if self.current_mode == self.PLAY_MODE_NORMAL:
                self.window.blit(self.repeat_none_img, self.mode_button_rect)
            elif self.current_mode == self.PLAY_MODE_REPEAT_ONE:
                self.window.blit(self.repeat_one_img, self.mode_button_rect)
            else:  
                self.window.blit(self.repeat_all_img, self.mode_button_rect)
            
            prev_label = small_font.render("上一首", True, (200, 200, 255))
            play_label = small_font.render("播放/暂停", True, (200, 200, 255))
            next_label = small_font.render("下一首", True, (200, 200, 255))
            mode_label = small_font.render("播放模式", True, (200, 200, 255))
            list_label = small_font.render("选择播放", True, (200, 200, 255))
            add_label = small_font.render("添加文件", True, (200, 200, 255))
            reset_label = small_font.render("重新加载", True, (200, 200, 255))
            mv_label = small_font.render("播放MV", True, (200, 200, 255))
            video_list_label = small_font.render("视频列表", True, (200, 200, 255))  
            if self.current_speed == 1.0:
                speedd_label = font.render("倍速 ▼", True, (200, 200, 255))
            else:
                speedd_label = font.render(f"{self.current_speed}x ▼", True, (200, 200, 255))
            aaaa_label = small_font.render(self.out,True, (0, 255, 0))
            network_label = small_font.render("网络操作", True, (200, 200, 255))
            
            
            self.window.blit(prev_label, (self.prev_button_rect.centerx - prev_label.get_width()//2, self.prev_button_rect.bottom + 5))
            self.window.blit(play_label, (self.play_button_rect.centerx - play_label.get_width()//2, self.play_button_rect.bottom + 5))
            self.window.blit(next_label, (self.next_button_rect.centerx - next_label.get_width()//2, self.next_button_rect.bottom + 5))
            self.window.blit(mode_label, (self.mode_button_rect.centerx - mode_label.get_width()//2, self.mode_button_rect.bottom + 5))
            self.window.blit(list_label, (self.list_button_rect.centerx - list_label.get_width()//2, self.list_button_rect.bottom + 5))
            self.window.blit(add_label, (self.add_button_rect.centerx - add_label.get_width()//2, self.add_button_rect.bottom + 5))
            self.window.blit(reset_label, (self.reset_button_rect.centerx - reset_label.get_width()//2, self.reset_button_rect.bottom + 5))
            self.window.blit(mv_label, (self.mv_button_rect.centerx - mv_label.get_width()//2, self.mv_button_rect.bottom + 5))
            self.window.blit(aaaa_label,(300,260))
            self.window.blit(network_label, (self.network_button_rect.centerx - network_label.get_width()//2, 
                                           self.network_button_rect.bottom + 5))
            
            self.window.blit(video_list_label, (self.video_list_button_rect.centerx - video_list_label.get_width()//2, self.video_list_button_rect.bottom + 5))
            if self.aaaa:
                pygame.draw.rect(self.window, (200, 200, 200), (50, 300, self.progress_bar_width, self.progress_bar_height), 2)
                pygame.draw.rect(self.window,(0,255,0),(50,300,int(self.percent * (self.progress_bar_width / 100)),self.progress_bar_height))
                downloader_label = small_font.render(self.downloaded,True,(200,200,200))
                percent_label = small_font.render(f"{str(self.percent)}%",True,(255,0,0))
                sdsd_label = small_font.render(self.sdsd,True,(200,200,200))
                self.window.blit(downloader_label,(50,330))
                self.window.blit(percent_label,(500,305))
                self.window.blit(sdsd_label,(900,330))
                speed_label = small_font.render(self.speedd,True,(200,200,200))
                self.window.blit(speed_label,(500,330))
                
            
            if self.out != self.logout:
                self.log_message(self.out,"提示")
                self.out = self.logout
                
            if self.video_playing:
                self.window.blit(speedd_label, self.speed_button_rect)
            if cmd_input_active:
                cmd_text = f"> /{self.cmd_string}"
                cmd_label = font.render(cmd_text, True, (0, 255, 0))
                self.window.blit(cmd_label, (300, 190))
                prompt = small_font.render("命令模式: 输入命令后按Enter执行，Esc退出", True, (0, 200, 0))
                self.window.blit(prompt, (300, 220))
            
            controls_text = small_font.render("空格键: 暂停/播放  ←→: 上一首/下一首 /: 命令模式,输入/help打开帮助", True, (180, 180, 255))
            self.window.blit(controls_text, (50, 20))
            
            if len(self.playlist) == 0 and not self.video_playing:
                no_music = font.render("未找到音乐文件! 请点击'添加文件'或创建'music'文件夹并添加音乐", True, (255, 100, 100))
                self.window.blit(no_music, (50, self.height//2))
            
            pygame.display.flip()
            self.running = running
            self.cmd_input_active = cmd_input_active
            self.clock.tick(self.clock_tick)
        
        print("qasfgh")
        self.cleanup()
    
    

    
    def cleanup(self,s=True):
        # 断开服务器连接
        
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            pygame.quit()
            try:
                self.net_process.kill()
            except Exception as a:
                print(a)
                traceback.print_exc()
            if self.video_playing:
                self.stop_video(False)
            
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            if s:
                sys.exit(0)
        except Exception as e:
            messagebox.showerror(title="错误", message=f"清理资源时发生错误: {str(e)}")
            print(f"清理资源时发生错误: {str(e)}")
            traceback.print_exc()
            if s:
                sys.exit(1)
            

def main():
    annnn = MusicPlayer()
    while True:
        try:
            
            annnn.run()
        except Exception as a:
            messagebox.showerror(title="error",message=str(a))
            azx = messagebox.askretrycancel(title="error",message="是否重试")
            if azx:
                pass
            else:
                annnn.cleanup()
            traceback.print_exc()

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
        print(f"{a}\\config.ini")
        if os.path.exists(f"{a}\\config.ini"):
            self.config = configparser.ConfigParser()
            self.config.read(f'{a}\\config.ini')
            keys = self.config.options("host")
            for ggvg in keys:
                print(self.get(ggvg))
        else:
            print(os.path.abspath(f"{a}\\..\\..\\net\\config.ini"))
            if os.path.exists(f"{a}\\..\\..\\net\\config.ini"):
                self.config = configparser.ConfigParser()
                self.config.read(f'{a}\\..\\..\\net\\config.ini')
                keys = self.config.options("host")
                for ggvg in keys:
                    print(self.get(ggvg))
            else:
                messagebox.showerror("", "文件不存在")

    
    def get(self, key: str):
        try:
            print(self.config.sections())
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
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=host, port=port, username=username, password=password)
            self.sftp = self.ssh.open_sftp()
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
        self.current_path = self.rootdir
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
        self.path_var.set(self.get_display_path(self.current_path).replace(".1.2.3.trash","回收站"))
            
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
                if ext in ["",".thisfileisnull"] and not stat.S_ISDIR(file_attr.st_mode):
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

def netmain(ip="127.0.0.1", port=22, username="", password="", rootdir="/"):
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
    main()
    
    