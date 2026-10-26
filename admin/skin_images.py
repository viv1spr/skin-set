# -*- coding: utf-8 -*-
"""Компактная база картинок скинов для конструктора: data/skin-img.json = [[name, hash, phase], ...]
Источник — ByMykel/CSGO-API (4,7 МБ) — раньше грузился в браузере на каждом заходе. Теперь ~0,4 МБ со своего домена.
python3 admin/skin_images.py  (запускается еженедельно в pages-weekly.yml)"""
import json, os, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/skins.json"
PRE = "https://community.akamai.steamstatic.com/economy/image/"
def main():
    try:
        d = json.load(urllib.request.urlopen(SRC, timeout=60))
    except Exception as e:
        print("skip:", e); return
    out = []
    for it in d:
        n, im = it.get("name"), it.get("image") or ""
        if not n or not im.startswith(PRE): continue
        out.append([n, im[len(PRE):], (it.get("phase") or "")])
    if len(out) < 1500: print("too few", len(out)); return
    json.dump(out, open(os.path.join(ROOT, "data", "skin-img.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(out), "images")
if __name__ == "__main__": main()
