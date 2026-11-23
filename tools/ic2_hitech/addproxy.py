"""Add an empty server proxy class (Name extends Super, public no-arg ctor) to a client-only mod jar.
Usage: python -I addproxy.py jar internal/Name internal/Super"""
import sys, os, struct, zipfile
jar, name, sup = sys.argv[1:4]
cp = []
def utf(s): cp.append(b'\x01' + struct.pack('>H', len(s.encode())) + s.encode()); return len(cp)
def cls(n): i = utf(n); cp.append(b'\x07' + struct.pack('>H', i)); return len(cp)
this_c = cls(name); super_c = cls(sup)
init = utf('<init>'); vdesc = utf('()V'); code_n = utf('Code')
nat = len(cp) + 1; cp.append(b'\x0c' + struct.pack('>HH', init, vdesc))
mref = len(cp) + 1; cp.append(b'\x0a' + struct.pack('>HH', super_c, nat))
code = b'\x2a\xb7' + struct.pack('>H', mref) + b'\xb1'
code_attr = struct.pack('>HHI', 1, 1, len(code)) + code + struct.pack('>HH', 0, 0)
out = b'\xca\xfe\xba\xbe' + struct.pack('>HH', 0, 52) + struct.pack('>H', len(cp) + 1) + b''.join(cp)
out += struct.pack('>HHHH', 0x0021, this_c, super_c, 0) + struct.pack('>H', 0)
out += struct.pack('>H', 1) + struct.pack('>HHH', 0x0001, init, vdesc) + struct.pack('>H', 1) + struct.pack('>HI', code_n, len(code_attr)) + code_attr
out += struct.pack('>H', 0)
with zipfile.ZipFile(jar, 'a') as z:
    if name + '.class' in z.namelist(): sys.exit('already there')
    z.writestr(name + '.class', out)
print('added', name)
