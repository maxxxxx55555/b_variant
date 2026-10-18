# -*- coding: utf-8 -*-
"""Рисунки к заданию 2-1."""
import numpy as np
from sch import *
from figs12 import overlay_canvas, W, OUT

CROP = (-45, 95, 1168, 1100)
N1, N2, N0 = (411, 330), (1093, 330), (411, 1012)


def plain():
    fig, ax = overlay_canvas("p21_v22.png", (20, 95, 1168, 1100))
    save(fig, OUT + "fig21_scheme.png")


def annotated():
    """Исходная схема: узлы, полярность u_C и направление тока контура после коммутации."""
    fig, ax = overlay_canvas("p21_v22.png", CROP)
    node_tag(ax, N1, "1", off=(-38, -34)); node_tag(ax, N2, "2", off=(42, -32))
    ground(ax, N0, 24); label(ax, 372, 1048, "0", color=ANN, fs=FS - 1)
    # полярность напряжения на конденсаторе
    label(ax, 24, 548, "+", color=ANN2, fs=FS + 4); label(ax, 24, 625, "−", color=ANN2, fs=FS + 4)
    label(ax, -22, 585, r"$u_C$", color=ANN2)
    # направление контурного тока после размыкания ключа (против часовой стрелки)
    arrow(ax, (700, 160), (590, 160)); label(ax, 645, 125, "i", color=ANN)
    arrow(ax, (70, 300), (70, 430)); label(ax, 108, 365, "i", color=ANN)
    arrow(ax, (700, 1012), (840, 1012)); label(ax, 770, 1048, "i", color=ANN)
    arrow(ax, (1093, 930), (1093, 800)); label(ax, 1132, 865, "i", color=ANN)
    label(ax, 922, 292, "ключ", color=ANN, fs=FS - 2)
    save(fig, OUT + "fig21_nodes.png")


def spice_nodes():
    """Исходная схема с именами узлов из описания для ngspice."""
    fig, ax = overlay_canvas("p21_v22.png", CROP)
    lab = dict(color=ANN, fs=FS + 3)
    label(ax, 372, 296, "n1", **lab); label(ax, 1135, 296, "n2", **lab)
    label(ax, 760, 296, "ns", **lab); label(ax, 580, 122, "n4", **lab)
    label(ax, 108, 122, "n3", **lab); label(ax, 200, 700, "nv", **lab)
    label(ax, 455, 700, "nx", **lab)
    ground(ax, N0, 24); label(ax, 372, 1048, "0", **lab)
    label(ax, 922, 292, "S1", **lab)
    save(fig, OUT + "fig21_spicenodes.png")


def before():
    """Докоммутационная схема (постоянный ток): C1 - разрыв, L1 - перемычка."""
    w, h = 960, 800
    fig, ax = new_canvas(w, h)
    gy = 700
    xc, x2, x1, xr3, xn2 = 60, 230, 380, 590, 790
    wire(ax, [(xc, gy), (xn2, gy)])
    n1 = (x1, 300)
    wire(ax, [(x2, 300), (x1, 300)])
    # ветвь R2 - V1
    resistor(ax, (x2, 300), (x2, 520)); label(ax, x2 + 48, 410, "R2", ha="left")
    vsource(ax, (x2, 520), (x2, 700), forward=True); label(ax, x2 + 48, 610, "V1", ha="left")
    # ветвь R1 - I1
    resistor(ax, n1, (x1, 520)); label(ax, x1 + 48, 410, "R1", ha="left")
    isource(ax, (x1, 700), (x1, 520), forward=True); label(ax, x1 + 48, 610, "I1", ha="left")
    # R3 и замкнутый ключ
    resistor(ax, n1, (xr3, 300)); label(ax, (x1 + xr3) / 2, 252, "R3")
    wire(ax, [(xr3, 300), (xn2, 300)])
    dot(ax, (xr3 + 45, 300), r=5); dot(ax, (xn2 - 45, 300), r=5)
    label(ax, (xr3 + xn2) / 2, 262, "ключ замкнут", fs=FS - 3)
    # R4
    resistor(ax, (xn2, 300), (xn2, 700)); label(ax, xn2 + 48, 500, "R4", ha="left")
    # верхняя ветвь: R5, L1 (перемычка), C1 (разрыв)
    wire(ax, [(xn2, 300), (xn2, 100), (xc, 100), (xc, 330)])
    resistor(ax, (xc + 90, 100), (xc + 410, 100)); label(ax, xc + 250, 62, "R5")
    wire(ax, [(xn2 - 250, 100), (xn2 - 90, 100)], lw=LW * 1.8)
    label(ax, xn2 - 170, 62, "L1 – перемычка", fs=FS - 3)
    wire(ax, [(xc, 420), (xc, 700)])
    dot(ax, (xc, 330), r=9); dot(ax, (xc, 420), r=9)
    arrow(ax, (xc - 46, 420), (xc - 46, 330), color=ANN2); label(ax, xc - 80, 375, r"$u_C$", color=ANN2)
    label(ax, xc + 22, 262, "C1 – разрыв", fs=FS - 3, ha="left")
    label(ax, xc + 60, 170, "i = 0", color=ANN, fs=FS - 2, ha="left")
    for p in [(x1, 700), (xn2, 700), (x2, 700), (xc, 700), (x1, 300), (xn2, 300)]:
        dot(ax, p)
    node_tag(ax, (x1, 300), "1", off=(-34, -30)); node_tag(ax, (xn2, 300), "2", off=(-38, 36))
    ground(ax, (x1, 700), 22); label(ax, x1 + 42, 745, "0", color=ANN, fs=FS - 1)
    ax.set_xlim(-110, w); ax.set_ylim(h, 0)
    save(fig, OUT + "fig21_before.png")


def after():
    """Эквивалентная схема свободного процесса: R6 = R4 + R5, L1, C1."""
    w, h = 820, 620
    fig, ax = new_canvas(w, h)
    x0, x1, y0, y1 = 150, 690, 110, 500
    wire(ax, [(x0, y0), (x1, y0)]); wire(ax, [(x0, y1), (x1, y1)])
    inductor(ax, (x0, y0), (x1, y0), t=0.5, half=54, side=-1); label(ax, (x0 + x1) / 2, y0 - 46, "L1")
    resistor(ax, (x1, y0), (x1, y1)); label(ax, x1 + 46, (y0 + y1) / 2, "R6", ha="left")
    capacitor(ax, (x0, y1), (x0, y0), t=0.5, gap=9, plate=26); label(ax, x0 - 56, (y0 + y1) / 2 + 52, "C1", ha="right")
    wire(ax, [(x0, y0), (x0, y1)], lw=0.0)
    # контурный ток против часовой стрелки: по C1 сверху вниз
    arrow(ax, (x0, 190), (x0, 250)); label(ax, x0 + 28, 220, "i", color=ANN, ha="left")
    arrow(ax, (x1, 400), (x1, 340))
    arrow(ax, (610, y0), (530, y0)); arrow(ax, (300, y1), (400, y1))
    label(ax, x0 - 38, 258, "+", color=ANN2, fs=FS + 4); label(ax, x0 - 38, 332, "−", color=ANN2, fs=FS + 4)
    label(ax, x0 - 88, 295, r"$u_C$", color=ANN2)
    dot(ax, (x0, y0)); dot(ax, (x1, y0)); dot(ax, (x0, y1)); dot(ax, (x1, y1))
    save(fig, OUT + "fig21_after.png")


if __name__ == "__main__":
    plain(); annotated(); spice_nodes(); before(); after()
