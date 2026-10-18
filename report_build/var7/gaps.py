# Измерение свободного места внизу каждой страницы (мм)
import sys, numpy as np
from PIL import Image
import glob
dpi = 85
mm = lambda px: px / dpi * 25.4
res = []
for f in sorted(glob.glob('report/pg/p-*.png')):
    im = np.array(Image.open(f).convert('L'))
    h, w = im.shape
    x0, x1 = int(25 / 25.4 * dpi), int(202 / 25.4 * dpi)
    n = int(f.split('-')[-1].split('.')[0])
    stamp_top = 252 if n == 1 else 277
    y0 = int(15 / 25.4 * dpi); y1 = int((stamp_top - 3) / 25.4 * dpi)
    reg = im[y0:y1, x0:x1] < 200
    rows = np.where(reg.any(axis=1))[0]
    last = mm(rows.max() + y0) if len(rows) else 15
    free = (stamp_top - 10) - last     # до нижней границы текста (стамп - 10 мм)
    res.append((n, free))
print(' '.join(f'{n}:{free:.0f}' for n, free in res))
print('страницы с пустотой > 45 мм:', [n for n, fr in res if fr > 45])
