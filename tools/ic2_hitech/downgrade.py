"""Downgrade Java 11-16 class files in a jar to Java 8 (class version 52), in place of a copy.

Handles what javac 16 emits for plain code:
  * NestHost/NestMembers: attributes removed, private members of nest classes made package-private
    (interfaces: public), so inner classes can still reach them on Java 8.
  * invokedynamic StringConcatFactory: replaced by invokestatic of a generated static helper
    (StringBuilder chain) with the same descriptor, padded with 2 NOPs -> code length, branch
    offsets and StackMapTable stay valid.
Anything else (records, Java 9+ library calls) is reported, not fixed.
Usage: python -I downgrade.py in.jar out.jar
"""
import os, struct, sys, zipfile, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfparse import ClassFile

OPLEN = {}
for op in range(256): OPLEN[op] = 1
for op in (0x10, 0x12, 0x15, 0x16, 0x17, 0x18, 0x19, 0x36, 0x37, 0x38, 0x39, 0x3a, 0xa9, 0xbc): OPLEN[op] = 2
for op in (0x11, 0x13, 0x14, 0x84, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xbb, 0xbd, 0xc0, 0xc1, 0xc6, 0xc7) + tuple(range(0x99, 0xa9)): OPLEN[op] = 3
OPLEN[0xc5] = 4
for op in (0xb9, 0xba, 0xc8, 0xc9): OPLEN[op] = 5


def instructions(code):
    i = 0
    while i < len(code):
        op = code[i]
        if op == 0xaa:  # tableswitch
            p = (i + 4) & ~3
            lo, hi = struct.unpack_from('>ii', code, p + 4)
            ln = p + 12 + 4 * (hi - lo + 1) - i
        elif op == 0xab:  # lookupswitch
            p = (i + 4) & ~3
            n = struct.unpack_from('>i', code, p + 4)[0]
            ln = p + 8 + 8 * n - i
        elif op == 0xc4:  # wide
            ln = 6 if code[i + 1] == 0x84 else 4
        else:
            ln = OPLEN[op]
        yield i, op, ln
        i += ln


def parse_desc(desc):
    args = re.findall(r'\[*(?:L[^;]+;|[ZBCSIJFD])', desc[1:desc.index(')')])
    return args, desc[desc.index(')') + 1:]


APPEND = {'Z': '(Z)', 'C': '(C)', 'B': '(I)', 'S': '(I)', 'I': '(I)', 'J': '(J)', 'F': '(F)', 'D': '(D)'}
LOAD = {'Z': 0x15, 'C': 0x15, 'B': 0x15, 'S': 0x15, 'I': 0x15, 'J': 0x16, 'F': 0x17, 'D': 0x18}


def concat_helper(cf, name, desc, recipe, consts):
    args, _ = parse_desc(desc)
    sb = 'java/lang/StringBuilder'
    code = bytearray()
    code += b'\xbb' + struct.pack('>H', cf.klass(sb)) + b'\x59'
    code += b'\xb7' + struct.pack('>H', cf.mref(sb, '<init>', '()V'))
    slot, ai, ci = 0, 0, 0
    text = ''

    def flush_text():
        nonlocal text
        if text:
            code.extend(b'\x13' + struct.pack('>H', cf.string(text)))
            code.extend(b'\xb6' + struct.pack('>H', cf.mref(sb, 'append', '(Ljava/lang/String;)L%s;' % sb)))
            text = ''

    for ch in recipe:
        if ch == '\x01':
            flush_text()
            a = args[ai]; ai += 1
            if a in LOAD:
                code.extend(bytes([LOAD[a], slot]))
                adesc = APPEND[a] + 'L%s;' % sb
                slot += 2 if a in 'JD' else 1
            else:
                code.extend(bytes([0x19, slot]))
                slot += 1
                adesc = ('(Ljava/lang/String;)' if a == 'Ljava/lang/String;' else '(Ljava/lang/Object;)') + 'L%s;' % sb
            code.extend(b'\xb6' + struct.pack('>H', cf.mref(sb, 'append', adesc)))
        elif ch == '\x02':
            text += consts[ci]; ci += 1
        else:
            text += ch
    flush_text()
    code += b'\xb6' + struct.pack('>H', cf.mref(sb, 'toString', '()Ljava/lang/String;')) + b'\xb0'
    body = struct.pack('>HHI', 6, max(slot, 1), len(code)) + code + struct.pack('>HH', 0, 0)
    cf.methods.append([0x1009, cf.utf8(name), cf.utf8(desc), [[cf.utf8('Code'), bytearray(body)]]])


def downgrade(b, report):
    cf = ClassFile(b)
    if cf.major <= 52:
        return b
    cname = cf.cp.cls(cf.this)
    names = {i: cf.cp.utf(a[0]) for i, a in enumerate(cf.attrs)}
    nest = any(n in ('NestHost', 'NestMembers') for n in names.values())
    for n in names.values():
        if n in ('Record', 'PermittedSubclasses'):
            report.append('%s: has %s (not handled)' % (cname, n))
    cf.attrs = [a for a in cf.attrs if cf.cp.utf(a[0]) not in ('NestHost', 'NestMembers')]
    is_iface = bool(cf.access & 0x0200)
    if nest:
        for group in (cf.fields, cf.methods):
            for m in group:
                if m[0] & 0x0002:
                    m[0] &= ~0x0002
                    if is_iface:
                        m[0] |= 0x0001
    # bootstrap methods
    bsms = []
    for a in cf.attrs:
        if cf.cp.utf(a[0]) == 'BootstrapMethods':
            d = a[1]; n = struct.unpack_from('>H', d, 0)[0]; p = 2
            for _ in range(n):
                mh, na = struct.unpack_from('>HH', d, p); p += 4
                bargs = list(struct.unpack_from('>%dH' % na, d, p)); p += 2 * na
                bsms.append((mh, bargs))
    helper = 0
    for m in list(cf.methods):
        for a in m[3]:
            if cf.cp.utf(a[0]) != 'Code':
                continue
            d = a[1]
            clen = struct.unpack_from('>I', d, 4)[0]
            code = d[8:8 + clen]
            for pos, op, ln in instructions(bytes(code)):
                if op != 0xba:
                    continue
                idx = struct.unpack_from('>H', code, pos + 1)[0]
                tag, (bsm_i, nat_i) = cf.cp.e[idx]
                mh, bargs = bsms[bsm_i]
                kind, ref = cf.cp.e[mh][1]
                owner, mname, _ = cf.cp.ref(ref)
                if owner != 'java/lang/invoke/StringConcatFactory':
                    continue
                iname, idesc = cf.cp.nat(nat_i)
                if mname == 'makeConcatWithConstants':
                    recipe = cf.cp.utf(cf.cp.e[bargs[0]][1])
                    consts = []
                    for c in bargs[1:]:
                        t, v = cf.cp.e[c]
                        consts.append(cf.cp.utf(v) if t == 8 else str(struct.unpack('>i', v)[0]) if t == 3 else '?')
                else:  # makeConcat: all args, no constants
                    recipe = '\x01' * len(parse_desc(idesc)[0])
                    consts = []
                hname = 'jdg$concat$%d' % helper
                helper += 1
                concat_helper(cf, hname, idesc, recipe, consts)
                mref = cf.add(11 if is_iface else 10, (cf.this, cf.nat(hname, idesc)))
                code[pos:pos + 5] = b'\xb8' + struct.pack('>H', mref) + b'\x00\x00'
            d[8:8 + clen] = code
    if helper:
        report.append('%s: %d string concat call sites rewritten' % (cname, helper))
    # Java 9 covariant overrides in java.nio buffers (IntBuffer.rewind() -> IntBuffer): use the Java 8
    # Buffer signature. Only safe where the result is popped or used as a Buffer - reported for review.
    for i, e in enumerate(list(cf.cp.e)):
        if e and e[0] == 10:
            owner, nm, d = cf.cp.ref(i)
            if re.fullmatch(r'java/nio/\w+Buffer', owner) and owner != 'java/nio/Buffer' \
                    and nm in ('flip', 'rewind', 'clear', 'mark', 'reset', 'position', 'limit') and d.endswith(')L%s;' % owner):
                nd = d[:d.index(')') + 1] + 'Ljava/nio/Buffer;'
                cf.cp.e[i] = (10, (e[1][0], cf.nat(nm, nd)))
                report.append('%s: %s.%s%s -> %s (check result is not used as %s)' % (cname, owner, nm, d, nd, owner))
    if SHIM:
        apply_shims(cf, cname, bsms, is_iface, report)
    cf.major, cf.minor = 52, 0
    return cf.to_bytes()


SHIM = None  # internal name of the injected shim class, e.g. jdgshim/htc_reactors/Shim
OBJ = 'Ljava/lang/Object;'


def shim_target(owner, name, desc, op):
    """(shim method, shim desc) for a Java 9+ library call, or None."""
    args, ret = parse_desc(desc)
    if op == 0xb8 and owner in ('java/util/List', 'java/util/Set', 'java/util/Map'):
        kind = {'java/util/List': 'list', 'java/util/Set': 'set', 'java/util/Map': 'map'}[owner]
        if name == 'of':
            return kind + 'Of', desc
        if name == 'copyOf' and kind == 'list':
            return 'copyOfList', '(Ljava/util/Collection;)Ljava/util/List;'
    inst = {('java/util/stream/Stream', 'toList'): 'toList', ('java/util/Optional', 'isEmpty'): 'optIsEmpty',
            ('java/util/Optional', 'orElseThrow'): 'optOrElseThrow', ('java/lang/String', 'isBlank'): 'strIsBlank',
            ('java/lang/String', 'strip'): 'strStrip', ('java/lang/String', 'repeat'): 'strRepeat'}
    if op in (0xb6, 0xb9):
        if (owner, name) in inst and not (name == 'orElseThrow' and args):
            return inst[(owner, name)], '(L%s;%s)%s' % (owner, ''.join(args), ret)
        if owner in ('java/util/List', 'java/util/ArrayList', 'java/util/SequencedCollection') and \
                name in ('addFirst', 'addLast', 'getFirst', 'getLast', 'removeFirst', 'removeLast'):
            r = 'V' if name.startswith('add') else OBJ
            return name, '(Ljava/util/List;%s)%s' % (''.join(OBJ for _ in args), r)
    return None


def apply_shims(cf, cname, bsms, is_iface, report):
    # records: Record -> Object, MatchException -> RuntimeException
    for i, e in enumerate(cf.cp.e):
        if e and e[0] == 7:
            n = cf.cp.utf(e[1])
            if n == 'java/lang/Record':
                cf.cp.e[i] = (7, cf.utf8('java/lang/Object'))
            elif n == 'java/lang/MatchException':
                cf.cp.e[i] = (7, cf.utf8('java/lang/RuntimeException'))
    cf.attrs = [a for a in cf.attrs if cf.cp.utf(a[0]) != 'Record']
    n_fix = 0
    for m in cf.methods:
        for a in m[3]:
            if cf.cp.utf(a[0]) != 'Code':
                continue
            d = a[1]
            clen = struct.unpack_from('>I', d, 4)[0]
            code = d[8:8 + clen]
            for pos, op, ln in instructions(bytes(code)):
                if op == 0xba:
                    idx = struct.unpack_from('>H', code, pos + 1)[0]
                    tag, (bsm_i, nat_i) = cf.cp.e[idx]
                    mh = bsms[bsm_i][0]
                    owner = cf.cp.ref(cf.cp.e[mh][1][1])[0]
                    if owner == 'java/lang/runtime/ObjectMethods':
                        iname, idesc = cf.cp.nat(nat_i)
                        target = {'toString': ('recordToString', '(Ljava/lang/Object;)Ljava/lang/String;'),
                                  'hashCode': ('recordHashCode', '(Ljava/lang/Object;)I'),
                                  'equals': ('recordEquals', '(Ljava/lang/Object;Ljava/lang/Object;)Z')}[iname]
                        code[pos:pos + 5] = b'\xb8' + struct.pack('>H', cf.mref(SHIM, *target)) + b'\x00\x00'
                        n_fix += 1
                    continue
                if op not in (0xb6, 0xb8, 0xb9):
                    continue
                idx = struct.unpack_from('>H', code, pos + 1)[0]
                e = cf.cp.e[idx]
                if not e or e[0] not in (10, 11):
                    continue
                owner, name, desc = cf.cp.ref(idx)
                t = shim_target(owner, name, desc, op)
                if not t:
                    continue
                new = b'\xb8' + struct.pack('>H', cf.mref(SHIM, t[0], t[1]))
                code[pos:pos + ln] = new + b'\x00' * (ln - 3)
                n_fix += 1
            d[8:8 + clen] = code
    if n_fix:
        report.append('%s: %d Java 9+ calls/record methods routed to %s' % (cname, n_fix, SHIM))


def build_shim(pkg):
    """Compile shim/Shim.java.tmpl with JDK 8 into package pkg; returns class bytes."""
    import subprocess, tempfile, shutil
    here = os.path.dirname(os.path.abspath(__file__))
    tmpl = open(os.path.join(here, 'shim', 'Shim.java.tmpl')).read().replace('PKG', pkg.replace('/', '.'))
    work = tempfile.mkdtemp()
    try:
        src = os.path.join(work, 'Shim.java')
        open(src, 'w').write(tmpl)
        javac = os.path.join(os.environ['USERPROFILE'], '.gradle', 'jdks', 'azul_systems__inc_-8-amd64-windows.2', 'bin', 'javac')
        subprocess.check_call([javac, '-nowarn', '-Xlint:none', '-d', work, src])
        return open(os.path.join(work, *pkg.split('/'), 'Shim.class'), 'rb').read()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(src, dst, shim_pkg=None):
    global SHIM
    report = []
    zin = zipfile.ZipFile(src)
    shim_bytes = None
    if shim_pkg:
        SHIM = shim_pkg + '/Shim'
        shim_bytes = build_shim(shim_pkg)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        if shim_bytes:
            zout.writestr(SHIM + '.class', shim_bytes)
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith('.class') and not info.filename.startswith('META-INF/') and data[:4] == b'\xca\xfe\xba\xbe' \
                    and int.from_bytes(data[6:8], 'big') > 52:
                data = downgrade(data, report)
                report.append('downgraded ' + info.filename)
            zout.writestr(info, data)
    print('\n'.join(report))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
