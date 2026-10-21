# -*- coding: utf-8 -*-
"""Каталог скинов CS2 с фильтрами (как на маркетплейсах) — /skiny/, /en/skins/ и т.д.
Запуск: python3 admin/catalog.py          — данные + страницы каталога на 6 языках
        python3 admin/catalog.py --data   — только data/catalog.json (для бота цен)
Данные: RAW из index.html + data/skins-extra.json (цвета), admin/skins-api.json (картинки, редкость, тип),
        data/prices.json (цены по качеству), data/wiki-index.json (у каких скинов есть своя страница).
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
e = lambda s: html.escape(str(s), quote=True)
IMGP = "https://community.akamai.steamstatic.com/economy/image/"
WEARS = ["FN", "MW", "FT", "WW", "BS"]
SNIPER = {"AWP", "SSG 08", "SCAR-20", "G3SG1"}
CATS = ["knife", "gloves", "rifle", "sniper", "pistol", "smg", "heavy"]
APICAT = {"Knives": "knife", "Gloves": "gloves", "Rifles": "rifle", "Pistols": "pistol", "SMGs": "smg", "Heavy": "heavy"}
FAM = [("red", "#d1222b"), ("orange", "#f27420"), ("gold", "#e0b43a"), ("green", "#25a55f"), ("teal", "#14b8bd"), ("blue", "#2457e0"),
       ("purple", "#7a3bd0"), ("pink", "#ff5cb0"), ("white", "#f2f2f2"), ("gray", "#8c8c8c"), ("black", "#161616"), ("brown", "#7a5230")]
# точки отсчёта для определения семейства цвета
REFC = [("red", "#c4161c"), ("red", "#6a0f14"), ("orange", "#f26a1b"), ("gold", "#d4af37"), ("gold", "#f2d230"), ("green", "#1d9b5a"), ("green", "#6b6b3a"),
        ("teal", "#00b3b8"), ("blue", "#1f4fd6"), ("blue", "#1a2350"), ("purple", "#6a2bb5"), ("pink", "#ff5cb0"), ("white", "#f0f0f0"),
        ("gray", "#8a8a8a"), ("black", "#151515"), ("brown", "#6b4a2b")]
PHASES = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Ruby", "Sapphire", "Emerald", "Black Pearl"]
RAR_ORDER = ["Consumer Grade", "Industrial Grade", "Mil-Spec Grade", "Restricted", "Classified", "Covert", "Extraordinary", "Contraband"]


def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fam(h):
    r, g, b = rgb(h)
    return min(REFC, key=lambda c: sum((x - y) ** 2 * w for x, y, w in zip((r, g, b), rgb(c[1]), (3, 4, 2))))[0]


def build_data():
    s = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    i = s.find("const RAW"); j = s.find("];", i)
    raw = re.sub(r"//[^\n]*", "", s[s.find("[", i):j + 1]); raw = re.sub(r",\s*]$", "]", raw.strip())
    rows = [(r[1], r[2], r[4:]) for r in json.loads(raw)]
    rows += [(r[1], r[2], r[4]) for r in json.load(open(os.path.join(ROOT, "data/skins-extra.json")))]
    cols = {}
    for w, sk, c in rows:
        cols.setdefault(w.replace("★ ", "") + " | " + sk, c)
    api = {}
    for r in json.load(open(os.path.join(ROOT, "admin/skins-api.json"))):
        api.setdefault((r[0], r[5] or ""), r); api.setdefault((r[0], ""), r)
    pr = json.load(open(os.path.join(ROOT, "data/prices.json")))
    try: wiki = set(json.load(open(os.path.join(ROOT, "data/wiki-index.json"))))
    except Exception: wiki = set()
    out = []
    for n, p in pr.items():
        w = p.get("w") or {}
        ps = [round(w.get(k) or 0, 2) for k in WEARS]
        if not any(ps): continue
        m = re.match(r"(.*?)\s*\((.*)\)$", n)
        base, ph = (m.group(1), m.group(2)) if m else (n, "")
        a = api.get((base, ph)) or api.get((base, ""))
        if not a or " | " not in base: continue
        weapon, skin = n.split(" | ", 1)
        cat = APICAT.get(a[4])
        if not cat: continue
        if cat == "rifle" and weapon in SNIPER: cat = "sniper"
        c = cols.get(n) or cols.get(base) or []
        fams = []
        for h in c[:3]:
            f = fam(h)
            if f not in fams: fams.append(f)
        img = a[1][len(IMGP):] if a[1].startswith(IMGP) else a[1]
        slug = None
        if n in wiki:
            slug = re.sub(r"[^a-z0-9]+", "-", n.lower().replace("★", "").replace("|", " ").replace("&", " and ").replace("'", "")).strip("-")
        out.append({"n": n, "w": weapon, "s": skin, "c": cat, "ph": ph if ph in PHASES else "", "r": RAR_ORDER.index(a[2]) if a[2] in RAR_ORDER else 0,
                    "f": [FAM.index(next(x for x in FAM if x[0] == f)) for f in fams], "h": c[:3], "p": ps, "i": img, "u": slug, "k": (a[6] if len(a) > 6 else "") or ""})
    out.sort(key=lambda x: (x["u"] is None, -max(x["p"])))
    json.dump(out, open(os.path.join(ROOT, "data/catalog.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    return out


L = {
 "ru": dict(title="Скины CS2 — справочник: ножи, перчатки и оружие по цвету, редкости и коллекциям — Skinset", desc="Справочник {n} скинов CS2: ножи, перчатки, винтовки, пистолеты. Редкость, коллекция, цвета, фазы Doppler, цены по качеству и с чем сочетать.",
   h1="Справочник скинов CS2", lead="{n} скинов: редкость, коллекция, цвета и фазы. Выбери скин, чтобы узнать о нём больше и собрать с ним сет.",
   search="Поиск: AK-47 Redline, Karambit…", filters="Фильтры", reset="Сбросить", cat="Категория", all="Все", type="Тип", color="Цвет", price="Цена", wear="Качество", phase="Фаза", rar="Редкость",
   coll="Коллекция", s_r="По редкости", mkt="Цена на рынке", mkth="Цены на рынке по качеству",
   sort="Сортировка", s_pop="Сначала популярные", s_pa="Сначала дешёвые", s_pd="Сначала дорогие", s_n="По названию", found="Найдено: {n}", more="Показать ещё", none="Ничего не найдено — попробуй убрать часть фильтров.",
   from_="от", min="от", max="до", buy="Купить", build="Собрать сет со скином", details="Подробнее о скине", show="Показать {n}", close="Закрыть", allpages="Все страницы скинов",
   crumbs=("Главная", "Скины CS2"),
   cats=dict(knife="Ножи", gloves="Перчатки", rifle="Винтовки", sniper="Снайперские", pistol="Пистолеты", smg="Пистолеты-пулемёты", heavy="Тяжёлое"),
   fams=["Красный", "Оранжевый", "Золотой", "Зелёный", "Бирюзовый", "Синий", "Фиолетовый", "Розовый", "Белый", "Серый", "Чёрный", "Коричневый"],
   rars=["Ширпотреб", "Промышленное", "Армейское", "Запрещённое", "Засекреченное", "Тайное", "★ Экстраординарное", "Контрабанда"],
   wears=["Прямо с завода", "Немного поношенное", "После полевых", "Поношенное", "Закалённое в боях"]),
 "en": dict(title="CS2 skins wiki: knives, gloves and guns by color, rarity and collection — Skinset", desc="Guide to {n} CS2 skins: knives, gloves, rifles, pistols. Rarity, collection, colors, Doppler phases, prices by wear and what to pair them with.",
   h1="CS2 skins wiki", lead="{n} skins: rarity, collection, colors and phases. Pick a skin to learn more about it and build a set around it.",
   search="Search: AK-47 Redline, Karambit…", filters="Filters", reset="Reset", cat="Category", all="All", type="Type", color="Color", price="Price", wear="Wear", phase="Phase", rar="Rarity",
   coll="Collection", s_r="By rarity", mkt="Market price", mkth="Market prices by wear",
   sort="Sort", s_pop="Popular first", s_pa="Price: low to high", s_pd="Price: high to low", s_n="Name", found="Found: {n}", more="Show more", none="Nothing found — try removing some filters.",
   from_="from", min="min", max="max", buy="Buy", build="Build a set with this skin", details="Skin details", show="Show {n}", close="Close", allpages="All skin pages",
   crumbs=("Home", "CS2 skins"),
   cats=dict(knife="Knives", gloves="Gloves", rifle="Rifles", sniper="Sniper rifles", pistol="Pistols", smg="SMGs", heavy="Heavy"),
   fams=["Red", "Orange", "Gold", "Green", "Teal", "Blue", "Purple", "Pink", "White", "Gray", "Black", "Brown"],
   rars=["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "★ Extraordinary", "Contraband"],
   wears=["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]),
 "de": dict(title="CS2-Skins Wiki: Messer, Handschuhe und Waffen nach Farbe, Seltenheit und Kollektion — Skinset", desc="Guide zu {n} CS2-Skins: Messer, Handschuhe, Gewehre, Pistolen. Seltenheit, Kollektion, Farben, Doppler-Phasen, Preise nach Zustand.",
   h1="CS2-Skins Wiki", lead="{n} Skins: Seltenheit, Kollektion, Farben und Phasen. Wähle einen Skin, um mehr zu erfahren und ein Set damit zu bauen.",
   search="Suche: AK-47 Redline, Karambit…", filters="Filter", reset="Zurücksetzen", cat="Kategorie", all="Alle", type="Typ", color="Farbe", price="Preis", wear="Zustand", phase="Phase", rar="Seltenheit",
   coll="Kollektion", s_r="Nach Seltenheit", mkt="Marktpreis", mkth="Marktpreise nach Zustand",
   sort="Sortierung", s_pop="Beliebt zuerst", s_pa="Preis aufsteigend", s_pd="Preis absteigend", s_n="Name", found="Gefunden: {n}", more="Mehr anzeigen", none="Nichts gefunden — entferne einige Filter.",
   from_="ab", min="von", max="bis", buy="Kaufen", build="Set mit diesem Skin bauen", details="Details zum Skin", show="{n} anzeigen", close="Schließen", allpages="Alle Skin-Seiten",
   crumbs=("Start", "CS2-Skins"),
   cats=dict(knife="Messer", gloves="Handschuhe", rifle="Gewehre", sniper="Scharfschützen", pistol="Pistolen", smg="MPs", heavy="Schwere Waffen"),
   fams=["Rot", "Orange", "Gold", "Grün", "Türkis", "Blau", "Lila", "Pink", "Weiß", "Grau", "Schwarz", "Braun"],
   rars=["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "★ Extraordinary", "Contraband"],
   wears=["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]),
 "pt": dict(title="Wiki de skins de CS2: facas, luvas e armas por cor, raridade e coleção — Skinset", desc="Guia de {n} skins de CS2: facas, luvas, rifles, pistolas. Raridade, coleção, cores, fases Doppler, preços por desgaste e combinações.",
   h1="Wiki de skins de CS2", lead="{n} skins: raridade, coleção, cores e fases. Escolha uma skin para saber mais e montar um set com ela.",
   search="Buscar: AK-47 Redline, Karambit…", filters="Filtros", reset="Limpar", cat="Categoria", all="Todas", type="Tipo", color="Cor", price="Preço", wear="Desgaste", phase="Fase", rar="Raridade",
   coll="Coleção", s_r="Por raridade", mkt="Preço de mercado", mkth="Preços de mercado por desgaste",
   sort="Ordenar", s_pop="Populares primeiro", s_pa="Menor preço", s_pd="Maior preço", s_n="Nome", found="Encontradas: {n}", more="Mostrar mais", none="Nada encontrado — tente remover alguns filtros.",
   from_="a partir de", min="de", max="até", buy="Comprar", build="Montar set com esta skin", details="Detalhes da skin", show="Mostrar {n}", close="Fechar", allpages="Todas as páginas de skins",
   crumbs=("Início", "Skins de CS2"),
   cats=dict(knife="Facas", gloves="Luvas", rifle="Rifles", sniper="Snipers", pistol="Pistolas", smg="Submetralhadoras", heavy="Pesadas"),
   fams=["Vermelho", "Laranja", "Dourado", "Verde", "Turquesa", "Azul", "Roxo", "Rosa", "Branco", "Cinza", "Preto", "Marrom"],
   rars=["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "★ Extraordinary", "Contraband"],
   wears=["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]),
 "tr": dict(title="CS2 skin rehberi: renge, nadirliğe ve koleksiyona göre bıçak, eldiven ve silahlar — Skinset", desc="{n} CS2 skin rehberi: bıçaklar, eldivenler, tüfekler, tabancalar. Nadirlik, koleksiyon, renkler, Doppler fazları, aşınmaya göre fiyatlar.",
   h1="CS2 skin rehberi", lead="{n} skin: nadirlik, koleksiyon, renkler ve fazlar. Daha fazlasını öğrenmek ve set kurmak için bir skin seç.",
   search="Ara: AK-47 Redline, Karambit…", filters="Filtreler", reset="Sıfırla", cat="Kategori", all="Tümü", type="Tür", color="Renk", price="Fiyat", wear="Aşınma", phase="Faz", rar="Nadirlik",
   coll="Koleksiyon", s_r="Nadirliğe göre", mkt="Piyasa fiyatı", mkth="Aşınmaya göre piyasa fiyatları",
   sort="Sırala", s_pop="Önce popüler", s_pa="Önce ucuz", s_pd="Önce pahalı", s_n="İsim", found="Bulunan: {n}", more="Daha fazla göster", none="Hiçbir şey bulunamadı — bazı filtreleri kaldır.",
   from_="", min="en az", max="en çok", buy="Satın al", build="Bu skinle set kur", details="Skin detayları", show="{n} göster", close="Kapat", allpages="Tüm skin sayfaları",
   crumbs=("Ana sayfa", "CS2 skinleri"),
   cats=dict(knife="Bıçaklar", gloves="Eldivenler", rifle="Tüfekler", sniper="Keskin nişancı", pistol="Tabancalar", smg="Hafif makineli", heavy="Ağır silahlar"),
   fams=["Kırmızı", "Turuncu", "Altın", "Yeşil", "Turkuaz", "Mavi", "Mor", "Pembe", "Beyaz", "Gri", "Siyah", "Kahverengi"],
   rars=["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "★ Extraordinary", "Contraband"],
   wears=["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]),
 "pl": dict(title="Wiki skinów CS2: noże, rękawice i bronie według koloru, rzadkości i kolekcji — Skinset", desc="Przewodnik po {n} skinach CS2: noże, rękawice, karabiny, pistolety. Rzadkość, kolekcja, kolory, fazy Doppler, ceny według stanu.",
   h1="Wiki skinów CS2", lead="{n} skinów: rzadkość, kolekcja, kolory i fazy. Wybierz skin, aby dowiedzieć się więcej i złożyć z nim zestaw.",
   search="Szukaj: AK-47 Redline, Karambit…", filters="Filtry", reset="Wyczyść", cat="Kategoria", all="Wszystkie", type="Typ", color="Kolor", price="Cena", wear="Stan", phase="Faza", rar="Rzadkość",
   coll="Kolekcja", s_r="Według rzadkości", mkt="Cena rynkowa", mkth="Ceny rynkowe według stanu",
   sort="Sortuj", s_pop="Najpierw popularne", s_pa="Od najtańszych", s_pd="Od najdroższych", s_n="Nazwa", found="Znaleziono: {n}", more="Pokaż więcej", none="Nic nie znaleziono — usuń część filtrów.",
   from_="od", min="od", max="do", buy="Kup", build="Złóż zestaw z tym skinem", details="Szczegóły skina", show="Pokaż {n}", close="Zamknij", allpages="Wszystkie strony skinów",
   crumbs=("Start", "Skiny CS2"),
   cats=dict(knife="Noże", gloves="Rękawice", rifle="Karabiny", sniper="Snajperki", pistol="Pistolety", smg="PM-y", heavy="Ciężkie"),
   fams=["Czerwony", "Pomarańczowy", "Złoty", "Zielony", "Turkusowy", "Niebieski", "Fioletowy", "Różowy", "Biały", "Szary", "Czarny", "Brązowy"],
   rars=["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "★ Extraordinary", "Contraband"],
   wears=["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]),
}
RCOL = ["#b0c3d9", "#5e98d9", "#4b69ff", "#8847ff", "#d32ce6", "#eb4b4b", "#e4ae39", "#e4ae39"]

CSS = r"""
.cat{max-width:1440px;margin:0 auto;padding:22px 24px 60px}
.cat .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:10px}.cat .crumbs a{color:var(--soft)}
.cat h1{font-size:clamp(1.8rem,3.4vw,2.6rem);margin:0 0 6px;text-transform:uppercase}
.cat .lead{color:var(--soft);margin:0 0 18px;font-size:1rem}
.cbar{display:flex;gap:10px;align-items:center;margin-bottom:16px;flex-wrap:wrap}
.cbar .q{flex:1 1 320px;position:relative}
.cbar .q input{width:100%;height:44px;padding:0 14px 0 40px;background:rgba(14,15,17,.85);border:1px solid var(--line2);color:var(--ink);font:400 1rem var(--body);outline:none}
.cbar .q input:focus{border-color:var(--pick)}
.cbar .q svg{position:absolute;left:12px;top:12px;width:20px;height:20px;color:var(--dim)}
.cbar select{height:44px;padding:0 12px;background:rgba(14,15,17,.85);border:1px solid var(--line2);color:var(--ink);font:500 .92rem var(--body)}
.cbar .fbtn{display:none;height:44px;padding:0 16px;background:var(--pick);border:0;color:#fff;font:600 .9rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;cursor:pointer}
.cbar .cnt{color:var(--soft);font-size:.9rem;margin-left:auto}
.cats{display:flex;gap:6px;overflow-x:auto;margin-bottom:16px;padding-bottom:4px;scrollbar-width:thin}
.cats button{flex:none;height:40px;padding:0 16px;background:rgba(14,15,17,.75);border:1px solid var(--line);color:var(--soft);font:600 .85rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;cursor:pointer;white-space:nowrap}
.cats button:hover{color:var(--ink);border-color:var(--line2)}
.cats button.on{background:var(--pick);border-color:var(--pick);color:#fff}
.cats button small{opacity:.6;font-weight:500;margin-left:4px}
.shade{display:none}
.lay{display:grid;grid-template-columns:270px 1fr;gap:20px;align-items:start}
.side{position:sticky;top:76px;max-height:calc(100vh - 90px);overflow:auto;background:rgba(14,15,17,.78);border:1px solid var(--line);scrollbar-width:thin}
.side .sh{display:none}
.fg{border-bottom:1px solid var(--line);padding:12px 14px}
.fg:last-child{border-bottom:0}
.fg>b{display:flex;justify-content:space-between;align-items:center;font:600 .78rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--soft);margin-bottom:10px;cursor:pointer;user-select:none}
.fg>b i{font-style:normal;color:var(--pick);font-size:.75rem;letter-spacing:0}
.fg.shut>b{margin-bottom:0}.fg.shut .fb{display:none}
.ck{display:flex;align-items:center;gap:9px;padding:5px 2px;cursor:pointer;font-size:.92rem;color:var(--ink)}
.ck input{appearance:none;width:16px;height:16px;border:1px solid var(--line2);background:transparent;flex:none;display:grid;place-items:center;cursor:pointer;margin:0}
.ck input:checked{background:var(--pick);border-color:var(--pick)}
.ck input:checked::after{content:"";width:8px;height:4px;border-left:2px solid #fff;border-bottom:2px solid #fff;transform:rotate(-45deg) translate(1px,-1px)}
.ck span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ck small{color:var(--dim);font-size:.78rem}
.ck.zero{opacity:.38}
.ck .dot{width:10px;height:10px;border-radius:50%;flex:none}
.tlist{max-height:260px;overflow:auto;scrollbar-width:thin}
.tsearch{width:100%;height:32px;margin-bottom:8px;padding:0 10px;background:rgba(255,255,255,.04);border:1px solid var(--line);color:var(--ink);font:400 .88rem var(--body);outline:none}
.sws2{display:grid;grid-template-columns:repeat(6,1fr);gap:7px}
.sws2 button{aspect-ratio:1;border:1px solid rgba(255,255,255,.25);cursor:pointer;position:relative;padding:0}
.sws2 button.on{outline:2px solid #fff;outline-offset:2px}
.sws2 button.on::after{content:"";position:absolute;left:50%;top:50%;width:8px;height:4px;border-left:2px solid #fff;border-bottom:2px solid #fff;transform:translate(-50%,-70%) rotate(-45deg);filter:drop-shadow(0 0 2px #000)}
.pr{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.pr input{width:100%;height:36px;padding:0 10px;background:rgba(255,255,255,.04);border:1px solid var(--line);color:var(--ink);font:400 .92rem var(--body);outline:none}
.pr input:focus{border-color:var(--pick)}
.pq{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.pq button,.chips button{height:28px;padding:0 9px;background:rgba(255,255,255,.04);border:1px solid var(--line);color:var(--soft);font:500 .78rem var(--body);cursor:pointer}
.pq button:hover,.chips button:hover{color:var(--ink);border-color:var(--line2)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.chips button{display:inline-flex;align-items:center;gap:6px;height:30px;color:var(--ink);border-color:var(--line2)}
.chips button::after{content:"×";color:var(--pick);font-size:1rem}
.chips .clr{border-color:transparent;color:var(--pick)}.chips .clr::after{content:""}
.grid2{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.ci{position:relative;display:flex;flex-direction:column;text-decoration:none;color:inherit;background:linear-gradient(170deg,rgba(255,255,255,.05),rgba(255,255,255,.01));border:1px solid var(--line);border-top:2px solid var(--rc);padding:10px 12px 12px;cursor:pointer;transition:transform .15s,border-color .15s,background .15s;min-width:0}
.ci:hover{transform:translateY(-3px);border-color:var(--line2);background:linear-gradient(170deg,rgba(255,255,255,.09),rgba(255,255,255,.02))}
.ci .im{position:relative;overflow:hidden;height:120px;display:grid;place-items:center;margin-bottom:8px}
.ci .im::before{content:"";position:absolute;inset:10% 15%;background:radial-gradient(closest-side,var(--rc),transparent);opacity:.18}
.ci img{position:relative;max-width:100%;max-height:120px;object-fit:contain;filter:drop-shadow(0 8px 10px rgba(0,0,0,.55))}
.ci .wn{font-size:.8rem;color:var(--soft);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:6px}
.ci .mt{margin-top:auto;font-size:.74rem;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ci .mt b{font-weight:600}
.mdb .mh{font:600 .72rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin:6px 0 4px}
.ci .sn{font:600 1.02rem/1.2 var(--body);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:2px 0 1px}
.ci .ph{position:absolute;top:8px;left:8px;padding:3px 6px;background:rgba(0,0,0,.55);border:1px solid var(--line2);font:600 .66rem/1 var(--hud);letter-spacing:.06em;text-transform:uppercase}
.ci .cs{position:absolute;top:9px;right:9px;display:flex;gap:3px}.ci .cs i{width:9px;height:9px;border:1px solid rgba(255,255,255,.3)}
.ci .pp{margin-top:auto;display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.ci .pp b{font:600 1.1rem/1 var(--hud);letter-spacing:.02em;white-space:nowrap}
.ci .pp small{color:var(--dim);font-size:.72rem;white-space:nowrap}
.ci .wr{display:flex;gap:3px;margin-top:7px}
.ci .wr span{flex:1;text-align:center;font:600 .62rem/1 var(--hud);padding:3px 0;background:rgba(255,255,255,.05);color:var(--dim)}
.ci .wr span.y{color:var(--ink);background:rgba(255,255,255,.1)}
.moreb{display:block;margin:20px auto 0;height:46px;padding:0 28px;background:transparent;border:1px solid var(--line2);color:var(--ink);font:600 .9rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
.moreb:hover{border-color:var(--pick);color:var(--pick)}
.empty{padding:40px;text-align:center;color:var(--soft);border:1px dashed var(--line2)}
.md{position:fixed;inset:0;z-index:100;display:none;place-items:center;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);padding:16px}
.md.open{display:grid}
.mdb{position:relative;width:min(760px,100%);max-height:calc(100vh - 32px);overflow:auto;background:#121317;border:1px solid var(--line2);border-bottom:3px solid var(--rc,var(--pick));display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:22px}
.mdb .x{position:absolute;top:8px;right:10px;width:36px;height:36px;background:none;border:0;color:var(--soft);font-size:1.6rem;cursor:pointer}
.mdb img{width:100%;aspect-ratio:4/3;object-fit:contain;filter:drop-shadow(0 12px 16px rgba(0,0,0,.6))}
.mdb h3{margin:0 0 2px;font:600 1.5rem/1.1 var(--hud);text-transform:uppercase}
.mdb .mw{color:var(--soft);font-size:.88rem;margin-bottom:12px}
.mdb table{width:100%;border-collapse:collapse;font-size:.9rem}.mdb td{padding:8px 4px;border-bottom:1px solid var(--line)}.mdb td:nth-child(2){font:600 1rem var(--hud);text-align:right;white-space:nowrap}.mdb td:last-child{text-align:right;width:1%}
.mdb .bb{display:inline-block;padding:6px 10px;border:1px solid var(--line2);font:600 .68rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-decoration:none;color:var(--ink)}.mdb .bb:hover{border-color:var(--pick);color:var(--pick)}
.mdb .act{display:flex;flex-direction:column;gap:8px;margin-top:14px}
.mdb .act a{display:flex;justify-content:center;align-items:center;height:44px;font:600 .85rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;text-decoration:none}
.mdb .act .p{background:var(--pick);color:#fff}.mdb .act .s{border:1px solid var(--line2);color:var(--ink)}
.allp{margin-top:40px;color:var(--soft)}.allp summary{cursor:pointer;font:600 .85rem var(--hud);letter-spacing:.1em;text-transform:uppercase;padding:10px 0}
.allp ul{columns:4 220px;list-style:none;padding:0;margin:0;font-size:.85rem}.allp li{padding:2px 0;break-inside:avoid}.allp a{color:var(--soft)}
@media(max-width:980px){
 .lay{grid-template-columns:1fr}
 .cbar .fbtn{display:block}
 .side{position:fixed;inset:0 auto 0 0;top:0;width:min(340px,88vw);max-height:none;height:100%;z-index:90;transform:translateX(-102%);transition:transform .25s;background:#121317;border:0;border-right:1px solid var(--line2)}
 .side.open{transform:none;box-shadow:20px 0 60px rgba(0,0,0,.6)}
 .side .sh{display:flex;position:sticky;top:0;z-index:2;justify-content:space-between;align-items:center;padding:12px 14px;background:#121317;border-bottom:1px solid var(--line)}
 .side .sh b{font:600 1rem var(--hud);letter-spacing:.1em;text-transform:uppercase}
 .side .sh button{height:36px;padding:0 14px;background:var(--pick);border:0;color:#fff;font:600 .8rem var(--hud);letter-spacing:.08em;text-transform:uppercase}
 .shade{position:fixed;inset:0;z-index:89;background:rgba(0,0,0,.55);display:none}.shade.open{display:block}
 .mdb{grid-template-columns:1fr}
}
@media(max-width:560px){.cat{padding:14px 12px 40px}.grid2{grid-template-columns:repeat(2,1fr);gap:8px}.ci{padding:8px 9px 10px}.ci .im{height:90px}.ci img{max-height:90px}.ci .sn{font-size:.9rem}.ci .pp b{font-size:1rem}.cbar .q{order:-1;flex-basis:100%}.cbar .fbtn,.cbar select{flex:1 1 0;min-width:0}.cbar .cnt{width:100%;margin:0}}
"""

JS = r"""
(()=>{const L=window.CL,LANG=document.documentElement.lang,RATE=+document.body.dataset.rate,HOME=document.body.dataset.home,CP0=document.body.dataset.cp;
const IMG="https://community.akamai.steamstatic.com/economy/image/",W=["FN","MW","FT","WW","BS"],REF="L4QnfHPvxc";
const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const nf=new Intl.NumberFormat(LANG,{maximumFractionDigits:RATE>=50?2:0});
const money=usd=>{const v=usd*90/RATE;const s=nf.format(v>=100?Math.round(v):v);return L.cur[0]+s+L.cur[1]};
let D=[],S={q:"",c:"",t:[],f:[],w:[],ph:[],r:[],k:[],pmin:"",pmax:"",sort:"pop"},shown=60;
const qs=new URLSearchParams(location.search);
for(const k of ["q","c","sort","pmin","pmax"])if(qs.get(k))S[k]=qs.get(k);
for(const k of ["t","f","w","ph","r","k"])if(qs.get(k))S[k]=qs.get(k).split(",").filter(Boolean);
const price=x=>{const ws=S.w.length?S.w.map(w=>W.indexOf(w)):[0,1,2,3,4];let m=Infinity;for(const i of ws)if(x.p[i]&&x.p[i]<m)m=x.p[i];return m};
const local=usd=>usd*90/RATE;
function match(x,skip){
 if(skip!=="c"&&S.c&&x.c!==S.c)return false;
 if(skip!=="t"&&S.t.length&&!S.t.includes(x.w))return false;
 if(skip!=="f"&&S.f.length&&!S.f.some(f=>x.f.includes(+f)))return false;
 if(skip!=="w"&&S.w.length&&!S.w.some(w=>x.p[W.indexOf(w)]))return false;
 if(skip!=="ph"&&S.ph.length&&!S.ph.includes(x.ph))return false;
 if(skip!=="r"&&S.r.length&&!S.r.includes(String(x.r)))return false;
 if(skip!=="k"&&S.k.length&&!S.k.includes(x.k))return false;
 if(skip!=="p"&&(S.pmin||S.pmax)){const p=price(x);if(!isFinite(p))return false;const v=local(p);if(S.pmin&&v<+S.pmin)return false;if(S.pmax&&v>+S.pmax)return false}
 if(S.q){const q=S.q.toLowerCase().replace(/\s*\|\s*/g," ");if(!(x.n.toLowerCase().replace(" | "," ")).includes(q))return false}
 return true}
function count(key,fn){const m=new Map();for(const x of D)if(match(x,key))for(const v of fn(x))m.set(v,(m.get(v)||0)+1);return m}
function ck(group,val,label,n,extra=""){const on=S[group].includes(String(val));return `<label class="ck${n?"":" zero"}"><input type="checkbox" data-g="${group}" value="${esc(val)}"${on?" checked":""}>${extra}<span>${esc(label)}</span><small>${n||0}</small></label>`}
function drawSide(){
 // категории сверху
 const cc=count("c",x=>[x.c]);const tot=D.filter(x=>match(x,"c")).length;
 $("#cats").innerHTML=`<button data-c=""${S.c?"":' class="on"'}>${esc(L.all)}<small>${tot}</small></button>`+L.catk.map(k=>`<button data-c="${k}"${S.c===k?' class="on"':""}>${esc(L.cats[k])}<small>${cc.get(k)||0}</small></button>`).join("");
 // тип оружия / модели ножа
 const tc=count("t",x=>[x.w]);const types=[...new Set(D.filter(x=>!S.c||x.c===S.c).map(x=>x.w))].sort((a,b)=>(tc.get(b)||0)-(tc.get(a)||0)||a.localeCompare(b));
 const tf=($("#tq")||{}).value||"";
 $("#fT").innerHTML=`<input class="tsearch" id="tq" placeholder="${esc(L.search.split(":")[0])}…" value="${esc(tf)}"><div class="tlist">${types.filter(t=>!tf||t.toLowerCase().includes(tf.toLowerCase())).map(t=>ck("t",t,t,tc.get(t))).join("")}</div>`;
 const tq=$("#tq");tq.oninput=()=>{const p=tq.selectionStart;drawSide();const n=$("#tq");n.focus();n.setSelectionRange(p,p)};
 // цвет
 const fc=count("f",x=>x.f);$("#fF").innerHTML=`<div class="sws2">${L.fam.map((f,i)=>`<button type="button" data-f="${i}" title="${esc(L.fams[i])} (${fc.get(i)||0})" aria-label="${esc(L.fams[i])}" style="background:${f}"${S.f.includes(String(i))?' class="on"':""}></button>`).join("")}</div>`;
 // качество
 const wc=count("w",x=>W.filter((w,i)=>x.p[i]));$("#fW").innerHTML=W.map((w,i)=>ck("w",w,L.wears[i],wc.get(w),`<small style="width:24px;color:var(--soft)">${w}</small>`)).join("");
 // фаза
 const pc=count("ph",x=>x.ph?[x.ph]:[]);const phs=L.phases.filter(p=>pc.get(p)||S.ph.includes(p));$("#gPh").hidden=!phs.length;$("#fPh").innerHTML=phs.map(p=>ck("ph",p,p,pc.get(p))).join("");
 // редкость
 const rc=count("r",x=>[String(x.r)]);$("#fR").innerHTML=L.rars.map((r,i)=>rc.get(String(i))||S.r.includes(String(i))?ck("r",i,r,rc.get(String(i)),`<i class="dot" style="background:${L.rcol[i]}"></i>`):"").join("");
 // коллекция
 const kc=count("k",x=>x.k?[x.k]:[]);const kf=($("#kq")||{}).value||"";const ks=[...kc.keys()].concat(S.k.filter(v=>!kc.has(v))).sort((a,b)=>(kc.get(b)||0)-(kc.get(a)||0)||a.localeCompare(b));
 $("#fK").innerHTML=`<input class="tsearch" id="kq" placeholder="${esc(L.search.split(":")[0])}…" value="${esc(kf)}"><div class="tlist">${ks.filter(k=>!kf||k.toLowerCase().includes(kf.toLowerCase())).map(k=>ck("k",k,k,kc.get(k))).join("")}</div>`;
 const kq=$("#kq");kq.oninput=()=>{const p=kq.selectionStart;drawSide();const n=$("#kq");n.focus();n.setSelectionRange(p,p)};
 // цена
 $("#pmin").value=S.pmin;$("#pmax").value=S.pmax;
 // счётчики в заголовках групп
 const badge=(id,n)=>{const b=$(id);if(b)b.textContent=n?n:""};badge("#bT",S.t.length);badge("#bF",S.f.length);badge("#bW",S.w.length);badge("#bPh",S.ph.length);badge("#bR",S.r.length);badge("#bK",S.k.length);badge("#bP",(S.pmin||S.pmax)?"•":"");
}
function chips(){const c=[];
 if(S.c)c.push(["c",S.c,L.cats[S.c]]);for(const t of S.t)c.push(["t",t,t]);for(const f of S.f)c.push(["f",f,L.fams[f]]);for(const w of S.w)c.push(["w",w,w]);for(const p of S.ph)c.push(["ph",p,p]);for(const r of S.r)c.push(["r",r,L.rars[r]]);for(const k of S.k)c.push(["k",k,k]);
 if(S.pmin||S.pmax)c.push(["p","",(S.pmin?L.min+" "+S.pmin:"")+(S.pmax?" "+L.max+" "+S.pmax:"")]);if(S.q)c.push(["q","","“"+S.q+"”"]);
 $("#chips").innerHTML=c.map(([g,v,l])=>`<button data-x="${g}" data-v="${esc(v)}">${esc(l)}</button>`).join("")+(c.length>1?`<button class="clr" data-x="all">${esc(L.reset)}</button>`:"");
 const n=c.length;$("#fbtn").textContent=L.filters+(n?` (${n})`:"")}
function card(x){const im=x.i.startsWith("http")?x.i:IMG+x.i+"/256fx256f";
 const href=x.u?L.wiki+x.u+"/":"#";
 return `<a class="ci" href="${href}" data-n="${esc(x.n)}" style="--rc:${L.rcol[x.r]}"><div class="im"><img src="${esc(im)}" alt="${esc(x.n)}" loading="lazy" width="256" height="192"></div>${x.ph?`<span class="ph">${esc(x.ph)}</span>`:""}<span class="sn">${esc(x.s.replace(/\s*\(.*\)$/,""))}</span><span class="wn">${esc(x.w)}</span><span class="mt"><b style="color:${L.rcol[x.r]}">${esc(L.rars[x.r])}</b>${x.k?` · ${esc(x.k)}`:""}</span><span class="cs">${(x.h||[]).slice(0,3).map(h=>`<i style="background:${h}"></i>`).join("")}</span></a>`}
function list(){let a=D.filter(x=>match(x));
 if(S.sort==="pa")a.sort((x,y)=>price(x)-price(y));else if(S.sort==="pd")a.sort((x,y)=>price(y)-price(x));else if(S.sort==="n")a.sort((x,y)=>x.n.localeCompare(y.n));else if(S.sort==="r")a.sort((x,y)=>y.r-x.r||price(y)-price(x));
 return a}
let cur=[];
function render(keep){cur=list();if(!keep)shown=60;
 $("#cnt").textContent=L.found.replace("{n}",cur.length.toLocaleString(LANG));
 $("#grid").innerHTML=cur.length?cur.slice(0,shown).map(card).join(""):`<div class="empty" style="grid-column:1/-1">${esc(L.none)}</div>`;
 $("#more").hidden=cur.length<=shown;$("#shw").textContent=L.show.replace("{n}",cur.length.toLocaleString(LANG));
 drawSide();chips();sync()}
function sync(){const p=new URLSearchParams();for(const k of ["q","c","pmin","pmax"])if(S[k])p.set(k,S[k]);if(S.sort!=="pop")p.set("sort",S.sort);for(const k of ["t","f","w","ph","r","k"])if(S[k].length)p.set(k,S[k].join(","));
 const u=location.pathname+(p.toString()?"?"+p:"");history.replaceState(null,"",u)}
function toggle(g,v){v=String(v);const a=S[g];const i=a.indexOf(v);i<0?a.push(v):a.splice(i,1);render()}
document.addEventListener("change",ev=>{const t=ev.target;if(t.dataset&&t.dataset.g){toggle(t.dataset.g,t.value)}});
document.addEventListener("click",ev=>{const t=ev.target;
 const cb=t.closest("#cats button");if(cb){S.c=cb.dataset.c;S.t=[];S.ph=[];render();return}
 const fb=t.closest("[data-f]");if(fb){toggle("f",fb.dataset.f);return}
 const x=t.closest("[data-x]");if(x){const g=x.dataset.x;if(g==="all"){S={q:"",c:"",t:[],f:[],w:[],ph:[],r:[],k:[],pmin:"",pmax:"",sort:S.sort};$("#q").value=""}else if(g==="c")S.c="",S.t=[];else if(g==="p")S.pmin=S.pmax="";else if(g==="q"){S.q="";$("#q").value=""}else S[g]=S[g].filter(v=>v!==x.dataset.v);render();return}
 const pq=t.closest("[data-pq]");if(pq){const [a,b]=pq.dataset.pq.split("-");S.pmin=a;S.pmax=b;render();return}
 const gh=t.closest(".fg>b");if(gh){gh.parentNode.classList.toggle("shut");return}
 if(t.closest("#fbtn")){$("#side").classList.add("open");$("#shade").classList.add("open");return}
 if(t.closest("#shw")||t.closest("#shade")){$("#side").classList.remove("open");$("#shade").classList.remove("open");return}
 if(t.closest("#reset")){S={q:"",c:"",t:[],f:[],w:[],ph:[],r:[],k:[],pmin:"",pmax:"",sort:S.sort};$("#q").value="";render();return}
 if(t.closest("#more")){shown+=60;render(true);return}
 const ci=t.closest(".ci");if(ci&&ci.getAttribute("href")==="#"){ev.preventDefault();modal(ci.dataset.n);return}
 if(t.closest(".md .x")||t.classList.contains("md")){$("#md").classList.remove("open");return}
});
let tm;$("#q").addEventListener("input",e=>{clearTimeout(tm);tm=setTimeout(()=>{S.q=e.target.value.trim();render()},180)});
$("#sort").addEventListener("change",e=>{S.sort=e.target.value;render()});
for(const id of ["pmin","pmax"])$("#"+id).addEventListener("change",e=>{S[id]=e.target.value;render()});
document.addEventListener("keydown",e=>{if(e.key==="Escape")$("#md").classList.remove("open")});
function modal(n){const x=D.find(y=>y.n===n);if(!x)return;const im=x.i.startsWith("http")?x.i:IMG+x.i+"/512fx384f";
 const base=n.replace(/\s*\(.*\)$/,"").replace(" | "," ");
 const rows=W.map((w,i)=>x.p[i]?`<tr><td>${esc(L.wears[i])}</td><td>${money(x.p[i])}</td><td><a class="bb" target="_blank" rel="nofollow sponsored noopener" href="https://dmarket.com/ingame-items/item-list/csgo-skins?title=${encodeURIComponent(base)}&ref=${REF}">DMarket</a></td></tr>`:"").join("");
 const set=encodeURIComponent((x.c==="knife"||x.c==="gloves"?"★ ":"")+x.w+"|"+x.s);
 $("#mdb").style.setProperty("--rc",L.rcol[x.r]);
 $("#mdb").innerHTML=`<button class="x" aria-label="${esc(L.close)}">×</button><div><img src="${esc(im)}" alt="${esc(n)}"></div><div><h3>${esc(x.s)}</h3><div class="mw">${esc(x.w)} · <span style="color:${L.rcol[x.r]}">${esc(L.rars[x.r])}</span></div><div class="mh">${esc(L.mkth)}</div><table>${rows}</table><div class="act"><a class="p" href="${HOME}${CP0}/?set=${set}">${esc(L.build)} →</a>${x.u?`<a class="s" href="${L.wiki}${x.u}/">${esc(L.details)}</a>`:""}</div></div>`;
 $("#md").classList.add("open")}
$("#q").value=S.q;$("#sort").value=S.sort;
fetch("/data/catalog.json").then(r=>r.json()).then(j=>{D=j;render(true)}).catch(()=>{});
})();
"""


def build(lang, data):
    from skins_wiki import head, header, FOOT, WIKI, LANGS, HREFLANG, RATE, money_parts, lp, LANG_JS, CSS_V, SITE, HOME
    from about import CP
    t = L[lang]; n = len(data)
    canon = SITE + WIKI[lang]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{WIKI[l]}">' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{WIKI["en"]}">'
    pre, suf = money_parts(lang)
    cl = dict(t, cur=[pre, suf], catk=CATS, fam=[f[1] for f in FAM], phases=PHASES, rcol=RCOL, wiki=WIKI[lang])
    cl.pop("title"); cl.pop("desc")
    # первые карточки — сразу в HTML (для поисковиков и быстрого первого экрана)
    def card(x):
        im = x["i"] if x["i"].startswith("http") else "https://community.akamai.steamstatic.com/economy/image/" + x["i"] + "/256fx256f"
        href = f'{WIKI[lang]}{x["u"]}/' if x["u"] else "#"
        sk = re.sub(r"\s*\(.*\)$", "", x["s"])
        return (f'<a class="ci" href="{href}" data-n="{e(x["n"])}" style="--rc:{RCOL[x["r"]]}"><div class="im"><img src="{e(im)}" alt="{e(x["n"])}" loading="lazy" width="256" height="192"></div>'
                + (f'<span class="ph">{e(x["ph"])}</span>' if x["ph"] else "") + f'<span class="sn">{e(sk)}</span><span class="wn">{e(x["w"])}</span>'
                f'<span class="mt"><b style="color:{RCOL[x["r"]]}">{e(t["rars"][x["r"]])}</b>' + (f' · {e(x["k"])}' if x["k"] else "") + '</span>'
                '<span class="cs">' + "".join(f'<i style="background:{h}"></i>' for h in (x.get("h") or [])[:3]) + '</span></a>')
    first = "".join(card(x) for x in data[:60])
    allp = "".join(f'<li><a href="{WIKI[lang]}{x["u"]}/">{e(x["n"])}</a></li>' for x in sorted((x for x in data if x["u"]), key=lambda x: x["n"]))
    search_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": t["h1"], "url": canon, "description": t["desc"].format(n=n)},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": t["crumbs"][0], "item": SITE + HOME[lang]},
              {"@type": "ListItem", "position": 2, "name": t["crumbs"][1], "item": canon}]}]
    rate = RATE[lang]
    quick = [500, 2000, 10000, 50000] if lang == "ru" else [round(v / rate) for v in (450, 1800, 9000, 45000)]
    qbtn = "".join(f'<button type="button" data-pq="{a}-{b}">{e(lp(lang, a * rate) if a else "0")}–{e(lp(lang, b * rate))}</button>' for a, b in zip([0] + quick[:-1], quick)) + f'<button type="button" data-pq="{quick[-1]}-">{e(lp(lang, quick[-1] * rate))}+</button>'
    g = lambda gid, title, body, bid, shut=False, hid=False: f'<div class="fg{" shut" if shut else ""}" id="{gid}"{" hidden" if hid else ""}><b>{e(title)} <i id="{bid}"></i></b><div class="fb">{body}</div></div>'
    side = (f'<div class="sh"><b>{e(t["filters"])}</b><button type="button" id="shw">{e(t["show"].format(n=n))}</button></div>'
            + g("gT", t["type"], '<div id="fT"></div>', "bT")
            + g("gF", t["color"], '<div id="fF"></div>', "bF")
            + g("gR", t["rar"], '<div id="fR"></div>', "bR")
            + g("gPh", t["phase"], '<div id="fPh"></div>', "bPh")
            + g("gK", t["coll"], '<div id="fK"></div>', "bK", shut=True)
            + g("gW", t["wear"], '<div id="fW"></div>', "bW", shut=True)
            + g("gP", t["mkt"] + f" ({(pre + suf).strip()})", f'<div class="pr"><input id="pmin" type="number" min="0" inputmode="numeric" placeholder="{e(t["min"])}"><input id="pmax" type="number" min="0" inputmode="numeric" placeholder="{e(t["max"])}"></div><div class="pq">{qbtn}</div>', "bP", shut=True)
            + f'<div class="fg"><button type="button" id="reset" class="moreb" style="margin:0;width:100%;height:38px">{e(t["reset"])}</button></div>')
    css_extra = f"<style>{CSS}</style>"
    h = head(lang, t["title"].format(n=n), t["desc"].format(n=n), canon, alts, ld).replace("</head>", css_extra + "</head>")
    return h + f"""
<body data-rate="{rate}" data-home="{HOME[lang]}" data-cp="{CP[lang][0]}">
{header(lang, WIKI)}
<main class="cat">
<nav class="crumbs"><a href="{HOME[lang]}">{e(t['crumbs'][0])}</a> › {e(t['crumbs'][1])}</nav>
<h1>{e(t['h1'])}</h1><p class="lead">{e(t['lead'].format(n=n))}</p>
<div class="cbar"><button type="button" class="fbtn" id="fbtn">{e(t['filters'])}</button><label class="q">{search_svg}<input id="q" type="search" placeholder="{e(t['search'])}" autocomplete="off"></label>
<select id="sort" aria-label="{e(t['sort'])}"><option value="pop">{e(t['s_pop'])}</option><option value="r">{e(t['s_r'])}</option><option value="n">{e(t['s_n'])}</option><option value="pd">{e(t['s_pd'])}</option><option value="pa">{e(t['s_pa'])}</option></select><span class="cnt" id="cnt">{e(t['found'].format(n=n))}</span></div>
<div class="cats" id="cats"></div>
<div class="shade" id="shade"></div><div class="lay"><aside class="side" id="side">{side}</aside>
<section style="padding:0"><div class="chips" id="chips"></div><div class="grid2" id="grid">{first}</div><button type="button" class="moreb" id="more">{e(t['more'])}</button></section></div>
<details class="allp"><summary>{e(t['allpages'])}</summary><ul>{allp}</ul></details>
</main>
<div class="md" id="md"><div class="mdb" id="mdb"></div></div>
<footer><p>{e(FOOT[lang])}</p></footer>
<script>window.CL={json.dumps(cl, ensure_ascii=False)};</script>
<script>{JS}</script>
{LANG_JS}
</body>
</html>
"""


def main():
    data = build_data()
    if "--data" in sys.argv:
        print(len(data), "items"); return
    from skins_wiki import WIKI
    for lang in L:
        out = os.path.join(ROOT, WIKI[lang].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        import navmore; open(out, "w", encoding="utf-8").write(navmore.fix(build(lang, data)))
    print(len(data), "items, catalog pages written")


if __name__ == "__main__":
    main()
