# -*- coding: utf-8 -*-
"""Рисунки к заданию 1-2."""
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


CROP = (20, 95, 1168, 1100)
N1, N2, N3 = (405, 334), (1076, 334), (405, 1005)


def plain():
    fig, ax = overlay_canvas("p1_v22.png", CROP)
    save(fig, OUT + "fig12_scheme.png")


def currents():
    fig, ax = overlay_canvas("p1_v22.png", CROP)
    node_tag(ax, N1, "1", off=(-38, -34)); node_tag(ax, N2, "2", off=(40, -30))
    node_tag(ax, N3, "3", off=(-38, 36))
    # ветвь V2-R6: слева направо
    arrow(ax, (645, 167), (805, 167)); label(ax, 725, 128, r"$I_{R6}$", color=ANN)
    # R4: слева направо
    arrow(ax, (470, 334), (625, 334)); label(ax, 548, 298, r"$I_{R4}$", color=ANN)
    # R1: сверху вниз
    arrow(ax, (405, 395), (405, 560)); label(ax, 452, 480, r"$I_{R1}$", color=ANN)
    # R3: сверху вниз
    arrow(ax, (70, 395), (70, 560)); label(ax, 121, 480, r"$I_{R3}$", color=ANN)
    # R2-I1: снизу вверх
    arrow(ax, (237, 745), (237, 600)); label(ax, 291, 672, r"$I_{R2}$", color=ANN)
    # V1-R5: ток идёт вниз через V1 и влево по R5
    arrow(ax, (660, 1005), (500, 1005)); label(ax, 580, 968, r"$I_{R5}$", color=ANN)
    arrow(ax, (1076, 750), (1076, 905)); label(ax, 1120, 830, r"$I_{R5}$", color=ANN)
    # полярность напряжения источника тока
    label(ax, 280, 800, "+", color=ANN2, fs=FS + 4); label(ax, 280, 884, "−", color=ANN2, fs=FS + 4)
    label(ax, 352, 842, r"$U_{I1}$", color=ANN2, ha="center")
    save(fig, OUT + "fig12_currents.png")


def contours():
    fig, ax = overlay_canvas("p1_v22.png", CROP)
    c1, c2, c3, c4 = "#1b6ca8", "#2e8b57", "#c0561a", "#8e2f9c"
    kw = dict(lw=2.5)
    contour(ax, [(450, 262), (1030, 262), (1030, 300), (450, 300)], c1, ms=18, **kw)
    label(ax, 740, 234, r"$I_{K1}$", color=c1, fs=FS - 2)
    contour(ax, [(525, 430), (1010, 430), (1010, 950), (525, 950)], c2, **kw)
    label(ax, 768, 690, r"$I_{K2}$", color=c2)
    contour(ax, [(97, 372), (374, 372), (374, 975), (97, 975)], c3,
            fracs=[0.78, 0.25, 0.25, 0.25], **kw)
    label(ax, 312, 735, r"$I_{K3}$", color=c3)
    # контур K4 идёт против часовой стрелки (по направлению тока I1)
    contour(ax, [(158, 425), (158, 940), (212, 940), (212, 425)], c4,
            fracs=[0.3, 0.5, 0.5, 0.5], ms=20, **kw)
    label(ax, 186, 398, r"$I_{K4}$", color=c4, fs=FS - 4)
    node_tag(ax, N1, "1", off=(-38, -34)); node_tag(ax, N2, "2", off=(40, -30))
    node_tag(ax, N3, "3", off=(-38, 36))
    save(fig, OUT + "fig12_contours.png")


def spice_nodes():
    fig, ax = overlay_canvas("p1_v22.png", CROP)
    lab = dict(color=ANN, fs=FS + 4)
    label(ax, 372, 300, "n1", **lab); label(ax, 1126, 300, "n2", **lab)
    label(ax, 372, 1042, "0", **lab); ground(ax, N3, 22)
    label(ax, 643, 132, "e2", **lab); label(ax, 1128, 880, "d", **lab)
    label(ax, 190, 620, "f", **lab)
    save(fig, OUT + "fig12_spice.png")


def norton():
    """Преобразованная схема для метода узловых потенциалов."""
    w, h = 1140, 760
    fig, ax = new_canvas(w, h)
    gy = 640      # нижняя шина (узел 3)
    ry = 330      # шина узла 1 слева
    # нижняя шина
    wire(ax, [(70, gy), (990, gy)])
    # левая шина узла 1
    wire(ax, [(70, ry), (440, ry)])
    # вертикальные ветви к узлу 3: R3, I1, R1
    resistor(ax, (70, ry), (70, gy)); label(ax, 118, (ry + gy) / 2, "R3", ha="left")
    isource(ax, (215, gy), (215, ry), forward=True); label(ax, 262, (ry + gy) / 2, "I1", ha="left")
    resistor(ax, (360, ry), (360, gy)); label(ax, 408, (ry + gy) / 2, "R1", ha="left")
    for x in (215, 360):
        dot(ax, (x, ry)); dot(ax, (x, gy))
    dot(ax, (70, ry)); dot(ax, (70, gy))
    # шина узла 1 вверх: x = 440
    wire(ax, [(440, ry), (440, 80)])
    # три ветви между узлами 1 и 2: I2 (вверху), R6, R4
    y_i2, y_r6, y_r4 = 80, 210, 330
    x1, x2 = 440, 760
    isource(ax, (x1, y_i2), (x2, y_i2), forward=True); label(ax, 600, y_i2 - 52, "I2")
    resistor(ax, (x1, y_r6), (x2, y_r6)); label(ax, 600, y_r6 - 48, "R6")
    resistor(ax, (x1, y_r4), (x2, y_r4)); label(ax, 600, y_r4 + 50, "R4")
    for y in (y_r6, y_r4):
        dot(ax, (x1, y)); dot(ax, (x2, y))
    # шина узла 2
    wire(ax, [(x2, y_i2), (x2, ry)])
    wire(ax, [(x2, ry), (990, ry)])
    # ветви I3 и R5 между узлом 2 и узлом 3
    isource(ax, (855, ry), (855, gy), forward=True); label(ax, 903, (ry + gy) / 2, "I3", ha="left")
    resistor(ax, (990, ry), (990, gy)); label(ax, 1036, (ry + gy) / 2, "R5", ha="left")
    dot(ax, (855, ry)); dot(ax, (855, gy)); dot(ax, (990, ry)); dot(ax, (990, gy))
    # узлы
    dot(ax, (x1, ry), r=10); dot(ax, (x2, ry), r=10); dot(ax, (440, gy), r=10)
    node_tag(ax, (x1, ry), "1", off=(-34, 30)); node_tag(ax, (x2, ry), "2", off=(-32, 30))
    node_tag(ax, (440, gy), "3", off=(40, 32)); ground(ax, (440, gy), 22)
    save(fig, OUT + "fig12_norton.png")


if __name__ == "__main__":
    plain(); currents(); contours(); spice_nodes(); norton()
