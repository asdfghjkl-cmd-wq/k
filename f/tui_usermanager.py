#!/usr/bin/env python3
"""
独立用户管理 TUI - 连接文件服务器的管理 socket 操作账户
依赖: textual, requests
启动: python console.py
"""

import re
import socket
from typing import Optional

import requests
from requests.exceptions import RequestException

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Button, Input, Static, RichLog,
)
from textual.screen import Screen
from textual import work


# ==================== 后端 API 封装 ====================
class ServerAPI:
    """包含登录与管理 socket 二次验证"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.csrf_token: Optional[str] = None
        self.logged_in = False
        self.username: Optional[str] = None
        self.sock: Optional[socket.socket] = None  # 延迟到登录成功后创建

    def _extract_csrf_from_html(self, html: str) -> Optional[str]:
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
        return match.group(1) if match else None

    def get_csrf_from_page(self) -> bool:
        try:
            resp = self.session.get(f"{self.base_url}/login")
            if resp.status_code == 200:
                token = self._extract_csrf_from_html(resp.text)
                if token:
                    self.csrf_token = token
                    return True
            return False
        except RequestException:
            return False

    def login(self, username: str, password: str) -> tuple[bool, str]:
        if not self.csrf_token:
            if not self.get_csrf_from_page():
                return False, "无法获取 CSRF Token，请检查服务器连接"

        data = {
            "username": username,
            "password": password,
            "csrf_token": self.csrf_token
        }
        try:
            resp = self.session.post(
                f"{self.base_url}/login",
                data=data,
                allow_redirects=False
            )
        except RequestException as e:
            return False, str(e)

        if resp.status_code == 302 and resp.headers.get("Location", "").startswith("/"):
            self.logged_in = True
            self.username = username
            try:
                home_resp = self.session.get(f"{self.base_url}/")
                new_token = self._extract_csrf_from_html(home_resp.text)
                if new_token:
                    self.csrf_token = new_token
            except RequestException:
                pass

            # 登录成功后，连接管理 socket 并验证
            result, msg = self._connect_and_verify(username, password)
            if not result:
                self.logged_in = False
                self.sock = None
                return False, msg
            return True, "登录成功"
        elif resp.status_code == 200 and "用户名或密码错误" in resp.text:
            new_token = self._extract_csrf_from_html(resp.text)
            if new_token:
                self.csrf_token = new_token
            return False, "用户名或密码错误"
        else:
            return False, f"未知错误 (HTTP {resp.status_code})"

    def _connect_and_verify(self, username: str, password: str) -> tuple[bool, str]:
        """连接管理 socket 并执行二次验证"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect(("127.0.0.1", 12346))
        except Exception as e:
            return False, f"无法连接管理端口: {e}"

        try:
            # 1. 接收服务器发送的 'auth'
            auth_challenge = self._recv_until_delimiter()
            if auth_challenge != b"auth":
                return False, "服务器未发送 auth 挑战"

            # 2. 发送用户名和密码
            self.sock.sendall(f"{username},{password}".encode() + b"</s>")

            # 3. 接收验证结果
            result = self._recv_until_delimiter()
            if result == b"y":
                return True, "管理通道验证成功"
            else:
                return False, "管理通道验证失败（用户名或密码错误）"
        except Exception as e:
            return False, f"验证过程错误: {e}"

    def _recv_until_delimiter(self) -> bytes:
        """接收数据直到遇到 </s> 或连接关闭"""
        response = b""
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if response.endswith(b"</s>"):
                response = response.rstrip(b"</s>")
                break
        return response

    def _send_socket_cmd(self, cmd: str) -> str:
        if not self.sock:
            return "管理 socket 未连接"
        try:
            self.sock.sendall(cmd.encode() + b"</s>")
            response = self._recv_until_delimiter()
            return response.decode().strip()
        except Exception as e:
            return f"Socket 通信错误: {e}"

    # ---- 用户管理命令 ----
    def add_user(self, username: str, password: str) -> str:
        return self._send_socket_cmd(f"adduser {username} {password}")

    def del_user(self, username: str) -> str:
        return self._send_socket_cmd(f"deluser {username}")

    def add_nigga(self, username: str) -> str:
        return self._send_socket_cmd(f"addnigga {username}")

    def del_nigga(self, username: str) -> str:
        return self._send_socket_cmd(f"delnigga {username}")

    def set_admin(self, username: str) -> str:
        return self._send_socket_cmd(f"setadmin {username}")

    def list_users(self) -> str:
        return self._send_socket_cmd("listuser")


# ==================== 登录界面 ====================
class LoginScreen(Screen):
    CSS = """
    .login_form {
        align: center middle;
        width: 40;
        height: auto;
        margin: 1 2;
    }
    .title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Static("登录到用户管理", classes="title"),
            Input(placeholder="服务器地址 (例: http://localhost:5000)", id="url"),
            Input(placeholder="管理员用户名", id="user"),
            Input(placeholder="密码", password=True, id="pass"),
            Button("登录", id="login_btn", variant="primary"),
            Static("", id="error_msg"),
            classes="login_form",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#url").value = "http://localhost:5000"

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_btn":
            url = self.query_one("#url").value.strip()
            user = self.query_one("#user").value.strip()
            password = self.query_one("#pass").value

            if not url or not user:
                self.query_one("#error_msg").update("请填写所有字段")
                return

            self.app.api = ServerAPI(url)
            ok, msg = self.app.api.login(user, password)
            if ok:
                await self.app.switch_screen(UserManageScreen())
            else:
                self.query_one("#error_msg").update(f"登录失败: {msg}")


# ==================== 用户管理界面 ====================
class UserManageScreen(Screen):
    CSS = """
    #user_mgr_container {
        width: 70%;
        max-width: 80;
        min-height: 24;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        margin: 1 2;
    }
    #user_mgr_title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        text-align: center;
    }
    #user_list_out {
        height: 10;
        border: solid $secondary;
        overflow-y: auto;
        margin-bottom: 1;
    }
    #user_inputs {
        margin-bottom: 1;
    }
    .input-field {
        width: 100%;
        margin-bottom: 1;
    }
    #user_buttons {
        margin-bottom: 1;
        align-horizontal: center;
    }
    .action-btn {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Static("用户管理", id="user_mgr_title"),
            RichLog(id="user_list_out", highlight=True, markup=True),
            Vertical(
                Input(placeholder="用户名", id="uname", classes="input-field"),
                Input(placeholder="密码（添加用户时必填）", id="upass", password=True, classes="input-field"),
                id="user_inputs",
            ),
            Horizontal(
                Button("添加", id="add_user", variant="success", classes="action-btn"),
                Button("删除", id="del_user", variant="error", classes="action-btn"),
                Button("拉黑", id="add_nigga", variant="warning", classes="action-btn"),
                Button("解封", id="del_nigga", classes="action-btn"),
                Button("设为管理", id="set_admin", classes="action-btn"),
                id="user_buttons",
            ),
            Button("关闭", id="close", variant="primary"),
            id="user_mgr_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        out = self.app.api.list_users()
        log = self.query_one("#user_list_out", RichLog)
        log.clear()
        log.write(out)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        api: ServerAPI = self.app.api
        uname = self.query_one("#uname").value.strip()
        if event.button.id == "close":
            # 正常关闭管理 socket
            if api.sock:
                try:
                    api.sock.sendall(b'</c>')
                    api.sock.shutdown(socket.SHUT_RDWR)
                    api.sock.close()
                except:
                    pass
            self.app.exit()
            return

        if event.button.id in ("del_user", "add_nigga", "del_nigga", "set_admin"):
            if not uname:
                self.notify("请输入用户名", severity="error")
                return

        result = ""
        if event.button.id == "add_user":
            upass = self.query_one("#upass").value
            if not uname or not upass:
                self.notify("需要用户名和密码", severity="error")
                return
            result = api.add_user(uname, upass)
        elif event.button.id == "del_user":
            result = api.del_user(uname)
        elif event.button.id == "add_nigga":
            result = api.add_nigga(uname)
        elif event.button.id == "del_nigga":
            result = api.del_nigga(uname)
        elif event.button.id == "set_admin":
            result = api.set_admin(uname)
        else:
            return

        self.notify(result)
        self.refresh_list()


# ==================== 主应用 ====================
class UserManagerApp(App):
    BINDINGS = [
        ("ctrl+q", "quit", "退出"),
    ]

    def __init__(self):
        super().__init__()
        self.api: Optional[ServerAPI] = None

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())


if __name__ == "__main__":
    try:
        app = UserManagerApp()
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("按 Enter 键退出...")