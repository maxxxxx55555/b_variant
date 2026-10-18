# -*- coding: utf-8 -*-
"""Памятка для проверки ДЗ1 (вариант 22) в Micro-Cap: номиналы, настройки анализов,
ожидаемые значения и список скриншотов. Значения берутся из calc/*.py."""
import os, sys, html as H
import numpy as np
from report_lib import f, to_pdf, W, MINUS

sys.path.insert(0, W + "calc")
import task12, task21, task22

OUT_HTML = W + "report/memo.html"
OUT_PDF = W + "report/MicroCap_pamyatka_var22.pdf"
os.makedirs(W + "report", exist_ok=True)
if not os.path.exists(W + "report/figs"):
    os.symlink(W + "figs", W + "report/figs")

CSS = """
@page { size: A4; margin: 14mm 14mm 14mm 18mm; }
html { font-size: 11.5pt; }
body { font-family: "Liberation Serif", "Times New Roman", serif; line-height: 1.38; color: #111; margin: 0; }
h1 { font-size: 18pt; margin: 0 0 2mm; }
h2 { font-size: 14pt; margin: 7mm 0 2mm; border-bottom: 0.8pt solid #444; padding-bottom: 1mm; break-after: avoid; }
h3 { font-size: 12pt; margin: 4mm 0 1mm; break-after: avoid; }
p { margin: 0 0 2.2mm; text-align: justify; }
.sub { color: #444; margin-bottom: 4mm; }
.note { border: 0.8pt solid #b3300f; background: #fbf3ef; padding: 2.5mm 3.5mm; margin: 3mm 0; break-inside: avoid; }
.ok { border: 0.8pt solid #2e8b57; background: #f1f8f4; padding: 2.5mm 3.5mm; margin: 3mm 0; break-inside: avoid; }
table { border-collapse: collapse; margin: 2mm 0 3mm; break-inside: avoid; font-size: 10.5pt; }
th, td { border: 0.7pt solid #555; padding: 0.9mm 2.2mm; text-align: center; vertical-align: middle; }
td.l, th.l { text-align: left; }
th { background: #eceff4; font-weight: 700; }
figure { margin: 2mm 0 3mm; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; }
figcaption { font-size: 10pt; color: #333; margin-top: 1mm; }
ul, ol { margin: 0 0 2.5mm; padding-left: 6mm; }
li { margin-bottom: 1mm; }
code, .m { font-family: "Liberation Mono", "DejaVu Sans Mono", monospace; font-size: 10pt; background: #f1f1f1; padding: 0 1mm; }
.cols { display: flex; gap: 6mm; align-items: flex-start; }
.cols > div { flex: 1; }
"""


def tbl(header, rows, left=()):
    h = "".join(f'<th class="l">{c}</th>' if i in left else f"<th>{c}</th>" for i, c in enumerate(header))
    b = ""
    for r in rows:
        b += "<tr>" + "".join(f'<td class="l">{c}</td>' if i in left else f"<td>{c}</td>" for i, c in enumerate(r)) + "</tr>"
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


def fig(name, cap, width="130mm"):
    return f'<figure><img src="figs/{name}" style="width:{width}"><figcaption>{cap}</figcaption></figure>'


def main():
    # ------------------------------------------------------------ данные расчёта
    xn, phi, _, _ = task12.nodal()
    I12, U12, P12, U_I1, _ = task12.voltages_and_powers(xn, phi[0])
    phi1_21, U0 = task21.initial_conditions()
    R6, al, w0, wd, _ = task21.parameters()
    T = 2 * np.pi / wd
    tt = np.linspace(0, 1.5e-3, 30001)
    uc = task21.uc_analytic(tt, U0)
    il = task21.il_analytic(tt, U0)
    kmax, kil = uc.argmax(), np.abs(il).argmax()
    phi22, I22, _ = task22.solve()
    UL3 = task22.ZL(task22.L3) * I22["L3"]
    S_V1, S_V2, S_I1, S_br, S_load, _ = task22.powers(phi22, I22)
    sq2 = np.sqrt(2)

    out = []
    A = out.append
    A("<h1>Micro-Cap: что собрать и что прислать</h1>")
    A('<div class="sub">ДЗ1, модуль 1 · вариант 22 · БИТ253, Чигиринцев Максим · задания 1-2, 2-1, 2-2</div>')

    A('<div class="note"><b>Почему эта памятка.</b> Micro-Cap — программа для Windows. В моём рабочем окружении её нет '
      '(сайт производителя недоступен из-за сетевых ограничений), поэтому настоящих скриншотов Micro-Cap я получить не '
      'могу, а имитировать их не буду: в отчёте должны быть ваши реальные результаты. Ниже — всё, что нужно, чтобы '
      'собрать три схемы за 20–30 минут: номиналы, ориентация источников, настройки анализов и числа, которые должны '
      'получиться (они рассчитаны в Python и независимо проверены в ngspice). <b>Пришлите скриншоты — я перепишу '
      'разделы «Проверка в SPICE-симуляторе» под Micro-Cap и соберу итоговый PDF.</b></div>')

    A("<h2>1. Что прислать мне</h2>")
    A(tbl(["№", "Задание", "Что должно быть на скриншоте"], [
        ["1", "1-2", "Схема в режиме <b>Dynamic DC</b>: видны потенциалы узлов и токи ветвей (кнопки Node Voltages и Currents)"],
        ["2", "1-2", "Окно <b>DC Analysis</b>: токи I(R1), I(R3), I(R4), I(R5), I(R6) в зависимости от ЭДС V1 (0…400 В)"],
        ["3", "2-1", "Схема с ключом, номиналами и номерами узлов"],
        ["4", "2-1", "Окно <b>Transient</b>: u<sub>C</sub>(t) и i<sub>L</sub>(t) на интервале 0…1,7 мс"],
        ["5", "2-2", "Схема задания 2-2: источники, номиналы, номера узлов"],
        ["6", "2-2", "<b>Dynamic AC</b> при 1 кГц: амплитуды и фазы токов ветвей (кнопка Currents)"],
        ["7", "2-2", "Окно <b>Transient</b>: u<sub>L3</sub>(t) и токи на интервале 20…24 мс, а также RMS тока в R2"],
    ], left=(2,)))
    A("<p>Кроме скриншотов напишите <b>версию Micro-Cap</b> (Help → About). Если можно — приложите сами файлы схем "
      "(<span class='m'>.cir</span> Micro-Cap) и числа текстом (Numeric Output): так я не ошибусь при чтении "
      "значений с картинок. Файлы <span class='m'>sources/spice/*.cir</span> из репозитория — описания для ngspice, "
      "а не схемы Micro-Cap, в Micro-Cap они не открываются.</p>")

    A("<h2>2. Общие замечания</h2>")
    A("<ul>"
      "<li>Названия пунктов меню даны по Micro-Cap 11/12, в вашей версии они могут слегка отличаться.</li>"
      "<li>Нужен компонент <b>Ground</b> в базисном узле (на рисунках ниже он отмечен).</li>"
      "<li>Включите отображение номеров узлов (кнопка Node Numbers), чтобы они попали на скриншот.</li>"
      "<li>В Micro-Cap положительным считается ток от первого вывода компонента ко второму, поэтому знак тока "
      "зависит от поворота компонента. Сверяйте модуль и направление по моим рисункам, а правильность сборки — по "
      "<b>контрольным цифрам</b> (потенциалы узлов).</li>"
      "<li>Источники ЭДС — <b>Battery</b> (плюс — длинная пластина), источник тока — <b>Isource</b>. Если "
      "контрольные цифры вышли с обратным знаком, поверните соответствующий источник на 180°.</li>"
      "</ul>")

    # ------------------------------------------------------------ 1-2
    A("<h2>3. Задание 1-2: цепь постоянного тока</h2>")
    A(fig("fig12_currents.png", "Рисунок 1 — Схема задания 1-2: узлы и положительные направления токов (как в отчёте)", "118mm"))
    A(tbl(["V1, В", "V2, В", "I1, А", "R1, Ом", "R2, Ом", "R3, Ом", "R4, Ом", "R5, Ом", "R6, Ом"],
          [[f(task12.V1, 0), f(task12.V2, 0), f(task12.I1, 2), f(task12.R1, 0), f(task12.R2, 0), f(task12.R3, 0),
            f(task12.R4, 0), f(task12.R5, 0), f(task12.R6, 0)]]))
    A("<h3>Как собрать</h3><ul>"
      "<li><b>V2</b> (Battery): «+» направлен к R6, то есть слева направо в верхней ветви.</li>"
      "<li><b>V1</b> (Battery): «+» внизу — стрелка ЭДС направлена вниз, к резистору R5.</li>"
      "<li><b>I1</b> (Isource): ток течёт снизу вверх через R2 в узел 1.</li>"
      "<li>Ground — в узле 3 (нижняя шина).</li></ul>")
    A(f'<div class="ok"><b>Контрольная цифра:</b> потенциал узла 1 равен {f(phi[0], 3)} В, узла 2 — {f(phi[1], 3)} В '
      '(относительно узла 3).</div>')
    A("<h3>Анализ A — Dynamic DC (скриншот № 1)</h3>")
    A("<p>Analysis → Dynamic DC; на схеме включите показ потенциалов узлов и токов ветвей. Ожидаемые значения:</p>")
    rows = []
    for k, d in (("R1", "сверху вниз, 1 → 3"), ("R2", "снизу вверх (задан I1)"), ("R3", "сверху вниз, 1 → 3"),
                 ("R4", "слева направо, 1 → 2"), ("R5", "по рисунку 1 (от узла 2 к узлу 3 через V1)"),
                 ("R6", "слева направо, 1 → 2")):
        rows.append([f"I<sub>{k}</sub>", f(I12[k], 5), d, f(U12[k], 4)])
    A(tbl(["Ток", "Значение, А", "Направление", "U на резисторе, В"], rows, left=(2,)))
    A(f"<p>Напряжение на источнике тока U<sub>I1</sub> (от нижнего вывода к верхнему) = {f(U_I1, 4)} В.</p>")
    A("<h3>Анализ B — DC (скриншот № 2)</h3>")
    A("<p>Analysis → DC. Переменная: Variable 1 — компонент V1 (Battery), метод Linear, диапазон 400,0 (от 0 до 400 В), "
      "шаг 5 В. В таблице графиков задайте Y-выражения I(R1), I(R3), I(R4), I(R5), I(R6) (можно на одном графике). "
      f"Графики должны быть прямыми линиями; при V1 = {f(task12.V1, 0)} В значения совпадают с таблицей выше "
      "(проверьте курсором).</p>")

    # ------------------------------------------------------------ 2-1
    A("<h2>4. Задание 2-1: переходный процесс (найти напряжение на ёмкости)</h2>")
    A(fig("fig21_nodes.png", "Рисунок 2 — Схема задания 2-1 (узлы и полярность u<sub>C</sub>)", "112mm"))
    A(tbl(["V1, В", "I1, А", "R1, Ом", "R2, Ом", "R3, Ом", "R4, Ом", "R5, Ом", "C1, мкФ", "L1, мГн"],
          [[f(task21.V1, 0), f(task21.I1, 2), f(task21.R1, 0), f(task21.R2, 0), f(task21.R3, 0), f(task21.R4, 0),
            f(task21.R5, 0), f(task21.C1 * 1e6, 1), f(task21.L1 * 1e3, 0)]]))
    A("<h3>Как собрать</h3><ul>"
      "<li><b>V1</b> (Battery): «+» внизу (стрелка ЭДС вниз), <b>I1</b> (Isource): ток снизу вверх. Ground — в "
      "нижнем проводе.</li>"
      "<li><b>Ключ</b> — компонент Switch (ключ, управляемый напряжением), включённый последовательно с R3, между R3 и "
      "узлом 2, как на рисунке. "
      "Управляющее напряжение — Pulse Source: 1 В до момента t<sub>0</sub> = 200 мкс и 0 В после него (фронт около "
      "1 нс); пороги ключа между 0 и 1 В (например, 0,5 В). Сопротивление включённого ключа ≈ 1 мОм, "
      "выключенного ≥ 1 ГОм. До t<sub>0</sub> ключ замкнут, после — разомкнут.</li>"
      "<li>Напряжение u<sub>C</sub> — потенциал узла между R5 и C1 (верхняя обкладка) относительно земли.</li></ul>")
    A(f'<div class="ok"><b>Контрольные цифры (режим до коммутации, Operating Point):</b> потенциал узла 1 = '
      f'{f(phi1_21, 3)} В, напряжение на конденсаторе u<sub>C</sub>(0<sub>−</sub>) = {f(U0, 3)} В, ток катушки = 0.</div>')
    A("<h3>Анализ — Transient (скриншот № 4)</h3>")
    A("<p>Analysis → Transient: Time Range = <span class='m'>1.7m</span>, Maximum Time Step = <span class='m'>0.5u</span> "
      "(или меньше), Operating Point включён. Графики: u<sub>C</sub> (узел между R5 и C1 или V(C1)) и "
      "<span class='m'>I(L1)</span>. До 200 мкс значения постоянны, после — затухающие колебания:</p>")
    A(f"<p>α = {f(al, 0)} 1/с, ω<sub>св</sub> = {f(wd, 0)} рад/с (период {f(T * 1e6, 1)} мкс); первый максимум "
      f"u<sub>C</sub> = {f(uc[kmax], 3)} В при t − t<sub>0</sub> = {f(tt[kmax] * 1e6, 1)} мкс; максимальный ток катушки "
      f"{f(il[kil], 4)} А при t − t<sub>0</sub> = {f(tt[kil] * 1e6, 1)} мкс.</p>")
    rows = [[str(t), f(task21.uc_analytic(t * 1e-6, U0), 3), f(task21.il_analytic(t * 1e-6, U0), 4)]
            for t in (0, 50, 100, 200, 300, 400, 600, 800, 1000)]
    A(tbl(["t − t<sub>0</sub>, мкс", "u<sub>C</sub>, В", "i<sub>L</sub>, А"], rows))
    A("<p>Значения можно снять курсором (Scope → Cursor Mode); в таблице t отсчитывается от момента размыкания "
      "ключа (в Micro-Cap это 200 мкс от начала расчёта).</p>")

    # ------------------------------------------------------------ 2-2
    A("<h2>5. Задание 2-2: синусоидальный режим, f = 1 кГц</h2>")
    A(fig("fig22_currents.png", "Рисунок 3 — Схема задания 2-2: узлы и положительные направления токов", "125mm"))
    A(tbl(["Величина", "Значение", "Величина", "Значение"], [
        ["V1, В (амплитуда)", f(task22.E1, 0), "C2, мкФ", f(task22.C2 * 1e6, 2)],
        ["V2, В (амплитуда)", f(task22.E2, 0), "C3, мкФ", f(task22.C3 * 1e6, 2)],
        ["I1, А (амплитуда)", f(task22.I1, 2), "L1, мГн", f(task22.L1 * 1e3, 0)],
        ["R1, Ом", f(task22.R1, 0), "L2, мГн", f(task22.L2 * 1e3, 0)],
        ["R2, Ом", f(task22.R2, 0), "L3, мГн", f(task22.L3 * 1e3, 0)],
        ["R3, Ом", f(task22.R3, 0), "f, кГц", "1"],
        ["C1, мкФ", f(task22.C1 * 1e6, 2), "", ""]]))
    A("<h3>Как собрать</h3><ul>"
      "<li>Источники V1, V2, I1 — синусоидальные (Sine Source: напряжение, Isource с синусоидальным заданием), "
      "частота 1 кГц, <b>амплитуды 130 В, 284 В, 0,49 А</b>, начальные фазы 0. Для анализа AC у источников нужна "
      "AC-амплитуда, равная той же величине.</li>"
      "<li>Полярность: V1 — «+» внизу (стрелка ЭДС вниз), V2 — «+» справа (стрелка ЭДС вправо, к ветви L2, C2), "
      "I1 — ток снизу вверх через R2.</li>"
      "<li>Ground — в узле 4 (правая нижняя точка). Ток в ветви с R2 («показание амперметра») берётся как "
      "ток компонента R2: <span class='m'>I(R2)</span>.</li></ul>")
    A("<h3>Анализ A — Dynamic AC при 1 кГц (скриншот № 6)</h3>")
    A("<p>Analysis → Dynamic AC, частота 1 kHz; на схеме включите показ токов (амплитуда и фаза в градусах). "
      "Ожидаемые комплексные амплитуды токов ветвей (направления — по рисунку 3):</p>")
    names = {"R1": "R1 (сверху вниз)", "L1": "L1, V1 (сверху вниз)", "L2": "L2, C2, V2 (слева направо)",
             "C1": "C1 (слева направо)", "R2": "R2, I1 (снизу вверх)", "C3": "C3 (сверху вниз)",
             "L3": "R3, L3 (сверху вниз)"}
    rows = []
    for k in task22.BRANCHES:
        z = I22[k]
        rows.append([f"I<sub>{k}</sub>", names[k], f(abs(z), 4), f(np.degrees(np.angle(z)), 2), f(abs(z) / sq2, 4)])
    A(tbl(["Ток", "Ветвь", "Амплитуда, А", "Фаза, °", "Действующее, А"], rows, left=(1,)))
    A(f'<div class="ok"><b>Контрольная цифра:</b> амплитуда напряжения узла 1 относительно узла 4 равна '
      f'{f(abs(phi22[0]), 3)} В, фаза {f(np.degrees(np.angle(phi22[0])), 2)}°.</div>')
    A("<h3>Анализ B — Transient (скриншот № 7)</h3>")
    A("<p>Analysis → Transient: Time Range = <span class='m'>24m</span>, Maximum Time Step = <span class='m'>2u</span>; "
      "окно X Range — 20m…24m (переходный процесс к этому времени закончился). Графики: напряжение на L3 "
      "(<span class='m'>V(L3)</span>), токи ветвей, а также <span class='m'>RMS(I(R2))</span> — показание амперметра. "
      "Ожидаемо:</p>")
    A("<ul>"
      f"<li>напряжение на L3: амплитуда {f(abs(UL3), 3)} В, фаза {f(np.degrees(np.angle(UL3)), 2)}°, то есть "
      f"u<sub>L3</sub>(t) = {f(abs(UL3), 2)}·sin(2π·1000·t + {f(np.degrees(np.angle(UL3)), 2)}°) В;</li>"
      f"<li>показание амперметра в ветви с R2: {f(task22.I1 / sq2, 4)} А (действующее значение);</li>"
      f"<li>мощности ветви с V1 (источник): P = {f(S_V1.real, 3)} Вт, Q = {f(S_V1.imag, 3)} вар, "
      f"|S| = {f(abs(S_V1), 3)} В·А; на выводах ветви V1–L1: P = {f(-S_br.real, 3)} Вт, Q = {f(-S_br.imag, 3)} вар "
      "(проверка в Micro-Cap необязательна — достаточно токов и напряжений).</li></ul>")

    A("<h2>6. Что изменится в отчёте</h2>")
    A("<ul>"
      "<li>Разделы 1.4, 2.4, 3.4 («Проверка в SPICE-симуляторе») будут переписаны под Micro-Cap: ваши скриншоты, "
      "таблицы «расчёт — Micro-Cap», выводы.</li>"
      "<li>Приложение Б (описания схем для ngspice) заменится таблицами параметров схем и настроек анализов "
      "Micro-Cap; на титульном листе и в тексте будет указано, что проверка выполнена в Micro-Cap "
      "(с вашей версией).</li>"
      "<li>Аналитическая часть и расчёты в Python остаются без изменений.</li></ul>")
    A("<p>Если что-то не получилось — присылайте как есть (даже с расхождениями), я подскажу, где ошибка в сборке.</p>")

    html = ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Micro-Cap: памятка к ДЗ1, вариант 22</title>'
            f"<style>{CSS}</style></head><body>" + "".join(out) + "</body></html>")
    open(OUT_HTML, "w", encoding="utf-8").write(html)
    to_pdf(OUT_HTML, OUT_PDF)
    print("готово:", OUT_PDF)


if __name__ == "__main__":
    main()
