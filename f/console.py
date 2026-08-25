import os
import socket
import struct
from time import sleep
import time
import tqdm
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from file_rw import recv_file, send_file

def recv_exact(sock, n):
    """精确接收 n 字节数据"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_enc_frame(sock, key, plaintext: bytes):
    """发送 AES-256-GCM 加密帧：长度(4字节大端) + nonce(12) + 密文 + tag(16)"""
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    payload = nonce + ct + tag
    sock.sendall(struct.pack('>I', len(payload)) + payload)

def recv_enc_frame(sock, key):
    """接收并解密 AES-256-GCM 加密帧，返回明文字节串；连接关闭返回 None"""
    raw_len = recv_exact(sock, 4)
    if raw_len is None:
        return None
    length = struct.unpack('>I', raw_len)[0]
    payload = recv_exact(sock, length)
    if payload is None:
        return None
    if length < 28:   # nonce(12) + tag(16) 是最小帧
        raise ValueError("非法加密帧长度")
    nonce, body = payload[:12], payload[12:]
    ct, tag = body[:-16], body[-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)

def recv_reply(sock, key):
    """读取回复，直到收到 \4 结束帧或连接关闭"""
    out = b''
    while True:
        frame = recv_enc_frame(sock, key)
        if frame is None:
            break
        if frame == b'\4':
            break
        out += frame
    return out

def update(host, port):
    aa = input('path:')
    if os.path.isfile(aa):
        a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        a.connect((host, port))
        send_file(a, aa)

def download(h, p):
    aa = input('path:')
    a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    a.connect((h, p))
    a.sendall(struct.pack('!I', len(aa)) + aa.encode())
    save_dir = os.path.dirname(aa) if os.path.dirname(aa) else '.'
    recv_file(a, save_dir, display=True)

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
    else:
        exit()
    sock.connect((aa, bb))

    # 1. 接收公钥长度 + 公钥数据
    raw_len = recv_exact(sock, 4)
    pub_len = struct.unpack('>I', raw_len)[0]
    pub_bytes = recv_exact(sock, pub_len)
    public_key = RSA.import_key(pub_bytes)

    # 2. 生成 32 字节随机会话密钥，用 RSA-OAEP 加密后发送（仅此一次非对称运算）
    session_key = os.urandom(32)
    cipher = PKCS1_OAEP.new(public_key)
    enc = cipher.encrypt(session_key)
    sock.sendall(struct.pack('>I', len(enc)) + enc)

    # 3. 认证信息走 AES-256-GCM 加密帧
    n = input('user:')
    p = input('password:')
    if n == "" and p == "":
        p = n = 'admin'
    send_enc_frame(sock, session_key, f'{n},{p}'.encode())

    # 4. 接收认证结果（AES-GCM 帧，直到 \4 结束）
    sock.settimeout(10)
    try:
        response = recv_reply(sock, session_key)
    except Exception:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        login()
    print('认证结果:', response.decode())
    sock.settimeout(None)   # 回复以 \4 帧结束，无需再用超时判断响应结束
    return sock, session_key, aa, bb

sock, session_key, aa, bb = login()
# 后续命令全部走 AES-256-GCM 加密帧
abibi = time.time()
while True:
    cmd = input(f'{aa}:{bb} {int((time.time()-abibi)*1000)}ms> ')
    abibi = time.time()
    if cmd == 'quit':
        cmd = '</c>'
        send_enc_frame(sock, session_key, cmd.encode())
        resp = recv_reply(sock, session_key)
        print(resp.decode())
        exit(0)
    if cmd == "":
        cmd = "k"

    send_enc_frame(sock, session_key, cmd.encode())
    resp = recv_reply(sock, session_key)
    text = resp.replace(b'\0', b'').decode('utf-8', errors='replace')
    if text:
        print(text, end='', flush=True)
        if cmd == 'update' or cmd == 'download':
            try:
                n = int(text.strip())
                if cmd == 'update':
                    update(aa, n)
                else:
                    download(aa, n)
            except ValueError:
                pass
    print()
