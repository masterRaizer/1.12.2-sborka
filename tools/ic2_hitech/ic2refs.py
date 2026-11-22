"""Report references from mod jars into ic2/* that the given IC2 jar does not provide."""
import sys, os, glob, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfparse import ClassFile
ic2 = zipfile.ZipFile(sys.argv[1]); idx = {}
for n in ic2.namelist():
    if n.endswith('.class') and n.startswith('ic2/'):
        cf = ClassFile(ic2.read(n)); name = cf.cp.cls(cf.this)
        idx[name] = (cf.cp.cls(cf.super_) if cf.super_ else None, [cf.cp.cls(i) for i in cf.interfaces],
                     {(cf.cp.utf(m[1]), cf.cp.utf(m[2])) for m in cf.methods}, {(cf.cp.utf(f[1]), cf.cp.utf(f[2])) for f in cf.fields})
def has(owner, key, field):
    if key[0] == '<init>':
        return key in idx[owner][2]
    seen = set(); todo = [owner]
    while todo:
        c = todo.pop()
        if c in seen: continue
        seen.add(c)
        if c not in idx: return c.startswith('ic2/') is False  # left IC2: assume vanilla/forge provides it
        sup, ifs, ms, fs = idx[c]
        if key in (fs if field else ms): return True
        if sup: todo.append(sup)
        todo += ifs
    return False
jars = []
for d in sys.argv[2:]: jars += glob.glob(os.path.join(d, '*.jar')) + glob.glob(os.path.join(d, '1.12.2', '*.jar'))
for j in sorted(jars):
    if 'industrialcraft' in j: continue
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    miss = set()
    for n in z.namelist():
        if not n.endswith('.class') or n.startswith('META-INF/'): continue
        try: cf = ClassFile(z.read(n))
        except Exception: continue
        for i, e in enumerate(cf.cp.e):
            if e and e[0] == 7:
                c = cf.cp.cls(i)
                if c.startswith('ic2/') and c not in idx: miss.add(('class', c, '', ''))
            if e and e[0] in (9, 10, 11):
                o, nm, d = cf.cp.ref(i)
                if o.startswith('ic2/') and o in idx and not has(o, (nm, d), e[0] == 9): miss.add(('field' if e[0] == 9 else 'method', o, nm, d))
    if miss:
        print('==', os.path.basename(j), len(miss))
        for m in sorted(miss)[:40]: print('  ', *m)
