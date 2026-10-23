# -*- coding: utf-8 -*-
"""Английские и турецкие цветовые страницы (+ EN ножи/перчатки по цвету) — по образцу color_pages_ru.py.
Запуск: python3 admin/color_pages_i18n.py   (идемпотентно; списки скинов берутся из существующих страниц)
"""
import json, os, re, html
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(ROOT, "admin"))
from budget_pages import wiki_url, img, SETS, money, path as bpath, blog_links, BUD  # noqa
from color_pages_ru import parse_items, replace_section, faq_ld, PRICES  # noqa

e = lambda s: html.escape(str(s), quote=True)
SITE = "https://skin-set.com"
COL = ["#c4161c", "#1f4fd6", "#ff5cb0", "#6a2bb5", "#1d9b5a", "#d4af37", "#f26a1b", "#00c2c7", "#f4f4f4"]
BLOG = ["krasno-chernyj-inventar-cs2-tri-seta", "sinij-inventar-cs2-tri-seta", "rozovyj-inventar-cs2-tri-seta", "fioletovyj-inventar-cs2-tri-seta", "zelenyj-inventar-cs2-tri-seta",
        "zolotoj-inventar-cs2-tri-seta", "oranzhevo-belyj-inventar-cs2-tri-seta", "biryuzovyj-inventar-cs2-tri-seta", "cherno-belyj-inventar-cs2-tri-seta"]


def usd(weapon, skin):
    p = PRICES.get(weapon.replace("★ ", "") + " | " + skin)
    if not p or not p.get("w"): return None
    v = [x for x in p["w"].values() if x]
    return min(v) if v else None


def mon(lang, usd_v):
    return money(lang, usd_v * 90 / BUD[lang][0])


EN = [
 dict(page="red-black", kp="red", name="Red", adj="red", inv="red and black loadout",
  intro="Red and black is the most aggressive palette in CS2 and one of the most searched loadout colors: players have been building red CS:GO sets since the AK-47 Redline days. The core is deep red with black: Crimson Web on the knife and pistols, Redline and Bloodsport on the AK-47, Neo-Noir or Hyper Beast on the AWP. Black matters as much as red here: it ties the bright skins together so the set doesn't turn into a mess.",
  how="Start with the knife or the AK-47, the two most visible items. With a Crimson Web knife, go for dark gloves with red (Crimson Weave, Crimson Kimono) and Redline, Bloodsport or Fuel Injector on rifles. Keep pistols dark with red details: Desert Eagle Crimson Web, Glock-18 Candy Apple, USP-S Cyrex. Avoid orange and pink next to pure red: they make it look muddy."),
 dict(page="blue", kp="blue", name="Blue", adj="blue", inv="blue inventory",
  intro="A blue CS2 loadout is the classic choice for a calm inventory that still looks expensive. There are blue skins for every budget, from Blue Laminate and Royal Blue to Doppler Sapphire and Blue Steel knives. Blue reads well on every map and doesn't get old as fast as neon colors.",
  how="Don't mix cold blue with teal or purple. Knife: Doppler Phase 4, Blue Steel or Bright Water; gloves: Moto or Specialist in blue; AK-47: Blue Laminate or Frontside Misty; AWP: Corticera or Capillary. Keep pistols dark blue: USP-S Royal Blue, Glock-18 Off World, Desert Eagle Blue Ply. The bigger the budget, the deeper the shade you can go for."),
 dict(page="pink", kp="pink", name="Pink", adj="pink", inv="pink inventory",
  intro="A pink CS2 inventory is the loudest and most recognizable one: you see it from the first frame. It is built around Fade and Doppler Phase 2 knives, Pink DDPAT, Printstream with pink accents and Hyper Beast. Streamers love pink sets, and it is easy to get a clean look even on a small budget.",
  how="Pick your shade first: warm pink-orange (Fade) or cold magenta (Doppler Phase 2). Fade pairs with pink and orange gloves, Doppler with Pandora's Box and cold pinks. Use Neon Revolution or Phantom Disruptor on the AK-47 and Pink DDPAT or Hyper Beast on the AWP. Keep pistols a bit calmer so the set doesn't feel overloaded."),
 dict(page="purple", kp="purple", name="Purple", adj="purple", inv="purple inventory",
  intro="Purple is one of the most searched CS2 loadout colors: it looks expensive and is rarer than red or blue. The palette is built on Doppler Phase 2 and Sapphire knives, Pandora's Box gloves, AWP Lightning Strike, M4A1-S Nightmare and AK-47 Baroque Purple. A purple inventory looks great both on a budget and at the premium end.",
  how="Decide which purple you like: warm with pink (Doppler Phase 2) or cold with blue (Sapphire, Ultraviolet). Gloves: Pandora's Box, Moto Finish Line or Hand Wraps Cobalt Skulls. The signature AWP is Lightning Strike, the M4 is Nightmare or Purple DDPAT, the AK-47 is Baroque Purple. Pistols: Glock-18 Moonrise, USP-S Purple DDPAT, Desert Eagle Light Rail. Never mix purple with green."),
 dict(page="green", kp="green", name="Green", adj="green", inv="green inventory",
  intro="Green CS2 loadouts range from acid Hydra and Emerald to calm military khaki. A green inventory is usually built around a Gamma Doppler Emerald knife or Hydra and Emerald Web gloves, with Hydroponic, Emerald Pinstripe, Atheris and Glock-18 Gamma Doppler on the weapons. It stands out a lot on dark maps.",
  how="Don't mix acid green with khaki; pick one direction. For a bright set: Gamma Doppler knife, Emerald Web or Hydra gloves, AK-47 Hydroponic or Jungle Spray, AWP Atheris. For a military set: Boreal Forest, Safari Mesh or Forest DDPAT knives and calm camos on the guns. Match pistols to the main rifle, not the other way round."),
 dict(page="gold", kp="gold", name="Gold", adj="gold", inv="gold inventory",
  intro="A gold CS2 loadout is the 'pro player' look: Lore, Tiger Tooth, AK-47 Gold Arabesque, AWP Dragon Lore. It looks luxurious, yet there are affordable options too: Lore on cheaper knives, M4A4 Buzz Kill, Desert Eagle Blaze with yellow-orange tones.",
  how="Gold works with black and dark brown and clashes with silver and cold colors. Knife: Lore or Tiger Tooth; gloves: Driver Gloves King Snake or Sport Gloves Amphibious in warm tones. AK-47: Gold Arabesque (premium) or Fuel Injector; AWP: Dragon Lore or Mortis; pistols: Glock-18 Weasel, Desert Eagle Golden Koi."),
 dict(page="orange", kp="orange", name="Orange", adj="orange", inv="orange and white loadout",
  intro="An orange and white loadout is all about Asiimov: AK-47, AWP, M4A4 and even the knife in one legendary finish. It reads instantly and fits any budget: Battle-Scarred Asiimov costs reasonable money, while Asiimov, Fade and Slaughter knives make the premium version.",
  how="Balance orange and white: with an AWP and AK-47 Asiimov, take white or black pistols (USP-S Cortex, Glock-18 Bullet Queen). Knife: Asiimov, Fade or Tiger Tooth; gloves: Sport Gloves Omega or Driver Gloves in orange and white. Avoid red next to orange, it warms the set up and kills the clean Asiimov look."),
 dict(page="teal", kp="turquoise", name="Teal", adj="teal", inv="teal inventory",
  intro="Teal is a rare and fresh palette: Gamma Doppler, Bright Water, Ice Coaled and Water Elemental with light blue tones. A teal inventory stands out next to the usual red and blue sets and looks great on bright maps.",
  how="Teal easily drifts into green or blue, so compare shades side by side. Knife: Gamma Doppler Phase 1–2, Bright Water or Blue Steel; gloves: Sport Gloves Superconductor or Specialist Mogul. AK-47: Ice Coaled or Aquamarine Revenge; AWP: Atheris or Pit Viper; pistols: Glock-18 Water Elemental, USP-S Torque."),
 dict(page="black-white", kp="black-and-white", name="Black & white", adj="black and white", inv="black and white inventory",
  intro="Black and white is the most versatile set: Printstream on the Desert Eagle, M4A1-S and USP-S, Vulcan and Neo-Noir, Stained and Black Laminate knives. A black and white CS2 inventory never looks tasteless and is the easiest one to upgrade as your budget grows.",
  how="Put the contrast on the key items: Stained, Damascus Steel or Ultraviolet knife, Specialist Fade or Driver Gloves Black Tie. AK-47: Vulcan or a light Neon Rider; M4A1-S and Desert Eagle: Printstream; AWP: Containment Breach or a white Asiimov. Add one color accent at most."),
]

TR = [
 dict(page="kirmizi", name="Kırmızı", adj="kırmızı", inv="kırmızı-siyah envanter",
  intro="Kırmızı-siyah, CS2'nin en agresif paleti ve en çok aranan set renklerinden biri. Temeli koyu kırmızı ve siyah: bıçakta ve tabancalarda Crimson Web, AK-47'de Redline ve Bloodsport, AWP'de Neo-Noir ya da Hyper Beast. Siyah burada kırmızı kadar önemli: parlak skinleri birbirine bağlar.",
  how="Önce bıçağı ya da AK-47'yi seç. Crimson Web bıçakla kırmızılı koyu eldivenler (Crimson Weave, Crimson Kimono), tüfeklerde Redline, Bloodsport veya Fuel Injector iyi gider. Tabancalar kırmızı detaylı koyu olsun: Desert Eagle Crimson Web, Glock-18 Candy Apple, USP-S Cyrex. Kırmızının yanında turuncu ve pembeden kaçın."),
 dict(page="mavi", name="Mavi", adj="mavi", inv="mavi envanter",
  intro="Mavi CS2 envanteri, sakin ama pahalı görünen bir set isteyenler için klasik. Her bütçeye mavi skin var: Blue Laminate ve Royal Blue'dan Doppler Sapphire ve Blue Steel bıçaklara kadar. Mavi her haritada iyi okunur ve neon renkler kadar çabuk sıkmaz.",
  how="Soğuk maviyi turkuaz ve morla karıştırma. Bıçak: Doppler Phase 4, Blue Steel ya da Bright Water; eldiven: mavi Moto veya Specialist; AK-47: Blue Laminate ya da Frontside Misty; AWP: Corticera. Tabancalar koyu mavi: USP-S Royal Blue, Glock-18 Off World, Desert Eagle Blue Ply."),
 dict(page="pembe", name="Pembe", adj="pembe", inv="pembe envanter",
  intro="Pembe CS2 envanteri en dikkat çekici olanı: ilk karede fark edilir. Fade ve Doppler Phase 2 bıçaklar, Pink DDPAT, pembe detaylı Printstream ve Hyper Beast üzerine kurulur. Küçük bütçeyle bile bütünlüklü bir pembe set yapmak kolaydır.",
  how="Önce tonu seç: sıcak pembe-turuncu (Fade) ya da soğuk magenta (Doppler Phase 2). Fade'e pembe-turuncu eldiven, Doppler'a Pandora's Box gider. AK-47'de Neon Revolution, AWP'de Pink DDPAT ya da Hyper Beast. Tabancaları biraz sakin tut."),
 dict(page="mor", name="Mor", adj="mor", inv="mor envanter",
  intro="Mor envanter, CS2'de en çok aranan renk setlerinden biri: pahalı görünür ve kırmızı ya da maviden daha az görülür. Mor setin temeli Doppler Phase 2 ve Sapphire bıçaklar, Pandora's Box eldivenler, AWP Lightning Strike, M4A1-S Nightmare ve AK-47 Baroque Purple'dır. Mor CS2 envanteri hem ucuz hem premium versiyonda iyi durur.",
  how="Hangi moru sevdiğine karar ver: pembeye yakın sıcak mor (Doppler Phase 2) ya da maviye yakın soğuk mor (Sapphire, Ultraviolet). Eldiven: Pandora's Box, Moto Finish Line veya Hand Wraps Cobalt Skulls. AWP'de Lightning Strike, M4'te Nightmare ya da Purple DDPAT, AK-47'de Baroque Purple. Tabancalar: Glock-18 Moonrise, USP-S Purple DDPAT, Desert Eagle Light Rail. Moru yeşille karıştırma."),
 dict(page="yesil", name="Yeşil", adj="yeşil", inv="yeşil envanter",
  intro="Yeşil CS2 setleri asit yeşili Hydra ve Emerald'dan sakin askeri hakiye kadar uzanır. Yeşil envanter genelde Gamma Doppler Emerald bıçak ya da Hydra ve Emerald Web eldiven etrafında kurulur; silahlarda Hydroponic, Emerald Pinstripe, Atheris ve Glock-18 Gamma Doppler kullanılır.",
  how="Asit yeşiliyle hakiyi karıştırma, bir yön seç. Parlak set için Gamma Doppler bıçak, Emerald Web ya da Hydra eldiven, AK-47 Hydroponic, AWP Atheris. Askeri set için Boreal Forest, Safari Mesh veya Forest DDPAT bıçak ve sakin kamuflajlar."),
 dict(page="altin", name="Altın", adj="altın", inv="altın envanter",
  intro="Altın CS2 seti 'pro oyuncu' görünümüdür: Lore, Tiger Tooth, AK-47 Gold Arabesque, AWP Dragon Lore. Lüks görünür ama uygun seçenekler de var: ucuz bıçaklarda Lore, M4A4 Buzz Kill, sarı-turuncu tonlarıyla Desert Eagle Blaze.",
  how="Altın siyah ve koyu kahveyle uyumludur, gümüş ve soğuk renklerle uymaz. Bıçak: Lore ya da Tiger Tooth; eldiven: Driver Gloves King Snake. AK-47: Gold Arabesque ya da Fuel Injector; AWP: Dragon Lore ya da Mortis; tabancalar: Glock-18 Weasel, Desert Eagle Golden Koi."),
 dict(page="turuncu", name="Turuncu", adj="turuncu", inv="turuncu-beyaz envanter",
  intro="Turuncu-beyaz set demek Asiimov demek: AK-47, AWP, M4A4 ve hatta bıçak aynı efsane desende. Anında tanınır ve her bütçeye uyar: Battle-Scarred Asiimov makul fiyatlı, Asiimov, Fade ve Slaughter bıçaklar ise premium versiyonu oluşturur.",
  how="Turuncu ve beyazı dengede tut: AWP ve AK-47 Asiimov ise tabancalar beyaz ya da siyah olsun (USP-S Cortex, Glock-18 Bullet Queen). Bıçak: Asiimov, Fade ya da Tiger Tooth; eldiven: Sport Gloves Omega. Turuncunun yanına kırmızı koyma."),
 dict(page="turkuaz", name="Turkuaz", adj="turkuaz", inv="turkuaz envanter",
  intro="Turkuaz nadir ve taze bir palet: Gamma Doppler, Bright Water, Ice Coaled ve Water Elemental. Turkuaz envanter alışılmış kırmızı ve mavi setler arasında öne çıkar ve açık renkli haritalarda çok iyi görünür.",
  how="Turkuaz kolayca yeşile ya da maviye kayar, tonları yan yana karşılaştır. Bıçak: Gamma Doppler Phase 1–2, Bright Water ya da Blue Steel; eldiven: Sport Gloves Superconductor. AK-47: Ice Coaled veya Aquamarine Revenge; AWP: Atheris; tabancalar: Glock-18 Water Elemental, USP-S Torque."),
 dict(page="siyah-beyaz", name="Siyah-beyaz", adj="siyah-beyaz", inv="siyah-beyaz envanter",
  intro="Siyah-beyaz en çok yönlü set: Desert Eagle, M4A1-S ve USP-S'de Printstream, Vulcan ve Neo-Noir, Stained ve Black Laminate bıçaklar. Siyah-beyaz CS2 envanteri asla zevksiz görünmez ve bütçe büyüdükçe geliştirmesi en kolay settir.",
  how="Kontrastı ana eşyalara koy: Stained, Damascus Steel ya da Ultraviolet bıçak, Specialist Fade ya da Driver Gloves Black Tie. AK-47: Vulcan; M4A1-S ve Desert Eagle: Printstream; AWP: Containment Breach. En fazla bir renk vurgusu ekle."),
]

L = {
 "en": dict(home="Home", hub=("Color sets", "/en/cs2-skin-sets-by-color/"), sets_h="Ready-made {adj} loadouts: 3 budgets",
   sets_p="Built by the Skinset builder at current prices. “Open in builder” loads exactly this set, then you can swap any slot.",
   b=[("Budget set — under $55", "5000", 5000), ("Mid set — under $330", "30000", 30000), ("No limit — the priciest skins in this color", "none", None)],
   total="Total", open="Open in builder →", how_h="How to build a {adj} CS2 loadout", list_h="{Name} CS2 skins by slot",
   list_p="For every slot: the skins with the closest color match and the lowest market price.", from_="from", noprice="no price",
   kg_h="Knives and gloves in this color", faq_h="FAQ", blog_h="Related articles", other_h="Other colors", bud="Loadouts by budget:", budl=[15, 50, 100, 250, 500],
   title="{Name} CS2 skins: {adj} loadout ideas with prices — Skinset",
   desc="{Name} CS2 loadout: knife, gloves, AK-47, M4, AWP and pistols in one {adj} palette. 3 ready sets from {MIN}, every {adj} skin by slot with prices.",
   h1="{Name} CS2 skins: {inv} ideas",
   faq=lambda c, s, ck, kn: [
    (f"How do I build a {c['adj']} loadout in CS2?", f"Open the Skinset builder on this page: the color is already selected. Set a budget and it picks a knife, gloves, AK-47, M4, AWP and pistols in a {c['adj']} palette."),
    (f"How much does a {c['adj']} CS2 inventory cost?", f"A {c['adj']} weapon set without a knife costs about {s[0]}. A full set with knife and gloves starts around {s[1]}" + (f" (knife: {ck})" if ck else "") + f", and the priciest option in our database is about {s[2]}."),
    (f"Which knife fits a {c['adj']} loadout?", (f"In the premium version the builder picks {kn}. " if kn else "") + f"See the full list with prices on <a href=\"/en/{c['kp']}-knives-cs2/\">{c['name']} CS2 knives</a>."),
    ("Is this for CS:GO or CS2?", "Both: CS:GO skins carried over to Counter-Strike 2 unchanged, so a CS:GO set and a CS2 set are the same thing. Prices update every 4 hours.")]),
 "tr": dict(home="Ana sayfa", hub=None, sets_h="Hazır {adj} setler: 3 bütçe",
   sets_p="Setler Skinset oluşturucusuyla güncel fiyatlarla kuruldu. “Oluşturucuda aç” tam bu seti yükler, sonra istediğin slotu değiştirebilirsin.",
   b=[("Ucuz set — 1.850 ₺ altı", "5000", 5000), ("Orta set — 11.000 ₺ altı", "30000", 30000), ("Limitsiz — bu renkteki en pahalı skinler", "none", None)],
   total="Toplam", open="Oluşturucuda aç →", how_h="{Adj} CS2 seti nasıl kurulur", list_h="Slota göre {adj} CS2 skinleri",
   list_p="Her slot için renge en iyi uyan skinler ve piyasadaki en düşük fiyat.", from_="", noprice="fiyat yok",
   kg_h=None, faq_h="Sık sorulan sorular", blog_h="İlgili yazılar", other_h="Diğer renkler", bud="Bütçeye göre setler:", budl=[500, 1000, 2500, 5000, 10000],
   title="{Name} CS2 skinleri: {inv}, hazır setler ve fiyatlar — Skinset",
   desc="{Inv} CS2: bıçak, eldiven, AK-47, M4, AWP ve tabancalar tek {adj} palette. {MIN}'den başlayan 3 hazır set ve slota göre tüm {adj} skinler.",
   h1="{Name} CS2 skinleri: {inv}",
   faq=lambda c, s, ck, kn: [
    (f"CS2'de {c['inv']} nasıl kurulur?", f"Bu sayfadaki Skinset oluşturucusunu aç: renk zaten seçili. Bütçeni gir, {c['adj']} palette bıçak, eldiven, AK-47, M4, AWP ve tabancaları seçsin."),
    (f"{c['Inv']} kaç para?", f"Bıçaksız {c['adj']} silah seti yaklaşık {s[0]}. Bıçak ve eldivenli tam set {s[1]} civarından başlar" + (f" (bıçak: {ck})" if ck else "") + f"; veritabanındaki en pahalı seçenek yaklaşık {s[2]}."),
    (f"{c['Name']} sete hangi bıçak yakışır?", (f"Premium versiyonda oluşturucu {kn} seçer. " if kn else "") + "Bıçağı oluşturucuda sabitleyip diğer slotları aynı renkte doldurabilirsin."),
    ("Bu set CS:GO için mi CS2 için mi?", "İkisi için de: CS:GO skinleri Counter-Strike 2'ye değişmeden geçti. Fiyatlar 4 saatte bir güncellenir.")]),
}


def li(lang, w, s, c):
    p = usd(w, s); im = img(w, s); t = L[lang]
    pic = f'<img src="{e(im)}" alt="{e(w.replace("★ ", ""))} | {e(s)}" loading="lazy" width="60" height="45">' if im else '<i></i>'
    wu = wiki_url(lang, w.replace("★ ", "") + " | " + s)
    pr = ((t["from_"] + " ") if t["from_"] else "") + mon(lang, p) if p else t["noprice"]
    return f'<li style="--c0:{c}">{pic}<span><b>{f"<a href={chr(34)}{wu}{chr(34)}>{e(s)}</a>" if wu else e(s)}</b><small>{e(w)}</small></span><em>{e(pr)}</em></li>'


def setblock(lang, name, color, s, href_base, budget):
    t = L[lang]; lis = []
    rate = BUD[lang][0]
    for x in s:
        n = f"{x[1].replace('★ ', '')} | {x[2]}"; im = img(x[1], x[2])
        pic = f'<img src="{e(im)}" alt="{e(n)}" loading="lazy" width="54" height="40">' if im else ""
        wu = wiki_url(lang, n)
        lis.append(f'<li>{pic}<span><b>{f"<a href={chr(34)}{wu}{chr(34)}>{e(n)}</a>" if wu else e(n)}</b><small>{e(x[4] or "")} · {e(money(lang, x[3] / rate))}</small></span></li>')
    q = quote(";".join(f"{x[1]}|{x[2]}" for x in s), safe="")
    href = f"{href_base}?{'budget=' + str(budget) + '&' if budget else ''}set={q}"
    tot = sum(x[3] for x in s)
    return (f'<div class="seo-set" style="--c0:{color}"><h3><i></i>{e(name)}</h3><ul>{"".join(lis)}</ul>'
            f'<div class="est"><span>{t["total"]}: <b>≈ {e(money(lang, tot / rate))}</b></span><a href="{e(href)}">{e(t["open"])}</a></div></div>'), tot


def url_color(lang, c):
    return f"/en/{c['page']}-cs2-skins/" if lang == "en" else f"/tr/{c['page']}-cs2-skinleri/"


def do_color(lang, p, c, CC):
    t = L[lang]; u = url_color(lang, c)
    f = os.path.join(ROOT, u.strip("/"), "index.html"); s = open(f, encoding="utf-8").read()
    i = s.find('<div class="seo-list">'); j = s.find("</div>", i)
    groups = re.findall(r"<h3>(.*?)</h3><ul>(.*?)</ul>", s[i:j], re.S)
    lists = "".join(f"<h3>{g}</h3><ul>{''.join(li(lang, *x) for x in parse_items(uu))}</ul>" for g, uu in groups)
    sets = []
    for lab, key, bud in t["b"]:
        ss = [x for x in SETS[str(p)][key] if x[1]]
        b, tot = setblock(lang, lab, COL[p], ss, u, bud); sets.append((b, tot, ss))
    rate = BUD[lang][0]; m = lambda r: money(lang, r / rate)
    knife = next((x for x in sets[2][2] if x[0] == "knife"), None)
    cheap_k = next((x for x in sets[1][2] if x[0] == "knife"), None)
    kn = lambda x: f"{x[1].replace('★ ', '')} | {x[2]} (~{m(x[3])})" if x else None
    c2 = dict(c, Name=c["name"], Inv=c["inv"][:1].upper() + c["inv"][1:], kp=c.get("kp", ""))
    faq = t["faq"](c2, [m(sets[0][1]), m(sets[1][1]), m(sets[2][1])], kn(cheap_k), kn(knife))
    fmt = dict(Name=c["name"], adj=c["adj"], Adj=c["adj"][:1].upper() + c["adj"][1:], inv=c["inv"], Inv=c2["Inv"], MIN=m(sets[0][1]))
    crumbs = [(t["home"], "/en/" if lang == "en" else "/tr/")] + ([t["hub"]] if t["hub"] else []) + [(c["name"], u)]
    bl = blog_links(lang, [BLOG[p], "krasivyj-inventar-cs2-za-5000-rubley", "kachestvo-skinov-cs2-fn-mw-ft-ww-bs"])
    kg = (f'<h2>{e(t["kg_h"])}</h2><ul class="seo-chips"><li><a href="/en/{c["kp"]}-knives-cs2/">{e(c["name"])} CS2 knives</a></li><li><a href="/en/{c["kp"]}-gloves-cs2/">{e(c["name"])} CS2 gloves</a></li></ul>\n' if t["kg_h"] else "")
    inner = (f'<nav class="seo-crumbs">' + " › ".join(f'<a href="{uu}">{e(n)}</a>' for n, uu in crumbs[:-1]) + f' › {e(c["name"])}</nav>\n'
             f'<h1 id="seoH2">{e(t["h1"].format(**fmt))}</h1><div id="seoColor" class="seo-dyn" hidden></div>\n'
             f'<p class="seo-lead">{e(c["intro"])}</p>\n'
             f'<h2>{e(t["sets_h"].format(**fmt))}</h2><p>{e(t["sets_p"])}</p>\n' + "".join(b for b, _, _ in sets) +
             f'\n<h2>{e(t["how_h"].format(**fmt))}</h2><p>{e(c["how"])}</p>\n'
             f'<div class="seo-list"><h2>{e(t["list_h"].format(**fmt))}</h2><p>{e(t["list_p"])}</p>{lists}</div>\n' + kg +
             f'<h2>{e(t["faq_h"])}</h2>' + "".join(f"<h3>{e(q)}</h3><p>{a if '<a ' in a else e(a)}</p>" for q, a in faq) +
             (f'\n<h2>{e(t["blog_h"])}</h2><ul class="seo-chips">' + "".join(f'<li><a href="{h}">{e(tt)}</a></li>' for h, tt in bl) + "</ul>" if bl else "") +
             f'\n<h2>{e(t["other_h"])}</h2><ul class="seo-links" id="seoLinks">' + "".join(f'<li><a href="{url_color(lang, d)}"{" class=on" if d is c else ""}>{e(d["name"])}</a></li>' for d in CC) + "</ul>\n"
             f'<p class="seo-budgets"><b>{e(t["bud"])}</b> ' + " · ".join(f'<a href="{bpath(lang, n)}">{e(money(lang, n))}</a>' for n in t["budl"]) + "</p>")
    s = replace_section(s, inner, faq_ld([(q, re.sub(r"<[^>]+>", "", a)) for q, a in faq], [(n, uu) for n, uu in crumbs]))
    s = re.sub(r"<title>.*?</title>", f"<title>{e(t['title'].format(**fmt))}</title>", s, count=1)
    d = t["desc"].format(**fmt)
    for pat in [r'<meta name="description" content="[^"]*">', r'<meta property="og:description" content="[^"]*">']:
        s = re.sub(pat, lambda mm: re.sub(r'content="[^"]*"', f'content="{e(d)}"', mm.group(0)), s, count=1)
    open(f, "w", encoding="utf-8").write(s)


def do_type_en(p, c, kind):
    lang = "en"; T1 = "Knives" if kind == "knives" else "Gloves"; t1 = kind
    u = f"/en/{c['kp']}-{kind}-cs2/"
    f = os.path.join(ROOT, u.strip("/"), "index.html"); s = open(f, encoding="utf-8").read()
    i = s.find('<div class="seo-list">'); j = s.find("</div>", i)
    items = sorted(parse_items(s[i:j]), key=lambda x: usd(x[0], x[1]) or 9e9)
    pr = [(x, usd(x[0], x[1])) for x in items if usd(x[0], x[1])]
    nm = lambda x: f'{x[0].replace("★ ", "")} | {x[1]}'
    title_n = f"{c['name']} CS2 {t1}"
    rate = BUD[lang][0]
    b1, _ = setblock(lang, "Loadout under $330", COL[p], [x for x in SETS[str(p)]["30000"] if x[1]], url_color(lang, c), 30000)
    b2, _ = setblock(lang, "Premium loadout", COL[p], [x for x in SETS[str(p)]["none"] if x[1]], url_color(lang, c), None)
    rng = f" from {mon(lang, pr[0][1])} to {mon(lang, pr[-1][1])}" if pr else ""
    if kind == "knives":
        intro = f"The knife is the center of any loadout: it is on screen every round, and most players build the set around it. Here are all {c['adj']} CS2 knives in the Skinset database — {len(items)} options{rng}. Prices are the lowest market price across all wears and update every 4 hours."
        how = f"To make the knife fit, match the gloves and main weapons to its palette. The easiest way is the builder: it locks your knife and spends the rest of the budget on gloves, AK-47, M4, AWP and pistols. Below are two ready {c['adj']} loadouts with a knife."
    else:
        intro = f"Gloves are visible every round next to the knife, so their color sets the tone of the whole inventory. Here are all {c['adj']} CS2 gloves in the Skinset database — {len(items)} options{rng}. Prices are the lowest across all wears; for gloves, Factory New can cost several times more than Battle-Scarred."
        how = f"The most visible combo is gloves plus knife: when they share a palette, the loadout reads instantly. The builder locks the gloves you pick and matches a knife, AK-47, M4, AWP and pistols. Below are two ready {c['adj']} loadouts."
    faq = []
    if pr:
        faq.append((f"What {'is the cheapest' if kind == 'knives' else 'are the cheapest'} {c['adj']} {'knife' if kind == 'knives' else 'gloves'} in CS2?", "The most affordable right now: " + ", ".join(f"{nm(x)} (from {mon(lang, v)})" for x, v in pr[:2]) + "."))
        faq.append((f"What {'is the most expensive' if kind == 'knives' else 'are the most expensive'} {c['adj']} {'knife' if kind == 'knives' else 'gloves'}?", "At the top: " + ", ".join(f"{nm(x)} (from {mon(lang, v)})" for x, v in reversed(pr[-2:])) + ". Price depends heavily on wear and float."))
    faq.append((f"What goes with {c['adj']} {'a knife' if kind == 'knives' else 'gloves'}?", f"Open the builder with a {c['adj']} loadout, hit “Pick” on the slot and lock the {'knife' if kind == 'knives' else 'gloves'}: the other slots get filled in the same palette for your budget."))
    other = "gloves" if kind == "knives" else "knives"
    under = [50, 75, 100, 150, 200] if kind == "knives" else [40, 75, 100]
    inner = (f'<nav class="seo-crumbs"><a href="/en/">Home</a> › <a href="{url_color(lang, c)}">{e(c["name"])}</a> › {e(title_n)}</nav>\n'
             f'<h1>{e(title_n)}: full list with prices</h1><div id="seoColor" hidden></div><ul id="seoLinks" hidden></ul>\n'
             f'<p class="seo-lead">{e(intro)}</p>\n'
             f'<h2>All {e(c["adj"])} CS2 {kind} — cheapest first</h2><div class="seo-list"><ul>{"".join(li(lang, *x) for x in items)}</ul></div>\n'
             f'<h2>What to pair them with</h2><p>{e(how)}</p>{b1}{b2}\n'
             f'<p><a class="seo-cta" href="{url_color(lang, c)}">Build a {e(c["adj"])} loadout →</a></p>\n'
             f'<h2>FAQ</h2>' + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq) +
             f'\n<h2>See also</h2><ul class="seo-chips"><li><a href="/en/{c["kp"]}-{other}-cs2/">{e(c["name"])} CS2 {other}</a></li><li><a href="{url_color(lang, c)}">{e(c["name"])} CS2 skins</a></li>'
             + "".join(f'<li><a href="/en/cs2-{"knife" if kind == "knives" else "gloves"}-under-{n}-dollars/">{T1} under ${n}</a></li>' for n in under) + "</ul>\n"
             f'<h2>{T1} in other colors</h2><ul class="seo-chips">' + "".join(f'<li><a href="/en/{d["kp"]}-{kind}-cs2/"{" class=on" if d is c else ""}>{e(d["name"])}</a></li>' for d in EN) + "</ul>")
    s = replace_section(s, inner, faq_ld(faq, [("Home", "/en/"), (c["name"], url_color(lang, c)), (title_n, u)]))
    s = re.sub(r"<title>.*?</title>", f"<title>{e(title_n)}: full list, prices and what to pair them with — Skinset</title>", s, count=1)
    if pr:
        d = f"All {c['adj']} CS2 {kind} with prices from {mon(lang, pr[0][1])}: {', '.join(nm(x) for x, _ in pr[-3:][::-1])} and more. Ready loadouts and what to pair them with."
        for pat in [r'<meta name="description" content="[^"]*">', r'<meta property="og:description" content="[^"]*">']:
            s = re.sub(pat, lambda mm: re.sub(r'content="[^"]*"', f'content="{e(d)}"', mm.group(0)), s, count=1)
    open(f, "w", encoding="utf-8").write(s)


def main():
    for p, c in enumerate(EN):
        for k in ("knives", "gloves"): do_type_en(p, c, k)
        do_color("en", p, c, EN)
    for p, c in enumerate(TR):
        do_color("tr", p, c, TR)
    print("ok")


if __name__ == "__main__":
    main()
