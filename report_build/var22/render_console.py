# -*- coding: utf-8 -*-
"""Отрисовка вывода программ (Python и ngspice) в виде изображений «консоли»."""
import re, subprocess, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

W = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/"
OUT = W + "figs/"


def console_png(lines, path, fs=9.6):
    cw = 0.602 * fs                       # ширина символа DejaVu Sans Mono, pt
    n = max(len(l) for l in lines)
    pad = 12
    w = (n * cw + 2 * pad) / 72
    h = (len(lines) * fs * 1.28 + 2 * pad) / 72
    fig = plt.figure(figsize=(w, h), dpi=220)
    fig.patch.set_facecolor("#fbfbfb")
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, w * 72); ax.set_ylim(h * 72, 0)
    ax.add_patch(plt.Rectangle((0.5, 0.5), w * 72 - 1, h * 72 - 1, fill=False, ec="#8a8a8a", lw=0.9))
    for i, l in enumerate(lines):
        col = "#0b3d91" if l.startswith("$ ") else "#111111"
        ax.text(pad, pad + (i + 0.5) * fs * 1.28, l, family="DejaVu Sans Mono", fontsize=fs,
                color=col, va="center", ha="left")
    fig.savefig(path, dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)


def run_py(name):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run(["python3", f"calc/{name}.py"], cwd=W, capture_output=True, text=True, env=env)
    out = r.stdout.rstrip("\n").split("\n")
    return [f"$ python3 {name}.py"] + out


def spice_lines(log, netlist):
    keep = []
    for l in open(W + "spice/" + log, encoding="utf-8").read().split("\n"):
        s = l.rstrip()
        if (s.startswith("Circuit:") or re.match(r"^[\w@#\(\)\[\]\.]+ = ", s) or s.startswith("irms")
                or (s.startswith("No. of Data Rows") and "Rows : 1" not in s)):
            keep.append(s)
    return [f"$ ngspice -b {netlist} -o {log}"] + keep


if __name__ == "__main__":
    for nm in ("task12", "task21", "task22"):
        lines = run_py(nm)
        open(W + f"spice/../figs/{nm}_out.txt", "w", encoding="utf-8").write("\n".join(lines))
        console_png(lines, OUT + f"{nm}_console.png")
    for lg, nl, tag in (("t12.log", "t12.cir", "t12"), ("t21.log", "t21.cir", "t21"), ("t22.log", "t22.cir", "t22")):
        lines = spice_lines(lg, nl)
        open(W + f"figs/{tag}_spice_out.txt", "w", encoding="utf-8").write("\n".join(lines))
        console_png(lines, OUT + f"{tag}_spice_console.png")
