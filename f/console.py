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
        upload_file(a,host,port)


import json

import hashlib


def recv_msg(sock):
    raw_len = sock.recv(4)
    if not raw_len:
        return None
    msg_len = struct.unpack('!I', raw_len)[0]
    data = b''
    while len(data) < msg_len:
        chunk = sock.recv(msg_len - len(data))
        if not chunk:
            raise ConnectionError("连接中断")
        data += chunk
    return data

def send_msg(sock, data):
    sock.sendall(struct.pack('!I', len(data)))
    sock.sendall(data)

def send_json(sock, obj):
    send_msg(sock, json.dumps(obj).encode('utf-8'))

def recv_json(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return json.loads(data.decode('utf-8'))

def compute_hash(data):
    return hashlib.sha256(data).hexdigest()

def upload_file(filepath, host, port, block_size=4096):
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    file_hash = compute_hash(open(filepath, 'rb').read())
    total_blocks = (file_size + block_size - 1) // block_size 
    print(total_blocks)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((host, port))

    try:
        meta = {
            "type": "meta",
            "filename": filename,
            "file_size": file_size,
            "block_size": block_size,
            "total_blocks": total_blocks,
            "file_hash": file_hash
        }
        send_json(sock, meta)

        resp = recv_json(sock)
        assert resp is not None
        missing_blocks = resp.get('blocks', [])
        print(f"需要发送 {len(missing_blocks)} 个块")

        with open(filepath, 'rb') as f:
            for block_id in missing_blocks:
                offset = block_id * block_size
                f.seek(offset)
                data = f.read(block_size)

                header = struct.pack('!II', block_id, len(data))
                
                for i in range(1,10):
                    try:
                        send_msg(sock, header + data)
                    except Exception:
                        print(f"块 {block_id} 发送失败")
                        sleep(i*2)
                        continue
                    
                    ack= recv_json(sock)
                    assert ack is not None
                    if ack.get('type') == 'ack':
                        print(f"块 {block_id} 发送成功,",total_blocks)
                        break
                    else:

                        print(f"块 {block_id} 发送失败")
                        sleep(i*2)
                    

        send_json(sock, {"type": "complete"})
        result = recv_json(sock)
        assert result is not None
        if result.get('type') == 'success':
            print("上传成功且校验通过")
            return True
        else:
            print(f"上传失败: {result.get('reason')}")
            return False
    finally:
        sock.close()





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
    return sock,cipher,aa
sock,cipher,aa = login()
# 4. 后续命令同样加密发送，明文接收回复
while True:
    cmd = input('> ')
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
            chunk = sock.recv(8)
        except (socket.timeout, TimeoutError):
            # 超时，认为数据已发送完毕
            break
        if not chunk:
            break

        buffer += chunk

        # 输出所有可解码的文本（保留可能不完整的字节在 decoder 内部）
        text = decoder.decode(chunk)
        if text:
            print(text, end='')

        # 检查是否收到结束标记
        if b'</s>' in buffer:
            received_end = True
            break

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
        n = int(resp.decode())
        update(aa,n)
    