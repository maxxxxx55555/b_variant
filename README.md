# ДЗ 1 (модуль 1): задания 1-2, 2-1, 2-2

## Вариант 22 — БИТ253, Чигиринцев Максим

* `DZ1_BIT253_var22_Chigirintsev.pdf` — отчёт для загрузки в SmartLMS.
* `sources/calc/` — программы расчёта на Python 3 (NumPy, SciPy): `python3 task12.py`, `task21.py`, `task22.py`.
* `sources/spice/` — описания схем для ngspice: `ngspice -b t12.cir -o t12.log` (и `t21.cir`, `t22.cir`).

## Вариант 7 — БИТ251, Диордиев Богдан Юрьевич

* `DZ1_BIT251_var7_Diordiev.pdf` — отчёт для загрузки в SmartLMS.
* `sources_var7/calc/` — программы расчёта на Python 3 (NumPy): `python3 task12.py`, `task21.py`, `task22.py`.
* `sources_var7/spice/` — описания схем для ngspice: `ngspice -b t12.cir -o t12.log` (и `t21.cir`, `t22.cir`).

## Проверка в LTspice (вариант 22)

* `LTspice_var22_files.zip` — готовые схемы LTspice (`.asc`) и запасные нетлисты (`.cir`) для заданий 1-2, 2-1, 2-2.
  Те же файлы лежат в `report_build/var22/ltspice/files/`; генератор и проверка — `report_build/var22/ltspice/build_ltspice.py`.
* `LTspice_pamyatka_DZ1_var22.pdf` — памятка: как запустить, какие значения должны получиться, какие скриншоты прислать.
* Файлы проверены разбором схемы и прогоном нетлиста в ngspice; в самом LTspice они не запускались (в среде разработки он недоступен).
