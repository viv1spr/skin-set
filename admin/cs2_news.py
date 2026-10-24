# -*- coding: utf-8 -*-
"""Страница «Обновления CS2»: официальные новости и патчноуты Valve из Steam News API.
Запуск: python3 admin/cs2_news.py           — скачать свежие новости (нужен интернет) и пересобрать страницы
        python3 admin/cs2_news.py --offline — пересобрать из data/cs2-news.json
Страницы: список на 6 языках + отдельная страница каждого обновления на RU и EN.
"""
import json, os, re, html, sys, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa

e = lambda s: html.escape(str(s), quote=True)
DATA = os.path.join(ROOT, "data/cs2-news.json")
API = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=730&count=60&feeds=steam_community_announcements&maxlength=0&format=json"
IDX = {"ru": "/obnovleniya-cs2/", "en": "/en/cs2-updates/", "de": "/de/cs2-updates/", "pt": "/pt/atualizacoes-cs2/", "tr": "/tr/cs2-guncellemeleri/", "pl": "/pl/aktualizacje-cs2/"}
DETAIL = {"ru": "ru", "en": "en", "de": "en", "pt": "en", "tr": "en", "pl": "en"}  # на каком языке открывать страницу обновления
MON = {"ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
       "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
       "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
       "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
       "tr": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
       "pl": ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]}
SEC_RU = {"MAPS": "Карты", "GAMEPLAY": "Геймплей", "MISC": "Разное", "ITEMS": "Предметы", "MAP SCRIPTING": "Скрипты карт", "AUDIO": "Звук", "SOUND": "Звук",
          "ANIMATION": "Анимации", "UI": "Интерфейс", "USER INTERFACE": "Интерфейс", "NETWORKING": "Сеть", "GRAPHICS": "Графика", "RENDERING": "Графика",
          "ANTI-CHEAT": "Античит", "CS2 WORKSHOP": "Мастерская", "WORKSHOP": "Мастерская", "PREMIER": "Premier", "COMPETITIVE": "Соревновательный",
          "WEAPONS": "Оружие", "INVENTORY": "Инвентарь", "STEAM DECK": "Steam Deck", "LINUX": "Linux", "MAC": "Mac", "DEMOS": "Демки",
          "SETTINGS": "Настройки", "INPUT": "Управление", "SPECTATING": "Наблюдение", "MOVEMENT": "Передвижение", "BOTS": "Боты", "CASUAL": "Обычный режим",
          "DEATHMATCH": "Бой насмерть", "WINGMAN": "Напарники", "ARMS RACE": "Гонка вооружений", "RETAKES": "Ретейки"}
T = {
 "ru": dict(tab="Обновления CS2", h1="Обновления CS2", title="Обновления CS2: последний патч и все патчноуты Valve — Skinset",
   desc="Все обновления Counter-Strike 2 от Valve: последний патч {D}, полные патчноуты, новые кейсы, коллекции и скины. Обновляется автоматически.",
   lead="Официальные обновления и новости Counter-Strike 2 из Steam — патчноуты, новые кейсы, коллекции, стикеры и операции. Страница обновляется автоматически, как только Valve публикует апдейт. Тексты патчноутов — на английском, как в оригинале; сверху каждого — краткая сводка на русском.",
   last="Последнее обновление", read="Читать полностью", src="Оригинал в Steam", skins="Скины и предметы", sections="Что изменилось", items="изм.",
   upd_t="Обновление CS2 от {D}: патчноут — Skinset", news_t="{T} — новость CS2 от {D} — Skinset", upd_h="Обновление CS2 от {D}", news_h="{T}",
   upd_desc="Патчноут обновления Counter-Strike 2 от {D}: {S}. Полный список изменений от Valve.", news_desc="Новость Counter-Strike 2 от {D}: {T}. Официальный анонс Valve.",
   back="← Все обновления CS2", prev="Предыдущее", next="Следующее", note="Источник: официальный блог Counter-Strike 2 в Steam. Тексты и изображения принадлежат Valve.",
   home="Главная", cta="Новые скины уже в конструкторе →", total="изменений", lang_note="Патчноут на английском — в оригинале от Valve."),
 "en": dict(tab="CS2 updates", h1="CS2 updates", title="CS2 updates: latest patch and all Valve patch notes — Skinset",
   desc="Every Counter-Strike 2 update from Valve: the latest patch {D}, full patch notes, new cases, collections and skins. Updated automatically.",
   lead="Official Counter-Strike 2 updates and news from Steam: patch notes, new cases, collections, stickers and operations. This page updates automatically as soon as Valve posts an update.",
   last="Latest update", read="Read full notes", src="Original on Steam", skins="Skins & items", sections="What changed", items="changes",
   upd_t="CS2 update {D}: patch notes — Skinset", news_t="{T} — CS2 news {D} — Skinset", upd_h="CS2 update — {D}", news_h="{T}",
   upd_desc="Counter-Strike 2 patch notes for {D}: {S}. The full list of changes from Valve.", news_desc="Counter-Strike 2 news from {D}: {T}. Official Valve announcement.",
   back="← All CS2 updates", prev="Previous", next="Next", note="Source: the official Counter-Strike 2 blog on Steam. Text and images belong to Valve.",
   home="Home", cta="New skins are already in the builder →", total="changes", lang_note=""),
 "de": dict(tab="CS2-Updates", h1="CS2-Updates", title="CS2-Updates: neuester Patch und alle Patchnotes von Valve — Skinset",
   desc="Alle Counter-Strike-2-Updates von Valve: neuester Patch {D}, Patchnotes, neue Cases, Kollektionen und Skins.",
   lead="Offizielle Counter-Strike-2-Updates und News aus Steam: Patchnotes, neue Cases, Kollektionen und Sticker. Die Seite aktualisiert sich automatisch. Patchnotes auf Englisch, wie im Original.",
   last="Neuestes Update", read="Ganze Patchnotes", src="Original auf Steam", skins="Skins & Items", sections="Was sich geändert hat", items="Änderungen", home="Start",
   note="Quelle: offizieller Counter-Strike-2-Blog auf Steam. Texte und Bilder gehören Valve."),
 "pt": dict(tab="Atualizações CS2", h1="Atualizações do CS2", title="Atualizações do CS2: último patch e todas as notas da Valve — Skinset",
   desc="Todas as atualizações do Counter-Strike 2: último patch {D}, notas completas, novas caixas, coleções e skins.",
   lead="Atualizações e notícias oficiais do Counter-Strike 2 na Steam: notas de patch, novas caixas, coleções e adesivos. A página atualiza automaticamente. Notas em inglês, como no original.",
   last="Última atualização", read="Ler notas completas", src="Original na Steam", skins="Skins e itens", sections="O que mudou", items="mudanças", home="Início",
   note="Fonte: blog oficial do Counter-Strike 2 na Steam. Textos e imagens pertencem à Valve."),
 "tr": dict(tab="CS2 güncellemeleri", h1="CS2 güncellemeleri", title="CS2 güncellemeleri: son yama ve tüm Valve yama notları — Skinset",
   desc="Valve'ın tüm Counter-Strike 2 güncellemeleri: son yama {D}, yama notları, yeni kasalar, koleksiyonlar ve skinler.",
   lead="Steam'den resmi Counter-Strike 2 güncellemeleri ve haberleri: yama notları, yeni kasalar, koleksiyonlar ve çıkartmalar. Sayfa otomatik güncellenir. Yama notları orijinal haliyle İngilizce.",
   last="Son güncelleme", read="Tüm notları oku", src="Steam'deki orijinal", skins="Skinler ve eşyalar", sections="Neler değişti", items="değişiklik", home="Ana sayfa",
   note="Kaynak: Steam'deki resmi Counter-Strike 2 blogu. Metin ve görseller Valve'a aittir."),
 "pl": dict(tab="Aktualizacje CS2", h1="Aktualizacje CS2", title="Aktualizacje CS2: najnowszy patch i wszystkie notatki Valve — Skinset",
   desc="Wszystkie aktualizacje Counter-Strike 2 od Valve: najnowszy patch {D}, notatki, nowe skrzynki, kolekcje i skiny.",
   lead="Oficjalne aktualizacje i newsy Counter-Strike 2 ze Steam: notatki z patchy, nowe skrzynki, kolekcje i naklejki. Strona aktualizuje się automatycznie. Notatki po angielsku, jak w oryginale.",
   last="Najnowsza aktualizacja", read="Czytaj całość", src="Oryginał na Steam", skins="Skiny i przedmioty", sections="Co się zmieniło", items="zmian", home="Start",
   note="Źródło: oficjalny blog Counter-Strike 2 na Steam. Teksty i obrazy należą do Valve."),
}
SKIN_RE = re.compile(r"\b(case|collection|sticker|capsule|armory|charm|souvenir|skins?|graffiti|agent|patch(?:es)? pack|music kit|operation|terminal)\b", re.I)

CSS = """
.nw{max-width:980px;margin:0 auto;padding:22px 24px 60px}
.nw .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:12px}.nw .crumbs a{color:var(--soft)}
.nw h1{margin:6px 0 10px;font:700 clamp(1.9rem,4vw,3rem)/1.05 var(--hud);text-transform:uppercase}
.nw .lead{color:var(--soft);font-size:1.02rem;margin:0 0 22px}
.nw-card{display:block;margin:0 0 12px;padding:16px 18px;background:linear-gradient(170deg,rgba(255,255,255,.06),rgba(255,255,255,.015));border:1px solid var(--line2,rgba(255,255,255,.14));border-left:3px solid #e8402a;color:var(--ink,#fff);text-decoration:none}
.nw-card:hover{border-color:rgba(255,255,255,.35)}.nw-card.first{border-left-color:#ffd36a;background:linear-gradient(170deg,rgba(228,174,57,.14),rgba(255,255,255,.02))}
.nw-card .top{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:.82rem;color:var(--dim)}
.nw-card h2{margin:6px 0 6px;font:700 1.25rem/1.15 var(--hud);text-transform:uppercase}
.nw-card p{margin:0;color:var(--soft);font-size:.92rem}
.tag{display:inline-block;padding:3px 7px;font:600 .68rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;background:rgba(255,255,255,.08);color:var(--soft)}
.tag.sk{background:rgba(228,174,57,.2);color:#ffd36a}.tag.new{background:#e8402a;color:#fff}
.sum{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0;padding:0;list-style:none}.sum li{padding:4px 8px;border:1px solid var(--line,rgba(255,255,255,.1));font-size:.8rem;color:var(--soft)}.sum b{color:var(--ink,#fff)}
.notes{margin-top:18px;padding:18px 20px;background:rgba(14,15,17,.75);border:1px solid var(--line2,rgba(255,255,255,.14));line-height:1.55;color:var(--soft);overflow-wrap:anywhere}
.notes h3{margin:18px 0 8px;font:700 1.05rem var(--hud);letter-spacing:.06em;color:var(--ink,#fff);text-transform:uppercase}.notes h3:first-child{margin-top:0}
.notes ul{margin:4px 0 10px;padding-left:20px}.notes li{margin:3px 0}.notes p{margin:6px 0}.notes a{color:#66c0f4}
.notes img{max-width:100%;height:auto;display:block;margin:12px 0}.notes .yt{display:block;margin:12px 0;color:#66c0f4}
.nw .pn{display:flex;justify-content:space-between;gap:10px;margin-top:20px;flex-wrap:wrap}.nw .pn a,.nw .back{color:#66c0f4;text-decoration:none}
.nw .note{margin-top:22px;font-size:.82rem;color:var(--dim)}
.nw .cta{display:inline-block;margin-top:18px;padding:13px 20px;background:linear-gradient(90deg,#e8402a,#ff6a3d);color:#fff;font:700 .88rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-decoration:none}
@media(max-width:600px){.nw{padding:16px 14px 40px}.notes{padding:14px}}
"""


def _utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).replace(tzinfo=None)


def fetch():
    req = urllib.request.Request(API, headers={"User-Agent": "skin-set.com news bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        items = json.load(r)["appnews"]["newsitems"]
    old = {x["gid"]: x for x in (json.load(open(DATA)) if os.path.exists(DATA) else [])}
    for x in items:
        old[x["gid"]] = {"gid": x["gid"], "t": x["title"], "d": x["date"], "u": x["url"], "c": x["contents"]}
    out = sorted(old.values(), key=lambda x: -x["d"])[:200]
    json.dump(out, open(DATA, "w"), ensure_ascii=False, indent=0)
    return out


def bb(src):
    """BBCode Steam → безопасный HTML"""
    s = e(src).replace("{STEAM_CLAN_IMAGE}", "https://clan.akamai.steamstatic.com/images")
    s = s.replace("\\[", "&#91;").replace("\\]", "&#93;")
    s = re.sub(r"\[img(?: src=&quot;([^&]*)&quot;)?\](.*?)\[/img\]", lambda m: f'<img src="{m.group(1) or m.group(2)}" alt="" loading="lazy">' if (m.group(1) or m.group(2)).startswith("http") else "", s, flags=re.S)
    s = re.sub(r"\[previewyoutube=([\w-]+)[^\]]*\]\[/previewyoutube\]", r'<a class="yt" href="https://www.youtube.com/watch?v=\1" target="_blank" rel="noopener nofollow">▶ YouTube</a>', s)
    s = re.sub(r"\[url=&quot;?(https?://[^\]&]*)&quot;?[^\]]*\](.*?)\[/url\]", r'<a href="\1" target="_blank" rel="noopener nofollow">\2</a>', s, flags=re.S)
    s = re.sub(r"\[url\](https?://[^\[]*)\[/url\]", r'<a href="\1" target="_blank" rel="noopener nofollow">\1</a>', s)
    for a, b_ in [("h1", "h3"), ("h2", "h3"), ("h3", "h3"), ("b", "b"), ("i", "i"), ("u", "u"), ("strike", "s"), ("p", "p"), ("list", "ul"), ("olist", "ol"), ("code", "code"), ("quote", "blockquote"), ("table", "table"), ("tr", "tr"), ("td", "td"), ("th", "th")]:
        s = re.sub(rf"\[{a}(?:[^\]]*)\]", f"<{b_}>", s); s = s.replace(f"[/{a}]", f"</{b_}>")
    s = s.replace("[*]", "<li>").replace("[/*]", "</li>").replace("[hr][/hr]", "<hr>").replace("[hr]", "<hr>")
    s = re.sub(r"\[/?[a-z]+[^\]]*\]", "", s)
    # заголовки разделов вида «[ MAPS ]»
    s = re.sub(r"<p>\s*&#91;\s*([^&<\]]{2,40}?)\s*(?:&#93;|\])\s*</p>", lambda m: f"<h3>{m.group(1).strip()}</h3>", s)
    s = s.replace("\n", "<br>")
    s = re.sub(r"<p>\s*</p>", "", s)
    return s


def sections(c):
    """[(НАЗВАНИЕ, кол-во пунктов верхнего уровня)]"""
    out = []
    parts = re.split(r"\[p\]\s*\\?\[\s*([A-Z0-9 &/\-]{2,40}?)\s*\\?\]\s*\[/p\]", c)
    for k in range(1, len(parts), 2):
        body = parts[k + 1]; depth = 0; n = 0
        for m in re.finditer(r"\[(/?)(list|\*)\]", body):
            if m.group(2) == "list": depth += -1 if m.group(1) else 1
            elif not m.group(1) and depth == 1: n += 1
        out.append((parts[k].strip(), n))
    return out


def plain(c, n=220):
    t = re.sub(r"\[[^\]]*\]", " ", c.replace("\\[", "[").replace("\\]", "]"))
    t = re.sub(r"\{STEAM_CLAN_IMAGE\}\S*", "", t); t = re.sub(r"\s+", " ", t).strip()
    return t[:n].rsplit(" ", 1)[0] + "…" if len(t) > n else t


def dstr(lang, ts):
    d = _utc(ts)
    return f"{d.day} {MON[lang][d.month - 1]} {d.year}" if lang not in ("en", "tr") else (f"{MON[lang][d.month - 1]} {d.day}, {d.year}" if lang == "en" else f"{d.day} {MON[lang][d.month - 1]} {d.year}")


def slugs(items):
    seen = {}; out = {}
    for x in sorted(items, key=lambda x: x["d"]):
        d = _utc(x["d"]).strftime("%Y-%m-%d")
        seen[d] = seen.get(d, 0) + 1
        out[x["gid"]] = d if seen[d] == 1 else f"{d}-{seen[d]}"
    return out


def is_patch(x):
    return x["t"].strip().lower() in ("counter-strike 2 update", "cs2 update", "release notes")


def secname(lang, n):
    return SEC_RU.get(n.upper(), n.title()) if lang == "ru" else n.title()


def summary(lang, x):
    t = T[lang]; sec = sections(x["c"])
    return sec, ("<ul class=\"sum\">" + "".join(f"<li>{e(secname(lang, a))} <b>{b}</b></li>" for a, b in sec if b) + "</ul>") if sec else ""


def page_shell(lang, url, title, desc, ld, body, alts):
    h = head(lang, title, desc, SITE + url, alts, ld).replace("</head>", f"<style>{CSS}</style></head>")
    p = h + f"\n<body>\n{header(lang, {l: (url if l == lang else IDX[l]) for l in IDX})}\n<main class=\"nw\">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n"
    from skins_wiki import WIKI
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


def detail_url(lang, sl):
    return f"{IDX[DETAIL[lang]]}{sl}/"


def build(items):
    sl = slugs(items); made = []
    items = sorted(items, key=lambda x: -x["d"])
    # отдельные страницы обновлений: RU и EN
    for lang in ("ru", "en"):
        t = T[lang]
        for k, x in enumerate(items):
            u = detail_url(lang, sl[x["gid"]]); D = dstr(lang, x["d"]); sec, sumh = summary(lang, x)
            patch = is_patch(x)
            S = ", ".join(f"{secname(lang, a).lower() if lang == 'ru' else a.title()} ({b})" for a, b in sec if b) or plain(x["c"], 120)
            title = (t["upd_t"] if patch else t["news_t"]).format(D=D, T=x["t"]); h1 = (t["upd_h"] if patch else t["news_h"]).format(D=D, T=x["t"])
            desc = (t["upd_desc"] if patch else t["news_desc"]).format(D=D, S=S, T=x["t"])[:300]
            sk = bool(SKIN_RE.search(x["c"] + " " + x["t"]))
            nav = ""
            if k + 1 < len(items): nav += f'<a href="{detail_url(lang, sl[items[k + 1]["gid"]])}">← {e(t["prev"])}: {e(dstr(lang, items[k + 1]["d"]))}</a>'
            if k > 0: nav += f'<a href="{detail_url(lang, sl[items[k - 1]["gid"]])}">{e(t["next"])}: {e(dstr(lang, items[k - 1]["d"]))} →</a>'
            ld = [{"@context": "https://schema.org", "@type": "NewsArticle", "headline": h1, "datePublished": _utc(x["d"]).isoformat() + "Z",
                   "author": {"@type": "Organization", "name": "Valve"}, "publisher": {"@type": "Organization", "name": "Skinset", "url": SITE}, "mainEntityOfPage": SITE + u, "inLanguage": "en", "isBasedOn": x["u"]},
                  {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": t["home"], "item": SITE + HOME[lang]}, {"@type": "ListItem", "position": 2, "name": t["h1"], "item": SITE + IDX[lang]}, {"@type": "ListItem", "position": 3, "name": h1, "item": SITE + u}]}]
            body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › <a href="{IDX[lang]}">{e(t["h1"])}</a> › {e(D)}</nav>'
                    f'<h1>{e(h1)}</h1><div class="top" style="display:flex;gap:8px;flex-wrap:wrap;color:var(--dim);font-size:.85rem"><span>{e(D)}</span>{"<span class=\"tag sk\">" + e(t["skins"]) + "</span>" if sk else ""}<a href="{e(x["u"])}" target="_blank" rel="noopener nofollow" style="color:#66c0f4">{e(t["src"])}</a></div>'
                    + (f'<h2 style="margin:18px 0 6px;font:700 1.1rem var(--hud);text-transform:uppercase">{e(t["sections"])}</h2>{sumh}' if sumh else "")
                    + (f'<p class="note">{e(t["lang_note"])}</p>' if t.get("lang_note") else "")
                    + f'<div class="notes" lang="en">{bb(x["c"])}</div>'
                    + (f'<a class="cta" href="{HOME[lang]}">{e(t["cta"])}</a>' if sk else "")
                    + f'<div class="pn">{nav}</div><p><a class="back" href="{IDX[lang]}">{e(t["back"])}</a></p><p class="note">{e(t["note"])}</p>')
            alts = f'<link rel="alternate" hreflang="ru" href="{SITE}{detail_url("ru", sl[x["gid"]])}"><link rel="alternate" hreflang="en" href="{SITE}{detail_url("en", sl[x["gid"]])}"><link rel="alternate" hreflang="x-default" href="{SITE}{detail_url("en", sl[x["gid"]])}">'
            out = os.path.join(ROOT, u.strip("/"), "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(page_shell(lang, u, title, desc, ld, body, alts)); made.append(u)
    # списки на 6 языках
    for lang in IDX:
        t = T[lang]; dl = DETAIL[lang]; tl = T[dl]
        cards = []
        for k, x in enumerate(items[:60]):
            D = dstr(lang, x["d"]); sec, sumh = summary(lang if lang == "ru" else "en", x); patch = is_patch(x)
            sk = bool(SKIN_RE.search(x["c"] + " " + x["t"]))
            hh = (tl["upd_h"] if patch else tl["news_h"]).format(D=dstr(dl, x["d"]), T=x["t"]) if lang in ("ru", "en") else (x["t"] if not patch else f"Counter-Strike 2 Update — {D}")
            tot = sum(b for _, b in sec)
            cards.append(f'<a class="nw-card{" first" if k == 0 else ""}" href="{detail_url(lang, sl[x["gid"]])}"><div class="top"><span>{e(D)}</span>'
                         + (f'<span class="tag new">{e(t["last"])}</span>' if k == 0 else "") + (f'<span class="tag sk">{e(t["skins"])}</span>' if sk else "")
                         + (f'<span class="tag">{tot} {e(t["items"])}</span>' if tot else "") + f'</div><h2>{e(hh)}</h2><p>{e(plain(x["c"]))}</p>{sumh}</a>')
        D0 = dstr(lang, items[0]["d"])
        url = IDX[lang]
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": t["h1"], "url": SITE + url, "description": t["desc"].format(D=D0)},
              {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + detail_url(lang, sl[x["gid"]])} for i, x in enumerate(items[:20])]}]
        body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav><h1>{e(t["h1"])}</h1><p class="lead">{e(t["lead"])}</p>'
                + "".join(cards) + f'<p class="note">{e(t["note"])}</p>')
        alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{IDX[l]}">' for l in IDX) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{IDX["en"]}">'
        out = os.path.join(ROOT, url.strip("/"), "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(page_shell(lang, url, t["title"], t["desc"].format(D=D0), ld, body, alts)); made.append(url)
    # sitemap
    sm = os.path.join(ROOT, "sitemap.xml"); xml = open(sm, encoding="utf-8").read()
    today = datetime.date.today().isoformat()
    add = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in made if f"<loc>{SITE}{p}</loc>" not in xml)
    for l in IDX: xml = re.sub(r"(<loc>" + re.escape(SITE + IDX[l]) + r"</loc><lastmod>)[^<]*", lambda m: m.group(1) + today, xml)
    open(sm, "w", encoding="utf-8").write(xml.replace("</urlset>", add + "</urlset>"))
    return len(made)


def main():
    if "--offline" in sys.argv: items = json.load(open(DATA))
    else:
        try: items = fetch()
        except Exception as ex:
            print("fetch failed:", ex)
            if not os.path.exists(DATA): return
            items = json.load(open(DATA))
    print(build(items), "pages")


if __name__ == "__main__":
    main()
