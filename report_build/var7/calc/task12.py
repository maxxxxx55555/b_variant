# -*- coding: utf-8 -*-
"""Задание 1-2, вариант 7.
Цепь постоянного тока: законы Кирхгофа, контурные токи,
узловые потенциалы. Python 3.13, NumPy."""
import numpy as np

# ---------- исходные данные ----------
V1, V2 = 306.0, 115.0      # ЭДС источников напряжения, В
I1 = 2.88                  # ток источника тока, А
R1, R2, R3, R4, R5, R6 = 46.0, 23.0, 91.0, 36.0, 33.0, 18.0  # Ом

NAMES = ["R1", "R3", "R4", "R5", "R6"]   # порядок неизвестных токов


def kirchhoff():
    """Законы Кирхгофа: A x = b,
    x = [I_R1, I_R3, I_R4, I_R5, I_R6]."""
    A = np.array([
        [1.0, 1.0, 1.0, 0.0, 1.0],     # 1-й закон, узел 1
        [0.0, 0.0, 1.0, -1.0, 1.0],    # 1-й закон, узел 2
        [0.0, 0.0, -R4, 0.0, R6],      # 2-й закон, контур K1
        [-R1, 0.0, R4, R5, 0.0],       # 2-й закон, контур K2
        [R1, -R3, 0.0, 0.0, 0.0],      # 2-й закон, контур K3
    ])
    b = np.array([I1, 0.0, V2, 0.0, -V1])
    return np.linalg.solve(A, b), A, b


def mesh():
    """Контурные токи: R_K * I_K = E_K.
    Неизвестны I_K1, I_K2, I_K3; контурный ток I_K4 = I1 задан."""
    RK = np.array([[R4 + R6, -R4, 0.0],
                   [-R4, R1 + R4 + R5, -R1],
                   [0.0, -R1, R1 + R3]])
    EK = np.array([V2, 0.0, R3 * I1 - V1])
    K1, K2, K3 = np.linalg.solve(RK, EK)
    x = np.array([K3 - K2, I1 - K3, K2 - K1, K2, K1])  # токи ветвей
    return x, np.array([K1, K2, K3]), RK, EK


def nodal():
    """Узловые потенциалы: Y * phi = J,
    узел 3 базисный (phi3 = 0)."""
    G1, G3, G4, G5, G6 = 1/R1, 1/R3, 1/R4, 1/R5, 1/R6
    I2, I3 = V2 / R6, V1 / R3   # эквивалентные источники тока
    Y = np.array([[G1 + G3 + G4 + G6, -(G4 + G6)],
                  [-(G4 + G6), G4 + G5 + G6]])
    J = np.array([I1 - I2 - I3, I2])
    phi1, phi2 = np.linalg.solve(Y, J)
    x = np.array([G1 * phi1, G3 * phi1 + I3, G4 * (phi1 - phi2),
                  G5 * phi2, G6 * (phi1 - phi2) + I2])
    return x, np.array([phi1, phi2]), Y, J


def voltages_and_powers(x, phi1):
    """Напряжения и мощности. x = [I_R1, I_R3, I_R4, I_R5, I_R6]."""
    I = dict(zip(NAMES, x))
    I["R2"] = I1
    R = {"R1": R1, "R2": R2, "R3": R3, "R4": R4, "R5": R5, "R6": R6}
    U = {k: I[k] * R[k] for k in R}           # U = I * R
    P = {k: I[k] ** 2 * R[k] for k in R}      # мощность приёмников
    U_I1 = phi1 + I1 * R2                     # напряжение на I1
    P_src = {"V1": V1 * I["R3"], "V2": V2 * I["R6"],
             "I1": U_I1 * I1}
    return I, U, P, U_I1, P_src


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True, linewidth=110)
    xk, A, b = kirchhoff()
    xm, Ik, RK, EK = mesh()
    xn, phi, Y, J = nodal()

    print("Метод 1. Законы Кирхгофа, матрица A и вектор b:")
    print(A)
    print(b)
    print("Метод 2. Контурные токи I_K1..I_K3, А:", Ik)
    print("Метод 3. Потенциалы phi1, phi2 (phi3 = 0), В:", phi)
    print()
    print(f"{'ветвь':6s}{'Кирхгоф':>14s}{'контурные':>14s}"
          f"{'узловые':>14s}   (токи, А)")
    for n, a, c, d in zip(NAMES, xk, xm, xn):
        print(f"I_{n:4s}{a:14.6f}{c:14.6f}{d:14.6f}")
    print("max|Кирхгоф-контурные| =", np.abs(xk - xm).max())
    print("max|Кирхгоф-узловые|   =", np.abs(xk - xn).max())

    I, U, P, U_I1, P_src = voltages_and_powers(xn, phi[0])
    print("\nНапряжения и мощности:")
    for k in ["R1", "R2", "R3", "R4", "R5", "R6"]:
        print(f"{k}: I = {I[k]:9.5f} А, U = {U[k]:9.4f} В, "
              f"P = {P[k]:9.4f} Вт")
    print(f"I1: U = {U_I1:.4f} В;  V1: I = {I['R3']:.5f} А;  "
          f"V2: I = {I['R6']:.5f} А")
    print(f"Баланс мощностей: источники "
          f"{sum(P_src.values()):.6f} Вт, "
          f"приёмники {sum(P.values()):.6f} Вт")
