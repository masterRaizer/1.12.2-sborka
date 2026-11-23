"""Сколько блоков реально ставит жила размера N (алгоритм WorldGenMinable 1.12 / CoFH), в сплошном камне."""
import math, random, sys
def vein(size, rnd, cofh):
    f = rnd.random() * math.pi
    d0 = 8 + math.sin(f) * size / 8.0; d1 = 8 - math.sin(f) * size / 8.0
    d2 = 8 + math.cos(f) * size / 8.0; d3 = 8 - math.cos(f) * size / 8.0
    d4 = 64 + rnd.randrange(3) - 2; d5 = 64 + rnd.randrange(3) - 2
    placed = set()
    rng = range(size + 1) if cofh else range(size)
    for i in rng:
        fr = i / size
        d6 = d0 + (d1 - d0) * fr; d7 = d4 + (d5 - d4) * fr; d8 = d2 + (d3 - d2) * fr
        d9 = rnd.random() * size / 16.0
        d10 = (math.sin(math.pi * fr) + 1.0) * d9 + 1.0
        d11 = d10
        for x in range(math.floor(d6 - d10 / 2), math.floor(d6 + d10 / 2) + 1):
            a = (x + 0.5 - d6) / (d10 / 2)
            if a * a >= 1: continue
            for y in range(math.floor(d7 - d11 / 2), math.floor(d7 + d11 / 2) + 1):
                b = (y + 0.5 - d7) / (d11 / 2)
                if a * a + b * b >= 1: continue
                for z in range(math.floor(d8 - d10 / 2), math.floor(d8 + d10 / 2) + 1):
                    c = (z + 0.5 - d8) / (d10 / 2)
                    if a * a + b * b + c * c < 1:
                        placed.add((x, y, z))
    return len(placed)
rnd = random.Random(1)
N = 3000
for s in [3,4,5,6,7,8,9,10,12,14,16,17,18,20,22,24,26,28,30,32,34,36,37,40]:
    v = sum(vein(s, rnd, False) for _ in range(N)) / N
    c = sum(vein(s, rnd, True) for _ in range(N)) / N
    print("%3d  vanilla %6.1f   cofh %6.1f" % (s, v, c))
