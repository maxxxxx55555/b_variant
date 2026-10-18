# -*- coding: utf-8 -*-
"""Задание 2-1, вариант 7.
Переходный процесс после замыкания ключа, ток через L1,
классический метод. Python 3.13, NumPy."""
import numpy as np

# ---------- исходные данные ----------
V1, I1 = 218.0, 1.26                 # В, А (источники постоянные)
R1, R2, R3, R4, R5 = 62.0, 60.0, 79.0, 52.0, 94.0   # Ом
C1, L1 = 0.59e-6, 6.0e-3             # Ф, Гн

def dc_state(closed):
    """Режим постоянного тока (C1 - разрыв, L1 - перемычка).
    Узел 1 - общая точка R1, R2, V1, C1; узел 2 - общая точка
    R3, R4, R5; нижний провод - узел 0. Ветвь V1-R3 направлена
    от узла 1 к узлу 2, ветвь R2-L1-I1 вносит в узел 1 ток I1."""
    G1, G3 = 1 / R1, 1 / R3
    G4 = 1 / R4 if closed else 0.0       # ключ замкнут / разомкнут
    Y = np.array([[G1 + G3, -G3],
                  [-G3, G3 + G4]])
    J = np.array([I1 - G3 * V1, G3 * V1])
    p1, p2 = np.linalg.solve(Y, J)
    i3 = G3 * (p1 + V1 - p2)             # ток ветви V1-R3
    return p1, p2, i3

def initial_conditions():
    """До коммутации (ключ разомкнут): u_C(0-) = phi2 - phi1
    (плюс на обкладке, к которой подключён R5), i_L(0-) = I1."""
    p1, p2, _ = dc_state(False)
    return p1, p2, p2 - p1, I1

def forced():
    """Принуждённый режим после коммутации (ключ замкнут)."""
    p1, p2, i3 = dc_state(True)
    return p1, p2, i3, p2 - p1, I1       # ..., u_C пр, i_L пр

def free_process():
    """Свободный процесс: V1 - перемычка, I1 - обрыв.
    Z(p) = R5 + 1/(p C1) + R3 || (R1 + R4) = 0."""
    R_ab = R3 * (R1 + R4) / (R3 + R1 + R4)
    R_eq = R5 + R_ab
    tau = R_eq * C1
    return R_ab, R_eq, tau, -1 / tau     # корень p = -1/tau

def uc(t):
    """u_C(t) = u_пр + (u_C(0) - u_пр) e^{pt}, t >= 0."""
    u0 = initial_conditions()[2]
    up, p = forced()[3], free_process()[3]
    return up + (u0 - up) * np.exp(p * t)

def il(t):
    """i_L(t) = i_пр + (i_L(0) - i_пр) e^{pt}; i_пр = i_L(0) = I1,
    поэтому свободная составляющая равна нулю."""
    i0 = initial_conditions()[3]
    ip, p = forced()[4], free_process()[3]
    return ip + (i0 - ip) * np.exp(p * t)


# ---------- независимая проверка: численное решение схемы ----------
# Узлы: 0 - земля, 1 и 2 - узлы схемы, 3 - между C1 и R5, 4 - между
# I1 и L1, 5 - между L1 и R2, 6 - между V1 и R3, 7 - между R4 и
# ключом. Элемент: (тип, узел a, узел b, значение). У V и C плюс на
# узле a, ток источника тока I течёт внутри него от a к b.
NET = [("R", 1, 0, R1), ("R", 5, 1, R2), ("L", 4, 5, L1),
       ("I", 0, 4, I1), ("V", 6, 1, V1), ("R", 6, 2, R3),
       ("C", 3, 1, C1), ("R", 3, 2, R5), ("R", 2, 7, R4),
       ("S", 7, 0, None)]
NN = 7                                   # число узлов без земли

def mna(h=None, trap=True, closed=False, hist=None):
    """Модифицированные узловые уравнения. h=None - режим
    постоянного тока (C - разрыв, L - перемычка); иначе C и L
    заменены схемами замещения (метод трапеций или Эйлера),
    hist[k] = [u, i] - напряжение и ток элемента k на пред. шаге."""
    ext = [k for k, e in enumerate(NET) if e[0] == "V" or
           (e[0] == "S" and closed) or (e[0] == "L" and h is None)]
    n = NN + 1 + len(ext)                # строки: узлы и токи V
    A, b = np.zeros((n, n)), np.zeros(n)

    def g_stamp(a, c, g):                # проводимость между a и c
        A[a, a] += g; A[c, c] += g; A[a, c] -= g; A[c, a] -= g

    def j_stamp(a, c, j):                # ток j из узла a в узел c
        b[a] -= j; b[c] += j

    for k, (typ, a, c, val) in enumerate(NET):
        if typ == "R":
            g_stamp(a, c, 1 / val)
        elif typ == "I":
            j_stamp(a, c, val)
        elif typ == "C" and h:
            u, i = hist[k]
            g = (2 if trap else 1) * val / h
            g_stamp(a, c, g)
            j_stamp(c, a, g * u + (i if trap else 0.0))
        elif typ == "L" and h:
            u, i = hist[k]
            g = h / ((2 if trap else 1) * val)
            g_stamp(a, c, g)
            j_stamp(a, c, i + (g * u if trap else 0.0))
    for m, k in enumerate(ext, NN + 1):  # источники ЭДС, перемычки
        typ, a, c, val = NET[k]
        A[m, a] += 1; A[m, c] -= 1       # v_a - v_c = E
        A[a, m] += 1; A[c, m] -= 1       # ток x[m] течёт от a к c
        b[m] = val if typ == "V" else 0.0
    x = np.zeros(n)
    x[1:] = np.linalg.solve(A[1:, 1:], b[1:])   # земля: v0 = 0
    return x, ext

def transient(t_end=700e-6, h=0.1e-6):
    """Замыкание ключа в t = 0. Начальное состояние - режим
    постоянного тока при разомкнутом ключе. Первый шаг - метод
    Эйлера (разрыв токов), далее - метод трапеций."""
    x, ext = mna()
    kC = next(k for k, e in enumerate(NET) if e[0] == "C")
    kL = next(k for k, e in enumerate(NET) if e[0] == "L")
    hist = {kC: [x[3] - x[1], 0.0],
            kL: [0.0, x[NN + 1 + ext.index(kL)]]}
    t, u, i = [0.0], [hist[kC][0]], [hist[kL][1]]
    for s in range(int(round(t_end / h))):
        trap = s > 0
        x, _ = mna(h, trap, True, hist)
        for k in (kC, kL):
            _, a, c, val = NET[k]
            u0, i0 = hist[k]
            un = x[a] - x[c]
            if k == kC:
                g = (2 if trap else 1) * val / h
                hist[k] = [un, g * (un - u0) - (i0 if trap else 0.0)]
            else:
                g = h / ((2 if trap else 1) * val)
                hist[k] = [un, g * (un + (u0 if trap else 0.0)) + i0]
        t.append((s + 1) * h)
        u.append(hist[kC][0])
        i.append(hist[kL][1])
    return np.array(t), np.array(u), np.array(i)

if __name__ == "__main__":
    p1, p2, U0, IL0 = initial_conditions()
    print("Докоммутационный режим (ключ разомкнут):")
    print(f"  phi1 = {p1:.5f} В, phi2 = {p2:.5f} В")
    print(f"  u_C(0-) = {U0:.5f} В, i_L(0-) = {IL0:.5f} А")
    f1, f2, i3, Up, ILp = forced()
    print("Принуждённый режим (ключ замкнут):")
    print(f"  phi1 = {f1:.5f} В, phi2 = {f2:.5f} В, "
          f"I_V1 = {i3:.5f} А")
    print(f"  u_C пр = {Up:.5f} В, i_L пр = {ILp:.5f} А")
    R_ab, R_eq, tau, p = free_process()
    print(f"Свободный процесс: R3||(R1+R4) = {R_ab:.4f} Ом, "
          f"R_экв = {R_eq:.4f} Ом")
    print(f"  tau = {tau * 1e6:.4f} мкс, p = {p:.2f} 1/с")
    print(f"u_C(t) = {Up:.4f} + {U0 - Up:.4f}*exp({p:.1f}t), В")
    print(f"i_L(t) = {ILp:.4f} + {IL0 - ILp:.1f}*exp({p:.1f}t) "
          f"= {I1:.4f} А")
    print("\n t, мкс    u_C, В     i_L, А")
    for tk in (0, 50, 100, 200, 300, 400, 500, 600):
        print(f"{tk:6d} {uc(tk * 1e-6):10.4f} {il(tk * 1e-6):10.5f}")
    t, un, iln = transient()
    print("\nЧисленное решение схемы (метод трапеций, h = 0.1 мкс):")
    print(f"  max|u_C(числ.) - u_C(аналит.)| = "
          f"{np.abs(un - uc(t)).max():.3e} В")
    print(f"  max|i_L(числ.) - I1| = {np.abs(iln - I1).max():.3e} А")
