# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

from io import BytesIO
import os
import sys
import tkinter as tk
import threading
import queue
from ls import *
from PIL import ImageTk, Image
import pickle
import pymsgbox
import base64
import pystray
from pystray import MenuItem
import time
import faulthandler

# 启用崩溃日志
with open("crash.log", "w") as f:
    faulthandler.enable(file=f)

appdata = os.environ["appdata"]
if not os.path.exists(f"{appdata}\\clipboard_viewer"):
    os.makedirs(f"{appdata}\\clipboard_viewer")

# ------------------- 数据存储类 -------------------
class clipbords_tk_dict:
    def __init__(self):
        self.dict = {}

    def set(self, index, format, data):
        # 图片对象序列化为 PNG 字节流
        if format == 'BITMAP' and isinstance(data, Image.Image):
            buf = BytesIO()
            data.save(buf, format='PNG')
            self.dict[index] = {"format": format, "data": buf.getvalue(), "is_image": True}
        else:
            self.dict[index] = {"format": format, "data": data}

    def get(self, index):
        entry = self.dict[index]
        if entry.get("is_image"):
            entry["data"] = Image.open(BytesIO(entry["data"]))
            del entry["is_image"]
        return entry

class h:
    def save_all(self):
        print("自动保存")
        self.save_ctd()
        self.save_config()
        if sls_status:
            schedule_save()

    def save_ctd(self):
        try:
            with open(f"{appdata}\\clipboard_viewer\\clipboard.save", "wb") as w:
                pickle.dump(ctd, w)
        except Exception as e:
            print("保存剪贴板失败:", e)

    def save_config(self):
        n = [sls_status, sls_time, exitt]
        try:
            with open(f"{appdata}\\clipboard_viewer\\config.save", "wb") as w:
                pickle.dump(n, w)
        except Exception as e:
            print("保存配置失败:", e)

    def read_ctd(self):
        if os.path.exists(f"{appdata}\\clipboard_viewer\\clipboard.save"):
            with open(f"{appdata}\\clipboard_viewer\\clipboard.save", "rb") as r:
                s = pickle.load(r)
        else:
            s = clipbords_tk_dict()
        # 过滤掉无效格式
        s.dict = {k: v for k, v in s.dict.items() if v.get("format") != "notf"}
        return s

    def read_config(self):
        if os.path.exists(f"{appdata}\\clipboard_viewer\\config.save"):
            with open(f"{appdata}\\clipboard_viewer\\config.save", "rb") as r:
                s = pickle.load(r)
        else:
            s = [False, 0, 2]
        return s[0], s[1], s[2]

# ------------------- 全局状态 -------------------
hs = h()
sls_status, sls_time, exitt = hs.read_config()
root = tk.Tk()
if sls_status:
    ctd = hs.read_ctd()
    print("自动保存已启用")
else:
    ctd = clipbords_tk_dict()

lds = False
last_ignore = 0
IGNORE_WINDOW = 300  # 300ms 内忽略自身写入触发的剪贴板变化
op = OperationClipboard()
clipboard_queue = queue.Queue()
exiting = False
lock = threading.Lock()

# ------------------- 界面初始化 -------------------
dataicon = dataicon= "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"
dedata = base64.b64decode(dataicon)
icn = Image.open(BytesIO(dedata))
ico = ImageTk.PhotoImage(icn)
def lll():
    root.deiconify()
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    root.attributes('-topmost', False)

n = (
    MenuItem("display windows", default=True, action=lll),
    MenuItem("setting", action=lambda: setting()),
    MenuItem("quit", action=lambda: quiti()),
)
icon = pystray.Icon("clipboard viewer", icon=icn, title="clipboard viewer", menu=n)
iconthread = threading.Thread(target=icon.run, daemon=True)
iconthread.start()

root.iconphoto(True, ico)
root.geometry("800x600+20+200")
root.title("Clipboards Viewer")
root.minsize(537, 417)

menu = tk.Menu(root)
menu.add_command(label="setting", command=lambda: setting())
menu.add_command(label="save", command=lambda: hs.save_all())
root.config(menu=menu)

listbox = tk.Listbox(root, bg="#FFFFFF", selectmode=tk.SINGLE)
display_frame = tk.Frame(root)
button_frame = tk.Frame(root)

flabel = tk.Label(display_frame, text="", anchor="w", justify="left")
dlabel = tk.Label(display_frame, text="", anchor="w", justify="left", wraplength=600)
ilabel = tk.Label(display_frame, text="", anchor="w", justify="left")
flabel.pack(fill="x", padx=5, pady=2)
dlabel.pack(fill="x", padx=5, pady=2)
ilabel.pack(fill="x", padx=5, pady=2)

listbox.bind("<<ListboxSelect>>", lambda e: display_set())

tk.Button(button_frame, text="删除", command=lambda: delete(listbox.curselection())).pack(pady=5)
tk.Button(button_frame, text="复制", command=lambda: get(listbox.curselection())).pack(pady=5)
bu = tk.Button(button_frame, text="启动/展示", command=lambda: start())
bu.pack(pady=5)
bu.pack_forget()

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=2)
root.columnconfigure((0, 1, 2), weight=1)
listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
button_frame.grid(row=0, column=2, sticky="n")
display_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

# ------------------- GUI 功能函数 -------------------
def rebuild_listbox():
    listbox.delete(0, tk.END)
    new_dict = {}
    for i, old_idx in enumerate(sorted(ctd.dict.keys())):
        entry = ctd.dict[old_idx]
        new_dict[i] = entry
        disp = entry['data']
        if entry['format'] == 'BITMAP':
            disp = "<图片>"
        listbox.insert(tk.END, f"{i}. {disp}")
    ctd.dict = new_dict
    flabel.config(text="")
    dlabel.config(text="")
    ilabel.config(image="", text="")

def display_set(event=None):
    sel = listbox.curselection()
    if not sel:
        return
    idx = sel[0]
    if idx not in ctd.dict:
        return
    entry = ctd.get(idx)
    fmt = entry['format']
    data = entry['data']

    ilabel.config(image="", text="")

    if fmt == 'BITMAP':
        try:
            img = data.copy()
            img.thumbnail((240, 240))
            photo = ImageTk.PhotoImage(img)
            ilabel.config(image=photo, text="缩略图:", compound="right")
            ilabel.image = photo
        except Exception as e:
            print(f"缩略图生成失败: {e}")
            ilabel.config(text="缩略图: 生成失败")
        bu.pack(pady=5)
    elif fmt == 'HDROP':
        data_str = "\n".join(data) if data else "空"
        bu.pack(pady=5)
    else:
        data_str = str(data)
        bu.pack_forget()
    flabel.config(text=f"格式: {fmt}")
    dlabel.config(text=f"数据: {data_str[0:150]}")

def delete(selection):
    if selection:
        idx = selection[0]
        if idx in ctd.dict:
            del ctd.dict[idx]
            rebuild_listbox()

def start():
    sel = listbox.curselection()
    if not sel:
        return
    idx = sel[0]
    if idx not in ctd.dict:
        return
    entry = ctd.get(idx)
    fmt = entry['format']
    data = entry['data']
    if fmt == "BITMAP":
        data.show()
    elif fmt == "HDROP":
        for i in data:
            os.startfile(i)

def get(selection):
    global lds, last_ignore
    if not selection:
        return
    idx = selection[0]
    if idx not in ctd.dict:
        return
    entry = ctd.get(idx)
    fmt = entry['format']
    try:
        lds = True
        if fmt == "notf":
            from ls import win32clipboard
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
            finally:
                win32clipboard.CloseClipboard()
        else:
            last_ignore = time.time() * 1000
            op.set_clipboard(fmt, entry['data'])
        print(f"已恢复索引 {idx}, data:", entry['data'])
    except Exception as e:
        print(f"复制操作失败: {e}")
        lds = False

def quiti():
    global exiting
    with lock:
        if exiting:
            return
        exiting = True
    root.quit()
    lcb.stop()
    icon.stop()
    iconthread.join(timeout=1)
    thread.join(timeout=1)
    lcb.cleanup()
    if sls_status:
        hs.save_all()

def on_closing():
    if exitt == 0:
        quiti()
    elif exitt == 1:
        root.withdraw()
    elif exitt == 2:
        a = pymsgbox.confirm("退出方式", "退出", buttons=("直接退出", "仅关闭窗口", "不退出"))
        if a == "直接退出":
            quiti()
        elif a == "仅关闭窗口":
            root.withdraw()

def setting():
    global sls_status, sls_time, exitt
    window = tk.Toplevel(root)
    window.title("setting")
    window.geometry("300x300")
    tk.Label(window, text="持久化存储").pack(anchor="w")
    x = tk.IntVar(window, 1 if sls_status else 0)
    tk.Radiobutton(window, text="启用持久化存储", variable=x, value=1).pack()
    tk.Radiobutton(window, text="关闭持久化存储", variable=x, value=0).pack()
    tk.Label(window, text="时间间隔(以秒为单位)").pack()
    b = tk.Entry(window)
    b.insert(0, str(sls_time / 1000))
    b.pack()
    tk.Label(window, text="退出").pack(anchor="w")
    nnnn = tk.IntVar(window, exitt)
    tk.Radiobutton(window, text="直接退出", variable=nnnn, value=0).pack()
    tk.Radiobutton(window, text="仅关闭窗口", variable=nnnn, value=1).pack()
    tk.Radiobutton(window, text="每次都询问", variable=nnnn, value=2).pack()
    f = tk.Frame(window)

    def save():
        global sls_status, sls_time, exitt
        sls_status = x.get() == 1
        exitt = nnnn.get()
        try:
            sls_time = max(5000, int(float(b.get()) * 1000))
        except ValueError:
            print("时间格式错误")
        if sls_status:
            schedule_save()
        hs.save_config()
        window.destroy()

    tk.Button(f, text="保存", command=save).pack(side="left")
    tk.Button(f, text="取消", command=lambda: window.destroy()).pack(side="right")
    f.pack()
    window.grab_set()

# ------------------- 剪贴板事件处理 -------------------
def process_clipboard():
    global lds, last_ignore
    try:
        while True:
            event = clipboard_queue.get_nowait()
            if event == "monitor_stopped":
                print("警告：剪贴板监听线程已退出！")
                continue
            if event == "monitor_started":
                print("剪贴板监听就绪")
                continue
            if isinstance(event, str) and event.startswith("error:"):
                print(f"监听器错误: {event}")
                continue
            if event == "clipboard_changed":
                if lds:
                    lds = False
                    continue
                now = time.time() * 1000
                if now - last_ignore < IGNORE_WINDOW:
                    continue
                try:
                    data = op.get_clipboard()
                except Exception as e:
                    print(f"读取剪贴板时出错: {e}")
                    continue
                if data and data.get("format") != "notf":
                    idx = len(ctd.dict)
                    disp = data['data']
                    if data['format'] == 'BITMAP':
                        disp = "<图片>"
                    ctd.set(idx, data['format'], data['data'])
                    listbox.insert(tk.END, f"{idx}. {disp}")
    except queue.Empty:
        pass
    except Exception as e:
        print(f"process_clipboard 内部异常: {e}")
    finally:
        root.after(100, process_clipboard)

# ------------------- 自动保存定时器 -------------------
save_timer_id = None
def schedule_save():
    global save_timer_id
    if save_timer_id:
        root.after_cancel(save_timer_id)
    save_timer_id = root.after(sls_time, hs.save_all)

# ------------------- 启动 -------------------
rebuild_listbox()
root.protocol("WM_DELETE_WINDOW", on_closing)

lcb = ClipboardMonitor(clipboard_queue)
thread = threading.Thread(target=lcb.start, daemon=True)

try:
    if sys.argv[1] == "bt":
        root.withdraw()
except:
    pass

root.after(100, process_clipboard)

try:
    thread.start()
    root.mainloop()
except KeyboardInterrupt:
    if not exiting:
        quiti()
except Exception as e:
    print("error:", str(e))
    quiti()