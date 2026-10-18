# -*- coding: utf-8 -*-
"""Задание 2-2, вариант 22.
Синусоидальный режим (f = 1 кГц): комплексные амплитуды токов
методом узловых потенциалов, показание амперметра, u_L3(t),
мощности ветви с V1. Python 3.13, NumPy."""
import numpy as np

# ---------- исходные данные ----------
# значения источников - амплитудные, начальные фазы равны нулю
f = 1.0e3
E1, E2, I1 = 130.0, 284.0, 0.49          # V1, V2 (В), I1 (А)
R1, R2, R3 = 23.0, 6.0, 94.0             # Ом
C1, C2, C3 = 0.83e-6, 0.71e-6, 0.52e-6   # Ф
L1, L2, L3 = 6.0e-3, 10.0e-3, 12.0e-3    # Гн
w = 2 * np.pi * f                        # рад/с

ZL = lambda L: 1j * w * L                # сопр. индуктивности
ZC = lambda C: 1 / (1j * w * C)          # сопр. ёмкости

# сопротивления ветвей (нумерация слева направо, сверху вниз)
Z1 = R1                    # R1
Z2 = ZL(L1)                # L1 (ветвь с V1)
Z3 = ZL(L2) + ZC(C2)       # L2 и C2 (ветвь с V2)
Z4 = ZC(C1)                # C1
Z6 = ZC(C3)                # C3
Z7 = R3 + ZL(L3)           # R3 и L3
BRANCHES = ["R1", "L1", "L2", "C1", "R2", "C3", "L3"]


def solve():
    """Узловые потенциалы, узел 4 - базисный.
    Возвращает потенциалы и токи ветвей."""
    Y1, Y2, Y3, Y4, Y6, Y7 = (1 / z for z in
                              (Z1, Z2, Z3, Z4, Z6, Z7))
    Y = np.array([[Y1 + Y2 + Y3, -Y3, -(Y1 + Y2)],
                  [-Y3, Y3 + Y6 + Y7, 0.0],
                  [-(Y1 + Y2), 0.0, Y1 + Y2 + Y4]], dtype=complex)
    J = np.array([-Y2 * E1 - Y3 * E2, I1 + Y3 * E2, Y2 * E1],
                 dtype=complex)
    p1, p2, p3 = np.linalg.solve(Y, J)
    I = {"R1": Y1 * (p1 - p3),        # 1 -> 3
         "L1": Y2 * (p1 - p3 + E1),   # 1 -> 3 (через L1 и V1)
         "L2": Y3 * (p1 - p2 + E2),   # 1 -> 2 (через V2, L2, C2)
         "C1": Y4 * p3,               # 3 -> 4
         "R2": complex(I1),           # 4 -> 2 (источник тока)
         "C3": Y6 * p2,               # 2 -> 4
         "L3": Y7 * p2}               # 2 -> 4 (через R3 и L3)
    return (p1, p2, p3), I, (Y, J)


def powers(phi, I):
    """Комплексные мощности S = 1/2 U I* (амплитудные значения)."""
    p1, p2, p3 = phi
    S_V1 = 0.5 * E1 * np.conj(I["L1"])           # источник V1
    S_V2 = 0.5 * E2 * np.conj(I["L2"])           # источник V2
    U_I1 = p2 + R2 * I1                          # напряжение на I1
    S_I1 = 0.5 * U_I1 * I1
    S_br = 0.5 * (p1 - p3) * np.conj(I["L1"])    # ветвь V1-L1
    Zs = {"R1": R1, "L1": Z2, "L2": Z3, "C1": Z4,
          "R2": R2, "C3": Z6, "L3": Z7}
    S_load = sum(0.5 * Zs[k] * abs(I[k]) ** 2 for k in Zs)
    return S_V1, S_V2, S_I1, S_br, S_load, U_I1


def polar(z):
    return abs(z), np.degrees(np.angle(z))


if __name__ == "__main__":
    phi, I, (Y, J) = solve()
    print(f"w = {w:.3f} рад/с")
    for n, z in zip(("phi1", "phi2", "phi3"), phi):
        m, a = polar(z)
        print(f"{n} = {z.real:9.4f}{z.imag:+9.4f}j В = "
              f"{m:8.4f} В, фаза {a:8.3f}°")
    print("\nКомплексные амплитуды токов ветвей:")
    for k in BRANCHES:
        m, a = polar(I[k])
        print(f"I_{k}: {I[k].real:9.5f}{I[k].imag:+9.5f}j А = "
              f"{m:.5f} А, фаза {a:8.3f}°, "
              f"действ. {m / np.sqrt(2):.5f} А")
    kcl = (abs(I["R1"] + I["L1"] + I["L2"]),
           abs(I["L2"] + I["R2"] - I["C3"] - I["L3"]),
           abs(I["R1"] + I["L1"] - I["C1"]))
    print("Невязка 1-го закона Кирхгофа, узлы 1, 2, 3 (А): "
          + ", ".join(f"{x:.1e}" for x in kcl))
    print(f"\nАмперметр в ветви R2 (действующее значение): "
          f"{abs(I['R2']) / np.sqrt(2):.5f} А")
    UL3 = ZL(L3) * I["L3"]
    m, a = polar(UL3)
    print(f"U_L3 = {UL3.real:.4f}{UL3.imag:+.4f}j = "
          f"{m:.4f} В, фаза {a:.3f}°")
    print(f"u_L3(t) = {m:.3f}*sin(2*pi*{f:.0f}*t + {a:.3f}°), В")
    S_V1, S_V2, S_I1, S_br, S_load, U_I1 = powers(phi, I)
    print(f"\nИсточник V1: S = {S_V1.real:.4f}{S_V1.imag:+.4f}j ВА, "
          f"|S| = {abs(S_V1):.4f} ВА, P = {S_V1.real:.4f} Вт, "
          f"Q = {S_V1.imag:.4f} вар")
    print(f"Ветвь V1-L1 на выводах (отдаёт в цепь): "
          f"P = {-S_br.real:.4f} Вт, Q = {-S_br.imag:.4f} вар, "
          f"|S| = {abs(S_br):.4f} ВА")
    print(f"Баланс: источники {S_V1 + S_V2 + S_I1:.4f}, "
          f"приёмники {S_load:.4f}")
