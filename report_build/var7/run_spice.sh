#!/bin/sh
# Пересчёт моделирования в ngspice (создаёт *.log и данные tran*.txt, dc12.txt)
cd "$(dirname "$0")/spice" && for t in t12 t21 t22; do ngspice -b $t.cir -o $t.log; done
