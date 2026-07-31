import os
import shutil

def get_file_path():
    while True:
        path = input("请输入文件路径: ").strip()
        if os.path.isfile(path):
            return path
        print("文件不存在或不是有效文件，请重新输入。")

def get_chunk_size():
    while True:
        choice = input(
            "选择分块大小:\n"
            "1. 1KB\n"
            "2. 90KB\n"
            "3. 1MB\n"
            "4. 90MB\n"
            "5. 900MB\n"
            "直接回车默认90MB\n"
            "输入数字: "
        ).strip()
        if choice == "1":
            return 1024
        elif choice == "2":
            return 1024 * 90
        elif choice == "3":
            return 1024 * 1024
        elif choice == "4":
            return 1024 * 1024 * 90
        elif choice == "5":
            return 1024 * 1024 * 900
        elif choice == "":
            return 1024 * 1024 * 90
        elif choice == "nf":
            return int(eval(input("eval:")))
        else:
            print("无效选择，请重新输入。")


# 主逻辑
def call(source_path,chunk_size,output_dir):


    if os.path.exists(output_dir):
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        else:
            os.remove(output_dir)  # 如果是同名文件则删除
    os.makedirs(output_dir)

    file_count = 0
    with open(source_path, "rb") as src:
        while True:
            data = src.read(chunk_size)
            if not data:
                break
            file_count += 1
            print(file_count)
            # 4位编号便于排序
            out_name = os.path.join(output_dir, f"{file_count:04d}.data")
            with  open(out_name, "wb") as chunk:
                chunk.write(data)

# 写入元信息
    meta_path = os.path.join(output_dir, "file")
    with open(meta_path, "w", encoding="utf-8") as meta:
        meta.write(f"{os.path.basename(source_path)}\n")
        meta.write(f"{file_count}\n")
        meta.write(f"{chunk_size}\n")

if __name__ == "__main__":
    source_path = get_file_path()
    chunk_size = get_chunk_size()

    output_dir = "./a"
    call(source_path,chunk_size,output_dir)