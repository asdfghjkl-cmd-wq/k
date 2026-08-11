import os
import socket
import struct
import tqdm
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def update(ip,port):
    ac = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ac.connect((ip,port))
    fil = input("path:")
    if os.path.isfile(fil):
        name = os.path.basename(fil)
        size = os.path.getsize(fil)

        ac.send(name.encode()+b';'+str(size).encode())
       
        ac.recv(10)          # 接收 "ok"
    # 发送文件时，可以不发送结尾 \0，而是发送完成后 shutdown 写端
        with tqdm.tqdm(total=size) as dd:
            with open(fil, 'rb') as d:
                while True:
                    data = d.read(2048)
                    if not data:
                        break
                    ac.send(data)
                    dd.update(2048)
        ac.shutdown(socket.SHUT_WR)   # 告诉对端写完了
        ac.recv(10)   # 等待最终确认
        ac.close()



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
aa = input("address:")
if ':' in aa:
    xx = aa.split(':')
    aa = xx[0]
    bb = xx[1]
else:
    bb = input('post:')
if aa=='':
    aa="127.0.0.1"
    bb = "7060"
if bb.isdecimal():
    bb = int(bb)
else:exit()
sock.connect((aa,bb))

# 1. 接收公钥长度 + 公钥数据
raw_len = sock.recv(4)
pub_len = struct.unpack('>I', raw_len)[0]
pub_bytes = b''
while len(pub_bytes) < pub_len:
    pub_bytes += sock.recv(pub_len - len(pub_bytes))
public_key = RSA.import_key(pub_bytes)

# 2. 加密并发送认证信息
n = input('user:')
p = input('password:')
if n == "" and p == "":
    p = n = 'admin'
cipher = PKCS1_OAEP.new(public_key)
auth_data = f'{n},{p}'.encode()   # 注意长度不能超过86字节
enc = cipher.encrypt(auth_data)
sock.sendall(struct.pack('>I', len(enc)) + enc)

# 3. 接收服务器的明文回复（以换行结束）
response = b''
while True:
    ch = sock.recv(1)
    if ch == b'\0' or not ch:
        break
    response += ch
print('认证结果:', response.decode())

# 4. 后续命令同样加密发送，明文接收回复
while True:
    cmd = input('> ')
    if cmd == 'quit':
        exit(0)
    

    enc_cmd = cipher.encrypt(cmd.encode())
    sock.sendall(struct.pack('>I', len(enc_cmd)) + enc_cmd)
    resp = b''
    while True:
        ch = sock.recv(1)
        if ch == b'\0' or not ch:
            break
        resp += ch
    print(resp.decode())
    if cmd == 'update':
        n = int(resp.decode())
        update(aa,n)
    