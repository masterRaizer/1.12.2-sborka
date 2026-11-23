"""Copy HiTech CraftTweaker scripts into a game dir for this pack.
- every recipe REMOVAL is disabled (owner: keep our recipes, only add theirs) -> //[pack: removal disabled]
- items of mods we don't have are swapped for an equivalent (substitutes.json) or, when null, the whole statement
  that uses them is commented out /*[pack: missing item]...*/ so one missing item does not abort the whole file.
Usage: python -I copy_scripts.py <hitech scripts dir> <target scripts dir> <glob>...
"""
import os, re, sys, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
SUBS = json.load(open(os.path.join(HERE, 'substitutes.json'), encoding='utf-8'))
SUBS.pop('_comment', None)
DROP = [re.compile(x) for x in SUBS.pop('_drop_patterns', [])]
REMOVAL = re.compile(r'(recipes\.remove|\.remove\s*\(|removeShaped|removeShapeless|removeAll|removeRecipe|\.removeOutput|'
                     r'JEI\.(hide|removeAndHide)|furnace\.remove|\.removeFuel|\.removeInput|banItem|\.ban\()')
BRACKET = re.compile(r'<\s*([a-z0-9_]+)\s*:\s*([a-z0-9_./]+)\s*(?::\s*(\d+|\*)\s*)?>')


def item_key(m):
    return m.group(1) + ':' + m.group(2) + (':' + m.group(3) if m.group(3) else '')


def lookup(key):
    """substitute target, None = drop, False = keep as is"""
    for k in (key, key.rsplit(':', 1)[0] if key.count(':') > 1 else None):
        if k and k in SUBS: return SUBS[k]
    for k, v in SUBS.items():
        if k.endswith(':') and key.startswith(k): return v
    return False


def substitute(text):
    n = [0]
    def rep(m):
        t = lookup(item_key(m))
        if t:
            n[0] += 1
            return '<' + t + '>'
        return m.group(0)
    return BRACKET.sub(rep, text), n[0]


def statements(text):
    """(start, end) spans of top-level-ish statements ending with ';' (paren/bracket depth 0)."""
    spans, i, start, depth = [], 0, 0, 0
    L = len(text)
    while i < L:
        c = text[i]
        if text.startswith('//', i):
            j = text.find('\n', i); i = L if j < 0 else j; continue
        if text.startswith('/*', i):
            j = text.find('*/', i + 2); i = L if j < 0 else j + 2; continue
        if c in '"\'':
            j = i + 1
            while j < L and text[j] != c:
                j += 2 if text[j] == '\\' else 1
            i = j + 1; continue
        if c in '([': depth += 1
        elif c in ')]': depth -= 1
        elif depth == 0 and c in '{}':
            start = i + 1
        elif depth == 0 and c == ';':
            spans.append((start, i + 1)); start = i + 1
        i += 1
    return spans


def drop_missing(text):
    out, last, dropped = [], 0, 0
    for s, e in statements(text):
        body = text[s:e]
        if (any(lookup(item_key(m)) is None for m in BRACKET.finditer(body)) or any(d.search(body) for d in DROP)) and '*/' not in body:
            lead = len(body) - len(body.lstrip())
            out.append(text[last:s + lead]); out.append('/*[pack: missing item] ' + body[lead:] + '*/')
            last = e; dropped += 1
    out.append(text[last:])
    return ''.join(out), dropped


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    tot = [0, 0, 0]
    for pat in sys.argv[3:]:
        for f in sorted(glob.glob(os.path.join(src, pat))):
            lines, nrem = [], 0
            for line in open(f, encoding='utf-8', errors='replace').read().split('\n'):
                s = line.strip()
                if not s.startswith('//') and REMOVAL.search(line) and s.endswith(';') and s.count('(') == s.count(')'):
                    lines.append('//[pack: removal disabled] ' + line); nrem += 1
                else:
                    lines.append(line)
            text, nsub = substitute('\n'.join(lines))
            text, ndrop = drop_missing(text)
            open(os.path.join(dst, os.path.basename(f)), 'w', encoding='utf-8').write(text)
            tot[0] += nrem; tot[1] += nsub; tot[2] += ndrop
            if nrem or nsub or ndrop:
                print('%-42s removals off %3d, swapped %3d, dropped %3d' % (os.path.basename(f), nrem, nsub, ndrop))
    print('total: removals disabled %d, items swapped %d, statements dropped %d' % tuple(tot))


if __name__ == '__main__':
    main()
