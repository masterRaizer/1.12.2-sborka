"""Patch Tinkers' Addons toolkits (ModExtraModifier) to be stackable.

* <init>:  SingleAspect(this)  ->  LevelAspect(this, 1000)   (toolkit can be applied repeatedly)
* applyEffect: modifiers += max(1, tier-1) * max(1, level)
      tier = last char of identifier "bonus-modifier_N" (1 iron, 2 gold, 3 diamond, 4 ender)
      -> iron +1, gold +1, diamond +2, ender +3 per application
Both methods are branch-free, so no StackMapTable is needed; LineNumber/LocalVariable tables of the
two rewritten methods are dropped (optional debug info).

Usage: python -I patch_tadd.py <in.jar> <out.jar>
"""
import struct, sys, zipfile

CLS = 'com/oitsjustjose/tinkers_addons/modifiers/ModExtraModifier.class'
MOD = 'com/oitsjustjose/tinkers_addons/modifiers/ModExtraModifier'
SINGLE = 'slimeknights/tconstruct/library/modifiers/ModifierAspect$SingleAspect'
LEVEL = 'slimeknights/tconstruct/library/modifiers/ModifierAspect$LevelAspect'
IMOD = 'Lslimeknights/tconstruct/library/modifiers/IModifier;'
NBT = 'Lnet/minecraft/nbt/NBTTagCompound;'
TOOLNBT = 'slimeknights/tconstruct/library/tools/ToolNBT'
TAGUTIL = 'slimeknights/tconstruct/library/utils/TagUtil'
MNBT = 'slimeknights/tconstruct/library/modifiers/ModifierNBT'


class ClassFile:
    def __init__(self, d):
        self.d = d; p = 8
        n = struct.unpack('>H', d[p:p+2])[0]; p += 2
        self.cp = [None] * n; i = 1
        while i < n:
            t = d[p]
            if t == 1: size = 3 + struct.unpack('>H', d[p+1:p+3])[0]
            elif t in (3, 4, 9, 10, 11, 12, 17, 18): size = 5
            elif t in (5, 6): size = 9
            elif t in (7, 8, 16, 19, 20): size = 3
            elif t == 15: size = 4
            else: raise ValueError(t)
            self.cp[i] = d[p:p+size]; p += size; i += 2 if t in (5, 6) else 1
        self.access, self.this, self.super = struct.unpack('>HHH', d[p:p+6]); p += 6
        ic = struct.unpack('>H', d[p:p+2])[0]; self.ifaces = d[p:p+2+2*ic]; p += 2 + 2 * ic
        p, self.fields = self._members(p)
        p, self.methods = self._members(p)
        self.attrs = d[p:]

    def _members(self, p):
        d = self.d; c = struct.unpack('>H', d[p:p+2])[0]; p += 2; out = []
        for _ in range(c):
            acc, nm, ds, ac = struct.unpack('>HHHH', d[p:p+8]); p += 8; attrs = []
            for _ in range(ac):
                an, al = struct.unpack('>HI', d[p:p+6]); attrs.append([an, bytearray(d[p+6:p+6+al])]); p += 6 + al
            out.append([acc, nm, ds, attrs])
        return p, out

    def utf(self, i): return self.cp[i][3:].decode('utf8')

    def _find(self, raw):
        for i, e in enumerate(self.cp):
            if e == raw: return i
        self.cp.append(raw); return len(self.cp) - 1

    def U(self, s): b = s.encode(); return self._find(b'\x01' + struct.pack('>H', len(b)) + b)
    def C(self, s): return self._find(b'\x07' + struct.pack('>H', self.U(s)))
    def NT(self, n, t): return self._find(b'\x0c' + struct.pack('>HH', self.U(n), self.U(t)))
    def M(self, c, n, t): return self._find(b'\x0a' + struct.pack('>HH', self.C(c), self.NT(n, t)))
    def F(self, c, n, t): return self._find(b'\x09' + struct.pack('>HH', self.C(c), self.NT(n, t)))

    def method(self, name, desc):
        for m in self.methods:
            if self.utf(m[1]) == name and self.utf(m[2]) == desc: return m
        raise KeyError(name)

    def set_code(self, m, max_stack, max_locals, code):
        for a in m[3]:
            if self.utf(a[0]) == 'Code':
                old = a[1]; cl = struct.unpack('>I', old[4:8])[0]; p = 8 + cl
                el = struct.unpack('>H', old[p:p+2])[0]
                assert el == 0, 'exception table present'
                a[1] = bytearray(struct.pack('>HHI', max_stack, max_locals, len(code)) + code + b'\x00\x00' + b'\x00\x00')
                return
        raise KeyError('Code')

    def code_of(self, m):
        for a in m[3]:
            if self.utf(a[0]) == 'Code':
                cl = struct.unpack('>I', a[1][4:8])[0]; return bytes(a[1][8:8+cl]), struct.unpack('>HH', a[1][0:4])
        raise KeyError('Code')

    def dump(self):
        out = bytearray(self.d[:8]) + struct.pack('>H', len(self.cp))
        for e in self.cp[1:]:
            if e is not None: out += e
        out += struct.pack('>HHH', self.access, self.this, self.super) + self.ifaces
        for group in (self.fields, self.methods):
            out += struct.pack('>H', len(group))
            for acc, nm, ds, attrs in group:
                out += struct.pack('>HHHH', acc, nm, ds, len(attrs))
                for an, ab in attrs: out += struct.pack('>HI', an, len(ab)) + ab
        return bytes(out + self.attrs)


def h(i): return struct.pack('>H', i)


def patch(d):
    cf = ClassFile(d)
    # ---- <init>: swap SingleAspect for LevelAspect(this, 1000)
    init = cf.method('<init>', '(I)V')
    code, (ms, ml) = cf.code_of(init)
    single_cls = cf.C(SINGLE); single_init = cf.M(SINGLE, '<init>', '(' + IMOD + ')V')
    old = b'\xbb' + h(single_cls) + b'\x59\x2a\xb7' + h(single_init)
    assert code.count(old) == 1, 'SingleAspect construction pattern not found'
    new = (b'\xbb' + h(cf.C(LEVEL)) + b'\x59\x2a' + b'\x11' + struct.pack('>h', 1000) +
           b'\xb7' + h(cf.M(LEVEL, '<init>', '(' + IMOD + 'I)V')))
    cf.set_code(init, ms + 1, ml, code.replace(old, new))

    # ---- applyEffect: modifiers += max(1, tier-1) * max(1, level)
    ae = cf.method('applyEffect', '(' + NBT + NBT + ')V')
    c = bytearray()
    c += b'\x2b' + b'\xb8' + h(cf.M(TAGUTIL, 'getToolStats', '(' + NBT + ')L' + TOOLNBT + ';')) + b'\x4e'   # aload_1; getToolStats; astore_3
    c += b'\x2d\x59' + b'\xb4' + h(cf.F(TOOLNBT, 'modifiers', 'I'))                                        # aload_3; dup; getfield modifiers
    c += b'\x2a' + b'\xb6' + h(cf.M(MOD, 'getIdentifier', '()Ljava/lang/String;'))                         # aload_0; getIdentifier
    c += b'\x59' + b'\xb6' + h(cf.M('java/lang/String', 'length', '()I')) + b'\x04\x64'                     # dup; length; iconst_1; isub
    c += b'\xb6' + h(cf.M('java/lang/String', 'charAt', '(I)C'))                                            # charAt
    c += b'\x10\x30\x64' + b'\x04\x64' + b'\x04'                                                            # bipush 48; isub; iconst_1; isub; iconst_1
    mx = cf.M('java/lang/Math', 'max', '(II)I')
    c += b'\xb8' + h(mx)                                                                                    # max(tier-1, 1)
    c += b'\x2c' + b'\xb8' + h(cf.M(MNBT, 'readTag', '(' + NBT + ')L' + MNBT + ';'))                        # aload_2; readTag
    c += b'\xb4' + h(cf.F(MNBT, 'level', 'I')) + b'\x04' + b'\xb8' + h(mx)                                   # .level; iconst_1; max
    c += b'\x68\x60' + b'\xb5' + h(cf.F(TOOLNBT, 'modifiers', 'I'))                                          # imul; iadd; putfield
    c += b'\x2b\x2d' + b'\xb6' + h(cf.M(TOOLNBT, 'get', '()' + NBT))                                        # aload_1; aload_3; get
    c += b'\xb8' + h(cf.M(TAGUTIL, 'setToolTag', '(' + NBT + NBT + ')V')) + b'\xb1'                         # setToolTag; return
    cf.set_code(ae, 5, 4, bytes(c))
    return cf.dump()


def main(src, dst):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        hit = False
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == CLS: data = patch(data); hit = True
            zout.writestr(info, data)
    print('patched' if hit else 'CLASS NOT FOUND')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
