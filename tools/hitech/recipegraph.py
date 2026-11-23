"""Dependency tree of HiTech items: which recipes make an item and what they need.
Parses HiTech's CraftTweaker scripts (shaped/shapeless, IC2 machine tweaks, Modular Machinery / Requious builders).
Usage: python -I recipegraph.py <scripts dir> <items.tsv of our pack> <target item>...
"""
import os, re, sys, glob, collections

sdir, ours_tsv = sys.argv[1], sys.argv[2]
targets = sys.argv[3:]
ours = set()
for line in open(ours_tsv, encoding='utf-8'):
    p = line.split('\t')
    if len(p) > 2: ours.add(p[0])

ITEM = re.compile(r'<([a-z0-9_]+:[a-z0-9_./]+)(?::(\d+|\*))?>')
recipes = collections.defaultdict(list)  # out id -> list of (kind, file, inputs set)


def norm(m):
    return m.group(1) + (':' + m.group(2) if m.group(2) and m.group(2) != '*' else '')


for f in glob.glob(os.path.join(sdir, '*.zs')):
    text = open(f, encoding='utf-8', errors='replace').read()
    text = re.sub(r'//[^\n]*', '', text)
    name = os.path.basename(f)
    # crafting table: recipes.addShaped(["id",] <out>..., [[...]]) ; addShapeless
    for m in re.finditer(r'recipes\.addShap(?:ed|eless)\((?:"[^"]*",\s*)?(<[^>]+>)(.*?)\]\s*\)?\s*(?:,|\))', text, re.S):
        out = ITEM.search(m.group(1))
        if not out: continue
        ins = {norm(x) for x in ITEM.finditer(m.group(2))}
        recipes[norm(out)].append(('craft', name, ins))
    # IC2 machine tweaks: mods.ic2.X.addRecipe(<out>, <in>)
    for m in re.finditer(r'mods\.ic2\.(\w+)\.(?:add\w*Recipe)\(([^;]*)\);', text):
        its = [norm(x) for x in ITEM.finditer(m.group(2))]
        if len(its) >= 2: recipes[its[0]].append(('ic2.' + m.group(1), name, set(its[1:])))
    # Modular Machinery / Requious builders: val x = ...newBuilder("id","machine",t); x.addItemInput(...); x.addItemOutput(...)
    for m in re.finditer(r'(?:val\s+(\w+)\s*=\s*)?(?:mods\.modularmachinery\.)?RecipeBuilder\.newBuilder\("([^"]+)",\s*"([^"]+)"[^;]*;?', text):
        var, rid, machine = m.group(1), m.group(2), m.group(3)
        end = text.find('.build()', m.end())
        chunk = text[m.start():end]
        ins = {norm(x) for x in re.finditer(r'addItemInput\((<[^>]+>)', chunk) for x in [ITEM.search(x.group(1))] if x}
        ins |= {'(machine) ' + machine}
        for o in re.finditer(r'addItemOutput\((<[^>]+>)', chunk):
            oi = ITEM.search(o.group(1))
            if oi: recipes[norm(oi)].append(('mm:' + machine, name, ins))

seen = set()


def known(i):
    base = ':'.join(i.split(':')[:2])
    return base in ours


def walk(item, depth):
    pad = '  ' * depth
    status = 'OURS' if known(item) and not item.startswith('contenttweaker') else 'MISSING'
    rs = recipes.get(item) or recipes.get(':'.join(item.split(':')[:2]))
    print('%s%s [%s]%s' % (pad, item, status, '' if rs else ' (no recipe in scripts)'))
    if item in seen or depth > 12: return
    seen.add(item)
    if status == 'OURS' and not rs: return
    if rs:
        kind, f, ins = rs[0]
        print('%s  via %s (%s)%s' % (pad, kind, f, '  +%d more recipes' % (len(rs) - 1) if len(rs) > 1 else ''))
        for i in sorted(ins):
            if i.startswith('(machine)'):
                print('%s    %s' % (pad, i)); continue
            if known(i) and not i.startswith('contenttweaker') and not recipes.get(i):
                continue
            walk(i, depth + 2)


for t in targets:
    walk(t, 0)
print('\nMISSING items in the tree:', sorted(i for i in seen if not known(i) or i.startswith('contenttweaker')))
