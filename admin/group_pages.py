# -*- coding: utf-8 -*-
"""Страницы «скины на AWP / AK-47 / …» и «коллекции и кейсы CS2» (RU + EN).
Запуск: python3 admin/group_pages.py   (данные: data/catalog.json; идемпотентно)
"""
import json, os, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(ROOT, "admin"))
from price_pages import CSS, RC, imgurl, WEARS, WEARN, SETL, e, money, wiki_url, head, header, FOOT, HOME, SITE, LANG_JS, navmore, csmoney, quote, bpath  # noqa

RATE = {"ru": 90, "en": 1}
RAR = {"ru": ["Ширпотреб", "Промышленное", "Армейское", "Запрещённое", "Засекреченное", "Тайное", "Экстраординарное", "Контрабанда"],
       "en": ["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "Extraordinary", "Contraband"]}
WEAPONS = [("AK-47", "ak-47"), ("AWP", "awp"), ("M4A4", "m4a4"), ("M4A1-S", "m4a1-s"), ("Desert Eagle", "desert-eagle"), ("USP-S", "usp-s"),
           ("Glock-18", "glock-18"), ("Karambit", "karambit"), ("Butterfly Knife", "butterfly"), ("M9 Bayonet", "m9-bayonet"), ("Sport Gloves", "sport-gloves")]
EXTRA_CSS = """.gp-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 16px}.gp-tabs a{padding:7px 12px;border:1px solid var(--line2,rgba(255,255,255,.18));color:var(--ink,#fff);text-decoration:none;font:600 .78rem/1 var(--hud);letter-spacing:.06em;text-transform:uppercase}.gp-tabs a.on,.gp-tabs a:hover{border-color:#ff159a;color:#ff5cb8}
.pp-l{display:flex;flex-direction:column;flex:1;color:inherit;text-decoration:none;min-width:0}.pp-l .pr{margin-top:auto;padding-top:8px;display:flex;justify-content:space-between;align-items:baseline;gap:6px;font-size:.82rem;color:var(--soft)}.pp-l .pr em{font:700 1.05rem var(--hud);font-style:normal;color:#ffd36a}
.pp-btn{display:grid;gap:6px;margin-top:10px}.pp-btn a{display:flex;align-items:center;justify-content:center;min-height:32px;padding:6px 8px;font:600 .72rem/1.1 var(--hud);letter-spacing:.06em;text-transform:uppercase;text-decoration:none;text-align:center}
.pp-btn .b-csm{background:linear-gradient(90deg,#ff159a,#c40f78);color:#fff;border:1px solid #ff159a}.pp-btn .b-set{background:transparent;color:var(--ink,#fff);border:1px solid var(--line2,rgba(255,255,255,.22))}
.gp-list{columns:3 260px;gap:18px;list-style:none;padding:0}.gp-list li{break-inside:avoid;padding:5px 0;border-bottom:1px solid var(--line,rgba(255,255,255,.08))}.gp-list a{color:var(--ink,#fff)}.gp-list small{color:var(--soft);margin-left:6px}"""


def wurl(lang, slug):
    return f"/skiny-na-{slug}/" if lang == "ru" else f"/en/cs2-{slug}-skins/"


def cslug(k):
    return re.sub(r"[^a-z0-9]+", "-", k.lower().replace("&", "and")).strip("-")


def curl(lang, k=None):
    base = "/kollekcii-i-kejsy-cs2/" if lang == "ru" else "/en/cs2-collections-and-cases/"
    return base + (cslug(k) + "/" if k else "")


def low(x):
    v = [p for p in x["p"] if p]
    return min(v) if v else None


def bestw(x):
    ps = [(w, v) for w, v in zip(WEARS, x["p"]) if v]
    return min(ps, key=lambda z: z[1]) if ps else (None, None)


def pl(n, a, b, c):
    n = abs(n) % 100; n1 = n % 10
    return c if 10 < n < 20 else a if n1 == 1 else b if 1 < n1 < 5 else c


def card(lang, x):
    w, v = bestw(x); n = x["n"] + (f" ({x['ph']})" if x.get("ph") and f"({x['ph']})" not in x["n"] else "")
    wu = wiki_url(lang, n)
    inner = (f'<div class="im"><img src="{e(imgurl(x["i"]))}" alt="{e(n)}" loading="lazy" width="160" height="96"></div>'
             f'<span class="w">{e(x["w"])} · {e(RAR[lang][min(x.get("r", 0), 7)])}</span><b>{e(x["s"] + (" · " + x["ph"] if x.get("ph") else ""))}</b>'
             f'<div class="pr"><span title="{e(WEARN[lang].get(w, ""))}">{w or ""}</span><em>{e(money(lang, v * RATE[lang])) if v else "—"}</em></div>')
    lk = f'<a class="pp-l" href="{wu}">{inner}</a>' if wu else f'<div class="pp-l">{inner}</div>'
    star = "★ " if x["c"] in ("knife", "gloves") else ""
    sq = quote(f"{star}{x['w']}|{x['s']}" + (f" ({x['ph']})" if x.get("ph") else ""), safe="")
    btn = (f'<div class="pp-btn"><a class="b-csm" href="{e(csmoney.url(n, w))}" {csmoney.REL}>{e(csmoney.LABEL[lang])}</a>'
           f'<a class="b-set" href="{HOME[lang]}?set={sq}">{e(SETL[lang])}</a></div>')
    return f'<div class="pp-c" style="--rc:{RC[min(x.get("r", 0), 7)]}">{lk}{btn}</div>'


def faq_html(faq):
    return "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq)


def build(lang, url, title, desc, h1, crumbs, lead, body, faq, ld_items):
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]},
          {"@context": "https://schema.org", "@type": "ItemList", "name": h1, "numberOfItems": len(ld_items), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n} for i, n in enumerate(ld_items[:30])]}]
    h = head(lang, title, desc, SITE + url, f'<link rel="alternate" hreflang="{"ru" if lang == "ru" else "en"}" href="{SITE}{url}">', ld).replace("</head>", f"<style>{CSS}{EXTRA_CSS}</style></head>")
    nav = " › ".join(f'<a href="{u}">{e(n)}</a>' for n, u in crumbs[:-1]) + f" › {e(crumbs[-1][0])}"
    page = h + f"""
<body>
{header(lang, {l: (url if l == lang else HOME[l]) for l in HOME})}
<main class="pp">
<nav class="crumbs">{nav}</nav>
<h1>{e(h1)}</h1>
<p class="lead">{e(lead)}</p>
{body}
<h2>{"Вопросы и ответы" if lang == "ru" else "FAQ"}</h2>
<div class="faq">{faq_html(faq)}</div>
</main>
<footer><p>{e(FOOT[lang])}</p></footer>
</body>
</html>
"""
    page = page.replace("</body>", LANG_JS + "</body>", 1)
    out = os.path.join(ROOT, url.strip("/"), "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(navmore.fix(page))
    return url


def weapon_pages(lang, cat, date):
    made = []
    m = lambda v: money(lang, v * RATE[lang])
    for wname, slug in WEAPONS:
        xs = [x for x in cat if x["w"] == wname and low(x)]
        if len(xs) < 5: continue
        xs.sort(key=low)
        top = sorted(xs, key=lambda x: -max(p for p in x["p"] if p))
        nm = lambda x: x["s"] + (f" ({x['ph']})" if x.get("ph") else "")
        url = wurl(lang, slug)
        tabs = '<div class="gp-tabs">' + "".join(f'<a href="{wurl(lang, s2)}"{" class=on" if s2 == slug else ""}>{e(w2)}</a>' for w2, s2 in WEAPONS) + "</div>"
        cheap = ", ".join(f"{nm(x)} ({m(low(x))})" for x in xs[:3])
        pricey = ", ".join(f"{nm(x)} ({m(max(p for p in x['p'] if p))})" for x in top[:3])
        if lang == "ru":
            title = f"Скины на {wname} в КС 2: все раскраски с ценами, от дешёвых к дорогим — Skinset"
            desc = f"Все скины на {wname} в CS2 с ценами: самые дешёвые от {m(low(xs[0]))} ({nm(xs[0])}), самые дорогие — {nm(top[0])}. Цены по качеству, где купить и с чем собрать сет."
            h1 = f"Скины на {wname} в CS2: все раскраски и цены"
            lead = f"Здесь все {len(xs)} скинов на {wname} из базы Skinset — от самых дешёвых к самым дорогим. Самые доступные сейчас: {cheap}. Для каждого показано самое дешёвое качество и цена; нажми на скин, чтобы увидеть цены по всем качествам. Цены обновлены {date}."
            body = (tabs + f'<div class="pp-grid">{"".join(card(lang, x) for x in xs[:120])}</div>'
                    f'<h2>Самые дорогие скины на {e(wname)}</h2><p>{e(pricey)}. Цена самых дорогих скинов зависит от качества и float: Factory New стоит в разы дороже Battle-Scarred.</p>'
                    f'<h2>Как выбрать скин на {e(wname)}</h2><p>Сначала реши, какой цвет у всего сета: скин на {e(wname)} смотрится лучше, если нож и перчатки в той же гамме. Конструктор Skinset закрепит выбранный скин и подберёт остальные слоты под бюджет. Для экономии бери Field-Tested: разница с Minimal Wear в цене часто двукратная, а в игре её почти не видно.</p>'
                    f'<p><a class="cta" href="/">Собрать сет в конструкторе →</a></p>')
            faq = [(f"Какой самый дешёвый скин на {wname}?", f"Сейчас самые дешёвые: {cheap}. Цены обновляются каждые 4 часа."),
                   (f"Какой самый дорогой скин на {wname}?", f"Самые дорогие: {pricey}."),
                   (f"Сколько всего скинов на {wname} в CS2?", f"В базе Skinset {len(xs)} скинов на {wname}. Все скины из CS:GO перенеслись в CS2 без изменений.")]
            crumbs = [("Главная", "/"), ("Скины CS2", "/skiny/"), (f"Скины на {wname}", url)]
        else:
            title = f"All {wname} skins in CS2: {len(xs)} finishes with prices, cheapest to most expensive — Skinset"
            desc = f"Every {wname} skin in CS2 with prices: cheapest from {m(low(xs[0]))} ({nm(xs[0])}), most expensive {nm(top[0])}. Prices by wear, where to buy and loadouts."
            h1 = f"CS2 {wname} skins: every finish with prices"
            lead = f"All {len(xs)} {wname} skins in the Skinset database, sorted from cheapest to most expensive. The cheapest right now: {cheap}. Each card shows the cheapest wear and its price; click a skin for prices in every wear. Prices updated {date}."
            body = (tabs + f'<div class="pp-grid">{"".join(card(lang, x) for x in xs[:120])}</div>'
                    f'<h2>Most expensive {e(wname)} skins</h2><p>{e(pricey)}. Prices at the top depend heavily on wear and float: Factory New can cost several times more than Battle-Scarred.</p>'
                    f'<h2>How to pick a {e(wname)} skin</h2><p>Decide on the color of the whole loadout first: a {e(wname)} skin looks better when the knife and gloves share its palette. The Skinset builder locks the skin you pick and fills the other slots for your budget. To save money, go for Field-Tested: Minimal Wear often costs twice as much and the difference is barely visible in game.</p>'
                    f'<p><a class="cta" href="/en/">Build a loadout →</a></p>')
            faq = [(f"What is the cheapest {wname} skin?", f"The cheapest right now: {cheap}. Prices update every 4 hours."),
                   (f"What is the most expensive {wname} skin?", f"At the top: {pricey}."),
                   (f"How many {wname} skins are there in CS2?", f"The Skinset database has {len(xs)} {wname} skins. All CS:GO skins carried over to CS2 unchanged.")]
            crumbs = [("Home", "/en/"), ("CS2 skins", "/en/skins/"), (f"{wname} skins", url)]
        made.append(build(lang, url, title, desc, h1, crumbs, lead, body, faq, [x["n"] for x in xs]))
    return made


def collection_pages(lang, cat, date):
    made = []
    m = lambda v: money(lang, v * RATE[lang])
    groups = {}
    for x in cat:
        k = x.get("k")
        if k and low(x) and ("Case" in k or "Collection" in k) and "Souvenir" not in k:
            groups.setdefault(k, []).append(x)
    groups = {k: v for k, v in groups.items() if len(v) >= 5}
    nm = lambda x: x["n"] + (f" ({x['ph']})" if x.get("ph") and f"({x['ph']})" not in x["n"] else "")
    index = []
    for k, xs in sorted(groups.items()):
        xs.sort(key=lambda x: (-min(x.get("r", 0), 6), -(low(x) or 0)))
        url = curl(lang, k)
        is_case = "Case" in k
        guns = [x for x in xs if x["c"] not in ("knife", "gloves")]
        rare = [x for x in xs if x["c"] in ("knife", "gloves")]
        top = sorted(xs, key=lambda x: -max(p for p in x["p"] if p))[:3]
        cheap = sorted(xs, key=low)[:3]
        if lang == "ru":
            kind = "кейса" if is_case else "коллекции"
            title = f"{k}: все скины {kind}, что выпадает и цены (КС 2) — Skinset"
            desc = f"Что выпадает из {k} в CS2: {len(guns)} {pl(len(guns), "скин", "скина", "скинов")} на оружие" + (f" и {len(rare)} {pl(len(rare), 'редкий нож или перчатки', 'редких ножа/перчаток', 'редких ножей/перчаток')}" if rare else "") + f". Самый дорогой — {nm(top[0])}, самые дешёвые от {m(low(cheap[0]))}."
            h1 = f"{k}: все скины и цены"
            lead = (f"{'Из кейса' if is_case else 'В коллекции'} {k} — {len(guns)} {pl(len(guns), "скин", "скина", "скинов")} на оружие" + (f" и {len(rare)} {pl(len(rare), 'редкий предмет', 'редких предмета', 'редких предметов')} (ножи или перчатки)" if rare else "") +
                    f". Самые дорогие: {', '.join(f'{nm(x)} ({m(max(p for p in x[chr(112)] if p))})' for x in top)}. Самые дешёвые: {', '.join(f'{nm(x)} ({m(low(x))})' for x in cheap)}. Цены обновлены {date}.")
            faq = [(f"Что выпадает из {k}?", f"{len(guns)} {pl(len(guns), "скин", "скина", "скинов")} на оружие" + (f" и {len(rare)} редких ножей или перчаток" if rare else "") + ". Полный список с ценами — на этой странице, от самых редких к обычным."),
                   (f"Какой самый дорогой скин в {k}?", f"{nm(top[0])} — от {m(max(p for p in top[0]['p'] if p))} в лучшем качестве."),
                   (f"Сколько стоят скины из {k}?", f"От {m(low(cheap[0]))} ({nm(cheap[0])}) до {m(max(p for p in top[0]['p'] if p))}. Цена зависит от редкости и качества (FN, MW, FT, WW, BS).")]
            crumbs = [("Главная", "/"), ("Коллекции и кейсы", curl(lang)), (k, url)]
        else:
            kind = "case" if is_case else "collection"
            title = f"{k}: all skins, drops and prices (CS2) — Skinset"
            desc = f"What drops from {k} in CS2: {len(guns)} weapon skins" + (f" and {len(rare)} rare knives/gloves" if rare else "") + f". Most expensive: {nm(top[0])}; cheapest from {m(low(cheap[0]))}."
            h1 = f"{k}: all skins and prices"
            lead = (f"The {k} contains {len(guns)} weapon skins" + (f" plus {len(rare)} rare special items (knives or gloves)" if rare else "") +
                    f". Most expensive: {', '.join(f'{nm(x)} ({m(max(p for p in x[chr(112)] if p))})' for x in top)}. Cheapest: {', '.join(f'{nm(x)} ({m(low(x))})' for x in cheap)}. Prices updated {date}.")
            faq = [(f"What drops from {k}?", f"{len(guns)} weapon skins" + (f" and {len(rare)} rare knives or gloves" if rare else "") + ". The full list with prices is on this page, from rarest to most common."),
                   (f"What is the most expensive skin in {k}?", f"{nm(top[0])}, from {m(max(p for p in top[0]['p'] if p))} in the best wear."),
                   (f"How much do {k} skins cost?", f"From {m(low(cheap[0]))} ({nm(cheap[0])}) up to {m(max(p for p in top[0]['p'] if p))}. Price depends on rarity and wear (FN, MW, FT, WW, BS).")]
            crumbs = [("Home", "/en/"), ("Collections and cases", curl(lang)), (k, url)]
        body = (f'<div class="pp-grid">{"".join(card(lang, x) for x in guns[:120])}</div>' +
                (f'<h2>{"Редкие предметы (ножи и перчатки)" if lang == "ru" else "Rare special items (knives and gloves)"}</h2><div class="pp-grid">{"".join(card(lang, x) for x in sorted(rare, key=lambda x: -(low(x) or 0))[:60])}</div>' if rare else "") +
                f'<p><a class="cta" href="{curl(lang)}">{"← Все коллекции и кейсы" if lang == "ru" else "← All collections and cases"}</a></p>')
        made.append(build(lang, url, title, desc, h1, crumbs, lead, body, faq, [nm(x) for x in xs]))
        index.append((k, url, len(xs), max(max(p for p in x["p"] if p) for x in xs)))
    # хаб
    url = curl(lang)
    cases = [r for r in index if "Case" in r[0]]; cols = [r for r in index if "Case" not in r[0]]
    lst = lambda rows: '<ul class="gp-list">' + "".join(f'<li><a href="{u}">{e(k)}</a><small>{n} {pl(n, "скин", "скина", "скинов") if lang == "ru" else "skins"}</small></li>' for k, u, n, _ in rows) + "</ul>"
    if lang == "ru":
        body = f'<h2>Кейсы CS2</h2>{lst(cases)}<h2>Коллекции CS2</h2>{lst(cols)}'
        faq = [("Чем кейс отличается от коллекции?", "Кейс открывается ключом, и из него может выпасть редкий нож или перчатки. Скины коллекций выпадают после матчей или в сувенирных наборах, ножей в них нет."),
               ("Где посмотреть, что выпадает из кейса?", "Открой нужный кейс в списке: там все скины с ценами, от самых редких к обычным.")]
        made.append(build(lang, url, "Коллекции и кейсы CS2: что выпадает из каждого кейса и цены скинов — Skinset",
                          f"Все {len(cases)} {pl(len(cases), 'кейс', 'кейса', 'кейсов')} и {len(cols)} {pl(len(cols), 'коллекция', 'коллекции', 'коллекций')} CS2: что выпадает, редкие ножи и перчатки, цены скинов по качеству.",
                          "Коллекции и кейсы CS2", [("Главная", "/"), ("Коллекции и кейсы", url)],
                          f"Все кейсы и коллекции CS2 из базы Skinset: {len(cases)} {pl(len(cases), 'кейс', 'кейса', 'кейсов')} и {len(cols)} {pl(len(cols), 'коллекция', 'коллекции', 'коллекций')}. Открой любой — увидишь все скины, редкие ножи и перчатки и актуальные цены.", body, faq, [r[0] for r in index]))
    else:
        body = f'<h2>CS2 cases</h2>{lst(cases)}<h2>CS2 collections</h2>{lst(cols)}'
        faq = [("What is the difference between a case and a collection?", "A case is opened with a key and can drop a rare knife or gloves. Collection skins drop after matches or in souvenir packages and have no knives."),
               ("Where can I see what drops from a case?", "Open the case in the list: it shows every skin with prices, from rarest to most common.")]
        made.append(build(lang, url, "CS2 collections and cases: what drops from every case, with prices — Skinset",
                          f"All {len(cases)} CS2 cases and {len(cols)} collections: what drops, rare knives and gloves, skin prices by wear.",
                          "CS2 collections and cases", [("Home", "/en/"), ("Collections and cases", url)],
                          f"Every CS2 case and collection in the Skinset database: {len(cases)} cases and {len(cols)} collections. Open any of them to see all skins, rare knives and gloves, and current prices.", body, faq, [r[0] for r in index]))
    return made


def main():
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json")))
    d = datetime.date.today(); made = []
    for lang in ("ru", "en"):
        date = d.strftime("%d.%m.%Y" if lang == "ru" else "%b %d, %Y")
        made += weapon_pages(lang, cat, date) + collection_pages(lang, cat, date)
    for lang, f in (("ru", "skiny/index.html"), ("en", "en/skins/index.html")):
        p = os.path.join(ROOT, f)
        if not os.path.exists(p): continue
        h = open(p, encoding="utf-8").read()
        blk = ('<section class="gp-hub" style="max-width:1200px;margin:30px auto;padding:0 20px"><h2>' + ("Скины по оружию" if lang == "ru" else "Skins by weapon") + '</h2><p class="gp-tabs" style="display:flex;flex-wrap:wrap;gap:8px">'
               + "".join(f'<a href="{wurl(lang, s2)}" style="padding:7px 12px;border:1px solid rgba(255,255,255,.2);color:#fff;text-decoration:none">{e(w2)}</a>' for w2, s2 in WEAPONS)
               + f'</p><p><a href="{curl(lang)}">' + ("Коллекции и кейсы CS2: что выпадает и цены →" if lang == "ru" else "CS2 collections and cases: drops and prices →") + "</a></p></section>")
        h = re.sub(r'<section class="gp-hub".*?</section>', "", h, flags=re.S)
        h = h.replace("</main>", blk + "</main>", 1)
        open(p, "w", encoding="utf-8").write(h)
    sm = os.path.join(ROOT, "sitemap.xml"); x = open(sm, encoding="utf-8").read()
    add = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for p in made if f"<loc>{SITE}{p}</loc>" not in x)
    open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>"))
    print(len(made), "pages")


if __name__ == "__main__":
    main()
