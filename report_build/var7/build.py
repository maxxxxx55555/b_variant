# -*- coding: utf-8 -*-
"""Сборка отчёта: HTML -> PDF (Chromium) -> рамка и основная надпись."""
import os, sys, shutil
from report_lib import *
import report_content as C
import stamp

HTML = W + "report/report.html"
RAW = W + "report/raw.pdf"
FINAL = W + "report/DZ1_BIT251_var7_Diordiev.pdf"
os.makedirs(W + "report", exist_ok=True)
if not os.path.exists(W + "report/figs"):
    os.symlink(W + "figs", W + "report/figs")


def build_once(labels, pages):
    D = Doc(labels, pages)
    C.sec1(D); C.sec2(D); C.sec3(D); C.appendices(D)
    return D, C.front(D)


D, fr = build_once({}, {})
labels = D.new
D, fr = build_once(labels, {})
assert D.new == labels, "нумерация нестабильна"
for it in range(3):
    assemble(D, fr, HTML)
    to_pdf(HTML, RAW)
    pages, n = find_pages(RAW, D.toc)
    if pages == D.pages and len(pages) == len(D.toc):
        break
    D, fr = build_once(labels, pages)
print("страниц:", n, "найдено заголовков:", len(pages), "из", len(D.toc))
info = dict(author_short="Диордиев Б.", designation="ДЗ1.БИТ251.В7",
            title1="Домашнее задание № 1", title2="Модуль 1. Расчёт", title3="электрических цепей",
            org="БИТ251", pdf_title="Домашнее задание № 1, вариант 7", pdf_author="Диордиев Богдан Юрьевич")
total = stamp.overlay(RAW, FINAL, info)
print("готово:", FINAL, total, "стр.")
