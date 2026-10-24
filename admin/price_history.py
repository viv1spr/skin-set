# -*- coding: utf-8 -*-
"""История цен по дням (последний снимок за сутки, UTC) для каждого скина и износа.
Хранится НЕ в main (чтобы не раздувать репозиторий), а в ветке history, которую workflow перезаписывает одним коммитом.
Сайт берёт файлы через воркер: https://auth.skin-set.com/hist/<файл>.

  python3 admin/price_history.py --dir /tmp/hist             — добавить текущие data/prices.json за сегодня
  python3 admin/price_history.py --dir /tmp/hist --backfill  — восстановить прошлые дни из git-истории data/prices.json

Формат: meta.json {"days": ["2026-10-15", ...], "shards": 64, "t": ...}
        NN.json   {"AK-47 | Redline": {"FT": [12.3, null, ...], ...}, ...}   — массивы выровнены по days
Шард: djb2(name) % 64 (та же функция в JS на сайте).
"""
import json, os, sys, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH = 64
KEEP = 400
WEARS = ["FN", "MW", "FT", "WW", "BS"]


def shard(name):
    h = 5381
    for ch in name:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return h % SH


def load(d):
    """→ days, {name: {wear: {day: v}}}"""
    mp = os.path.join(d, "meta.json")
    if not os.path.exists(mp): return [], {}
    days = json.load(open(mp))["days"]; data = {}
    for k in range(SH):
        f = os.path.join(d, f"{k:02d}.json")
        if not os.path.exists(f): continue
        for n, ws in json.load(open(f)).items():
            data[n] = {w: {days[i]: v for i, v in enumerate(arr) if v is not None} for w, arr in ws.items()}
    return days, data


def put(data, day, prices):
    for n, rec in prices.items():
        for w, v in (rec.get("w") or {}).items():
            if v and v > 0: data.setdefault(n, {}).setdefault(w, {})[day] = round(v, 2)


def save(d, data):
    days = sorted({day for ws in data.values() for m in ws.values() for day in m})[-KEEP:]
    os.makedirs(d, exist_ok=True)
    out = [dict() for _ in range(SH)]
    for n, ws in data.items():
        rec = {}
        for w in WEARS:
            m = ws.get(w)
            if not m: continue
            arr = [m.get(day) for day in days]
            if any(v is not None for v in arr): rec[w] = arr
        if rec: out[shard(n)][n] = rec
    for k in range(SH):
        json.dump(out[k], open(os.path.join(d, f"{k:02d}.json"), "w"), separators=(",", ":"))
    json.dump({"days": days, "shards": SH, "t": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"}, open(os.path.join(d, "meta.json"), "w"))
    return days


def backfill(data):
    log = subprocess.run(["git", "log", "--format=%H %ct", "--", "data/prices.json"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
    seen = set()
    for line in log:  # от новых к старым: берём последний снимок каждого дня
        if not line.strip(): continue
        sha, ts = line.split()
        day = datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).strftime("%Y-%m-%d")
        if day in seen: continue
        try: p = json.loads(subprocess.run(["git", "show", f"{sha}:data/prices.json"], cwd=ROOT, capture_output=True, text=True).stdout)
        except Exception: continue
        seen.add(day)
        for n, rec in p.items():
            for w, v in (rec.get("w") or {}).items():
                if v and v > 0: data.setdefault(n, {}).setdefault(w, {}).setdefault(day, round(v, 2))
    return len(seen)


def main():
    d = sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else os.path.join(ROOT, "data/hist")
    days, data = load(d)
    if "--backfill" in sys.argv: print("backfilled days:", backfill(data))
    today = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
    put(data, today, json.load(open(os.path.join(ROOT, "data/prices.json"))))
    days = save(d, data)
    print(len(days), "days,", len(data), "skins →", d)


if __name__ == "__main__":
    main()
