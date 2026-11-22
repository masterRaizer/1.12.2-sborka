import sys, os, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfparse import ClassFile
src = zipfile.ZipFile(sys.argv[1]); names = set(sys.argv[2].split(','))
refs = set()
for n in src.namelist():
    if n not in names: continue
    cf = ClassFile(src.read(n))
    for i, e in enumerate(cf.cp.e):
        if e and e[0] in (9, 10, 11):
            o, nm, d = cf.cp.ref(i)
            if o.startswith('java/') or o.startswith('javax/') or o.startswith('[Ljava'): refs.add((e[0], o, nm, d))
for r in sorted(refs): print(*r)
