# -*- coding: utf-8 -*-
"""Мини-библиотека для рисования электрических схем в стиле исходных схем задания
(прямоугольные резисторы, круглые источники со стрелкой, точки в узлах).
Координаты - в пикселях (ось y направлена вниз, как у изображений)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "Liberation Serif",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Serif",
    "mathtext.it": "Liberation Serif:italic",
    "mathtext.bf": "Liberation Serif:bold",
    "mathtext.sf": "Liberation Serif",
    "mathtext.default": "it",
    "axes.unicode_minus": True,
})

LW = 2.9          # толщина линий схемы, pt
BLACK = "#000000"
ANN = "#0b3d91"   # цвет пояснительных стрелок и подписей
ANN2 = "#b3300f"
FS = 21           # размер подписей, pt (при масштабе 1 пиксель = 0,72 pt)


def new_canvas(w, h, dpi=100):
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _vec(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p
    L = np.hypot(*d)
    e = d / L
    n = np.array([-e[1], e[0]])
    return p, q, e, n, L


def wire(ax, pts, lw=LW, color=BLACK, ls="-", z=2):
    pts = np.asarray(pts, float)
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, ls=ls, solid_capstyle="round",
            solid_joinstyle="round", zorder=z)


def dot(ax, p, r=8.5, color=BLACK, z=5):
    ax.add_patch(Circle(p, r, fc=color, ec=color, zorder=z))


def label(ax, x, y, s, fs=FS, color=BLACK, ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, zorder=10, **kw)


def resistor(ax, p, q, t=0.5, half=34, w=17):
    p, q, e, n, L = _vec(p, q)
    c = p + (q - p) * t
    a, b = c - e * half, c + e * half
    wire(ax, [p, a]); wire(ax, [b, q])
    box = np.array([a + n * w, b + n * w, b - n * w, a - n * w])
    ax.add_patch(Polygon(box, closed=True, fc="white", ec=BLACK, lw=LW, zorder=3,
                         joinstyle="miter"))
    return c


def capacitor(ax, p, q, t=0.5, gap=8, plate=20):
    p, q, e, n, L = _vec(p, q)
    c = p + (q - p) * t
    a, b = c - e * gap, c + e * gap
    wire(ax, [p, a]); wire(ax, [b, q])
    wire(ax, [a + n * plate, a - n * plate]); wire(ax, [b + n * plate, b - n * plate])
    return c


def inductor(ax, p, q, t=0.5, half=36, side=1):
    p, q, e, n, L = _vec(p, q)
    c = p + (q - p) * t
    a, b = c - e * half, c + e * half
    wire(ax, [p, a]); wire(ax, [b, q])
    r = half / 3.0
    th = np.linspace(np.pi, 0, 40)
    pts = []
    for k in range(3):
        ctr = a + e * (r * (2 * k + 1))
        for u in th:
            pts.append(ctr + e * (r * np.cos(u)) + n * side * (r * np.sin(u)) * 0.9)
    wire(ax, np.array(pts))
    return c


def vsource(ax, p, q, forward=True, t=0.5, R=34):
    """Источник ЭДС: стрелка внутри круга направлена от «-» к «+»."""
    p, q, e, n, L = _vec(p, q)
    c = p + (q - p) * t
    wire(ax, [p, c - e * R]); wire(ax, [c + e * R, q])
    ax.add_patch(Circle(c, R, fc="white", ec=BLACK, lw=LW, zorder=3))
    d = e if forward else -e
    tip = c + d * 24
    base = c - d * 8
    tri = np.array([tip, base + n * 13, base - n * 13])
    ax.add_patch(Polygon(tri, closed=True, fc=BLACK, ec=BLACK, zorder=4))
    return c


def isource(ax, p, q, forward=True, t=0.5, R=34):
    p, q, e, n, L = _vec(p, q)
    c = p + (q - p) * t
    wire(ax, [p, c - e * R]); wire(ax, [c + e * R, q])
    ax.add_patch(Circle(c, R, fc="white", ec=BLACK, lw=LW, zorder=3))
    d = e if forward else -e
    for s in (-3, 11):
        tip = c + d * (s + 4)
        l1 = c + d * (s - 8) + n * 12
        l2 = c + d * (s - 8) - n * 12
        wire(ax, [l1, tip, l2], lw=LW * 0.85, z=4)
    return c


def switch_open(ax, p, q, t=0.5, half=36, up=1):
    p, q, e, n, L = _vec(p, q)
    c = p + (q - p) * t
    a, b = c - e * half, c + e * half
    wire(ax, [p, a]); wire(ax, [b, q])
    wire(ax, [a, b - e * 6 + n * up * 20])
    dot(ax, a, r=5); dot(ax, b, r=5)
    return c


def ground(ax, p, size=26):
    x, y = p
    wire(ax, [(x, y), (x, y + 14)])
    for k, w in enumerate((size, size * 0.66, size * 0.33)):
        wire(ax, [(x - w, y + 14 + k * 9), (x + w, y + 14 + k * 9)])


def arrow(ax, p, q, color=ANN, lw=2.6, ms=22, ls="-", z=8, style="-|>", shrink=0):
    a = FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=color,
                        lw=lw, ls=ls, zorder=z, shrinkA=shrink, shrinkB=shrink,
                        joinstyle="miter", capstyle="butt")
    ax.add_patch(a)
    return a


def node_tag(ax, p, text, off=(0, 0), color=ANN, r=19, fs=FS - 1):
    """Номер узла в кружке рядом с точкой p."""
    x, y = p[0] + off[0], p[1] + off[1]
    ax.add_patch(Circle((x, y), r, fc="white", ec=color, lw=2.2, zorder=9))
    ax.text(x, y, text, fontsize=fs, color=color, ha="center", va="center", zorder=10)


def contour(ax, pts, color, lw=3.0, ls=(0, (6, 4)), fracs=None, ms=24):
    """Замкнутый контур по точкам с небольшими стрелками направления.
    fracs - положение стрелки на каждой стороне (доля длины стороны)."""
    pts = np.asarray(pts, float)
    closed = np.vstack([pts, pts[:1]])
    ax.plot(closed[:, 0], closed[:, 1], color=color, lw=lw, ls=ls, zorder=7)
    fracs = fracs or [0.5] * len(pts)
    for i in range(len(pts)):
        a, b = closed[i], closed[i + 1]
        m = a + (b - a) * fracs[i]
        d = (b - a) / np.hypot(*(b - a))
        arrow(ax, m - d * 12, m + d * 12, color=color, lw=lw, ms=ms, z=8)


def save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
