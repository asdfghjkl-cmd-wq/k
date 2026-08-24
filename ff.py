from random import randint
import socket
import threading
from time import sleep

n = input('from:')

if ':' in n:
    xx = n.split(':')
    n = xx[0]
    bb = xx[1]
else:
    bb = input('port:')


t = input('to:')

if ':' in t:
    xx = t.split(':')
    t = xx[0]
    p = xx[1]
else:
    p = input('port:')


def ftt(f:socket.socket,t:socket.socket):
    while True:
        
        n=f.recv(1024)
        t.sendall(n)
        print('send')



f = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
f.bind((n,int(bb)))
f.listen(1)
print('wait')
df,mm = f.accept()
print('ok')
tx = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tx.connect((t,int(p)))
n = threading.Thread(target=ftt,args=(df,tx),daemon=True)
n.start()
threading.Thread(target=ftt,args=(tx,df),daemon=True).start()
n.join()