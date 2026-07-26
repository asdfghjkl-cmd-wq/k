a = False
import os

try:
    try:
        import pymsgbox
    except ImportError as e:
        print(f"缺少依赖 pymsgbox，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install pymsgbox")
        import pymsgbox
    try:
        import pygame
    except ImportError as e:
        print(f"缺少依赖 pygame，正在安装...")
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
        print(f"缺少依赖 mutagen，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install mutagen")
        import mutagen
    try:
        import pyperclip
    except ImportError as e:
        print(f"缺少依赖 pyperclip，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install pyperclip")
        import pyperclip
    try:
        from bilibili_api import video
    except ImportError as e:
        print(f"缺少依赖 bilibili-api，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install bilibili-api")
        from bilibili_api import video
    try:
        os.environ['PYTHON_VLC_MODULE_PATH'] = f"./pvlc"
        import vlc
    except ImportError as e:
        print(f"缺少依赖 python-vlc，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install python-vlc")
        import vlc
    a = os.system("you-get")
    if a != 0:
        print(f"缺少依赖 you-get，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install you-get")
        a = os.system("you-get")
        if a != 0:
            print("无法安装 you-get，请手动安装后重试")
            exit(1)
    try:
        import aiohttp
    except ImportError as e:
        print(f"缺少依赖 aiohttp，正在安装...")
        os.system("pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple")
        os.system("pip install aiohttp")
        import aiohttp
except Exception as e:
    print(f"初始化依赖时出错: {str(e)},重试中")
    import traceback
    traceback.print_exc()
    os.system("pip install --upgrade setuptools wheel")
    os.system("python -m  pip install pymsgbox pygame mutagen pyperclip bilibili-api python-vlc aiohttp")


    
    a = open("restart.bat","w")
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
import json
import struct
import queue
import ssl
from functools import partial
import select
from multiprocessing import Process
import keyboard

#from net import net
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
