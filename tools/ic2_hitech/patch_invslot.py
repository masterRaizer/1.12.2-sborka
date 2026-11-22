"""Make mods built for IC2 2.8.1xx call the IC2 2.8.2xx InvSlot constructors (TileEntityInventory -> IInventorySlotHolder).
Usage: python -I patch_invslot.py in.jar out.jar"""
import sys, os, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfparse import ClassFile
OLD, NEW = '(Lic2/core/block/TileEntityInventory;', '(Lic2/core/block/IInventorySlotHolder;'
zin = zipfile.ZipFile(sys.argv[1]); n_fix = 0
with zipfile.ZipFile(sys.argv[2], 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename.endswith('.class') and not info.filename.startswith('META-INF/'):
            cf = ClassFile(data); changed = False
            for i, e in enumerate(list(cf.cp.e)):
                if e and e[0] == 10:
                    o, nm, d = cf.cp.ref(i)
                    if o.startswith('ic2/core/block/invslot/') and nm == '<init>' and d.startswith(OLD):
                        cf.cp.e[i] = (10, (e[1][0], cf.nat(nm, NEW + d[len(OLD):]))); changed = True; n_fix += 1
                        print(info.filename, o, d)
            if changed: data = cf.to_bytes()
        zout.writestr(info, data)
print('fixed refs:', n_fix)
