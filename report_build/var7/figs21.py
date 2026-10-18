# -*- coding: utf-8 -*-
"""Рисунки к заданию 2-1 (вариант 7)."""
import numpy as np
from sch import *
from figs12 import overlay_canvas, W, OUT

IMG = "p21_v7.png"
CROP = (10, 0, 1189, 1155)
N1, N2, N0 = (283, 279), (1106, 279), (283, 1103)


def plain():
    fig, ax = overlay_canvas(IMG, CROP)
    save(fig, OUT + "fig21_scheme.png")


def annotated():
    """Исходная схема: узлы, полярность u_C, положительное направление i_L."""
    fig, ax = overlay_canvas(IMG, CROP)
    node_tag(ax, N1, "1", off=(-38, -34)); node_tag(ax, N2, "2", off=(42, -32))
    ground(ax, N0, 24); label(ax, 236, 1138, "0", color=ANN, fs=FS - 1)
    # полярность напряжения на конденсаторе: плюс на обкладке, к которой подключён R5
    label(ax, 461, 30, "−", color=ANN2, fs=FS + 4); label(ax, 516, 30, "+", color=ANN2, fs=FS + 4)
    label(ax, 584, 33, r"$u_C$", color=ANN2)
    # положительное направление тока индуктивности (по стрелке источника тока I1)
    arrow(ax, (77, 885), (77, 780)); label(ax, 128, 832, r"$i_L$", color=ANN)
    label(ax, 695, 1050, "ключ", color=ANN, fs=FS - 2)
    save(fig, OUT + "fig21_nodes.png")


def spice_nodes():
    """Исходная схема с именами узлов из описания для ngspice."""
    fig, ax = overlay_canvas(IMG, CROP)
    lab = dict(color=ANN, fs=FS + 1)
    label(ax, 240, 242, "n1", **lab); label(ax, 1152, 242, "n2", **lab)
    ground(ax, N0, 24); label(ax, 236, 1138, "0", **lab)
    label(ax, 690, 30, "n3", **lab); label(ax, 124, 832, "n4", **lab)
    label(ax, 124, 560, "n5", **lab); label(ax, 700, 238, "n6", **lab)
    label(ax, 905, 1062, "ns", **lab); label(ax, 695, 1050, "S1", **lab)
    save(fig, OUT + "fig21_spicenodes.png")


# ------------------------------------------------------------------ эквивалентные схемы
XL, XM, XR = 100, 340, 960          # левая ветвь, узел 1 (R1), правая ветвь (R4)
YT, YM, YB = 95, 290, 700           # верхняя ветвь, средняя линия, нижний провод


def draw(c1, l1, v1, i1, sw, name, notes):
    w, h = 1090, 800
    fig, ax = new_canvas(w, h)
    xc = 520                      # положение C1 и V1
    xr5 = 760                     # положение R5 и R3
    # --- верхняя ветвь
    wire(ax, [(XM, YM), (XM, YT), (xc - 60, YT)])
    wire(ax, [(xc + 60, YT), (XR, YT), (XR, YM)])
    if c1 == "cap":
        capacitor(ax, (xc - 60, YT), (xc + 60, YT), t=0.5, gap=9, plate=26)
        label(ax, xc, YT - 48, "C1")
    else:
        wire(ax, [(xc - 60, YT), (xc - 18, YT)]); wire(ax, [(xc + 18, YT), (xc + 60, YT)])
        dot(ax, (xc - 18, YT), r=7); dot(ax, (xc + 18, YT), r=7)
        label(ax, xc, YT - 48, "C1 – разрыв", fs=FS - 3)
        label(ax, xc - 62, YT + 40, "−", color=ANN2, fs=FS + 4)
        label(ax, xc + 62, YT + 40, "+", color=ANN2, fs=FS + 4)
        label(ax, xc, YT + 44, r"$u_C$", color=ANN2)
    resistor(ax, (xc + 60, YT), (XR - 60, YT)); label(ax, xr5 + 15, YT - 46, "R5")
    # --- средняя ветвь: V1 и R3
    wire(ax, [(XL, YM), (XM, YM)])
    if v1 == "src":
        vsource(ax, (XM, YM), (xc + 60, YM), forward=True, t=0.5)
        label(ax, (XM + xc + 60) / 2, YM + 52, "V1")
    else:
        wire(ax, [(XM, YM), (xc + 60, YM)], lw=LW * 1.8)
        label(ax, (XM + xc + 60) / 2, YM + 46, "V1 – перемычка", fs=FS - 3)
    resistor(ax, (xc + 60, YM), (XR, YM)); label(ax, xr5 + 15, YM + 46, "R3")
    # --- левая ветвь: R2, L1, I1
    wire(ax, [(XL, YM), (XL, YB), (XM, YB)])
    resistor(ax, (XL, YM), (XL, 440)); label(ax, XL + 48, 365, "R2", ha="left")
    if l1 == "coil":
        inductor(ax, (XL, 440), (XL, 540), t=0.5, half=40, side=1); label(ax, XL + 48, 490, "L1", ha="left")
    else:
        wire(ax, [(XL, 440), (XL, 540)], lw=LW * 1.8)
        label(ax, XL + 48, 490, "L1 –\nперемычка", fs=FS - 3, ha="left", multialignment="left")
    if i1 == "src":
        isource(ax, (XL, YB), (XL, 540), forward=True, t=0.5); label(ax, XL + 52, 625, "I1", ha="left")
    else:
        wire(ax, [(XL, 540), (XL, 585)]); wire(ax, [(XL, 650), (XL, YB)])
        dot(ax, (XL, 585), r=7); dot(ax, (XL, 650), r=7)
        label(ax, XL + 28, 618, "I1 – обрыв", fs=FS - 3, ha="left")
    # --- R1
    resistor(ax, (XM, YM), (XM, YB)); label(ax, XM + 48, 495, "R1", ha="left")
    # --- правая ветвь: R4 и ключ
    resistor(ax, (XR, YM), (XR, 560)); label(ax, XR + 46, 425, "R4", ha="left")
    wire(ax, [(XR, 560), (XR, YB)])
    xs = 650
    if sw == "closed":
        wire(ax, [(XR, YB), (XM, YB)])
        label(ax, xs, YB + 44, "ключ замкнут", fs=FS - 3)
    else:
        wire(ax, [(XR, YB), (xs + 55, YB)]); wire(ax, [(xs - 55, YB), (XM, YB)])
        wire(ax, [(xs + 55, YB), (xs - 55 + 8, YB - 38)])
        dot(ax, (xs + 55, YB), r=6); dot(ax, (xs - 55, YB), r=6)
        label(ax, xs, YB + 44, "ключ разомкнут", fs=FS - 3)
    for p in [(XM, YM), (XR, YM), (XM, YB)]:
        dot(ax, p)
    node_tag(ax, (XM, YM), "1", off=(-34, -32)); node_tag(ax, (XR, YM), "2", off=(36, -32))
    ground(ax, (XM, YB), 22); label(ax, XM + 44, YB + 52, "0", color=ANN, fs=FS - 1)
    # --- пояснения
    for (x, y, s, kw) in notes:
        label(ax, x, y, s, **kw)
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
    save(fig, OUT + name)


def before():
    """Докоммутационная схема (постоянный ток, ключ разомкнут)."""
    draw("gap", "wire", "src", "src", "open", "fig21_before.png", [])


def forced():
    """Принуждённый режим после замыкания ключа (постоянный ток)."""
    draw("gap", "wire", "src", "src", "closed", "fig21_forced.png", [])


def free():
    """Схема для свободного процесса: V1 - перемычка, I1 - разрыв."""
    draw("cap", "coil", "wire", "gap", "closed", "fig21_free.png", [])


if __name__ == "__main__":
    plain(); annotated(); spice_nodes(); before(); forced(); free()
