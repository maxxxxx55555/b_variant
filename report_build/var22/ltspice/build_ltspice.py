# -*- coding: utf-8 -*-
"""Строит файлы LTspice (.asc и запасные .cir) для ДЗ1, вариант 22, и проверяет их:
1) разбор схемы собственным нетлистером (связность, ориентация источников);
2) прогон полученного нетлиста в ngspice и сравнение с расчётом на Python (calc/*.py).
LTspice в рабочем окружении недоступен, поэтому сама программа здесь не запускалась."""
import json, os, re, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "calc"))
from ltspice_gen import Sch, netlist_from_asc
import task12, task21, task22

OUT = os.path.join(HERE, "files")
os.makedirs(OUT, exist_ok=True)

T0 = 200e-6                       # момент размыкания ключа на оси времени моделирования, с
SWITCH_R = "R={if(V(ctrl)>0.5,1e-6,1e9)}"      # ключ S1: резистор, управляемый напряжением V(ctrl)
CTRL_PULSE = "PULSE(1 0 200u 1n 1n 1 2)"        # управляющий импульс: 1 В (замкнут) до 200 мкс, затем 0 В


def branch(s, x, y_from, y_to, comps, first_gap=48, gap=16):
    """Вертикальная цепочка компонентов от шины y_from к шине y_to. comps: (sym, name, value, rot, value2)."""
    y = y_from + first_gap
    prev = (x, y_from)
    res = {}
    for (sym, name, val, r, v2) in comps:
        top, bot = s.comp(sym, name, val, x, y, r, v2)
        s.wire(prev[0], prev[1], top[0], top[1])
        res[name] = (top, bot)
        prev = bot
        y = bot[1] + gap
    assert prev[1] <= y_to, (name, prev, y_to)
    s.wire(prev[0], prev[1], x, y_to)
    return res


def note(s, x, y, lines, row_h=32):
    """Комментарий на схеме (TEXT с ';'): несколько коротких строк; возвращает следующую свободную y."""
    for ln in lines:
        assert len(ln) <= 100, ln
        s.text(x, y, ln, directive=False)
        y += row_h
    return y


def meas_block(s, x0, y0, lines, ncols, col_w, row_h=32):
    """Директивы .meas столбиками под схемой; возвращает нижнюю границу блока."""
    rows = -(-len(lines) // ncols)
    for k, ln in enumerate(lines):
        c, r = divmod(k, rows)
        s.text(x0 + c * col_w, y0 + r * row_h, ln)
    return y0 + rows * row_h


# ------------------------------------------------------------------ контрольные значения (из расчёта на Python)
def exp_12():
    """Токи резисторов (направление от первого вывода ко второму в схеме LTspice) при V1 = 290 В."""
    xn, phi, _, _ = task12.nodal()
    I = dict(zip(task12.NAMES, xn))
    I["R2"] = task12.I1
    vf = phi[0] + task12.R2 * task12.I1
    return [("ir1", "I(R1)", I["R1"]), ("ir2", "I(R2)", I["R2"]), ("ir3", "I(R3)", I["R3"]),
            ("ir4", "I(R4)", I["R4"]), ("ir5", "I(R5)", I["R5"]), ("ir6", "I(R6)", I["R6"]),
            ("vn1", "V(n1)", phi[0]), ("vn2", "V(n2)", phi[1]), ("vf", "V(f)", vf)]


T_POINTS = (0, 50, 100, 200, 300, 400, 600, 800)           # мкс после размыкания ключа


def exp_21():
    _, U0 = task21.initial_conditions()
    out = [("uc_before", "V(n3)", f"{T0 * 1e6 - 50:g}u", U0), ("il_before", "I(L1)", f"{T0 * 1e6 - 50:g}u", 0.0)]
    for k in T_POINTS:
        t = k * 1e-6
        out.append((f"uc_{k}", "V(n3)", f"{T0 * 1e6 + k:g}u", float(task21.uc_analytic(t, U0))))
        out.append((f"il_{k}", "I(L1)", f"{T0 * 1e6 + k:g}u", float(task21.il_analytic(t, U0))))
    return out


def exp_22():
    phi, I, _ = task22.solve()
    UL3 = task22.ZL(task22.L3) * I["L3"]
    cur = [(d, I[d]) for d in task22.BRANCHES]
    volt = [("n1", phi[0]), ("n2", phi[1]), ("n3", phi[2]), ("g2", UL3)]
    return cur, volt, UL3


# ------------------------------------------------------------------ задание 1-2
def build_12():
    s = Sch(1300, 900)
    Y1, Y2, Y0 = 128, 352, 704
    b = {}
    b.update(branch(s, 192, Y1, Y0, [("res", "R1", "88", "R0", None)]))
    b.update(branch(s, 336, Y1, Y0, [("res", "R3", "93", "R0", None)]))
    b.update(branch(s, 480, Y1, Y0, [("res", "R2", "21", "R180", None), ("current", "I1", "2.97", "R180", None)]))
    b.update(branch(s, 768, Y1, Y2, [("voltage", "V2", "64", "R180", None), ("res", "R6", "54", "R0", None)]))
    b.update(branch(s, 912, Y1, Y2, [("res", "R4", "38", "R0", None)]))
    b.update(branch(s, 1056, Y2, Y0, [("voltage", "V1", "290", "R180", None), ("res", "R5", "93", "R0", None)]))
    s.wire(192, Y1, 912, Y1)          # шина узла 1
    s.wire(768, Y2, 1056, Y2)         # шина узла 2
    s.wire(192, Y0, 1056, Y0)         # шина узла 3 (земля)
    s.flag(624, Y0, "0"); s.flag(624, Y1, "n1"); s.flag(912, Y2, "n2")
    s.flag(*b["V2"][1], "e2"); s.flag(*b["V1"][1], "d"); s.flag(*b["I1"][0], "f")
    y = note(s, 192, 776, ["DZ1, variant 22, task 1-2: DC circuit. V1 is swept 0...400 V (the task value is 290 V)",
                           "Nodes: n1, n2 = nodes 1, 2 of the report; 0 = node 3"])
    s.text(192, y, ".dc V1 0 400 5")
    lines = [f".meas dc {nm} FIND {ex} AT 290" for nm, ex, _ in exp_12()]
    y = meas_block(s, 192, y + 48, lines, 3, 400)
    s.h = y + 32
    return s


# ------------------------------------------------------------------ задание 2-1
def build_21():
    s = Sch(1300, 900)
    Y1, Y2, Y0 = 128, 352, 704
    b = {}
    b.update(branch(s, 192, Y1, Y0, [("res", "R2", "77", "R0", None), ("voltage", "V1", "309", "R180", None)]))
    b.update(branch(s, 336, Y1, Y0, [("res", "R1", "100", "R180", None), ("current", "I1", "1.47", "R180", None)]))
    b.update(branch(s, 480, Y1, Y2, [("res", "R3", "38", "R0", None), ("res", "RS1", SWITCH_R, "R0", None)]))
    b.update(branch(s, 624, Y2, Y0, [("res", "R4", "36", "R0", None)]))
    b.update(branch(s, 768, Y2, Y0, [("ind", "L1", "5m", "R0", None), ("res", "R5", "17", "R0", None),
                                      ("cap", "C1", "1u", "R0", None)]))
    s.wire(192, Y1, 480, Y1)
    s.wire(480, Y2, 768, Y2)
    b.update(branch(s, 912, 512, Y0, [("voltage", "Vc", CTRL_PULSE, "R0", None)], first_gap=0))
    s.wire(192, Y0, 912, Y0)
    s.flag(*b["Vc"][0], "ctrl")
    s.flag(480, Y0, "0"); s.flag(336, Y1, "n1"); s.flag(624, Y2, "n2")
    s.flag(*b["C1"][0], "n3"); s.flag(*b["L1"][1], "n4"); s.flag(*b["R2"][1], "nv"); s.flag(*b["R3"][1], "ns")
    s.flag(*b["I1"][0], "nx")
    y = note(s, 192, 776, ["DZ1, variant 22, task 2-1: transient process after opening the key S1",
                           "RS1 = key S1 (controlled by Vc): closed (1 uOhm) until t = 200 us, then open (1 GOhm)",
                           "Report time t = simulation time - 200 us.  u_C = V(n3), i_L = I(L1)"])
    s.text(192, y, ".tran 0 1.7m 0 0.2u")
    s.text(192, y + 32, ".options plotwinsize=0 numdgt=15")
    lines = [f".meas tran {nm} FIND {ex} AT {at}" for nm, ex, at, _ in exp_21()]
    y = meas_block(s, 192, y + 80, lines, 3, 430)
    s.h = y + 32
    return s


# ------------------------------------------------------------------ задание 2-2
def build_22(mode):
    s = Sch(1500, 1100)
    Y1, Y3, Y2, Y0 = 128, 384, 448, 800
    b = {}
    b.update(branch(s, 912, Y1, Y2, [("voltage", "V2", "SINE(0 284 1k)", "R180", "AC 284 0"),
                                      ("ind", "L2", "10m", "R0", None), ("cap", "C2", "0.71u", "R0", None)]))
    b.update(branch(s, 192, Y1, Y3, [("res", "R1", "23", "R0", None)]))
    b.update(branch(s, 336, Y1, Y3, [("ind", "L1", "6m", "R0", None), ("voltage", "V1", "SINE(0 130 1k)", "R180", "AC 130 0")]))
    b.update(branch(s, 480, Y3, Y0, [("cap", "C1", "0.83u", "R0", None)]))
    b.update(branch(s, 624, Y3, Y0, [("res", "Rg", "1e12", "R0", None)]))
    b.update(branch(s, 768, Y2, Y0, [("res", "R2", "6", "R180", None), ("current", "I1", "SINE(0 0.49 1k)", "R180", "AC 0.49 0")]))
    b.update(branch(s, 912, Y2, Y0, [("cap", "C3", "0.52u", "R0", None)]))
    b.update(branch(s, 1056, Y2, Y0, [("res", "R3", "94", "R0", None), ("ind", "L3", "12m", "R0", None)]))
    s.wire(192, Y1, 912, Y1)          # узел 1
    s.wire(192, Y3, 624, Y3)          # узел 3
    s.wire(768, Y2, 1056, Y2)         # узел 2
    s.wire(480, Y0, 1056, Y0)         # узел 4 (земля)
    s.flag(768, Y0, "0"); s.flag(576, Y1, "n1"); s.flag(256, Y3, "n3"); s.flag(840, Y2, "n2")
    s.flag(*b["R3"][1], "g2")
    y = note(s, 192, 872, ["DZ1, variant 22, task 2-2: sinusoidal steady state, f = 1 kHz (amplitudes, zero phase)",
                           "Nodes: n1, n2, n3 = nodes 1, 2, 3 of the report; 0 = node 4.  u_L3 = V(g2)",
                           "Rg = 1e12 Ohm only fixes the DC potential of node n3 (it does not affect the AC result)"])
    if mode == "ac":
        s.text(192, y, ".ac dec 20 100 10k")
        lines = []
        for dev, _ in exp_22()[0]:
            lines += [f".meas ac i{dev}_mag FIND mag(I({dev})) AT 1k", f".meas ac i{dev}_ph FIND ph(I({dev})) AT 1k"]
        for n, _ in exp_22()[1]:
            lines += [f".meas ac v{n}_mag FIND mag(V({n})) AT 1k", f".meas ac v{n}_ph FIND ph(V({n})) AT 1k"]
        y = meas_block(s, 192, y + 48, lines, 3, 460)
        s.h = y + 32
    else:
        s.text(192, y, ".tran 0 24m 0 2u")
        s.text(192, y + 32, ".options plotwinsize=0 numdgt=15")
        s.text(192, y + 64, ".meas tran irms RMS I(R2) FROM 20m TO 24m")
        s.text(192, y + 96, ".meas tran ul3max MAX V(g2) FROM 20m TO 24m")
        s.text(192, y + 128, ".meas tran ul3min MIN V(g2) FROM 20m TO 24m")
        s.h = y + 176
    return s


# ------------------------------------------------------------------ netlist из .asc
def with_switch(comps):
    """Замена резистора RS1 на ключ S1 (стандартная модель ключа SPICE); источник Vc уже есть в схеме."""
    out, extra = [], []
    for c in comps:
        if c.startswith("RS1 "):
            a, b_ = c.split()[1:3]
            out.append(f"S1 {a} {b_} ctrl 0 SWM")
            extra = [".model SWM SW(Ron=1u Roff=1G Vt=0.5 Vh=0.1)"]
        else:
            out.append(c)
    return out, extra


def cir_text(title, asc_text, switch=False):
    """Запасной вариант: нетлист LTspice (открывается через File -> Open, запуск Simulate -> Run)."""
    comps, texts = netlist_from_asc(asc_text)
    extra = []
    if switch:
        comps, extra = with_switch(comps)
    directives = [t[1:] for t in texts if t.startswith("!")]
    lines = [f"* {title}"] + comps + extra + directives + [".end"]
    return "\n".join(lines) + "\n"


def to_ngspice(asc_text, switch=False):
    """Тот же нетлист для ngspice: SINE -> SIN; R={if(..)} -> R='ternary_fcn(..)' либо ключ S1."""
    comps, texts = netlist_from_asc(asc_text)
    extra = []
    if switch:
        comps, extra = with_switch(comps)
    else:
        comps = [re.sub(r"R=\{if\((.*)\)\}$", r"R='ternary_fcn(\1)'", c) for c in comps]
    comps = [re.sub(r"SINE\(", "SIN(", c) for c in comps]
    return "\n".join(["* check"] + comps + extra + [".options numdgt=10", ".end"]) + "\n"


def run_ngspice(netlist, ctl):
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "n.cir"), "w").write(netlist.replace(".end", ".control\nset noaskquit\n" + ctl + "\n.endc\n.end"))
        r = subprocess.run(["ngspice", "-b", "n.cir"], cwd=d, capture_output=True, text=True)
        return r.stdout + r.stderr


def vals_of(out):
    return {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r"^([\w@\[\]\(\)#]+)\s*=\s*([-+0-9.eE]+)", out, re.M)}


def cmp(tag, name, got, want, tol, ok):
    good = got is not None and abs(got - want) <= tol * max(1.0, abs(want))
    print(f"{tag:5s} {name:12s} {got!s:>22s} {want:>22.10g}  {'OK' if good else 'ОШИБКА'}")
    return ok and good


def check_all():
    ok = True
    # ---- 1-2: режим по постоянному току при V1 = 290 В
    asc = build_12().asc()
    out = run_ngspice(to_ngspice(asc), "op\nprint v(n1) v(n2) v(f)\nprint @r1[i] @r2[i] @r3[i] @r4[i] @r5[i] @r6[i]")
    v = vals_of(out)
    for nm, ex, want in exp_12():
        key = ex.lower() if ex.startswith("V") else "@" + ex[2:-1].lower() + "[i]"
        ok = cmp("1-2", ex, v.get(key), want, 1e-5, ok)
    # ---- 2-1: до и после размыкания ключа (оба варианта ключа: резистор R(t) заменён на ключ S1)
    for sw in (False, True):
        asc = build_21().asc()
        out = run_ngspice(to_ngspice(asc, sw), "tran 0.2u 1.7m 0 0.2u\n" + "\n".join(
            f"meas tran m{k} FIND {ex.lower()} AT={at}" for k, (nm, ex, at, w) in enumerate(exp_21())))
        v = vals_of(out)
        for k, (nm, ex, at, want) in enumerate(exp_21()):
            ok = cmp("2-1", f"{nm}", v.get(f"m{k}"), want, 2e-3, ok)
    # ---- 2-2: амплитуды и фазы при f = 1 кГц
    asc = build_22("ac").asc()
    nl = to_ngspice(asc)
    cur, volt, UL3 = exp_22()
    comps, _ = netlist_from_asc(asc)
    nets = sorted({n for c in comps for n in c.split()[1:3] if n != "0"})
    out = run_ngspice(nl, "set units=radians\nac lin 1 1000 1000\n" + "\n".join(
        f"print real(v({n})) imag(v({n}))" for n in nets))
    pts = {}
    for m in re.finditer(r"^(real|imag)\((v\(\w+\))\)\s*=\s*([-+0-9.eE]+)", out, re.M | re.I):
        pts.setdefault(m.group(2).lower(), {})[m.group(1).lower()] = float(m.group(3))
    V = {k[2:-1]: complex(d["real"], d["imag"]) for k, d in pts.items()}
    V["0"] = 0j
    for n, z in volt:
        ok = cmp("2-2", f"|V({n})|", abs(V[n]), abs(z), 1e-5, ok)
        ok = cmp("2-2", f"arg V({n})", float(np.degrees(np.angle(V[n]))), float(np.degrees(np.angle(z))), 1e-5, ok)
    # токи ветвей: I = (V(вывод 1) - V(вывод 2)) / Z, выводы и ориентация - из схемы .asc
    w = task22.w
    Z = {"R": lambda x: x, "L": lambda x: 1j * w * x, "C": lambda x: 1 / (1j * w * x)}

    def num(t):
        return float(t.replace("u", "e-6").replace("m", "e-3"))
    val = {c.split()[0]: c.split() for c in comps}
    for dev, want in cur:
        p = val[dev]
        got = (V[p[1].lower()] - V[p[2].lower()]) / Z[dev[0]](num(p[3]))
        ok = cmp("2-2", f"|I({dev})|", abs(got), abs(want), 1e-5, ok)
        ok = cmp("2-2", f"arg I({dev})", float(np.degrees(np.angle(got))), float(np.degrees(np.angle(want))), 1e-5, ok)
    return ok


# ------------------------------------------------------------------ запись файлов
def write_files():
    asc12, asc21 = build_12().asc(), build_21().asc()
    asc22a, asc22t = build_22("ac").asc(), build_22("tran").asc()
    files = {
        "task12_dc_var22.asc": asc12, "task21_tran_var22.asc": asc21,
        "task22_ac_var22.asc": asc22a, "task22_tran_var22.asc": asc22t,
        "task12_dc_var22.cir": cir_text("DZ1 variant 22, task 1-2 (DC), LTspice netlist", asc12),
        "task21_tran_var22.cir": cir_text("DZ1 variant 22, task 2-1 (transient), LTspice netlist", asc21, switch=True),
        "task22_ac_var22.cir": cir_text("DZ1 variant 22, task 2-2 (AC), LTspice netlist", asc22a),
        "task22_tran_var22.cir": cir_text("DZ1 variant 22, task 2-2 (transient), LTspice netlist", asc22t),
    }
    for name, text in files.items():
        text.encode("ascii")                      # LTspice плохо переносит не-ASCII в файлах схем
        open(os.path.join(OUT, name), "w", encoding="ascii", newline="\r\n").write(text)
    return sorted(files)


if __name__ == "__main__":
    print("ВСЁ СОВПАДАЕТ" if check_all() else "ЕСТЬ РАСХОЖДЕНИЯ")
    print(write_files())
