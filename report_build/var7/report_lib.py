# -*- coding: utf-8 -*-
"""Инфраструктура сборки отчёта: нумерация, формулы (MathJax), вёрстка по ГОСТ 2.105,
рендер в PDF (Chromium), содержание с номерами страниц."""
import hashlib, html as H, json, os, re, subprocess

W = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/"
RENDER = W + "../render/"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
MINUS = "−"

CSS = r"""
@page { size: 210mm 297mm; margin: 15mm 8mm 30mm 25mm; }
@page first { size: 210mm 297mm; margin: 15mm 8mm 55mm 25mm; }
html { font-size: 14pt; }
body { margin: 0; font-family: "Times New Roman", "Liberation Serif", serif; font-size: 14pt;
       line-height: 1.724; text-align: justify; color: #000; }
p { margin: 0; text-indent: 12.5mm; orphans: 2; widows: 2; }
p.ni, .ni { text-indent: 0; }
h1, h2, h3 { font-size: 14pt; font-weight: 700; margin: 0; line-height: 1.724; text-align: left;
         text-indent: 12.5mm; break-after: avoid; hyphens: none; }
h1 { break-before: page; margin-bottom: 1.724em; }
h2, h3 { margin: 0; }
.c { text-align: center; text-indent: 0; }
.b { font-weight: 700; }
.first { page: first; }
mjx-container[display="true"] { display: block; margin: 0; text-align: center; }
mjx-container svg { overflow: visible; }
mjx-container svg text { font-family: "Times New Roman", "Liberation Serif", serif; }
.eq { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center;
      margin: 6pt 0; text-indent: 0; break-inside: avoid; line-height: 1.2; }
.eq .eb { grid-column: 2; }
.eq .en { grid-column: 3; justify-self: end; padding-left: 4mm; }
.where { text-indent: 0; text-align: left; }
.where div { text-indent: 0; }
figure { margin: 4pt 0 12pt; text-align: center; break-inside: avoid; text-indent: 0; }
figure img { display: block; margin: 0 auto; max-width: 100%; }
figcaption { text-indent: 0; text-align: center; line-height: 1.35; margin-top: 4pt; }
.tcap { text-indent: 0; text-align: left; margin: 4pt 0 2pt; break-after: avoid; line-height: 1.4; }
table.t { border-collapse: collapse; width: 100%; margin: 0 0 8pt; text-indent: 0; text-align: center;
          line-height: 1.3; break-inside: avoid; }
table.t th, table.t td { border: 0.7pt solid #000; padding: 1.1mm 1.4mm; vertical-align: middle;
                         font-weight: 400; hyphens: none; }
table.t th { font-weight: 400; }
table.t thead { display: table-header-group; }
table.t tr { break-inside: avoid; }
table.t td.l { text-align: left; }
.note { font-size: 12pt; text-indent: 12.5mm; }
.toc div.r { display: flex; text-indent: 0; text-align: left; }
.toc .t { flex: 0 1 auto; }
.toc .d { flex: 1 1 auto; border-bottom: 1.2pt dotted #000; margin: 0 1.5mm 6pt 1.5mm; min-width: 5mm; }
.toc .g { flex: none; }
.toc .l2 { padding-left: 8mm; }
.appx, .appx p { font-size: 12pt; }
.appx h2.np { break-before: page; }
.appx h1 + h2.np { break-before: auto; }
.appx h2 { margin-top: 1.2em; }
.appx h1 + h2 { margin-top: 0; }
.appx pre { font-family: "Liberation Mono", "Courier New", monospace; font-size: 12pt; line-height: 1.1;
            white-space: pre; margin: 0; text-indent: 0; text-align: left; }
sup, sub { line-height: 0; }
.nw { white-space: nowrap; }
"""


def f(x, nd=3, sign=False):
    """Число с десятичной запятой и настоящим минусом."""
    s = f"{x:.{nd}f}"
    if sign and not s.startswith("-"):
        s = "+" + s
    return s.replace(".", ",").replace("-", MINUS)


def tx(x, nd=3, sign=False):
    """Число для TeX (запятая без пробела)."""
    s = f"{x:.{nd}f}"
    if sign and not s.startswith("-"):
        s = "+" + s
    return s.replace(".", "{,}")


def sci(x, nd=1):
    """Число в виде a·10^b для HTML."""
    m, e = f"{x:.{nd}e}".split("e")
    return f"{f(float(m), nd)}·10<sup>{str(int(e)).replace('-', MINUS)}</sup>"


class Doc:
    def __init__(self, labels=None, pages=None):
        self.out = []
        self.labels = labels or {}
        self.new = {}
        self.cnt = {"fig": 0, "tab": 0, "eq": 0}
        self.h1n = 0
        self.h2n = 0
        self.h3n = 0
        self.formulas = {}
        self.toc = []
        self.pages = pages or {}
        self.hid = 0

    # --- формулы ---
    def _reg(self, tex, display):
        k = hashlib.md5((("D" if display else "I") + tex).encode()).hexdigest()[:14]
        self.formulas[k] = {"tex": tex, "display": display}
        return f"§M{k}§"

    def m(self, tex):
        return self._reg(tex, False)

    def eq(self, tex, label=None, keep=False):
        self.cnt["eq"] += 1
        n = self.cnt["eq"]
        if label:
            self.new["eq:" + label] = n
        st = ' style="break-after:avoid"' if keep else ""
        self.out.append(f'<div class="eq"{st}><div class="eb">{self._reg(tex, True)}</div>'
                        f'<div class="en">({n})</div></div>')

    def where(self, items):
        """items: [(TeX-символ, пояснение), ...] — «где» в первой строке, без двоеточия."""
        rows = []
        for i, (sym, txt) in enumerate(items):
            end = "." if i == len(items) - 1 else ";"
            pre = "где " if i == 0 else ""
            rows.append(f"<div>{pre}{self._reg(sym, False) if sym else ''} — {txt}{end}</div>")
        self.out.append('<div class="where">' + "".join(rows) + "</div>")

    # --- ссылки ---
    def ref(self, kind, label):
        v = self.labels.get(f"{kind}:{label}")
        if v is None:
            return "?"
        return f"({v})" if kind == "eq" else str(v)

    # --- блоки ---
    def raw(self, s):
        self.out.append(s)

    def p(self, text, cls="", keep=False):
        st = ' style="break-after:avoid"' if keep else ""
        self.out.append(f'<p class="{cls}"{st}>{text}</p>' if cls else f"<p{st}>{text}</p>")

    def cont(self, text):
        """Продолжение предложения после формулы: без абзацного отступа."""
        self.out.append(f'<p class="ni">{text}</p>')

    def note(self, text):
        self.out.append(f'<p class="note">{text}</p>')

    def h1(self, text, appendix=None):
        if appendix is None:
            self.h1n += 1
            num = f"{self.h1n}"
            title = f"{num} {text}"
        else:
            num = appendix.split()[-1]
            title = f"{appendix}. {text}"
        self.h2n = 0
        self.h3n = 0
        self.hid += 1
        hid = f"s{self.hid}"
        self.toc.append((1, title, hid))
        self.out.append(f'<h1 id="{hid}">{title}</h1>')
        self._cur = num

    def h2(self, text, toc=True, np=False):
        self.h2n += 1
        self.h3n = 0
        title = f"{self._cur}.{self.h2n} {text}"
        self.hid += 1
        hid = f"s{self.hid}"
        if toc:
            self.toc.append((2, title, hid))
        cls = ' class="np"' if np else ""
        self.out.append(f'<h2 id="{hid}"{cls}>{title}</h2>')

    def h3(self, text):
        self.h3n += 1
        title = f"{self._cur}.{self.h2n}.{self.h3n} {text}"
        self.out.append(f"<h3>{title}</h3>")

    def fig(self, file, caption, label=None, width=None):
        self.cnt["fig"] += 1
        n = self.cnt["fig"]
        if label:
            self.new["fig:" + label] = n
        st = f' style="width:{width}"' if width else ""
        self.out.append(f'<figure><img src="figs/{file}"{st}><figcaption>Рисунок {n} — {caption}'
                        f"</figcaption></figure>")

    def table(self, caption, label, header, rows, widths=None, left=()):
        """header: список строк (могут содержать формулы-метки); rows: список списков."""
        self.cnt["tab"] += 1
        n = self.cnt["tab"]
        if label:
            self.new["tab:" + label] = n
        cg = ""
        if widths:
            cg = "<colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>"
        th = "<thead><tr>" + "".join(f"<th>{h}</th>" for h in header) + "</tr></thead>"
        body = ""
        for r in rows:
            body += "<tr>" + "".join(
                f'<td class="l">{c}</td>' if i in left else f"<td>{c}</td>" for i, c in enumerate(r)) + "</tr>"
        self.out.append(f'<p class="tcap">Таблица {n} — {caption}</p>'
                        f'<table class="t">{cg}{th}<tbody>{body}</tbody></table>')

    def listing(self, code):
        self.out.append('<pre>' + H.escape(code.rstrip("\n")) + "</pre>")

    # --- сборка ---
    def toc_html(self):
        rows = []
        for lvl, title, hid in self.toc:
            pg = self.pages.get(hid, "00")
            cls = "r l2" if lvl == 2 else "r"
            rows.append(f'<div class="{cls}"><span class="t">{title}</span><span class="d"></span>'
                        f'<span class="g">{pg}</span></div>')
        return '<div class="toc">' + "".join(rows) + "</div>"


BATCH = r"""<!doctype html><html><head><meta charset="utf-8">
<style>html{font-family:"Times New Roman","Liberation Serif",serif;font-size:14pt}</style>
<script>window.MathJax = {startup: {typeset: false},
  svg: {fontCache: 'none', linebreaks: {inline: false}},
  options: {enableEnrichment: false, enableSpeech: false, enableBraille: false,
            enableComplexity: false, menuOptions: {settings: {enrich: false, speech: false,
            braille: false, assistiveMml: false, collapsible: false}}}};</script>
<script src="node_modules/@mathjax/mathjax-termes-font/tex-mml-svg-mathjax-termes.js"></script>
</head><body><pre id="out">PENDING</pre>
<script id="data" type="application/json">__DATA__</script>
<script>
const items = JSON.parse(document.getElementById('data').textContent);
MathJax.startup.promise.then(async () => {
  const res = {};
  for (const [k, v] of Object.entries(items)) {
    const n = await MathJax.tex2svgPromise(v.tex, {display: !!v.display});
    res[k] = n.outerHTML;
  }
  document.getElementById('out').textContent = JSON.stringify(res);
}).catch(e => { document.getElementById('out').textContent = 'ERROR ' + e + ' ' + (e && e.stack); });
</script></body></html>"""


def render_formulas(formulas):
    """Возвращает {ключ: svg}. Формулы набираются MathJax внутри Chromium (там измеряется ширина
    кириллического текста); результаты кэшируются на диске."""
    cache_path = RENDER + "mjcache2.json"
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    todo = {k: v for k, v in formulas.items() if k not in cache}
    if todo:
        data = json.dumps(todo, ensure_ascii=False).replace("</", "<\\/")
        open(RENDER + "mjbatch.html", "w", encoding="utf-8").write(BATCH.replace("__DATA__", data))
        r = subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                            "--allow-file-access-from-files", "--virtual-time-budget=300000",
                            "--dump-dom", "file://" + RENDER + "mjbatch.html"],
                           capture_output=True, text=True, timeout=900)
        m = re.search(r'<pre id="out">(.*?)</pre>', r.stdout, re.S)
        txt = H.unescape(m.group(1)) if m else "NO OUTPUT"
        if not txt.startswith("{"):
            raise RuntimeError("MathJax(Chromium): " + txt[:800])
        res = json.loads(txt)
        for k, svg in res.items():
            if "merror" in svg:
                raise RuntimeError("Ошибка TeX: " + todo[k]["tex"])
            svg = re.sub(r' tabindex="0"| ctxtmenu_counter="\d+"| CtxtMenu_Attached_\d+', "", svg)
            cache[k] = svg
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    return {k: cache[k] for k in formulas}


def assemble(doc, front_html, out_html):
    body = front_html + "".join(doc.out)
    body = re.sub(r"([(«]?)(§M[0-9a-f]{14}§)([,.;:!?)»]*)",
                  lambda m: (f'<span class="nw">{m.group(0)}</span>' if (m.group(1) or m.group(3))
                             else m.group(0)), body)
    svgs = render_formulas(doc.formulas)
    body = re.sub("§M([0-9a-f]{14})§", lambda m: svgs[m.group(1)], body)
    page = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
            "<title>Домашнее задание №1, вариант 7</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    open(out_html, "w", encoding="utf-8").write(page)


def to_pdf(html_path, pdf_path):
    r = subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", f"--print-to-pdf={pdf_path}",
                        "file://" + html_path], capture_output=True, text=True, timeout=600)
    if not os.path.exists(pdf_path):
        raise RuntimeError("Chromium: " + r.stderr[-1500:])


def find_pages(pdf_path, toc):
    """Номера страниц заголовков (по тексту PDF), без учёта страницы содержания."""
    import pypdf
    rd = pypdf.PdfReader(pdf_path)
    norm = lambda s: re.sub(r"\s+", "", s)
    texts = [norm(p.extract_text() or "") for p in rd.pages]
    res = {}
    start = 1
    for lvl, title, hid in toc:
        key = norm(title)
        for i in range(start, len(texts)):
            if key in texts[i]:
                res[hid] = i + 1
                start = i
                break
    return res, len(rd.pages)
