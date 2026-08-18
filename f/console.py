import os
import socket
import struct
from time import sleep
import tqdm
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
def update(host,port):
    a = input('path:')
    if os.path.isfile(a):
        send_file(a,host,port)

def send_file(filepath, host, port):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found")
        return
    
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        
        # 1. 发送文件名长度和文件名
        filename_bytes = filename.encode('utf-8')
        filename_len = len(filename_bytes)
        client_socket.sendall(struct.pack('!I', filename_len))
        client_socket.sendall(filename_bytes)
        
        # 2. 发送文件大小
        client_socket.sendall(struct.pack('!Q', filesize))
        
        # 3. 发送文件内容
        sent = 0
        with tqdm.tqdm(total=filesize) as dd:
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(8192)
                    dd.update(8192)
                    if not data:
                        break
                    client_socket.sendall(data)
                    sent += len(data)
        
        print(f"Sent {sent} bytes")



def login():
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

    sock.settimeout(10)
    try:sock.recv(10)
    except Exception:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        login(aa,bb,n,p=p)
    # 3. 接收服务器的明文回复（以换行结束）
    try:
        response = b''
        while True:
            ch = sock.recv(1)
            if ch == b'\0' or not ch:
                break
            response += ch
    except:
        response = b''
        while True:
            ch = sock.recv(1)
            if ch == b'\0' or not ch:
                break
            response += ch
    print('认证结果:', response.decode())
    return sock,cipher,aa
sock,cipher,aa = login()
# 4. 后续命令同样加密发送，明文接收回复
while True:
    cmd = input('> ')
    if cmd == 'quit':
        cmd = '</c>'
        enc_cmd = cipher.encrypt(cmd.encode())
        sock.sendall(struct.pack('>I', len(enc_cmd)) + enc_cmd)
        while True:
            ch = sock.recv(1)
            if ch == b'\0' or not ch:
                break
            resp += ch
        print(resp.decode())
        exit(0)
    if cmd == "":
        cmd = "k"

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
    