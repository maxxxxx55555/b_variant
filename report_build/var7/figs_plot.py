# -*- coding: utf-8 -*-
"""Графики: результаты расчёта (Python) и моделирования (ngspice), вариант 7."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
sys.path.insert(0, "calc")
import task12, task21, task22

W = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/"
OUT = W + "figs/"
SP = W + "spice/"

plt.rcParams.update({
    "font.family": "Liberation Serif", "font.size": 12,
    "mathtext.fontset": "custom", "mathtext.rm": "Liberation Serif",
    "mathtext.it": "Liberation Serif:italic", "mathtext.bf": "Liberation Serif:bold",
    "mathtext.default": "it", "axes.unicode_minus": True,
    "axes.grid": True, "grid.color": "#c9c9c9", "grid.linewidth": 0.6,
    "axes.edgecolor": "#333333", "axes.linewidth": 0.9,
})
NAVY, ORANGE, GREEN, RED, PURPLE, GRAY = "#1f3b73", "#d95f02", "#2e8b57", "#b3300f", "#7b3294", "#555555"


def comma(v, _=None):
    return f"{v:g}".replace(".", ",").replace("-", "−")


def style(ax):
    ax.xaxis.set_major_formatter(FuncFormatter(comma))
    ax.yaxis.set_major_formatter(FuncFormatter(comma))
    ax.tick_params(direction="in")


# ---------------------------------------------------------------- задание 1-2
def fig12_dc():
    d = np.loadtxt(SP + "dc12.txt")
    v = d[:, 0]
    cols = [("R1", 1, "#1f77b4", "-"), ("R3", 3, "#9467bd", "--"), ("R4", 5, GREEN, "-"),
            ("R5", 7, RED, "-"), ("R6", 9, ORANGE, "--")]
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    xk, _, _, _ = task12.nodal()
    ref = dict(zip(task12.NAMES, xk))
    for name, c, col, ls in cols:
        ax.plot(v, d[:, c], color=col, ls=ls, lw=2.0, label=rf"$I_{{{name}}}$")
        ax.plot([task12.V1], [ref[name]], "o", color=col, ms=6, mec="black", mew=0.8, zorder=5)
    ax.axvline(task12.V1, color=GRAY, ls=":", lw=1.4)
    ax.text(task12.V1 - 5, -2.2, "V1 = 306 В", ha="right", va="bottom", color=GRAY)
    ax.set_xlabel("ЭДС источника V1, В"); ax.set_ylabel("Ток ветви, А")
    ax.set_xlim(0, 400); ax.set_ylim(-2.3, 4.2)
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.13), frameon=False, handlelength=2.0,
              columnspacing=1.2)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT + "fig12_dc.png", dpi=220); plt.close(fig)


# ---------------------------------------------------------------- задание 2-1
def fig21_python():
    U0 = task21.initial_conditions()[2]
    Up = task21.forced()[3]
    tau = task21.free_process()[2]
    t = np.linspace(0, 600e-6, 1201)
    tn = np.array([-100e-6, 0])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.9), sharex=True)
    a1.plot(tn * 1e6, [U0, U0], color=NAVY, lw=2.2)
    a1.plot(t * 1e6, task21.uc(t), color=NAVY, lw=2.2, label=r"$u_C(t)$")
    a1.axhline(Up, color=GRAY, ls="--", lw=1.2)
    a1.text(590, Up + 4, rf"$u_{{C\,пр}}$ = {comma(round(Up, 2))} В", ha="right", va="bottom", color=GRAY)
    a1.plot([0], [U0], "o", color=ORANGE, ms=7, mec="black", mew=0.8, zorder=5)
    a1.annotate(rf"$u_C(0)$ = {comma(round(U0, 1))} В", (0, U0), (40, U0 - 14), fontsize=12,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.9))
    ut = task21.uc(tau)
    a1.plot([tau * 1e6], [ut], "o", color=ORANGE, ms=7, mec="black", mew=0.8, zorder=5)
    a1.annotate(rf"t = τ = {comma(round(tau * 1e6, 1))} мкс" + "\n" + rf"$u_C$ = {comma(round(float(ut), 1))} В",
                (tau * 1e6, ut), (230, 190), fontsize=12, arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.9))
    a1.axvline(0, color=RED, lw=1.2, ls=":")
    a1.set_ylabel(r"$u_C$, В"); a1.set_ylim(80, 235)
    a1.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    a2.plot(tn * 1e6, [task21.I1, task21.I1], color=GREEN, lw=2.2)
    a2.plot(t * 1e6, task21.il(t), color=GREEN, lw=2.2, label=r"$i_L(t) = I_1$")
    a2.axvline(0, color=RED, lw=1.2, ls=":")
    a2.set_ylabel(r"$i_L$, А"); a2.set_xlabel("Время t, мкс (t = 0 — момент замыкания ключа)")
    a2.set_xlim(-100, 600); a2.set_ylim(0, 2.0)
    a2.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    for a in (a1, a2): style(a)
    fig.tight_layout()
    fig.savefig(OUT + "fig21_python.png", dpi=220); plt.close(fig)


def fig21_spice():
    d = np.loadtxt(SP + "tran21.txt")
    t, uc, il = d[:, 0], d[:, 1] - d[:, 3], d[:, 5]
    ts = 100e-6
    tt = t - ts
    U0 = task21.initial_conditions()[2]
    ua = np.where(tt < 0, U0, task21.uc(np.clip(tt, 0, None)))
    ia = np.full_like(tt, task21.I1)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.9), sharex=True)
    st = 160
    a1.plot(tt * 1e6, uc, color=NAVY, lw=2.2, label="ngspice")
    a1.plot(tt[::st] * 1e6, ua[::st], "o", color=ORANGE, ms=4.2, mec="black", mew=0.5, ls="none",
            label="аналитический расчёт")
    a1.set_ylabel(r"$u_C$, В"); a1.axvline(0, color=RED, lw=1.2, ls=":")
    a1.set_ylim(80, 235)
    a1.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    a2.plot(tt * 1e6, il, color=GREEN, lw=2.2, label="ngspice")
    a2.plot(tt[::st] * 1e6, ia[::st], "o", color=ORANGE, ms=4.2, mec="black", mew=0.5, ls="none",
            label="аналитический расчёт")
    a2.set_ylabel(r"$i_L$, А"); a2.set_xlabel("Время t − t₀, мкс (t₀ = 100 мкс — момент замыкания ключа)")
    a2.axvline(0, color=RED, lw=1.2, ls=":")
    a2.set_xlim(-100, 600); a2.set_ylim(0, 2.0)
    a2.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    for a in (a1, a2): style(a)
    fig.tight_layout()
    fig.savefig(OUT + "fig21_spice.png", dpi=220); plt.close(fig)
    m = tt >= 0
    return np.abs(uc[m] - ua[m]).max(), np.abs(il - ia).max()


# ---------------------------------------------------------------- задание 2-2
SPICE_COL = {"L3": 5, "C2": 7, "C1": 9, "L1": 11, "L2": 13, "V1": 15}


def tran22_data():
    d = np.loadtxt(SP + "tran22.txt")
    y = {k: d[:, c] for k, c in SPICE_COL.items()}
    y["UL3"] = d[:, 1] - d[:, 3]
    return d[:, 0], y


def fig22_plots():
    phi, I, _ = task22.solve()
    UL3 = task22.ZL(task22.L3) * I["L3"]
    t, y = tran22_data()
    w = task22.w
    T = 1 / task22.f
    t0 = 20e-3
    m = (t >= t0) & (t <= t0 + 3 * T)
    ta = np.linspace(t0, t0 + 3 * T, 73)
    # u_L3(t)
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.plot(t[m] * 1e3, y["UL3"][m], color=NAVY, lw=2.2, label="ngspice")
    ax.plot(ta * 1e3, abs(UL3) * np.sin(w * ta + np.angle(UL3)), "o", color=ORANGE, ms=4.5, mec="black",
            mew=0.5, ls="none", label=r"аналитический расчёт $u_{L3}(t)$")
    ax.set_xlabel("Время t, мс"); ax.set_ylabel(r"$u_{L3}$, В")
    ax.set_xlim(t0 * 1e3, (t0 + 3 * T) * 1e3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=False)
    style(ax); fig.tight_layout()
    fig.savefig(OUT + "fig22_ul3.png", dpi=220); plt.close(fig)
    # токи ветвей (малые графики)
    names = [("L3", r"$i_{L3}$"), ("C2", r"$i_{C2}$"), ("C1", r"$i_{C1}$"), ("L1", r"$i_{L1}$"),
             ("L2", r"$i_{L2}$"), ("V1", r"$i_{V1}$")]
    fig, axs = plt.subplots(3, 2, figsize=(7.0, 6.2), sharex=True)
    for ax, (k, lab) in zip(axs.flat, names):
        ax.plot(t[m] * 1e3, y[k][m], color=NAVY, lw=2.0, label="ngspice")
        ax.plot(ta * 1e3, abs(I[k]) * np.sin(w * ta + np.angle(I[k])), "o", color=ORANGE, ms=3.6,
                mec="black", mew=0.4, ls="none", label="расчёт")
        ax.set_ylabel(lab + ", А"); ax.set_xlim(t0 * 1e3, (t0 + 3 * T) * 1e3)
        style(ax)
    for ax in axs[-1]: ax.set_xlabel("Время t, мс")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT + "fig22_currents_t.png", dpi=220); plt.close(fig)
    # погрешности
    mm = t >= t0
    err = {}
    for k in ("L3", "C2", "C1", "L1", "L2", "V1"):
        a = abs(I[k]) * np.sin(w * t[mm] + np.angle(I[k]))
        err[k] = np.abs(y[k][mm] - a).max()
    a = abs(UL3) * np.sin(w * t[mm] + np.angle(UL3))
    err["UL3"] = np.abs(y["UL3"][mm] - a).max()
    return err


if __name__ == "__main__":
    fig12_dc(); fig21_python()
    print("2-1 max err (uc, il):", fig21_spice())
    print("2-2 max err:", fig22_plots())
