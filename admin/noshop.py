# -*- coding: utf-8 -*-
"""Убирает кнопки покупки DMarket (не работает из России) и ставит заглушку «Здесь может быть ваша площадка».
python3 admin/noshop.py   — идемпотентно, по всем страницам и шаблонам блога.
Чтобы вернуть площадку: поменять SHOP_JS ниже (url/label) и перезапустить.
"""
import glob, os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import csmoney

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGOF = {"ru": "ru", "en": "en", "de": "de", "pt-BR": "pt", "pt": "pt", "tr": "tr", "pl": "pl"}
ABOUT = {"ru": "/o-proekte/", "en": "/en/about/", "de": "/de/ueber-uns/", "pt": "/pt/sobre/", "tr": "/tr/hakkimizda/", "pl": "/pl/o-projekcie/"}
AD = {  # (маленькая подпись, крупно, коротко для карточки, описание для «Площадок»)
    "ru": ("Купить", "Ваша площадка", "Купить · ваша площадка", "Маркетплейсам и брендам: кнопка покупки в каждой карточке скина. Напишите нам."),
    "en": ("Buy", "Your marketplace", "Buy · your marketplace", "For marketplaces and brands: a buy button on every skin card. Get in touch."),
    "de": ("Kaufen", "Ihr Marktplatz", "Kaufen · Ihr Marktplatz", "Für Marktplätze und Marken: ein Kauf-Button auf jeder Skin-Karte. Schreiben Sie uns."),
    "pt": ("Comprar", "Sua loja", "Comprar · sua loja", "Para marketplaces e marcas: botão de compra em cada card de skin. Fale conosco."),
    "tr": ("Satın al", "Pazar yeriniz", "Satın al · pazar yeriniz", "Pazar yerleri ve markalar için: her skin kartında satın alma düğmesi. Bize yazın."),
    "pl": ("Kup", "Twój marketplace", "Kup · Twój marketplace", "Dla marketplace'ów i marek: przycisk zakupu na każdej karcie skina. Napisz do nas."),
}
STEP4 = {"ru": "Сохраняй сет или делись им", "en": "Save the set or share it", "de": "Set speichern oder teilen", "pt": "Salve o set ou compartilhe",
         "tr": "Seti kaydet ya da paylaş", "pl": "Zapisz zestaw lub udostępnij"}
STEP4_OLD = ["Покупай по кнопке DMarket", "Buy via the DMarket button", "Über den DMarket-Button kaufen", "DMarket düğmesinden al"]
WHERE = {  # абзац «где купить» и ответ FAQ
    "ru": "Skinset показывает ориентир по цене для каждого предмета и всего сета — цены обновляются каждые 4 часа. Сам сайт ничего не продаёт и не связан с сайтами кейсов: собери сет здесь, а купить скины можно на любой удобной площадке.",
    "en": "Skinset shows a price guide for every item and the whole set, updated every 4 hours. The site doesn't sell anything and has nothing to do with case sites: build the set here and buy the skins on any marketplace you like.",
    "de": "Skinset zeigt Richtpreise für jedes Item und das ganze Set, alle 4 Stunden aktualisiert. Die Seite verkauft nichts und hat nichts mit Case-Seiten zu tun: Set hier bauen, Skins auf einem Marktplatz deiner Wahl kaufen.",
    "pt": "O Skinset mostra uma referência de preço para cada item e para o set, atualizada a cada 4 horas. O site não vende nada e não tem ligação com sites de caixas: monte o set aqui e compre as skins na loja que preferir.",
    "tr": "Skinset her eşya ve tüm set için 4 saatte bir güncellenen fiyat rehberi gösterir. Site bir şey satmaz, kasa siteleriyle ilgisi yoktur: seti burada kur, skinleri istediğin pazar yerinden al.",
    "pl": "Skinset pokazuje orientacyjne ceny każdego przedmiotu i całego zestawu, aktualizowane co 4 godziny. Strona nic nie sprzedaje i nie ma nic wspólnego ze skrzynkami: złóż zestaw tutaj, a skiny kup na dowolnym rynku.",
}
AD_CSS = """<style id="noshop-css">
.cb a.ad,.cb a.csm{grid-column:1/-1;width:100%;background:linear-gradient(90deg,rgba(255,21,154,.22),#16161d 70%)!important;color:#fff!important;border:1px solid #ff159a!important;font-size:.62rem!important;letter-spacing:.06em;box-shadow:0 4px 14px rgba(255,21,154,.15)}
.buy a.ad,.buy a.csm{background:linear-gradient(90deg,rgba(255,21,154,.28),rgba(255,21,154,.08) 55%,#16161d)!important;color:#fff!important;border:2px solid #ff159a!important;box-shadow:0 0 0 1px rgba(255,21,154,.25),0 8px 26px rgba(255,21,154,.38)!important}
.buy a.ad .tx small,.buy a.csm .tx small{color:rgba(255,255,255,.85)!important;opacity:1}.buy a.ad .tx b,.buy a.csm .tx b{color:#fff!important;font-size:.98rem}
.buy a.ad .ico,.buy a.ad .lg,.buy a.csm .ico,.buy a.csm .lg{background:transparent!important;color:#fff!important;border-color:rgba(255,255,255,.35)!important}
.buy a.ad .arr,.buy a.csm .arr{color:#fff!important;opacity:1}
.cb a.ad:hover,.cb a.csm:hover{background:#24121d!important}.buy a.ad:hover,.buy a.csm:hover{background:linear-gradient(90deg,rgba(255,21,154,.42),rgba(255,21,154,.16) 60%,#1d1420)!important;box-shadow:0 0 0 1px rgba(255,21,154,.4),0 10px 32px rgba(255,21,154,.5)!important}
.sp-price{background:rgba(255,255,255,.05)!important;color:var(--ink,#fff)!important;box-shadow:none!important;border:1px solid rgba(255,255,255,.14);cursor:default}
.sp-ad{display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding:12px 14px;background:#16161d;border:1px solid #ff159a;color:#fff;font:700 .82rem/1 var(--hud,sans-serif);letter-spacing:.08em;text-transform:uppercase;text-decoration:none;box-shadow:0 8px 22px rgba(255,21,154,.3)}
.sp-ad img{width:20px;height:20px;border-radius:4px;margin-right:8px;vertical-align:-5px}
.sp-ad small{font:500 .7rem/1 var(--hud,sans-serif);opacity:.85;margin-right:6px}
.sp-ad:hover{filter:brightness(1.12)}
</style>"""


CSM = {  # (кнопка, маленькая подпись, описание для «Площадок»)
    "ru": ("Купить на CS.MONEY", "Купить на", "Маркетплейс скинов CS2: покупка, обмен и моментальная продажа скинов."),
    "en": ("Buy on CS.MONEY", "Buy on", "CS2 skin marketplace: buy, trade and instantly sell skins."),
    "de": ("Bei CS.MONEY kaufen", "Kaufen bei", "CS2-Skin-Marktplatz: Skins kaufen, tauschen und sofort verkaufen."),
    "pt": ("Comprar na CS.MONEY", "Comprar na", "Marketplace de skins de CS2: compre, troque e venda skins na hora."),
    "tr": ("CS.MONEY'de satın al", "Satın al", "CS2 skin pazarı: skin al, takas et ve anında sat."),
    "pl": ("Kup na CS.MONEY", "Kup na", "Marketplace skinów CS2: kupuj, wymieniaj i sprzedawaj skiny od ręki."),
}
CSM_SEARCH = "https://cs.money/market/buy/?search="


def shops_js(lang):
    lb, k, ab = CSM[lang]
    return ('const SHOPS = [ { id:"csm", label:' + repr(lb) + ', kick:' + repr(k) + ', long:"CS.MONEY", mark:"CS", about:' + repr(ab)
            + ', url:(q,s) => { const n=s?(s.weapon.replace("★ ","")+" | "+s.skin.replace(/\\s*\\(.*\\)/,"")+(s.wearShown?" ("+WEAR_FULL[s.wearShown]+")":"")):""; '
            + 'return n?"' + CSM_SEARCH + '"+encodeURIComponent(n)+"&' + csmoney.UTM + '":"' + csmoney.MARKET + '"; } } ];')


FONT_RE = re.compile(r'(?<!<noscript>)<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)" rel="stylesheet">')
STEAM_IMG = "https://community.akamai.steamstatic.com/economy/image/"


def perf(s):
    """Скорость: шрифты не блокируют отрисовку, картинки скинов в нужном размере, локальная база картинок."""
    s = FONT_RE.sub(lambda m: f'<link rel="preload" as="style" href="{m.group(1)}" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link href="{m.group(1)}" rel="stylesheet"></noscript>', s)
    # превью скинов (ленивые картинки) — 360px вместо 512px
    s = re.sub(r'(<img\b[^>]*?src="' + re.escape(STEAM_IMG) + r'[A-Za-z0-9_-]+)("[^>]*\bloading="lazy")', r'\1/360fx270f\2', s)
    # конструктор: своя компактная база картинок вместо 4,7 МБ с GitHub
    s = s.replace('const IMG_SRC="https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/skins.json";', 'const IMG_SRC="/data/skin-img.json";')
    s = s.replace('try{const r=await fetch(IMG_SRC);if(!r.ok)throw 0;const list=await r.json();',
                  'try{const r=await fetch(IMG_SRC);if(!r.ok)throw 0;const list=(await r.json()).map(a=>Array.isArray(a)?{name:a[0],image:"' + STEAM_IMG + '"+a[1]+"/360fx270f",phase:a[2]}:a);')
    s = s.replace('fetch("/data/skins-extra.json",{cache:"no-store"})', 'fetch("/data/skins-extra.json")')
    return s


HOMES = {"https://skin-set.com/": "ru", "https://skin-set.com/en/": "en", "https://skin-set.com/de/": "de", "https://skin-set.com/pt/": "pt", "https://skin-set.com/tr/": "tr", "https://skin-set.com/pl/": "pl"}
HOME_TITLE = {"ru": ("Skinset — подбор скинов CS2 по цвету:", "Skinset CS2 — подбор скинов по цвету:"),
              "en": ("Skinset — CS2 skins by color:", "Skinset CS2 — skins by color:"),
              "de": ("Skinset — CS2-Skins nach Farbe:", "Skinset CS2 — Skins nach Farbe:"),
              "pt": ("Skinset — skins de CS2 por cor:", "Skinset CS2 — skins por cor:"),
              "tr": ("Skinset — renge göre CS2 skinleri:", "Skinset CS2 — renge göre skinler:"),
              "pl": ("Skinset — skiny CS2 według koloru:", "Skinset CS2 — skiny według koloru:")}


def brand(s):
    """Бренд для Google: «Skinset CS2» (по слову «skinset» в выдаче — косметологическая клиника)."""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
    lang = HOMES.get(m.group(1)) if m else None
    if not lang: return s
    a, b = HOME_TITLE[lang]
    s = s.replace("<title>" + a, "<title>" + b).replace('content="' + a, 'content="' + b)
    s = s.replace('og:site_name" content="Skinset"', 'og:site_name" content="Skinset CS2"')
    if 'id="ld-site"' not in s:
        url = m.group(1)
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebSite", "@id": "https://skin-set.com/#website", "url": url, "name": "Skinset CS2",
             "alternateName": ["Skinset", "Skin Set CS2", "skin-set.com"], "inLanguage": lang,
             "publisher": {"@id": "https://skin-set.com/#org"}},
            {"@type": "Organization", "@id": "https://skin-set.com/#org", "name": "Skinset CS2", "alternateName": "skin-set.com",
             "url": "https://skin-set.com/", "logo": "https://skin-set.com/img/apple-touch-icon.png",
             "sameAs": ["https://www.twitch.tv/viv1stop"]}]}
        import json as _j
        s = s.replace("</head>", '<script type="application/ld+json" id="ld-site">' + _j.dumps(ld, ensure_ascii=False) + "</script></head>", 1)
    return s



GATE_TXT = {
    "ru": ("Нравится? Продолжим со Steam", "Вход бесплатный и занимает пару секунд. Бонус — соберём сет из твоих скинов.", "Позже"),
    "en": ("Enjoying it? Continue with Steam", "It's free and takes a couple of seconds. Bonus — we'll build a set from your skins.", "Maybe later"),
    "de": ("Gefällt's dir? Weiter mit Steam", "Kostenlos und in ein paar Sekunden erledigt. Bonus — ein Set aus deinen Skins.", "Später"),
    "pt": ("Curtindo? Continue com a Steam", "É grátis e leva poucos segundos. Bônus — um set com as suas skins.", "Depois"),
    "tr": ("Beğendin mi? Steam ile devam et", "Ücretsiz ve birkaç saniye sürer. Bonus — skinlerinle set kurarız.", "Sonra"),
    "pl": ("Podoba się? Kontynuuj ze Steam", "Za darmo i zajmuje kilka sekund. Bonus — zestaw z twoich skinów.", "Później"),
}
GATE_CSS = """<style id="stm-gate2">
.stm-gate{background:rgba(5,6,10,.72)!important;backdrop-filter:blur(6px)}
.stm-gbox{width:min(380px,100%)!important;border:1px solid rgba(232,64,42,.35)!important;border-top:1px solid rgba(232,64,42,.35)!important;border-radius:18px!important;padding:30px 26px 18px!important;
 background:radial-gradient(420px 200px at 50% -40px,rgba(232,64,42,.22),transparent 70%),#111318!important;box-shadow:0 30px 80px rgba(0,0,0,.6)!important;animation:stmIn .28s ease}
.stm-gi{width:68px;height:68px;margin:0 auto;border-radius:50%;display:grid;place-items:center;background:rgba(232,64,42,.12);box-shadow:0 0 0 8px rgba(232,64,42,.05)}
.stm-gi svg{width:38px!important;height:38px!important;color:#ff6a3d!important}
.stm-gbox h3{margin:16px 0 8px!important;font-size:1.3rem!important;text-transform:none!important;letter-spacing:.01em!important}
.stm-gbox p{margin:0 0 20px!important;font-size:.92rem!important;line-height:1.5!important}
.stm-gin{height:50px!important;border-radius:12px!important;font-size:.9rem!important;background:linear-gradient(180deg,#ff6a3d,#e8402a)!important;box-shadow:0 8px 24px rgba(232,64,42,.35)!important}
.stm-glater{margin-top:8px!important;font-size:.78rem!important}
.stm-gx{top:10px!important;right:12px!important}
@keyframes stmIn{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}
</style>"""


GATE_LIMIT = "Infinity"  # вернуть обязательный вход: поставить, например, "5"


def gate(s):
    """окно входа в конструкторе: после 5 смен цвета/скинов, короче и дружелюбнее"""
    if not re.search(r"const LIM=(?:\d+|Infinity);let GC=", s): return s
    # GATE_LIMIT: сколько смен цвета/скинов без входа; "Infinity" — вход не требуется (сейчас выключено)
    s = re.sub(r"/\* без входа: [^*]*\*/", "/* без входа: лимит смен цвета и скинов = GATE_LIMIT, дальше предложение войти */", s, count=1)
    s = re.sub(r"const LIM=(?:\d+|Infinity);let GC=", "const LIM=" + GATE_LIMIT + ";let GC=", s, count=1)
    for lg, (t, p, l) in GATE_TXT.items():
        s = re.sub(lg + r':\{gateT:"[^"]*",gateP:"[^"]*",later:"[^"]*"', lambda m: lg + ':{gateT:' + json.dumps(t, ensure_ascii=False) + ',gateP:' + json.dumps(p, ensure_ascii=False) + ',later:' + json.dumps(l, ensure_ascii=False), s, count=1)
    if 'id="stm-gate2"' in s: s = re.sub(r'<style id="stm-gate2">.*?</style>', lambda m: GATE_CSS, s, count=1, flags=re.S)
    elif "</head>" in s: s = s.replace("</head>", GATE_CSS + "</head>", 1)
    return s

SHOPS_LEAD = {"на две площадки": "на CS.MONEY", "lead to two marketplaces": "lead to CS.MONEY",
              "führen zu zwei Marktplätzen": "führen zu CS.MONEY", "levam a duas lojas": "levam à CS.MONEY",
              "iki pazar yerine götürür": "CS.MONEY'ye götürür", "prowadzą na dwa rynki": "prowadzą na CS.MONEY"}


BQ_OLD = 'q.addEventListener("click",()=>{clearTimeout(bT);applyBudget(q.dataset.v===""?null:+q.dataset.v,true)})'
BQ_NEW = 'q.addEventListener("click",()=>{clearTimeout(bT);if(q.getAttribute("aria-pressed")==="true"&&typeof reroll==="function"){reroll();return}applyBudget(q.dataset.v===""?null:+q.dataset.v,true)})'


def shopsfix(s):
    s = s.replace(BQ_OLD, BQ_NEW)  # повторный клик по выбранному бюджету — перемешать сет
    """страница «Где покупать»: убрать устаревшую таблицу DMarket / Lis-Skins"""
    s = re.sub(r'<div class="tablewrap"><table class="cmp">.*?</table></div>\s*', "", s, flags=re.S)
    for a, b in SHOPS_LEAD.items(): s = s.replace(a, b)
    return s


def fix(s):
    m = re.search(r'<html lang="([^"]+)"', s); lang = LANGOF.get(m.group(1) if m else "ru", "ru")
    o = s
    # конструктор
    s = re.sub(r'const SHOPS = \[.*?\}\s*\];', lambda _: shops_js(lang), s, count=1, flags=re.S)
    s = re.sub(r'data-buy title="[^"]*\$\{sh\.label\}"', 'data-buy title="${sh.long||sh.label}"', s)
    s = re.sub(r'<span class="tx"><small>[^<]*</small><b>\$\{sh\.label\}</b></span>', '<span class="tx"><small>${sh.kick||""}</small><b>${sh.long||sh.label}</b></span>', s)
    s = s.replace('${mark(sh.id,sh.label.slice(0,2).toUpperCase())}', '${mark(sh.id,sh.id==="ad"?"+":sh.label.slice(0,2).toUpperCase())}')
    s = s.replace('target="_blank" rel="noopener sponsored" href="${sh.url("")}">', 'href="${sh.url("")}">')
    if lang != "ru":
        s = s.replace("</svg>Картинка сета</button>", "</svg>" + {"en": "Set image", "de": "Set-Bild", "pt": "Imagem do set", "tr": "Set görseli", "pl": "Obraz zestawu"}[lang] + "</button>")
    s = s.replace('${mark(sh.id,sh.id==="ad"?"+":sh.label.slice(0,2).toUpperCase())}', '${mark(sh.id,sh.mark||sh.label.slice(0,2).toUpperCase())}')
    s = s.replace('${mark(sh.id,sh.label.slice(0,2).toUpperCase(),"ico")}', '${mark(sh.id,sh.mark||sh.label.slice(0,2).toUpperCase(),"ico")}')
    s = re.sub(r'target="_blank" rel="noopener(?: sponsored)?" href="\$\{sh\.url\(queryW\(s\)(?:,s)?\)\}"', lambda m: 'target="_blank" rel="noopener sponsored" href="${sh.url(queryW(s),s)}"', s)
    if "const LOGOS = {" in s and 'csm:["/img/csmoney.png"]' not in s:
        s = s.replace("const LOGOS = {", 'const LOGOS = {\n  csm:["/img/csmoney.png"],', 1)
    for x in STEP4_OLD: s = s.replace(f"<span>{x}</span>", f"<span>{STEP4[lang]}</span>")
    s = re.sub(r'<li><b>4</b><span>[^<]*DMarket[^<]*</span>', f'<li><b>4</b><span>{STEP4[lang]}</span>', s)
    # тексты «где купить»
    s = re.sub(r'<p>[^<]*(?:Купить на DMarket|Buy on DMarket|Kaufen bei DMarket|Comprar na DMarket|DMarket\'ten al|Kup na DMarket)[^<]*</p>', f'<p>{WHERE[lang]}</p>', s)
    s = re.sub(r'"text":"[^"]*(?:кнопка перехода на DMarket|has a DMarket button|Button zu DMarket|botão para a DMarket|DMarket düğmesi var|przycisk do DMarket)[^"]*"', '"text":"' + WHERE[lang] + '"', s)
    # всплывашка скина в блоге: вместо кнопки покупки — цена и заглушка
    s = s.replace('`<a class="sp-buy" href="${dm(name,cur)}" target="_blank" rel="noopener sponsored"><span>${T.buy}</span><b>${price}</b></a>',
                  '`<div class="sp-buy sp-price"><span>${T.mk||""}</span><b>${price}</b></div><a class="sp-ad" href="' + ABOUT[lang] + '#partners">' + AD[lang][1] + ' →</a>')
    s = re.sub(r'buy:"",(?:mk:"[^"]*",)+', 'buy:"",', s)
    s = re.sub(r'(\{q:"[^"]*",)buy:"[^"]*"', lambda m: m.group(1) + 'buy:"",mk:"' + {"ru": "Цена на рынке", "en": "Market price", "de": "Marktpreis", "pt": "Preço de mercado", "tr": "Piyasa fiyatı", "pl": "Cena rynkowa"}[lang] + '"', s)
    # таблицы цен в статьях блога: убрать ссылки DMarket
    s = re.sub(r'<td class="pb"><a href="https://dmarket\.com[^"]*"[^>]*>DMarket</a></td>', '<td class="pb"></td>', s)
    # списки скинов на цветовых страницах и прочие прямые ссылки на DMarket/Lis-Skins
    s = re.sub(r'<a href="https://(?:dmarket\.com|lis-skins\.com)[^"]*"[^>]*>(?:DMarket|Lis-Skins)</a>', "", s)
    s = re.sub(r'<a href="https://dmarket\.com[^"]*"[^>]*>(.*?)</a>', r"\1", s)
    s = re.sub(r'<a class="sp-ad"[^>]*>.*?</a>', lambda m: '<a class="sp-ad" ' + csmoney.REL + ' href="' + CSM_SEARCH + '${encodeURIComponent(name.replace(/★\\s*/,"").replace(/\\s*\\((Phase \\d|Ruby|Sapphire|Emerald|Black Pearl)\\)$/,"")+(cur?" ("+WF[cur]+")":""))}&' + csmoney.UTM + '"><span><img src="/img/csmoney.png" alt=""><small>' + CSM[lang][1] + '</small>CS.MONEY</span><span>→</span></a>', s)
    s = re.sub(r'<style id="noshop-css">.*?</style>', lambda _: AD_CSS, s, flags=re.S)
    if s != o and 'id="noshop-css"' not in s:
        s = s.replace("</head>", AD_CSS + "</head>", 1)
    import navmore
    s = navmore.nogw(navmore.gametab(navmore.setsmain(navmore.hideabout(navmore.updlink(navmore.gwfirst(s))))))
    s = shopsfix(gate(perf(brand(s))))
    return s


def main():
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
        if "/admin/" in f: continue
        t = open(f, encoding="utf-8").read(); o = fix(t)
        if o != t: open(f, "w", encoding="utf-8").write(o); n += 1
    print(n, "files")


if __name__ == "__main__":
    main()
