import datetime
import os
from time import sleep
import pyotp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "key")

# 读取或输入密钥
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r", encoding="utf-8") as f:
        secret_key = f.read().strip()
else:
    secret_key = input("请输入 Base32 密钥: ").strip()
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write(secret_key)

# 初始化 TOTP，并进行简单的有效性检查
try:
    totp = pyotp.TOTP(secret_key)
except Exception as e:
    print(f"密钥无效: {e}")
    exit(1)


while True:
    try:
        otp_code = totp.now()
        remaining = totp.interval - datetime.datetime.now().timestamp() % totp.interval
        print(f"OTP: {otp_code}  剩余 {int(remaining)} 秒", end="\r")
        sleep(1)
    except KeyboardInterrupt:
        print("\n已退出。")
        os._exit(0)
        break
