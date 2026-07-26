import re,os,traceback
import tool.u1,tool.u2

UPLOAD_DIR = os.path.abspath("./uploads")
def safe_path(*parts):
    target = os.path.normpath(os.path.join(UPLOAD_DIR, *parts))
    if not os.path.abspath(target).startswith(os.path.abspath(UPLOAD_DIR)):
        raise ValueError("路径越权")
    return target

def call_tool():
    try:
        a = {'tool': 1, 'args': '.'}
        print(a,flush=True)
        if a["tool"] == 1:
            try:
                tool.u2.call(os.path.join(os.path.join(".","uploads"),a["args"]),os.path.join(".","uploads"))
                return "",200
            except FileNotFoundError as a:

                traceback.print_exc()
                return str(a),400
                
        elif a["tool"] == 2:
            try:
                m = re.search(r'-c\s+(\S+)\s+-f\s+(.+)', a["args"])
                print(m.groups())
                if m:
                    tool.u1.call(safe_path(os.path.join(".","uploads",m.group(2))),int(m.group(1)),os.path.join(".","uploads",os.path.basename(m.group(2))))
                    return "",200
                else:
                    return "error",400
            except Exception as a:
                traceback.print_exc()
                return str(a),400
        elif a["tool"] == 3:
            return "使用Assembly以合成文件\n使用cut以分割文件,用法-c 分割块大小 -f 文件目录",201
        else:
            return "Not Found",404
    except Exception as w:
        with open("lo","w",encoding="utf-8") as a:
            traceback.print_exc()

os.chroot