"""Remove mixin class entries from mixin JSON configs inside a jar.
Usage: python -I patch_mixinjson.py jar config.json:Entry[,Entry] ... ('*' empties the config)"""
import sys, os, json, zipfile
jar = sys.argv[1]; rules = {}
for r in sys.argv[2:]:
    cfg, ents = r.split(':', 1); rules[cfg] = set(ents.split(','))
zin = zipfile.ZipFile(jar); tmp = jar + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename in rules:
            j = json.loads(data); drop = rules[info.filename]
            for k in ('mixins', 'client', 'server'):
                if j.get(k):
                    j[k] = [] if '*' in drop else [m for m in j[k] if m not in drop]
            j['required'] = False
            data = json.dumps(j, indent=2).encode()
            print(info.filename, {k: j.get(k) for k in ('mixins', 'client', 'server')})
        zout.writestr(info, data)
zin.close(); os.replace(tmp, jar)
