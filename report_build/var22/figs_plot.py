# -*- coding: utf-8 -*-
"""Графики: результаты расчёта (Python) и моделирования (ngspice)."""
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
    ax.text(task12.V1 + 5, 3.62, "V1 = 290 В", ha="left", va="top", color=GRAY)
    ax.set_xlabel("ЭДС источника V1, В"); ax.set_ylabel("Ток ветви, А")
    ax.set_xlim(0, 400)
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.13), frameon=False, handlelength=2.0, columnspacing=1.2)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT + "fig12_dc.png", dpi=220); plt.close(fig)


# ---------------------------------------------------------------- задание 2-1
def fig21_python():
    phi1, U0 = task21.initial_conditions()
    R6, al, w0, wd, Rkr = task21.parameters()
    t = np.linspace(0, 1.5e-3, 3001)
    uc = task21.uc_analytic(t, U0)
    il = task21.il_analytic(t, U0)
    env = abs(U0) * w0 / wd * np.exp(-al * t)
    tp = np.array([-0.2e-3, 0])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.9), sharex=True)
    a1.plot(tp * 1e3, [U0, U0], color=NAVY, lw=2.2)
    a1.plot(t * 1e3, uc, color=NAVY, lw=2.2, label=r"$u_C(t)$")
    a1.plot(t * 1e3, env, color=GRAY, ls="--", lw=1.2, label=r"огибающая $\pm|U_0|\,\omega_0/\omega_{св}\,e^{-\alpha t}$")
    a1.plot(t * 1e3, -env, color=GRAY, ls="--", lw=1.2)
    a1.plot([0], [U0], "o", color=ORANGE, ms=7, mec="black", mew=0.8, zorder=5)
    a1.annotate(rf"$u_C(0)$ = {comma(round(U0, 3))} В", (0, U0), (0.33, U0 + 3), fontsize=12,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.9))
    k = uc.argmax()
    a1.plot([t[k] * 1e3], [uc[k]], "o", color=ORANGE, ms=7, mec="black", mew=0.8, zorder=5)
    a1.annotate(f"максимум {comma(round(uc[k], 2))} В\nпри t = {comma(round(t[k] * 1e6, 1))} мкс",
                (t[k] * 1e3, uc[k]), (0.55, 24), fontsize=12, arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.9))
    a1.axvline(0, color=RED, lw=1.2, ls=":")
    a1.set_ylabel(r"$u_C$, В"); a1.set_ylim(-58, 44)
    a1.legend(loc="lower right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    a2.plot(tp * 1e3, [0, 0], color=GREEN, lw=2.2)
    a2.plot(t * 1e3, il, color=GREEN, lw=2.2, label=r"$i_{L}(t)$")
    a2.axvline(0, color=RED, lw=1.2, ls=":")
    a2.set_ylabel(r"$i_L$, А"); a2.set_xlabel("Время t, мс"); a2.set_xlim(-0.2, 1.5)
    a2.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    for a in (a1, a2): style(a)
    fig.tight_layout()
    fig.savefig(OUT + "fig21_python.png", dpi=220); plt.close(fig)


def fig21_spice():
    d = np.loadtxt(SP + "tran21.txt")
    t, uc, il = d[:, 0], d[:, 1], d[:, 3]
    ts = 200e-6
    phi1, U0 = task21.initial_conditions()
    tt = t - ts
    ua = np.where(tt < 0, U0, task21.uc_analytic(np.clip(tt, 0, None), U0))
    ia = np.where(tt < 0, 0.0, task21.il_analytic(np.clip(tt, 0, None), U0))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.9), sharex=True)
    st = 90
    a1.plot(tt * 1e3, uc, color=NAVY, lw=2.2, label="ngspice")
    a1.plot(tt[::st] * 1e3, ua[::st], "o", color=ORANGE, ms=4.2, mec="black", mew=0.5, ls="none",
            label="аналитический расчёт")
    a1.set_ylabel(r"$u_C$, В"); a1.axvline(0, color=RED, lw=1.2, ls=":")
    a1.legend(loc="lower right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    a2.plot(tt * 1e3, il, color=GREEN, lw=2.2, label="ngspice")
    a2.plot(tt[::st] * 1e3, ia[::st], "o", color=ORANGE, ms=4.2, mec="black", mew=0.5, ls="none",
            label="аналитический расчёт")
    a2.set_ylabel(r"$i_L$, А"); a2.set_xlabel("Время t − t₀, мс (t₀ = 200 мкс — момент размыкания ключа)")
    a2.axvline(0, color=RED, lw=1.2, ls=":")
    a2.set_xlim(-0.2, 1.5)
    a2.legend(loc="upper right", frameon=True, fancybox=False, edgecolor="#bbbbbb", fontsize=11)
    for a in (a1, a2): style(a)
    fig.tight_layout()
    fig.savefig(OUT + "fig21_spice.png", dpi=220); plt.close(fig)
    m = tt >= 0
    return np.abs(uc[m] - ua[m]).max(), np.abs(il[m] - ia[m]).max()


# ---------------------------------------------------------------- задание 2-2
def tran22_data():
    d = np.loadtxt(SP + "tran22.txt")
    return d[:, 0], {"UL3": d[:, 1], "R1": d[:, 3], "L1": d[:, 5], "L2": d[:, 7], "C1": d[:, 9],
                     "C3": d[:, 11], "L3": d[:, 13]}


def fig22_plots():
    phi, I, _ = task22.solve()
    UL3 = task22.ZL(task22.L3) * I["L3"]
    t, y = tran22_data()
    w = task22.w
    T = 1 / task22.f
    m = (t >= 20e-3) & (t <= 20e-3 + 3 * T)
    ta = np.linspace(20e-3, 20e-3 + 3 * T, 61)
    # u_L3(t)
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.plot(t[m] * 1e3, y["UL3"][m], color=NAVY, lw=2.2, label="ngspice")
    ax.plot(ta * 1e3, abs(UL3) * np.sin(w * ta + np.angle(UL3)), "o", color=ORANGE, ms=4.5, mec="black",
            mew=0.5, ls="none", label=r"аналитический расчёт $u_{L3}(t)$")
    ax.set_xlabel("Время t, мс"); ax.set_ylabel(r"$u_{L3}$, В")
    ax.set_xlim(20, 23)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=False)
    style(ax); fig.tight_layout()
    fig.savefig(OUT + "fig22_ul3.png", dpi=220); plt.close(fig)
    # токи ветвей (малые графики)
    names = [("R1", r"$i_{R1}$"), ("L1", r"$i_{L1}$"), ("L2", r"$i_{L2}$"), ("C1", r"$i_{C1}$"),
             ("C3", r"$i_{C3}$"), ("L3", r"$i_{L3}$")]
    fig, axs = plt.subplots(3, 2, figsize=(7.0, 6.2), sharex=True)
    for ax, (k, lab) in zip(axs.flat, names):
        ax.plot(t[m] * 1e3, y[k][m], color=NAVY, lw=2.0, label="ngspice")
        ax.plot(ta * 1e3, abs(I[k]) * np.sin(w * ta + np.angle(I[k])), "o", color=ORANGE, ms=3.6,
                mec="black", mew=0.4, ls="none", label="расчёт")
        ax.set_ylabel(lab + ", А"); ax.set_xlim(20, 23)
        style(ax)
    for ax in axs[-1]: ax.set_xlabel("Время t, мс")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT + "fig22_currents_t.png", dpi=220); plt.close(fig)
    # погрешности
    err = {}
    for k in ("R1", "L1", "L2", "C1", "C3", "L3"):
        a = abs(I[k]) * np.sin(w * t[m] + np.angle(I[k]))
        err[k] = np.abs(y[k][m] - a).max()
    a = abs(UL3) * np.sin(w * t[m] + np.angle(UL3))
    err["UL3"] = np.abs(y["UL3"][m] - a).max()
    return err


if __name__ == "__main__":
    fig12_dc(); fig21_python()
    print("2-1 max err (uc, il):", fig21_spice())
    print("2-2 max err:", fig22_plots())
