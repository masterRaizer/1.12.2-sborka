"""Like apirefs.py but only members actually invoked/accessed by code (not leftover constant-pool entries)."""
import sys, os, zipfile, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfparse import ClassFile
from downgrade import instructions
z = zipfile.ZipFile(sys.argv[1]); refs = set()
for n in z.namelist():
    if not n.endswith('.class') or n.startswith('META-INF'): continue
    cf = ClassFile(z.read(n))
    for m in cf.methods:
        for a in m[3]:
            if cf.cp.utf(a[0]) != 'Code': continue
            d = a[1]; clen = struct.unpack_from('>I', d, 4)[0]; code = bytes(d[8:8 + clen])
            for pos, op, ln in instructions(code):
                if op in (0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9):
                    idx = struct.unpack_from('>H', code, pos + 1)[0]; e = cf.cp.e[idx]
                    o, nm, ds = cf.cp.ref(idx)
                    if o.startswith('java/') or o.startswith('javax/'): refs.add((e[0], o, nm, ds))
for r in sorted(refs): print(*r)
