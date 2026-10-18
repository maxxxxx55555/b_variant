# -*- coding: utf-8 -*-
"""Рамка и основная надпись (ГОСТ 2.104, формы 2 и 2а) поверх страниц PDF."""
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pypdf

FD = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("LS", FD + "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LS-I", FD + "LiberationSerif-Italic.ttf"))

THICK = 0.8 * mm * 1.0
THIN = 0.35 * mm * 0.7


def _line(c, x0, y0, x1, y1, w=THIN):
    c.setLineWidth(w)
    c.line(x0 * mm, y0 * mm, x1 * mm, y1 * mm)


def _text(c, x, y, s, size=10, font="LS-I", align="c"):
    c.setFont(font, size)
    if align == "c":
        c.drawCentredString(x * mm, y * mm, s)
    elif align == "l":
        c.drawString(x * mm, y * mm, s)
    else:
        c.drawRightString(x * mm, y * mm, s)


def draw_page(c, pageno, total, first, info):
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    # рамка листа: слева 20 мм, с остальных сторон 5 мм
    c.setLineWidth(THICK)
    c.rect(20 * mm, 5 * mm, 185 * mm, 287 * mm)
    X0, X1 = 20, 205
    if first:
        H = 40
        top = 5 + H
        c.setLineWidth(THICK)
        c.line(X0 * mm, top * mm, X1 * mm, top * mm)
        # строки левого блока (по 5 мм), снизу вверх
        rows = ["hdr", "Разраб.", "Пров.", "", "Н. контр.", "Утв.", "", ""]
        for i, kind in enumerate(rows):
            y0 = 5 + 5 * i
            if i > 0:
                _line(c, X0, y0, 85, y0)
            vx = [37, 60, 75] if kind in ("Разраб.", "Пров.", "Н. контр.", "Утв.") else [27, 37, 60, 75]
            for x in vx:
                _line(c, x, y0, x, y0 + 5)
            if kind == "hdr":
                for x0, x1, s in ((20, 27, "Изм."), (27, 37, "Лист"), (37, 60, "№ докум."),
                                  (60, 75, "Подп."), (75, 85, "Дата")):
                    _text(c, (x0 + x1) / 2, y0 + 1.4, s, 8.5 if x1 - x0 < 8 else 10)
            elif kind:
                _text(c, 21, y0 + 1.4, kind, 10, align="l")
        _text(c, 48.5, 5 + 5 * 1 + 1.4, info["author_short"], 10.5)       # Разраб.
        # центр и правая часть
        _line(c, 85, 5, 85, top, THICK)
        _line(c, 85, 30, X1, 30, THICK)
        _line(c, 155, 5, 155, 30, THICK)
        _line(c, 155, 25, X1, 25)
        _line(c, 155, 20, X1, 20, THICK)
        _line(c, 170, 20, 170, 30); _line(c, 185, 20, 185, 30)
        _text(c, 145, 38.2, info["designation"], 15, "LS-I")
        # наименование документа
        _text(c, 120, 21.5, info["title1"], 12)
        _text(c, 120, 16.5, info["title2"], 12)
        _text(c, 120, 11.5, info["title3"], 12)
        for x0, x1, s in ((155, 170, "Лит."), (170, 185, "Лист"), (185, 205, "Листов")):
            _text(c, (x0 + x1) / 2, 26.4, s, 10)
        _text(c, 177.5, 21.2, str(pageno), 11)
        _text(c, 195, 21.2, str(total), 11)
        _text(c, 180, 11.2, info["org"], 13)
    else:
        top = 5 + 15
        c.setLineWidth(THICK)
        c.line(X0 * mm, top * mm, X1 * mm, top * mm)
        for i in range(1, 3):
            _line(c, X0, 5 + 5 * i, 85, 5 + 5 * i)
        for x in (27, 37, 60, 75):
            _line(c, x, 5, x, top)
        for x0, x1, s in ((20, 27, "Изм."), (27, 37, "Лист"), (37, 60, "№ докум."),
                          (60, 75, "Подп."), (75, 85, "Дата")):
            _text(c, (x0 + x1) / 2, 6.4, s, 8.5 if x1 - x0 < 8 else 10)
        _line(c, 85, 5, 85, top, THICK)
        _line(c, 195, 5, 195, top, THICK)
        _line(c, 195, 15, X1, 15)
        _text(c, 140, 11.3, info["designation"], 15, "LS-I")
        _text(c, 200, 16.4, "Лист", 10)
        _text(c, 200, 8.6, str(pageno), 12)


def overlay(in_pdf, out_pdf, info):
    r = pypdf.PdfReader(in_pdf)
    total = len(r.pages)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(210 * mm, 297 * mm), initialFontName="LS", initialFontSize=10)
    for i in range(total):
        draw_page(c, i + 1, total, i == 0, info)
        c.showPage()
    c.save()
    buf.seek(0)
    ov = pypdf.PdfReader(buf)
    w = pypdf.PdfWriter()
    for i, p in enumerate(r.pages):
        p.merge_page(ov.pages[i])
        w.add_page(p)
    w.add_metadata({"/Title": info["pdf_title"], "/Author": info["pdf_author"],
                    "/Subject": "Домашнее задание №1, модуль 1"})
    with open(out_pdf, "wb") as f:
        w.write(f)
    return total
