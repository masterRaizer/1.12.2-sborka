"""Replace a UTF-8 constant in one class of a jar (e.g. drop a Cleanroom-only @Mod dependency).
Usage: python -I patch_utf8.py in.jar out.jar path/Class.class "old" "new" """
import sys, os, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfparse import ClassFile
src, dst, cls, old, new = sys.argv[1:6]
zin = zipfile.ZipFile(src); hits = 0
tmp = dst + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == cls:
            cf = ClassFile(data)
            for i, e in enumerate(cf.cp.e):
                if e and e[0] == 1 and old in e[1]:
                    cf.cp.e[i] = (1, e[1].replace(old, new)); hits += 1
            data = cf.to_bytes()
        zout.writestr(info, data)
zin.close()
os.replace(tmp, dst)
print('replaced in', hits, 'constants')
