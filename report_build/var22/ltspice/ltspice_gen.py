# -*- coding: utf-8 -*-
"""Генератор схем LTspice (.asc) и netlist (.cir) для ДЗ1, вариант 22.

Схемы собираются только из вертикальных компонентов (повороты R0 и R180), поэтому геометрия
не зависит от направления поворота R90/R270. Выводы стандартных символов LTspice
(res, cap, ind, voltage, current) заданы относительно начала символа."""
import os

# координаты выводов относительно точки вставки символа при повороте R0
SYM = {
    "res": ([(16, 16), (16, 96)], "R"),
    "ind": ([(16, 16), (16, 96)], "L"),
    "cap": ([(16, 0), (16, 64)], "C"),
    "voltage": ([(0, 16), (0, 96)], "V"),    # первый вывод «+»
    "current": ([(0, 0), (0, 80)], "I"),     # ток течёт от первого вывода ко второму
}


def rot(p, r):
    return p if r == "R0" else (-p[0], -p[1])


class Sch:
    def __init__(self, w=1200, h=1000):
        self.w, self.h = w, h
        self.wires, self.flags, self.comps, self.texts = [], [], [], []

    # вертикальный компонент: (x, ytop) - верхний вывод; возвращает координаты (верхний, нижний) выводов
    def comp(self, sym, name, value, x, ytop, r="R0", value2=None, label=True):
        pins = [rot(p, r) for p in SYM[sym][0]]
        up = min(pins, key=lambda p: p[1])
        ox, oy = x - up[0], ytop - up[1]
        absp = [(ox + p[0], oy + p[1]) for p in pins]
        self.comps.append(dict(sym=sym, name=name, value=value, value2=value2, pos=(ox, oy), rot=r,
                               pins=absp, label=label))
        top = min(absp, key=lambda p: p[1])
        bot = max(absp, key=lambda p: p[1])
        return top, bot

    def wire(self, x1, y1, x2, y2):
        if (x1, y1) != (x2, y2):
            self.wires.append((x1, y1, x2, y2))

    def flag(self, x, y, name):
        self.flags.append((x, y, name))

    def text(self, x, y, s, directive=True):
        self.texts.append((x, y, ("!" if directive else ";") + s))

    # ---- запись .asc
    def asc(self):
        pts = self._special_points()
        out = ["Version 4", f"SHEET 1 {self.w} {self.h}"]
        for (x1, y1, x2, y2) in self._split_wires(pts):
            out.append(f"WIRE {x1} {y1} {x2} {y2}")
        for (x, y, n) in self.flags:
            out.append(f"FLAG {x} {y} {n}")
        for c in self.comps:
            out.append(f"SYMBOL {c['sym']} {c['pos'][0]} {c['pos'][1]} {c['rot']}")
            out.append(f"SYMATTR InstName {c['name']}")
            out.append(f"SYMATTR Value {c['value']}")
            if c["value2"]:
                out.append(f"SYMATTR Value2 {c['value2']}")
        for (x, y, s) in self.texts:
            out.append(f"TEXT {x} {y} Left 2 {s}")
        return "\n".join(out) + "\n"

    def _special_points(self):
        pts = set()
        for c in self.comps:
            pts.update(c["pins"])
        for (x, y, n) in self.flags:
            pts.add((x, y))
        for (x1, y1, x2, y2) in self.wires:
            pts.add((x1, y1)); pts.add((x2, y2))
        return pts

    def _split_wires(self, pts):
        res = []
        for (x1, y1, x2, y2) in self.wires:
            cut = [(x1, y1), (x2, y2)]
            for (px, py) in pts:
                if (px, py) in cut:
                    continue
                if x1 == x2 == px and min(y1, y2) < py < max(y1, y2):
                    cut.append((px, py))
                if y1 == y2 == py and min(x1, x2) < px < max(x1, x2):
                    cut.append((px, py))
            cut.sort(key=lambda p: (p[0], p[1]))
            for a, b in zip(cut[:-1], cut[1:]):
                res.append((a[0], a[1], b[0], b[1]))
        return res


# ------------------------------------------------------------------ нетлистер (для проверки)
def parse_asc(text):
    """Читает подмножество .asc (WIRE, FLAG, SYMBOL, SYMATTR, TEXT) и строит netlist, как это делает LTspice."""
    wires, flags, comps, texts = [], [], [], []
    cur = None
    for line in text.splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] == "WIRE":
            wires.append(tuple(map(int, t[1:5])))
        elif t[0] == "FLAG":
            flags.append((int(t[1]), int(t[2]), t[3]))
        elif t[0] == "SYMBOL":
            cur = dict(sym=t[1], pos=(int(t[2]), int(t[3])), rot=t[4])
            comps.append(cur)
        elif t[0] == "SYMATTR" and cur is not None:
            cur[t[1]] = line.split(None, 2)[2]
        elif t[0] == "TEXT":
            texts.append(line.split(None, 5)[5] if len(line.split(None, 5)) > 5 else "")
    # объединение точек
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        parent[find(a)] = find(b)

    for (x1, y1, x2, y2) in wires:
        union((x1, y1), (x2, y2))
    # конец провода на внутренней точке другого провода соединяет их (проверка пересечений)
    for (x1, y1, x2, y2) in wires:
        for (a1, b1, a2, b2) in wires:
            if (a1, b1, a2, b2) == (x1, y1, x2, y2):
                continue
            for (px, py) in ((a1, b1), (a2, b2)):
                if x1 == x2 == px and min(y1, y2) < py < max(y1, y2):
                    raise ValueError(f"конец провода внутри другого провода: {(px, py)}")
                if y1 == y2 == py and min(x1, x2) < px < max(x1, x2):
                    raise ValueError(f"конец провода внутри другого провода: {(px, py)}")
    pins = []
    for c in comps:
        p = [rot(q, c["rot"]) for q in SYM[c["sym"]][0]]
        c["pins"] = [(c["pos"][0] + q[0], c["pos"][1] + q[1]) for q in p]
        pins.extend(c["pins"])
        for q in c["pins"]:
            find(q)
    names = {}
    for (x, y, n) in flags:
        if (x, y) not in parent:
            raise ValueError(f"метка {n} не лежит на проводе или выводе: {(x, y)}")
        root = find((x, y))
        if root in names and names[root] != n:
            raise ValueError(f"две метки на одной цепи: {names[root]}, {n}")
        names[root] = n
    # провода не должны пересекать выводы внутри
    for q in pins:
        for (x1, y1, x2, y2) in wires:
            if x1 == x2 == q[0] and min(y1, y2) < q[1] < max(y1, y2):
                raise ValueError(f"вывод внутри провода: {q}")
            if y1 == y2 == q[1] and min(x1, x2) < q[0] < max(x1, x2):
                raise ValueError(f"вывод внутри провода: {q}")
    # имена цепей
    net, k = {}, 0
    for c in comps:
        for q in c["pins"]:
            r = find(q)
            if r not in net:
                if r in names:
                    net[r] = "0" if names[r] == "0" else names[r]
                else:
                    k += 1
                    net[r] = f"N{k:03d}"
    lines = []
    for c in comps:
        n = [net[find(q)] for q in c["pins"]]
        lines.append((c["InstName"], n, c["Value"], c.get("Value2")))
    return lines, texts


def netlist_from_asc(text):
    comps, texts = parse_asc(text)
    out = []
    for name, n, val, val2 in comps:
        out.append(f"{name} {n[0]} {n[1]} {val}" + (f" {val2}" if val2 else ""))
    return out, texts
