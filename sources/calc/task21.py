# -*- coding: utf-8 -*-
"""Задание 2-1, вариант 22.
Переходный процесс после размыкания ключа, напряжение на C1,
классический метод. Python 3.13, NumPy, SciPy."""
import numpy as np
from scipy.integrate import solve_ivp

# ---------- исходные данные ----------
V1, I1 = 309.0, 1.47                  # В, А (источники постоянные)
R1, R2, R3, R4, R5 = 100.0, 77.0, 38.0, 36.0, 17.0   # Ом
C1, L1 = 1.0e-6, 5.0e-3               # Ф, Гн


def initial_conditions():
    """Докоммутационный режим: ключ замкнут, цепь постоянного тока,
    C1 - разрыв, L1 - перемычка. Узловое уравнение для узла 1
    (узел 0 - нижний провод):
    I1 = (phi1 + V1)/R2 + phi1/(R3 + R4)."""
    phi1 = (I1 - V1 / R2) / (1 / R2 + 1 / (R3 + R4))
    phi2 = phi1 * R4 / (R3 + R4)      # делитель R3-R4
    return phi1, phi2                 # u_C(0-) = phi2, i_L(0-) = 0


def parameters():
    """Параметры свободного процесса
    в контуре R6 = R4 + R5, L1, C1."""
    R6 = R4 + R5
    alpha = R6 / (2 * L1)             # коэффициент затухания, 1/с
    w0 = 1 / np.sqrt(L1 * C1)         # резонансная частота, рад/с
    wd = np.sqrt(w0 ** 2 - alpha ** 2)  # частота свободных колебаний
    R_kr = 2 * np.sqrt(L1 / C1)       # критическое сопротивление, Ом
    return R6, alpha, w0, wd, R_kr


def uc_analytic(t, U0):
    """u_C(t) = U0 e^{-alpha t} (cos wd t + alpha/wd sin wd t)."""
    _, a, _, w, _ = parameters()
    return U0 * np.exp(-a * t) * (np.cos(w * t)
                                  + a / w * np.sin(w * t))


def il_analytic(t, U0):
    """i_L(t) = C du_C/dt = -U0/(wd L) e^{-alpha t} sin wd t."""
    _, a, _, w, _ = parameters()
    return -U0 / (w * L1) * np.exp(-a * t) * np.sin(w * t)


def uc_numeric(t, U0):
    """Независимая проверка: численное решение системы
    L di/dt + R6 i + u = 0,  du/dt = i/C."""
    R6 = parameters()[0]
    f = lambda _, y: [y[1] / C1, -(y[0] + R6 * y[1]) / L1]
    sol = solve_ivp(f, (0, t[-1]), [U0, 0.0], t_eval=t,
                    rtol=1e-11, atol=1e-12, method="DOP853")
    return sol.y[0], sol.y[1]


if __name__ == "__main__":
    phi1, U0 = initial_conditions()
    R6, alpha, w0, wd, R_kr = parameters()
    print(f"Докоммутационный режим: phi1 = {phi1:.5f} В, "
          f"u_C(0-) = {U0:.5f} В, i_L(0-) = 0")
    print(f"R6 = R4 + R5 = {R6:.1f} Ом; R_кр = 2*sqrt(L/C) = "
          f"{R_kr:.2f} Ом -> колебательный режим")
    print(f"alpha = {alpha:.2f} 1/с, w0 = {w0:.2f} рад/с, "
          f"w_св = {wd:.3f} рад/с")
    amp = U0 * w0 / wd
    psi = np.arctan(wd / alpha)
    print(f"u_C(t) = {U0:.4f}*exp(-{alpha:.0f}t)*(cos({wd:.1f}t)"
          f"+{alpha / wd:.5f}*sin({wd:.1f}t)), В")
    print(f"       = {amp:.4f}*exp(-{alpha:.0f}t)*"
          f"sin({wd:.1f}t + {psi:.5f}), В")
    print(f"i_L(t) = {-U0 / (wd * L1):.5f}*exp(-{alpha:.0f}t)*"
          f"sin({wd:.1f}t), А")

    t = np.linspace(0, 1.5e-3, 3001)
    ua = uc_analytic(t, U0)
    un, _ = uc_numeric(t, U0)
    print(f"max|u_C(аналит.) - u_C(числ.)| = "
          f"{np.abs(ua - un).max():.3e} В")
    print("\n t, мкс    u_C, В     i_L, А")
    for tk in (0, 50, 100, 200, 300, 400, 600, 800, 1000):
        print(f"{tk:6d} {uc_analytic(tk * 1e-6, U0):10.4f} "
              f"{il_analytic(tk * 1e-6, U0):10.5f}")
    k = ua.argmax()
    print(f"Первый максимум u_C: {ua[k]:.4f} В "
          f"при t = {t[k] * 1e6:.1f} мкс")
