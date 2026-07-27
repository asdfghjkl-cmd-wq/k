import ctypes
import io
import threading
import time
import traceback
import win32clipboard, win32con
from win32clipboard import (
    OpenClipboard, CloseClipboard, EmptyClipboard,
    GetClipboardData, SetClipboardData, EnumClipboardFormats, error
)
from PIL import Image, ImageGrab

# ---------- 全局剪贴板锁，保证任何时刻只有一个线程访问剪贴板 ----------
clipboard_lock = threading.Lock()

def log_error(msg):
    with open("crash.log", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

class ClipboardMonitor:
    """无窗口轮询监听，与主线程共享剪贴板锁"""
    def __init__(self, queue):
        self.queue = queue
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()
        self.queue.put("monitor_started")

    def _poll(self):
        try:
            get_seq = ctypes.windll.user32.GetClipboardSequenceNumber
            get_seq.restype = ctypes.c_uint32
            last_seq = 0
            # 首次获取序列号时也要加锁
            with clipboard_lock:
                last_seq = get_seq()
            while self._running:
                time.sleep(0.5)
                with clipboard_lock:
                    seq = get_seq()
                if seq != last_seq:
                    last_seq = seq
                    self.queue.put("clipboard_changed")
        except Exception:
            self.queue.put(f"error: {traceback.format_exc()}")
        finally:
            self.queue.put("monitor_stopped")

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def cleanup(self):
        pass

class OperationClipboard:
    def copy_image_to_clipboard(self, img, is_close=True):
        with clipboard_lock:
            try:
                if not img:
                    return
                if isinstance(img, str):
                    img = Image.open(img)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                output = io.BytesIO()
                img.save(output, format="BMP")
                dib = output.getvalue()[14:]
                if is_close:
                    OpenClipboard()
                try:
                    if is_close:
                        EmptyClipboard()
                    SetClipboardData(win32con.CF_DIB, dib)
                finally:
                    if is_close:
                        CloseClipboard()
            except Exception:
                log_error(f"图片写入失败: {traceback.format_exc()}")

    @staticmethod
    def get_clipboard_bitmap():
        return ImageGrab.grabclipboard()

    @staticmethod
    def set_clipboard_files(file_list, is_close=True):
        """直接传递文件路径元组，由 PyWin32 自动构建 CF_HDROP"""
        with clipboard_lock:
            try:
                if is_close:
                    OpenClipboard()
                    EmptyClipboard()
                # PyWin32 可接受元组直接设置文件列表
                SetClipboardData(win32con.CF_HDROP, file_list)
            finally:
                if is_close:
                    CloseClipboard()

    def get_clipboard(self):
        with clipboard_lock:
            try:
                OpenClipboard()
            except:
                return None
            try:
                fmts = []
                last = 0
                while True:
                    nxt = EnumClipboardFormats(last)
                    if nxt == 0:
                        break
                    fmts.append(nxt)
                    last = nxt
                if not fmts:
                    return {'format': 'notf', 'data': None}
                if win32con.CF_UNICODETEXT in fmts:
                    return {'format': 'Unicode', 'data': GetClipboardData(win32con.CF_UNICODETEXT)}
                if win32con.CF_TEXT in fmts:
                    return {'format': 'ANSI', 'data': GetClipboardData(win32con.CF_TEXT)}
                if win32con.CF_BITMAP in fmts or win32con.CF_DIB in fmts:
                    img = self.get_clipboard_bitmap()
                    if img:
                        return {'format': 'BITMAP', 'data': img}
                    return {'format': 'notf', 'data': None}
                if win32con.CF_HDROP in fmts:
                    return {'format': 'HDROP', 'data': GetClipboardData(win32con.CF_HDROP)}
            except:
                log_error(f"读取剪贴板失败: {traceback.format_exc()}")
                return None
            finally:
                try:
                    CloseClipboard()
                except:
                    pass
        return None

    def set_clipboard(self, writeformat, data):
        with clipboard_lock:
            try:
                OpenClipboard()
            except:
                return
            try:
                EmptyClipboard()
                if writeformat == "Unicode":
                    SetClipboardData(win32con.CF_UNICODETEXT, data)
                elif writeformat == "ANSI":
                    SetClipboardData(win32con.CF_TEXT, data)
                elif writeformat == "BITMAP":
                    self.copy_image_to_clipboard(data, is_close=False)
                elif writeformat == "HDROP":
                    # 直接调用简化版
                    self.set_clipboard_files(data, is_close=False)
            except:
                log_error(f"写入剪贴板失败: {traceback.format_exc()}")
            finally:
                CloseClipboard()