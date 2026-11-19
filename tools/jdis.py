"""Minimal Java class disassembler (javap -c like). Usage: python -I jdis.py file.class [methodFilter]"""
import struct, sys

OPS = {}
def op(code, name, n=0): OPS[code] = (name, n)
names0 = ("nop aconst_null iconst_m1 iconst_0 iconst_1 iconst_2 iconst_3 iconst_4 iconst_5 lconst_0 lconst_1 "
          "fconst_0 fconst_1 fconst_2 dconst_0 dconst_1").split()
for i, n in enumerate(names0): op(i, n)
op(0x10, 'bipush', 1); op(0x11, 'sipush', 2); op(0x12, 'ldc', 1); op(0x13, 'ldc_w', 2); op(0x14, 'ldc2_w', 2)
for i, n in enumerate("iload lload fload dload aload".split()): op(0x15 + i, n, 1)
for i, n in enumerate(f"{t}load_{k}" for t in "ilfda" for k in range(4)): op(0x1a + i, n)
for i, n in enumerate("iaload laload faload daload aaload baload caload saload".split()): op(0x2e + i, n)
for i, n in enumerate("istore lstore fstore dstore astore".split()): op(0x36 + i, n, 1)
for i, n in enumerate(f"{t}store_{k}" for t in "ilfda" for k in range(4)): op(0x3b + i, n)
for i, n in enumerate("iastore lastore fastore dastore aastore bastore castore sastore pop pop2 dup dup_x1 dup_x2 dup2 dup2_x1 dup2_x2 swap".split()): op(0x4f + i, n)
ar = "iadd ladd fadd dadd isub lsub fsub dsub imul lmul fmul dmul idiv ldiv fdiv ddiv irem lrem frem drem ineg lneg fneg dneg ishl lshl ishr lshr iushr lushr iand land ior lor ixor lxor".split()
for i, n in enumerate(ar): op(0x60 + i, n)
op(0x84, 'iinc', 2)
cv = "i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s lcmp fcmpl fcmpg dcmpl dcmpg".split()
for i, n in enumerate(cv): op(0x85 + i, n)
br = "ifeq ifne iflt ifge ifgt ifle if_icmpeq if_icmpne if_icmplt if_icmpge if_icmpgt if_icmple if_acmpeq if_acmpne goto jsr".split()
for i, n in enumerate(br): op(0x99 + i, n, 2)
op(0xa9, 'ret', 1); op(0xaa, 'tableswitch', -1); op(0xab, 'lookupswitch', -1)
for i, n in enumerate("ireturn lreturn freturn dreturn areturn return".split()): op(0xac + i, n)
for i, n in enumerate("getstatic putstatic getfield putfield invokevirtual invokespecial invokestatic".split()): op(0xb2 + i, n, 2)
op(0xb9, 'invokeinterface', 4); op(0xba, 'invokedynamic', 4); op(0xbb, 'new', 2); op(0xbc, 'newarray', 1); op(0xbd, 'anewarray', 2)
op(0xbe, 'arraylength'); op(0xbf, 'athrow'); op(0xc0, 'checkcast', 2); op(0xc1, 'instanceof', 2); op(0xc2, 'monitorenter'); op(0xc3, 'monitorexit')
op(0xc4, 'wide', -2); op(0xc5, 'multianewarray', 3); op(0xc6, 'ifnull', 2); op(0xc7, 'ifnonnull', 2); op(0xc8, 'goto_w', 4); op(0xc9, 'jsr_w', 4)


def parse(path):
    d = open(path, 'rb').read(); p = 8
    n = struct.unpack('>H', d[p:p+2])[0]; p += 2
    cp = [None] * n; i = 1
    while i < n:
        t = d[p]; p += 1
        if t == 1:
            l = struct.unpack('>H', d[p:p+2])[0]; cp[i] = ('utf', d[p+2:p+2+l].decode('utf8', 'replace')); p += 2 + l
        elif t in (3, 4):
            v = struct.unpack('>i' if t == 3 else '>f', d[p:p+4])[0]; cp[i] = ('num', v); p += 4
        elif t in (5, 6):
            v = struct.unpack('>q' if t == 5 else '>d', d[p:p+8])[0]; cp[i] = ('num', v); p += 8; i += 1
        elif t in (7, 8, 16, 19, 20):
            cp[i] = ({7: 'class', 8: 'str', 16: 'mtype', 19: 'module', 20: 'pkg'}[t], struct.unpack('>H', d[p:p+2])[0]); p += 2
        elif t in (9, 10, 11, 12, 17, 18):
            cp[i] = ({9: 'ref', 10: 'ref', 11: 'ref', 12: 'nat', 17: 'dyn', 18: 'dyn'}[t],) + struct.unpack('>HH', d[p:p+4]); p += 4
        elif t == 15:
            cp[i] = ('mh', d[p], struct.unpack('>H', d[p+1:p+3])[0]); p += 3
        else:
            raise ValueError(f'bad tag {t}')
        i += 1

    def s(k):
        e = cp[k]
        if e is None: return '?'
        if e[0] == 'utf': return e[1]
        if e[0] == 'num': return repr(e[1])
        if e[0] in ('class', 'mtype'): return s(e[1])
        if e[0] == 'str': return '"' + s(e[1]) + '"'
        if e[0] == 'ref': return s(e[1]) + '.' + s(e[2])
        if e[0] == 'nat': return s(e[1]) + ':' + s(e[2])
        if e[0] == 'dyn': return 'dyn#' + str(e[1]) + ':' + s(e[2])
        if e[0] == 'mh': return 'mh:' + s(e[2])
        return str(e)

    p += 6
    ic = struct.unpack('>H', d[p:p+2])[0]; p += 2 + 2 * ic

    def attrs(p):
        c = struct.unpack('>H', d[p:p+2])[0]; p += 2; out = []
        for _ in range(c):
            nm, l = struct.unpack('>HI', d[p:p+6]); out.append((s(nm), p + 6, l)); p += 6 + l
        return p, out

    fc = struct.unpack('>H', d[p:p+2])[0]; p += 2; fields = []
    for _ in range(fc):
        acc, nm, ds = struct.unpack('>HHH', d[p:p+6]); p, _a = attrs(p + 6); fields.append(s(nm) + ' ' + s(ds))
    mc = struct.unpack('>H', d[p:p+2])[0]; p += 2; methods = []
    for _ in range(mc):
        acc, nm, ds = struct.unpack('>HHH', d[p:p+6]); p, a = attrs(p + 6)
        code = None
        for an, ap, al in a:
            if an == 'Code':
                cl = struct.unpack('>I', d[ap+4:ap+8])[0]; code = (ap + 8, cl)
        methods.append((s(nm), s(ds), code))
    return d, s, fields, methods


def dis(d, s, start, length):
    pc = 0; out = []
    while pc < length:
        o = d[start + pc]; name, n = OPS.get(o, (f'op{o:#x}', 0)); a = start + pc + 1; arg = ''
        if name == 'tableswitch':
            pad = (4 - (pc + 1) % 4) % 4; b = a + pad
            lo, hi = struct.unpack('>ii', d[b+4:b+12]); n = pad + 12 + 4 * (hi - lo + 1); arg = f'{lo}..{hi}'
        elif name == 'lookupswitch':
            pad = (4 - (pc + 1) % 4) % 4; b = a + pad
            np_ = struct.unpack('>i', d[b+4:b+8])[0]; n = pad + 8 + 8 * np_; arg = f'{np_} pairs'
        elif name == 'wide':
            n = 5 if d[a] == 0x84 else 3
        elif name == 'bipush': arg = str(struct.unpack('>b', d[a:a+1])[0])
        elif name == 'sipush': arg = str(struct.unpack('>h', d[a:a+2])[0])
        elif name == 'ldc': arg = s(d[a])
        elif name in ('ldc_w', 'ldc2_w', 'new', 'anewarray', 'checkcast', 'instanceof') or name.startswith(('get', 'put', 'invoke')):
            arg = s(struct.unpack('>H', d[a:a+2])[0])
        elif name.startswith('if') or name in ('goto', 'jsr'):
            arg = '-> ' + str(pc + struct.unpack('>h', d[a:a+2])[0])
        elif name == 'iinc': arg = f'{d[a]} {struct.unpack(">b", d[a+1:a+2])[0]}'
        elif n == 1: arg = str(d[a])
        out.append(f'  {pc:4d}: {name} {arg}'.rstrip())
        pc += 1 + n
    return out


if __name__ == '__main__':
    d, s, fields, methods = parse(sys.argv[1])
    flt = sys.argv[2] if len(sys.argv) > 2 else None
    if not flt:
        print('FIELDS:', *fields, sep='\n  ')
        print('METHODS:', *[m[0] + m[1] for m in methods], sep='\n  ')
    for nm, ds, code in methods:
        if flt and flt not in nm: continue
        if not flt: continue
        print(f'== {nm}{ds}')
        if code: print('\n'.join(dis(d, s, *code)))
