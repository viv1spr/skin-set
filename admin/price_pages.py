# -*- coding: utf-8 -*-
"""Страницы «нож CS2 до N ₽ / перчатки CS2 до N ₽» (RU) и «CS2 knife under $N / gloves under $N» (EN).
Запуск: python3 admin/price_pages.py   (данные: data/catalog.json — цены в $ по износам FN..BS)
"""
import json, os, re, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE  # noqa
from budget_pages import money, wiki_url, path as bpath, blog_links  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa

e = lambda s: html.escape(str(s), quote=True)
RATE = {"ru": 90, "en": 1}
WEARS = ["FN", "MW", "FT", "WW", "BS"]
WEARN = {"ru": {"FN": "Прямо с завода", "MW": "Немного поношенное", "FT": "После полевых", "WW": "Поношенное", "BS": "Закалённое в боях"},
         "en": {"FN": "Factory New", "MW": "Minimal Wear", "FT": "Field-Tested", "WW": "Well-Worn", "BS": "Battle-Scarred"}}
LIST = {("ru", "knife"): [4000, 5000, 7000, 10000, 15000], ("ru", "gloves"): [3000, 5000, 10000],
        ("en", "knife"): [50, 75, 100, 150, 200], ("en", "gloves"): [40, 75, 100]}


def slug(lang, kind, n):
    if lang == "ru": return f"/{'nozh' if kind == 'knife' else 'perchatki'}-cs2-do-{n}-rubley/"
    return f"/en/cs2-{'knife' if kind == 'knife' else 'gloves'}-under-{n}-dollars/"


COLORS = {"ru": [("krasnye", "Красные"), ("sinie", "Синие"), ("rozovye", "Розовые"), ("fioletovye", "Фиолетовые"), ("zelenye", "Зелёные"), ("zolotye", "Золотые"), ("oranzhevye", "Оранжевые"), ("biryuzovye", "Бирюзовые"), ("cherno-belye", "Чёрно-белые")],
          "en": [("red", "Red"), ("blue", "Blue"), ("pink", "Pink"), ("purple", "Purple"), ("green", "Green"), ("gold", "Gold"), ("orange", "Orange"), ("turquoise", "Turquoise"), ("black-and-white", "Black & white")]}

T = {
 "ru": dict(
  knife=dict(h1="Нож в CS2 до {B}", title="Нож в КС 2 до {B}: {N} дешёвых ножей с ценами — Skinset",
   desc="Какой нож купить в CS2 до {B}: {N} вариантов от {MIN}. Самые дешёвые {T1}, лучшее качество в бюджете и цены, которые обновляются каждые 4 часа.",
   lead="Нож — самый заметный предмет инвентаря, и купить его можно дешевле, чем кажется. Здесь все ножи CS2, которые сейчас стоят до {B} хотя бы в одном качестве: {N} вариантов, самый дешёвый — {CHEAP} за {MIN}. Для каждого показано лучшее качество, которое укладывается в бюджет.",
   tips_h="Как выбрать нож до {B}", tips=[
    "<b>Тип ножа важнее раскраски.</b> Самые дешёвые сейчас — {T1}: за те же деньги можно взять их в хорошей раскраске, а Karambit или Butterfly в этом бюджете будут разве что в Safari Mesh или Boreal Forest.",
    "<b>Field-Tested — лучший баланс.</b> На ноже потёртости видно меньше, чем на AK или AWP, а разница с Minimal Wear по цене бывает двукратной. <a href=\"/blog/kachestvo-skinov-cs2-fn-mw-ft-ww-bs/\">Подробнее о качестве FN, MW, FT, WW, BS</a>.",
    "<b>Подбирай нож под цвет сета.</b> Даже дешёвый нож смотрится дорого, если перчатки и оружие в той же гамме. Конструктор Skinset закрепит выбранный нож и подберёт к нему остальное.",
   ],
   faq=lambda d: [
    ("Какой самый дешёвый нож в CS2?", f"Сейчас самый доступный — {d['cheap'][0]} за {d['cheap'][1]}. Следом идут " + ", ".join(f"{a} ({b})" for a, b in d['next']) + ". Цены обновляются каждые 4 часа."),
    (f"Какой нож купить до {d['B']}?", f"В этот бюджет укладываются {d['N']} ножей. Если важен вид — бери недорогой тип ножа ({d['types']}) в яркой раскраске в Field-Tested. Если важен престиж — Karambit или Butterfly в простой раскраске."),
    ("Ножи из CS:GO работают в CS2?", "Да, все ножи из CS:GO перенеслись в Counter-Strike 2 без изменений, цены и качество те же."),
   ]),
  gloves=dict(h1="Перчатки в CS2 до {B}", title="Перчатки в КС 2 до {B}: {N} дешёвых перчаток с ценами — Skinset",
   desc="Какие перчатки купить в CS2 до {B}: {N} вариантов от {MIN}. Самые дешёвые {T1}, лучшее качество в бюджете и актуальные цены.",
   lead="Перчатки видно в каждом раунде вместе с ножом, а стоят они нередко дешевле ножа. Здесь все перчатки CS2, которые сейчас можно взять до {B} хотя бы в одном качестве: {N} вариантов, самые дешёвые — {CHEAP} за {MIN}.",
   tips_h="Как выбрать перчатки до {B}", tips=[
    "<b>Бери Field-Tested или Well-Worn.</b> У перчаток износ почти не заметен в игре, а разница в цене между FN и FT бывает в 5–10 раз.",
    "<b>Самые доступные модели</b> сейчас — {T1}. Sport Gloves и Specialist Gloves стоят заметно дороже даже в простых раскрасках.",
    "<b>Перчатки задают цвет сета.</b> Подбирай их вместе с ножом: конструктор Skinset закрепит перчатки и подберёт нож и оружие в той же гамме.",
   ],
   faq=lambda d: [
    ("Какие самые дешёвые перчатки в CS2?", f"Сейчас самые доступные — {d['cheap'][0]} за {d['cheap'][1]}. Следом идут " + ", ".join(f"{a} ({b})" for a, b in d['next']) + "."),
    (f"Какие перчатки купить до {d['B']}?", f"В этот бюджет укладываются {d['N']} вариантов. Чаще всего это {d['types']} — в Field-Tested или Well-Worn."),
    ("Что дешевле — нож или перчатки?", "Самые дешёвые перчатки обычно немного дешевле самого дешёвого ножа, но в среднем перчатки дороже: моделей мало, а редкость выше."),
   ]),
  cols=dict(price="Цена", best="Лучшее в бюджете", from_="от", types="По типам", type="Тип", count="Вариантов", minp="Мин. цена",
            other="Другие бюджеты", colors_k="Ножи по цвету", colors_g="Перчатки по цвету", inv="Полный инвентарь под бюджет", faq="Вопросы и ответы", blog="Статьи по теме",
            cta="Собрать сет вокруг ножа →", cta_g="Собрать сет вокруг перчаток →", home="Главная", upd="Цены обновлены {D}. Показано {S} из {N}.", more="Ещё ножи"),
  short_k="Нож до {B}", short_g="Перчатки до {B}", seo_h="Ножи и перчатки по цене",
 ),
 "en": dict(
  knife=dict(h1="CS2 knife under {B}", title="Cheapest CS2 knives under {B}: {N} knives with prices — Skinset",
   desc="Which CS2 knife to buy under {B}: {N} options from {MIN}. The cheapest {T1}, the best wear that fits your budget, prices updated every 4 hours.",
   lead="A knife is the most visible item in any loadout, and it can cost less than you think. Here are all CS2 knives that currently sell under {B} in at least one wear: {N} options, the cheapest being {CHEAP} at {MIN}. Each card shows the best wear that fits the budget.",
   tips_h="How to pick a knife under {B}", tips=[
    "<b>Knife type matters more than finish.</b> The cheapest right now are {T1}: for the same money you get them in a nice finish, while a Karambit or Butterfly at this budget means Safari Mesh or Boreal Forest at best.",
    "<b>Field-Tested is the sweet spot.</b> Wear shows less on a knife than on an AK or AWP, and Minimal Wear can cost twice as much. <a href=\"/en/blog/kachestvo-skinov-cs2-fn-mw-ft-ww-bs/\">More on FN, MW, FT, WW, BS</a>.",
    "<b>Match the knife to your loadout color.</b> Even a cheap knife looks expensive when the gloves and weapons share its palette. The Skinset builder locks the knife and fills in the rest.",
   ],
   faq=lambda d: [
    ("What is the cheapest knife in CS2?", f"Right now the cheapest is {d['cheap'][0]} at {d['cheap'][1]}, followed by " + ", ".join(f"{a} ({b})" for a, b in d['next']) + ". Prices update every 4 hours."),
    (f"Which knife should I buy under {d['B']}?", f"{d['N']} knives fit this budget. If looks matter most, take a cheaper knife type ({d['types']}) in a bright finish in Field-Tested. For prestige, a Karambit or Butterfly in a basic finish."),
    ("Do CS:GO knives work in CS2?", "Yes. Every CS:GO knife carried over to Counter-Strike 2 unchanged, with the same wear and value."),
   ]),
  gloves=dict(h1="CS2 gloves under {B}", title="Cheapest CS2 gloves under {B}: {N} gloves with prices — Skinset",
   desc="Which CS2 gloves to buy under {B}: {N} options from {MIN}. The cheapest {T1}, the best wear within budget and live prices.",
   lead="Gloves are on screen every round next to your knife, and they are often cheaper than one. Here are all CS2 gloves that currently sell under {B} in at least one wear: {N} options, the cheapest being {CHEAP} at {MIN}.",
   tips_h="How to pick gloves under {B}", tips=[
    "<b>Go for Field-Tested or Well-Worn.</b> Glove wear is barely visible in game, while Factory New can cost 5–10× more than FT.",
    "<b>The most affordable models</b> right now are {T1}. Sport and Specialist Gloves cost much more even in plain finishes.",
    "<b>Gloves set the color of the loadout.</b> Pick them together with the knife: the Skinset builder locks the gloves and matches a knife and weapons in the same palette.",
   ],
   faq=lambda d: [
    ("What are the cheapest gloves in CS2?", f"Right now the cheapest are {d['cheap'][0]} at {d['cheap'][1]}, followed by " + ", ".join(f"{a} ({b})" for a, b in d['next']) + "."),
    (f"Which gloves should I buy under {d['B']}?", f"{d['N']} gloves fit this budget, mostly {d['types']} in Field-Tested or Well-Worn."),
    ("Are gloves cheaper than knives?", "The cheapest gloves are usually a bit cheaper than the cheapest knife, but on average gloves cost more: there are fewer models and they are rarer."),
   ]),
  cols=dict(price="Price", best="Best wear in budget", from_="from", types="By type", type="Type", count="Options", minp="Min price",
            other="Other budgets", colors_k="Knives by color", colors_g="Gloves by color", inv="Full loadout by budget", faq="FAQ", blog="Related articles",
            cta="Build a loadout around a knife →", cta_g="Build a loadout around gloves →", home="Home", upd="Prices updated {D}. Showing {S} of {N}.", more="More knives"),
  short_k="Knife under {B}", short_g="Gloves under {B}", seo_h="Knives and gloves by price",
 ),
}

CSS = """
.pp{max-width:1180px;margin:0 auto;padding:22px 24px 60px}
.pp .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:12px}.pp .crumbs a{color:var(--soft)}
.pp h1{margin:6px 0 10px;font:700 clamp(1.9rem,4vw,3rem)/1.05 var(--hud);text-transform:uppercase}
.pp .lead{color:var(--soft);font-size:1.04rem;max-width:860px;margin:0 0 8px}
.pp .upd{color:var(--dim);font-size:.85rem;margin:0 0 18px}
.pp h2{margin:32px 0 12px;font:700 1.4rem/1.1 var(--hud);text-transform:uppercase}
.pp h2::before{content:"";display:block;width:40px;height:4px;background:var(--pick,#e8402a);margin-bottom:10px}
.pp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.pp-c{display:flex;flex-direction:column;min-width:0;overflow:hidden;background:linear-gradient(170deg,rgba(255,255,255,.06),rgba(255,255,255,.015));border:1px solid var(--line2,rgba(255,255,255,.14));border-bottom:3px solid var(--rc,#8847ff);padding:10px 12px 12px;color:var(--ink,#fff);text-decoration:none}
.pp-c:hover{border-color:rgba(255,255,255,.35)}
.pp-c .im{height:96px;display:grid;place-items:center;margin-bottom:6px}.pp-c img{max-width:100%;max-height:96px;object-fit:contain;filter:drop-shadow(0 8px 10px rgba(0,0,0,.55))}
.pp-c .w{font-size:.78rem;color:var(--soft)}.pp-c b{font:700 1.02rem/1.15 var(--hud);text-transform:uppercase}
.pp-c .pr{margin-top:auto;padding-top:8px;display:flex;justify-content:space-between;align-items:baseline;gap:6px;font-size:.82rem;color:var(--soft)}
.pp-c .pr em{font:700 1.05rem var(--hud);font-style:normal;color:#ffd36a}
.pp table{width:100%;border-collapse:collapse;font-size:.92rem}.pp th,.pp td{padding:8px 10px;border-bottom:1px solid var(--line,rgba(255,255,255,.08));text-align:left}.pp th{color:var(--dim);font-weight:500}
.pp ul.tips{padding-left:20px;color:var(--soft);display:grid;gap:8px;max-width:900px}.pp ul.tips a,.pp .faq a{color:#66c0f4}
.pp .faq h3{margin:18px 0 6px;font:600 1.05rem var(--hud)}.pp .faq p{margin:0;color:var(--soft);max-width:900px}
.pp .chips{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}.pp .chips a{display:inline-block;padding:7px 12px;border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--ink,#fff);text-decoration:none;font-size:.88rem}
.pp .chips a.on{border-color:#e8402a;background:rgba(232,64,42,.15)}.pp .chips a:hover{border-color:rgba(255,255,255,.4)}
.pp .cta{display:inline-block;margin-top:18px;padding:14px 22px;background:linear-gradient(90deg,#e8402a,#ff6a3d);color:#fff;font:700 .9rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-decoration:none}
@media(max-width:600px){.pp{padding:16px 14px 40px}.pp-grid{grid-template-columns:repeat(2,1fr);gap:8px}.pp-c .im{height:72px}.pp-c img{max-height:72px}.pp-c b{font-size:.9rem}}
"""
RC = ["#b0c3d9", "#5e98d9", "#4b69ff", "#8847ff", "#d32ce6", "#eb4b4b", "#e4ae39", "#e4ae39"]
MAXC = 120


def imgurl(i):
    return i if i.startswith("http") else "https://community.akamai.steamstatic.com/economy/image/" + i + "/360fx360f"


def page(lang, kind, n, cat, date):
    t = T[lang]; k = t[kind]; c = t["cols"]
    B = money(lang, n); cap = n / RATE[lang]
    rows = []
    for x in cat:
        if x["c"] != kind: continue
        ps = [(w, v) for w, v in zip(WEARS, x["p"]) if v]
        fit = [(w, v) for w, v in ps if v <= cap]
        if not fit: continue
        best = fit[0]; low = min(v for _, v in ps)
        rows.append(dict(x=x, best=best, low=low))
    rows.sort(key=lambda r: (r["best"][1], r["low"]))
    N = len(rows)
    fm = lambda usd: money(lang, usd * RATE[lang])
    nm = lambda r: r["x"]["n"] + (f" ({r['x']['ph']})" if r["x"].get("ph") else "")
    bytype = {}
    for r in rows: bytype.setdefault(r["x"]["w"], []).append(r["low"])
    types = sorted(bytype.items(), key=lambda kv: min(kv[1]))
    tnames = ", ".join(w for w, _ in types[:4])
    fmt = dict(B=B, N=N, MIN=fm(rows[0]["low"]), CHEAP=nm(rows[0]), T1=tnames)
    url = slug(lang, kind, n)
    cards = []
    for r in rows[:MAXC]:
        x = r["x"]; wu = wiki_url(lang, x["n"]); w, v = r["best"]
        inner = (f'<div class="im"><img src="{e(imgurl(x["i"]))}" alt="{e(nm(r))}" loading="lazy" width="160" height="96"></div>'
                 f'<span class="w">{e(x["w"])}</span><b>{e(x["s"] + (" · " + x["ph"] if x.get("ph") else ""))}</b>'
                 f'<div class="pr"><span title="{e(WEARN[lang][w])}">{w}</span><em>{e(fm(v))}</em></div>')
        tag = f'<a class="pp-c" href="{wu}"' if wu else '<div class="pp-c"'
        cards.append(f'{tag} style="--rc:{RC[min(x.get("r", 6), 7)]}">{inner}</{"a" if wu else "div"}>')
    d = dict(B=B, N=N, cheap=(nm(rows[0]), fm(rows[0]["low"])), next=[(nm(r), fm(r["low"])) for r in rows[1:4]], types=tnames)
    faq = k["faq"](d)
    other_k = [(slug(lang, kind, m), (t["short_k"] if kind == "knife" else t["short_g"]).format(B=money(lang, m)), m == n) for m in LIST[(lang, kind)]]
    other_o = [(slug(lang, ok, m), (t["short_k"] if ok == "knife" else t["short_g"]).format(B=money(lang, m)), False) for ok in ("knife", "gloves") if ok != kind for m in LIST[(lang, ok)]]
    colpages = [(f"/{s}-{'nozhi' if kind == 'knife' else 'perchatki'}-cs2/" if lang == "ru" else f"/en/{s}-{'knives' if kind == 'knife' else 'gloves'}-cs2/", l) for s, l in COLORS[lang]]
    invb = [1000, 3000, 5000, 10000, 30000] if lang == "ru" else [15, 50, 100, 250, 500]
    blog = blog_links(lang, ["samye-deshevye-nozhi-cs2", "kachestvo-skinov-cs2-fn-mw-ft-ww-bs", "perchatki-k-nozhu-doppler-po-fazam"])
    title = k["title"].format(**fmt); desc = k["desc"].format(**fmt); h1 = k["h1"].format(**fmt)
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": c["home"], "item": SITE + HOME[lang]}, {"@type": "ListItem", "position": 2, "name": h1, "item": SITE + url}]},
          {"@context": "https://schema.org", "@type": "ItemList", "name": h1, "numberOfItems": N, "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": nm(r)} for i, r in enumerate(rows[:20])]}]
    h = head(lang, title, desc, SITE + url, f'<link rel="alternate" hreflang="{"ru" if lang == "ru" else "en"}" href="{SITE}{url}">', ld).replace("</head>", f"<style>{CSS}</style></head>")
    builder = HOME[lang] + ("#" if False else "")
    page = h + f"""
<body>
{header(lang, {l: (url if l == lang else HOME[l]) for l in HOME})}
<main class="pp">
<nav class="crumbs"><a href="{HOME[lang]}">{e(c['home'])}</a> › {e(h1)}</nav>
<h1>{e(h1)}</h1>
<p class="lead">{e(k['lead'].format(**fmt))}</p>
<p class="upd">{e(c['upd'].format(D=date, S=min(N, MAXC), N=N))}</p>
<div class="pp-grid">{''.join(cards)}</div>
<h2>{e(c['types'])}</h2>
<table><thead><tr><th>{e(c['type'])}</th><th>{e(c['count'])}</th><th>{e(c['minp'])}</th></tr></thead><tbody>{''.join(f'<tr><td>{e(w)}</td><td>{len(v)}</td><td>{e(fm(min(v)))}</td></tr>' for w, v in types)}</tbody></table>
<h2>{e(k['tips_h'].format(**fmt))}</h2>
<ul class="tips">{''.join(f'<li>{x.format(**fmt)}</li>' for x in k['tips'])}</ul>
<a class="cta" href="{builder}">{e(c['cta'] if kind == 'knife' else c['cta_g'])}</a>
<h2>{e(c['other'])}</h2>
<ul class="chips">{''.join(f'<li><a href="{u}"{" class=on" if on else ""}>{e(l)}</a></li>' for u, l, on in other_k + other_o)}</ul>
<h2>{e(c['colors_k'] if kind == 'knife' else c['colors_g'])}</h2>
<ul class="chips">{''.join(f'<li><a href="{u}">{e(l)}</a></li>' for u, l in colpages)}</ul>
<h2>{e(c['inv'])}</h2>
<ul class="chips">{''.join(f'<li><a href="{bpath(lang, m)}">{e(money(lang, m))}</a></li>' for m in invb)}</ul>
<h2>{e(c['faq'])}</h2>
<div class="faq">{''.join(f'<h3>{e(q)}</h3><p>{a}</p>' for q, a in faq)}</div>
{(f'<h2>{e(c["blog"])}</h2><ul class="chips">' + ''.join(f'<li><a href="{u}">{e(l)}</a></li>' for u, l in blog) + '</ul>') if blog else ''}
</main>
<footer><p>{e(FOOT[lang])}</p></footer>
</body>
</html>
"""
    page = page.replace("</body>", LANG_JS + "</body>", 1)
    return url, navmore.fix(page)


def links_line(lang):
    t = T[lang]
    items = [(slug(lang, k, m), (t["short_k"] if k == "knife" else t["short_g"]).format(B=money(lang, m))) for k in ("knife", "gloves") for m in LIST[(lang, k)]]
    return f'<p class="seo-prices"><b>{e(t["seo_h"])}:</b> ' + " · ".join(f'<a href="{u}">{e(l)}</a>' for u, l in items) + "</p>"


def main():
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json")))
    d = datetime.date.today(); made = []
    for (lang, kind), lst in LIST.items():
        date = d.strftime("%d.%m.%Y" if lang == "ru" else "%b %d, %Y")
        for n in lst:
            url, html_ = page(lang, kind, n, cat, date)
            out = os.path.join(ROOT, url.strip("/"), "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(html_); made.append(url)
    # ссылки с главной, бюджетных и цветовых страниц ножей/перчаток
    import glob
    targets = {"ru": ["index.html"] + glob.glob(os.path.join(ROOT, "inventar-cs2-za-*/index.html")) + glob.glob(os.path.join(ROOT, "*-nozhi-cs2/index.html")) + glob.glob(os.path.join(ROOT, "*-perchatki-cs2/index.html")) + [os.path.join(ROOT, "blog/samye-deshevye-nozhi-cs2/index.html")],
               "en": ["en/index.html"] + glob.glob(os.path.join(ROOT, "en/cs2-loadout-under-*/index.html")) + glob.glob(os.path.join(ROOT, "en/*-knives-cs2/index.html")) + glob.glob(os.path.join(ROOT, "en/*-gloves-cs2/index.html")) + [os.path.join(ROOT, "en/blog/samye-deshevye-nozhi-cs2/index.html")]}
    nl = 0
    for lang, fs in targets.items():
        line = links_line(lang)
        for f in fs:
            f = f if os.path.isabs(f) else os.path.join(ROOT, f)
            if not os.path.exists(f): continue
            s = open(f, encoding="utf-8").read(); o = s
            if 'class="seo-prices"' in s:
                s = re.sub(r'<p class="seo-prices">.*?</p>', line, s, count=1, flags=re.S)
            elif '<p class="seo-budgets">' in s:
                s = re.sub(r'(<p class="seo-budgets">.*?</p>)', lambda m: m.group(1) + "\n" + line, s, count=1, flags=re.S)
            elif "</article>" in s:
                s = s.replace("</article>", line + "</article>", 1)
            elif '<ul class="seo-chips">' in s:
                i = s.rfind('</ul>', 0, s.find("</section>", s.find('<section class="seo'))) + 5
                s = s[:i] + "\n" + line + s[i:]
            if s != o: open(f, "w", encoding="utf-8").write(s); nl += 1
    sm = os.path.join(ROOT, "sitemap.xml"); x = open(sm, encoding="utf-8").read()
    add = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for p in made if f"<loc>{SITE}{p}</loc>" not in x)
    x = re.sub(r"(<loc>" + re.escape(SITE) + r"/(?:en/)?(?:nozh|perchatki|cs2-knife|cs2-gloves)-[^<]*</loc><lastmod>)[^<]*", lambda m: m.group(1) + d.isoformat(), x)
    open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>"))
    print(len(made), "pages; links in", nl, "files")


if __name__ == "__main__":
    main()
