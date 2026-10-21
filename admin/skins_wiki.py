# -*- coding: utf-8 -*-
"""Вики-страницы скинов CS2 на 6 языках + индекс.
Запуск: python3 admin/skins_wiki.py
Данные: data/skins-base.json (список), data/wiki-sets.json (сеты считает admin/skin-wiki-data.js),
        data/prices.json (цены), admin/skins-api.json (картинки, редкость, коллекция).
Цены на странице — снимок (округлён), в браузере обновляются из /data/prices.json.
"""
import json, os, re, html, math, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(ROOT, "admin"))
from about import NAV, HOME, HREFLANG, CP, PCOL, PNAMES, CSS as BASE_CSS, LANG_JS, LNAMES, ABOUT_LABEL, PATHS as ABOUT  # noqa
from budget_pages import money, BUD, path as bpath  # noqa

e = lambda s: html.escape(str(s), quote=True)
SITE = "https://skin-set.com"
LANGS = ["ru", "en", "de", "pt", "tr", "pl"]
WIKI = {"ru": "/skiny/", "en": "/en/skins/", "de": "/de/skins/", "pt": "/pt/skins/", "tr": "/tr/skinler/", "pl": "/pl/skiny/"}
RATE = {l: BUD[l][0] for l in LANGS}
REF = "L4QnfHPvxc"
WEARS = ["FN", "MW", "FT", "WW", "BS"]
WEARN = {"ru": {"FN": "Прямо с завода", "MW": "Немного поношенное", "FT": "После полевых испытаний", "WW": "Поношенное", "BS": "Закалённое в боях"},
         "*": {"FN": "Factory New", "MW": "Minimal Wear", "FT": "Field-Tested", "WW": "Well-Worn", "BS": "Battle-Scarred"}}
RAR = {"ru": {"Consumer Grade": "Ширпотреб", "Industrial Grade": "Промышленное качество", "Mil-Spec Grade": "Армейское качество", "Restricted": "Запрещённое",
              "Classified": "Засекреченное", "Covert": "Тайное", "Extraordinary": "Экстраординарное", "Contraband": "Контрабанда"}}
# именованные цвета для описания
CN = [("red", "#c4161c"), ("darkred", "#6a0f14"), ("orange", "#f26a1b"), ("gold", "#d4af37"), ("yellow", "#f2d230"), ("green", "#1d9b5a"), ("olive", "#6b6b3a"),
      ("teal", "#00b3b8"), ("blue", "#1f4fd6"), ("navy", "#1a2350"), ("purple", "#6a2bb5"), ("pink", "#ff5cb0"), ("white", "#f0f0f0"), ("gray", "#8a8a8a"),
      ("black", "#151515"), ("brown", "#6b4a2b")]
CNAME = {
 "ru": dict(red="красный", darkred="бордовый", orange="оранжевый", gold="золотой", yellow="жёлтый", green="зелёный", olive="оливковый", teal="бирюзовый", blue="синий", navy="тёмно-синий", purple="фиолетовый", pink="розовый", white="белый", gray="серый", black="чёрный", brown="коричневый"),
 "en": dict(red="red", darkred="dark red", orange="orange", gold="gold", yellow="yellow", green="green", olive="olive", teal="teal", blue="blue", navy="navy", purple="purple", pink="pink", white="white", gray="gray", black="black", brown="brown"),
 "de": dict(red="Rot", darkred="Dunkelrot", orange="Orange", gold="Gold", yellow="Gelb", green="Grün", olive="Oliv", teal="Türkis", blue="Blau", navy="Dunkelblau", purple="Lila", pink="Pink", white="Weiß", gray="Grau", black="Schwarz", brown="Braun"),
 "pt": dict(red="vermelho", darkred="vinho", orange="laranja", gold="dourado", yellow="amarelo", green="verde", olive="oliva", teal="turquesa", blue="azul", navy="azul-marinho", purple="roxo", pink="rosa", white="branco", gray="cinza", black="preto", brown="marrom"),
 "tr": dict(red="kırmızı", darkred="bordo", orange="turuncu", gold="altın", yellow="sarı", green="yeşil", olive="haki", teal="turkuaz", blue="mavi", navy="lacivert", purple="mor", pink="pembe", white="beyaz", gray="gri", black="siyah", brown="kahverengi"),
 "pl": dict(red="czerwony", darkred="bordowy", orange="pomarańczowy", gold="złoty", yellow="żółty", green="zielony", olive="oliwkowy", teal="turkusowy", blue="niebieski", navy="granatowy", purple="fioletowy", pink="różowy", white="biały", gray="szary", black="czarny", brown="brązowy"),
}
SLOTN = {
 "ru": dict(knife="Нож", gloves="Перчатки"), "en": dict(knife="Knife", gloves="Gloves"), "de": dict(knife="Messer", gloves="Handschuhe"),
 "pt": dict(knife="Faca", gloves="Luvas"), "tr": dict(knife="Bıçak", gloves="Eldiven"), "pl": dict(knife="Nóż", gloves="Rękawice")}

T = {
"ru": dict(
 title="{name} — цена, качество и с чем сочетать | Skinset", desc="{name}: цены по качеству от {pmin}, редкость «{rar}», цвета и готовые сеты с ножом и перчатками в тон. Купить на DMarket.",
 crumbs=("Главная", "Скины CS2"), h1="{name}", sub="Скин для {w} · {rar}", coll="Коллекция", typ="Тип", rarL="Редкость", colL="Цвета",
 intro="{name} — скин для {w} редкости «{rar}»{coll}. Основные цвета — {cols}. Самый доступный вариант на рынке сейчас — {cw} от {cp}{fn}.",
 fn=", в Factory New — от {p}", ratio="Разница между самым дешёвым и самым дорогим качеством — примерно в {x} раза, поэтому выбор износа сильно влияет на цену сета.",
 price_h="Цена {name} по качеству", tab=("Качество", "Цена от", ""), buy="Купить", noprice="нет в продаже", live="Цены обновляются каждые 4 часа; точная цена и float — на DMarket.",
 sets_h="С чем сочетать {name}", sets_p="Конструктор Skinset подобрал к скину нож, перчатки и оружие в той же гамме ({color}). Нажми «Открыть в конструкторе», чтобы загрузить сет и заменить любой слот.",
 cheap="Недорогой сет", lux="Максимальный сет", total="Итого", open="Открыть в конструкторе",
 sim_h="Похожие скины по цвету", more_h="Другие скины {w}", all="Все скины CS2",
 faq_h="Вопросы и ответы",
 q1="Сколько стоит {name}?", a1="Сейчас {name} стоит от {pmin} ({cw}). {fnq}Цены — минимальные на рынке, обновляются каждые 4 часа.", a1fn="В Factory New — от {p}. ",
 q2="С чем сочетать {name}?", a2="К {name} хорошо подходят {pair}. Это сочетание из максимального сета Skinset в {color} гамме; вариант дешевле — на этой же странице.",
 q3="Какое качество {name} выбрать?", a3="Для экономии бери {cw} — это самый дешёвый вариант. Если важен внешний вид, смотри Factory New или Minimal Wear: на них рисунок без потёртостей.",
 cta="Собрать сет с этим скином →", idx_t="Все скины CS2: цены, качество и сочетания — Skinset", idx_d="Справочник скинов CS2: {n} скинов с ценами по качеству, цветами и готовыми сетами. Ножи, перчатки, AK-47, AWP, M4 и пистолеты.",
 idx_h="Скины CS2", idx_p="Справочник скинов из конструктора Skinset: у каждого — цены по качеству, цвета, похожие скины и готовые сеты с ножом и перчатками в тон.",
 color_set="Сет «{c}»"),
"en": dict(
 title="{name} — price, wear and what to pair it with | Skinset", desc="{name}: prices by wear from {pmin}, {rar} rarity, colors and ready loadouts with a matching knife and gloves. Buy on DMarket.",
 crumbs=("Home", "CS2 skins"), h1="{name}", sub="{w} skin · {rar}", coll="Collection", typ="Type", rarL="Rarity", colL="Colors",
 intro="{name} is a {rar} skin for the {w}{coll}. Main colors: {cols}. The cheapest version on the market right now is {cw} from {cp}{fn}.",
 fn=", Factory New starts at {p}", ratio="The gap between the cheapest and the most expensive wear is about {x}×, so the wear you pick changes the set price a lot.",
 price_h="{name} price by wear", tab=("Wear", "From", ""), buy="Buy", noprice="not listed", live="Prices update every 4 hours; exact price and float are on DMarket.",
 sets_h="What to pair {name} with", sets_p="The Skinset builder matched a knife, gloves and guns in the same palette ({color}). Click “Open in builder” to load the set and swap any slot.",
 cheap="Budget set", lux="Max set", total="Total", open="Open in builder",
 sim_h="Similar skins by color", more_h="More {w} skins", all="All CS2 skins",
 faq_h="FAQ",
 q1="How much is {name}?", a1="{name} currently starts at {pmin} ({cw}). {fnq}Prices are market minimums and update every 4 hours.", a1fn="Factory New starts at {p}. ",
 q2="What goes well with {name}?", a2="{name} pairs well with {pair}. That combo comes from the Skinset max set in the {color} palette; a cheaper version is on this page too.",
 q3="Which wear of {name} should I buy?", a3="To save money, take {cw} — it's the cheapest. If looks matter, check Factory New or Minimal Wear: the pattern has no scratches.",
 cta="Build a set with this skin →", idx_t="All CS2 skins: prices, wear and combos — Skinset", idx_d="CS2 skin guide: {n} skins with prices by wear, colors and ready loadouts. Knives, gloves, AK-47, AWP, M4 and pistols.",
 idx_h="CS2 skins", idx_p="Skin guide from the Skinset builder: each skin has prices by wear, colors, similar skins and ready sets with a matching knife and gloves.",
 color_set="{c} set"),
"de": dict(
 title="{name} — Preis, Zustand und Kombinationen | Skinset", desc="{name}: Preise nach Zustand ab {pmin}, Seltenheit {rar}, Farben und fertige Loadouts mit passendem Messer und Handschuhen. Kaufen bei DMarket.",
 crumbs=("Start", "CS2-Skins"), h1="{name}", sub="{w}-Skin · {rar}", coll="Kollektion", typ="Typ", rarL="Seltenheit", colL="Farben",
 intro="{name} ist ein {rar}-Skin für die {w}{coll}. Hauptfarben: {cols}. Die günstigste Variante auf dem Markt ist gerade {cw} ab {cp}{fn}.",
 fn=", Factory New ab {p}", ratio="Zwischen dem günstigsten und dem teuersten Zustand liegt etwa Faktor {x} — der Zustand verändert den Set-Preis stark.",
 price_h="{name} Preis nach Zustand", tab=("Zustand", "Ab", ""), buy="Kaufen", noprice="nicht gelistet", live="Preise werden alle 4 Stunden aktualisiert; genauer Preis und Float auf DMarket.",
 sets_h="Womit {name} kombinieren", sets_p="Der Skinset-Builder hat Messer, Handschuhe und Waffen in derselben Palette gewählt ({color}). „Im Builder öffnen“ lädt das Set — dann jeden Slot tauschen.",
 cheap="Günstiges Set", lux="Maximales Set", total="Gesamt", open="Im Builder öffnen",
 sim_h="Ähnliche Skins nach Farbe", more_h="Weitere {w}-Skins", all="Alle CS2-Skins",
 faq_h="FAQ",
 q1="Was kostet {name}?", a1="{name} kostet aktuell ab {pmin} ({cw}). {fnq}Preise sind Marktminima und werden alle 4 Stunden aktualisiert.", a1fn="Factory New ab {p}. ",
 q2="Was passt zu {name}?", a2="Zu {name} passen {pair}. Die Kombination stammt aus dem maximalen Skinset-Set in der Palette {color}; eine günstigere Version steht ebenfalls hier.",
 q3="Welchen Zustand von {name} kaufen?", a3="Zum Sparen nimm {cw} — das ist am günstigsten. Wenn die Optik zählt, schau auf Factory New oder Minimal Wear.",
 cta="Set mit diesem Skin bauen →", idx_t="Alle CS2-Skins: Preise, Zustand und Kombinationen — Skinset", idx_d="CS2-Skin-Guide: {n} Skins mit Preisen nach Zustand, Farben und fertigen Loadouts. Messer, Handschuhe, AK-47, AWP, M4 und Pistolen.",
 idx_h="CS2-Skins", idx_p="Skin-Guide aus dem Skinset-Builder: zu jedem Skin Preise nach Zustand, Farben, ähnliche Skins und fertige Sets mit passendem Messer und Handschuhen.",
 color_set="Set „{c}“"),
"pt": dict(
 title="{name} — preço, desgaste e com o que combinar | Skinset", desc="{name}: preços por desgaste a partir de {pmin}, raridade {rar}, cores e sets prontos com faca e luvas combinando. Compre na DMarket.",
 crumbs=("Início", "Skins de CS2"), h1="{name}", sub="Skin de {w} · {rar}", coll="Coleção", typ="Tipo", rarL="Raridade", colL="Cores",
 intro="{name} é uma skin {rar} para a {w}{coll}. Cores principais: {cols}. A versão mais barata no mercado agora é {cw} a partir de {cp}{fn}.",
 fn=", Factory New a partir de {p}", ratio="A diferença entre o desgaste mais barato e o mais caro é de cerca de {x}×, então o desgaste muda muito o preço do set.",
 price_h="Preço de {name} por desgaste", tab=("Desgaste", "A partir de", ""), buy="Comprar", noprice="sem anúncio", live="Os preços atualizam a cada 4 horas; preço exato e float na DMarket.",
 sets_h="Com o que combinar {name}", sets_p="O montador Skinset escolheu faca, luvas e armas na mesma paleta ({color}). Clique em “Abrir no montador” para carregar o set e trocar qualquer slot.",
 cheap="Set econômico", lux="Set máximo", total="Total", open="Abrir no montador",
 sim_h="Skins parecidas pela cor", more_h="Mais skins de {w}", all="Todas as skins de CS2",
 faq_h="Perguntas frequentes",
 q1="Quanto custa {name}?", a1="{name} custa agora a partir de {pmin} ({cw}). {fnq}Os preços são mínimos de mercado e atualizam a cada 4 horas.", a1fn="Factory New a partir de {p}. ",
 q2="Com o que {name} combina?", a2="{name} combina bem com {pair}. A combinação vem do set máximo do Skinset na paleta {color}; uma versão mais barata também está nesta página.",
 q3="Qual desgaste de {name} comprar?", a3="Para economizar, pegue {cw} — é o mais barato. Se o visual importa, veja Factory New ou Minimal Wear.",
 cta="Montar um set com esta skin →", idx_t="Todas as skins de CS2: preços, desgaste e combinações — Skinset", idx_d="Guia de skins de CS2: {n} skins com preços por desgaste, cores e sets prontos. Facas, luvas, AK-47, AWP, M4 e pistolas.",
 idx_h="Skins de CS2", idx_p="Guia de skins do montador Skinset: cada skin tem preços por desgaste, cores, skins parecidas e sets prontos com faca e luvas combinando.",
 color_set="Set {c}"),
"tr": dict(
 title="{name} — fiyat, aşınma ve neyle uyumlu | Skinset", desc="{name}: aşınmaya göre fiyatlar {pmin}'den başlar, nadirlik {rar}, renkler ve uyumlu bıçak ile eldivenli hazır setler. DMarket'ten al.",
 crumbs=("Ana sayfa", "CS2 skinleri"), h1="{name}", sub="{w} skini · {rar}", coll="Koleksiyon", typ="Tür", rarL="Nadirlik", colL="Renkler",
 intro="{name}, {w} için {rar} nadirlikte bir skin{coll}. Ana renkler: {cols}. Şu an piyasadaki en ucuz sürüm {cw}, {cp} fiyattan başlıyor{fn}.",
 fn="; Factory New {p}'den başlıyor", ratio="En ucuz ve en pahalı aşınma arasındaki fark yaklaşık {x} kat — aşınma seçimi set fiyatını çok etkiler.",
 price_h="Aşınmaya göre {name} fiyatı", tab=("Aşınma", "En düşük", ""), buy="Satın al", noprice="ilan yok", live="Fiyatlar 4 saatte bir güncellenir; kesin fiyat ve float DMarket'te.",
 sets_h="{name} neyle uyumlu", sets_p="Skinset oluşturucusu aynı paletten bıçak, eldiven ve silah seçti ({color}). Seti yüklemek ve istediğin slotu değiştirmek için “Oluşturucuda aç”a tıkla.",
 cheap="Uygun fiyatlı set", lux="Maksimum set", total="Toplam", open="Oluşturucuda aç",
 sim_h="Renge göre benzer skinler", more_h="Diğer {w} skinleri", all="Tüm CS2 skinleri",
 faq_h="Sık sorulan sorular",
 q1="{name} ne kadar?", a1="{name} şu an {pmin}'den başlıyor ({cw}). {fnq}Fiyatlar piyasa minimumudur ve 4 saatte bir güncellenir.", a1fn="Factory New {p}'den başlıyor. ",
 q2="{name} neyle uyumlu?", a2="{name} ile {pair} iyi gider. Bu kombinasyon Skinset'in {color} paletindeki maksimum setinden; daha ucuz sürümü de bu sayfada.",
 q3="{name} için hangi aşınma alınmalı?", a3="Tasarruf için {cw} al — en ucuzu bu. Görünüm önemliyse Factory New veya Minimal Wear'a bak.",
 cta="Bu skinle set kur →", idx_t="Tüm CS2 skinleri: fiyatlar, aşınma ve kombinasyonlar — Skinset", idx_d="CS2 skin rehberi: aşınmaya göre fiyatları, renkleri ve hazır setleriyle {n} skin. Bıçaklar, eldivenler, AK-47, AWP, M4 ve tabancalar.",
 idx_h="CS2 skinleri", idx_p="Skinset oluşturucusundan skin rehberi: her skin için aşınmaya göre fiyatlar, renkler, benzer skinler ve uyumlu bıçak ile eldivenli hazır setler.",
 color_set="{c} set"),
"pl": dict(
 title="{name} — cena, stan i z czym łączyć | Skinset", desc="{name}: ceny według stanu od {pmin}, rzadkość {rar}, kolory i gotowe zestawy z pasującym nożem i rękawicami. Kup na DMarket.",
 crumbs=("Start", "Skiny CS2"), h1="{name}", sub="Skin do {w} · {rar}", coll="Kolekcja", typ="Typ", rarL="Rzadkość", colL="Kolory",
 intro="{name} to skin {rar} do {w}{coll}. Główne kolory: {cols}. Najtańsza wersja na rynku to teraz {cw} od {cp}{fn}.",
 fn=", Factory New od {p}", ratio="Różnica między najtańszym a najdroższym stanem to około {x}×, więc wybór stanu mocno zmienia cenę zestawu.",
 price_h="Cena {name} według stanu", tab=("Stan", "Od", ""), buy="Kup", noprice="brak ofert", live="Ceny aktualizują się co 4 godziny; dokładna cena i float na DMarket.",
 sets_h="Z czym łączyć {name}", sets_p="Kreator Skinset dobrał nóż, rękawice i bronie w tej samej palecie ({color}). Kliknij „Otwórz w kreatorze”, aby wczytać zestaw i wymienić dowolny slot.",
 cheap="Tani zestaw", lux="Maksymalny zestaw", total="Razem", open="Otwórz w kreatorze",
 sim_h="Podobne skiny według koloru", more_h="Inne skiny {w}", all="Wszystkie skiny CS2",
 faq_h="Pytania i odpowiedzi",
 q1="Ile kosztuje {name}?", a1="{name} kosztuje teraz od {pmin} ({cw}). {fnq}Ceny to minima rynkowe, aktualizowane co 4 godziny.", a1fn="Factory New od {p}. ",
 q2="Z czym pasuje {name}?", a2="Do {name} dobrze pasują {pair}. To połączenie z maksymalnego zestawu Skinset w palecie {color}; tańsza wersja jest na tej stronie.",
 q3="Jaki stan {name} kupić?", a3="Żeby oszczędzić, bierz {cw} — to najtańsza opcja. Jeśli liczy się wygląd, patrz na Factory New lub Minimal Wear.",
 cta="Zbuduj zestaw z tym skinem →", idx_t="Wszystkie skiny CS2: ceny, stan i połączenia — Skinset", idx_d="Przewodnik po skinach CS2: {n} skinów z cenami według stanu, kolorami i gotowymi zestawami. Noże, rękawice, AK-47, AWP, M4 i pistolety.",
 idx_h="Skiny CS2", idx_p="Przewodnik po skinach z kreatora Skinset: dla każdego skina ceny według stanu, kolory, podobne skiny i gotowe zestawy z pasującym nożem i rękawicami.",
 color_set="Zestaw {c}"),
}
COLLW = {"ru": ", из коллекции «{c}»", "en": " from the {c}", "de": " aus der {c}", "pt": " da {c}", "tr": " ({c})", "pl": " z {c}"}
GROUPS = [("knife", {"ru": "Ножи", "en": "Knives", "de": "Messer", "pt": "Facas", "tr": "Bıçaklar", "pl": "Noże"}),
          ("gloves", {"ru": "Перчатки", "en": "Gloves", "de": "Handschuhe", "pt": "Luvas", "tr": "Eldivenler", "pl": "Rękawice"}),
          ("ak", None), ("m4", None), ("m4s", None), ("awp", None), ("deagle", None), ("usp", None), ("glock", None)]

# ---------- данные ----------
WS = json.load(open(os.path.join(ROOT, "data/wiki-sets.json")))
NAMES = list(WS)
PR = json.load(open(os.path.join(ROOT, "data/prices.json")))
API = {}
for r in json.load(open(os.path.join(ROOT, "admin/skins-api.json"))):
    API.setdefault((r[0], r[5] or ""), r); API.setdefault((r[0], ""), r)


def api(name):
    m = re.match(r"(.*?)\s*\((.*)\)$", name)
    b, ph = (m.group(1), m.group(2)) if m else (name, "")
    return API.get((b, ph)) or API.get((b, ""))


def slugify(n):
    s = n.lower().replace("★", "").replace("|", " ").replace("&", " and ").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


SLUG = {n: slugify(n) for n in NAMES if n in WS and any((PR.get(n) or {}).get("w", {}).values())}
assert len(set(SLUG.values())) == len(SLUG), "duplicate slugs"


def url(lang, n): return f"{WIKI[lang]}{SLUG[n]}/"


def hex2rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cname(h):
    r, g, b = hex2rgb(h)
    return min(CN, key=lambda c: sum((x - y) ** 2 * w for x, y, w in zip((r, g, b), hex2rgb(c[1]), (3, 4, 2))))[0]


def r2(v):  # округление до 2 значащих — меньше лишних коммитов
    if v <= 0: return 0
    k = 10 ** max(0, int(math.log10(v)) - 1); return round(v / k) * k


def lp(lang, rub): return money(lang, r2(rub / RATE[lang]) if rub / RATE[lang] >= 10 else rub / RATE[lang])


def dm(name, wear=None):
    base = re.sub(r"\s*\(.*\)$", "", name)
    q = f"https://dmarket.com/ingame-items/item-list/csgo-skins?title={quote(base.replace(' | ', ' '))}"
    if wear: q += "&exterior=" + quote(WEARN["*"][wear].lower().replace(" ", "-"))
    return q + "&ref=" + REF


CSS = BASE_CSS + r"""
.wk{max-width:1100px;margin:0 auto;padding:28px 0 60px}
.crumbs{font-size:.85rem;color:var(--soft);margin-bottom:18px}.crumbs a{color:var(--soft)}
.wk h1{font-size:clamp(2rem,4.4vw,3.2rem);margin:6px 0 8px;text-transform:none}
.wk .sub{color:var(--soft);font:500 .9rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase}
.top{display:grid;grid-template-columns:1.1fr 1fr;gap:28px;align-items:center;margin:18px 0 10px}
.pic{background:radial-gradient(closest-side,rgba(255,255,255,.08),transparent),linear-gradient(160deg,rgba(255,255,255,.06),rgba(255,255,255,.01));border:1px solid var(--line2);border-bottom:3px solid var(--rc,var(--pick));padding:18px;clip-path:polygon(16px 0,100% 0,100% calc(100% - 16px),calc(100% - 16px) 100%,0 100%,0 16px)}
.pic img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:contain;filter:drop-shadow(0 16px 20px rgba(0,0,0,.6))}
.facts{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.facts li{display:flex;justify-content:space-between;gap:12px;padding:10px 14px;background:rgba(14,15,17,.72);border:1px solid var(--line)}
.facts span{color:var(--soft)}.facts b{font-weight:500;text-align:right}
.sw{display:inline-flex;gap:5px;vertical-align:middle}.sw i{width:16px;height:16px;border:1px solid rgba(255,255,255,.3);display:inline-block}
.lead2{font-size:1.08rem;color:var(--ink);max-width:75ch}
.wk h2{font-size:clamp(1.3rem,2.4vw,1.8rem);margin:44px 0 16px}
.pt{width:100%;border-collapse:collapse}.pt td,.pt th{padding:11px 12px;border-bottom:1px solid var(--line);text-align:left}
.pt th{font:600 .74rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--soft)}
.pt td:nth-child(2){font:600 1.05rem/1 var(--hud);white-space:nowrap}.pt td:last-child{text-align:right}
.pt small{color:var(--dim);display:block;font-size:.78rem}
.bb{display:inline-block;padding:8px 12px;border:1px solid var(--line2);font:600 .72rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;text-decoration:none}.bb:hover{border-color:var(--pick);color:var(--pick)}
.note{color:var(--dim);font-size:.85rem}
.sets{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.st{border:1px solid var(--line);background:rgba(14,15,17,.72);padding:16px}
.st h3{margin:0 0 12px;font:600 1rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase}
.st ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.st li{display:flex;align-items:center;gap:10px;font-size:.9rem}.st li.cur b{color:var(--pick)}
.st li img{width:56px;height:42px;object-fit:contain;flex:none}
.st li span{display:flex;flex-direction:column;min-width:0}.st li b{font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.st li small{color:var(--soft);font-size:.76rem}
.st .ft{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;margin-top:12px;color:var(--soft)}.st .ft b{color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.cardk{display:block;text-decoration:none;border:1px solid var(--line);background:rgba(14,15,17,.72);padding:10px;transition:border-color .15s,transform .15s}
.cardk:hover{border-color:var(--line2);transform:translateY(-2px)}
.cardk img{display:block;width:100%;height:90px;object-fit:contain}
.cardk b{display:block;font:500 .9rem/1.2 var(--body);margin-top:6px}.cardk small{color:var(--soft);font-size:.78rem}
.faq h3{font:600 1.05rem/1.25 var(--hud);text-transform:uppercase;letter-spacing:.03em;margin:20px 0 6px}.faq p{color:var(--soft);margin:0}
.idx h2{scroll-margin-top:80px}.jump{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0}.jump a{padding:7px 10px;border:1px solid var(--line2);text-decoration:none;font-size:.85rem}
@media(max-width:860px){.top,.sets{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,1fr)}}
"""
import hashlib
CSS_V = hashlib.md5(CSS.encode()).hexdigest()[:8]
RCOL = {"Consumer Grade": "#b0c3d9", "Industrial Grade": "#5e98d9", "Mil-Spec Grade": "#4b69ff", "Restricted": "#8847ff", "Classified": "#d32ce6", "Covert": "#eb4b4b", "Extraordinary": "#e4ae39", "Contraband": "#e4ae39"}

LIVE_JS = r"""<script>(async()=>{try{const r=await fetch("/data/prices.json",{cache:"default"});if(!r.ok)return;const P=await r.json();const R=+document.body.dataset.rate||1;const f=new Intl.NumberFormat(document.documentElement.lang,{maximumFractionDigits:R>=50?2:0});
document.querySelectorAll("[data-pk]").forEach(td=>{const p=P[td.dataset.pk];const v=p&&p.w&&p.w[td.dataset.w];if(v){td.textContent=td.dataset.pre+f.format(v*90/R)+td.dataset.suf}})}catch(e){}})();</script>"""


def head(lang, title, desc, canon, alts, ld, extra=""):
    CSSV = CSS_V
    return f"""<!doctype html>
<html lang="{HREFLANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
{alts}
<meta property="og:type" content="website"><meta property="og:url" content="{canon}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{e(extra or SITE + '/img/og-' + lang + '.png')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0c0f">
<link rel="icon" type="image/svg+xml" href="/img/favicon.svg"><link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Roboto+Condensed:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/wiki.css?v={CSSV}">
{''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)}
</head>"""


def header(lang, langlinks):
    nav = "".join(f'<a href="{h}"{" class=on" if h == WIKI[lang] else ""}>{e(n)}</a>' for h, n in NAV[lang]) + f'<a href="{ABOUT[lang]}">{e(ABOUT_LABEL[lang])}</a>'
    lm = "".join(f'<a href="{langlinks[l]}" hreflang="{HREFLANG[l]}"{" class=on" if l == lang else ""}><span>{LNAMES[l]}</span><small>{l.upper()}</small></a>' for l in LANGS)
    return f"""<header class="hud">
  <a class="logo" href="{HOME[lang]}"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 26 L12 6 H20 L28 26 H22 L16 12 L10 26 Z" fill="#e8402a"/><path d="M11 20 H21 L23 26 H9 Z" fill="#fff" opacity=".9"/></svg>Skinset</a>
  <nav class="tabs">{nav}</nav>
  <div class="langs"><button class="lbtn" type="button" aria-haspopup="menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg><span>{lang.upper()}</span></button><div class="lmenu">{lm}</div></div>
</header>"""


FOOT = {"ru": "Skinset — фанатский проект, не связан с Valve. Названия предметов принадлежат их правообладателям.",
        "en": "Skinset is a fan project, not affiliated with Valve. Item names belong to their owners.",
        "de": "Skinset ist ein Fanprojekt ohne Verbindung zu Valve. Itemnamen gehören ihren Inhabern.",
        "pt": "Skinset é um projeto de fã, sem ligação com a Valve. Os nomes dos itens pertencem aos seus donos.",
        "tr": "Skinset bir hayran projesidir, Valve ile bağlantısı yoktur. Eşya adları sahiplerine aittir.",
        "pl": "Skinset to projekt fanowski, niezwiązany z Valve. Nazwy przedmiotów należą do ich właścicieli."}


def money_parts(lang):
    s = money(lang, 12345)  # разбираем формат на префикс/суффикс
    m = re.match(r"^(\D*?)(\d[\d.,\u00a0 ]*\d)(\D*)$", s)
    return m.group(1), m.group(3)


def wname(lang, w): return (WEARN.get(lang) or WEARN["*"])[w]


def setcard(lang, title, rows, me, colors_pi):
    t = T[lang]; lis = []
    for r in rows:
        n = f"{r[1].replace('★ ', '')} | {r[2]}"; a = api(n); im = a[1] if a else ""
        inner = f'<img src="{e(im)}" alt="{e(n)}" loading="lazy" width="56" height="42">' if im else ""
        label = f'<a href="{url(lang, n)}">{e(n)}</a>' if n in SLUG and n != me else e(n)
        lis.append(f'<li{" class=cur" if n == me else ""}>{inner}<span><b>{label}</b><small>{e(r[4] or "")}{" · " if r[4] else ""}{e(lp(lang, r[3]))}</small></span></li>')
    q = quote(";".join(f"{r[1]}|{r[2]}" for r in rows), safe="")
    href = f"{HOME[lang]}{CP[lang][colors_pi]}/?set={q}"
    tot = sum(r[3] for r in rows)
    return f'<div class="st"><h3>{e(title)}</h3><ul>{"".join(lis)}</ul><div class="ft"><span>{e(t["total"])}: <b>≈ {e(lp(lang, tot))}</b></span><a class="bb" href="{e(href)}">{e(t["open"])} →</a></div></div>'


def card(lang, n):
    a = api(n); im = a[1] if a else ""
    w, sk = n.split(" | ", 1)
    p = minprice(n)
    return f'<a class="cardk" href="{url(lang, n)}"><img src="{e(im)}" alt="{e(n)}" loading="lazy" width="200" height="150"><b>{e(sk)}</b><small>{e(w)}{" · " + e(lp(lang, p[1])) if p else ""}</small></a>'


def minprice(n):
    p = PR.get(n)
    if not p or not p.get("w"): return None
    w, v = min(((k, v) for k, v in p["w"].items() if v), key=lambda z: z[1], default=(None, None))
    return (w, v * 90) if w else None


def page(lang, n):
    t = T[lang]; d = WS[n]; a = api(n)
    w, sk = n.split(" | ", 1)
    rar_en = a[2] if a else ""; rar = (RAR.get(lang) or {}).get(rar_en, rar_en)
    coll = a[6] if a and len(a) > 6 and a[6] else ""
    im = a[1] if a else ""
    cols = []
    for h in d["c"]:
        c = cname(h)
        if c not in cols: cols.append(c)
    colsn = ", ".join(CNAME[lang][c] for c in cols[:3])
    pw = (PR.get(n) or {}).get("w") or {}
    wp = [(k, pw[k] * 90) for k in WEARS if pw.get(k)]
    if not wp: return None
    cw, cp = min(wp, key=lambda z: z[1]); mx = max(v for _, v in wp)
    fnp = dict(wp).get("FN")
    pi = d["preset"]; colorname = PNAMES[lang][pi].lower() if lang not in ("de",) else PNAMES[lang][pi]
    F = dict(name=n, w=w, rar=rar, pmin=lp(lang, cp), cw=wname(lang, cw) if lang == "ru" else WEARN["*"][cw], cp=lp(lang, cp),
             cols=colsn, coll=COLLW[lang].format(c=coll) if coll else "", color=colorname)
    intro = t["intro"].format(**F, fn=t["fn"].format(p=lp(lang, fnp)) if fnp and cw != "FN" else "")
    ratio = t["ratio"].format(x=f"{mx / cp:.1f}".replace(".", "," if lang != "en" else ".")) if len(wp) > 1 and mx / cp >= 1.5 else ""
    pre, suf = money_parts(lang)
    rows = []
    for k in WEARS:
        v = pw.get(k)
        nm = f"{wname(lang, k)}" + (f"<small>{WEARN['*'][k]}</small>" if lang == "ru" else f"<small>{k}</small>")
        if v:
            rows.append(f'<tr><td>{nm}</td><td data-pk="{e(n)}" data-w="{k}" data-pre="{e(pre)}" data-suf="{e(suf)}">{e(lp(lang, v * 90))}</td><td><a class="bb" href="{e(dm(n, k))}" target="_blank" rel="nofollow sponsored noopener">{e(t["buy"])}</a></td></tr>')
    # пара для FAQ
    pair = [r for r in d["lux"] if r[0] in ("knife", "gloves") and f"{r[1].replace('★ ', '')} | {r[2]}" != n]
    pair_s = (" и " if lang == "ru" else " and " if lang == "en" else " und " if lang == "de" else " e " if lang == "pt" else " ve " if lang == "tr" else " i ").join(f"{r[1].replace('★ ', '')} | {r[2]}" for r in pair[:2]) or "—"
    faq = [(t["q1"].format(**F), t["a1"].format(**F, fnq=t["a1fn"].format(p=lp(lang, fnp)) if fnp and cw != "FN" else "")),
           (t["q2"].format(**F), t["a2"].format(**F, pair=pair_s)),
           (t["q3"].format(**F), t["a3"].format(**F))]
    sim = [x for x in d["sim"] if x in SLUG][:8]
    more = [x for x in NAMES if x in SLUG and x != n and x.split(" | ")[0] == w and x not in sim][:8]
    canon = SITE + url(lang, n)
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{url(l, n)}">' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{url("en", n)}">'
    ld = [{"@context": "https://schema.org", "@type": "Product", "name": n, "image": im, "description": intro, "brand": {"@type": "Brand", "name": "Counter-Strike 2"},
           "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": round(min(pw[k] for k in pw if pw[k]), 2), "highPrice": round(max(pw[k] for k in pw if pw[k]), 2), "offerCount": len(wp), "url": dm(n)}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": t["crumbs"][0], "item": SITE + HOME[lang]},
              {"@type": "ListItem", "position": 2, "name": t["crumbs"][1], "item": SITE + WIKI[lang]},
              {"@type": "ListItem", "position": 3, "name": n, "item": canon}]}]
    title = t["title"].format(**F); desc = t["desc"].format(**F)
    setq = quote(f"{d['w']}|{d['sk']}", safe="")
    sw = "".join(f'<i style="background:{h}"></i>' for h in d["c"][:4])
    body = f"""<body data-rate="{RATE[lang]}">
{header(lang, {l: url(l, n) for l in LANGS})}
<main><article class="wk">
<nav class="crumbs"><a href="{HOME[lang]}">{e(t['crumbs'][0])}</a> › <a href="{WIKI[lang]}">{e(t['crumbs'][1])}</a> › {e(w)} › {e(sk)}</nav>
<span class="sub">{e(t['sub'].format(**F))}</span>
<h1>{e(n)}</h1>
<div class="top"><div class="pic" style="--rc:{RCOL.get(rar_en, '#c4161c')}"><img src="{e(im)}" alt="{e(n)}" width="512" height="384"></div>
<div><ul class="facts"><li><span>{e(t['typ'])}</span><b>{e(w)}</b></li><li><span>{e(t['rarL'])}</span><b style="color:{RCOL.get(rar_en, '#fff')}">{e(rar)}</b></li>{f'<li><span>{e(t["coll"])}</span><b>{e(coll)}</b></li>' if coll else ''}<li><span>{e(t['colL'])}</span><b><span class="sw">{sw}</span> {e(colsn)}</b></li><li><span>{e(t['tab'][1])}</span><b>{e(lp(lang, cp))}</b></li></ul>
<div class="btns" style="margin-top:16px"><a class="btn p" href="{HOME[lang]}{CP[lang][pi]}/?set={setq}">{e(t['cta'])}</a></div></div></div>
<p class="lead2">{e(intro)}</p>{f'<p class="note">{e(ratio)}</p>' if ratio else ''}
<h2>{e(t['price_h'].format(**F))}</h2>
<table class="pt"><thead><tr><th>{e(t['tab'][0])}</th><th>{e(t['tab'][1])}</th><th></th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="note">{e(t['live'])}</p>
<h2>{e(t['sets_h'].format(**F))}</h2><p>{e(t['sets_p'].format(**F))}</p>
<div class="sets">{setcard(lang, t['cheap'], d['cheap'], n, pi)}{setcard(lang, t['lux'], d['lux'], n, pi)}</div>
<p><a href="{HOME[lang]}{CP[lang][pi]}/">{e(t['color_set'].format(c=PNAMES[lang][pi]))} →</a></p>
{f'<h2>{e(t["sim_h"])}</h2><div class="grid">{"".join(card(lang, x) for x in sim)}</div>' if sim else ''}
{f'<h2>{e(t["more_h"].format(**F))}</h2><div class="grid">{"".join(card(lang, x) for x in more)}</div>' if more else ''}
<section class="faq" style="padding:0"><h2>{e(t['faq_h'])}</h2>{''.join(f'<h3>{e(q)}</h3><p>{e(a_)}</p>' for q, a_ in faq)}</section>
<p style="margin-top:36px"><a href="{WIKI[lang]}">← {e(t['all'])}</a></p>
</article></main>
<footer><p>{e(FOOT[lang])}</p></footer>
{LANG_JS}{LIVE_JS}
</body>
</html>
"""
    return head(lang, title, desc, canon, alts, ld, im) + "\n" + body


def index(lang):
    t = T[lang]; n = len(SLUG)
    canon = SITE + WIKI[lang]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{WIKI[l]}">' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{WIKI["en"]}">'
    groups = []
    for slot, gn in GROUPS:
        items = [x for x in NAMES if x in SLUG and WS[x]["slot"] == slot]
        if not items: continue
        title = gn[lang] if gn else items[0].split(" | ")[0]
        items.sort(key=lambda x: -(minprice(x) or (0, 0))[1])
        groups.append((slot, title, items))
    other = [x for x in NAMES if x in SLUG and WS[x]["slot"] not in [g[0] for g in GROUPS]]
    if other: groups.append(("other", {"ru": "Другое", "en": "Other", "de": "Andere", "pt": "Outros", "tr": "Diğer", "pl": "Inne"}[lang], other))
    jump = "".join(f'<a href="#{s}">{e(ti)} <small>{len(it)}</small></a>' for s, ti, it in groups)
    body = "".join(f'<h2 id="{s}">{e(ti)}</h2><div class="grid">{"".join(card(lang, x) for x in it)}</div>' for s, ti, it in groups)
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": t["idx_h"], "url": canon, "description": t["idx_d"].format(n=n)}]
    return head(lang, t["idx_t"], t["idx_d"].format(n=n), canon, alts, ld) + f"""
<body data-rate="{RATE[lang]}">
{header(lang, WIKI)}
<main><article class="wk idx">
<nav class="crumbs"><a href="{HOME[lang]}">{e(t['crumbs'][0])}</a> › {e(t['crumbs'][1])}</nav>
<h1>{e(t['idx_h'])}</h1><p class="lead2">{e(t['idx_p'])}</p>
<div class="jump">{jump}</div>
{body}
</article></main>
<footer><p>{e(FOOT[lang])}</p></footer>
{LANG_JS}
</body>
</html>
"""


def main():
    import navmore
    open(os.path.join(ROOT, "wiki.css"), "w", encoding="utf-8").write(CSS)
    made = []
    for lang in LANGS:
        for n in SLUG:
            h = page(lang, n)
            if not h: continue
            h = navmore.fix(h)
            out = os.path.join(ROOT, url(lang, n).strip("/"), "index.html")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            old = open(out, encoding="utf-8").read() if os.path.exists(out) else None
            if old != h: open(out, "w", encoding="utf-8").write(h)
            made.append(url(lang, n))
        made.append(WIKI[lang])
    json.dump(sorted(SLUG), open(os.path.join(ROOT, "data/wiki-index.json"), "w"), ensure_ascii=False)
    import catalog; catalog.main()  # индекс /skiny/ — каталог с фильтрами
    # отдельная карта сайта для вики
    d = datetime.date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{p}</loc></url>\n" for p in made) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap-skins.xml"), "w", encoding="utf-8").write(sm)
    print(len(made), "pages")


if __name__ == "__main__":
    main()
