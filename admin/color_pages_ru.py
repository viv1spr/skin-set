# -*- coding: utf-8 -*-
"""Переписывает SEO-блок русских цветовых страниц, а также страниц ножей и перчаток по цвету.
Запуск: python3 admin/color_pages_ru.py   (идемпотентно; списки скинов берутся из уже существующих страниц)
"""
import json, os, re, html, statistics
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(ROOT, "admin"))
from budget_pages import wiki_url, img, SETS, CSS as BP_CSS, money, path as bpath, blog_links  # noqa

e = lambda s: html.escape(str(s), quote=True)
SITE = "https://skin-set.com"
PRICES = json.load(open(os.path.join(ROOT, "data/prices.json")))
REF = "L4QnfHPvxc"


def price(weapon, skin):
    p = PRICES.get(weapon.replace("★ ", "") + " | " + skin)
    if not p or not p.get("w"): return None
    v = [x for x in p["w"].values() if x]
    return min(v) * 90 if v else None


def rub(v):
    return money("ru", v)


def dm(weapon, skin):
    base = re.sub(r"\s*\(.*\)$", "", skin)
    return f"https://dmarket.com/ru/ingame-items/item-list/csgo-skins?title={quote(weapon.replace('★ ', '') + ' ' + base)}&ref={REF}"


# stem, прилаг. мн., ед.м., «сет» в заголовке, имя в блоге, ключевые скины, текст
C = [
 dict(stem="krasnye", pl="красные", m="красный", Set="Красный сет КС 2 и КС ГО", inv="красно-чёрный инвентарь", blog="krasno-chernyj-inventar-cs2-tri-seta",
  intro="Красно-чёрный — самый «агрессивный» цвет в CS2 и один из самых популярных запросов: красный сет кс го собирают ещё со времён AK-47 Redline. Основа гаммы — насыщенный красный с чёрным: Crimson Web на ноже и пистолетах, Redline и Bloodsport на AK-47, Neo-Noir или Hyper Beast на AWP. Чёрный здесь важен не меньше красного: он связывает яркие скины и не даёт сету превратиться в пёструю мешанину.",
  how="Начни с ножа или AK-47 — это самые заметные предметы. Если нож с Crimson Web, перчатки бери тёмные с красным (Crimson Weave, Crimson Kimono), а оружие — Redline, Bloodsport, Fuel Injector. Пистолеты лучше держать в тёмной гамме с красными деталями: Desert Eagle Crimson Web, Glock-18 Candy Apple, USP-S Cyrex. Избегай оранжевых и розовых оттенков — рядом с чистым красным они выглядят грязно."),
 dict(stem="sinie", pl="синие", m="синий", Set="Синий сет КС 2 и КС ГО", inv="синий инвентарь", blog="sinij-inventar-cs2-tri-seta",
  intro="Синий сет кс го — классика для тех, кто хочет спокойный, но дорогой на вид инвентарь. В синей гамме много скинов на любой бюджет: от Blue Laminate и Royal Blue до Doppler Sapphire и Blue Steel на ножах. Синий хорошо читается на всех картах и не так быстро надоедает, как кислотные цвета.",
  how="Главное — не смешивать холодный синий с бирюзой и фиолетовым. Нож Doppler Phase 4, Blue Steel или Bright Water, перчатки Moto или Specialist в синем, на AK-47 — Blue Laminate или Frontside Misty, на AWP — Corticera или Capillary. Пистолеты подбирай тёмно-синие: USP-S Royal Blue, Glock-18 Off World, Desert Eagle Blue Ply. Чем больше бюджет, тем глубже и насыщеннее можно брать оттенок."),
 dict(stem="rozovye", pl="розовые", m="розовый", Set="Розовый сет КС 2 и КС ГО", inv="розовый инвентарь", blog="rozovyj-inventar-cs2-tri-seta",
  intro="Розовый инвентарь CS2 — самый яркий и узнаваемый: такой сет видно с первого кадра. В основе — Fade и Doppler Phase 2 на ножах, Pink DDPAT, Printstream с розовыми вставками, Hyper Beast. Розовый сет кс го часто собирают стримеры и те, кто хочет выделиться, и в нём легко получить цельную картинку даже на небольшой бюджет.",
  how="Определись с оттенком: тёплый розово-оранжевый (Fade) или холодный малиновый (Doppler Phase 2). Под Fade подходят перчатки с розовым и оранжевым, под Doppler — Pandora's Box и холодные розовые. На AK-47 подойдёт Neon Revolution или Phantom Disruptor, на AWP — Pink DDPAT или Hyper Beast. Пистолеты лучше держать чуть спокойнее, чтобы не перегружать сет."),
 dict(stem="fioletovye", pl="фиолетовые", m="фиолетовый", Set="Фиолетовый сет КС 2 и КС ГО", inv="фиолетовый инвентарь", blog="fioletovyj-inventar-cs2-tri-seta",
  intro="Фиолетовый сет кс го — один из самых частых запросов среди цветовых сетов: фиолетовый выглядит дорого и при этом встречается реже красного или синего. Основа гаммы — Doppler Phase 2 и Sapphire на ножах, Pandora's Box на перчатках, AWP Lightning Strike, M4A1-S Nightmare, AK-47 Baroque Purple. Фиолетовый инвентарь CS2 хорошо смотрится и в бюджетном, и в премиальном варианте.",
  how="Выбери, какой фиолетовый тебе ближе: тёплый с розовым (Doppler Phase 2) или холодный с синим (Sapphire, Ultraviolet). Перчатки — Pandora's Box, Moto Finish Line или Hand Wraps Cobalt Skulls. На AWP самый узнаваемый вариант — Lightning Strike, на M4 — Nightmare или Purple DDPAT, на AK-47 — Baroque Purple. Пистолеты — Glock-18 Moonrise, USP-S Purple DDPAT, Desert Eagle Light Rail. Не смешивай фиолетовый с зелёным — это убивает цельность."),
 dict(stem="zelenye", pl="зелёные", m="зелёный", Set="Зелёный сет КС 2 и КС ГО", inv="зелёный инвентарь", blog="zelenyj-inventar-cs2-tri-seta",
  intro="Зелёный сет кс го — от «кислотного» Hydra и Emerald до спокойного военного хаки. Зелёный инвентарь CS2 собирают вокруг Gamma Doppler Emerald на ноже или перчаток Hydra и Emerald Web, а на оружие ставят Hydroponic, Emerald Pinstripe, Atheris и Glock-18 Gamma Doppler. Это цвет, который сильно выделяется на тёмных картах.",
  how="Не смешивай кислотно-зелёный с хаки: выбери одно направление. Для яркого сета — нож Gamma Doppler, перчатки Emerald Web или Hydra, AK-47 Hydroponic или Jungle Spray, AWP Atheris. Для военного — Boreal Forest, Safari Mesh, Forest DDPAT на ножах и спокойные камуфляжи на оружии. Пистолеты подбирай под основное оружие, а не наоборот."),
 dict(stem="zolotye", pl="золотые", m="золотой", Set="Золотой сет КС 2 и КС ГО", inv="золотой инвентарь", blog="zolotoj-inventar-cs2-tri-seta",
  intro="Золотой сет кс 2 — для тех, кто хочет инвентарь «как у про-игроков»: Lore, Tiger Tooth, AK-47 Gold Arabesque, AWP Dragon Lore. Золотой инвентарь CS2 смотрится роскошно, и при этом в нём есть доступные варианты: Lore на дешёвых ножах, M4A4 Buzz Kill, Desert Eagle Blaze с жёлто-оранжевыми тонами.",
  how="Золото хорошо сочетается с чёрным и тёмно-коричневым, плохо — с серебром и холодными цветами. Нож — Lore или Tiger Tooth, перчатки — Driver Gloves King Snake или Sport Gloves Amphibious в тёплых тонах. На AK-47 — Gold Arabesque (премиум) или Fuel Injector, на AWP — Dragon Lore или Mortis, на пистолеты — Glock-18 Weasel, Desert Eagle Golden Koi."),
 dict(stem="oranzhevye", pl="оранжевые", m="оранжевый", Set="Оранжевый сет КС 2 и КС ГО", inv="оранжево-белый инвентарь", blog="oranzhevo-belyj-inventar-cs2-tri-seta",
  intro="Оранжево-белый сет — это прежде всего Asiimov: AK-47, AWP, M4A4 и даже нож в одной легендарной раскраске. Оранжевый инвентарь CS2 читается мгновенно и подходит на любой бюджет: Asiimov есть в Battle-Scarred за умеренные деньги, а на ножах — Asiimov, Fade и Slaughter для премиального варианта.",
  how="Держи баланс оранжевого и белого: если AWP и AK-47 Asiimov, пистолеты лучше брать с белым или чёрным (USP-S Cortex, Glock-18 Bullet Queen). Нож — Asiimov, Fade или Tiger Tooth, перчатки — Sport Gloves Omega или Driver Gloves в оранжево-белых тонах. Избегай красного рядом с оранжевым — сет станет тёплым и потеряет «чистоту» Asiimov."),
 dict(stem="biryuzovye", pl="бирюзовые", m="бирюзовый", Set="Бирюзовый сет КС 2 и КС ГО", inv="бирюзовый инвентарь", blog="biryuzovyj-inventar-cs2-tri-seta",
  intro="Бирюзовый сет — редкая и свежая гамма: Gamma Doppler, Bright Water, Ice Coaled, Water Elemental с голубыми тонами. Бирюзовый инвентарь CS2 выделяется на фоне привычных красных и синих сетов и при этом хорошо подходит к светлым картам.",
  how="Бирюза легко уходит в зелёный или синий, поэтому сравнивай оттенки вживую. Нож — Gamma Doppler Phase 1–2, Bright Water или Blue Steel, перчатки — Sport Gloves Superconductor или Specialist Mogul. На AK-47 подойдут Ice Coaled или Aquamarine Revenge, на AWP — Atheris или Pit Viper, на пистолеты — Glock-18 Water Elemental, USP-S Torque."),
 dict(stem="cherno-belye", pl="чёрно-белые", m="чёрно-белый", Set="Чёрно-белый сет КС 2 и КС ГО", inv="чёрно-белый инвентарь", blog="cherno-belyj-inventar-cs2-tri-seta",
  intro="Чёрно-белый сет — самый универсальный: Printstream на Desert Eagle, M4A1-S и USP-S, Vulcan и Neo-Noir, ножи Stained и Black Laminate. Чёрно-белый инвентарь CS2 никогда не выглядит безвкусно, и его проще всего дополнять по мере роста бюджета.",
  how="Ставь контраст на главные предметы: нож Stained, Damascus Steel или Ultraviolet, перчатки Specialist Fade или Driver Gloves Black Tie. На AK-47 — Vulcan или Neon Rider в светлой гамме, на M4A1-S и Desert Eagle — Printstream, на AWP — Containment Breach или Asiimov с белым. Чёрно-белый проще всего «разбавить» одним цветным акцентом — главное, чтобы акцент был один."),
]
TYPES = {"nozhi": ("Нож", "ножи", "ножа", "knife"), "perchatki": ("Перчатки", "перчатки", "перчаток", "gloves")}


def parse_items(block):
    """[(weapon, skin, color)] из старого .seo-list"""
    out = []
    for m in re.finditer(r'<li style="--c0:([^"]+)">(?:<i></i>|<img[^>]*>)<span><b>(.*?)</b><small>(.*?)</small>', block):
        b = m.group(2)
        for _ in range(3): b = re.sub(r"<[^>]+>", "", html.unescape(b))
        out.append((html.unescape(m.group(3)), b, m.group(1)))
    return out


def li(w, s, c):
    p = price(w, s); im = img(w, s)
    pic = f'<img src="{e(im)}" alt="{e(w.replace("★ ", ""))} | {e(s)}" loading="lazy" width="60" height="45">' if im else '<i></i>'
    wu = wiki_url("ru", w.replace("★ ", "") + " | " + s)
    return (f'<li style="--c0:{c}">{pic}<span><b>{f'<a href="{wu}">{e(s)}</a>' if wu else e(s)}</b><small>{e(w)}</small></span><em>{"от " + e(rub(p)) if p else "нет цены"}</em>'
            f'</li>')


CSS = BP_CSS.replace("<style data-bp>", "<style data-cp>") .replace("</style>", """
.seo.collapsed{max-height:230px}
.seo-list li img{width:60px;height:45px;object-fit:contain;flex:none;filter:drop-shadow(0 4px 6px rgba(0,0,0,.5))}
.seo-lead{font-size:1.02rem;color:var(--ink)}
</style>""")


def setblock(name, color, s, href_base, budget):
    lis = []
    for x in s:
        n = f"{x[1].replace('★ ', '')} | {x[2]}"; im = img(x[1], x[2])
        pic = f'<img src="{e(im)}" alt="{e(n)}" loading="lazy" width="54" height="40">' if im else ""
        wu = wiki_url("ru", n)
        lis.append(f'<li>{pic}<span><b>{f'<a href="{wu}">{e(n)}</a>' if wu else e(n)}</b><small>{e(x[4] or "")} · {e(rub(x[3]))}</small></span></li>')
    q = quote(";".join(f"{x[1]}|{x[2]}" for x in s), safe="")
    href = f"{href_base}?{'budget=' + str(budget) + '&' if budget else ''}set={q}"
    tot = sum(x[3] for x in s)
    return (f'<div class="seo-set" style="--c0:{color}"><h3><i></i>{e(name)}</h3><ul>{"".join(lis)}</ul>'
            f'<div class="est"><span>Итого: <b>≈ {e(rub(tot))}</b></span><a href="{e(href)}">Открыть в конструкторе →</a></div></div>'), tot


def replace_section(s, inner, ld):
    i = s.find('<section class="seo'); j = s.find("</section>", i) + len("</section>")
    btn = re.search(r'<button class="seo-tg".*?</button>', s[i:j], re.S).group(0)
    s = s[:i] + f'<section class="seo collapsed" id="seo">{btn}\n      <div class="seo-in">\n{inner}\n      </div>\n    </section>' + s[j:]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = re.sub(r"<style data-(?:cp|bp)>.*?</style>", "", s, flags=re.S)
    return s.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld) + CSS + "</head>", 1)


def faq_ld(faq, crumbs):
    return [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": k + 1, "name": n, "item": SITE + u} for k, (n, u) in enumerate(crumbs)]}]


def color_links(cur):
    return "".join(f'<li><a href="/{c["stem"]}-skiny-cs2/"{" class=on" if c is cur else ""}>{e(c["Set"].split(" КС")[0])}</a></li>' for c in C)


def do_color(p, c):
    f = os.path.join(ROOT, f'{c["stem"]}-skiny-cs2', "index.html"); s = open(f, encoding="utf-8").read()
    i = s.find('<div class="seo-list">'); j = s.find("</div>", i)
    old = s[i:j]
    groups = re.findall(r"<h3>(.*?)</h3><ul>(.*?)</ul>", old, re.S)
    lists = "".join(f"<h3>{g}</h3><ul>{''.join(li(*x) for x in parse_items(u))}</ul>" for g, u in groups)
    sets = []
    for lab, key, bud in [("Бюджетный сет — до 5 000 ₽", "5000", 5000), ("Средний сет — до 30 000 ₽", "30000", 30000), ("Без лимита — самые дорогие скины в цвете", "none", None)]:
        ss = [x for x in SETS[str(p)][key] if x[1]]
        b, tot = setblock(lab, ["#c4161c", "#1f4fd6", "#ff5cb0", "#6a2bb5", "#1d9b5a", "#d4af37", "#f26a1b", "#00c2c7", "#f4f4f4"][p], ss, f'/{c["stem"]}-skiny-cs2/', bud)
        sets.append((b, tot, ss))
    knife = next((x for x in sets[2][2] if x[0] == "knife"), None)
    cheap_k = next((x for x in sets[1][2] if x[0] == "knife"), None)
    name = c["Set"].split(" КС")[0]  # «Фиолетовый сет»
    faq = [
        (f"Как собрать {c['m']} сет в КС 2?", f"Открой конструктор Skinset на этой странице: цвет уже выбран. Укажи бюджет — сервис подберёт нож, перчатки, AK-47, M4, AWP и пистолеты в {c['m'].replace('ый', 'ой').replace('ий', 'ей')} гамме."),
        (f"Сколько стоит {c['m']} инвентарь CS2?", f"Оружейный {c['m']} сет без ножа можно собрать примерно за {rub(sets[0][1])}. Полный сет с ножом и перчатками — от {rub(sets[1][1])}" + (f" (нож {cheap_k[1].replace('★ ', '')} | {cheap_k[2]})" if cheap_k else "") + f", а самый дорогой вариант в базе обходится примерно в {rub(sets[2][1])}."),
        (f"Какой нож выбрать для сета «{name.lower()}»?", (f"В премиальном варианте конструктор ставит {knife[1].replace('★ ', '')} | {knife[2]} (около {rub(knife[3])}). " if knife else "") + f"Полный список с ценами — на странице «<a href=\"/{c['stem']}-nozhi-cs2/\">{c['pl'].capitalize()} ножи CS2</a>»."),
        ("Это сет для КС ГО или для КС 2?", "Для обоих: скины из CS:GO перенеслись в Counter-Strike 2 без изменений, поэтому «сет кс го» и «сет кс 2» — одно и то же. Цены в Skinset — актуальные рыночные, обновляются каждые 4 часа."),
    ]
    bl = blog_links("ru", [c["blog"], "s-chem-sochetat-ak-47-redline" if p == 0 else "kakie-perchatki-podhodyat-k-fioletovomu-nozhu" if p == 3 else "perchatki-k-nozhu-doppler-po-fazam", "krasivyj-inventar-cs2-za-5000-rubley"])
    inner = (f'<nav class="seo-crumbs"><a href="/">Главная</a> › <a href="/cvetovye-sety-skinov-cs2/">Цветовые сеты</a> › {e(name)}</nav>\n'
             f'<h1 id="seoH2">{e(c["Set"])}: {e(c["inv"])} CS2</h1><div id="seoColor" class="seo-dyn" hidden></div>\n'
             f'<p class="seo-lead">{e(c["intro"])}</p>\n'
             f'<h2>Готовые {e(c["pl"])} сеты: 3 бюджета</h2><p>Сеты собраны конструктором Skinset по текущим ценам. «Открыть в конструкторе» загрузит именно этот сет — дальше можно заменить любой слот.</p>\n'
             + "".join(b for b, _, _ in sets) +
             f'\n<h2>Как собрать {e(c["m"])} сет в CS2</h2><p>{e(c["how"])}</p>\n'
             f'<div class="seo-list"><h2>{e(c["pl"].capitalize())} скины CS2 по слотам</h2><p>По каждому слоту — скины с самым точным совпадением цвета и минимальная цена на рынке.</p>{lists}</div>\n'
             f'<h2>Ножи и перчатки в этом цвете</h2><ul class="seo-chips"><li><a href="/{c["stem"]}-nozhi-cs2/">{e(c["pl"].capitalize())} ножи CS2</a></li><li><a href="/{c["stem"]}-perchatki-cs2/">{e(c["pl"].capitalize())} перчатки CS2</a></li></ul>\n'
             f'<h2>Вопросы и ответы</h2>' + "".join(f"<h3>{e(q)}</h3><p>{a if '<a ' in a else e(a)}</p>" for q, a in faq) +
             (f'\n<h2>Статьи по теме</h2><ul class="seo-chips">' + "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in bl) + "</ul>" if bl else "") +
             f'\n<h2>Другие цвета</h2><ul class="seo-links" id="seoLinks">{color_links(c)}</ul>\n'
             f'<p class="seo-budgets"><b>Сеты под бюджет:</b> ' + " · ".join(f'<a href="{bpath("ru", n)}">за {rub(n)}</a>' for n in [1000, 3000, 5000, 10000, 30000, 100000]) + "</p>")
    faq_plain = [(q, re.sub(r"<[^>]+>", "", a)) for q, a in faq]
    s = replace_section(s, inner, faq_ld(faq_plain, [("Главная", "/"), ("Цветовые сеты", "/cvetovye-sety-skinov-cs2/"), (name, f'/{c["stem"]}-skiny-cs2/')]))
    open(f, "w", encoding="utf-8").write(s)


def do_type(p, c, kind):
    T1, Tpl, Tgen, slot = TYPES[kind]
    f = os.path.join(ROOT, f'{c["stem"]}-{kind}-cs2', "index.html"); s = open(f, encoding="utf-8").read()
    i = s.find('<div class="seo-list">'); j = s.find("</div>", i)
    items = parse_items(s[i:j])
    items = sorted(items, key=lambda x: price(x[0], x[1]) or 9e9)
    pr = [(x, price(x[0], x[1])) for x in items if price(x[0], x[1])]
    other = "perchatki" if kind == "nozhi" else "nozhi"
    pl_title = f'{c["pl"].capitalize()} {Tpl} CS2'
    nm = lambda x: f'{x[0].replace("★ ", "")} | {x[1]}'
    cheap, exp = (pr[:2], pr[-2:]) if pr else ([], [])
    full = [x for x in SETS[str(p)]["30000"] if x[1]]
    lux = [x for x in SETS[str(p)]["none"] if x[1]]
    col = ["#c4161c", "#1f4fd6", "#ff5cb0", "#6a2bb5", "#1d9b5a", "#d4af37", "#f26a1b", "#00c2c7", "#f4f4f4"][p]
    b1, _ = setblock("Сет до 30 000 ₽", col, full, f'/{c["stem"]}-skiny-cs2/', 30000)
    b2, _ = setblock("Премиальный сет", col, lux, f'/{c["stem"]}-skiny-cs2/', None)
    if kind == "nozhi":
        intro = (f"Нож — центр любого инвентаря: его видно в каждом раунде, и именно с него обычно начинают собирать сет. Здесь собраны все {c['pl']} ножи CS2 из базы Skinset — {len(items)} вариантов"
                 + (f" от {rub(pr[0][1])} до {rub(pr[-1][1])}" if pr else "") + ". Цены — минимальные на рынке по любому износу, обновляются каждые 4 часа.")
        how = f"Чтобы нож не выглядел чужим, подбирай перчатки и основное оружие в той же гамме. Проще всего открыть конструктор: он закрепит выбранный нож и распределит остаток бюджета на перчатки, AK-47, M4, AWP и пистолеты. Ниже — два готовых {c['m']} сета с ножом."
    else:
        intro = (f"Перчатки видны в каждом раунде вместе с ножом, поэтому их цвет задаёт тон всего инвентаря. Здесь собраны все {c['pl']} перчатки CS2 из базы Skinset — {len(items)} вариантов"
                 + (f" от {rub(pr[0][1])} до {rub(pr[-1][1])}" if pr else "") + ". Цены — минимальные на рынке по любому износу; у перчаток разница между Factory New и Battle-Scarred бывает в разы.")
        how = f"Самое заметное сочетание — перчатки и нож: если они в одной гамме, сет читается сразу. Конструктор закрепит выбранные перчатки и подберёт к ним нож, AK-47, M4, AWP и пистолеты. Ниже — два готовых {c['m']} сета."
    faq = []
    if cheap:
        faq.append((f"{'Какой самый дешёвый' if kind == 'nozhi' else 'Какие самые дешёвые'} {c['m'] if kind == 'nozhi' else c['pl']} {'нож' if kind == 'nozhi' else 'перчатки'} в CS2?",
                    "Самые доступные сейчас — " + ", ".join(f"{nm(x)} (от {rub(v)})" for x, v in cheap) + "."))
        faq.append((f"{'Какой' if kind == 'nozhi' else 'Какие'} {c['m'] if kind == 'nozhi' else c['pl']} {'нож самый дорогой' if kind == 'nozhi' else 'перчатки самые дорогие'}?",
                    "Верх списка — " + ", ".join(f"{nm(x)} (от {rub(v)})" for x, v in reversed(exp)) + ". Цена сильно зависит от износа и float."))
    faq.append((f"Что подобрать к {'фиолетовому ножу' if False else ('ножу' if kind == 'nozhi' else 'перчаткам')} в {c['m'].replace('ый', 'ом').replace('ий', 'ем')} цвете?",
                f"Открой конструктор с {c['m'].replace('ый', 'ым').replace('ий', 'им')} сетом, нажми «Выбрать» на слоте и закрепи {('нож' if kind == 'nozhi' else 'перчатки')} — остальные слоты подберутся в той же гамме под твой бюджет."))
    bl = blog_links("ru", ["samye-deshevye-nozhi-cs2" if kind == "nozhi" else "perchatki-k-nozhu-doppler-po-fazam", "kakie-perchatki-podhodyat-k-fioletovomu-nozhu" if p == 3 else "perchatki-k-nozhu-doppler-po-fazam" if kind == "nozhi" else "samye-deshevye-nozhi-cs2", c["blog"]])
    inner = (f'<nav class="seo-crumbs"><a href="/">Главная</a> › <a href="/{c["stem"]}-skiny-cs2/">{e(c["Set"].split(" КС")[0])}</a> › {e(pl_title)}</nav>\n'
             f'<h1>{e(pl_title)}: список и цены</h1><div id="seoColor" hidden></div><ul id="seoLinks" hidden></ul>\n'
             f'<p class="seo-lead">{e(intro)}</p>\n'
             f'<h2>Все {e(c["pl"])} {e(Tpl)} CS2 — от дешёвых к дорогим</h2><div class="seo-list"><ul>{"".join(li(*x) for x in items)}</ul></div>\n'
             f'<h2>С чем сочетать</h2><p>{e(how)}</p>{b1}{b2}\n'
             f'<p><a class="seo-cta" href="/{c["stem"]}-skiny-cs2/">Собрать {e(c["m"])} сет →</a></p>\n'
             f'<h2>Вопросы и ответы</h2>' + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq) +
             f'\n<h2>Смотри также</h2><ul class="seo-chips"><li><a href="/{c["stem"]}-{other}-cs2/">{e(c["pl"].capitalize())} {"перчатки" if kind == "nozhi" else "ножи"} CS2</a></li><li><a href="/{c["stem"]}-skiny-cs2/">{e(c["Set"].split(" КС")[0])}</a></li>'
             + "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in bl) + "</ul>\n"
             f'<h2>{e(T1)} других цветов</h2><ul class="seo-chips">' + "".join(f'<li><a href="/{d["stem"]}-{kind}-cs2/"{" class=on" if d is c else ""}>{e(d["pl"].capitalize())}</a></li>' for d in C) + "</ul>")
    s = replace_section(s, inner, faq_ld(faq, [("Главная", "/"), (c["Set"].split(" КС")[0], f'/{c["stem"]}-skiny-cs2/'), (pl_title, f'/{c["stem"]}-{kind}-cs2/')]))
    s = re.sub(r"<title>.*?</title>", f"<title>{e(pl_title)}: список, цены и с чем сочетать — Skinset</title>", s, count=1)
    if pr:
        d = f"Все {c['pl']} {Tpl} CS2 с ценами от {rub(pr[0][1])}: {', '.join(nm(x) for x, _ in pr[-3:][::-1])} и другие. Готовые сеты и с чем сочетать."
        for pat in [r'<meta name="description" content="[^"]*">', r'<meta property="og:description" content="[^"]*">']:
            s = re.sub(pat, lambda m: re.sub(r'content="[^"]*"', f'content="{e(d)}"', m.group(0)), s, count=1)
    open(f, "w", encoding="utf-8").write(s)


def main():
    for p, c in enumerate(C):
        # сначала ножи/перчатки — они читают старые списки; потом цвет
        for k in TYPES: do_type(p, c, k)
        do_color(p, c)
    print("ok")


if __name__ == "__main__":
    main()
