# -*- coding: utf-8 -*-
"""Рисунки к заданию 2-2 (вариант 7)."""
import numpy as np
from sch import *
from figs12 import overlay_canvas, W, OUT

IMG = "p22_v7.png"
CROP = (20, 195, 1162, 985)
P1, P2, P3, P4 = (167, 267), (581, 267), (996, 267), (581, 681)


def ground_up(ax, p, size=24):
    """Знак «земля», обращённый вверх (базисный узел 2 расположен на верхней шине)."""
    x, y = p
    wire(ax, [(x, y), (x, y - 16)])
    for k, w in enumerate((size, size * 0.66, size * 0.33)):
        wire(ax, [(x - w, y - 16 - k * 9), (x + w, y - 16 - k * 9)])


def plain():
    fig, ax = overlay_canvas(IMG, CROP)
    save(fig, OUT + "fig22_scheme.png")


def annotated():
    fig, ax = overlay_canvas(IMG, CROP)
    node_tag(ax, P1, "1", off=(-36, -34)); node_tag(ax, P2, "2", off=(-36, -34))
    node_tag(ax, P3, "3", off=(36, -34)); node_tag(ax, P4, "4", off=(38, 36))
    d = r"$\dot{I}_{"
    # ветвь C3-L3: слева направо по нижней шине
    arrow(ax, (405, 785), (525, 785)); label(ax, 465, 826, d + "L3}$", color=ANN)
    # ветвь C2-R3: сверху вниз
    arrow(ax, (167, 545), (167, 640)); label(ax, 112, 592, d + "C2}$", color=ANN)
    # C1: слева направо
    arrow(ax, (415, 267), (540, 267)); label(ax, 478, 230, d + "C1}$", color=ANN)
    # ветвь L1-R1: сверху вниз
    arrow(ax, (581, 410), (581, 520)); label(ax, 642, 465, d + "L1}$", color=ANN)
    # источник V1: слева направо
    arrow(ax, (835, 267), (955, 267)); label(ax, 895, 230, d + "V1}$", color=ANN)
    # ветвь V2-L2: справа налево по нижней шине
    arrow(ax, (955, 681), (860, 681)); label(ax, 908, 644, d + "L2}$", color=ANN)
    # ветвь R2-I1: снизу вверх
    arrow(ax, (1099, 450), (1099, 335)); label(ax, 1046, 392, d + "R2}$", color=ANN)
    # напряжение на L3: плюс на выводе, куда входит ток
    label(ax, 286, 757, "+", color=ANN2, fs=FS + 4); label(ax, 360, 757, "−", color=ANN2, fs=FS + 4)
    label(ax, 318, 733, r"$\dot{U}_{L3}$", color=ANN2)
    save(fig, OUT + "fig22_currents.png")


def complex_scheme():
    """Схема замещения: каждая ветвь заменена комплексным сопротивлением Z1...Z6."""
    fig, ax = overlay_blank(CROP)
    d = r"$\underline{Z}_"
    # Z1 (C3, L3): левая вертикаль и нижняя шина
    resistor(ax, (63, 267), (63, 785)); label(ax, 109, 526, d + "1$", ha="left")
    wire(ax, [(63, 267), (167, 267)]); wire(ax, [(63, 785), (581, 785), (581, 681)])
    # Z2 (C2, R3)
    resistor(ax, (167, 267), (167, 681)); label(ax, 213, 474, d + "2$", ha="left")
    wire(ax, [(167, 681), (581, 681)])
    # Z3 (C1)
    resistor(ax, (167, 267), (581, 267)); label(ax, 374, 318, d + "3$")
    # V1
    vsource(ax, (581, 267), (996, 267), forward=True); label(ax, 788, 322, r"$\dot{V}_1$")
    # Z4 (L1, R1)
    resistor(ax, (581, 267), (581, 681)); label(ax, 627, 474, d + "4$", ha="left")
    # V2 и Z5 (L2)
    vsource(ax, (996, 267), (996, 681), forward=True); label(ax, 1042, 474, r"$\dot{V}_2$", ha="left")
    resistor(ax, (996, 681), (581, 681)); label(ax, 788, 722, d + "5$")
    # ветвь I1, Z6 (R2)
    wire(ax, [(581, 681), (581, 888)])
    isource(ax, (581, 888), (1099, 888), forward=True); label(ax, 840, 944, r"$\dot{I}_1$")
    resistor(ax, (1099, 888), (1099, 267)); label(ax, 1053, 577, d + "6$", ha="right")
    wire(ax, [(1099, 267), (996, 267)])
    for p in (P1, P2, P3, P4):
        dot(ax, p)
    node_tag(ax, P1, "1", off=(-36, -34)); node_tag(ax, P2, "2", off=(-36, 36))
    node_tag(ax, P3, "3", off=(36, -34)); node_tag(ax, P4, "4", off=(38, 36))
    ground_up(ax, P2, 24)
    save(fig, OUT + "fig22_complex.png")


def overlay_blank(crop):
    x0, y0, x1, y1 = crop
    fig, ax = new_canvas(x1 - x0, y1 - y0)
    ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
    return fig, ax


def spice_nodes():
    fig, ax = overlay_canvas(IMG, CROP)
    lab = dict(color=ANN, fs=FS - 2)
    label(ax, 128, 232, "n1", **lab); label(ax, 1036, 232, "n3", **lab)
    label(ax, 626, 716, "n4", **lab)
    ground_up(ax, P2, 22); label(ax, 618, 226, "0", **lab)
    label(ax, 268, 752, "a2", **lab)
    # амперметры: источники нулевого напряжения VA1 ... VA7
    for (x, y, nm, dx, dy) in [(63, 380, "VA1", 52, 0), (167, 380, "VA2", 52, 0), (275, 267, "VA3", 0, -36),
                               (581, 318, "VA4", 52, 0), (996, 590, "VA5", 52, 0), (690, 267, "VA6", 0, -36),
                               (1099, 440, "VA7", -52, 0)]:
        ax.add_patch(Circle((x, y), 15, fc="white", ec=ANN, lw=2.2, zorder=9))
        ax.text(x, y, "A", fontsize=FS - 7, color=ANN, ha="center", va="center", zorder=10)
        label(ax, x + dx, y + dy, nm, **lab)
    save(fig, OUT + "fig22_spice.png")


if __name__ == "__main__":
    plain(); annotated(); complex_scheme(); spice_nodes()
