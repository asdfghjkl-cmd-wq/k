"""
文件上传服务 - 含大文件分卷上传（修复版）
修复内容：
1. 集成过期分卷会话清理，防止内存/磁盘泄漏（每5分钟清理一次）。
2. 使用绝对路径读取 HTML 模板，避免工作目录变更导致热重载失败。
3. 对大文件上传 API 增加必要的校验与错误处理。
4. 优化并发控制，避免进度计数异常（前端已建议修复，此处确保后端稳健）。
5. 引入 CSRF 保护（Flask-WTF）。
"""
import pickle

from markupsafe import escape
import magic
import zipfile, requests
from threading import Thread, Lock, Event
from queue import Queue
from urllib.parse import urlparse
import logging
import tool.u1
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
import tool.u2

from flask_wtf.csrf import CSRFProtect, CSRFError

# 禁用不安全的请求警告（针对 verify=False）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_filename_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')[-1]

# ==================== 异步任务系统 ====================
task_store = {}          # { task_id: { 'status':..., 'error':..., 'tool_id':..., 'progress':{'total':0,'current':0}, 'cancel_event':Event() } }
task_store_lock = Lock()

MAX_WORKERS = 2
task_queue = Queue()
def save_user():
    global user_list,nigga_list,users,admin
    try:
        n = {
            "ud":users,
            'ul':user_list,
            'nl':nigga_list,
            "admin":admin
        }
        with open(f"{BASE_DIR}\\user.pkl","wb") as d:
            pickle.dump(n,d)
        
    except: 
        print("save over",flush=True)

def load_user():
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', name)
    ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD', password))
    users = {ADMIN_USERNAME: ADMIN_PASSWORD_HASH}
    users["admina"] = generate_password_hash("aadmin123")
    nigga_list = ["admina"]
    user_list = [os.environ.get('ADMIN_USERNAME', name)]
    admin = os.environ.get('ADMIN_USERNAME', name)
    try:
        with open(f"{BASE_DIR}\\user.pkl","rb") as l:
            n = dict(pickle.load(l))
        users = n.get("ud")
        user_list = n.get("ul")
        nigga_list = n.get("nl")
        admin = n.get('admin')
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', name)
        ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD', password))
        return users,user_list,nigga_list,admin
    except:
        return users,user_list,nigga_list,admin

def worker():
    while True:
        task_id, func, base_args, tool_id = task_queue.get()
        if task_id is None:
            break
        with task_store_lock:
            task_store[task_id]['status'] = 'running'
        try:
            with app.app_context():
                if tool_id == 6:   # 下载任务
                    func(*base_args, task_id=task_id, cancel_event=task_store[task_id]['cancel_event'])
                else:
                    func(*base_args)
            with task_store_lock:
                task_store[task_id]['status'] = 'finished'
        except Exception as e:
            traceback.print_exc()
            with task_store_lock:
                if task_store[task_id]['cancel_event'].is_set():
                    task_store[task_id]['status'] = 'cancelled'
                else:
                    task_store[task_id]['status'] = 'failed'
                    task_store[task_id]['error'] = str(e)
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
    MAX_CONTENT_LENGTH=200 * 1024 * 1024,
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
name = ran_str(4)
password = ran_str(8)
print("name:", name, "\n", "password:", password, "\n", flush=True)

users,user_list,nigga_list,admin = load_user()
# ==================== 全局 HTML 模板 ====================
HTML_TEMPLATE = ""

def load_html():
    global HTML_TEMPLATE
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            HTML_TEMPLATE = f.read()
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
                return "no admin",403
        return f(*args, **kwargs)
    return wrap

def safe_path(*parts):
    target = os.path.realpath(os.path.join(UPLOAD_DIR, *parts))
    if not target.startswith(os.path.realpath(UPLOAD_DIR) + os.sep):
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

def zipe(file: str, dir):
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
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.infolist():
                member_path = os.path.realpath(os.path.join(target_dir, member.filename))
                if not member_path.startswith(target_dir + os.sep) and member_path != target_dir:
                    raise Exception(f"Zip Slip 攻击检测: {member.filename}")
            zf.extractall(target_dir)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        app.logger.error(f"解压失败: {e}")
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)
        raise


def download(url,dir, task_id, cancel_event):
    """下载文件，支持进度更新和取消"""
    filepath = None
    try:
        filename = get_filename_from_url(url)
        filepath = os.path.join(UPLOAD_DIR, dir ,filename)
        resp = requests.get(url, stream=True, timeout=10, verify=False)
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))

        with task_store_lock:
            task_store[task_id]['progress'] = {'total': total, 'current': 0}

        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if cancel_event.is_set():
                    resp.close()
                    raise Exception("下载被取消")
                if chunk:
                    f.write(chunk)
                    with task_store_lock:
                        task_store[task_id]['progress']['current'] += len(chunk)
    except Exception as e:
        logging.error(f"下载错误: {e}")
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
        logging.warning(f"user login failure.from {request.remote_addr} user:{username},password:{password}")
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    logging.info("user logout")
    return redirect(url_for('login'))

@app.route("/loginok")
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



@app.route('/')
@login_required
def index():

    return render_template_string(HTML_TEMPLATE, username=session.get('user_id',''))

@app.route('/api/task/<task_id>', methods=['GET'])
@isadmin
@login_required
def get_task_status(task_id):
    with task_store_lock:
        task = task_store.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '无效任务ID'}), 404
    return jsonify({
        'success': True,
        'status': task['status'],
        'error': task.get('error', ''),
        'tool_id': task['tool_id'],
        'progress': task.get('progress', {})
    })

@app.route('/api/task/<task_id>/cancel', methods=['POST'])
@isadmin
@login_required
def cancel_task(task_id):
    with task_store_lock:
        task = task_store.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '无效任务ID'}), 404
    if task['status'] not in ('running', 'pending'):
        return jsonify({'success': False, 'error': '任务无法取消'}), 400
    task['cancel_event'].set()
    return jsonify({'success': True})

@app.route("/move", methods=['POST'])
@isadmin
@login_required
def move():
    try:
        data = request.get_json()
        if not data:
            abort(400)
        source = data["source"]
        target = data["target"]

    except (KeyError, TypeError):
        abort(400)

    try:
        src = safe_path(source)
        dst = safe_path(target)
    except ValueError:
        return "错误: 目录越权", 400

    if not os.path.exists(src):
        return "源路径不存在", 404

    try:
        if os.path.isfile(src):
            # 移动文件：shutil.move 会自动处理目标为目录或文件的情况
            shutil.move(src, dst)
        elif os.path.isdir(src):
            
            shutil.move(src, dst)
        else:
            return "源路径类型未知", 400
        return "移动成功", 200
    except Exception as e:
        logging.error(f"移动失败: {e}")
        return "移动失败", 500
        
@app.route("/copy", methods=['POST'])
@isadmin
@login_required
def copy():
    try:
        data = request.get_json()
        if not data:
            abort(400)
        source = data["source"]
        target = data["target"]

    except (KeyError, TypeError):
        abort(400)

    try:
        src = safe_path(source)
        dst = safe_path(target)
    except ValueError:
        return "错误: 目录越权", 400

    if not os.path.exists(src):
        return "源路径不存在", 404

    try:
        if os.path.isfile(src):
            # 移动文件：shutil.move 会自动处理目标为目录或文件的情况
            shutil.copy(src, dst)
        elif os.path.isdir(src):
            
            shutil.copytree(src, dst)
        else:
            return "源路径类型未知", 400

        return "复制成功",200
    except Exception as e:
        logging.error(f"复制失败: {e}")
        return "复制失败", 500

    

    

@app.route("/toolcall", methods=['POST'])
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
        elif tool_id == 4:
            func = time.sleep
            arg_list = (10,)
        elif tool_id == 5:
            func = zipe
            arg_list = (clean,safe_dir)
        elif tool_id == 6:
            func = download
            arg_list = (clean,safe_dir)  

        else:
            return jsonify({'success': False, 'error': '未知工具'}), 404

        task_id = str(uuid.uuid4())
        with task_store_lock:
            task_store[task_id] = {
                'status': 'pending',
                'error': '',
                'tool_id': tool_id,
                'progress': {'total': 0, 'current': 0},
                'cancel_event': Event(),
                'path': a.get("path")
            }
        task_queue.put((task_id, func, arg_list, tool_id))
        return jsonify({'success': True, 'task_id': task_id}), 202

    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))
        traceback.print_exc()
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/upload', methods=['POST'])
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

@app.route("/new")
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
    rel_path = request.args.get('path', '').strip()
    try:
        target_dir = safe_path(rel_path) if rel_path else UPLOAD_DIR
    except ValueError:
        return jsonify({'success': False, 'error': '非法路径'}), 400
    if not os.path.isdir(target_dir):
        return jsonify({'success': False, 'error': '路径不存在'}), 404
    items = []
    mine = magic.Magic(mime=True)
    try:
        for name in os.listdir(target_dir):
            if name.startswith('.') or name == 'metadata' or name == 'chunks': continue
            full = os.path.join(target_dir, name)
            n = str(full)
            is_dir = os.path.isdir(full)
            if os.path.isfile(full):
                with open(full,"rb") as d:
                    g = d.read(2048)
                    type_file = mine.from_buffer(g)
            else:type_file = ""
            
            info = {} if is_dir else (get_file_info(full) or {})
            items.append({
                'name': escape(name),
                'type': 'directory' if is_dir else 'file',
                'size': info.get('size', 0),
                'modified': info.get('modified', ''),
                'type_file': type_file
            })
        items.sort(key=lambda x: (0 if x['type']=='directory' else 1, x['name'].lower()))
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': "see log"}), 500
    print(items,flush=True)
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

@app.route('/share_put',methods=["POST"])
@isadmin
@login_required
def share_put():
    global share_dict

    a = dict(request.json)
    file = a.get('file')
    u =str(uuid.uuid4())
    share_dict[u] = file
    host = request.host_url
    return jsonify({"link": str(host+"share_get/"+u)})

@app.route('/share_get/<path:uuid>')
def down(uuid):
    try:
        file_path = share_dict.get(uuid,"")
    except:
        abort(404)
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


@app.route('/api/clear-all', methods=['DELETE'])
@login_required
@isadmin
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
    return redirect(url_for('login'))

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

def restart_service():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def fix_userl():
    for user in users.keys():
        if user not in nigga_list:
            if user not in user_list:
                user_list.append(user)

    a = 0
    for user in user_list:
        if user in nigga_list:
            nigga_list.remove(user)
        if user_list.count(user) != 1:
            user_list.pop(a)
        if user not in users:
            user_list.remove(user)
        a += 1
    a = 0
    for user in nigga_list:
        if nigga_list.count(user) != 1:
            nigga_list.pop(a)
        if user not in users:
            nigga_list.remove(user)
        a += 1
    print("fix")



def w():
    time.sleep(1)
    while True:
        if len(nigga_list)+len(user_list) != len(users):fix_userl()

        a = input("exec:").strip()
        logging.info(f"exec:{a.split(" ")[0:2]}")
        try:
            if a == "exit" or a == "\\" or a == "q":
                os._exit(0)
            elif a.lower().startswith("ls"):
                sss = generate_tree(os.path.join(BASE_DIR,"uploads",a.replace("ls","").strip()))
                print(sss)
            elif a == "load":
                load_html()
                print("fuck",flush=True)
            elif a.lower().startswith('debug'):
                ddd = a.lower().replace("debug","").strip()
                if ddd == "open":
                    create_file(os.path.join(BASE_DIR,"de.lock"))
                    restart_service()
                elif ddd == "close":
                    if os.path.exists(os.path.join(BASE_DIR,"de.lock")):
                        os.remove(os.path.join(BASE_DIR,"de.lock"))
                    restart_service()
            elif a.lower() == "restart":
                restart_service()
            elif a.lower().startswith("adduser"):
                n = a.split(" ")
                for i in range(len(n)):
                 if n[i] == "":
                     n.pop(i)
                if len(n) == 3:
                    username = n[1]
                    password = n[2]
                    users[username] = generate_password_hash(password)
                    user_list.append(username)
                    print(f"用户 {username} 已添加")
                    save_user()
            elif a.lower().startswith("deluser"):
                n = a.split(" ")
                for i in range(len(n)):
                 if n[i] == "":
                     n.pop(i)
                if len(n) == 2:
                    username = n[1]
                    if username in users and username in user_list:
                        del users[username]
                        user_list.remove(username)
                        print(f"用户 {username} 已删除")
                        save_user()
                    if username in users and username in nigga_list:
                            del users[username]
                            nigga_list.remove(username)
                            print(f"用户 {username} 已删除")
                            save_user()

            elif a.lower().startswith("listuser"):
                global admin
                print("当前用户列表:")
                for user in users.keys():
                    a = ""
                    if user in nigga_list:a += " forbid"
                    elif user in user_list:a += " authorized"
                 
                    else:user_list.append(user);a += " authorized"
                    if user == admin:a += " admin"
                    print(f"--{user} {a}")
                save_user()
                
            elif a.lower().startswith("addnigga"):
                n = a.split(" ")
                for i in range(len(n)):
                    if n[i] == "":
                        n.pop(i)
                    if len(n) == 2:
                        username = n[1]
                        if username not in users:
                            print(f"{username}不存在")
                        elif username not in nigga_list:
                            nigga_list.append(username)
                            user_list.remove(username)
                            print(f"用户 {username} 已移入黑名单")
                            save_user()
            elif a.lower().startswith("delnigga"):
                n = a.split(" ")
                for i in range(len(n)):
                    if n[i] == "":
                        n.pop(i)
                if len(n) == 2:
                    username = n[1]
                    if username not in users:
                        print(f"{username}不存在")
                    elif username not in user_list:
                        nigga_list.remove(username)
                        user_list.append(username)
                        print(f"用户 {username} 已移出黑名单")
                        save_user()
            elif a.lower().startswith("setadmin"):
                n = a.split(" ")
                for i in range(len(n)):
                    if n[i] == "":
                        n.pop(i)
                if len(n) == 2:
                    username = n[1]
                    if username not in users:
                        print(f"{username}不存在")
                    elif username in user_list :
                        admin = username
                        print(f"用户 {username} 已设为管理员")
                        save_user()
            elif app.debug and a.lower().startswith("get") :
                n = a.split(" ")
                print(eval(n[1]),flush=True)
            
            else: print("not found")
        except Exception as e:
            traceback.print_exc()
            logging.error(f"exec error:{str(e)}")
import keyboard
keyboard.add_hotkey("ctrl+n",os._exit,args=(0,))
if __name__ == '__main__':
    print(f"🌐 启动：http://0.0.0.0:5000", flush=True)
    if os.path.exists(os.path.join(BASE_DIR,"de.lock")):
        app.debug = True
    s = Thread(target=w, daemon=True)
    s.start()
    app.run("0.0.0.0", 5000, use_reloader=False)