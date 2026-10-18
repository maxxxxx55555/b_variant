# -*- coding: utf-8 -*-
"""Рисунки к заданию 2-2."""
import numpy as np
from sch import *
from figs12 import overlay_canvas, W, OUT

CROP = (20, 150, 1215, 1000)
P1, P2, P3, P4 = (214, 291), (801, 291), (214, 878), (801, 878)


def plain():
    fig, ax = overlay_canvas("p22_v22.png", CROP)
    save(fig, OUT + "fig22_scheme.png")


def annotated():
    fig, ax = overlay_canvas("p22_v22.png", CROP)
    node_tag(ax, P1, "1", off=(-36, -34)); node_tag(ax, P2, "2", off=(36, -34))
    node_tag(ax, P3, "3", off=(-36, 36)); node_tag(ax, P4, "4", off=(40, 36))
    ground(ax, P4, 24)
    d = r"$\dot{I}_{"
    # R1: сверху вниз
    arrow(ax, (68, 360), (68, 470)); label(ax, 112, 415, d + "R1}$", color=ANN)
    # ветвь L1-V1: сверху вниз
    arrow(ax, (214, 515), (214, 630)); label(ax, 262, 572, d + "L1}$", color=ANN)
    # ветвь V2-L2-C2: слева направо
    arrow(ax, (570, 291), (660, 291)); label(ax, 615, 253, d + "L2}$", color=ANN)
    # C1: слева направо
    arrow(ax, (270, 878), (420, 878)); label(ax, 345, 916, d + "C1}$", color=ANN)
    # R2-I1: снизу вверх
    arrow(ax, (801, 670), (801, 540)); label(ax, 850, 605, d + "R2}$", color=ANN)
    # C3: сверху вниз
    arrow(ax, (948, 345), (948, 455)); label(ax, 996, 400, d + "C3}$", color=ANN)
    # R3-L3: сверху вниз
    arrow(ax, (1095, 515), (1095, 625)); label(ax, 1046, 570, d + "L3}$", color=ANN)
    # напряжение на L3
    label(ax, 1056, 690, "+", color=ANN2, fs=FS + 4); label(ax, 1056, 782, "−", color=ANN2, fs=FS + 4)
    label(ax, 1038, 736, r"$\dot{U}_{L3}$", color=ANN2, ha="right")
    save(fig, OUT + "fig22_currents.png")


def complex_scheme():
    """Схема замещения для комплексных амплитуд: ветви заменены сопротивлениями Z1...Z7."""
    fig, ax = overlay_blank(CROP)
    wire(ax, [(68, 291), (214, 291)]); wire(ax, [(68, 878), (214, 878)])
    resistor(ax, (68, 291), (68, 878)); label(ax, 112, 584, r"$Z_1$", ha="left")
    resistor(ax, (214, 291), (214, 560)); label(ax, 258, 425, r"$Z_2$", ha="left")
    vsource(ax, (214, 878), (214, 560), forward=False, t=0.5)
    label(ax, 258, 720, r"$\dot{V}_1$", ha="left")
    vsource(ax, (214, 291), (410, 291), forward=True); label(ax, 312, 360, r"$\dot{V}_2$")
    resistor(ax, (410, 291), (801, 291)); label(ax, 605, 254, r"$Z_3$")
    resistor(ax, (214, 878), (801, 878)); label(ax, 507, 922, r"$Z_4$")
    resistor(ax, (801, 291), (801, 583)); label(ax, 850, 437, r"$Z_5$", ha="left")
    isource(ax, (801, 878), (801, 583), forward=True); label(ax, 850, 735, r"$\dot{I}_1$", ha="left")
    wire(ax, [(801, 291), (1095, 291)]); wire(ax, [(801, 878), (1095, 878)])
    resistor(ax, (948, 291), (948, 878)); label(ax, 900, 584, r"$Z_6$", ha="right")
    resistor(ax, (1095, 291), (1095, 878)); label(ax, 1142, 584, r"$Z_7$", ha="left")
    for p in (P1, P2, P3, P4, (948, 291), (948, 878)):
        dot(ax, p)
    node_tag(ax, P1, "1", off=(-36, -34)); node_tag(ax, P2, "2", off=(36, -34))
    node_tag(ax, P3, "3", off=(-36, 36)); node_tag(ax, P4, "4", off=(40, 36))
    ground(ax, P4, 24)
    save(fig, OUT + "fig22_complex.png")


def overlay_blank(crop):
    x0, y0, x1, y1 = crop
    fig, ax = new_canvas(x1 - x0, y1 - y0)
    ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
    return fig, ax


def spice_nodes():
    fig, ax = overlay_canvas("p22_v22.png", CROP)
    lab = dict(color=ANN, fs=FS - 2)
    label(ax, 180, 255, "n1", **lab); label(ax, 836, 255, "n2", **lab)
    label(ax, 180, 925, "n3", **lab); label(ax, 836, 925, "0", **lab); ground(ax, P4, 22)
    label(ax, 1056, 605, "g2", **lab)
    # амперметры: источники нулевого напряжения VA1 ... VA6
    for (x, y, nm, dx, dy) in [(68, 350, "VA1", 52, 0), (214, 350, "VA2", 40, 44), (255, 291, "VA3", 0, -34),
                               (330, 878, "VA4", 0, 38), (948, 350, "VA5", 52, 0), (1095, 350, "VA6", 52, 0), (801, 640, "VA7", 52, 0)]:
        ax.add_patch(Circle((x, y), 15, fc="white", ec=ANN, lw=2.2, zorder=9))
        ax.text(x, y, "A", fontsize=FS - 7, color=ANN, ha="center", va="center", zorder=10)
        label(ax, x + dx, y + dy, nm, **lab)
    save(fig, OUT + "fig22_spice.png")


def ltspice_nodes():
    """Схема 2-2 с именами цепей, как в файлах LTspice (без амперметров: токи берутся у самих компонентов)."""
    fig, ax = overlay_canvas("p22_v22.png", CROP)
    lab = dict(color=ANN, fs=FS - 2)
    label(ax, 180, 255, "n1", **lab); label(ax, 836, 255, "n2", **lab)
    label(ax, 180, 925, "n3", **lab); label(ax, 836, 925, "0", **lab); ground(ax, P4, 22)
    label(ax, 1056, 605, "g2", **lab)
    save(fig, OUT + "fig22_ltspice.png")


if __name__ == "__main__":
    plain(); annotated(); complex_scheme(); spice_nodes(); ltspice_nodes()
