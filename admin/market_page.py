# -*- coding: utf-8 -*-
"""Страница «Рынок CS2 сегодня»: что подорожало и подешевело за сутки и неделю (по истории цен).
Запуск: python3 admin/market_page.py --dir <папка с историей>  (по умолчанию data/hist)
Пишет /rynok-cs2/ и /en/cs2-market/, а также data/market.json (сводка — для поста в Telegram и главной).
"""
import json, os, re, sys, html, datetime, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from budget_pages import money, wiki_url  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa
from pagegrid import GRID_CSS  # noqa
from price_history import load  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/rynok-cs2/", "en": "/en/cs2-market/"}
RATE = {"ru": 90, "en": 1}
WEARN = {"ru": {"FN": "FN", "MW": "MW", "FT": "FT", "WW": "WW", "BS": "BS"}, "en": {"FN": "FN", "MW": "MW", "FT": "FT", "WW": "WW", "BS": "BS"}}
MINP = 2.0      # $: дешевле — шум
MAXCHG = 100.0  # %: больше — скорее ошибка данных
CATS = [("all", {"ru": "Все", "en": "All"}), ("knife", {"ru": "Ножи", "en": "Knives"}), ("gloves", {"ru": "Перчатки", "en": "Gloves"}), ("weapon", {"ru": "Оружие", "en": "Weapons"})]
T = {
 "ru": dict(h1="Рынок CS2 сегодня", title="Рынок скинов CS2 сегодня: что подорожало и подешевело — Skinset",
   desc="Какие скины CS2 подорожали и подешевели за сутки и за неделю: ножи, перчатки, AK-47, AWP. Индекс рынка, графики цен, обновление каждые 4 часа.",
   lead="Какие скины подорожали и подешевели за последние сутки и неделю. Цены — минимальные на рынке по каждому износу, обновляются каждые 4 часа. Скины дешевле $2 и резкие скачки из-за нехватки предложений не учитываются.",
   kick="Обновляется каждые 4 часа", idx="Индекс рынка", idx_d="медианное изменение цены по {n} позициям дороже $5 (скин + износ)", d1="за сутки", d7="за неделю",
   up1="Подорожали за сутки", dn1="Подешевели за сутки", up7="Подорожали за неделю", dn7="Подешевели за неделю", upd="Обновлено {D} (МСК)",
   home="Главная", none="Пока мало данных — история цен только начала собираться.", note="Цены — ориентир по открытым данным площадок, не финансовый совет.",
   sum="За сутки сильнее всего вырос {u} ({uc}), сильнее всего подешевел {d} ({dc}). Индекс рынка за неделю: {i}.", tracked="скинов отслеживаем", days="дней истории",
   inv="Узнай, сколько стоит твой инвентарь →", all_h="Все скины", all_p="Цены и изменения по всем отслеживаемым скинам и износам. Ищи, фильтруй и сортируй.", srch="Поиск: AK-47, Karambit, Asiimov…",
   sorts=[("c1d","Рост за сутки"), ("c1a","Падение за сутки"), ("c7d","Рост за неделю"), ("c7a","Падение за неделю"), ("pd","Сначала дорогие"), ("pa","Сначала дешёвые")], more="Показать ещё", cols=["Скин", "Цена", "Сутки", "Неделя"], found="Найдено: {n}"),
 "en": dict(h1="CS2 market today", title="CS2 skin market today: biggest risers and fallers — Skinset",
   desc="Which CS2 skins went up and down in the last 24 hours and 7 days: knives, gloves, AK-47, AWP. Market index and price charts, updated every 4 hours.",
   lead="Which skins went up and down over the last day and week. Prices are the lowest market listing for each wear, updated every 4 hours. Skins under $2 and spikes caused by thin supply are excluded.",
   kick="Updated every 4 hours", idx="Market index", idx_d="median price change across {n} listings over $5 (skin + wear)", d1="24h", d7="7 days",
   up1="Top risers · 24h", dn1="Top fallers · 24h", up7="Top risers · 7 days", dn7="Top fallers · 7 days", upd="Updated {D} UTC",
   home="Home", none="Not enough data yet — price history has just started.", note="Prices are a guide based on public marketplace data, not financial advice.",
   sum="In the last 24h the biggest riser was {u} ({uc}) and the biggest faller was {d} ({dc}). 7-day market index: {i}.", tracked="skins tracked", days="days of history",
   inv="Check what your inventory is worth →", all_h="All skins", all_p="Prices and changes for every tracked skin and wear. Search, filter and sort.", srch="Search: AK-47, Karambit, Asiimov…",
   sorts=[("c1d","Biggest gain · 24h"), ("c1a","Biggest drop · 24h"), ("c7d","Biggest gain · 7d"), ("c7a","Biggest drop · 7d"), ("pd","Price: high to low"), ("pa","Price: low to high")], more="Show more", cols=["Skin", "Price", "24h", "7d"], found="Found: {n}"),
}
CSS = """
html,body{overflow-x:clip}
.mk{max-width:1180px;margin:0 auto;padding:22px 24px 60px}
.mk .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:14px}.mk .crumbs a{color:var(--soft)}
.mk-kick{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(29,155,90,.14);border:1px solid rgba(29,155,90,.45);color:#7dffb0;font:600 .72rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase}
.mk-kick i{width:7px;height:7px;border-radius:50%;background:#2bd67b;animation:mkP 1.8s infinite}@keyframes mkP{50%{opacity:.3}}
.mk h1{margin:12px 0 8px;font:700 clamp(2.1rem,5vw,3.4rem)/1 var(--hud);text-transform:uppercase}
.mk h1::before,.mk h2::before{display:none!important}
.mk .lead{color:var(--soft);max-width:760px;margin:0}
.mk-top{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:12px;margin:22px 0}
.kpi{padding:16px 18px;background:rgba(255,255,255,.04);border:1px solid var(--line,rgba(255,255,255,.1))}
.kpi small{display:block;font:600 .72rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin-bottom:10px}
.kpi b{font:700 2.2rem/1 var(--hud)}.kpi span{display:block;margin-top:6px;font-size:.82rem;color:var(--soft)}
.kpi .row{display:flex;gap:18px;align-items:baseline}.kpi .row em{font-style:normal;font-size:.8rem;color:var(--dim);margin-left:4px}
.up{color:#2bd67b!important}.dn{color:#ff5d5d!important}
.mk .sum{color:var(--soft);margin:0 0 6px}
.mk-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:18px 0 6px}
.mk-tabs button{padding:9px 14px;background:rgba(255,255,255,.04);border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--soft);font:600 .78rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
.mk-all{margin-left:auto;align-self:center;color:#66c0f4;font:600 .82rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-decoration:none}
.mk-tabs button.on{background:#e8402a;border-color:#e8402a;color:#fff}
.mk-g{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px}
.lst{background:rgba(255,255,255,.03);border:1px solid var(--line,rgba(255,255,255,.1))}
.lst h2{margin:0;padding:14px 16px;font:700 1rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid var(--line,rgba(255,255,255,.1))}
.lst h2.u{color:#2bd67b}.lst h2.d{color:#ff5d5d}
.it{display:grid;grid-template-columns:22px 58px minmax(0,1fr) 84px 76px;gap:10px;align-items:center;padding:8px 14px;border-bottom:1px solid rgba(255,255,255,.05);color:var(--ink,#fff);text-decoration:none}
.it:last-child{border-bottom:0}.it:hover{background:rgba(255,255,255,.04)}
.it .n{font:600 .8rem var(--hud);color:var(--dim)}
.it img{width:58px;height:42px;object-fit:contain;filter:drop-shadow(0 4px 6px rgba(0,0,0,.5))}
.it .nm{min-width:0}.it .nm b{display:block;font:600 .9rem/1.2 var(--body,inherit);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.it .nm small{color:var(--dim);font-size:.76rem}
.it svg{width:84px;height:28px}
.it .ch{text-align:right}.it .ch b{display:block;font:700 .95rem var(--hud)}.it .ch small{color:var(--soft);font-size:.76rem}
.mk .cta{display:inline-block;margin-top:22px;padding:13px 18px;background:linear-gradient(90deg,#e8402a,#ff6a3d);color:#fff;font:700 .84rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-decoration:none}
.mk .note{margin-top:22px;font-size:.8rem;color:var(--dim)}
.all{margin-top:30px}.all h2{margin:0 0 6px;font:700 1.5rem/1 var(--hud);text-transform:uppercase}.all>p{color:var(--soft);margin:0 0 14px}
.af{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}
.af input,.af select{height:42px;padding:0 12px;background:rgba(255,255,255,.05);border:1px solid var(--line2,rgba(255,255,255,.16));color:var(--ink,#fff);font-size:.92rem;outline:none}
.af input{flex:1;min-width:200px}.af select option{background:#131417}
.af .kd{display:flex;gap:4px}.af .kd button{height:42px;padding:0 12px;background:rgba(255,255,255,.04);border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--soft);font:600 .74rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;cursor:pointer}.af .kd button.on{background:#e8402a;border-color:#e8402a;color:#fff}
.af .cnt{font-size:.82rem;color:var(--dim)}
.at{background:rgba(255,255,255,.03);border:1px solid var(--line,rgba(255,255,255,.1))}
.ar{display:grid;grid-template-columns:52px minmax(0,1fr) 110px 80px 80px;gap:10px;align-items:center;padding:7px 14px;border-bottom:1px solid rgba(255,255,255,.05);color:var(--ink,#fff);text-decoration:none}
.ar.h{color:var(--dim);font:600 .72rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;padding:10px 14px}.ar:not(.h):hover{background:rgba(255,255,255,.04)}
.ar img{width:52px;height:38px;object-fit:contain}.ar b{display:block;font-weight:600;font-size:.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ar small{color:var(--dim);font-size:.76rem}
.ar .p,.ar .c{text-align:right;font:700 .92rem var(--hud)}.ar .c.z{color:var(--dim)}
.amore{display:block;margin:12px auto 0;padding:12px 22px;background:rgba(255,255,255,.06);border:1px solid var(--line2,rgba(255,255,255,.2));color:#fff;font:700 .8rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
@media(max-width:600px){.ar{grid-template-columns:40px minmax(0,1fr) 72px 60px;gap:8px;padding:7px 10px}.ar .c7{display:none}.ar img{width:40px;height:30px}.af input{min-width:0;width:100%}}
[data-cat]{display:none}[data-cat].on{display:grid}
@media(max-width:900px){.mk-top{grid-template-columns:1fr 1fr}.mk-top .kpi:first-child{grid-column:1/-1}.kpi b{font-size:1.8rem}.mk-g{grid-template-columns:1fr}}
@media(max-width:600px){.mk{padding:16px 14px 40px}.it{grid-template-columns:18px 46px minmax(0,1fr) 70px;gap:8px;padding:8px 10px}.it svg{display:none}.it img{width:46px;height:34px}}
"""


def imgurl(i):
    return i if i.startswith("http") else "https://community.akamai.steamstatic.com/economy/image/" + i + "/120fx90f"


def spark(arr):
    v = [x for x in arr[-14:] if x is not None]
    if len(v) < 2: return ""
    lo, hi = min(v), max(v); rng = (hi - lo) or 1
    pts = " ".join(f"{i * 84 / (len(v) - 1):.1f},{26 - (x - lo) / rng * 24:.1f}" for i, x in enumerate(v))
    c = "#2bd67b" if v[-1] >= v[0] else "#ff5d5d"
    return f'<svg viewBox="0 0 84 28" aria-hidden="true"><polyline points="{pts}" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/></svg>'


def pct(lang, x):
    s = f"{x:+.1f}%"
    return s.replace(".", ",").replace("-", "−") if lang == "ru" else s.replace("-", "−")


def compute(d):
    days, data = load(d)
    if len(days) < 2: return days, [], None
    cat = {x["n"]: x for x in json.load(open(os.path.join(ROOT, "data/catalog.json")))}
    rows = []
    for n, ws in data.items():
        c = cat.get(n)
        if not c: continue
        kind = c["c"] if c["c"] in ("knife", "gloves") else "weapon"
        for w, m in ws.items():
            arr = [m.get(day) for day in days]
            cur = arr[-1]
            if cur is None or cur < MINP: continue
            prev = arr[-2]
            wk = next((arr[i] for i in range(max(0, len(arr) - 8), len(arr) - 1) if arr[i] is not None), None)
            c1 = (cur / prev - 1) * 100 if prev else None
            c7 = (cur / wk - 1) * 100 if wk else None
            if c1 is not None and abs(c1) > 50: c1 = None
            if c7 is not None and abs(c7) > MAXCHG: c7 = None
            rows.append(dict(n=n, w=w, cur=cur, c1=c1, c7=c7, arr=arr, kind=kind, i=c["i"], r=c.get("r", 3)))
    # индекс: популярные (дороже $5), медиана
    pop = [r for r in rows if r["cur"] >= 5]
    i1 = statistics.median([r["c1"] for r in pop if r["c1"] is not None]) if pop else None
    i7 = statistics.median([r["c7"] for r in pop if r["c7"] is not None]) if pop else None
    return days, rows, dict(i1=i1, i7=i7, n=len(pop), tracked=len({r["n"] for r in rows}))


def lst(lang, rows, key, rev, title, cls):
    rs = sorted([r for r in rows if r[key] is not None and ((r[key] > 0) if rev else (r[key] < 0))], key=lambda r: r[key], reverse=rev)[:10]
    if not rs: return ""
    items = []
    for k, r in enumerate(rs, 1):
        wu = wiki_url(lang, r["n"]); tag = f'<a class="it" href="{wu}">' if wu else '<div class="it">'
        items.append(f'{tag}<span class="n">{k}</span><img src="{e(imgurl(r["i"]))}" alt="" loading="lazy"><span class="nm"><b>{e(r["n"])}</b><small>{r["w"]}</small></span>{spark(r["arr"])}'
                     f'<span class="ch"><b class="{"up" if r[key] > 0 else "dn"}">{pct(lang, r[key])}</b><small>{e(money(lang, r["cur"] * RATE[lang]))}</small></span></{"a" if wu else "div"}>')
    return f'<div class="lst"><h2 class="{cls}">{e(title)}</h2>{"".join(items)}</div>'


ALLJS = r"""<script>(()=>{const R=__RATE__,CUR=__CUR__,WK=__WIKI__,FOUND=__FOUND__,lang=document.documentElement.lang;let D=null,k="all",n=50;const $=s=>document.getElementById(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);const f=new Intl.NumberFormat(lang,{maximumFractionDigits:R>=50?0:2});
const M=v=>CUR[0]+f.format(R>=50?Math.round(v*R/10)*10:v)+CUR[1];const P=x=>x==null?'<span class="c z">—</span>':Math.abs(x)<.05?'<span class="c z">0%</span>':'<span class="c '+(x>=0?"up":"dn")+'">'+(x>0?"+":x<0?"−":"")+Math.abs(x).toFixed(1).replace(".",lang==="en"?".":",")+"%</span>";
const IMG=i=>i?(i.startsWith("http")?i:"https://community.akamai.steamstatic.com/economy/image/"+i+"/120fx90f"):"";
function draw(){if(!D)return;const q=$("aq").value.trim().toLowerCase().split(/\s+/).filter(Boolean),so=$("as").value;
 let r=D.r.filter(x=>(k==="all"||x[5]===k)&&q.every(w=>x[0].toLowerCase().includes(w)));
 const key={c1d:x=>-(x[3]??-1e9),c1a:x=>(x[3]??1e9),c7d:x=>-(x[4]??-1e9),c7a:x=>(x[4]??1e9),pd:x=>-x[2],pa:x=>x[2]}[so];r.sort((a,b)=>key(a)-key(b));
 $("an").textContent=FOUND.replace("{n}",r.length);
 $("al").innerHTML=r.slice(0,n).map(x=>{const tag=x[6]?'<a class="ar" href="'+WK+x[6]+'/">':'<div class="ar">';return tag+'<img src="'+esc(IMG(D.img[x[0]]))+'" alt="" loading="lazy"><span><b>'+esc(x[0])+'</b><small>'+x[1]+'</small></span><span class="p">'+M(x[2])+'</span>'+P(x[3])+P(x[4]).replace('class="c','class="c c7')+(x[6]?"</a>":"</div>")}).join("");
 $("am").hidden=r.length<=n}
async function load(){if(D)return;try{D=await (await fetch("/data/market-all.json")).json()}catch(e){return}draw()}
$("aq").addEventListener("input",()=>{n=50;load();draw()});$("as").addEventListener("change",()=>{n=50;draw()});
$("ak").addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;k=b.dataset.k;$("ak").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));n=50;draw()});
$("am").addEventListener("click",()=>{n+=100;draw()});
const io=new IntersectionObserver(es=>{if(es.some(x=>x.isIntersecting)){load();io.disconnect()}},{rootMargin:"600px"});io.observe($("all"));if(location.hash==="#all")load()})();</script>"""


def build(d):
    days, rows, ix = compute(d)
    now = datetime.datetime.now(datetime.timezone.utc)
    out = {"t": now.isoformat(timespec="minutes"), "days": len(days)}
    for lang in URL:
        t = T[lang]; url = URL[lang]
        D = (now + datetime.timedelta(hours=3 if lang == "ru" else 0)).strftime("%d.%m.%Y %H:%M")
        if not rows:
            body = f'<h1>{e(t["h1"])}</h1><p class="lead">{e(t["none"])}</p>'
        else:
            tabs = '<div class="mk-tabs" id="mkt">' + "".join(f'<button data-c="{c}"{" class=on" if c == "all" else ""}>{e(l[lang])}</button>' for c, l in CATS) + f'<a class="mk-all" href="#all">{e(t["all_h"])} ({len(rows)}) ↓</a></div>'
            grids = []
            for c, _ in CATS:
                rr = rows if c == "all" else [r for r in rows if r["kind"] == c]
                grids.append(f'<div class="mk-g{" on" if c == "all" else ""}" data-cat="{c}">' + lst(lang, rr, "c1", True, t["up1"], "u") + lst(lang, rr, "c1", False, t["dn1"], "d")
                             + lst(lang, rr, "c7", True, t["up7"], "u") + lst(lang, rr, "c7", False, t["dn7"], "d") + "</div>")
            c1s = sorted([r for r in rows if r["c1"] is not None], key=lambda r: r["c1"])
            su = t["sum"].format(u=f'{c1s[-1]["n"]} {c1s[-1]["w"]}', uc=pct(lang, c1s[-1]["c1"]), d=f'{c1s[0]["n"]} {c1s[0]["w"]}', dc=pct(lang, c1s[0]["c1"]), i=pct(lang, ix["i7"] or 0)) if c1s else ""
            kpi = (f'<div class="mk-top"><div class="kpi"><small>{e(t["idx"])}</small><div class="row">'
                   + (f'<b class="{"up" if (ix["i1"] or 0) >= 0 else "dn"}">{pct(lang, ix["i1"] or 0)}</b><em>{e(t["d1"])}</em>' if ix["i1"] is not None else "")
                   + (f'<b class="{"up" if (ix["i7"] or 0) >= 0 else "dn"}">{pct(lang, ix["i7"] or 0)}</b><em>{e(t["d7"])}</em>' if ix["i7"] is not None else "")
                   + f'</div><span>{e(t["idx_d"].format(n=ix["n"]))}</span></div>'
                   f'<div class="kpi"><small>{e(t["tracked"])}</small><b>{ix["tracked"]}</b></div><div class="kpi"><small>{e(t["days"])}</small><b>{len(days)}</b><span>{e(days[0])} — {e(days[-1])}</span></div></div>')
            js = ('<script>(()=>{const t=document.getElementById("mkt");if(!t)return;t.addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;'
                  't.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));document.querySelectorAll("[data-cat]").forEach(g=>g.classList.toggle("on",g.dataset.cat===b.dataset.c))})})()</script>')
            inv = "/ocenka-inventarya/" if lang == "ru" else "/en/inventory-value/"
            body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav><span class="mk-kick pg-eb"><i></i>{e(t["kick"])} · {e(t["upd"].format(D=D))}</span>'
                    f'<h1 class="pg-h">{e(t["h1"])}</h1><p class="lead pg-l">{e(t["lead"])}</p>{kpi}<p class="sum">{e(su)}</p>{tabs}{"".join(grids)}{js}'
                    f'<section class="all" id="all"><h2>{e(t["all_h"])}</h2><p>{e(t["all_p"])}</p><div class="af"><input id="aq" type="search" placeholder="{e(t["srch"])}" autocomplete="off">'
                    + '<div class="kd" id="ak">' + "".join(f'<button data-k="{c}"{" class=on" if c == "all" else ""}>{e(l[lang])}</button>' for c, l in CATS) + '</div>'
                    + '<select id="as">' + "".join(f'<option value="{v}">{e(l)}</option>' for v, l in t["sorts"]) + f'</select><span class="cnt" id="an"></span></div>'
                    f'<div class="at"><div class="ar h"><span></span><span>{e(t["cols"][0])}</span><span class="p">{e(t["cols"][1])}</span><span class="c">{e(t["cols"][2])}</span><span class="c c7">{e(t["cols"][3])}</span></div><div id="al"></div></div>'
                    f'<button class="amore" id="am" hidden>{e(t["more"])}</button></section>'
                    + ALLJS.replace("__RATE__", str(RATE[lang])).replace("__CUR__", json.dumps(["", " ₽"] if lang == "ru" else ["$", ""])).replace("__WIKI__", json.dumps(WIKI[lang])).replace("__FOUND__", json.dumps(t["found"]))
                    + f'<p class="note">{e(t["note"])}</p>')
            if lang == "ru":
                out.update(i1=ix["i1"], i7=ix["i7"], up=[(r["n"], r["w"], r["c1"], r["cur"]) for r in sorted([r for r in rows if r["c1"] is not None], key=lambda r: -r["c1"])[:5]],
                           down=[(r["n"], r["w"], r["c1"], r["cur"]) for r in sorted([r for r in rows if r["c1"] is not None], key=lambda r: r["c1"])[:5]])
        alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
        ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": t["h1"], "url": SITE + url, "description": t["desc"], "dateModified": now.isoformat(timespec="seconds")}]
        h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}{GRID_CSS}</style></head>")
        p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) if l in URL else HOME[l] for l in HOME})}\n<main class="mk pg">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
        p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
        p = navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))
        f = os.path.join(ROOT, url.strip("/"), "index.html"); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(p)
    json.dump(out, open(os.path.join(ROOT, "data/market.json"), "w"), ensure_ascii=False)
    if rows:
        img = {}; allr = []
        for r in rows:
            img.setdefault(r["n"], r["i"])
            wu = wiki_url("ru", r["n"]) or ""
            allr.append([r["n"], r["w"], r["cur"], None if r["c1"] is None else round(r["c1"], 1), None if r["c7"] is None else round(r["c7"], 1), r["kind"], wu[len(WIKI["ru"]):].strip("/") if wu else ""])
        json.dump({"t": out["t"], "img": img, "r": allr}, open(os.path.join(ROOT, "data/market-all.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    # sitemap
    sm = os.path.join(ROOT, "sitemap.xml"); xml = open(sm, encoding="utf-8").read(); today = now.date().isoformat()
    for u in URL.values():
        if f"<loc>{SITE}{u}</loc>" not in xml: xml = xml.replace("</urlset>", f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n</urlset>")
        xml = re.sub(r"(<loc>" + re.escape(SITE + u) + r"</loc><lastmod>)[^<]*", lambda m: m.group(1) + today, xml)
    open(sm, "w", encoding="utf-8").write(xml)
    print(len(rows), "rows")


if __name__ == "__main__":
    build(sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else os.path.join(ROOT, "data/hist"))
