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
a = n.connect_ex(('127.0.0.1',12346))
if a != 0:
    subprocess.run(['start','python.exe',os.path.join(a,'app.py')],shell=True,start_new_session=True)
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
