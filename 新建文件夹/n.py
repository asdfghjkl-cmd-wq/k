a= open("app.py","r",encoding="utf-8").read()
b =open("a.html","r",encoding="utf-8").read()
c = open("tool/u1.py","r",encoding="utf-8").read()
d = open("tool/u2.py","r",encoding="utf-8").read()
n = open("n.txt",'w',encoding="utf-8")

print(f"[a.py]\n{a}\n\n\n[a.html]\n{b}\n\n\n[u1.py]\n{c}\n\n[u2.py]\n{d}\n\n请修复zip e",file=n)