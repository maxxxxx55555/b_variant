# -*- coding: utf-8 -*-
"""Рисунки к заданию 1-2 (вариант 7)."""
import numpy as np
from PIL import Image
from sch import *

W = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/"
OUT = W + "figs/"


def overlay_canvas(name, crop):
    im = Image.open(W + name).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    bg.alpha_composite(im)
    arr = np.array(bg.convert("RGB"))
    x0, y0, x1, y1 = crop
    fig, ax = new_canvas(x1 - x0, y1 - y0)
    ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
    ax.imshow(arr, extent=(0, arr.shape[1], arr.shape[0], 0), zorder=0, interpolation="lanczos")
    return fig, ax


IMG = "p1_v7.png"
CROP = (20, 105, 1166, 1085)
N1, N2, N3 = (422, 343), (1093, 343), (422, 1014)


def plain():
    fig, ax = overlay_canvas(IMG, CROP)
    save(fig, OUT + "fig12_scheme.png")


def currents():
    fig, ax = overlay_canvas(IMG, CROP)
    node_tag(ax, N1, "1", off=(-38, -34)); node_tag(ax, N2, "2", off=(40, -30))
    node_tag(ax, N3, "3", off=(-38, 36))
    # ветвь V2-R6: слева направо
    arrow(ax, (665, 175), (835, 175)); label(ax, 750, 136, r"$I_{R6}$", color=ANN)
    # R4: слева направо
    arrow(ax, (490, 343), (650, 343)); label(ax, 570, 305, r"$I_{R4}$", color=ANN)
    # R1: сверху вниз
    arrow(ax, (422, 420), (422, 585)); label(ax, 472, 500, r"$I_{R1}$", color=ANN)
    # ветвь R3-V1: сверху вниз
    arrow(ax, (86, 590), (86, 745)); label(ax, 140, 668, r"$I_{R3}$", color=ANN)
    # ветвь R2-I1: снизу вверх
    arrow(ax, (254, 745), (254, 600)); label(ax, 308, 672, r"$I_{R2}$", color=ANN)
    # R5: сверху вниз
    arrow(ax, (1093, 750), (1093, 910)); label(ax, 1137, 830, r"$I_{R5}$", color=ANN)
    # полярность напряжения источника тока
    label(ax, 292, 790, "+", color=ANN2, fs=FS + 4); label(ax, 292, 904, "−", color=ANN2, fs=FS + 4)
    label(ax, 352, 790, r"$U_{I1}$", color=ANN2, ha="center")
    save(fig, OUT + "fig12_currents.png")


def contour_gaps(ax, pts, color, gaps=(), fracs=None, lw=2.5, ms=24, ls=(0, (6, 4))):
    """Контур с разрывами линии в прямоугольниках gaps (x0, y0, x1, y1) - под подписями схемы."""
    pts = np.asarray(pts, float)
    closed = np.vstack([pts, pts[:1]])
    for i in range(len(pts)):
        a, b = closed[i], closed[i + 1]
        tt = np.linspace(0, 1, 600)
        xy = a[None, :] + (b - a)[None, :] * tt[:, None]
        ok = np.ones(len(tt), bool)
        for (x0, y0, x1, y1) in gaps:
            ok &= ~((xy[:, 0] > x0) & (xy[:, 0] < x1) & (xy[:, 1] > y0) & (xy[:, 1] < y1))
        run = []
        for k in range(len(tt) + 1):
            if k < len(tt) and ok[k]:
                run.append(xy[k])
            else:
                if len(run) > 1:
                    r = np.array(run)
                    ax.plot(r[:, 0], r[:, 1], color=color, lw=lw, ls=ls, zorder=7)
                run = []
    fracs = fracs or [0.5] * len(pts)
    for i in range(len(pts)):
        a, b = closed[i], closed[i + 1]
        m = a + (b - a) * fracs[i]
        d = (b - a) / np.hypot(*(b - a))
        arrow(ax, m - d * 12, m + d * 12, color=color, lw=lw, ms=ms, z=8)


def contours():
    fig, ax = overlay_canvas(IMG, CROP)
    c1, c2, c3, c4 = "#1b6ca8", "#2e8b57", "#c0561a", "#8e2f9c"
    kw = dict(lw=2.5)
    contour(ax, [(470, 272), (1040, 272), (1040, 308), (470, 308)], c1, ms=18, **kw)
    label(ax, 760, 246, r"$I_{K1}$", color=c1, fs=FS - 2)
    contour(ax, [(545, 425), (1025, 425), (1025, 955), (545, 955)], c2, **kw)
    label(ax, 785, 690, r"$I_{K2}$", color=c2)
    # контур K3 проходит рядом с ветвью R3-V1: линия прерывается под подписью R3
    contour_gaps(ax, [(133, 392), (392, 392), (392, 975), (133, 975)], c3,
                 gaps=[(120, 488, 166, 530)], fracs=[0.78, 0.25, 0.25, 0.62], **kw)
    label(ax, 335, 745, r"$I_{K3}$", color=c3)
    # контур K4 идёт против часовой стрелки (по направлению тока I1)
    contour_gaps(ax, [(192, 445), (192, 935), (226, 935), (226, 445)], c4,
                 gaps=[(212, 800, 300, 890)], fracs=[0.3, 0.5, 0.5, 0.4], ms=20, **kw)
    label(ax, 208, 418, r"$I_{K4}$", color=c4, fs=FS - 4)
    node_tag(ax, N1, "1", off=(-38, -34)); node_tag(ax, N2, "2", off=(40, -30))
    node_tag(ax, N3, "3", off=(-38, 36))
    save(fig, OUT + "fig12_contours.png")


def spice_nodes():
    fig, ax = overlay_canvas(IMG, CROP)
    lab = dict(color=ANN, fs=FS + 4)
    label(ax, 385, 308, "n1", **lab); label(ax, 1130, 308, "n2", **lab)
    label(ax, 385, 1050, "0", **lab); ground(ax, N3, 22)
    label(ax, 722, 138, "e2", **lab)
    label(ax, 122, 690, "g", **lab); label(ax, 296, 690, "f", **lab)
    save(fig, OUT + "fig12_spice.png")


def norton():
    """Преобразованная схема для метода узловых потенциалов."""
    w, h = 1240, 760
    fig, ax = new_canvas(w, h)
    gy = 640      # нижняя шина (узел 3)
    ry = 330      # шина узла 1
    xs = (70, 225, 380, 535)      # ветви между узлами 1 и 3: R3, I3, I1, R1
    x1, x2, xr = 650, 970, 1080
    wire(ax, [(70, gy), (xr, gy)])
    wire(ax, [(70, ry), (x1, ry)])
    resistor(ax, (xs[0], ry), (xs[0], gy)); label(ax, xs[0] + 48, (ry + gy) / 2, "R3", ha="left")
    isource(ax, (xs[1], ry), (xs[1], gy), forward=True); label(ax, xs[1] + 48, (ry + gy) / 2, "I3", ha="left")
    isource(ax, (xs[2], gy), (xs[2], ry), forward=True); label(ax, xs[2] + 48, (ry + gy) / 2, "I1", ha="left")
    resistor(ax, (xs[3], ry), (xs[3], gy)); label(ax, xs[3] + 48, (ry + gy) / 2, "R1", ha="left")
    for x in xs:
        dot(ax, (x, ry)); dot(ax, (x, gy))
    wire(ax, [(x1, ry), (x1, 80)])
    # три ветви между узлами 1 и 2: I2 (вверху), R6, R4
    y_i2, y_r6, y_r4 = 80, 210, 330
    isource(ax, (x1, y_i2), (x2, y_i2), forward=True); label(ax, (x1 + x2) / 2, y_i2 - 52, "I2")
    resistor(ax, (x1, y_r6), (x2, y_r6)); label(ax, (x1 + x2) / 2, y_r6 - 48, "R6")
    resistor(ax, (x1, y_r4), (x2, y_r4)); label(ax, (x1 + x2) / 2, y_r4 + 50, "R4")
    for y in (y_r6, y_r4):
        dot(ax, (x1, y)); dot(ax, (x2, y))
    # шина узла 2 и резистор R5 между узлами 2 и 3
    wire(ax, [(x2, y_i2), (x2, ry)])
    wire(ax, [(x2, ry), (xr, ry)])
    resistor(ax, (xr, ry), (xr, gy)); label(ax, xr + 46, (ry + gy) / 2, "R5", ha="left")
    dot(ax, (xr, ry)); dot(ax, (xr, gy))
    dot(ax, (x1, ry), r=10); dot(ax, (x2, ry), r=10); dot(ax, (x1, gy), r=10)
    node_tag(ax, (x1, ry), "1", off=(-34, 30)); node_tag(ax, (x2, ry), "2", off=(-32, 30))
    node_tag(ax, (x1, gy), "3", off=(-46, -34)); ground(ax, (x1, gy), 22)
    save(fig, OUT + "fig12_norton.png")


if __name__ == "__main__":
    plain(); currents(); contours(); spice_nodes(); norton()
