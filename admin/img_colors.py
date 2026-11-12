"""Реальные цвета скинов по картинкам Steam → data/img-colors.json
{ "Weapon | Skin": [[L,a,b,weight], ...] }  — до 4 кластеров по пикселям самого предмета (без прозрачного фона).
Запуск в GitHub Actions (нужен доступ к steamstatic): pip install pillow numpy && python3 admin/img_colors.py
"""
import json, os, io, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "data/img-colors.json")
IMG = json.load(open(os.path.join(ROOT, "data/skin-img.json")))
old = {}
if os.path.exists(OUT) and "--all" not in sys.argv:
    old = {k: v for k, v in json.load(open(OUT)).items() if isinstance(v, dict)}


def srgb2lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def kmeans(X, k=4, it=20):
    rng = np.random.default_rng(0)
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(it):
        lab = np.argmin(((X[:, None] - C[None]) ** 2).sum(-1), 1)
        for j in range(k):
            if (lab == j).any():
                C[j] = X[lab == j].mean(0)
    w = np.bincount(lab, minlength=k) / len(X)
    return C, w


def one(row):
    name, h = row[0].replace("★ ", ""), row[1]
    if not h or name in old:
        return name, old.get(name)
    url = f"https://community.akamai.steamstatic.com/economy/image/{h}/256fx192f"
    for t in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read()
            im = Image.open(io.BytesIO(data)).convert("RGBA")
            a = np.asarray(im).reshape(-1, 4).astype(float)
            px = a[a[:, 3] > 200][:, :3]
            if len(px) < 50:
                return name, None
            if len(px) > 6000:
                px = px[np.random.default_rng(1).choice(len(px), 6000, replace=False)]
            L = srgb2lab(px)
            C = np.hypot(L[:, 1], L[:, 2])
            chrom = C > 14
            hue = (np.degrees(np.arctan2(L[:, 2], L[:, 1])) % 360) // 30
            h = np.bincount(hue[chrom].astype(int), weights=C[chrom], minlength=12)
            h = h / h.sum() if h.sum() > 0 else h
            neu = L[~chrom, 0]
            nb = np.histogram(neu, bins=[0, 30, 60, 101])[0].astype(float)
            nb = nb / nb.sum() if nb.sum() > 0 else nb
            o = {"h": [round(float(x), 3) for x in h], "c": round(float(chrom.mean()), 3), "n": [round(float(x), 3) for x in nb]}
            return name, o
        except Exception:
            time.sleep(1 + t)
    return name, None


res = dict(old)
with ThreadPoolExecutor(16) as ex:
    for n, v in ex.map(one, IMG):
        if v:
            res[n] = v
json.dump(res, open(OUT, "w"), separators=(",", ":"))
print(len(res), "skins with image colors")
