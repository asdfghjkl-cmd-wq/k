import os
import shutil
import socket
import struct
from time import sleep
import tqdm
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from file_rw import recv_file,send_file
def update(host,port):
    aa = input('path:')
    if os.path.isfile(aa):
        a = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        a.connect(host,port)
        send_file(a,aa)

def download(h,p):
    aa = input('path:')

    a = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    a.connect((h,p))
    struct.pack('!I', len(aa)) + aa.encode()
    save_dir = os.path.dirname(aa) if os.path.dirname(aa) else '.'
    recv_file(a, save_dir,display=True)






def login():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    aa = input("address:")
    if ':' in aa:
        xx = aa.split(':')
        aa = xx[0].strip()
        bb = xx[1].strip()
    else:
        bb = input('post:')

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
        login()
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
    return sock,cipher,aa,bb
sock,cipher,aa,bb = login()
# 4. 后续命令同样加密发送，明文接收回复
while True:
    cmd = input(f'{aa}:{bb}> ')
    if cmd == 'quit':
        cmd = '</c>'
        enc_cmd = cipher.encrypt(cmd.encode())
        sock.sendall(struct.pack('>I', len(enc_cmd)) + enc_cmd)
        resp = b''
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
    resp = b""
    ch = b''

    import codecs

    decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    buffer = b''          # 累积原始字节，用于查找 </s>
    received_end = False

    while True:
        try:
            chunk = sock.recv(2)
        except (socket.timeout, TimeoutError):
            # 超时，认为数据已发送完毕
            break
        if not chunk:
            break

        buffer += chunk

        # 输出所有可解码的文本（保留可能不完整的字节在 decoder 内部）
        text = decoder.decode(chunk)


        if b'\4' in buffer:
            received_end = True
            break
        if text:
            print(text, end='',flush=True)
            if cmd == 'update' or cmd == 'download':
                n = int(text.removesuffix('\x00'))
                
            

        # 检查是否收到结束标记
        

    # 如果是因为超时退出但已经收到结束标记，同样正常结束
    # 刷新解码器，输出剩余内容
    text = decoder.decode(b'', final=True)
    if text:
        print(text, end='')

    # 可选：根据 received_end 判断是否正常结束
    if not received_end:
        print("\n[警告] 未收到结束标记 </s>，连接可能异常中断")
    print()
    if cmd == 'update':
        
        update(aa,n)
    if cmd == 'download':download(aa,n)
    