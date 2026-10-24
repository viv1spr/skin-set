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
          "DEATHMATCH": "Бой насмерть", "WINGMAN": "Напарники", "ARMS RACE": "Гонка вооружений", "RETAKES": "Ретейки", "CROSSHAIR": "Прицел", "ENGINE": "Движок", "SCRIPTING": "Скрипты", "CS SCRIPT": "Скрипты", "ARMORY": "Арсенал", "MAJOR": "Мейджор", "TOOLS": "Инструменты", "MUSIC KITS": "Наборы музыки", "OTHER": "Другое", "KNOWN ISSUES": "Известные проблемы", "MAP GUIDES": "Гайды по картам", "WORKSHOP MAPS": "Карты мастерской", "ANIMGRAPH 2": "AnimGraph 2"}
T = {
 "ru": dict(tab="Обновления CS2", h1="Обновления CS2", title="Обновления CS2: последний патч и все патчноуты Valve — Skinset",
   desc="Все обновления Counter-Strike 2 от Valve: последний патч {D}, полные патчноуты, новые кейсы, коллекции и скины. Обновляется автоматически.",
   lead="Все патчи и новости Counter-Strike 2 от Valve: что изменилось, новые кейсы, коллекции и стикеры. Страница обновляется сама, как только выходит апдейт.",
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
html,body{overflow-x:clip}
.nw{max-width:1180px;margin:0 auto;padding:22px 24px 60px}
.nw .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:14px}.nw .crumbs a{color:var(--soft)}
.nw-hero{position:relative;margin-bottom:22px}
.nw-kick{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(232,64,42,.14);border:1px solid rgba(232,64,42,.45);color:#ff8a70;font:600 .72rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase}
.nw-kick i{width:7px;height:7px;border-radius:50%;background:#ff4d2e;box-shadow:0 0 0 0 rgba(255,77,46,.6);animation:nwP 1.8s infinite}
@keyframes nwP{70%{box-shadow:0 0 0 8px rgba(255,77,46,0)}100%{box-shadow:0 0 0 0 rgba(255,77,46,0)}}
.nw h1{margin:12px 0 8px;font:700 clamp(2.1rem,5vw,3.6rem)/1 var(--hud);text-transform:uppercase;letter-spacing:.01em}
.nw .lead{color:var(--soft);font-size:1.02rem;max-width:720px;margin:0}
.nw-f{display:flex;gap:6px;flex-wrap:wrap;margin:22px 0 18px}
.nw-f button{padding:9px 14px;background:rgba(255,255,255,.04);border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--soft);font:600 .78rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
.nw-f button.on{background:#e8402a;border-color:#e8402a;color:#fff}.nw-f button:hover{color:var(--ink,#fff)}
.cov{position:relative;display:block;aspect-ratio:16/9;overflow:hidden;background:#101114}
.cov img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s}
.cov.gen{background:radial-gradient(120% 90% at 85% 0%,rgba(232,64,42,.55),transparent 55%),radial-gradient(90% 80% at 0% 100%,rgba(255,138,61,.18),transparent 60%),linear-gradient(160deg,#17181c,#0c0d10)}
.cov.gen::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(135deg,rgba(255,255,255,.035) 0 2px,transparent 2px 14px)}
.cov.gen .g{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:space-between;padding:7% 7%}
.cov.gen .g small{font:600 .7rem/1 var(--hud);letter-spacing:.22em;color:rgba(255,255,255,.55);text-transform:uppercase}
.cov.gen .g b{font:700 clamp(2.2rem,5vw,3.4rem)/.9 var(--hud);color:#fff;text-transform:uppercase}
.cov.gen .g b span{display:block;font-size:.42em;letter-spacing:.12em;color:#ff8a70;margin-top:6px}
.cov.gen .g em{font-style:normal;font:600 .78rem/1 var(--hud);letter-spacing:.12em;color:rgba(255,255,255,.75);text-transform:uppercase}
.cov.gen.news{background:radial-gradient(120% 90% at 85% 0%,rgba(228,174,57,.55),transparent 55%),linear-gradient(160deg,#1a1712,#0c0d10)}.cov.gen.news .g b span{color:#ffd36a}
.feat{display:grid;grid-template-columns:1.25fr 1fr;gap:0;margin-bottom:26px;background:linear-gradient(170deg,rgba(255,255,255,.07),rgba(255,255,255,.015));border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--ink,#fff);text-decoration:none}
.feat:hover .cov img{transform:scale(1.03)}
.feat .bd{padding:26px 28px;display:flex;flex-direction:column;gap:12px}
.feat h2{margin:0;font:700 clamp(1.5rem,2.6vw,2.1rem)/1.05 var(--hud);text-transform:uppercase}
.feat p{margin:0;color:var(--soft)}
.feat .go{margin-top:auto;align-self:flex-start;padding:12px 18px;background:#e8402a;color:#fff;font:700 .82rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase}
.nmeta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:.8rem;color:var(--dim)}
.nt{display:inline-block;padding:4px 7px;font:600 .66rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;background:rgba(255,255,255,.08);color:var(--soft)}
.nt.nts{background:rgba(228,174,57,.18);color:#ffd36a}.nt.ntn{background:#e8402a;color:#fff}.nt.ntp{background:rgba(102,192,244,.14);color:#8fd0ff}
.mon{margin:30px 0 12px;font:700 .95rem/1 var(--hud);letter-spacing:.18em;text-transform:uppercase;color:var(--dim);display:flex;align-items:center;gap:12px}
.mon::after{content:"";flex:1;height:1px;background:var(--line,rgba(255,255,255,.1))}
.gridn{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;align-items:start}
.cd{display:flex;flex-direction:column;background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1));color:var(--ink,#fff);text-decoration:none;transition:border-color .2s,transform .2s}
.cd:hover{border-color:rgba(255,255,255,.3);transform:translateY(-2px)}.cd:hover .cov img{transform:scale(1.04)}
.cd .bd{min-width:0;padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.cd h3{margin:0;font:700 1.08rem/1.15 var(--hud);text-transform:uppercase}
.cd p{margin:0;color:var(--soft);font-size:.88rem;line-height:1.45}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin:0;padding:0;list-style:none}.chips li{padding:3px 7px;border:1px solid var(--line,rgba(255,255,255,.12));font-size:.74rem;color:var(--soft)}.chips b{color:var(--ink,#fff);margin-left:3px}
.mon::before{display:none!important}
.cd.pc{flex-direction:row;min-height:0}
.cd.pc .dt{flex:none;width:92px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:radial-gradient(120% 100% at 100% 0%,rgba(232,64,42,.45),transparent 60%),#121317;border-right:1px solid var(--line,rgba(255,255,255,.1))}
.cd.pc .dt b{font:700 2.2rem/1 var(--hud)}.cd.pc .dt small{font:600 .68rem/1 var(--hud);letter-spacing:.12em;color:#ff8a70;text-transform:uppercase}
.cd.pc h3{font-size:1rem}
.gridn.pl{grid-template-columns:repeat(3,minmax(0,1fr))}
.nw .note{margin-top:28px;font-size:.8rem;color:var(--dim)}
/* страница обновления */
.art-h{position:relative;margin:0 0 22px;border:1px solid var(--line2,rgba(255,255,255,.14));overflow:hidden}
.art-h .cov{aspect-ratio:21/8}
.art-h.gen{background:radial-gradient(90% 140% at 100% 0%,rgba(232,64,42,.5),transparent 60%),repeating-linear-gradient(135deg,rgba(255,255,255,.03) 0 2px,transparent 2px 14px),linear-gradient(160deg,#17181c,#0c0d10)}
.art-h.gen .ov{position:relative;padding:34px 28px 26px;background:none}
.art-h .ov{position:absolute;inset:auto 0 0 0;padding:60px 28px 22px;background:linear-gradient(transparent,rgba(8,9,11,.92) 55%)}
.art-h h1{margin:8px 0 0;font-size:clamp(1.8rem,4.2vw,3rem);text-shadow:0 4px 20px rgba(0,0,0,.6)}
.art{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:22px;align-items:start}
.notes{padding:22px 26px;background:rgba(14,15,17,.78);border:1px solid var(--line2,rgba(255,255,255,.14));line-height:1.6;color:#d4d6db;overflow-wrap:anywhere;font-size:.98rem}
.notes h3{margin:24px 0 10px;padding-bottom:8px;border-bottom:1px solid var(--line,rgba(255,255,255,.1));font:700 1.05rem var(--hud);letter-spacing:.12em;color:#fff;text-transform:uppercase}.notes h3:first-child{margin-top:0}
.notes h3::before{content:"";display:inline-block;width:8px;height:8px;margin-right:10px;background:#e8402a;vertical-align:middle}
.notes ul{margin:4px 0 12px;padding-left:20px}.notes li{margin:4px 0}.notes li::marker{color:#e8402a}.notes li li::marker{color:var(--dim)}.notes p{margin:6px 0}.notes a{color:#66c0f4}
.notes img{max-width:100%;height:auto;display:block;margin:14px 0;border:1px solid var(--line,rgba(255,255,255,.1))}.notes .yt{display:inline-block;margin:12px 0;padding:9px 14px;background:#e8402a;color:#fff;text-decoration:none;font:700 .8rem/1 var(--hud);letter-spacing:.1em}
.side{display:flex;flex-direction:column;gap:14px;position:sticky;top:84px}
.box{padding:16px 18px;background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1))}
.box h4{margin:0 0 10px;font:700 .8rem/1 var(--hud);letter-spacing:.16em;color:var(--dim);text-transform:uppercase}
.box a.src{display:block;padding:11px 12px;background:#171a21;border:1px solid #2a475e;color:#c7d5e0;text-decoration:none;font:600 .82rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-align:center}
.box a.src:hover{background:#1b2838}
.box .ol{display:flex;flex-direction:column;gap:2px}.box .ol a{display:flex;justify-content:space-between;gap:10px;padding:8px 0;border-bottom:1px solid var(--line,rgba(255,255,255,.07));color:var(--soft);text-decoration:none;font-size:.86rem}.box .ol a:hover{color:#fff}.box .ol a span{color:var(--dim);flex:none}
.box .ln{font-size:.82rem;color:var(--dim);margin:10px 0 0}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}.pn a{padding:14px 16px;background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1));color:var(--ink,#fff);text-decoration:none}.pn a small{display:block;color:var(--dim);font-size:.76rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px}.pn a:hover{border-color:rgba(255,255,255,.3)}.pn a.nx{text-align:right;grid-column:2}
.nw .cta{display:block;margin-top:14px;padding:13px 16px;background:linear-gradient(90deg,#e8402a,#ff6a3d);color:#fff;font:700 .84rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;text-decoration:none;text-align:center}
.feat h2::before,.cd h3::before,.nw-hero h1::before{display:none!important}
@media(max-width:960px){.gridn{grid-template-columns:repeat(2,minmax(0,1fr))}.feat{grid-template-columns:1fr}.art{grid-template-columns:1fr}.side{position:static}}
@media(max-width:600px){.nw{padding:16px 14px 40px}.gridn{grid-template-columns:minmax(0,1fr)}.feat .bd{padding:18px}.notes{padding:16px}.art-h .cov{aspect-ratio:16/10}.art-h .ov{padding:40px 16px 16px}.pn{grid-template-columns:1fr}.pn a.nx{grid-column:auto}}
"""


def _utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).replace(tzinfo=None)


def fetch():
    req = urllib.request.Request(API, headers={"User-Agent": "skin-set.com news bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        items = json.load(r)["appnews"]["newsitems"]
    old = {x["gid"]: x for x in (json.load(open(DATA)) if os.path.exists(DATA) else [])}
    for x in items:
        prev = old.get(x["gid"], {})
        old[x["gid"]] = {"gid": x["gid"], "t": x["title"], "d": x["date"], "u": prev.get("u") or x["url"], "c": x["contents"], **({"img": prev["img"]} if prev.get("img") else {})}
    try:  # обложки и ссылки на новости из Steam Events
        req = urllib.request.Request("https://store.steampowered.com/events/ajaxgetadjacentpartnerevents/?appid=730&count_before=0&count_after=100&lang_list=0", headers={"User-Agent": "skin-set.com news bot"})
        with urllib.request.urlopen(req, timeout=30) as r:
            evs = json.load(r).get("events", [])
        for ev in evs:
            ab = ev.get("announcement_body") or {}
            try: jd = json.loads(ev.get("jsondata") or "{}")
            except Exception: jd = {}
            cap = next((c for c in (jd.get("localized_capsule_image") or []) if c), None)
            acc = int(ev.get("clan_steamid", 0)) - 103582791429521408
            for x in old.values():
                if x["t"].strip() == (ab.get("headline") or ev.get("event_name") or "").strip() and abs(x["d"] - (ab.get("posttime") or ev.get("rtime32_start_time") or 0)) < 172800:
                    if cap and acc > 0: x["img"] = f"https://clan.akamai.steamstatic.com/images/{acc}/{cap}"
                    if ab.get("gid"): x["u"] = f"https://store.steampowered.com/news/app/730/view/{ab['gid']}"
    except Exception as ex:
        print("events failed:", ex)
    out = sorted(old.values(), key=lambda x: -x["d"])[:200]
    json.dump(out, open(DATA, "w"), ensure_ascii=False, indent=0)
    return out


def bb(src):
    """BBCode Steam → безопасный HTML"""
    src = re.sub(r"(?:\[p\]\s*)?\\?\[\s+([A-Z0-9][A-Z0-9 &/\-]{1,38}?)\s+\\?\](?:\s*\[/p\])?", r"[h3]\1[/h3]", src)
    s = e(src).replace("{STEAM_CLAN_IMAGE}", "https://clan.akamai.steamstatic.com/images")
    s = s.replace("\\[", "&#91;").replace("\\]", "&#93;")
    s = re.sub(r"\[img(?: src=&quot;([^&]*)&quot;)?\](.*?)\[/img\]", lambda m: f'<img src="{m.group(1) or m.group(2)}" alt="" loading="lazy">' if (m.group(1) or m.group(2)).startswith("http") else "", s, flags=re.S)
    s = re.sub(r"\[previewyoutube=([\w-]+)[^\]]*\]\[/previewyoutube\]", r'<a class="yt" href="https://www.youtube.com/watch?v=\1" target="_blank" rel="noopener nofollow">▶ YouTube</a>', s)
    s = re.sub(r"\[url=&quot;?(https?://[^\]&]*)&quot;?[^\]]*\](.*?)\[/url\]", r'<a href="\1" target="_blank" rel="noopener nofollow">\2</a>', s, flags=re.S)
    s = re.sub(r"\[url\](https?://[^\[]*)\[/url\]", r'<a href="\1" target="_blank" rel="noopener nofollow">\1</a>', s)
    for a, b_ in [("h1", "h3"), ("h2", "h3"), ("h3", "h3"), ("h4", "h3"), ("h5", "h3"), ("b", "b"), ("i", "i"), ("u", "u"), ("strike", "s"), ("p", "p"), ("list", "ul"), ("olist", "ol"), ("code", "code"), ("quote", "blockquote"), ("table", "table"), ("tr", "tr"), ("td", "td"), ("th", "th")]:
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
    parts = re.split(r"(?:\[p\]\s*)?\\?\[\s+([A-Z0-9][A-Z0-9 &/\-]{1,38}?)\s+\\?\](?:\s*\[/p\])?", c)
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


def page_shell(lang, url, title, desc, ld, body, alts, og=""):
    h = head(lang, title, desc, SITE + url, alts, ld, og).replace("</head>", f"<style>{CSS}</style></head>")
    p = h + f"\n<body>\n{header(lang, {l: (url if l == lang else IDX[l]) for l in IDX})}\n<main class=\"nw\">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n"
    from skins_wiki import WIKI
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


def detail_url(lang, sl):
    return f"{IDX[DETAIL[lang]]}{sl}/"


UI = {"ru": dict(patchh="Обновление CS2", all="Все", patches="Патчи", news="Новости и скины", patch="Патч", newsl="Новость", kick="Valve · официально", read="Читать", others="Другие обновления", src="Открыть в Steam", sum_h="Что изменилось"),
      "en": dict(patchh="Counter-Strike 2 update", all="All", patches="Patches", news="News & skins", patch="Patch", newsl="News", kick="Valve · official", read="Read", others="More updates", src="Open on Steam", sum_h="What changed"),
      "de": dict(patchh="Counter-Strike-2-Update", all="Alle", patches="Patches", news="News & Skins", patch="Patch", newsl="News", kick="Valve · offiziell", read="Lesen"),
      "pt": dict(patchh="Atualização do CS2", all="Todas", patches="Patches", news="Notícias e skins", patch="Patch", newsl="Notícia", kick="Valve · oficial", read="Ler"),
      "tr": dict(patchh="Counter-Strike 2 güncellemesi", all="Tümü", patches="Yamalar", news="Haberler ve skinler", patch="Yama", newsl="Haber", kick="Valve · resmi", read="Oku"),
      "pl": dict(patchh="Aktualizacja CS2", all="Wszystkie", patches="Patche", news="Newsy i skiny", patch="Patch", newsl="News", kick="Valve · oficjalnie", read="Czytaj")}
MONN = {"ru": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
        "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
        "pt": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        "pl": ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]}


def image_of(x):
    if x.get("img"): return x["img"]
    m = re.search(r'\[img(?: src="([^"]+)")?\]([^\[]*)\[/img\]', x["c"])
    if not m: return None
    u = (m.group(1) or m.group(2)).replace("{STEAM_CLAN_IMAGE}", "https://clan.akamai.steamstatic.com/images")
    return u if u.startswith("http") and not u.lower().endswith(".gif") else None


def cover(lang, x, tot, big=False):
    im = image_of(x)
    if im: return f'<span class="cov"><img src="{e(im)}" alt="{e(x["t"])}" loading="{"eager" if big else "lazy"}"></span>'
    d = _utc(x["d"]); u = UI[lang]; patch = is_patch(x)
    mon = MON[lang][d.month - 1]
    return (f'<span class="cov gen{"" if patch else " news"}"><span class="g"><small>Counter-Strike 2</small>'
            f'<b>{d.day}<span>{e(mon)} {d.year}</span></b><em>{e(u["patch"] if patch else u["newsl"])}{f" · {tot} {e(T[lang].get("items", ""))}" if tot else ""}</em></span></span>')


def chips(lang, sec, n=6):
    s = [(a, b) for a, b in sec if b]
    return ('<ul class="chips">' + "".join(f"<li>{e(secname(lang, a))}<b>{b}</b></li>" for a, b in s[:n]) + "</ul>") if s else ""


def build(items):
    sl = slugs(items); made = []
    items = sorted(items, key=lambda x: -x["d"])
    # отдельные страницы обновлений: RU и EN
    for lang in ("ru", "en"):
        t = T[lang]; u_ = UI[lang]
        for k, x in enumerate(items):
            u = detail_url(lang, sl[x["gid"]]); D = dstr(lang, x["d"]); sec = sections(x["c"])
            patch = is_patch(x); tot = sum(b for _, b in sec)
            S = ", ".join(f"{secname(lang, a).lower() if lang == 'ru' else a.title()} ({b})" for a, b in sec if b) or plain(x["c"], 120)
            title = (t["upd_t"] if patch else t["news_t"]).format(D=D, T=x["t"]); h1 = (t["upd_h"] if patch else t["news_h"]).format(D=D, T=x["t"])
            desc = (t["upd_desc"] if patch else t["news_desc"]).format(D=D, S=S, T=x["t"])[:300]
            sk = bool(SKIN_RE.search(x["c"] + " " + x["t"]))
            pv = items[k + 1] if k + 1 < len(items) else None; nx = items[k - 1] if k > 0 else None
            pn = ""
            if pv: pn += f'<a href="{detail_url(lang, sl[pv["gid"]])}"><small>← {e(t["prev"])}</small>{e(dstr(lang, pv["d"]))}</a>'
            if nx: pn += f'<a class="nx" href="{detail_url(lang, sl[nx["gid"]])}"><small>{e(t["next"])} →</small>{e(dstr(lang, nx["d"]))}</a>'
            others = "".join(f'<a href="{detail_url(lang, sl[y["gid"]])}">{e(("Patch" if lang == "en" else "Патч") if is_patch(y) else y["t"])}<span>{e(dstr(lang, y["d"]))}</span></a>' for y in items[:7] if y is not x)[:4000]
            ld = [{"@context": "https://schema.org", "@type": "NewsArticle", "headline": h1, "datePublished": _utc(x["d"]).isoformat() + "Z",
                   "author": {"@type": "Organization", "name": "Valve"}, "publisher": {"@type": "Organization", "name": "Skinset", "url": SITE}, "mainEntityOfPage": SITE + u, "inLanguage": "en", "isBasedOn": x["u"]}
                  | ({"image": image_of(x)} if image_of(x) else {}),
                  {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": t["home"], "item": SITE + HOME[lang]}, {"@type": "ListItem", "position": 2, "name": t["h1"], "item": SITE + IDX[lang]}, {"@type": "ListItem", "position": 3, "name": h1, "item": SITE + u}]}]
            tags = f'<span class="nt {"ntp" if patch else "nts"}">{e(u_["patch"] if patch else u_["newsl"])}</span>' + (f'<span class="nt nts">{e(t["skins"])}</span>' if sk and patch else "") + (f'<span class="nt ntn">{e(t["last"])}</span>' if k == 0 else "")
            body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › <a href="{IDX[lang]}">{e(t["h1"])}</a> › {e(D)}</nav>'
                    + (f'<header class="art-h">{cover(lang, x, tot, True)}<div class="ov">' if image_of(x) else '<header class="art-h gen"><div class="ov">')
                    + f'<div class="nmeta">{tags}<span>{e(D)}</span></div><h1>{e(h1)}</h1></div></header>'
                    f'<div class="art"><div><div class="notes" lang="en">{bb(x["c"])}</div><div class="pn">{pn}</div></div>'
                    f'<aside class="side">'
                    + (f'<div class="box"><h4>{e(u_["sum_h"])}</h4>{chips(lang, sec, 20)}</div>' if tot else "")
                    + f'<div class="box"><a class="src" href="{e(x["u"])}" target="_blank" rel="noopener nofollow">{e(u_["src"])} ↗</a>' + (f'<p class="ln">{e(t["lang_note"])}</p>' if t.get("lang_note") else "")
                    + (f'<a class="cta" href="{HOME[lang]}">{e(t["cta"])}</a>' if sk else "") + '</div>'
                    + f'<div class="box"><h4>{e(u_["others"])}</h4><div class="ol">{others}</div><p class="ln"><a href="{IDX[lang]}" style="color:#66c0f4">{e(t["back"])}</a></p></div>'
                    f'</aside></div><p class="note">{e(t["note"])}</p>')
            alts = f'<link rel="alternate" hreflang="ru" href="{SITE}{detail_url("ru", sl[x["gid"]])}"><link rel="alternate" hreflang="en" href="{SITE}{detail_url("en", sl[x["gid"]])}"><link rel="alternate" hreflang="x-default" href="{SITE}{detail_url("en", sl[x["gid"]])}">'
            out = os.path.join(ROOT, u.strip("/"), "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(page_shell(lang, u, title, desc, ld, body, alts, image_of(x) or "")); made.append(u)
    # списки на 6 языках
    for lang in IDX:
        t = T[lang]; dl = DETAIL[lang]; tl = T[dl]; u_ = UI[lang]; sl_lang = "ru" if lang == "ru" else "en"
        def head_of(x):
            if lang in ("ru", "en"): return (tl["upd_h"] if is_patch(x) else tl["news_h"]).format(D=dstr(dl, x["d"]), T=x["t"])
            return x["t"] if not is_patch(x) else f"Counter-Strike 2 — {dstr(lang, x['d'])}"
        def tags_of(x, k):
            sk = bool(SKIN_RE.search(x["c"] + " " + x["t"])); p = is_patch(x)
            return (f'<span class="nt ntn">{e(t["last"])}</span>' if k == 0 else "") + f'<span class="nt {"ntp" if p else "nts"}">{e(u_["patch"] if p else u_["newsl"])}</span>' + (f'<span class="nt nts">{e(t["skins"])}</span>' if sk and p else "") + (f'<span>{e(dstr(lang, x["d"]))}</span>' if not p or k == 0 else "")
        x0 = items[0]; sec0 = sections(x0["c"]); tot0 = sum(b for _, b in sec0)
        feat = (f'<a class="feat" href="{detail_url(lang, sl[x0["gid"]])}" data-k="{"p" if is_patch(x0) else "n"}">{cover(lang, x0, tot0, True)}<div class="bd"><div class="nmeta">{tags_of(x0, 0)}</div><h2>{e(head_of(x0))}</h2>'
                + (chips(sl_lang, sec0, 8) if tot0 else f'<p>{e(plain(x0["c"], 200))}</p>') + f'<span class="go">{e(u_["read"])} →</span></div></a>')
        grid = []; curm = None
        for k, x in enumerate(items[1:60], 1):
            d = _utc(x["d"]); mk = (d.year, d.month)
            if mk != curm:
                if curm: grid.append("</div>")
                curm = mk; mname = (MONN.get(lang) or MON[lang if lang in MON else "en"])[d.month - 1]
                grid.append(f'<h2 class="mon">{e(mname.capitalize())} {d.year}</h2><div class="gridn">')
            sec = sections(x["c"]); tot = sum(b for _, b in sec)
            if is_patch(x) and not image_of(x):
                mo = MON[lang if lang in MON else "en"][d.month - 1]
                grid.append(f'<a class="cd pc" href="{detail_url(lang, sl[x["gid"]])}" data-k="p"><span class="dt"><b>{d.day}</b><small>{e(mo[:3] if lang != "ru" else mo[:3])}</small></span><div class="bd"><div class="nmeta">{tags_of(x, k)}</div><h3>{e(u_["patchh"])}</h3>'
                            + (chips(sl_lang, sec, 4) if tot else f'<p>{e(plain(x["c"], 110))}</p>') + '</div></a>')
            else:
                grid.append(f'<a class="cd" href="{detail_url(lang, sl[x["gid"]])}" data-k="{"p" if is_patch(x) else "n"}">{cover(lang, x, tot)}<div class="bd"><div class="nmeta">{tags_of(x, k)}</div><h3>{e(head_of(x))}</h3>'
                            + (chips(sl_lang, sec, 4) if tot else f'<p>{e(plain(x["c"], 130))}</p>') + '</div></a>')
        if curm: grid.append("</div>")
        D0 = dstr(lang, items[0]["d"]); url = IDX[lang]
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": t["h1"], "url": SITE + url, "description": t["desc"].format(D=D0)},
              {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + detail_url(lang, sl[x["gid"]])} for i, x in enumerate(items[:20])]}]
        filt = (f'<div class="nw-f" id="nwf"><button class="on" data-f="">{e(u_["all"])}</button><button data-f="p">{e(u_["patches"])}</button><button data-f="n">{e(u_["news"])}</button></div>'
                '<script>(()=>{const f=document.getElementById("nwf");f.addEventListener("click",ev=>{const b=ev.target.closest("button");if(!b)return;f.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));const k=b.dataset.f;'
                'document.querySelectorAll(".cd,.feat").forEach(c=>c.style.display=!k||c.dataset.k===k?"":"none");document.querySelectorAll(".gridn").forEach(g=>{const v=[...g.children].some(c=>c.style.display!=="none");g.style.display=v?"":"none";g.previousElementSibling.style.display=v?"":"none"})})})()</script>')
        body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav>'
                f'<div class="nw-hero"><span class="nw-kick"><i></i>{e(u_["kick"])}</span><h1>{e(t["h1"])}</h1><p class="lead">{e(t["lead"])}</p></div>'
                + filt + feat + "".join(grid) + f'<p class="note">{e(t["note"])}</p>')
        alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{IDX[l]}">' for l in IDX) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{IDX["en"]}">'
        out = os.path.join(ROOT, url.strip("/"), "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(page_shell(lang, url, t["title"], t["desc"].format(D=D0), ld, body, alts, image_of(items[0]) or "")); made.append(url)
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
