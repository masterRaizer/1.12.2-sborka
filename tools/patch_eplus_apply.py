"""Second Enchanting Plus patch: accept enchantments that the ITEM allows at an enchanting table.

Adds to net/darkhax/eplus/EnchLogic:
    public static boolean eplusCanApply(Enchantment e, ItemStack s) {
        return e.canApply(s) | e.canApplyAtEnchantingTable(s);   // branch-free, no StackMapTable needed
    }
and redirects the single `invokevirtual Enchantment.func_92089_a(ItemStack)Z` (canApply) call in
getValidEnchantments to it (same 3-byte length, same stack effect).

Usage: python -I patch_eplus_apply.py <in.jar> <out.jar>
"""
import struct, sys, zipfile

sys.path.insert(0, __file__.rsplit('\\', 1)[0].rsplit('/', 1)[0])
from patch_eplus import read_cp, find_methodref, instr_offsets, utf

CLS = 'net/darkhax/eplus/EnchLogic.class'
ENCH = 'net/minecraft/enchantment/Enchantment'
DESC_S = '(Lnet/minecraft/item/ItemStack;)Z'
NEW_NAME, NEW_DESC = 'eplusCanApply', '(Lnet/minecraft/enchantment/Enchantment;Lnet/minecraft/item/ItemStack;)Z'


def u(s): b = s.encode(); return b'\x01' + struct.pack('>H', len(b)) + b


def patch(d):
    cp, cp_end = read_cp(d)
    can_apply = find_methodref(cp, ENCH, 'func_92089_a', DESC_S)
    assert can_apply, 'canApply ref not found'
    ench_cls = struct.unpack('>H', cp[can_apply][1][1:3])[0]
    this_cls = struct.unpack('>H', d[cp_end+2:cp_end+4])[0]
    code_utf = next(i for i, e in enumerate(cp) if e and e[0] == 1 and utf(cp, i) == 'Code')
    n = len(cp)
    new = [u('canApplyAtEnchantingTable'), u(DESC_S),                                   # n, n+1
           b'\x0c' + struct.pack('>HH', n, n + 1),                                      # n+2 NaT
           b'\x0a' + struct.pack('>HH', ench_cls, n + 2),                               # n+3 Methodref atTable
           u(NEW_NAME), u(NEW_DESC),                                                     # n+4, n+5
           b'\x0c' + struct.pack('>HH', n + 4, n + 5),                                  # n+6 NaT
           b'\x0a' + struct.pack('>HH', this_cls, n + 6)]                               # n+7 Methodref helper
    at_table, helper = n + 3, n + 7

    # locate methods section
    p = cp_end + 6
    ic = struct.unpack('>H', d[p:p+2])[0]; p += 2 + 2 * ic

    def skip_attrs(p):
        c = struct.unpack('>H', d[p:p+2])[0]; p += 2
        for _ in range(c): p += 6 + struct.unpack('>I', d[p+2:p+6])[0]
        return p
    fc = struct.unpack('>H', d[p:p+2])[0]; p += 2
    for _ in range(fc): p = skip_attrs(p + 6)
    mcount_at = p
    mc = struct.unpack('>H', d[p:p+2])[0]; p += 2
    for _ in range(mc): p = skip_attrs(p + 6)
    methods_end = p

    code = (b'\x2a\x2b\xb6' + struct.pack('>H', can_apply) +
            b'\x2a\x2b\xb6' + struct.pack('>H', at_table) +
            b'\x80\xac')                                                                 # ior, ireturn
    code_attr = (struct.pack('>HI', code_utf, 12 + len(code)) + struct.pack('>HHI', 3, 2, len(code)) +
                 code + struct.pack('>HH', 0, 0))
    method = struct.pack('>HHHH', 0x0009, n + 4, n + 5, 1) + code_attr

    body = bytearray(d[cp_end:])
    # redirect the canApply call(s) inside existing code
    from patch_eplus import code_ranges
    count = 0
    for start, length in code_ranges(d, cp_end):
        for pc, o in instr_offsets(d, start, length):
            at = start + pc
            if o == 0xb6 and struct.unpack('>H', d[at+1:at+3])[0] == can_apply:
                body[at - cp_end] = 0xb8
                body[at - cp_end + 1:at - cp_end + 3] = struct.pack('>H', helper)
                count += 1
    body[mcount_at - cp_end:mcount_at - cp_end + 2] = struct.pack('>H', mc + 1)
    body = body[:methods_end - cp_end] + method + body[methods_end - cp_end:]
    out = d[:8] + struct.pack('>H', n + len(new)) + d[10:cp_end] + b''.join(new) + bytes(body)
    return out, count


def main(src, dst):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == CLS:
                data, c = patch(data); print('redirected canApply calls:', c)
            zout.writestr(info, data)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
