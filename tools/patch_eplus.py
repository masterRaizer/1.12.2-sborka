"""Patch Enchanting Plus so its sliders use Apotheosis' configured max level.

Replaces every `invokevirtual net/minecraft/enchantment/Enchantment.func_77325_b()I`
(Enchantment.getMaxLevel) with `invokestatic shadows/ench/asm/EnchHooks.getMaxLevel(Enchantment)I`.
Both instructions are 3 bytes and have the same stack effect (Enchantment -> int), so no
offsets, branch targets or stack map frames change. New constant-pool entries are appended.

Usage: python -I patch_eplus.py <in.jar> <out.jar>
"""
import struct, sys, zipfile

sys.path.insert(0, __file__.rsplit('\\', 1)[0].rsplit('/', 1)[0])
import jdis

TARGET = ('net/minecraft/enchantment/Enchantment', 'func_77325_b', '()I')
HOOK = ('shadows/ench/asm/EnchHooks', 'getMaxLevel', '(Lnet/minecraft/enchantment/Enchantment;)I')


def read_cp(d):
    """Return (cp list of (tag, raw bytes), end offset)."""
    n = struct.unpack('>H', d[8:10])[0]; p = 10; cp = [None] * n; i = 1
    while i < n:
        t = d[p]
        if t == 1:
            l = struct.unpack('>H', d[p+1:p+3])[0]; size = 3 + l
        elif t in (3, 4, 9, 10, 11, 12, 17, 18): size = 5
        elif t in (5, 6): size = 9
        elif t in (7, 8, 16, 19, 20): size = 3
        elif t == 15: size = 4
        else: raise ValueError(t)
        cp[i] = (t, d[p:p+size]); p += size
        i += 2 if t in (5, 6) else 1
    return cp, p


def utf(cp, i): return cp[i][1][3:].decode('utf8')


def find_methodref(cp, owner, name, desc):
    for i, e in enumerate(cp):
        if e and e[0] == 10:
            ci, nti = struct.unpack('>HH', e[1][1:5])
            if utf(cp, struct.unpack('>H', cp[ci][1][1:3])[0]) != owner: continue
            ni, di = struct.unpack('>HH', cp[nti][1][1:5])
            if utf(cp, ni) == name and utf(cp, di) == desc: return i
    return None


def code_ranges(d, cp_end):
    """Yield (start, length) of each method's Code bytes."""
    p = cp_end + 6
    ic = struct.unpack('>H', d[p:p+2])[0]; p += 2 + 2 * ic
    cp, _ = read_cp(d)

    def skip_attrs(p, want_code=False):
        out = []; c = struct.unpack('>H', d[p:p+2])[0]; p += 2
        for _ in range(c):
            nm, l = struct.unpack('>HI', d[p:p+6])
            if want_code and utf(cp, nm) == 'Code':
                out.append((p + 14, struct.unpack('>I', d[p+10:p+14])[0]))
            p += 6 + l
        return p, out
    fc = struct.unpack('>H', d[p:p+2])[0]; p += 2
    for _ in range(fc): p, _x = skip_attrs(p + 6)
    mc = struct.unpack('>H', d[p:p+2])[0]; p += 2; res = []
    for _ in range(mc):
        p, codes = skip_attrs(p + 6, True); res += codes
    return res


def instr_offsets(d, start, length):
    pc = 0
    while pc < length:
        o = d[start + pc]; name, n = jdis.OPS[o]; a = start + pc + 1
        if name in ('tableswitch', 'lookupswitch'):
            pad = (4 - (pc + 1) % 4) % 4; b = a + pad
            if name == 'tableswitch':
                lo, hi = struct.unpack('>ii', d[b+4:b+12]); n = pad + 12 + 4 * (hi - lo + 1)
            else:
                n = pad + 8 + 8 * struct.unpack('>i', d[b+4:b+8])[0]
        elif name == 'wide':
            n = 5 if d[a] == 0x84 else 3
        yield pc, o
        pc += 1 + n


def patch_class(d):
    cp, cp_end = read_cp(d)
    target = find_methodref(cp, *TARGET)
    if target is None: return d, 0
    n = len(cp)
    u = lambda s: b'\x01' + struct.pack('>H', len(s)) + s.encode()
    new = [u(HOOK[0]), b'\x07' + struct.pack('>H', n), u(HOOK[1]), u(HOOK[2]),
           b'\x0c' + struct.pack('>HH', n + 2, n + 3), b'\x0a' + struct.pack('>HH', n + 1, n + 4)]
    hook = n + 5
    ranges = code_ranges(d, cp_end)
    out = bytearray(d[:8] + struct.pack('>H', n + len(new)) + d[10:cp_end] + b''.join(new) + d[cp_end:])
    shift = sum(len(x) for x in new); count = 0
    for start, length in ranges:
        for pc, o in instr_offsets(d, start, length):
            at = start + pc
            if o == 0xb6 and struct.unpack('>H', d[at+1:at+3])[0] == target:
                out[at + shift] = 0xb8
                out[at + shift + 1:at + shift + 3] = struct.pack('>H', hook)
                count += 1
    return bytes(out), count


def main(src, dst):
    total = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            name = info.filename
            if name.upper().startswith('META-INF/') and name.upper().endswith(('.SF', '.RSA', '.DSA', '.EC')):
                print('drop signature', name); continue
            data = zin.read(name)
            if name == 'META-INF/MANIFEST.MF':
                # keep only the main section; per-entry digests belong to the removed signature
                data = data.replace(b'\r\n', b'\n').split(b'\n\n')[0].rstrip(b'\n') + b'\n\n'
            if name.endswith('.class'):
                data, c = patch_class(data)
                if c: print(f'patched {name}: {c}')
                total += c
            zout.writestr(info, data)
    print('total call sites patched:', total)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
