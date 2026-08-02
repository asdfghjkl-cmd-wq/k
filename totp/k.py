import datetime
import os
from time import sleep

import pyotp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(f"{BASE_DIR}/key"):
    i = open(f"{BASE_DIR}/key","r",encoding="utf-8").read()

else:
    i = input("base32:")
    open(f"{BASE_DIR}/key","w",encoding='utf-8').write(i)
a = pyotp.TOTP(i)


while True:
    n = a.now()
    time_remaining = a.interval - datetime.datetime.now().timestamp() % a.interval
    print("otp:",n,"  remaining ",int(time_remaining),"secoonds")
    sleep(1)