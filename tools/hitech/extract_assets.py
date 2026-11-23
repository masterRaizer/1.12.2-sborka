"""Copy HiTech's ContentTweaker/MM/Requious assets into <game>/resources/<domain> (ContentTweaker's resource folder).
Order like on HiTech: their resources/ folder first, then the ModernHitech.zip resource pack on top (it has priority there).
Usage: python -I extract_assets.py <hitech client dir> <target minecraft dir> domain...
"""
import os, sys, shutil, zipfile
src, dst = sys.argv[1], sys.argv[2]
domains = sys.argv[3:]
for d in domains:
    out = os.path.join(dst, 'resources', d)
    rsrc = os.path.join(src, 'resources', d)
    if os.path.isdir(rsrc):
        shutil.copytree(rsrc, out, dirs_exist_ok=True)
z = zipfile.ZipFile(os.path.join(src, 'resourcepacks', 'ModernHitech.zip'))
count = {}
for info in z.infolist():
    parts = info.filename.split('/')
    if len(parts) > 2 and parts[0] == 'assets' and parts[1] in domains and not info.is_dir():
        target = os.path.join(dst, 'resources', parts[1], *parts[2:])
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'wb') as f:
            f.write(z.read(info))
        count[parts[1]] = count.get(parts[1], 0) + 1
print(count)
