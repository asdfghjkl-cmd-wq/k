import ctypes
import ctypes.wintypes as wintypes
import io
import win32clipboard, win32gui, win32con
from win32clipboard import (GetClipboardData, OpenClipboard, CloseClipboard,
                            EmptyClipboard, SetClipboardData, EnumClipboardFormats, error)
from PIL import Image, ImageGrab


WM_CLIPBOARDUPDATE = 0x031D

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd",    wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam",  wintypes.WPARAM),
        ("lParam",  wintypes.LPARAM),
        ("time",    wintypes.DWORD),
        ("pt_x",    wintypes.LONG),
        ("pt_y",    wintypes.LONG),
    ]

class ClipboardMonitor:
    def __init__(self, queue):
        self.queue = queue
        self.hwnd = None
        self._running = True
        self.hinst = ctypes.windll.kernel32.GetModuleHandleW(None)
        self.class_atom = None

    def _window_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_CLIPBOARDUPDATE:
            try:
                self.queue.put("clipboard_changed")
            except Exception as e:
                print(f"队列写入失败: {e}")
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            self._running = False
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def start(self):
        try:
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._window_proc
            wc.hInstance = self.hinst
            wc.lpszClassName = "ClipboardMonitorClass"
            self.class_atom = win32gui.RegisterClass(wc)

            style = win32con.WS_OVERLAPPED & ~win32con.WS_VISIBLE
            self.hwnd = win32gui.CreateWindow(
                wc.lpszClassName, "Clipboard Monitor", style,
                0, 0, 0, 0, None, None, self.hinst, None
            )
            if not self.hwnd:
                self.queue.put("error: 窗口创建失败")
                return
            if not ctypes.windll.user32.AddClipboardFormatListener(self.hwnd):
                self.queue.put(f"error: AddClipboardFormatListener 失败, 错误码 {ctypes.GetLastError()}")
                return

            self.queue.put("monitor_started")
            print("剪贴板监听已启动，窗口句柄:", self.hwnd)

            msg = MSG()
            lpmsg = ctypes.byref(msg)
            while self._running:
                ret = ctypes.windll.user32.GetMessageW(lpmsg, None, 0, 0)
                if ret <= 0:
                    break
                ctypes.windll.user32.TranslateMessage(lpmsg)
                ctypes.windll.user32.DispatchMessageW(lpmsg)
        except Exception as e:
            self.queue.put(f"error: 监听线程异常退出: {e}")
            print(f"监听线程异常: {e}")
        finally:
            self._running = False
            self.queue.put("monitor_stopped")
            print("监听线程退出")

    def cleanup(self):
        """等待线程结束后调用，注销窗口类"""
        if self.class_atom:
            try:
                win32gui.UnregisterClass(self.class_atom, self.hinst)
            except Exception as e:
                print(f"清理窗口类失败: {e}")
            self.class_atom = None


    def stop(self):
        if self.hwnd:
            ctypes.windll.user32.RemoveClipboardFormatListener(self.hwnd)
            win32gui.PostMessage(self.hwnd, win32con.WM_DESTROY, 0, 0)
        
        self.hwnd = None


class DROPFILES(ctypes.Structure):                       # ← 强制对齐，修复文件粘贴失败
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt",     wintypes.POINT),
        ("fNC",    wintypes.BOOL),
        ("fWide",  wintypes.BOOL),
    ]

class OperationClipboard:
    def copy_image_to_clipboard(self, img, is_close=True):
        if not img:
            return
        if isinstance(img, str):
            img = Image.open(img)
        if img.mode != "RGB":
            img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format="BMP")
        dib_data = output.getvalue()[14:]

        if is_close:
            OpenClipboard()
        try:
            if is_close:
                EmptyClipboard()
            SetClipboardData(win32con.CF_DIB, dib_data)
        except error as e:
            print(f"图片写入剪贴板失败: {e}")
        finally:
            if is_close:
                CloseClipboard()

    @staticmethod
    def get_clipboard_bitmap():
        return ImageGrab.grabclipboard()

    @staticmethod
    def set_clipboard_files(file_list, is_close=True):
        if is_close:
            OpenClipboard()
            EmptyClipboard()

        df = DROPFILES()
        df.pFiles = ctypes.sizeof(DROPFILES)
        df.pt.x = df.pt.y = 0
        df.fNC = 0
        df.fWide = 1

        data = b""
        for path in file_list:
            data += path.encode("utf-16le") + b"\x00\x00"
        data += b"\x00\x00"

        buffer = bytes(df) + data
        SetClipboardData(win32con.CF_HDROP, buffer)

        if is_close:
            CloseClipboard()

    def get_clipboard(self):
        try:
            OpenClipboard()
        except error:
            return None
        try:
            formats = []
            last = 0
            while True:
                nxt = EnumClipboardFormats(last)
                if nxt == 0:
                    break
                formats.append(nxt)
                last = nxt

            if not formats:
                return {'format': "notf", 'data': None}
            if win32con.CF_UNICODETEXT in formats:
                return {'format': "Unicode", 'data': GetClipboardData(win32con.CF_UNICODETEXT)}
            if win32con.CF_TEXT in formats:
                return {'format': "ANSI", 'data': GetClipboardData(win32con.CF_TEXT)}
            if win32con.CF_BITMAP in formats or win32con.CF_DIB in formats:
                img = self.get_clipboard_bitmap()
                if img is not None:
                    return {'format': 'BITMAP', 'data': img}
                else:
                    return {'format': "notf", 'data': None}
            if win32con.CF_HDROP in formats:
                # PyWin32 自动将 CF_HDROP 解析为文件路径元组
                return {'format': "HDROP", 'data': GetClipboardData(win32con.CF_HDROP)}
        except error as e:
            print(f"读取剪贴板失败: {e}")
            return None
        finally:
            try:
                CloseClipboard()
            except error:
                pass
        return None

    def set_clipboard(self, writeformat, data):
        try:
            OpenClipboard()
        except error:
            return
        EmptyClipboard()
        try:
            if writeformat == "Unicode":
                SetClipboardData(win32con.CF_UNICODETEXT, data)
            elif writeformat == "ANSI":
                SetClipboardData(win32con.CF_TEXT, data)
            elif writeformat == "BITMAP":
                self.copy_image_to_clipboard(data, is_close=False)
            elif writeformat == "HDROP":
                self.set_clipboard_files(data, is_close=False)
        finally:
            CloseClipboard()