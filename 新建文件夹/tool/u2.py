import os,shutil
def aaa():
    e= input("path:")
    if os.path.exists(e) and os.path.isdir(e) and os.path.exists(e+"\\file"):
        return e
    else:
        return aaa()

def call(dir,tdir):
    file = open(os.path.join(dir,"file"),"r",encoding="utf-8")
    n = os.path.basename(file.readline().replace("\n",""))
    print(n,flush=True)
    x = int(file.readline().replace("\n",""))
    file.close()
    bn = open(os.path.join(tdir,n),"wb")
    for nb in range(1,x+1):
        an = open(dir+"/"+f"{nb:04d}"+".data","rb")
        bn.write(an.read())
        an.close()
if __name__ == "__main__":
    e = aaa()
    
    call(e,"./")