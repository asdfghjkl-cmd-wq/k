import os
import socket
import subprocess
import time
a = os.path.abspath(os.path.dirname(__file__))
def listen(s:socket.socket):
    sn = b""
    while True:
        snb = s.recv(1024)
        if snb == b"":
            return b""
        if snb.endswith(b"</s>"):
            sn += snb.replace(b"</s>",b"")

            return sn
        sn += snb

def send(s:socket.socket,msg:str):
    s.send(msg.encode())
    s.send(b"</s>")
 
n = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
n.settimeout(5)
aa = input('address:')

if ':' in aa:
    xx = aa.split(':')
    aa = xx[0]
    bb = xx[1]
else:
    bb = input('post:')
if bb.isdecimal():
    bb = int(bb)
else:exit()
n.connect((aa,bb))
a = listen(n)
if a == b'auth':
    b = input("user:")
    c = input('password:')
    send(n,f'{b},{c}')
    if listen(n) == b"y":
        print("auth ok")
    else:
        raise PermissionError('验证失败')
while True:
    a = input('exec:')
    if a == 'quit':
        break
    if a == 'exit':
        send(n,a)
        exit()

    send(n,a)
    a = listen(n).decode()
    print(a)
send(n,'</c>')
