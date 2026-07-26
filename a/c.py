import os
import random
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
key = get_random_bytes(16)
a = open("src/as.py", "r", encoding="utf-8")
ax = list()
n = 8
s = True
ama = ""
x = open(f"a.py","w",encoding="utf-8")
with open("src/ima.py", "r", encoding="utf-8") as aa:
    x.write(aa.read())
x.write("\nn = ''")
dda = ""

ligv = a
while s:
    
    dx = a.read(1)
    ama += dx

    if dx == "":
        s = False
        break
    else:

        x.write(f"\nn += {repr(dx)}\n")        
        
        ama += dda
        x.write(dda)
        x.flush()
        n += 1
        if n%10000 == 0:
            print(str(ama))
            ama = ""
            print(str(n))

x.write("\n")
with open("src/down.py", "r", encoding="utf-8") as aa:
    x.write(aa.read())
x.write("\nexec(n)")
x.close()
print(n)
os.system("python ./a.py")
