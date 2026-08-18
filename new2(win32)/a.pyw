# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import os, sys, threading, queue, time, traceback
import tkinter as tk
from io import BytesIO
from PIL import ImageTk, Image
import pickle, pymsgbox, base64, pystray
from pystray import MenuItem
import faulthandler
from ls import *  # ClipboardMonitor, OperationClipboard, clipboard_lock

# ---------- 全局日志 ----------
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),"clash.log")
open(LOG_FILE, "w").close()
faulthandler.enable(file=open(LOG_FILE, "a"))

def log(msg):
    pass

def log_exception(exc_type, exc_value, exc_tb):
    log(f"UNCAUGHT EXCEPTION: {''.join(traceback.format_exception(exc_type, exc_value, exc_tb))}")
    sys.__excepthook__(exc_type, exc_value, exc_tb)
sys.excepthook = log_exception

appdata = os.environ["appdata"]
save_dir = f"{appdata}\\clipboard_viewer"
os.makedirs(save_dir, exist_ok=True)

class clipbords_tk_dict:
    def __init__(self):
        self.dict = {}

    def set(self, index, format, data):
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
        self.save_ctd()
        self.save_config()
        if sls_status: schedule_save()

    def save_ctd(self):
        try:
            with open(f"{save_dir}\\clipboard.save", "wb") as f:
                pickle.dump(ctd, f)
        except: log(f"保存失败: {traceback.format_exc()}")

    def save_config(self):
        try:
            with open(f"{save_dir}\\config.save", "wb") as f:
                pickle.dump([sls_status, sls_time, exitt], f)
        except: log(f"配置保存失败: {traceback.format_exc()}")

    def read_ctd(self):
        path = f"{save_dir}\\clipboard.save"
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    s = pickle.load(f)
            except:
                s = clipbords_tk_dict()
        else:
            s = clipbords_tk_dict()
        s.dict = {k: v for k, v in s.dict.items() if v.get("format") != "notf"}
        return s

    def read_config(self):
        path = f"{save_dir}\\config.save"
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return pickle.load(f)
            except:
                pass
        return [False, 0, 2]

hs = h()
sls_status, sls_time, exitt = hs.read_config()
root = tk.Tk()
ctd = hs.read_ctd() if sls_status else clipbords_tk_dict()

lds = False
last_ignore = 0
IGNORE_WINDOW = 300
op = OperationClipboard()
clipboard_queue = queue.Queue()
exiting = False
lock = threading.Lock()

dataicon = "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"
dedata = base64.b64decode(dataicon)
icn = Image.open(BytesIO(dedata))
ico = ImageTk.PhotoImage(icn)

def show_win():
    root.deiconify()
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    root.attributes('-topmost', False)

tray_menu = (
    MenuItem("显示", show_win, default=True),
    MenuItem("设置", lambda: setting()),
    MenuItem("退出", lambda: quiti()),
)
icon = pystray.Icon("clipboard", icn, "Clipboard Viewer", tray_menu)
iconthread = threading.Thread(target=icon.run, daemon=True)
iconthread.start()

root.iconphoto(True, ico)
root.geometry("800x600+20+200")
root.title("Clipboards Viewer")
root.minsize(537,417)
menu_bar = tk.Menu(root)
menu_bar.add_command(label="设置", command=lambda: setting())
menu_bar.add_command(label="保存", command=lambda: hs.save_all())
root.config(menu=menu_bar)

listbox = tk.Listbox(root, bg="#FFFFFF", selectmode=tk.SINGLE)
display_frame = tk.Frame(root)
button_frame = tk.Frame(root)
flabel = tk.Label(display_frame, text="", anchor="w")
dlabel = tk.Label(display_frame, text="", anchor="w", wraplength=600)
ilabel = tk.Label(display_frame, text="", anchor="w")
flabel.pack(fill="x", padx=5, pady=2)
dlabel.pack(fill="x", padx=5, pady=2)
ilabel.pack(fill="x", padx=5, pady=2)
listbox.bind("<<ListboxSelect>>", lambda e: display_set())
tk.Button(button_frame, text="删除", command=lambda: delete(listbox.curselection())).pack(pady=5)
tk.Button(button_frame, text="复制", command=lambda: get(listbox.curselection())).pack(pady=5)
bu = tk.Button(button_frame, text="启动/展示", command=lambda: start())
bu.pack(pady=5); bu.pack_forget()
root.rowconfigure(0, weight=1); root.rowconfigure(1, weight=2)
root.columnconfigure((0,1,2), weight=1)
listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
button_frame.grid(row=0, column=2, sticky="n")
display_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

def rebuild_listbox():
    listbox.delete(0, tk.END)
    new_dict = {}
    for i, k in enumerate(sorted(ctd.dict.keys())):
        entry = ctd.dict[k]
        new_dict[i] = entry
        disp = entry['data']
        if entry['format'] == 'BITMAP':
            disp = "<图片>"
        listbox.insert(tk.END, f"{i}. {disp}")
    ctd.dict = new_dict
    flabel.config(text=""); dlabel.config(text=""); ilabel.config(image="", text="")

def display_set(event=None):
    sel = listbox.curselection()
    if not sel: return
    idx = sel[0]
    if idx not in ctd.dict: return
    entry = ctd.get(idx)
    fmt, data = entry['format'], entry['data']
    ilabel.config(image="", text="")
    if fmt == 'BITMAP':
        try:
            img = data.copy()
            img.thumbnail((240,240))
            photo = ImageTk.PhotoImage(img)
            ilabel.config(image=photo, text="缩略图:", compound="right")
            ilabel.image = photo
        except: ilabel.config(text="缩略图生成失败")
        bu.pack(pady=5)
    elif fmt == 'HDROP':
        bu.pack(pady=5)
    else:
        bu.pack_forget()
    flabel.config(text=f"格式: {fmt}")
    dlabel.config(text=f"数据: {str(data)[:150]}")

def delete(sel):
    if sel:
        idx = sel[0]
        if idx in ctd.dict:
            del ctd.dict[idx]
            rebuild_listbox()

def start():
    sel = listbox.curselection()
    if not sel: return
    idx = sel[0]
    if idx not in ctd.dict: return
    entry = ctd.get(idx)
    if entry['format'] == 'BITMAP':
        entry['data'].show()
    elif entry['format'] == 'HDROP':
        for p in entry['data']:
            os.startfile(p)

def get(sel):
    global lds, last_ignore
    if not sel: return
    idx = sel[0]
    if idx not in ctd.dict: return
    entry = ctd.get(idx)
    fmt = entry['format']
    if fmt == "notf": return
    try:
        lds = True
        last_ignore = time.time() * 1000
        op.set_clipboard(fmt, entry['data'])
        log(f"复制索引 {idx} 成功")
    except Exception as e:
        log(f"复制失败: {e}")
        lds = False

def quiti():
    global exiting
    with lock:
        if exiting: return
        exiting = True
    log("程序退出")
    root.quit()
    lcb.stop()
    icon.stop()
    iconthread.join(timeout=1)
    thread.join(timeout=1)
    if sls_status: hs.save_all()

def on_closing():
    if exitt == 0: quiti()
    elif exitt == 1: root.withdraw()
    elif exitt == 2:
        ans = pymsgbox.confirm("退出方式", "退出", buttons=("直接退出", "仅关闭窗口", "不退出"))
        if ans == "直接退出": quiti()
        elif ans == "仅关闭窗口": root.withdraw()

def setting():
    global sls_status, sls_time, exitt
    win = tk.Toplevel(root)
    win.title("设置"); win.geometry("300x300")
    tk.Label(win, text="持久化").pack(anchor="w")
    xvar = tk.IntVar(win, 1 if sls_status else 0)
    tk.Radiobutton(win, text="启用", variable=xvar, value=1).pack()
    tk.Radiobutton(win, text="关闭", variable=xvar, value=0).pack()
    tk.Label(win, text="间隔(秒)").pack()
    e = tk.Entry(win); e.insert(0, str(sls_time/1000)); e.pack()
    tk.Label(win, text="退出行为").pack(anchor="w")
    nvar = tk.IntVar(win, exitt)
    tk.Radiobutton(win, text="直接退出", variable=nvar, value=0).pack()
    tk.Radiobutton(win, text="仅关闭", variable=nvar, value=1).pack()
    tk.Radiobutton(win, text="询问", variable=nvar, value=2).pack()
    f = tk.Frame(win)
    def save():
        global sls_status, sls_time, exitt
        sls_status = xvar.get() == 1
        exitt = nvar.get()
        try: sls_time = max(5000, int(float(e.get())*1000))
        except: pass
        if sls_status: schedule_save()
        hs.save_config()
        win.destroy()
    tk.Button(f, text="保存", command=save).pack(side="left")
    tk.Button(f, text="取消", command=win.destroy).pack(side="right")
    f.pack()
    win.grab_set()

def process_clipboard():
    global lds, last_ignore
    try:
        while True:
            event = clipboard_queue.get_nowait()
            if event == "monitor_stopped": continue
            if event == "monitor_started": continue
            if isinstance(event, str) and event.startswith("error:"):
                log(f"监听错误: {event}"); continue
            if event == "clipboard_changed":
                if lds:
                    lds = False; continue
                if time.time()*1000 - last_ignore < IGNORE_WINDOW: continue
                try:
                    data = op.get_clipboard()
                except: continue
                if data and data.get("format") != "notf":
                    idx = len(ctd.dict)
                    disp = data['data']
                    if data['format'] == 'BITMAP': disp = "<图片>"
                    ctd.set(idx, data['format'], data['data'])
                    listbox.insert(tk.END, f"{idx}. {disp}")
    except queue.Empty: pass
    except: log(f"process_clipboard异常: {traceback.format_exc()}")
    finally: root.after(100, process_clipboard)

save_timer_id = None
def schedule_save():
    global save_timer_id
    if save_timer_id: root.after_cancel(save_timer_id)
    save_timer_id = root.after(sls_time, hs.save_all)

rebuild_listbox()
root.protocol("WM_DELETE_WINDOW", on_closing)
lcb = ClipboardMonitor(clipboard_queue)
thread = threading.Thread(target=lcb.start, daemon=True)
try:
    if sys.argv[1] == "bt": root.withdraw()
except: pass
root.after(100, process_clipboard)
thread.start()
root.mainloop()