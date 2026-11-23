"""Jar clean-up for Forge 1.12 on Java 8: drop META-INF/versions/** (multi-release), drop manifest lines
'ModType: CRL' (Cleanroom-only marker, FML skips such jars) and 'Multi-Release'. Usage: fixjar.py in.jar [out.jar]"""
import sys, os, zipfile, re
src = sys.argv[1]; dst = sys.argv[2] if len(sys.argv) > 2 else src
zin = zipfile.ZipFile(src); tmp = dst + '.tmp'; dropped = 0
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        if info.filename.startswith('META-INF/versions/'):
            dropped += 1; continue
        data = zin.read(info.filename)
        if info.filename == 'META-INF/MANIFEST.MF':
            text = data.decode('utf-8').replace('\r\n', '\n')
            text = re.sub(r'\n(?=[ ])', '\x00', text)  # join continuation lines temporarily
            lines = [l for l in text.split('\n') if not l.startswith('ModType:') and not l.startswith('Multi-Release:')]
            data = '\r\n'.join(lines).replace('\x00', '\r\n').encode('utf-8')
        zout.writestr(info, data)
zin.close(); os.replace(tmp, dst)
print(os.path.basename(dst), 'dropped versioned entries:', dropped)
