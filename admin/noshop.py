# -*- coding: utf-8 -*-
"""Убирает кнопки покупки DMarket (не работает из России) и ставит заглушку «Здесь может быть ваша площадка».
python3 admin/noshop.py   — идемпотентно, по всем страницам и шаблонам блога.
Чтобы вернуть площадку: поменять SHOP_JS ниже (url/label) и перезапустить.
"""
import glob, os, re, sys
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
.cb a.ad,.cb a.csm{grid-column:1/-1;width:100%;background:linear-gradient(90deg,#ff159a,#e0127f)!important;color:#fff!important;border:0!important;font-size:.62rem!important;letter-spacing:.06em;box-shadow:0 4px 14px rgba(45,115,255,.35)}
.buy a.ad,.buy a.csm{background:linear-gradient(90deg,#ff159a,#e0127f)!important;color:#fff!important;border:0!important;box-shadow:0 0 0 1px rgba(255,21,154,.35),0 8px 22px rgba(255,21,154,.3)}
.buy a.ad .tx small,.buy a.csm .tx small{color:rgba(255,255,255,.85)!important;opacity:1}.buy a.ad .tx b,.buy a.csm .tx b{color:#fff!important;font-size:.98rem}
.buy a.ad .ico,.buy a.ad .lg,.buy a.csm .ico,.buy a.csm .lg{background:rgba(255,255,255,.18)!important;color:#fff!important;border-color:rgba(255,255,255,.35)!important}
.buy a.ad .arr,.buy a.csm .arr{color:#fff!important;opacity:1}
.buy a.ad:hover,.cb a.ad:hover,.buy a.csm:hover,.cb a.csm:hover{filter:brightness(1.12)}
.sp-price{background:rgba(255,255,255,.05)!important;color:var(--ink,#fff)!important;box-shadow:none!important;border:1px solid rgba(255,255,255,.14);cursor:default}
.sp-ad{display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding:12px 14px;background:linear-gradient(90deg,#ff159a,#e0127f);color:#fff;font:700 .82rem/1 var(--hud,sans-serif);letter-spacing:.08em;text-transform:uppercase;text-decoration:none;box-shadow:0 8px 22px rgba(255,21,154,.3)}
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
    s = navmore.setsmain(navmore.hideabout(navmore.updlink(navmore.gwfirst(s))))
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
