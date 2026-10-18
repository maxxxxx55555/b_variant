# -*- coding: utf-8 -*-
"""Задание 2-2, вариант 7.
Синусоидальный режим (f = 8 кГц): комплексные амплитуды токов
методом узловых потенциалов, показание амперметра, u_L3(t),
мощности ветви с V1. Python 3.13, NumPy."""
import numpy as np

# ---------- исходные данные ----------
# значения источников - амплитудные, начальные фазы равны нулю
f = 8.0e3
E1, E2, I1 = 141.0, 158.0, 1.99          # V1, V2 (В), I1 (А)
R1, R2, R3 = 60.0, 34.0, 55.0            # Ом
C1, C2, C3 = 0.84e-6, 0.21e-6, 0.77e-6   # Ф
L1, L2, L3 = 1.0e-3, 10.0e-3, 14.0e-3    # Гн
w = 2 * np.pi * f                        # рад/с

ZL = lambda L: 1j * w * L                # сопр. индуктивности
ZC = lambda C: 1 / (1j * w * C)          # сопр. ёмкости

# сопротивления ветвей (нумерация слева направо, сверху вниз)
Z1 = ZC(C3) + ZL(L3)       # C3 и L3 (ветвь 1-4)
Z2 = R3 + ZC(C2)           # C2 и R3 (ветвь 1-4)
Z3 = ZC(C1)                # C1 (ветвь 1-2)
Z4 = R1 + ZL(L1)           # L1 и R1 (ветвь 2-4)
Z5 = ZL(L2)                # L2 (ветвь 3-4 с V2)
BRANCHES = ["L3", "C2", "C1", "L1", "L2", "V1", "R2"]


def solve():
    """Узловые потенциалы, узел 2 - базисный (phi2 = 0);
    ветвь 2-3 содержит только V1, поэтому phi3 = E1.
    Возвращает потенциалы и токи ветвей."""
    Y1, Y2, Y3, Y4, Y5 = (1 / z for z in (Z1, Z2, Z3, Z4, Z5))
    Y = np.array([[Y1 + Y2 + Y3, -(Y1 + Y2)],
                  [-(Y1 + Y2), Y1 + Y2 + Y4 + Y5]], dtype=complex)
    J = np.array([0.0, Y5 * (E1 + E2) - I1], dtype=complex)
    p1, p4 = np.linalg.solve(Y, J)
    p2, p3 = 0j, complex(E1)
    I = {"L3": Y1 * (p1 - p4),        # 1 -> 4 (через C3 и L3)
         "C2": Y2 * (p1 - p4),        # 1 -> 4 (через C2 и R3)
         "C1": Y3 * (p1 - p2),        # 1 -> 2
         "L1": Y4 * (p2 - p4),        # 2 -> 4 (через L1 и R1)
         "L2": Y5 * (p3 + E2 - p4)}   # 3 -> 4 (через V2 и L2)
    I["V1"] = I["C1"] - I["L1"]       # 2 -> 3 (узел 2)
    I["R2"] = complex(I1)             # 4 -> 3 (источник тока)
    return (p1, p2, p3, p4), I, (Y, J)


def powers(phi, I):
    """Комплексные мощности S = 1/2 U I* (амплитудные значения)."""
    p1, p2, p3, p4 = phi
    S_V1 = 0.5 * E1 * np.conj(I["V1"])           # источник V1
    S_V2 = 0.5 * E2 * np.conj(I["L2"])           # источник V2
    U_I1 = p3 + R2 * I1 - p4                     # напряжение на I1
    S_I1 = 0.5 * U_I1 * I1
    Zs = {"L3": Z1, "C2": Z2, "C1": Z3, "L1": Z4, "L2": Z5, "R2": R2}
    S_load = sum(0.5 * Zs[k] * abs(I[k]) ** 2 for k in Zs)
    return S_V1, S_V2, S_I1, S_load, U_I1


def polar(z):
    return abs(z), np.degrees(np.angle(z))


if __name__ == "__main__":
    phi, I, (Y, J) = solve()
    print(f"w = {w:.3f} рад/с")
    for n, z in zip(("phi1", "phi2", "phi3", "phi4"), phi):
        m, a = polar(z)
        print(f"{n} = {z.real:9.4f}{z.imag:+9.4f}j В = "
              f"{m:8.4f} В, фаза {a:8.3f}°")
    print("\nКомплексные амплитуды токов ветвей:")
    for k in BRANCHES:
        m, a = polar(I[k])
        print(f"I_{k}: {I[k].real:9.5f}{I[k].imag:+9.5f}j А = "
              f"{m:.5f} А, фаза {a:8.3f}°, "
              f"действ. {m / np.sqrt(2):.5f} А")
    kcl = (abs(I["L3"] + I["C2"] + I["C1"]),
           abs(I["C1"] - I["L1"] - I["V1"]),
           abs(I["V1"] + I["R2"] - I["L2"]),
           abs(I["L3"] + I["C2"] + I["L1"] + I["L2"] - I["R2"]))
    print("Невязка 1-го закона Кирхгофа, узлы 1, 2, 3, 4 (А): "
          + ", ".join(f"{x:.1e}" for x in kcl))
    print(f"\nАмперметр в ветви R2 (действующее значение): "
          f"{abs(I['R2']) / np.sqrt(2):.5f} А")
    UL3 = ZL(L3) * I["L3"]
    m, a = polar(UL3)
    print(f"U_L3 = {UL3.real:.4f}{UL3.imag:+.4f}j = "
          f"{m:.4f} В, фаза {a:.3f}°")
    print(f"u_L3(t) = {m:.3f}*sin(2*pi*{f:.0f}*t + {a:.3f}°), В")
    S_V1, S_V2, S_I1, S_load, U_I1 = powers(phi, I)
    print(f"\nВетвь с V1: S = {S_V1.real:.4f}{S_V1.imag:+.4f}j ВА, "
          f"|S| = {abs(S_V1):.4f} ВА,\n"
          f"            P = {S_V1.real:.4f} Вт, "
          f"Q = {S_V1.imag:.4f} вар")
    print(f"Баланс: источники {S_V1 + S_V2 + S_I1:.4f}, "
          f"приёмники {S_load:.4f}")
