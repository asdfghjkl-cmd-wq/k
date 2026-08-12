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



import psutil

def is_port_in_use(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN":
            return True
    return False
import tempfile
true=True
import hashlib
from math import fabs
from multiprocessing import Process as pro
from py7zr import SevenZipFile
from markupsafe import escape
from filelock import FileLock
import zipfile, requests,pyzipper
from threading import Thread
from queue import Queue
from urllib.parse import urlparse
import logging
import socket
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
ascii_lowercase += "0123456789"
from flask_wtf.csrf import CSRFProtect, CSRFError
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
# 禁用不安全的请求警告（针对 verify=False）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import redis


# 从环境变量读取 Redis 地址，方便部署
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
print(r.info('server')['redis_version'],flush=True)
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


    class u2:
        def call(dir,tdir,task_id,cancel_check):
            file = open(os.path.join(dir,"file"),"r",encoding="utf-8")
            n = os.path.basename(file.readline().replace("\n",""))
 
            x = int(file.readline().replace("\n",""))
            file.close()
            bn = open(os.path.join(tdir,n),"wb")
            for nb in range(1,x+1):
                if cancel_check():
                    os.remove(bn.name)
                    raise qe("cancel")
                an = open(os.path.join(dir,f"{nb:04d}"+".data"),"rb")
                bn.write(an.read())
                an.close()

# ==================== 异步任务系统 ====================


MAX_WORKERS = 3
task_queue = Queue()
def save_user():
    """将用户数据存入 Redis"""
    # 存储密码哈希
    if users:
        r.hset("users", mapping=users)   # {"username": "hash"}
    # 存储用户列表
    r.delete("user_list")
    if user_list:
        r.sadd("user_list", *user_list)
    # 存储黑名单
    r.delete("nigga_list")
    if nigga_list:
        r.sadd("nigga_list", *nigga_list)
    # 存储管理员
    r.set("admin", admin)
    print('save ok', flush=True)

def load_user():
    """从 Redis 加载用户数据"""
    global users, user_list, nigga_list, admin

    # 默认管理员（环境变量）
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', os.environ.get('a', None))
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', os.environ.get('p', None))
    ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD) if ADMIN_PASSWORD else None

    # 尝试从 Redis 读取
    redis_users = r.hgetall("users")
    redis_user_list = list(r.smembers("user_list"))
    redis_nigga_list = list(r.smembers("nigga_list"))
    redis_admin = r.get("admin")

    # 如果 Redis 中有数据就用 Redis 的
    if redis_users:
        users = redis_users
        user_list = redis_user_list
        nigga_list = redis_nigga_list
        admin = redis_admin if redis_admin else ADMIN_USERNAME
    else:
        # 首次运行，用环境变量初始化
        users = {ADMIN_USERNAME: ADMIN_PASSWORD_HASH}
        user_list = [ADMIN_USERNAME]
        nigga_list = []
        admin = ADMIN_USERNAME
        save_user()  # 写入 Redis

    return users, user_list, nigga_list, admin
tool_list = [6,50,51,1,2,4,64]
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
                    if tool_id == 64:
                        a, n = func(*base_args, task_id=task_id,
                                    cancel_check=lambda: is_cancelled(task_id))
                    else:
                        a = func(*base_args, task_id=task_id,
                                 cancel_check=lambda: is_cancelled(task_id))
                else:
                    r.hset(task_key(task_id), 'can_cancel', 'False')
                    func(*base_args)

            if a and tool_id == 64:
                r.hset(task_key(task_id), 'status', 'finished')
                r.hset(task_key(task_id), 'return', n)
            elif a:
                r.hset(task_key(task_id), 'status', 'finished')
            else:
                r.hset(task_key(task_id), 'status', 'failed;')

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

def ran_str(length, charset=ascii_lowercase):
    return ''.join(random.choice(charset) for _ in range(length))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'a.html')

try:
    with open(os.path.join(BASE_DIR, "s.key"), "r", encoding="utf-8") as s:
        k = s.read()
except:
    k = ran_str(128, ascii_letters)
    with open(os.path.join(BASE_DIR, "s.key"), "w", encoding="utf-8") as s:
        s.write(k)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=os.path.join(BASE_DIR, "app.log"),
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
    JSON_AS_ASCII=False
)

csrf = CSRFProtect(app)

logging.info("flask create ok")

UPLOAD_DIR = os.path.abspath(app.config['UPLOAD_FOLDER'])
CHUNK_DIR = os.path.join(UPLOAD_DIR, 'chunks')
META_DIR = os.path.join(UPLOAD_DIR, 'metadata')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)
share_dict = dict()


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
    global user_list,users,nigga_list,admin
    while True:
        time.sleep(10)
        redis_users = r.hgetall("users")
        redis_user_list = list(r.smembers("user_list"))
        redis_nigga_list = list(r.smembers("nigga_list"))
        redis_admin = r.get("admin")
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', os.environ.get('a', None))
        if redis_users:
            users = redis_users
            user_list = redis_user_list
            nigga_list = redis_nigga_list
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

users,user_list,nigga_list,admin = load_user()
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
        cleanup_expired_sessions()
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
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):

        if 'user_id' not in session or session.get('user_id') not in list(users.keys()):
            if (request.is_json or
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.path.startswith('/api/')):
                return jsonify({'success': False, 'error': '请先登录'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return wrap

def isadmin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        for aaa in nigga_list:
            if session.get('user_id') == aaa:
                if (request.is_json or
                    request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                    request.path.startswith('/api/')):
                    return jsonify({'success': False, 'error': 'no admin'}), 403
                return "no user",403
        return f(*args, **kwargs)
    return wrap

def isa(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('user_id') == admin:
            return f(*args, **kwargs)
        else:
            if (request.is_json or
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.path.startswith('/api/')):
                return jsonify({'success': False, 'error': 'no admin'}), 403

            return "no admin",403


def safe_path(*parts):
    # 无参数或仅传入 '.' 时，直接返回上传根目录
    if not parts or (len(parts) == 1 and parts[0] == '.'):
        return UPLOAD_DIR

    target = os.path.abspath(os.path.join(UPLOAD_DIR, *parts))
    target = os.path.realpath(target)
    print(target)
    if sys.platform.startswith('win'):
        if not target.lower().startswith(os.path.abspath(UPLOAD_DIR).lower()):
            raise ValueError("路径越权")
    else:
        if not target.startswith(os.path.abspath(UPLOAD_DIR)):
            raise ValueError("路径越权")
    return target

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
        a = pro(target=sece,args=(zp,target_dir,file,password,task_id),daemon=True)
        return True,a,target_dir
    except Exception as e:
        app.logger.error(f"解压失败: {e}")
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)
        return False,None,target_dir

def sece(zp,target_dir,file,password,task_id):
    try:
        with SevenZipFile(zp,mode="r",password=password) as df:
            for member in df.list():
                
                member_path = os.path.realpath(os.path.join(target_dir, member.filename))
                if not member_path.startswith(target_dir + os.sep) and member_path != target_dir:
                    raise Exception(f"Zip Slip 攻击检测: {member.filename}")
            df.extractall(target_dir)
            app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        save_task(task_id,{'error':str(e)})





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
            a =pro(target=zce,args=(zip_path,target_dir,file,task_id),daemon=True)
        else:a =pro(target=zece,args=(zip_path,target_dir,file,password.encode(),task_id),daemon=True)
        return True,a,target_dir
    except Exception as e:
        app.logger.error(f"解压失败: {e}")
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)
        return False,None,target_dir

def zce(zip_path,target_dir,file,task_id):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:

            for member in zf.infolist():
                member_path = os.path.realpath(os.path.join(target_dir, member.filename))
                if not member_path.startswith(target_dir + os.sep) and member_path != target_dir:
                    raise Exception(f"Zip Slip 攻击检测: {member.filename}")
            zf.extractall(target_dir)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        save_task(task_id,{'error':str(e)})

def zece(zip_path,target_dir,file,password,task_id):
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            zf.setpassword(password)

            for member in zf.infolist():
                member_path = os.path.realpath(os.path.join(target_dir, member.filename))
                if not member_path.startswith(target_dir + os.sep) and member_path != target_dir:
                    raise Exception(f"Zip Slip 攻击检测: {member.filename}")
            zf.extractall(target_dir)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        save_task(task_id,{'error':str(e)})

def download(url, dir, task_id, cancel_check):
    filepath = None
    try:
        filename = get_filename_from_url(url)
        filepath = os.path.join(UPLOAD_DIR, dir, filename)
        resp = requests.get(url, stream=True, timeout=10, verify=False)
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        update_task_progress(task_id, total=total, current=0)  # 使用已有的辅助函数

        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                if cancel_check():
                    resp.close()
                    raise Exception("下载被取消")
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 正确更新进度：传入已下载字节数
                    update_task_progress(task_id, current=downloaded)
        return True
    except Exception as e:
        logging.error(f"下载错误: {e}")
        save_task(task_id,{'error':str(e)})
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        raise

# ==================== 分卷上传会话管理 ====================
chunk_sessions = {}

def cleanup_expired_sessions():
    now = time.time()
    expired = [sid for sid, info in chunk_sessions.items() if now - info.get('created', 0) > 60*15]
    for sid in expired:
        session_dir = os.path.join(CHUNK_DIR, sid)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir, ignore_errors=True)
        chunk_sessions.pop(sid, None)
    if expired:
        print(f"[INFO] 清理了 {len(expired)} 个过期分卷会话")

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.info(f"user logining.from {request.remote_addr}")
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username in users and check_password_hash(users[username], password):
            session['user_id'] = username
            return redirect(request.args.get('next') or url_for('index'))
        error = '用户名或密码错误'
        logging.warning(f"user login failure.from {request.remote_addr} user:{username},password:{password[:4]}")
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
        for sa in nigga_list:
            if session.get("user_id") == sa:
                la = False
    return jsonify({"login":lo,"admin":la,"name":name})

@app.route("/api/gdl")
@login_required
@isadmin
def get_download_list():
    keys = r.keys(f"{TASK_PREFIX}*")
    running_downloads = []
    for key in keys:
        if isinstance(key, bytes):
            tid = key.decode().split(':', 1)[-1]
        else:
            tid = key.split(':', 1)[-1]
        tool_id = r.hget(key, 'tool_id')
        status = r.hget(key, 'status')
        if tool_id and status and str(tool_id) == '6' and status == 'running':
            running_downloads.append(tid)
    return jsonify(running_downloads), 200
            
@app.route("/api/dl")
@login_required
@isadmin
def get_task_list_all():
    # 获取 Redis 中所有任务
    keys = r.keys(f"{TASK_PREFIX}*")
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
@isadmin
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
    tool_id = 64
    
    save_task(task_id,{
                'status': 'pending',
                'error': '',
                'tool_id': tool_id,
                'progress': {'total': 0, 'current': 0},
                'file_info':{'src':sp},
                'path': os.path.dirname(os.path.abspath(sp))
            })
    arg_list = (sp,)
    print(arg_list)
    task_queue.put((task_id, func, arg_list, tool_id))
    return jsonify({'success':True,'task_id':task_id})
    




@app.route('/')
@login_required
def index():

    return render_template_string(HTML_TEMPLATE, username=session.get('user_id',''))

@app.route('/api/task/<task_id>', methods=['GET'])
@isadmin
@login_required
def get_task_status(task_id):

    task = get_task(task_id)
    if not task:
        return jsonify({'success': False, 'error': '无效任务ID'}), 404

    a = {}
    n = [str,int,list,dict,bool,bytes,bytearray]
    for aa,x in task.items():
    
        if type(x) in n:
            print(aa,":",x)
            a[aa] = x
    a['success'] =True

    return jsonify(a)


@app.route('/api/task/<task_id>/cancel', methods=['POST', 'GET'])
@login_required
@isadmin
def cancel_task(task_id):
    success = cancel_task_by_id(task_id)
    if not success:
        task = get_task(task_id)
        if not task:
            return jsonify({'success': False, 'error': '无效任务ID'}), 404
        return jsonify({'success': False, 'error': '任务无法取消'}), 400
    return jsonify({'success': True})


@app.route("/file/move", methods=['POST'])
@isadmin
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
    tool_id = 51

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

def move_file(source,target,task_id,cancel_check):
    

    try:
        src = safe_path(source)
        dst = resolve_target_path(src, target)
    except ValueError:
        return "错误: 目录越权", 400

    if not os.path.exists(src):
        return "源路径不存在", 404

    try:
        if os.path.isfile(src):
            # 移动文件：shutil.move 会自动处理目标为目录或文件的情况
            a = pro(target=shutil.move,args=(src,dst),daemon=True)
        elif os.path.isdir(src):
            a = pro(target=shutil.move,args=(src,dst),daemon=True)
                
        else:
            return "源路径类型未知", 400
        a.start()
        while a.is_alive():
            if cancel_check():
                a.kill()
                raise qe("移动被取消")
        return True
    except Exception as e:
        logging.error(f"移动失败: {e}")
        return False

        
@app.route("/file/copy", methods=['POST'])
@isadmin
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
    tool_id = 50

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




def copy_file(source,target,task_id,cancel_check):
    

    try:
        src = safe_path(source)
        dst = resolve_target_path(src, target)
    except ValueError:
        return "错误: 目录越权", 400

    if not os.path.exists(src):
        return "源路径不存在", 404

    try:
        if os.path.isfile(src):
            # 移动文件：shutil.move 会自动处理目标为目录或文件的情况
            a = pro(target=shutil.copy,args=(src,dst),daemon=True)
        elif os.path.isdir(src):
            if os.path.exists(dst):a = pro(target=shutil.copytree,args=(src,os.path.join(dst,os.path.basename(src))),daemon=True)

            else:a = pro(target=shutil.copytree,args=(src,dst),daemon=True)
                
        else:
            return "源路径类型未知", 400
        a.start()
        while a.is_alive():
            if cancel_check():
                a.kill()
                raise qe("复制被取消")
        return True
    except Exception as e:
        logging.error(f"复制失败: {e}")
        save_task(task_id,{'error':e})
        return False

    
@app.route('/file/zipex',methods=['POST'])
@login_required
@isadmin
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
    tool_id = 4
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
    print(f,flush=True)
    if not os.path.exists(f):
        
        return False
    

    _,n = os.path.splitext(f)
    try:
        if n == ".zip":
            a,b,target_dir = zipe(f,sp,password,task_id)
        elif n == '.7z':
            a,b,target_dir = sze(f,sp,password,task_id)

        else:
            save_task(task_id,{'error':'not found'})
            return False
        if not a:
            save_task(task_id,{'error':'error'})
            return False
        b.start()

        while b.is_alive():
            if cancel_check():
                if os.path.exists(target_dir) and not os.listdir(target_dir):
                    os.rmdir(target_dir)
                raise qe('canceled')
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
    # 确保目标路径在 UPLOAD_DIR 内部（或等于 UPLOAD_DIR 本身）
    if sys.platform.startswith('win'):
        if not target_abs.lower().startswith(upload_abs.lower()) and target_abs.lower() != upload_abs.lower():
            print(target_abs,flush=True)
            raise ValueError(f"目标路径越权;{target_abs};{upload_abs};{sys.platform}")
    else:
        if not target_abs.startswith(upload_abs) and target_abs != upload_abs:
            print(target_abs,flush=True)
            raise ValueError(f"目标路径越权;{target_abs};{upload_abs};{sys.platform}")
    return target_abs


@app.route('/api/disk_usage')
@isadmin
@login_required
def get_du():
    a,b,c = shutil.disk_usage(UPLOAD_DIR)
    return jsonify({'total':a,"used":b,"free":c})


@app.route("/api/toolcall", methods=['POST'])
@isadmin
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
        if tool_id == 1:   # Assembly
            func = tool.u2.call
            arg_list = (safe_path(clean), safe_dir)
        elif tool_id == 2: # Cut
            m = re.search(r'-c\s+(\S+)\s+-f\s+(.+)', args_raw)
            if not m:
                return jsonify({'success': False, 'error': '参数格式错误'}), 400
            chunk_size = int(m.group(1))
            file_path = m.group(2)
            fp_clean = clean_arg(file_path)
            func = tool.u1.call
            arg_list = (os.path.join(safe_dir,safe_path(fp_clean)), chunk_size,
                        os.path.join(safe_dir,os.path.basename(fp_clean)+"_cut"))
        elif tool_id == 3:
            return jsonify({'success': True, 'message': '使用Assembly以合成文件\n使用cut以分割文件,用法 -c 分割块大小 -f 文件(从根目录起)'}), 201
        
        elif tool_id == 6:
            func = download
            arg_list = (clean,safe_dir)  

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
@isadmin
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
            n = str(full)
            is_dir = os.path.isdir(full)
            if os.path.isfile(full):
                da,nb = os.path.splitext(n)
            else:nb = ""
            n = False
            a = ['.zip','.7z','.rar']
            if nb in a:
                n = True

            info = {} if is_dir else (get_file_info(full) or {})
            items.append({
                'name': escape(name),
                'type': 'directory' if is_dir else 'file',
                'size': info.get('size', 0),
                'modified': info.get('modified', ''),
                'type_file': nb,
                'type_zip':n
            })
        items.sort(key=lambda x: (0 if x['type']=='directory' else 1, x['name'].lower()))
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': "see log"}), 500

    return jsonify({'success': True, 'data': items})

@app.route('/api/folders', methods=['POST'])
@isadmin
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
@isadmin
@login_required
def delete_item(item_path):
    try:
        full = safe_path(item_path)
    except ValueError:
        return jsonify({'success': False, 'error': '路径非法'}), 400
    if not os.path.exists(full):
        return jsonify({'success': False, 'error': '路径不存在'}), 404
    try:
        if os.path.isfile(full):
            os.remove(full)
            rel = os.path.relpath(full, UPLOAD_DIR)
            meta_file = get_meta_path(rel)
            if os.path.exists(meta_file):
                os.remove(meta_file)
                meta_dir = os.path.dirname(meta_file)
                if meta_dir != META_DIR and not os.listdir(meta_dir):
                    os.rmdir(meta_dir)
        else:
            shutil.rmtree(full)
            rel = os.path.relpath(full, UPLOAD_DIR)
            meta_dir = os.path.join(META_DIR, rel)
            if os.path.exists(meta_dir):
                shutil.rmtree(meta_dir)
        return jsonify({'success': True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': ""}), 500

@app.route('/share/share_put', methods=['POST'])
@isadmin
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
        print(e,flush=True)
        abort(404)
    if not os.path.isfile(full): abort(404)
    
    dirname = os.path.dirname(full)
    filename = os.path.basename(full)
    resp = make_response(send_from_directory(dirname, filename, as_attachment=True))
    resp.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return resp


@app.route('/api/clear-all', methods=['DELETE'])
@login_required
@isadmin
@isa
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
@isadmin
def download_file(file_path):
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

def generate_tree(path_str, n=0):
    tree_str = ""
    path = Path(path_str).resolve()
    if not path.exists():
        return f"路径不存在: {path_str}\n"
    try:
        if path.is_file():
            tree_str += '    |' * n + '-' * 4 + path.name + '\n'
        elif path.is_dir():
            if n == 0:
                tree_str += str(path) + '\\\n'
            else:
                tree_str += '    |' * n + '-' * 4 + path.name + '\\\n'
            for child in sorted(path.iterdir()):
                tree_str += generate_tree(str(child), n + 1)
    except PermissionError:
        tree_str += '    |' * n + '-' * 4 + f"[权限不足] {path.name}\n"
    except Exception as e:
        tree_str += '    |' * n + '-' * 4 + f"[错误: {e}]\n"
    return tree_str

def create_file(filename):
    with open(filename, 'a'):
        os.utime(filename, None)




# ==================== 服务器控制台（修复版） ====================
import struct
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def recv_exact(sock, n):
    """精确接收 n 字节数据"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def listen_encrypted(sock, private_key):
    """
    接收 长度(4字节大端) + 密文，用私钥解密
    返回明文字节串
    """
    raw_len = recv_exact(sock, 4)
    if raw_len is None:
        return b""
    length = struct.unpack('>I', raw_len)[0]
    encrypted = recv_exact(sock, length)
    if encrypted is None:
        return b""
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(encrypted)

def send_plain(sock, msg: str):
    """明文发送字符串，末尾加换行符"""
    sock.sendall((msg + '\0').encode())

def w(port):
    global admin, users, app
    private_key = RSA.generate(1024)          # 认证用，注意1024位密钥OAEP最大明文约86字节
    public_key = private_key.publickey()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    time.sleep(1)

    while True:
        print('等待管理连接...', flush=True)
        login_r = False
        sf, client_addr = s.accept()
        print(f"新连接来自 {client_addr}", flush=True)

        try:
            # 1. 发送公钥（长度前缀 + 公钥数据）
            pub_bytes = public_key.export_key()
            sf.sendall(struct.pack('>I', len(pub_bytes)))
            sf.sendall(pub_bytes)

            # 2. 接收并解密认证信息
            encrypted_auth = listen_encrypted(sf, private_key)
            auth_str = encrypted_auth.decode()
            nm = auth_str.split(',')

            if nm[0] == admin and check_password_hash(users.get(nm[0], ''), nm[1]):
                send_plain(sf, "y")
                print('认证成功', flush=True)
                login_r = True
            else:
                print(f"认证失败: {nm}", flush=True)
                send_plain(sf, "n")
                sf.close()
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
                # 接收加密的命令
                encrypted_cmd = listen_encrypted(sf, private_key)
                if not encrypted_cmd:
                    break
                cmd = encrypted_cmd.decode()

                print(f"命令: {cmd}", flush=True)
                logging.info(f"exec: {cmd.split(' ')[0:2]}")

                if cmd == "</c>":
                    send_plain(sf, "bye")
                    sf.shutdown(socket.SHUT_RDWR)
                    sf.close()
                    break
                if cmd in ("exit", "\\", "q"):
                    keys = r.keys(f"{TASK_PREFIX}*")
                    print(keys,flush=True)
                        
                    os._exit(0)
                elif cmd.lower().startswith("ls"):
                    path_part = cmd.replace("ls", "", 1).strip()
                    tree = generate_tree(os.path.join(BASE_DIR, "uploads", path_part))
                    send_plain(sf, tree)

                elif cmd == "load":
                    load_html()
                    send_plain(sf, "load ok")
                elif cmd.lower().startswith('debug'):
                    ddd = cmd.lower().replace("debug", "").strip()
                    if ddd == "open":
                        create_file(os.path.join(BASE_DIR, "de.lock"))
                        app.debug = True
                    elif ddd == "close":
                        if os.path.exists(os.path.join(BASE_DIR, "de.lock")):
                            os.remove(os.path.join(BASE_DIR, "de.lock"))
                        app.debug = False
                    send_plain(sf, f"debug mode {'open' if app.debug else 'close'} ok")

                elif cmd.lower().startswith("adduser"):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 3:
                        username, password = parts[1], parts[2]
                        users[username] = generate_password_hash(password)
                        user_list.append(username)
                        send_plain(sf, f"用户 {username} 已添加")
                        save_user()
                    else:
                        send_plain(sf,f'error,{username} in not found')

                elif cmd.lower().startswith("deluser"):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username in users and username in user_list:
                            del users[username]
                            user_list.remove(username)
                            send_plain(sf, f"用户 {username} 已删除")
                            save_user()
                        elif username in users and username in nigga_list:
                            del users[username]
                            nigga_list.remove(username)
                            send_plain(sf, f"用户 {username} 已删除")
                            save_user()
                        else:
                            send_plain(sf, "用户不存在")

                elif cmd.lower().startswith("listuser"):
                    info = ["当前用户列表:"]
                    for user in users.keys():
                        role = ""
                        if user in nigga_list:
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

                elif cmd.lower().startswith("addnigga"):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username not in users:
                            send_plain(sf, f"{username} 不存在")
                        elif username not in nigga_list:
                            nigga_list.append(username)
                            if username in user_list:
                                user_list.remove(username)
                            send_plain(sf, f"用户 {username} 已移入黑名单")
                            save_user()

                elif cmd.lower().startswith("delnigga"):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username not in users:
                            send_plain(sf, f"{username} 不存在")
                        elif username in nigga_list:
                            nigga_list.remove(username)
                            if username not in user_list:
                                user_list.append(username)
                            send_plain(sf, f"用户 {username} 已移出黑名单")
                            save_user()

                elif cmd.lower().startswith("setadmin"):
                    parts = [p for p in cmd.split() if p]
                    if len(parts) == 2:
                        username = parts[1]
                        if username not in users:
                            send_plain(sf, f"{username} 不存在")
                        elif username in user_list:

                            admin = username
                            send_plain(sf, f"用户 {username} 已设为管理员")
                            save_user()

                elif app.debug and cmd.lower().startswith("get"):
                    parts = cmd.split()
                    try:
                        send_plain(sf, str(globals()[parts[1]]))
                    except KeyError:
                        send_plain(sf, f"变量 {parts[1]} 不存在")
                elif cmd.lower() == 'update':
                    while True:
                        sm = random.randint(6000,6050)
                        if not is_port_in_use(sm):
                            break
                    a = Thread(target=update_file,args=(client_addr,sm),daemon=True)
                    a.start()
                    send_plain(sf,str(sm))
                else:
                    send_plain(sf, "未知命令")
            except Exception as e:
                traceback.print_exc()
                logging.error(f"命令执行错误: {e}")
                try:
                    send_plain(sf, f"error: {e}")
                except:
                    break
        # 连接关闭后继续等待新连接


def update_file(ip, sm):
    # 直接绑定 0.0.0.0 避免地址错误
    a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    a.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    a.bind(('0.0.0.0', sm))
    a.listen(1)
    sd, addr = a.accept()
    try:
        md = sd.recv(8192).decode()
        file_name, file_size = md.split(";")
        file_size = int(file_size)
        sd.send(b"ok")  # 发送确认

        received = 0
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, 'wb') as fw:
            while received < file_size:
                data = sd.recv(min(2048, file_size - received))
                if not data:
                    break
                # 处理末尾的 \0
                if received + len(data) >= file_size:
                    # 可能是最后一块数据，包含 \0
                    # 简单做法：不发送 \0，靠长度判断结束
                    if data.endswith(b'\0'):
                        data = data.removesuffix(b'\0')
                fw.write(data)
                received += len(data)
        sd.send(b'ok')   # 发送成功确认
    except Exception as e:
        print(f"上传错误: {e}", flush=True)
        # 可以向客户端发送错误信息
    finally:
        sd.close()
        a.close()
            
a = FileLock(os.path.join(BASE_DIR,'pro.lock'))


if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey("ctrl+n",os._exit,args=(0,))
if __name__ == '__main__':
    print(f"🌐 启动：http://0.0.0.0:5000\n访问http://{socket.gethostbyname(socket.gethostname())}:5000", flush=True)
    if os.path.exists(os.path.join(BASE_DIR,"de.lock")):
        app.debug = True
        HTML_TEMPLATE += "<br/>\n<a href=\"/api/new\">new</a>"
    while True:
        sm = random.randint(6000,6050)
        if not is_port_in_use(sm):
            break
    sm = 7060
    print(f"管理端口链接:{socket.gethostbyname(socket.gethostname())}:{sm}",flush=True)
    logging.info(f"管理端口链接:{socket.gethostbyname(socket.gethostname())}:{sm}")
    s = Thread(target=w, daemon=True,args=(sm,))
    s.start()
    app.run("0.0.0.0", 5000, use_reloader=False,use_evalex=False)
else:

    try:
        a.acquire(timeout=0)          # a 是你上面创建的 FileLock 对象
    except Exception:                 # 拿不到锁说明别的 worker 已经启动了管理服务
        print("[Worker] 管理端口已由其他 worker 负责，本进程跳过。", flush=True)
    else:
        # 本 worker 抢到了锁，负责启动管理端口
        while True:
            sm = random.randint(6000, 6050)
            if not is_port_in_use(sm):
                break
        sm = 7060                     # 你最终强制使用的端口，建议直接固定
        print(f"管理端口链接: {socket.gethostbyname(socket.gethostname())}:{sm}", flush=True)
        logging.info(f"管理端口链接: {socket.gethostbyname(socket.gethostname())}:{sm}")

        s = Thread(target=w, daemon=True, args=(sm,))
        s.start()