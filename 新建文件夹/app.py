"""
文件上传服务 - 含大文件分卷上传（修复版）
修复内容：
1. 集成过期分卷会话清理，防止内存/磁盘泄漏（每5分钟清理一次）。
2. 使用绝对路径读取 HTML 模板，避免工作目录变更导致热重载失败。
3. 对大文件上传 API 增加必要的校验与错误处理。
4. 优化并发控制，避免进度计数异常（前端已建议修复，此处确保后端稳健）。
5. 引入 CSRF 保护（Flask-WTF）。
"""


import zipfile,requests

from threading import Thread,Lock

from queue import Queue
from urllib.parse import urlparse

import logging
import tool.u1
from string import ascii_lowercase,ascii_letters
from flask import (Flask, request, jsonify, render_template_string,
                   make_response, send_from_directory, session, redirect, url_for, abort)
import random
from flask_cors import CORS
import os, sys, json, traceback, shutil, re, uuid, time
from datetime import datetime
from urllib.parse import quote
from werkzeug.security import generate_password_hash, check_password_hash

import tool.u2

# 引入 Flask-WTF CSRF 保护
from flask_wtf.csrf import CSRFProtect, CSRFError


def get_filename_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')[-1]
def get_file_size(url):
    response = requests.head(url)
    return int(response.headers.get('content-length', 0))

# 任务状态存储 { task_id: { 'status': 'pending'|'running'|'finished'|'failed', 'result': str, 'error': str } }
task_store = {}
task_store_lock = Lock()

# 简单的线程池控制（限制同时执行的任务数）
MAX_WORKERS = 2
task_queue = Queue()

def worker():
    while True:
        task_id, func, args,id = task_queue.get()
        if task_id is None:
            break
        with task_store_lock:
            task_store[task_id]['status'] = 'running'
        try:
            # 工具函数需要应用上下文才能正常使用 app.logger 等
            with app.app_context():
                func(*args)
            with task_store_lock:
                task_store[task_id]['status'] = 'finished'
        except Exception as e:
            traceback.print_exc()
            with task_store_lock:
                task_store[task_id]['status'] = 'failed'
                task_store[task_id]['error'] = str(e)
        finally:
            task_queue.task_done()

# 启动工作线程
for _ in range(MAX_WORKERS):
    t = Thread(target=worker, daemon=True)
    t.start()


from functools import wraps
ascii_lowercase += "0123456789"
ascii_letters += "0123456789"
# ==================== 初始化 ====================
if sys.platform.startswith('win'):
    import io, locale
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    try: locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except: pass

def ran_str(len,j=ascii_lowercase):
    
    x = ""
    ascii_lowercase = j
    

    for _ in range(len):
        
        x += random.choice(ascii_lowercase)
    return x

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'a.html')

try:
    s=open(os.path.join(BASE_DIR,"s.key"),"r",encoding="utf-8")
    k = s.read()
except:
    k = ran_str(128,ascii_letters)
    s= open(os.path.join(BASE_DIR,"s.key"),"w",encoding="utf-8")
    s.write(k)
s.close()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=os.path.join(BASE_DIR,"app.log")
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

    MAX_CONTENT_LENGTH=200 * 1024 * 1024,  # 单分片最大200MB（按需调整）
    UPLOAD_FOLDER=os.path.join(BASE_DIR, 'uploads'),
    SECRET_KEY=os.environ.get('SECRET_KEY', k),
    JSON_AS_ASCII=False
)

# 初始化 CSRF 保护
csrf = CSRFProtect(app)

logging.info("flask create ok")

UPLOAD_DIR = os.path.abspath(app.config['UPLOAD_FOLDER'])
CHUNK_DIR = os.path.join(UPLOAD_DIR, 'chunks')  # 分片临时目录
META_DIR = os.path.join(UPLOAD_DIR, 'metadata')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)


name = ran_str(4)
password = ran_str(8)
print("name:",name,"\n","password:",password,"\n",flush=True)

total_size=okay_size = 0
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', name)
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD', password))

users = {ADMIN_USERNAME: ADMIN_PASSWORD_HASH}

print(ADMIN_USERNAME == name)



# 全局 HTML 模板内容（支持热重载）
HTML_TEMPLATE = ""

def load_html():
    """读取 HTML 模板，出错时保留旧内容"""
    global HTML_TEMPLATE
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            HTML_TEMPLATE = f.read()
    except Exception as e:
        print(f"[WARN] 无法加载模板 {HTML_FILE}: {e}")

load_html()  # 初次加载
logging.info("html load ok")
# ==================== 后台线程：清理过期会话 + 模板热重载 ====================
def download(url):
    global total_size,okay_size
    total_size=okay_size = 0
    try:
        filenr = get_filename_from_url(url=url)
        filename = os.path.join(UPLOAD_DIR,filenr)

        total_size = get_file_size(url)
        response = requests.get(url, stream=True,timeout=10,verify=False)
        response.raise_for_status()
        
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                
                if chunk:
                    okay_size += 8192
                    file.write(chunk)
        return ""
    except requests.exceptions.RequestException as e:
        logging.error("download error:"+str(e))
        total_size=okay_size = 0
        raise Exception("download error")
    finally:
        total_size=okay_size = 0

def background_tasks():
    
    global HTML_TEMPLATE
    
    while True:
        print("exec therad",flush=True)
        time.sleep(300)  # 每5分钟执行一次
        # 清理过期分卷会话
        cleanup_expired_sessions()
        # 热重载 HTML 模板
        try:
            with open(HTML_FILE, "r", encoding="utf-8") as f:
                new_tpl = f.read()
            if HTML_TEMPLATE != new_tpl:
                HTML_TEMPLATE = new_tpl
                print("[INFO] 模板已热重载")
        except Exception as e:
            print(f"[WARN] 模板重载异常: {e}")

if app.debug:
    pass
else:
    bg_thread = Thread(target=background_tasks, daemon=True)
    bg_thread.start()

# ==================== 工具函数 ====================
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):

        if 'user_id' not in session:
            if (request.is_json or
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.path.startswith('/api/')):
                return jsonify({'success': False, 'error': '请先登录'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return wrap

def safe_path(*parts):
    target = os.path.normpath(os.path.join(UPLOAD_DIR, *parts))
    if not os.path.abspath(target).startswith(os.path.abspath(UPLOAD_DIR)):
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



def zipe(file: str):
    """
    解压指定的 zip 文件到 uploads 目录下，自动创建与 zip 同名的子目录。
    如果目标目录已存在，会自动追加数字后缀避免覆盖。
    """
    # 1. 获取安全的绝对路径并检查文件是否存在
    zip_path = safe_path(file)
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"文件不存在: {file}")

    # 2. 生成目标目录名：去掉 .zip 后缀（只处理 .zip，忽略大小写）
    basename = os.path.basename(zip_path)
    if basename.lower().endswith('.zip'):
        dir_name = basename[:-4]  # 去掉后4个字符 ".zip"
    else:
        dir_name = basename  # 不是 .zip 就原样当目录名

    if not dir_name:           # 极端情况：文件名就是 ".zip"
        dir_name = "extracted"

    # 3. 保证目录不重名（已在循环外处理）
    target_base = os.path.join(UPLOAD_DIR, dir_name)
    target_dir = target_base
    counter = 1
    while os.path.exists(target_dir):
        target_dir = f"{target_base} ({counter})"
        counter += 1
        if counter > 1000:  # 防意外死循环
            ts = int(time.time() * 1000) % 1000000
            target_dir = f"{target_base}_{ts}"
            break

    # 4. 创建目录并解压
    try:
        os.makedirs(target_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(target_dir)
        app.logger.info(f"解压完成: {file} -> {target_dir}")
    except Exception as e:
        app.logger.error(f"解压失败: {e}")
        # 清理可能已创建的目录
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)
        raise




# ==================== 分卷上传会话管理 ====================
chunk_sessions = {}  # { session_id: { 'filename':..., 'folder':..., 'total':..., 'received':set(), 'created':timestamp } }

def cleanup_expired_sessions():
    """清理超过1小时未完成的会话"""
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
<div class="info">默认: admin / admin123</div></div></body></html>
'''


# 不再从文件读取，改用全局变量 HTML_TEMPLATE（由 load_html 及后台线程维护）

# ==================== 原有路由 ====================
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

@app.route('/')
@login_required
def index():
    return render_template_string(HTML_TEMPLATE, username=session.get('user_id',''))

@app.route('/api/task/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    global total_size,okay_size
    with task_store_lock:
        task = task_store.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '无效任务ID'}), 404
    return jsonify({
        'success': True,
        'status': task['status'],
        'error': task.get('error', ''),
        'total_size': total_size,
        'okay_size': okay_size
    })




@app.route("/toolcall", methods=['POST'])
@login_required
def call_tool():
    try:
        a = request.json
        logging.info(f"call_tool {a}")
        tool_id = a.get("tool")
        args_raw = a.get("args", "").strip()

        # 清理参数中的多余 uploads 前缀（统一转为相对路径）
        def clean_arg(s):
            s = s.replace('\\', '/').strip().strip("'\"")
            if s.lower().startswith('uploads/'):
                s = s[len('uploads/'):]
            elif s.lower() == 'uploads':
                s = ''
            if s == '.':
                s = ''  # 当前目录用空字符串表示
            return s

        clean = clean_arg(args_raw)

        if tool_id == 1:   # Assembly（u2.call）
            func = tool.u2.call
            # u2.call 需要源目录（里面包含 file 及 data 分片）的绝对路径，以及目标目录
            arg_list = (safe_path(clean), os.path.join(".", "uploads"))
        elif tool_id == 2: # Cut（u1.call）
            m = re.search(r'-c\s+(\S+)\s+-f\s+(.+)', args_raw)
            if not m:
                return jsonify({'success': False, 'error': '参数格式错误'}), 400
            chunk_size = int(m.group(1))
            file_path = m.group(2)
            fp_clean = clean_arg(file_path)
            func = tool.u1.call
            arg_list = (safe_path(fp_clean), chunk_size,
                        os.path.join(".", "uploads", os.path.basename(fp_clean)))
        elif tool_id == 3:
            return jsonify({'success': True, 'message': '使用Assembly以合成文件\n使用cut以分割文件,用法 -c 分割块大小 -f 文件目录'}), 201
        elif tool_id == 4:
            func = time.sleep
            arg_list = (10,)

        elif tool_id == 5:
            func = zipe
            arg_list = (clean,)
        elif tool_id == 6:
            func = download
            arg_list = (clean,)

        else:
            return jsonify({'success': False, 'error': '未知工具'}), 404

        # 提交异步任务
        task_id = str(uuid.uuid4())
        with task_store_lock:
            task_store[task_id] = {'status': 'pending', 'result': '', 'error': ''}
        task_queue.put((task_id, func, arg_list,tool_id))
        return jsonify({'success': True, 'task_id': task_id}), 202

    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


@app.route('/upload', methods=['POST'])
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
"""
@app.route('/tools')
@login_required
def call_tools():
    tool = request.args.get()
"""

@app.route("/new")

def sssss():
    if app.debug:
    # 热重载 HTML 模板
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
    try:
        for name in os.listdir(target_dir):
            if name.startswith('.') or name == 'metadata' or name == 'chunks': continue
            full = os.path.join(target_dir, name)
            is_dir = os.path.isdir(full)
            info = {} if is_dir else (get_file_info(full) or {})
            items.append({
                'name': name,
                'type': 'directory' if is_dir else 'file',
                'size': info.get('size', 0),
                'modified': info.get('modified', '')
            })
        items.sort(key=lambda x: (0 if x['type']=='directory' else 1, x['name'].lower()))
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': "see log"}), 500
    return jsonify({'success': True, 'data': items})

@app.route('/api/folders', methods=['POST'])
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
                # 尝试清理空文件夹
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

@app.route('/api/clear-all', methods=['DELETE'])
@login_required
def clear_all():
    try:
        for name in os.listdir(UPLOAD_DIR):
            if name == 'metadata' or name == 'chunks': continue
            path = os.path.join(UPLOAD_DIR, name)
            if os.path.isfile(path): os.remove(path)
            else: shutil.rmtree(path)
        # 清理元数据文件夹
        if os.path.exists(META_DIR):
            shutil.rmtree(META_DIR)
            os.makedirs(META_DIR, exist_ok=True)
        # chunks 不清理（可能正在上传）
        return jsonify({'success': True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error':""}), 500

@app.route('/download/<path:file_path>')
@login_required
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

@app.route("/console")
def ss():
    abort(404)

if __name__ == "__main__":
    print(app.debug,flush=True)

# ==================== 大文件分卷上传 API ====================
@app.route('/api/chunk/init', methods=['POST'])
@login_required
def chunk_init():
    """初始化分卷上传会话"""
    data = request.get_json(silent=True)
    if not data or 'filename' not in data or 'totalChunks' not in data:
        return jsonify({'success': False, 'error': '缺少参数'}), 400
    original = data['filename']
    total = int(data['totalChunks'])
    if total <= 0:
        return jsonify({'success': False, 'error': '分片数无效'}), 400
    folder = data.get('folder', '').strip()
    session_id = str(uuid.uuid4())
    # 创建会话信息
    chunk_sessions[session_id] = {
        'filename': original,
        'folder': folder,
        'total': total,
        'received': set(),
        'created': time.time()
    }
    # 创建分片存储目录
    os.makedirs(os.path.join(CHUNK_DIR, session_id), exist_ok=True)
    return jsonify({'success': True, 'session_id': session_id})

@app.route('/api/chunk/upload', methods=['POST'])
@login_required
def chunk_upload():
    """接收一个分片"""
    session_id = request.form.get('session_id')
    chunk_index = request.form.get('chunk_index')
    if not session_id or chunk_index is None:
        return jsonify({'success': False, 'error': '缺少会话或分片序号'}), 400
    if session_id not in chunk_sessions:
        return jsonify({'success': False, 'error': '无效的会话ID'}), 404
    if 'chunk' not in request.files:
        return jsonify({'success': False, 'error': '没有分片数据'}), 400
    try:
        chunk_index = int(chunk_index)
    except:
        return jsonify({'success': False, 'error': '分片序号错误'}), 400
    session_info = chunk_sessions[session_id]
    if chunk_index < 0 or chunk_index >= session_info['total']:
        return jsonify({'success': False, 'error': '分片序号超出范围'}), 400

    # 幂等处理：如果该分片已上传，直接返回成功
    if chunk_index in session_info['received']:
        return jsonify({'success': True, 'received': len(session_info['received']), 'duplicate': True})

    chunk_file = request.files['chunk']
    chunk_path = os.path.join(CHUNK_DIR, session_id, f"{chunk_index:06d}.part")
    try:
        chunk_file.save(chunk_path)
        session_info['received'].add(chunk_index)
        return jsonify({'success': True, 'received': len(session_info['received'])})
    except Exception as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': f'分片保存失败: {"see log"}'}), 500

@app.route('/api/chunk/status', methods=['GET'])
@login_required
def chunk_status():
    """查询上传进度"""
    session_id = request.args.get('session_id')
    if not session_id or session_id not in chunk_sessions:
        return jsonify({'success': False, 'error': '无效会话'}), 404
    info = chunk_sessions[session_id]
    return jsonify({
        'success': True,
        'total': info['total'],
        'received': sorted(list(info['received'])),
        'finished': len(info['received']) == info['total']
    })

@app.route('/api/chunk/complete', methods=['POST'])
@login_required
def chunk_complete():
    """合并分片并清理"""
    data = request.get_json(silent=True)
    if not data or 'session_id' not in data:
        return jsonify({'success': False, 'error': '缺少会话ID'}), 400
    session_id = data['session_id']
    if session_id not in chunk_sessions:
        return jsonify({'success': False, 'error': '无效会话'}), 404
    info = chunk_sessions[session_id]
    if len(info['received']) != info['total']:
        return jsonify({'success': False, 'error': '还有分片未上传'}), 400

    # 合并文件
    try:
        target_dir = safe_path(info['folder']) if info['folder'] else UPLOAD_DIR
    except ValueError as e:
        logging.error(str(e))
        return jsonify({'success': False, 'error': f'目录非法: {"see log"}'}), 400
    
    os.makedirs(target_dir, exist_ok=True)
    filename = clean_filename(info['filename'])
    if os.path.exists(os.path.join(target_dir, filename)):
        filename = unique_name(filename, target_dir)
    filepath = os.path.join(target_dir, filename)

    session_dir = os.path.join(CHUNK_DIR, session_id)
    try:
        with open(filepath, 'wb') as fout:
            for i in range(info['total']):
                part_path = os.path.join(session_dir, f"{i:06d}.part")
                if not os.path.exists(part_path):
                    raise Exception(f"缺失分片 {i}")
                with open(part_path, 'rb') as fin:
                    # 分块读取避免大文件撑爆内存
                    while True:
                        chunk = fin.read(8192)
                        if not chunk:
                            break
                        fout.write(chunk)
        # 记录元数据
        size = os.path.getsize(filepath)
        rel = os.path.relpath(filepath, UPLOAD_DIR)
        save_meta(rel, info['filename'], size)
        # 清理临时文件
        shutil.rmtree(session_dir, ignore_errors=True)
        chunk_sessions.pop(session_id, None)
        return jsonify({'success': True, 'filename': filename, 'size': size})
    except Exception as e:
        traceback.print_exc()
        logging.error(str(e))
        return jsonify({'success': False, 'error': f'合并失败: {"see log"}'}), 500



@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return redirect(url_for('login'))

# CSRF 错误处理
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'success': False, 'error': 'CSRF验证失败'}), 400

from pathlib import Path

def generate_tree(path_str, n=0):
    """
    生成目录树字符串
    :param path_str: 路径字符串（会自动转为 Path 对象）
    :param n: 当前缩进级别（内部递归使用）
    """
    tree_str = ""
    path = Path(path_str).resolve()  # 转为绝对路径，避免相对路径混淆
    
    if not path.exists():
        return f"路径不存在: {path_str}\n"
    
    try:
        if path.is_file():
            tree_str += '    |' * n + '-' * 4 + path.name + '\n'
        elif path.is_dir():
            # 根目录或子目录标识
            if n == 0:
                tree_str += str(path) + '\\\n'
            else:
                tree_str += '    |' * n + '-' * 4 + path.name + '\\\n'
            
            # 递归处理子项
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

def w():
    time.sleep(1)
    while True:
        a = input("exec:").strip()
        logging.info(f"exec:{a}")
        try:
            if a == "exit":
                os._exit(0)
            elif a.lower().startswith("ls"):
                sss = generate_tree(os.path.join(".","uploads",a.replace("ls","")))
                print(sss)
            elif a.lower().startswith('debug'):
                ddd = a.lower().replace("debug","").strip()
                if ddd == "open":
                    create_file(os.path.join(BASE_DIR,"de.lock"))
                    restart_service()
                elif ddd == "close":
                    os.remove(os.path.join(BASE_DIR,"de.lock"))
                    restart_service()
            elif a.lower() == "restart":
                 restart_service()
            else:print("not found")

        except Exception as a:
            traceback.print_exc()
            logging.error(f"exec error:{str(a)}")

            


if __name__ == '__main__':
    print(f"🌐 启动：http://0.0.0.0:5000",flush=True)
    if os.path.exists(os.path.join(BASE_DIR,"de.lock")):
        app.debug = True

    s = Thread(target=w,daemon=True)
    s.start()
    app.run("0.0.0.0",5000  ,use_reloader=False)