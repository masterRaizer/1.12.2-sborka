"""Tune Apotheosis configs in a config/apotheosis dir. Usage: tune.py <dir> [bosses] [spawners] [chorus] [reeds]"""
import re, sys, os
d = sys.argv[1]; opts = set(sys.argv[2:])
BOSSES = ["minecraft:wither","minecraft:ender_dragon","minecraft:elder_guardian","minecraft:giant",
 "draconicevolution:chaosguardian","mowziesmobs:barako","mowziesmobs:barakoan_player","mowziesmobs:ferrous_wroughtnaut",
 "mowziesmobs:frostmaw","mowziesmobs:naga","modernbackports:warden","modernbackports:hornet_queen",
 "modernbackports:brood_mother","modernbackports:summoner","modernbackports:alchemist","modernbackports:barnacle",
 "modernbackports:stalker","shatteredcitadels:guardian_mage","atum:pharaoh","artifacts:mimic"]
def edit(name, fn):
    p = os.path.join(d, name); s = open(p, encoding='utf-8', newline='').read(); n = fn(s)
    if n != s: open(p, 'w', encoding='utf-8', newline='').write(n); print('edited', name)
def setv(s, key, val):
    pat = re.compile(r'(%s"?%s"?=)[^\r\n]*' % (re.escape(key[:2]), re.escape(key[2:])))
    n, c = pat.subn(lambda m: m.group(1) + val, s)
    if c == 0: print('  NOT FOUND', key)
    return n
if 'bosses' in opts:
    def f(s):
        for b in BOSSES:
            if ('"%s"=' % b) in s: s = setv(s, 'I:' + b, '0')
            else: print('  absent', b)
        return s
    edit('deadly.cfg', f)
if 'spawners' in opts:
    edit('deadly.cfg', lambda s: setv(setv(s, 'S:Brutal Spawner Chance', '0.04'), 'S:Swarm Spawner Chance', '0.05'))
if 'chorus' in opts:
    # ignore_spawn_cap: value 0 already; set max_value 0 so the modifier cannot be enabled
    def f(s):
        m = re.search(r'ignore_spawn_cap \{.*?\}', s, re.S); blk = m.group(0)
        nb = re.sub(r'S:item=[^\r\n]*', 'S:item=minecraft:barrier', blk)
        return s.replace(blk, nb)
    edit('spawner.cfg', f)
if 'reeds' in opts:
    edit('garden.cfg', lambda s: setv(s, 'I:Reed Height', '5'))
