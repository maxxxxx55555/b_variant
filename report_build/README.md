# Сборка PDF-отчётов ДЗ1 (модуль 1)

Отчёты собираются из HTML (формулы набирает MathJax внутри Chromium), печатаются в PDF и получают рамку
и основную надпись по ГОСТ 2.104 (форма 2 на первом листе, форма 2а на остальных).

* `var22/` — вариант 22 (БИТ253, Чигиринцев М.), `var7/` — вариант 7 (БИТ251, Диордиев Б.).
* `render/` — пакеты для MathJax: `cd render && npm install` (каталог `node_modules` в репозиторий не входит).
* В каждом варианте: `calc/` (расчёт на Python), `spice/` (схемы для ngspice), `figs*.py` и `report_content.py`
  (рисунки и текст отчёта), `build.py` (сборка).

Порядок запуска (внутри `var22/` или `var7/`):

    sh run_spice.sh          # ngspice: логи и данные моделирования
    python3 render_console.py # «скриншоты» консольного вывода
    python3 figs12.py; python3 figs21.py; python3 figs22.py; python3 figs_plot.py
    python3 build.py         # report/*.pdf

Нужны: Python 3.13 (NumPy, SciPy, Matplotlib, SymPy, pypdf, reportlab), ngspice 42, Chromium
(путь задан в `report_lib.py`, `CHROME`), шрифт Liberation Serif.
