"""For each jar: class versions, Java 9+ bootstraps, Cleanroom/LWJGL3 references, v>52 class names (first few)."""
import sys, os, glob, zipfile, collections
PATS = [b'org/lwjgl/glfw', b'org/lwjgl/opengl/GL4', b'com/cleanroommc', b'ObjectMethods', b'SwitchBootstraps', b'java/lang/Record',
        b'StringConcatFactory', b'NestHost', b'org/lwjgl/system/MemoryStack']
d = sys.argv[1]
for j in sorted(glob.glob(os.path.join(d, '*.jar'))):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    vers = collections.Counter(); hits = collections.Counter(); newer = []
    for n in z.namelist():
        if not n.endswith('.class'): continue
        b = z.read(n)
        if b[:4] != b'\xca\xfe\xba\xbe': continue
        v = int.from_bytes(b[6:8], 'big'); vers[v] += 1
        if v > 52 and len(newer) < 3: newer.append(n)
        for p in PATS:
            if p in b: hits[p.decode()] += 1
    if max(vers or {0: 0}) > 52 or hits:
        print(os.path.basename(j), dict(vers), dict(hits), newer)
