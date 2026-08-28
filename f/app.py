"""
文件上传服务 - 含大文件分卷上传（修复版）
修复内容：
1. 集成过期分卷会话清理，防止内存/磁盘泄漏（每5分钟清理一次）。
2. 使用绝对路径读取 HTML 模板，避免工作目录变更导致热重载失败。
3. 对大文件上传 API 增加必要的校验与错误处理。
4. 优化并发控制，避免进度计数异常（前端已建议修复，此处确保后端稳健）。
5. 引入 CSRF 保护（Flask-WTF）。
"""
#f



import subprocess

import psutil,ipaddress
import filelock
from file_rw import recv_file,send_file

def is_port_in_use(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN": # type: ignore
            return True
    return False

import hashlib
import atexit

from py7zr import SevenZipFile
from markupsafe import escape

import zipfile, requests,pyzipper
import shlex
from threading import Thread,Event
from queue import Queue
from urllib.parse import urlparse
import logging
import select
import socket
import struct
from string import ascii_lowercase, ascii_letters
from flask import (Flask, request, jsonify, render_template_string,
                   make_response, send_from_directory, session, redirect, url_for, abort)
import random
from flask_cors import CORS
import os, sys, json, traceback, shutil, re, uuid, time
from datetime import datetime
from urllib.parse import quote
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_wtf.csrf import CSRFProtect, CSRFError
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
# 禁用不安全的请求警告（针对 verify=False）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import redis


# 从环境变量读取 Redis 地址，方便部署
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
REDIS_PASSWORD  = os.environ.get('REDIS_PASSWORD', None)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD,decode_responses=True)
try:
    print(r.info('server')['redis_version'],flush=True)
except Exception as e:
    print(f"[FATAL] Redis 连接失败: {e}", flush=True)
    raise SystemExit(f"Redis 连接失败: {e}")
class qe(BaseException):
    pass

def contains_chinese(text):
   for ch in text:
       if u'\u4e00' <= ch <= u'\u9fff':
           return True
   return False


def get_filename_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')[-1]



class tool:
    class u1:
        @staticmethod
        def call(source_path,chunk_size,output_dir,task_id,cancel_check):
            if os.path.exists(output_dir):
                if os.path.isdir(output_dir):
                        shutil.rmtree(output_dir)
                else:
                    os.remove(output_dir)  # 如果是同名文件则删除
            os.makedirs(output_dir)

            file_count = 0
            with open(source_path, "rb") as src:
                while True:
                    if cancel_check():
                        shutil.rmtree(output_dir)
                        raise qe("cancel")
                    data = src.read(chunk_size)
                    if not data:
                        break
                    file_count += 1

                    # 4位编号便于排序
                    out_name = os.path.join(output_dir, f"{file_count:04d}.data")
                    with  open(out_name, "wb") as chunk:
                        chunk.write(data)

    # 写入元信息
            meta_path = os.path.join(output_dir, "file")
            with open(meta_path, "w", encoding="utf-8") as meta:
                meta.write(f"{os.path.basename(source_path)}\n")
                meta.write(f"{file_count}\n")
                meta.write(f"{chunk_size}\n")
            return True


    class u2:
        def call(dir,tdir,task_id,cancel_check):
            with open(os.path.join(dir,"file"),"r",encoding="utf-8") as fmeta:
                n = os.path.basename(fmeta.readline().rstrip("\n"))
                x = int(fmeta.readline().rstrip("\n"))
            with open(os.path.join(tdir,n),"wb") as bn:
                for nb in range(1,x+1):
                    if cancel_check():
                        os.remove(bn.name)
                        raise qe("cancel")
                    with open(os.path.join(dir,f"{nb:04d}.data"),"rb") as an:
                        bn.write(an.read())
            return True

# ==================== 异步任务系统 ====================


MAX_WORKERS = 3
task_queue = Queue()
def save_user():
    """将用户数据存入 Redis"""
    # 存储密码哈希
    if users:
        r.hset("users", mapping=users)   # type: ignore # {"username": "hash"}
    # 存储用户列表
    r.delete("user_list")
    if user_list:
        r.sadd("user_list", *user_list) # type: ignore
    # 存储黑名单
    r.delete("blocked_users")
    if blocked_users:
        r.sadd("blocked_users", *blocked_users)
    # 存储管理员
    r.set("admin", admin) # type: ignore
    print('save ok', flush=True)

def load_user():
    """从 Redis 加载用户数据"""
    global users, user_list, blocked_users, admin

    # 一次性迁移旧黑名单 key（旧 key 为 nigga_list）
    if r.exists("nigga_list"):
        old = list(r.smembers("nigga_list"))
        if old:
            r.sadd("blocked_users", *old)
        r.delete("nigga_list")

    # 默认管理员（环境变量）
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', os.environ.get('a', None))
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', os.environ.get('p', None))
    ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD) if ADMIN_PASSWORD else None

    # 尝试从 Redis 读取
    redis_users = r.hgetall("users")
    redis_user_list = list(r.smembers("user_list"))
    redis_blocked_users = list(r.smembers("blocked_users"))
    redis_admin = r.get("admin")

    # 如果 Redis 中有数据就用 Redis 的
    if redis_users:
        users = redis_users
        user_list = redis_user_list
        blocked_users = redis_blocked_users
        admin = redis_admin if redis_admin else ADMIN_USERNAME
    else:
        # 首次运行，用环境变量初始化
        # 未配置管理员密码时不要写入 None 哈希，避免后续 check_password_hash 崩溃
        users = {ADMIN_USERNAME: ADMIN_PASSWORD_HASH} if (ADMIN_USERNAME and ADMIN_PASSWORD_HASH) else {}
        user_list = [ADMIN_USERNAME] if ADMIN_USERNAME else []
        blocked_users = []
        admin = ADMIN_USERNAME
        save_user()  # 写入 Redis

    return users, user_list, blocked_users, admin

# ==================== 工具 ID 常量 ====================
TOOL_CUT = 1        # 分割文件
TOOL_ASSEMBLY = 2   # 合成文件
TOOL_INFO = 3       # 使用说明（无任务）
TOOL_UNZIP = 4      # 解压
TOOL_DOWNLOAD = 6   # URL 下载
TOOL_COPY = 50      # 复制
TOOL_MOVE = 51      # 移动
TOOL_HASH = 64      # 计算哈希
# 可取消任务的工具集合
tool_list = {TOOL_CUT, TOOL_ASSEMBLY, TOOL_UNZIP, TOOL_DOWNLOAD, TOOL_COPY, TOOL_MOVE, TOOL_HASH}

def worker():
    while True:
        task_id, func, base_args, tool_id = task_queue.get()
        if task_id is None:
            break
        # 更新状态为 running
        r.hset(task_key(task_id), 'status', 'running')

        try:
            a = True
            with app.app_context():
                if tool_id in tool_list:
                    r.hset(task_key(task_id), 'can_cancel', 'True')
                    a = False
                    if tool_id == TOOL_HASH:
                        a, n = func(*base_args, task_id=task_id,
                                    cancel_check=lambda: is_cancelled(task_id))
                    else:
                        a = func(*base_args, task_id=task_id,
                                 cancel_check=lambda: is_cancelled(task_id))
                else:
                    r.hset(task_key(task_id), 'can_cancel', 'False')
                    func(*base_args)

            if a and tool_id == TOOL_HASH:
                r.hset(task_key(task_id), 'status', 'finished')
                r.hset(task_key(task_id), 'return', n)
            elif a:
                r.hset(task_key(task_id), 'status', 'finished')
            else:
                r.hset(task_key(task_id), 'status', 'failed')
                t = get_task(task_id)
                if not t or t.get('error') == '':
                    r.hset(task_key(task_id), 'error', 'unkown')

        except Exception as e:
            traceback.print_exc()
            if is_cancelled(task_id):
                r.hset(task_key(task_id), 'status', 'cancelled')
            else:
                r.hset(task_key(task_id), 'status', 'failed')
                r.hset(task_key(task_id), 'error', str(e))
        except qe:
            if is_cancelled(task_id):
                r.hset(task_key(task_id), 'status', 'cancelled')
        finally:
            if is_cancelled(task_id):
                r.hset(task_key(task_id), 'status', 'cancelled')
                r.hset(task_key(task_id), 'error', 'User cancelled')
            else:
                # 保持原有的 failed/finished 逻辑
                pass
            task_queue.task_done()

for _ in range(MAX_WORKERS):
    t = Thread(target=worker, daemon=True)
    t.start()

# ==================== 初始化 ====================
if sys.platform.startswith('win'):
    import io, locale
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    try: locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except: pass

def ran_str(length, charset=ascii_lowercase+'0123456789'):
    return ''.join(random.choice(charset) for _ in range(length))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'a.html')
TRASH_DIR = os.path.join(BASE_DIR,'trash')
if not os.path.exists(TRASH_DIR):
    os.makedirs(TRASH_DIR)
try:
    with open(os.path.join(BASE_DIR, "s.key"), "r", encoding="utf-8") as s:
        k = s.read()
except:
    k = ran_str(128, ascii_letters)
    with open(os.path.join(BASE_DIR, "s.key"), "w", encoding="utf-8") as s:
        s.write(k)
# 日志文件（不再在启动时截断，保留历史日志）
LOG_FILE = os.path.join(BASE_DIR, "app.log")
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_FILE,
    encoding="utf-8"
)



app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://127.0.0.1:5000",
            "https://127.0.0.1:5000",
            r"https?://.*\.goodlink\.website"
        ]
    }
}, supports_credentials=True)
app.config.update(
    MAX_CONTENT_LENGTH=1024 * 1024 * 1024,
    UPLOAD_FOLDER=os.path.join(BASE_DIR, 'uploads'),
    SECRET_KEY=os.environ.get('SECRET_KEY', k),
    JSON_AS_ASCII=False,SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_HTTPONLY=True
)
if __name__ != '__main__':
    app.config.update(
        SESSION_COOKIE_SECURE=True)

csrf = CSRFProtect(app)

logging.info("flask create ok")

UPLOAD_DIR = os.path.abspath(app.config['UPLOAD_FOLDER'])
META_DIR = os.path.join(UPLOAD_DIR, 'metadata')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)


# 任务数据用 Hash 存储，键为 task:<task_id>
TASK_PREFIX = "task:"

def task_key(task_id):
    return TASK_PREFIX + task_id

def save_task(task_id, data):
    """保存任务到 Redis（初始化或更新）"""
    key = task_key(task_id)
    # 需要序列化嵌套结构
    safe = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            safe[k] = json.dumps(v)
        else:
            safe[k] = str(v)
    r.hset(key, mapping=safe)
    # 任务 7 天无更新自动过期，防止无限累积
    r.expire(key, 7 * 24 * 3600)

def get_task(task_id):
    """从 Redis 读取任务，并反序列化"""
    key = task_key(task_id)
    if not r.exists(key):
        return None
    raw = r.hgetall(key)
    # 把已知的 JSON 字段反序列化
    if 'progress' in raw:
        try:
            raw['progress'] = json.loads(raw['progress'])
        except:
            pass
    if 'file_info' in raw:
        try:
            raw['file_info'] = json.loads(raw['file_info'])
        except:
            pass
    # cancel_flag 转 int
    raw['cancel_flag'] = int(raw.get('cancel_flag', 0))
    return raw

def delete_task(task_id):
    r.delete(task_key(task_id))

def is_cancelled(task_id):
    """任务执行中检查是否被取消"""
    flag = r.hget(task_key(task_id), 'cancel_flag')
    return flag == '1'

def cancel_task_by_id(task_id):
    """设置取消标记"""
    if not r.exists(task_key(task_id)):
        return False
    status = r.hget(task_key(task_id), 'status')
    if status not in ('running', 'pending'):
        return False
    r.hset(task_key(task_id), 'cancel_flag', '1')
    return True

def load_redis():
    global user_list,users,blocked_users,admin
    while True:
        time.sleep(10)
        redis_users = r.hgetall("users")
        redis_user_list = list(r.smembers("user_list"))
        redis_blocked_users = list(r.smembers("blocked_users"))
        redis_admin = r.get("admin")
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', os.environ.get('a', None))
        if redis_users:
            users = redis_users
            user_list = redis_user_list
            blocked_users = redis_blocked_users
            admin = redis_admin if redis_admin else ADMIN_USERNAME

def update_task_progress(task_id, total=None, current=None):
    """更新任务进度（下载等场景）"""
    key = task_key(task_id)
    progress_str = r.hget(key, 'progress')
    if progress_str:
        progress = json.loads(progress_str)
    else:
        progress = {'total': 0, 'current': 0}
    if total is not None:
        progress['total'] = total
    if current is not None:
        progress['current'] = current
    r.hset(key, 'progress', json.dumps(progress))

users,user_list,blocked_users,admin = load_user()
annn = Thread(target=load_redis,daemon=True)
annn.start()
# ==================== 全局 HTML 模板 ====================
HTML_TEMPLATE = ""

def get_hash(path,task_id,cancel_check):
    task_id = task_id
    n = hashlib.sha256()
    with open(path,'rb') as b:
        for chunk in iter(lambda: b.read(1024*1024*10), b''):
            n.update(chunk)
            if cancel_check():
                raise qe("cancel")

    return True,str(n.hexdigest())



def load_html():
    global HTML_TEMPLATE
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            HTML_TEMPLATE = f.read()
        if app.debug:
            HTML_TEMPLATE += "<br/>\n<a href=\"/api/new\">new</a>"
    except Exception as e:
        print(f"[WARN] 无法加载模板 {HTML_FILE}: {e}")
        HTML_TEMPLATE = "<h1>模板加载失败，请联系管理员</h1>"

load_html()
logging.info("html load ok")

# ==================== 后台线程 ====================
def background_tasks():
    global HTML_TEMPLATE
    while True:
        time.sleep(300)
        try:
            with open(HTML_FILE, "r", encoding="utf-8") as f:
                new_tpl = f.read()
            if HTML_TEMPLATE != new_tpl:
                HTML_TEMPLATE = new_tpl
                HTML_TEMPLATE += "<br/>\n<a href=\"/api/new\">new</a>"
                print("[INFO] 模板已热重载")
        except Exception as e:
            print(f"[WARN] 模板重载异常: {e}")

if not app.debug:
    bg_thread = Thread(target=background_tasks, daemon=True)
    bg_thread.start()

# ==================== 工具函数 ====================
def _is_api_request():
    return (request.is_json or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.path.startswith('/api/'))

def _reject(msg, status=403):
    if _is_api_request():
        return jsonify({'success': False, 'error': msg}), status
    return msg, status

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session or session.get('user_id') not in list(users.keys()):
            if _is_api_request():
                return jsonify({'success': False, 'error': '请先登录'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return wrap

def is_allowed(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        for aaa in blocked_users:
            if session.get('user_id') == aaa:
                return _reject('no admin', 403)
        return f(*args, **kwargs)
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('user_id') == admin:
            return f(*args, **kwargs)
        return _reject('no admin', 403)
    return wrap


def safe_path(*parts):
    # 无参数或仅传入 '.'/'' 时，直接返回上传根目录
    if not parts or (len(parts) == 1 and parts[0] in ('.', '')):
        return UPLOAD_DIR

    target = os.path.realpath(os.path.abspath(os.path.join(UPLOAD_DIR, *parts)))
    upload_abs = os.path.realpath(UPLOAD_DIR)
    # normcase 处理 Windows 大小写不敏感；os.sep 边界比较防 uploads_evil 之类前缀绕过
    if os.path.normcase(target) == os.path.normcase(upload_abs):
        return target
    if os.path.normcase(target).startswith(os.path.normcase(upload_abs) + os.sep):
        return target
    raise ValueError("路径越权")

def clean_filename(filename):
    if not filename: return "未命名文件"
    if isinstance(filename, bytes):
        try: filename = filename.decode('utf-8')
        except:
            try: filename = filename.decode('gbk')
            except: filename = filename.decode('latin-1')
    name, ext = os.path.splitext(filename)
    illegal = r'[\\/*?:"<>|]'
    name = re.sub(illegal, '', name).strip('. ')
    ext = ext.lstrip('.')
    if not name and not ext: return "未命名文件"
    if not name: return f"未命名文件.{ext}"
    if not ext: return name
    return f"{name}.{ext}"

def unique_name(filename, folder):
    path = os.path.join(folder, filename)
    if not os.path.exists(path): return filename
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_name = f"{name} ({counter}){ext}"
        if not os.path.exists(os.path.join(folder, new_name)):
            return new_name
        counter += 1
        if counter > 1000:
            ts = int(time.time() * 1000) % 1000000
            return f"{name}_{ts}{ext}"

def get_file_info(path):
    try:
        stat = os.stat(path)
        return {'size': stat.st_size, 'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
    except: return None

def save_meta(rel_path, original_name, size):
    meta_base = META_DIR
    rel_dir = os.path.dirname(rel_path)
    if rel_dir:
        meta_dir = os.path.join(meta_base, rel_dir)
    else:
        meta_dir = meta_base
    os.makedirs(meta_dir, exist_ok=True)
    meta_file = os.path.join(meta_dir, os.path.basename(rel_path) + '.json')
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump({
            'original_name': original_name,
            'relative_path': rel_path,
            'size': size,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)

def get_meta_path(rel_path):
    meta_base = META_DIR
    rel_dir = os.path.dirname(rel_path)
    if rel_dir:
        meta_dir = os.path.join(meta_base, rel_dir)
    else:
        meta_dir = meta_base
    return os.path.join(meta_dir, os.path.basename(rel_path) + '.json')

def sze(file,od,password,task_id):
    zp = safe_path(file)
    if not os.path.isfile(zp):
        raise FileNotFoundError(f"not found:{zp}")
    basename = str(os.path.basename(zp))
    a,b = os.path.splitext(basename)
    if not  a:
        a= "extracted"
    target_base = os.path.join(od,a)
    target_dir = target_base
    counter = 1
    while os.path.exists(target_dir):
        target_dir = f"{target_base} ({counter})"
        counter += 1
        if counter > 1000:
            ts = int(time.time() * 1000) % 1000000
            target_dir = f"{target_base}_{ts}"
            break
    target_dir = os.path.realpath(target_dir)
    # 最终检查确保解压目录仍位于 UPLOAD_DIR 下
    if not target_dir.startswith(os.path.realpath(UPLOAD_DIR) + os.sep) and target_dir != os.path.realpath(UPLOAD_DIR):
        raise ValueError("解压目标路径越权")
    os.makedirs(target_dir, exist_ok=True)
    try:
        sece(zp,target_dir,file,password,task_id)
        return True,target_dir
    except Exception as e:
        app.logger.error(f"解压失败: {e}")
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)
        return False,target_dir



def _extract_loop(zf, members, target_dir, task_id, max_total=50 * 1024**3, max_entries=100000):
    """统一的解压循环：取消检查 + Zip Slip 校验 + 进度更新 + 防解压炸弹上限"""
    total = len(members)
    if total > max_entries:
        raise Exception("解压条目数超限")
    acc = 0
    for idx, member in enumerate(members):
        # 每次解压一个文件前检查取消
        if is_cancelled(task_id):  # 直接使用 Redis 检查，因为此处拿不到 cancel_check 闭包
            # 清理已解压的部分
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=True)
            raise qe("解压被取消")
        name = member.filename
        # 防 Zip Slip 检查
        member_path = os.path.realpath(os.path.join(target_dir, name))
        if not member_path.startswith(target_dir + os.sep) and member_path != target_dir:
            raise Exception(f"Zip Slip 攻击检测: {name}")
        # 累计解压体积上限（防解压炸弹），file_size 兼容 zipfile/pyzipper，uncompressed 兼容 py7zr
        size = getattr(member, 'file_size', None) or getattr(member, 'uncompressed', None) or 0
        acc += size
        if acc > max_total:
            raise Exception("解压总大小超限")
        # 提取单个文件
        zf.extract(member, target_dir)
        # 更新任务进度
        update_task_progress(task_id, total=total, current=idx+1)
    return total

def sece(zp,target_dir,file,password,task_id):
    try:
        with SevenZipFile(zp,mode="r",password=password) as zf:
            _extract_loop(zf, zf.list(), target_dir, task_id)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        save_task(task_id, {'error': str(e)})
        raise e
        




def zipe(file: str, dir,password,task_id):
    """解压 ZIP 文件，并防止 Zip Slip 攻击"""
    zip_path = safe_path(file)
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"文件不存在: {file}")
    basename = os.path.basename(zip_path)
    if basename.lower().endswith('.zip'):
        dir_name = basename[:-4]
    else:
        dir_name = basename
    if not dir_name:
        dir_name = "extracted"
    # dir 已经是 safe_path 的结果，保证在 UPLOAD_DIR 内
    target_base = os.path.join(dir, dir_name)
    target_dir = target_base
    counter = 1
    while os.path.exists(target_dir):
        target_dir = f"{target_base} ({counter})"
        counter += 1
        if counter > 1000:
            ts = int(time.time() * 1000) % 1000000
            target_dir = f"{target_base}_{ts}"
            break
    target_dir = os.path.realpath(target_dir)
    # 最终检查确保解压目录仍位于 UPLOAD_DIR 下
    if not target_dir.startswith(os.path.realpath(UPLOAD_DIR) + os.sep) and target_dir != os.path.realpath(UPLOAD_DIR):
        raise ValueError("解压目标路径越权")
    os.makedirs(target_dir, exist_ok=True)
    try:
        if password == "":
            zce(zip_path,target_dir,file,task_id)
        else:zece(zip_path,target_dir,file,password.encode(),task_id)
        return True
    except Exception as e:
        app.logger.error(f"解压失败: {e}")
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)
        raise e

def zce(zip_path, target_dir, file, task_id):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            _extract_loop(zf, zf.infolist(), target_dir, task_id)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        save_task(task_id, {'error': str(e)})
        raise e

def zece(zip_path,target_dir,file,password,task_id):
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            zf.setpassword(password)
            _extract_loop(zf, zf.infolist(), target_dir, task_id)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        save_task(task_id, {'error': str(e)})
        raise e

def _is_blocked_ip(ip_str):
    """SSRF 防护：判断 IP 是否为内网/回环/链路本地/保留/组播等禁止访问的地址"""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return (addr.is_private or addr.is_loopback or addr.is_link_local
            or addr.is_reserved or addr.is_multicast or addr.is_unspecified)

def download(url, dir, task_id, cancel_check):
    filepath = None
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError(f"不支持的协议: {parsed.scheme}")
        host = parsed.hostname
        if not host:
            raise ValueError("URL 缺少主机名")
        # SSRF 防护：拒绝解析到内网/私网/回环地址
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror:
            raise ValueError(f"无法解析主机: {host}")
        if any(_is_blocked_ip(info[4][0]) for info in infos):
            raise ValueError(f"禁止下载内网/私网地址: {host}")
        filename = clean_filename(get_filename_from_url(url))
        filepath = os.path.join(UPLOAD_DIR, dir, filename)
        last_cancel_check = time.time()
        last_progress_update = time.time()
        with requests.Session() as s:
            s.max_redirects = 5  # 限制重定向次数
            resp = s.get(url, stream=True, timeout=(10, 30), verify=False)
            resp.raise_for_status()
            total = int(resp.headers.get('content-length', 0))
            update_task_progress(task_id, total=total, current=0)

            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    now = time.time()
                    # 取消检查节流：每 0.2 秒一次，避免每 8KB 一次高频 Redis 请求
                    if now - last_cancel_check >= 0.2:
                        last_cancel_check = now
                        if cancel_check():
                            resp.close()
                            raise Exception("下载被取消")
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 进度更新节流：每 0.5 秒一次
                        if now - last_progress_update >= 0.5:
                            update_task_progress(task_id, current=downloaded)
                            last_progress_update = now
                # 收尾时更新最终进度
                update_task_progress(task_id, current=downloaded)
        return True
    except Exception as e:
        logging.error(f"下载错误: {e}")
        save_task(task_id,{'error':str(e)})
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        raise

# ==================== 模板 ====================
LOGIN_TEMPLATE = '''
<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><title>登录</title>
<style>body{font-family:sans-serif;background:#f5f5f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.login{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);width:320px}
h2{margin-bottom:20px;color:#2c3e50;text-align:center}
input{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:4px}
button{width:100%;padding:10px;background:#3498db;color:#fff;border:none;border-radius:4px;cursor:pointer}
.error{background:#f8d7da;color:#721c24;padding:10px;border-radius:4px;margin-bottom:15px}
.info{margin-top:15px;text-align:center;color:#666;font-size:13px}</style></head>
<body><div class="login"><h2>登录</h2>{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="post">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<input name="username" placeholder="用户名" required autofocus>
<input type="password" name="password" placeholder="密码" required>
<button type="submit">登录</button></form>
</body></html>
'''


# ==================== 路由 ====================
def _safe_next(target):
    """防止开放重定向：只允许站内相对路径"""
    if target and target.startswith('/') and not target.startswith('//'):
        return target
    return url_for('index')

@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.info(f"user logining.from {request.remote_addr}")
    error = None
    if request.method == 'POST':
        ip = request.remote_addr or 'unknown'
        fail_key = f'login_fail:{ip}'
        if int(r.get(fail_key) or 0) >= 5:
            error = '尝试次数过多，请10分钟后再试'
            return render_template_string(LOGIN_TEMPLATE, error=error)
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username in users and users[username] and check_password_hash(users[username], password):
            session['user_id'] = username
            r.delete(fail_key)
            return redirect(_safe_next(request.args.get('next')))
        error = '用户名或密码错误'
        r.incr(fail_key)
        r.expire(fail_key, 600)
        logging.warning(f"user login failure.from {request.remote_addr} user:{username}")
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    logging.info("user logout")
    return redirect(url_for('login'))

@app.route("/api/loginok")
def loginok():
    name = ""
    lo = False
    la =False
    if "user_id" in session:
        lo = True
        name = session.get("user_id")
        la = True
        for sa in blocked_users:
            if session.get("user_id") == sa:
                la = False
    return jsonify({"login":lo,"admin":la,"name":name})

@app.route('/check')
def admin_or_no_user():
    if 'user_id' not in session or session.get('user_id') not in list(users.keys()):return 'Non-user',401
    else:
        if session.get('user_id') == admin:
            return 'admin',200
        else:return 'user',403

@app.route("/api/gdl")
@login_required
@is_allowed
def get_download_list():
    keys = r.scan_iter(match=f"{TASK_PREFIX}*")
    running_downloads = []
    for key in keys:
        if isinstance(key, bytes):
            tid = key.decode().split(':', 1)[-1]
        else:
            tid = key.split(':', 1)[-1]
        tool_id = r.hget(key, 'tool_id')
        status = r.hget(key, 'status')
        if tool_id and status and str(tool_id) == str(TOOL_DOWNLOAD) and status == 'running':
            running_downloads.append(tid)
    return jsonify(running_downloads), 200
            
@app.route("/api/dl")
@login_required
@is_allowed
def get_task_list_all():
    # 获取 Redis 中所有任务
    keys = r.scan_iter(match=f"{TASK_PREFIX}*")
    tasks = {}
    allowed_types = (str, int, float, bool, list, dict)
    for key in keys:
        # key 格式为 task:uuid
        if isinstance(key, bytes):
            tid = key.decode().split(':', 1)[-1]
        else:
            tid = key.split(':', 1)[-1]
        task = get_task(tid)  # 已经反序列化 progress/file_info
        if task:
            # 过滤不可序列化字段，保持与原 /api/dl 一致
            filtered = {}
            for k, v in task.items():
                if isinstance(v, allowed_types) or v is None:
                    filtered[k] = v
            tasks[tid] = filtered
    return jsonify(tasks)

@app.route('/file/hash',methods=['POST'])
@login_required
@is_allowed
def call_hash():
    a = request.json
    try:
        ah = a.get('path',"")
        sp = safe_path(ah)
        
    except Exception as d:
        logging.error(str(d))
        n = jsonify({'success':False})
        n.status_code = 400
        return n
    func = get_hash

    task_id = str(uuid.uuid4())
    tool_id = TOOL_HASH
    
    save_task(task_id,{
                'status': 'pending',
                'error': '',
                'tool_id': tool_id,
                'progress': {'total': 0, 'current': 0},
                'file_info':{'src':sp},
                'path': os.path.dirname(os.path.abspath(sp))
            })
    arg_list = (sp,)
    task_queue.put((task_id, func, arg_list, tool_id))
    return jsonify({'success':True,'task_id':task_id})
    




@app.route('/')
@login_required
def index():

    return render_template_string(HTML_TEMPLATE, username=session.get('user_id',''))

@app.route('/api/task/<task_id>', methods=['GET'])
@is_allowed
@login_required
def get_task_status(task_id):

    task = get_task(task_id)
    if not task:
        return jsonify({'success': False, 'error': '无效任务ID'}), 404

    a = {}
    # 注意：bytes/bytearray 无法被 jsonify 序列化，会直接 500
    n = [str, int, list, dict, bool, float]
    for aa,x in task.items():
        if type(x) in n:
            a[aa] = x
    a['success'] =True

    return jsonify(a)


@app.route('/api/task/<task_id>/cancel', methods=['POST', 'GET'])
@login_required
@is_allowed
def cancel_task(task_id):
    success = cancel_task_by_id(task_id)
    if not success:
        task = get_task(task_id)
        if not task:
            return jsonify({'success': False, 'error': '无效任务ID'}), 404
        return jsonify({'success': False, 'error': '任务无法取消'}), 400
    return jsonify({'success': True})

@app.route('/api/task/<task_id>/delete', methods=['POST', 'GET'])
@login_required
@is_allowed
def webdelete_task(task_id):
    task = get_task(task_id)          # 直接获取任务对象
    if not task:
        return jsonify({'success': False, 'error': '无效任务ID'}), 404
    status = task.get('status', '')
    if status == 'running':
        return jsonify({'success': False, 'error': '任务正在运行，无法删除'}), 403
    elif status == 'pending':
        return jsonify({'success': False, 'error': '任务仍在队列中，无法删除'}), 403
    else:
        delete_task(task_id)
        return jsonify({'success': True})
    

@app.route("/file/move", methods=['POST'])
@is_allowed
@login_required
def call_move():
    try:
        data = request.get_json()
        if not data:
            abort(400)
        source = data["source"]
        target = data["target"]
    
    except (KeyError, TypeError):
        abort(400)
    func = move_file

    task_id = str(uuid.uuid4())
    tool_id = TOOL_MOVE

    save_task(task_id,{
            'status': 'pending',
            'error': '',
            'tool_id': tool_id,
            'progress': {'total': 0, 'current': 0},

            'file_info':{'src':source,'dst':resolve_target_path(safe_path(source), target)},
            'path': os.path.dirname(os.path.abspath(source))
        })
    arg_list = (source,target)
    task_queue.put((task_id, func, arg_list, tool_id))
    return jsonify({'success':True,'task_id':task_id})

def move_file(source, target, task_id, cancel_check):
    try:
        src = safe_path(source)
        dst = resolve_target_path(src, target)
    except ValueError as e:
        save_task(task_id, {'error': str(e)})
        return False
    # 先复制
    if copy_file(source, target, task_id, cancel_check):
        # 复制成功且未被取消，删除源
        if os.path.isdir(src):
            shutil.rmtree(src)
        else:
            os.remove(src)
        return True
    return False

        
@app.route("/file/copy", methods=['POST'])
@is_allowed
@login_required
def call_copy():
    try:
        data = request.get_json()
        if not data:
            abort(400)
        source = data["source"]
        target = data["target"]
    
    except (KeyError, TypeError):
        abort(400)
    func = copy_file

    task_id = str(uuid.uuid4())
    tool_id = TOOL_COPY

    save_task(task_id,{
            'status': 'pending',
            'error': '',
            'tool_id': tool_id,
            'progress': {'total': 0, 'current': 0},

            'file_info':{'src':source,'dst':target},
            'path': os.path.dirname(os.path.abspath(source))
        })
    arg_list = (source,target)
    task_queue.put((task_id, func, arg_list, tool_id))
    return jsonify({'success':True,'task_id':task_id})




def copy_file(source, target, task_id, cancel_check):
    try:
        src = safe_path(source)
        dst = resolve_target_path(src, target)
    except ValueError as e:
        save_task(task_id, {'error': str(e)})
        return False

    if not os.path.exists(src):
        save_task(task_id, {'error': '源路径不存在'})
        return False

    try:
        if os.path.isfile(src):
            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            # 使用分块复制，每复制 1MB 检查一次取消
            with open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
                while True:
                    if cancel_check():
                        # 取消时删除未完成的目标文件
                        if os.path.exists(dst):
                            os.remove(dst)
                        raise qe("复制被取消")
                    chunk = f_in.read(1024 * 1024)  # 1MB 块
                    if not chunk:
                        break
                    f_out.write(chunk)
        elif os.path.isdir(src):
            # 递归复制目录（同样需要分块复制每个文件）
            # 简单起见，可以调用 shutil.copytree，但无法取消。
            # 更优方案：遍历目录树，对每个文件执行上面的分块复制逻辑，并频繁检查取消。
            # 此处给出一层简易递归实现：
            for root, dirs, files in os.walk(src):
                if cancel_check():
                    # 清理已复制的内容
                    if os.path.exists(dst):
                        shutil.rmtree(dst, ignore_errors=True)
                    raise qe("复制被取消")
                rel_path = os.path.relpath(root, src)
                dest_root = os.path.join(dst, rel_path)
                os.makedirs(dest_root, exist_ok=True)
                for file in files:
                    if cancel_check():
                        if os.path.exists(dst):
                            shutil.rmtree(dst, ignore_errors=True)
                        raise qe("复制被取消")
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_root, file)
                    # 再次调用分块复制逻辑（或封装为内部函数）
                    # 为了简洁，这里简化为 shutil.copy2，实际上应替换为分块循环
                    with open(src_file, 'rb') as f_in, open(dst_file, 'wb') as f_out:
                        while True:
                            if cancel_check():
                                if os.path.exists(dst):
                                    shutil.rmtree(dst, ignore_errors=True)
                                raise qe("复制被取消")
                            chunk = f_in.read(1024 * 1024)
                            if not chunk:
                                break
                            f_out.write(chunk)
        else:
            save_task(task_id, {'error': '源路径类型未知'})
            return False
        return True
    except Exception as e:
        traceback.print_exc()
        save_task(task_id, {'error': str(e)})
        return False

    
@app.route('/file/zipex',methods=['POST'])
@login_required
@is_allowed
def call_ze():
    a = dict(request.json)
    
    try:
        f = a['path']
        user_dir = a.get('outpath', '')
        if user_dir == "":
            user_dir = os.path.dirname(safe_path(f))
        password = a.get('password','')
    
        sp = resolve_target_path(f,user_dir)
    except Exception as e:
        logging.error(str(e))
        abort(400)
    func = zip_ex

    task_id = str(uuid.uuid4())
    tool_id = TOOL_UNZIP
    save_task(task_id, {
                'status': 'pending',
                'error': '',
                'tool_id': tool_id,
                'progress': {'total': 0, 'current': 0},
                                                'file_info':{'src':f,'dst':sp},
                'path': os.path.dirname(os.path.abspath(f))
            })
    arg_list = (f,sp,password)
    task_queue.put((task_id, func, arg_list, tool_id))
    return jsonify({'success':True,'task_id':task_id})
    

def zip_ex(f,sp,password,task_id,cancel_check):
   


    f =safe_path(f)
    if not os.path.exists(f):
        
        return False
    

    _,n = os.path.splitext(f)
    try:
        if n == ".zip":
            a = zipe(f,sp,password,task_id)
        elif n == '.7z':
            a = sze(f,sp,password,task_id)

        else:
            save_task(task_id,{'error':'not found'})
            return False
        if not a:
            task = get_task(task_id)
            if not task or task.get('error') == '':
                save_task(task_id, {'error': 'error'})
            return False

        return True
    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))
        save_task(task_id,{'error':e})
        return False


def resolve_target_path(src_abs: str, target: str) -> str:
    """
    将目标路径 target 解析为绝对路径。
    如果 target 是相对路径，则相对于 src_abs 的目录解析；
    如果 target 是绝对路径，则直接使用（但会检查是否在 UPLOAD_DIR 内）。
    """
    if not target:
        raise ValueError("目标路径不能为空")
    src_dir = os.path.dirname(src_abs)
    if os.path.isabs(target):
        target_abs = os.path.abspath(target)
    else:
        target_abs = os.path.abspath(os.path.join(src_dir, target))
    
    upload_abs:str = os.path.abspath(UPLOAD_DIR)
    target_abs = os.path.realpath(target_abs)
    upload_abs = os.path.realpath(upload_abs)
    # normcase + os.sep 边界比较，防前缀绕过与大小写绕过
    if os.path.normcase(target_abs) == os.path.normcase(upload_abs):
        return target_abs
    if os.path.normcase(target_abs).startswith(os.path.normcase(upload_abs) + os.sep):
        return target_abs
    raise ValueError(f"目标路径越权;{target_abs};{upload_abs};{sys.platform}")


@app.route('/api/disk_usage')
@is_allowed
@login_required
def get_du():
    a,b,c = shutil.disk_usage(UPLOAD_DIR)
    return jsonify({'total':a,"used":b,"free":c})


@app.route("/api/toolcall", methods=['POST'])
@is_allowed
@login_required
def call_tool():
    
    try:
        a = request.json
        a=dict(a)
        logging.info(f"call_tool {a}")
        tool_id = a.get("tool")
        args_raw = a.get("args", "").strip()



        def clean_arg(s):
            s = s.replace('\\', '/').strip().strip("'\"")
            if s.lower().startswith('uploads/'):
                s = s[len('uploads/'):]
            elif s.lower() == 'uploads':
                s = ''
            if s == '.':
                s = ''
            return s

        clean = clean_arg(args_raw)

        user_dir = a.get('path', '')
        
        safe_dir = safe_path(user_dir) if user_dir else UPLOAD_DIR
        if tool_id == TOOL_ASSEMBLY:   # 合成文件
            func = tool.u2.call
            arg_list = (safe_path(clean), safe_dir)
        elif tool_id == TOOL_CUT: # 分割文件
            m = re.search(r'-c\s+(\S+)\s+-f\s+(.+)', args_raw)
            if not m:
                return jsonify({'success': False, 'error': '参数格式错误'}), 400
            chunk_size = int(m.group(1))
            file_path = m.group(2)
            fp_clean = clean_arg(file_path)
            func = tool.u1.call
            arg_list = (os.path.join(safe_dir,safe_path(fp_clean)), chunk_size,
                        os.path.join(safe_dir,os.path.basename(fp_clean)+"_cut"))
        elif tool_id == TOOL_INFO:
            return jsonify({'success': True, 'message': '使用Assembly以合成文件\n使用cut以分割文件,用法 -c 分割块大小 -f 文件(从根目录起)'}), 201
        
        elif tool_id == TOOL_DOWNLOAD:
            if session.get('user_id') == admin:
                func = download
                arg_list = (clean,safe_dir)  
            else:return jsonify({'success': False, 'error': 'no admin'}), 403

        else:
            return jsonify({'success': False, 'error': '未知工具'}), 404

        task_id = str(uuid.uuid4())
        save_task(task_id,{
                'status': 'pending',
                'error': '',
                'tool_id': tool_id,
                'progress': {'total': 0, 'current': 0},

                'path': a.get("path")
            })
        task_queue.put((task_id, func, arg_list, tool_id))
        return jsonify({'success': True, 'task_id': task_id}), 202

    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))
        traceback.print_exc()
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/file/upload', methods=['POST'])
@is_allowed
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有选择文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400
    original = file.filename
    folder = request.form.get('folder', '').strip()
    try:
        target_dir = safe_path(folder) if folder else UPLOAD_DIR
    except ValueError as e:
        return jsonify({'success': False, 'error': f'目录非法: {str(e)}'}), 400
    os.makedirs(target_dir, exist_ok=True)
    filename = clean_filename(original)
    if os.path.exists(os.path.join(target_dir, filename)):
        filename = unique_name(filename, target_dir)
    filepath = os.path.join(target_dir, filename)
    try:
        file.save(filepath)
        size = os.path.getsize(filepath)
        rel = os.path.relpath(filepath, UPLOAD_DIR)
        save_meta(rel, original, size)
        return jsonify({'success': True, 'data': {'original': original, 'saved': filename, 'size': size}})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'保存失败: {str(e)}'}), 500

@app.route("/api/new")
def sssss():
    if app.debug:
        try:
            load_html()
            print("[INFO] 模板已热重载")
        except Exception as e:
            print(f"[WARN] 模板重载异常: {e}")
        return redirect("/")
    else:
        return redirect("/")








@app.route('/api/files')
@login_required
def list_files():
    sn =os.path.relpath(os.path.abspath(os.path.dirname(__file__)),os.path.abspath("."))
    rel_path = request.args.get('path', '').strip()
    try:
        target_dir = safe_path(rel_path) if rel_path else UPLOAD_DIR
    except ValueError:
        return jsonify({'success': False, 'error': '非法路径'}), 400
    if not os.path.isdir(target_dir):
        return jsonify({'success': False, 'error': '路径不存在'}), 404
    items = []

    try:
        for name in os.listdir(target_dir):
            if name.startswith('.') or name == 'metadata' or name == 'chunks': continue
            full = os.path.join(target_dir, name)
            is_dir = os.path.isdir(full)
            ext = os.path.splitext(full)[1] if os.path.isfile(full) else ""
            is_archive = ext in ('.zip', '.7z', '.rar')

            info = {} if is_dir else (get_file_info(full) or {})
            items.append({
                'name': escape(name),
                'type': 'directory' if is_dir else 'file',
                'size': info.get('size', 0),
                'modified': info.get('modified', ''),
                'type_file': ext,
                'type_zip': is_archive
            })
        items.sort(key=lambda x: (0 if x['type']=='directory' else 1, x['name'].lower()))
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': "see log"}), 500

    return jsonify({'success': True, 'data': items})

@app.route('/api/folders', methods=['POST'])
@is_allowed
@login_required
def create_folder():
    data = request.get_json(silent=True)
    if not data: return jsonify({'success': False, 'error': '无效数据'}), 400
    parent = data.get('path', '').strip()
    name = data.get('name', '').strip()
    if not name: return jsonify({'success': False, 'error': '名称不能为空'}), 400
    if re.search(r'[\\/*?:"<>|]', name):
        return jsonify({'success': False, 'error': '名称包含非法字符'}), 400
    try:
        parent_dir = safe_path(parent) if parent else UPLOAD_DIR
    except ValueError:
        return jsonify({'success': False, 'error': '父目录非法'}), 400
    new_dir = os.path.join(parent_dir, name)
    if os.path.exists(new_dir):
        return jsonify({'success': False, 'error': '文件夹已存在'}), 409
    try:
        os.makedirs(new_dir)
        return jsonify({'success': True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': "see log"}), 500


@app.route('/api/delete/<path:item_path>', methods=['DELETE'])
@is_allowed
@login_required
def delete_item(item_path):
    try:
        full = safe_path(item_path)
    except ValueError:
        return jsonify({'success': False, 'error': '路径非法'}), 400
    if not os.path.exists(full):
        return jsonify({'success': False, 'error': '路径不存在'}), 404

    # 生成唯一ID
    item_id = uuid.uuid4().hex
    trash_dest = os.path.join(TRASH_DIR, item_id)

    try:
        # 移动文件/文件夹到回收站
        shutil.move(full, trash_dest)

        # 记录原始路径（相对路径）、类型、删除时间
        rel_path = os.path.relpath(full, UPLOAD_DIR)
        meta = {
            'original_path': rel_path,
            'is_dir': os.path.isdir(trash_dest),
            'delete_time': int(time.time())
        }
        r.setex(f"trash:{item_id}", 86400 * 10, json.dumps(meta))  # 30天过期

        # 删除原有元数据（可选，如果需要恢复元数据请保留）
        # 这里保留原有元数据删除逻辑，因为恢复时会重新生成
        if os.path.isfile(full):
            meta_file = get_meta_path(rel_path)
            if os.path.exists(meta_file):
                os.remove(meta_file)
                meta_dir = os.path.dirname(meta_file)
                if meta_dir != META_DIR and not os.listdir(meta_dir):
                    os.rmdir(meta_dir)
        else:
            meta_dir = os.path.join(META_DIR, rel_path)
            if os.path.exists(meta_dir):
                shutil.rmtree(meta_dir)

        return jsonify({'success': True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/share/share_put', methods=['POST'])
@is_allowed
@login_required
def share_put():
    data = request.json
    file = data.get('file')
    try:
        full = safe_path(file)
    except ValueError:
        return jsonify({'success': False, 'error': '路径非法'}), 400
    u = str(uuid.uuid4())
    r.setex(f"share:{u}", 86400, full)   # 24小时过期
    host = request.host_url
    return jsonify({'link': host + "share/share_get/" + u})

@app.route('/share/share_get/<path:uuid>')
def down(uuid):
    file_path = r.get(f"share:{uuid}")
    if not file_path:
        abort(404)
    try:
        full = safe_path(file_path)
    except ValueError as e:
        abort(404)
    if not os.path.isfile(full): abort(404)
    
    dirname = os.path.dirname(full)
    filename = os.path.basename(full)
    resp = make_response(send_from_directory(dirname, filename, as_attachment=True))
    resp.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return resp


@app.route('/api/clear-all', methods=['DELETE'])
@login_required
@is_allowed
@is_admin
def clear_all():
    try:
        for name in os.listdir(UPLOAD_DIR):
            if name == 'metadata' or name == 'chunks': continue
            path = os.path.join(UPLOAD_DIR, name)
            if os.path.isfile(path): os.remove(path)
            else: shutil.rmtree(path)
        if os.path.exists(META_DIR):
            shutil.rmtree(META_DIR)
            os.makedirs(META_DIR, exist_ok=True)
        return jsonify({'success': True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error':""}), 500

@app.route('/download/<path:file_path>')
@login_required
@is_allowed
def web_download_file(file_path):
    try:
        full = safe_path(file_path)
    except ValueError:
        abort(404)
    if not os.path.isfile(full): abort(404)
    dirname = os.path.dirname(full)
    filename = os.path.basename(full)
    resp = make_response(send_from_directory(dirname, filename, as_attachment=True))
    resp.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return resp


def trash_autoclear():
    n = []
    for name in os.listdir(TRASH_DIR):
        k = r.get(f'trash:{name}')
        if not k:
            trash_path = os.path.join(TRASH_DIR, name)
            if os.path.exists(trash_path):
                if os.path.isdir(trash_path):
                    shutil.rmtree(trash_path)
                else:
                    os.remove(trash_path)
            r.delete(f'trash:{name}')  # 同步清理失效的 Redis 记录
            n.append(name)
    return n
def while_trash_autodelete():
    while True:
        time.sleep(10)
        trash_autoclear()
Thread(target=while_trash_autodelete,daemon=True).start(
)
#---------trash--------------
@app.route('/api/trash/list', methods=['GET'])
@is_allowed
@login_required
def trash_list():
    items = []
    keys = r.scan_iter(match="trash:*")
    for key in keys:
        item_id = key.split(':', 1)[-1]
        meta_json = r.get(key)
        if not meta_json:
            continue
        meta = json.loads(meta_json)
        trash_path = os.path.join(TRASH_DIR, item_id)
        if not os.path.exists(trash_path):
            r.delete(key)  # 清理无效记录
            continue
        # 获取文件信息
        stat = os.stat(trash_path)
        items.append({
            'id': item_id,
            'original_path': meta['original_path'],
            'is_dir': meta['is_dir'],
            'size': stat.st_size if not meta['is_dir'] else 0,
            'delete_time': meta['delete_time'],
            'name': os.path.basename(meta['original_path'])
        })
    # 按删除时间倒序
    items.sort(key=lambda x: x['delete_time'], reverse=True)
    return jsonify({'success': True, 'data': items})
@app.route('/api/trash/restore/<item_id>', methods=['POST'])
@is_allowed
@login_required
def trash_restore(item_id):
    meta_json = r.get(f"trash:{item_id}")
    if not meta_json:
        return jsonify({'success': False, 'error': '记录不存在'}), 404
    meta = json.loads(meta_json)
    trash_path = os.path.join(TRASH_DIR, item_id)
    if not os.path.exists(trash_path):
        r.delete(f"trash:{item_id}")
        return jsonify({'success': False, 'error': '文件已丢失'}), 404

    original_rel = meta['original_path']
    target_full = safe_path(original_rel)  # 验证路径安全

    # 如果原路径已存在，则自动重命名（加“_恢复”后缀）
    if os.path.exists(target_full):
        base, ext = os.path.splitext(target_full)
        counter = 1
        while os.path.exists(f"{base}_恢复{counter}{ext}"):
            counter += 1
        target_full = f"{base}_恢复{counter}{ext}"
        # 更新原始路径（用于后续元数据）
        original_rel = os.path.relpath(target_full, UPLOAD_DIR)

    try:
        # 移动回原位置
        shutil.move(trash_path, target_full)
        # 删除 Redis 记录
        r.delete(f"trash:{item_id}")
        # 重新生成元数据（如果是文件）
        if not meta['is_dir']:
            save_meta(original_rel, os.path.basename(target_full), os.path.getsize(target_full))
        return jsonify({'success': True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trash/delete/<item_id>', methods=['DELETE'])
@is_allowed
@login_required
def trash_delete(item_id):
    # 同步删除磁盘实体，避免文件残留到下一次自动清理
    trash_path = os.path.join(TRASH_DIR, item_id)
    if os.path.exists(trash_path):
        if os.path.isdir(trash_path):
            shutil.rmtree(trash_path, ignore_errors=True)
        else:
            os.remove(trash_path)
    r.delete(f"trash:{item_id}")
    return jsonify({'success': True})
@app.route('/api/trash/clear', methods=['DELETE'])
@is_allowed
@login_required
def trash_clear():
    keys = r.scan_iter(match="trash:*")
    for key in keys:
        item_id = key.split(':', 1)[-1]
        trash_path = os.path.join(TRASH_DIR, item_id)
        if os.path.exists(trash_path):
            if os.path.isdir(trash_path):
                shutil.rmtree(trash_path)
            else:
                os.remove(trash_path)
        r.delete(key)
    return jsonify({'success': True})


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return "not found<br><a href=\"/\"></a>"

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'success': False, 'error': 'CSRF验证失败'}), 400

# ==================== 服务器控制台（调试用） ====================
from pathlib import Path

def generate_tree(path_str,sock, n=0,):
    if n > 10:
        return ''
    tree_str = ""
    path = Path(path_str).resolve()
    if not path.exists():
        return f"路径不存在: {path_str}\n"
    
    try:
        if path.is_file():
            send_plain(sock,'    |' * n + '-' * 4 + path.name + '\n')
        elif path.is_dir():
            if n == 0:
                send_plain(sock,str(path) + '\\\n')
            else:
                send_plain(sock,'    |' * n + '-' * 4 + path.name + '\\\n')
            for child in sorted(path.iterdir()):
                
                tree_str += generate_tree(str(child),sock, n + 1)
    except PermissionError:
        send_plain(sock,'    |' * n + '-' * 4 + f"[权限不足] {path.name}\n")
    except Exception as e:
        send_plain(sock,'    |' * n + '-' * 4 + f"[错误: {e}]\n")
    
    return tree_str

def create_file(filename):
    with open(filename, 'a'):
        os.utime(filename, None)




# ==================== 服务器控制台（修复版） ====================


def recv_exact(sock, n):
    """精确接收 n 字节数据"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# 当前管理连接的 AES-256 会话密钥（每次握手临时生成，不落盘）
_admin_aes_key = None

def send_enc_frame(sock, key, plaintext: bytes):
    """发送 AES-256-GCM 加密帧：长度(4字节大端) + nonce(12) + 密文 + tag(16)"""
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    payload = nonce + ct + tag
    sock.sendall(struct.pack('>I', len(payload)) + payload)

def recv_enc_frame(sock, key):
    """接收并解密 AES-256-GCM 加密帧，返回明文字节串；连接关闭返回 None"""
    raw_len = recv_exact(sock, 4)
    if raw_len is None:
        return None
    length = struct.unpack('>I', raw_len)[0]
    payload = recv_exact(sock, length)
    if payload is None:
        return None
    if length < 28:   # nonce(12) + tag(16) 是最小帧
        raise ValueError("非法加密帧长度")
    nonce, body = payload[:12], payload[12:]
    ct, tag = body[:-16], body[-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)

def send_plain(sock, msg: str):
    """发送回复（走 AES-256-GCM 加密通道），末尾加换行符"""
    key = _admin_aes_key
    if key is not None:
        send_enc_frame(sock, key, (msg + '\0').encode())
    else:
        # 握手完成前的兜底明文（仅认证阶段可能用到）
        sock.sendall((msg + '\0').encode())

def stdin_shell(popen:subprocess.Popen,sock:socket.socket,event:Event):
    """终端输入线程：读取加密帧写入子进程 stdin；
    收到 EOT(\\4) 时关闭 stdin 让子进程自然退出；客户端断开时终止子进程；
    event 置位后通过超时轮询退出（Windows 的 select 仅支持 socket，此处检测的正是 socket，可用）。"""
    while not event.is_set():
        if not select.select([sock], [], [], 0.2)[0]:
            continue
        aaa = recv_enc_frame(sock, _admin_aes_key)
        if aaa is None:
            # 客户端断开：终止子进程，避免命令循环永久阻塞
            try:
                popen.terminate()
            except Exception:
                pass
            break
        if aaa == b'\4':
            # 终端结束：关闭 stdin 让子进程自然退出（EOF）
            try:
                popen.stdin.close()
            except Exception:
                pass
            break
        try:
            popen.stdin.write(aaa.decode())
            popen.stdin.flush()
        except (ValueError, OSError):
            # 子进程已退出导致 stdin 关闭
            break


def w(port,lock:filelock.FileLock):
    global admin, users, app, _admin_aes_key
    process = None
    # 认证失败限流键前缀（Redis 存储，1 小时过期）
    AUTH_FAIL_PREFIX = 'admin_fail:'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    time.sleep(1)

    while True:
        private_key = RSA.generate(3072)       # 认证用，注意1024位密钥OAEP最大明文约86字节
        public_key = private_key.publickey()
        
        if not r.smembers('command'):
            r.sadd('command','ping')
            r.sadd('command','python')
            r.sadd('command','python3')
            r.sadd('command','ls')
            r.sadd('command','echo')


        print('等待管理连接...', flush=True)
        login_r = False
        sf, client_addr = s.accept()
        print(f"新连接来自 {client_addr}", flush=True)

        try:
            # 1. 发送公钥（长度前缀 + 公钥数据）
            pub_bytes = public_key.export_key()
            sf.sendall(struct.pack('>I', len(pub_bytes)))
            sf.sendall(pub_bytes)

            # 2. 接收 RSA-OAEP 加密的 32 字节会话密钥，之后所有流量走 AES-256-GCM
            raw_len = recv_exact(sf, 4)
            if raw_len is None:
                raise ConnectionError("客户端未发送会话密钥")
            enc_len = struct.unpack('>I', raw_len)[0]
            enc_key = recv_exact(sf, enc_len)
            if enc_key is None:
                raise ConnectionError("会话密钥数据不完整")
            session_key = PKCS1_OAEP.new(private_key).decrypt(enc_key)
            if len(session_key) != 32:
                raise ValueError("会话密钥长度非法")
            _admin_aes_key = session_key

            # 3. 接收 AES-GCM 加密的认证信息
            encrypted_auth = recv_enc_frame(sf, session_key)
            if encrypted_auth is None:
                raise ConnectionError("客户端未发送认证信息")
            auth_str = encrypted_auth.decode()
            nm = auth_str.split(',')
            # 失败限流：以客户端标识 nm[2] 为键（Redis 存储），失败 >=5 次即锁定，键 1 小时过期
            fail_key = AUTH_FAIL_PREFIX + str(nm[2])
            fail_cnt = int(r.get(fail_key) or 0)
            if fail_cnt >= 5:
                print(f"认证已锁定: {nm}", flush=True)
                send_plain(sf, "n")
                send_enc_frame(sf, session_key, b'\4')
                sf.close()
                _admin_aes_key = None
                continue
            stored_hash = users.get(nm[0], '')
            if nm[0] == admin and stored_hash and check_password_hash(stored_hash, nm[1]):
                r.delete(fail_key)   # 成功后清零计数
                send_plain(sf, "y")
                send_enc_frame(sf, session_key, b'\4')
                print('认证成功', flush=True)
                login_r = True
            else:
                r.incr(fail_key)
                r.expire(fail_key, 3600)
                print(f"认证失败: {nm}", flush=True)
                send_plain(sf, "n")
                send_enc_frame(sf, session_key, b'\4')
                sf.close()
                _admin_aes_key = None
                continue
        except Exception as e:
            traceback.print_exc()
            try:
                send_plain(sf, "er")
            except:
                pass
            sf.close()
            continue
        
        # 命令处理循环
        while login_r:
            try:
                sf.sendall(b'c')
                
                # 接收加密的命令（AES-256-GCM 帧）
                encrypted_cmd = recv_enc_frame(sf, _admin_aes_key)
                if encrypted_cmd is None:
                    break
                cmd = encrypted_cmd.decode()

                logging.info(f"exec: {cmd.split(' ')[0:2]}")

                if cmd == "</c>":
                    send_plain(sf, "bye")
                    sf.shutdown(socket.SHUT_RDWR)
                    sf.close()
                    break
                if cmd in ("exit",):
                    keys = r.scan_iter(match=f"{TASK_PREFIX}*")
                    for key in keys:
                        cancel_task_by_id(key)
                        
                    os._exit(0)
                elif cmd.lower() == 'gettask':
                    keys = r.scan_iter(match=f"{TASK_PREFIX}*")
                    tasks = {}
                    
                    for key in keys:
                        # key 格式为 task:uuid
                        if isinstance(key, bytes):
                            tid = key.decode().split(':', 1)[-1]
                        else:
                            tid = key.split(':', 1)[-1]
                        task = get_task(tid)  # 已经反序列化 progress/file_info
                        if task:
                            # 过滤不可序列化字段，保持与原 /api/dl 一致
                            filtered = {}
                            for k, v in task.items():
                                
                                filtered[k] = v
                            tasks[tid] = filtered
                    send_plain(sock=sf,msg=str(tasks))
                elif cmd.lower() == 'cleartask':
                    keys = r.scan_iter(match=f"{TASK_PREFIX}*")
                    for key in keys:
                        if isinstance(key, bytes):
                            tid = key.decode().split(':', 1)[-1]
                        else:
                            tid = key.split(':', 1)[-1]
                        task = get_task(tid)
                        if task and task.get('status') not in ('running','pending'):
                            delete_task(tid)
                            send_plain(sf,f'remove task {tid}\n')
                elif cmd.lower().startswith("ls"):
                    path_part = cmd.replace("ls", "", 1).strip()
                    if path_part.startswith('-'):
                        
                        nn = cmd.split(' ')
                        sxs = nn[1]
                        try:
                            path_part = nn[2]
                        except IndexError:
                            path_part = ''
                        for s in sxs:
                            if s == 'l':
                                try:
                                    lp = safe_path(path_part) if path_part else UPLOAD_DIR
                                except ValueError:
                                    send_plain(sf, 'path not allowed')
                                    break
                                for n in os.listdir(lp):
                                    send_plain(sf, n+'\n')
                                break
                    else:

                        tree = generate_tree(os.path.join(BASE_DIR, "uploads", path_part),sf)
                    
                elif cmd.lower().startswith('del '):
                    rel = cmd[4:].strip()
                    try:
                        ss = safe_path(rel)
                    except ValueError:
                        send_plain(sf,'path not allowed')
                        continue
                    if os.path.basename(ss) == 'app.py':
                        send_plain(sf,'not can remove')
                    elif os.path.isfile(ss):
                        shutil.move(ss,TRASH_DIR)
                        send_plain(sf,'move to trash ok')
                    else:send_plain(sf,'file not found')

                elif cmd.lower().startswith('cat '):
                    rel = cmd[4:].strip()
                    try:
                        ss = safe_path(rel)
                    except ValueError:
                        send_plain(sf,'path not allowed')
                        continue
                    if not os.path.isfile(ss):
                        send_plain(sf,'file not found')
                        continue
                    with open(ss,'rb') as nn:
                        while True:
                            t = nn.read(1024)
                            if not t:
                                break
                            send_plain(sf, t.decode('utf-8','replace'))
                elif cmd == "load":
                    load_html()
                    send_plain(sf, "load ok")
                elif cmd.lower().startswith('debug '):
                    ddd = cmd.lower().replace("debug ", "").strip()
                    if ddd == "open":
                        create_file(os.path.join(BASE_DIR, "de.lock"))
                        app.debug = True
                    elif ddd == "close":
                        if os.path.exists(os.path.join(BASE_DIR, "de.lock")):
                            os.remove(os.path.join(BASE_DIR, "de.lock"))
                        app.debug = False
                    send_plain(sf, f"debug mode {'open' if app.debug else 'close'} ok")

                elif cmd.lower().startswith("adduser "):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 3:
                        username, password = parts[1], parts[2]
                        users[username] = generate_password_hash(password)
                        user_list.append(username)
                        send_plain(sf, f"用户 *** 已添加")
                        save_user()
                    else:
                        send_plain(sf,f'error,*** in not found')

                elif cmd.lower().startswith("deluser "):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username in users and username in user_list:
                            del users[username]
                            user_list.remove(username)
                            send_plain(sf, f"用户 *** 已删除")
                            save_user()
                        elif username in users and username in blocked_users:
                            del users[username]
                            blocked_users.remove(username)
                            send_plain(sf, f"用户 *** 已删除")
                            save_user()
                        else:
                            send_plain(sf, "用户不存在")

                elif cmd.lower()==("listuser"):
                    info = ["当前用户列表:"]
                    for user in users.keys():
                        role = ""
                        if user in blocked_users:
                            role += " forbid"
                        else:
                            if user not in user_list:
                                user_list.append(user)
                            role += " authorized"
                        if user == admin:
                            role += " admin"
                        info.append(f"--{user} {role}")
                    send_plain(sf, "\n".join(info))
                    save_user()

                elif cmd.lower().startswith("addnigga "):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username not in users:
                            send_plain(sf, f"*** 不存在")
                        elif username not in blocked_users:
                            blocked_users.append(username)
                            if username in user_list:
                                user_list.remove(username)
                            send_plain(sf, f"用户 *** 已移入黑名单")
                            save_user()

                elif cmd.lower().startswith("delnigga "):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username not in users:
                            send_plain(sf, f"*** 不存在")
                        elif username in blocked_users:
                            blocked_users.remove(username)
                            if username not in user_list:
                                user_list.append(username)
                            send_plain(sf, f"用户 *** 已移出黑名单")
                            save_user()

                elif cmd.lower().startswith("setadmin "):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username not in users:
                            send_plain(sf, f"*** 不存在")
                        elif username in user_list:

                            admin = username
                            send_plain(sf, f"用户 *** 已设为管理员")
                            save_user()

                elif app.debug and cmd.lower().startswith("get "):
                    parts = cmd.split()
                    try:
                        send_plain(sf, str(globals()[parts[1]]))
                    except KeyError:
                        try:
                            send_plain(sf, str(locals()[parts[1]]))
                        except KeyError:
                            send_plain(sf, f"变量 {parts[1]} 不存在")

                elif cmd.lower() == 'clearlog':        
                    open(LOG_FILE,'w',encoding='utf-8').close()
                    send_plain(sf,'log clear')
                    err_file = os.path.join(BASE_DIR,'error')
                    if os.path.exists(err_file):
                        os.remove(err_file)
                    send_plain(sf,'Error stack is clear')
                elif cmd.lower() == 'update':
                    ns = recv_enc_frame(sf,_admin_aes_key)
                    ns = ns.decode()
                    # 校验是合法 IPv4 且不是 0.0.0.0/组播，避免绑定所有接口导致未授权访问
                    if ipaddress.IPv4Address(ns).is_unspecified or ipaddress.IPv4Address(ns).is_multicast:
                        send_plain(sf, 'bad ip')
                        continue
                    while True:
                        sm = random.randint(6000,6050)
                        if not is_port_in_use(sm):
                            break
                    a = Thread(target=update_file,args=(ns,sm),daemon=True)
                    a.start()
                    send_plain(sf,str(sm))
                elif cmd.lower() == 'download':
                    ns = recv_enc_frame(sf,_admin_aes_key)
                    ns = ns.decode()
                    if ipaddress.IPv4Address(ns).is_unspecified or ipaddress.IPv4Address(ns).is_multicast:
                        send_plain(sf, 'bad ip')
                        continue
                    while True:
                        sm = random.randint(6000,6050)
                        if not is_port_in_use(sm):
                            break
                    a = Thread(target=download_file,args=(ns,sm),daemon=True)
                    a.start()
                    send_plain(sf,str(sm))

                elif cmd.startswith('run '):
                    rest = cmd[4:].strip()
                    stdin_on = False
                    if rest.startswith('term '):
                        stdin_on = True
                        rest = rest[5:].strip()
                    try:
                        tokens = shlex.split(rest)
                    except ValueError:
                        send_plain(sf, '参数解析失败')
                        continue
                    if not tokens:
                        send_plain(sf, 'can\'t exec')
                        continue
                    exe = shutil.which(tokens[0])
                    if tokens[0] not in r.smembers('command') or exe is None:
                        send_plain(sf, 'can\'t exec')
                    else:
                        # 通知客户端已进入终端模式（客户端据此决定是否启动 stdin 输入线程）
                        send_plain(sf, '\x02TERM')
                        # 不再使用 shell=True，避免 `run ping; rm -rf` 之类注入绕过白名单
                        # PYTHONUNBUFFERED=1 让 python 子进程行缓冲/无缓冲，保证实时输出
                        env = dict(os.environ)
                        env['PYTHONUNBUFFERED'] = '1'
                        lock = Event()

                        process = subprocess.Popen([exe] + tokens[1:], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=UPLOAD_DIR, text=True, env=env)
                        stdin_thread = None
                        if stdin_on:
                            print('term', flush=True)
                            stdin_thread = Thread(target=stdin_shell, name='command', args=(process, sf, lock), daemon=True)
                            stdin_thread.start()
                        # 用底层 fd 的 os.read：管道一有数据就返回（不攒满 4096），保证实时回显。
                        # 非阻塞 + 轮询；子进程退出时读尽剩余输出后结束。
                        def stdout_forward(p, sock):
                            fd = p.stdout.fileno()
                            try:
                                os.set_blocking(fd, False)
                            except OSError:
                                pass
                            while True:
                                try:
                                    chunk = os.read(fd, 4096)
                                except BlockingIOError:
                                    chunk = b''
                                except OSError:
                                    break
                                if chunk:
                                    # 字节透传：不在服务端解码，交给客户端按 utf-8/gbk 智能解码
                                    send_enc_frame(sock, _admin_aes_key, chunk)
                                elif p.poll() is not None:
                                    # 子进程已退出：读尽剩余输出
                                    while True:
                                        try:
                                            tail = os.read(fd, 4096)
                                        except (BlockingIOError, OSError):
                                            tail = b''
                                        if not tail:
                                            break
                                        send_enc_frame(sock, _admin_aes_key, tail)
                                    break
                                else:
                                    time.sleep(0.05)
                        reader = Thread(target=stdout_forward, args=(process, sf), daemon=True)
                        reader.start()
                        process.wait()
                        reader.join(timeout=2)   # 子进程退出后 stdout EOF，reader 会自行结束
                        if stdin_thread is not None:
                            lock.set()           # 停止 stdin 输入线程，避免其截获下一条命令
                            stdin_thread.join(timeout=1)
                        return_code = process.returncode
                        send_plain(sf, f"Process finished with return code {return_code}")
                elif cmd.lower( ) == 'export':
                    raise Exception('export')
                elif cmd.lower() == 'runlist':
                    send_plain(sf,str(r.smembers('command')))
                elif cmd.startswith('cr ') and app.debug:
                    cmd_name = cmd.replace("cr ", '', 1).strip()
                    if cmd_name and ' ' not in cmd_name and shutil.which(cmd_name):
                        r.sadd('command', cmd_name)
                        r.smembers('command')
                        send_plain(sf, f'command {cmd_name} added')
                    else:
                        send_plain(sf, 'can\'t add command')
                else:
                    send_plain(sf, "未知命令")
                    
            
            except Exception as e:
                traceback.print_exc()
                try:
                    with open(os.path.join(BASE_DIR,'error'),'w',encoding='utf-8') as d:
                        n = locals().copy()
                        cc=['private_key','public_key','pub_bytes','session_key','enc_key','e']
                        for x in cc:
                            n.pop(x)

                        print(n,file=d)
                        print(traceback.format_exc(),file=d)
                except Exception as en:
                    try:
                        send_plain(sf, f"error: {en}\n")
                    except:
                        break
                if not process is None:
                    if process.poll() is None:
                        process.terminate()
                logging.error(f"命令执行错误: {e}")
                try:
                    send_plain(sf, f"error: {e}\n")
                except:
                    break
            except KeyboardInterrupt:
                lock.release()
            finally:
                try:
                    send_enc_frame(sf, _admin_aes_key, b'\4')
                except:
                    break
        # 连接关闭后清空会话密钥
        _admin_aes_key = None
        # 连接关闭后继续等待新连接

def update_file(ip,port):
    n = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    n.bind((ip,port))
    n.listen(1)
    con,addr = n.accept()
    try:
        if not recv_file(con, save_dir=UPLOAD_DIR, max_size=1024 * 1024 * 1024):
            print('error', flush=True)
    finally:
        con.close()
        n.close()

def download_file(ip,port):
    n = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    n.bind((ip,port))
    n.listen(1)
    con,addr = n.accept()
    try:
        # 客户端发送：struct.pack('!I', len(name)) + name.encode()
        raw_len = con.recv(4)
        if len(raw_len) < 4:
            return
        name_len = struct.unpack('!I', raw_len)[0]
        name = b''
        while len(name) < name_len:
            chunk = con.recv(name_len - len(name))
            if not chunk:
                break
            name += chunk
        file_rel = name.decode()
        try:
            file_path = safe_path(file_rel)  # 仅允许 UPLOAD_DIR 内文件，防任意读取
        except ValueError:
            print('download path not allowed', flush=True)
        else:
            if not os.path.isfile(file_path):
                print('download file not found', flush=True)
            elif not send_file(con, file_path):
                print('error', flush=True)
    finally:
        con.close()
        n.close()

lock = filelock.SoftFileLock('.admin_lock')





if __name__ == '__main__':
    print(f"🌐 启动：http://0.0.0.0:5000\n访问http://{socket.gethostbyname(socket.gethostname())}:5000", flush=True)
    if os.path.exists(os.path.join(BASE_DIR,"de.lock")):
        app.debug = True
        HTML_TEMPLATE += "<br/>\n<a href=\"/api/new\">new</a>"
    while True:
        sm = random.randint(6000,6050)
        if not is_port_in_use(sm):
            break
    
    r.set('man_port',sm)
    print(f"管理端口链接:{socket.gethostbyname(socket.gethostname())}:{sm}",flush=True)
    logging.info(f"管理端口链接:{socket.gethostbyname(socket.gethostname())}:{sm}")
    s = Thread(target=w, daemon=True,args=(sm,))
    s.start()
    app.run("0.0.0.0", 5000, use_reloader=False,use_evalex=False)
else:
    try:
        # 本 worker 抢到了锁，负责启动管理端口
        lock.acquire(timeout=1)
        while True:
            sm = random.randint(6000, 6050)
            if not is_port_in_use(sm):
                break
        print(f"管理端口链接: {socket.gethostbyname(socket.gethostname())}:{sm}", flush=True)
        logging.info(f"管理端口链接: {socket.gethostbyname(socket.gethostname())}:{sm}")
        r.set('man_port',sm)
        s = Thread(target=w, daemon=True, args=(sm,lock))
        s.start()
        atexit.register(lock.release)

            
        
    except filelock.Timeout as e:print('no lock')