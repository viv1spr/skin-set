# -*- coding: utf-8 -*-
"""Страницы «инвентарь CS2 за N» для всех языков.
Запуск: python3 admin/budget_pages.py
Данные сетов: data/budget-sets.json (считает admin/budget-sets.js — тот же подбор, что в конструкторе).
"""
import json, os, re, html, statistics, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(ROOT, "admin"))
from about import CP, PCOL, PNAMES, HREFLANG  # noqa

e = lambda s: html.escape(str(s), quote=True)
SITE = "https://skin-set.com"

# язык: (курс ₽ за единицу, список сумм в местной валюте)
BUD = {
    "ru": (1, [500, 1000, 2000, 3000, 5000, 10000, 20000, 30000, 50000, 100000]),
    "en": (90, [5, 15, 25, 50, 100, 150, 250, 500, 1000]),
    "de": (100, [10, 25, 50, 100, 250, 500, 1000]),
    "pt": (18, [50, 100, 250, 500, 1000, 2500, 5000]),
    "tr": (2.7, [250, 500, 1000, 2500, 5000, 10000, 25000]),
    "pl": (22, [50, 100, 250, 500, 1000, 2500, 5000]),
}
HOMEF = {"ru": "index.html", "en": "en/index.html", "de": "de/index.html", "pt": "pt/index.html", "tr": "tr/index.html", "pl": "pl/index.html"}
PRE = {"ru": "", "en": "/en", "de": "/de", "pt": "/pt", "tr": "/tr", "pl": "/pl"}
LOCALE = {"ru": "ru_RU", "en": "en_US", "de": "de_DE", "pt": "pt_BR", "tr": "tr_TR", "pl": "pl_PL"}


def slug(lang, n):
    return {"ru": f"inventar-cs2-za-{n}-rubley", "en": f"cs2-loadout-under-{n}-dollars", "de": f"cs2-inventar-unter-{n}-euro",
            "pt": f"inventario-cs2-ate-{n}-reais", "tr": f"{n}-tl-alti-cs2-envanteri", "pl": f"ekwipunek-cs2-do-{n}-zl"}[lang]


def path(lang, n):
    return f"{PRE[lang]}/{slug(lang, n)}/"


def grp(n, sep):
    return f"{n:,}".replace(",", sep)


def money(lang, v):
    """v — сумма в местной валюте"""
    if lang == "ru": return grp(int(round(v / 10.0) * 10 if v >= 100 else round(v)), " ") + " ₽"
    if lang == "en": return f"${v:,.2f}" if v < 10 else f"${int(round(v)):,}"
    if lang == "de": return (f"{v:.2f}".replace(".", ",") if v < 10 else grp(int(round(v)), ".")) + " €"
    if lang == "pt": return "R$ " + (f"{v:.2f}".replace(".", ",") if v < 10 else grp(int(round(v)), "."))
    if lang == "tr": return grp(int(round(v)), ".") + " ₺"
    if lang == "pl": return (f"{v:.2f}".replace(".", ",") if v < 10 else grp(int(round(v)), " ")) + " zł"


SLOTN = {
    "ru": {"knife": "Нож", "gloves": "Перчатки"}, "en": {"knife": "Knife", "gloves": "Gloves"}, "de": {"knife": "Messer", "gloves": "Handschuhe"},
    "pt": {"knife": "Faca", "gloves": "Luvas"}, "tr": {"knife": "Bıçak", "gloves": "Eldiven"}, "pl": {"knife": "Nóż", "gloves": "Rękawice"},
}
SLOTW = {"ak": "AK-47", "m4": "M4A4 / M4A1-S", "awp": "AWP", "deagle": "Desert Eagle", "usp": "USP-S", "glock": "Glock-18"}


def slotname(lang, sid):
    return SLOTN[lang].get(sid) or SLOTW.get(sid, sid)


def tier(rub):
    return 0 if rub < 1500 else 1 if rub < 8500 else 2 if rub < 30000 else 3 if rub < 70000 else 4


# ---------------- тексты ----------------
T = {
 "ru": dict(
  title="Красивый инвентарь CS2 за {B}: готовые сеты в одном цвете — Skinset",
  desc="Что можно собрать в CS2 за {B}: {n} примеров сетов в красном, синем, фиолетовом и других цветах с реальными ценами, что влезает в бюджет и где купить скины.",
  h1="Красивый инвентарь CS2 за {B}", crumb="Главная", budgets="Инвентарь по бюджету",
  intro=[
   "{B} — бюджет «дёшево, но в одной гамме». Ножа и перчаток здесь не будет, зато все шесть основных стволов можно закрыть скинами в один цвет. Главное правило: один акцент на AK-47, M4 и AWP, пистолеты — в тон. Так даже дешёвый инвентарь выглядит как продуманный сет, а не случайный дроп из кейсов.",
   "За {B} уже можно выбирать: шесть основных стволов получают скины заметно лучше дропа, а на AK-47 и AWP хватает на узнаваемые раскраски. Ножа и перчаток пока нет — самый дешёвый нож стоит дороже всего бюджета, поэтому лучше собрать аккуратный оружейный сет и докупить нож позже.",
   "{B} — порог, с которого в сет влезают нож и перчатки. Это будут недорогие модели (Gut, Navaja, Shadow Daggers, перчатки в поношенном качестве), но инвентарь уже полный: нож, перчатки и шесть стволов в одной гамме. Чем ближе к верхней границе, тем больше денег уходит на нож.",
   "За {B} нож и перчатки становятся главной частью сета: можно взять популярные модели ножей и перчатки в хорошем состоянии, а оружие подобрать в тон без компромиссов по цвету. Это уровень, на котором инвентарь выглядит дорого и цельно.",
   "{B} — премиальный бюджет. Конструктор выбирает самые дорогие подходящие по цвету скины: ножи уровня Karambit и Butterfly, перчатки Sport и Specialist, топовые раскраски на AK-47 и AWP. Ограничением становится уже не бюджет, а то, сколько скинов нужного цвета существует в CS2."],
  data="В примерах ниже конструктор собирает в этот бюджет от {mn} до {mx} (в среднем {avg}). Самый дорогой предмет среди примеров — {top} за {topp}.",
  ex_h="Примеры сетов за {B}", ex_p="Это сеты, которые конструктор Skinset собирает на этот бюджет автоматически по ценам на {date}. Нажми «Открыть в конструкторе» — откроется точно этот сет, дальше можно менять отдельные слоты и качество.",
  total="Итого", open="Открыть в конструкторе", nofit="не влезает в бюджет",
  tab_h="Сколько стоит каждый слот при бюджете {B}", tab_c=["Слот", "Обычно", "Диапазон"],
  how_h="Как распределяется бюджет", how="Сначала каждому стволу достаётся минимум, потом нож и перчатки — если их минимальная цена влезает, потом уровни повышаются по очереди: важнее всего нож и перчатки, затем AK-47, M4 и AWP, затем пистолеты. Поэтому сет получается сбалансированным, а не «один дорогой AK и пустота».",
  oth="Другие бюджеты", col="Сеты по цвету", colpre="Сет", blog="Полезно почитать",
  faq_h="Вопросы и ответы",
  q1="Что можно купить в CS2 за {B}?", a1n="Шесть основных стволов (AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) в одной гамме, в среднем за {avg}. Ножа и перчаток в этот бюджет не влезает.", a1y="Полный инвентарь: нож, перчатки и шесть основных стволов в одной гамме. В среднем такой сет стоит {avg}, из них на нож уходит около {kn}.",
  q2="Можно ли купить нож за {B}?", a2n="Нет: самый дешёвый нож в примерах стоит около {kmin}, это больше бюджета. Лучше собрать оружие в одном цвете сейчас, а нож добавить позже — сет останется цельным.", a2y="Да. Самый доступный нож в примерах — {kname} примерно за {kp}. Конструктор сам решает, сколько отдать на нож, а сколько на оружие.",
  q3="Какой цвет сета самый дешёвый при бюджете {B}?", a3="В примерах дешевле всего выходит {cname} — около {cp}, дороже всего {xname} — около {xp}. Разница связана с тем, сколько скинов нужного цвета есть в CS2.",
  q4="Где купить скины для сета?", a4="Skinset показывает ориентир по цене для каждого предмета и всего сета — цены обновляются каждые 4 часа. Сам сайт ничего не продаёт и не связан с сайтами кейсов: собери сет здесь, а купить скины можно на любой удобной площадке.",
 ),
 "en": dict(
  title="Good-looking CS2 loadout under {B}: ready color sets — Skinset",
  desc="What you can build in CS2 for {B}: {n} example loadouts in red, blue, purple and other colors with real prices, what fits the budget and where to buy the skins.",
  h1="Good-looking CS2 loadout under {B}", crumb="Home", budgets="Loadouts by budget",
  intro=[
   "{B} is the “cheap but matching” budget. There is no room for a knife or gloves, but all six main guns can wear skins in one color. The rule: one accent on the AK-47, M4 and AWP, pistols in the same tone. That way even a cheap inventory looks like a planned set, not random case drops.",
   "At {B} you start having choices: the six main guns get skins clearly better than drops, and the AK-47 and AWP can wear recognizable finishes. No knife or gloves yet — the cheapest knife costs more than the whole budget, so build a clean gun set now and add a knife later.",
   "{B} is where a knife and gloves start to fit. They will be budget models (Gut, Navaja, Shadow Daggers, gloves in worn condition), but the inventory is complete: knife, gloves and six guns in one color. The closer to the top of the range, the more money goes into the knife.",
   "With {B} the knife and gloves become the centerpiece: popular knife models and gloves in good condition, with guns matched in tone without color compromises. This is the level where an inventory looks expensive and coherent.",
   "{B} is a premium budget. The builder picks the most expensive skins that match the color: Karambit and Butterfly-tier knives, Sport and Specialist gloves, top finishes on the AK-47 and AWP. The limit is no longer money but how many skins of that color exist in CS2."],
  data="In the examples below the builder spends between {mn} and {mx} on this budget ({avg} on average). The most expensive item among them is {top} at {topp}.",
  ex_h="Example loadouts under {B}", ex_p="These are the sets the Skinset builder assembles for this budget automatically, using prices from {date}. Click “Open in builder” to load exactly this set, then swap single slots and change wear.",
  total="Total", open="Open in builder", nofit="doesn't fit the budget",
  tab_h="How much each slot costs on a {B} budget", tab_c=["Slot", "Typical", "Range"],
  how_h="How the budget is split", how="First every gun gets a minimum, then the knife and gloves if their cheapest price fits, then tiers go up in turn: knife and gloves first, then AK-47, M4 and AWP, then pistols. That keeps the set balanced instead of “one expensive AK and nothing else”.",
  oth="Other budgets", col="Sets by color", colpre="Set", blog="Worth reading",
  faq_h="FAQ",
  q1="What can you buy in CS2 for {B}?", a1n="The six main guns (AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) in one color, around {avg} on average. A knife and gloves don't fit this budget.", a1y="A full inventory: knife, gloves and six main guns in one color. On average such a set costs {avg}, with about {kn} going into the knife.",
  q2="Can you get a knife for {B}?", a2n="No: the cheapest knife in the examples is about {kmin}, more than the budget. Build the guns in one color now and add a knife later — the set will still match.", a2y="Yes. The most affordable knife in the examples is the {kname} at about {kp}. The builder decides how much goes to the knife and how much to the guns.",
  q3="Which color set is the cheapest at {B}?", a3="In the examples the cheapest is {cname} at about {cp}, the most expensive is {xname} at about {xp}. The difference comes from how many skins of that color exist in CS2.",
  q4="Where do I buy the skins?", a4="Skinset shows a price guide for every item and the whole set, updated every 4 hours. The site doesn't sell anything and has nothing to do with case sites: build the set here and buy the skins on any marketplace you like.",
 ),
 "de": dict(
  title="Schönes CS2-Inventar unter {B}: fertige Farb-Sets — Skinset",
  desc="Was man in CS2 für {B} bauen kann: {n} Beispiel-Sets in Rot, Blau, Lila und weiteren Farben mit echten Preisen, was ins Budget passt und wo man die Skins kauft.",
  h1="Schönes CS2-Inventar unter {B}", crumb="Start", budgets="Inventar nach Budget",
  intro=[
   "{B} ist das Budget „günstig, aber einheitlich“. Messer und Handschuhe passen nicht hinein, dafür bekommen alle sechs Hauptwaffen Skins in einer Farbe. Die Regel: ein Akzent auf AK-47, M4 und AWP, Pistolen im gleichen Ton. So wirkt selbst ein günstiges Inventar wie ein geplantes Set statt zufälliger Case-Drops.",
   "Mit {B} hast du schon Auswahl: die sechs Hauptwaffen bekommen deutlich bessere Skins als Drops, und bei AK-47 und AWP reicht es für bekannte Designs. Messer und Handschuhe noch nicht — das günstigste Messer kostet mehr als das ganze Budget. Also jetzt ein sauberes Waffen-Set bauen und das Messer später ergänzen.",
   "Ab {B} passen Messer und Handschuhe ins Set. Es sind günstige Modelle (Gut, Navaja, Shadow Daggers, Handschuhe in abgenutztem Zustand), aber das Inventar ist komplett: Messer, Handschuhe und sechs Waffen in einer Farbe. Je näher am oberen Ende, desto mehr Geld geht ins Messer.",
   "Mit {B} werden Messer und Handschuhe zum Mittelpunkt: beliebte Messermodelle und Handschuhe in gutem Zustand, Waffen passend im Ton ohne Farbkompromisse. Auf diesem Niveau wirkt das Inventar teuer und stimmig.",
   "{B} ist ein Premium-Budget. Der Builder nimmt die teuersten farblich passenden Skins: Messer wie Karambit und Butterfly, Sport- und Specialist-Handschuhe, Top-Designs auf AK-47 und AWP. Die Grenze ist nicht mehr das Geld, sondern wie viele Skins in dieser Farbe es in CS2 gibt."],
  data="In den Beispielen unten gibt der Builder bei diesem Budget zwischen {mn} und {mx} aus (im Schnitt {avg}). Der teuerste Gegenstand darunter ist {top} für {topp}.",
  ex_h="Beispiel-Sets unter {B}", ex_p="Diese Sets stellt der Skinset-Builder für dieses Budget automatisch zusammen, Preise vom {date}. „Im Builder öffnen“ lädt genau dieses Set — danach einzelne Slots tauschen und den Zustand ändern.",
  total="Gesamt", open="Im Builder öffnen", nofit="passt nicht ins Budget",
  tab_h="Was jeder Slot bei {B} kostet", tab_c=["Slot", "Typisch", "Spanne"],
  how_h="So wird das Budget verteilt", how="Zuerst bekommt jede Waffe ein Minimum, dann Messer und Handschuhe, falls ihr günstigster Preis passt, dann steigen die Stufen der Reihe nach: zuerst Messer und Handschuhe, dann AK-47, M4 und AWP, dann Pistolen. So bleibt das Set ausgewogen statt „eine teure AK und sonst nichts“.",
  oth="Andere Budgets", col="Sets nach Farbe", colpre="Set", blog="Lesenswert",
  faq_h="FAQ",
  q1="Was kann man in CS2 für {B} kaufen?", a1n="Die sechs Hauptwaffen (AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) in einer Farbe, im Schnitt etwa {avg}. Messer und Handschuhe passen nicht ins Budget.", a1y="Ein komplettes Inventar: Messer, Handschuhe und sechs Hauptwaffen in einer Farbe. Im Schnitt kostet so ein Set {avg}, davon etwa {kn} für das Messer.",
  q2="Bekommt man für {B} ein Messer?", a2n="Nein: das günstigste Messer in den Beispielen kostet etwa {kmin}, mehr als das Budget. Baue jetzt die Waffen in einer Farbe und ergänze das Messer später.", a2y="Ja. Das günstigste Messer in den Beispielen ist {kname} für etwa {kp}. Der Builder entscheidet, wie viel ins Messer und wie viel in die Waffen geht.",
  q3="Welche Set-Farbe ist bei {B} am günstigsten?", a3="In den Beispielen ist {cname} mit etwa {cp} am günstigsten, {xname} mit etwa {xp} am teuersten. Der Unterschied hängt davon ab, wie viele Skins es in der Farbe gibt.",
  q4="Wo kauft man die Skins?", a4="Skinset zeigt Richtpreise für jedes Item und das ganze Set, alle 4 Stunden aktualisiert. Die Seite verkauft nichts und hat nichts mit Case-Seiten zu tun: Set hier bauen, Skins auf einem Marktplatz deiner Wahl kaufen.",
 ),
 "pt": dict(
  title="Inventário bonito de CS2 até {B}: sets prontos por cor — Skinset",
  desc="O que dá para montar no CS2 com {B}: {n} sets de exemplo em vermelho, azul, roxo e outras cores com preços reais, o que cabe no orçamento e onde comprar as skins.",
  h1="Inventário bonito de CS2 até {B}", crumb="Início", budgets="Inventário por orçamento",
  intro=[
   "{B} é o orçamento “barato, mas combinando”. Não sobra para faca e luvas, mas as seis armas principais podem ter skins na mesma cor. A regra: um destaque na AK-47, M4 e AWP, pistolas no mesmo tom. Assim até um inventário barato parece um set pensado, e não drops aleatórios de caixa.",
   "Com {B} já dá para escolher: as seis armas principais recebem skins bem melhores que drops, e na AK-47 e AWP cabem pinturas conhecidas. Faca e luvas ainda não — a faca mais barata custa mais que o orçamento inteiro. Monte agora um set de armas limpo e adicione a faca depois.",
   "{B} é o ponto em que faca e luvas começam a caber. Serão modelos baratos (Gut, Navaja, Shadow Daggers, luvas desgastadas), mas o inventário fica completo: faca, luvas e seis armas na mesma cor. Quanto mais perto do topo da faixa, mais dinheiro vai para a faca.",
   "Com {B} a faca e as luvas viram o centro do set: modelos populares de faca e luvas em bom estado, com as armas no mesmo tom sem abrir mão da cor. É o nível em que o inventário parece caro e coerente.",
   "{B} é um orçamento premium. O montador escolhe as skins mais caras que combinam com a cor: facas do nível Karambit e Butterfly, luvas Sport e Specialist, pinturas top na AK-47 e AWP. O limite deixa de ser o dinheiro e passa a ser quantas skins daquela cor existem no CS2."],
  data="Nos exemplos abaixo o montador gasta entre {mn} e {mx} com este orçamento ({avg} em média). O item mais caro entre eles é {top} por {topp}.",
  ex_h="Sets de exemplo até {B}", ex_p="Estes são os sets que o montador Skinset monta para este orçamento automaticamente, com preços de {date}. Clique em “Abrir no montador” para carregar exatamente este set e depois trocar slots e mudar o desgaste.",
  total="Total", open="Abrir no montador", nofit="não cabe no orçamento",
  tab_h="Quanto custa cada slot com {B}", tab_c=["Slot", "Normalmente", "Faixa"],
  how_h="Como o orçamento é dividido", how="Primeiro cada arma recebe um mínimo, depois a faca e as luvas, se o preço mínimo couber, depois os níveis sobem por vez: faca e luvas primeiro, depois AK-47, M4 e AWP, depois pistolas. Assim o set fica equilibrado, e não “uma AK cara e mais nada”.",
  oth="Outros orçamentos", col="Sets por cor", colpre="Set", blog="Vale a leitura",
  faq_h="Perguntas frequentes",
  q1="O que dá para comprar no CS2 com {B}?", a1n="As seis armas principais (AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) na mesma cor, cerca de {avg} em média. Faca e luvas não cabem nesse orçamento.", a1y="Um inventário completo: faca, luvas e seis armas principais na mesma cor. Em média esse set custa {avg}, com cerca de {kn} indo para a faca.",
  q2="Dá para comprar uma faca com {B}?", a2n="Não: a faca mais barata nos exemplos custa cerca de {kmin}, mais que o orçamento. Monte as armas numa cor agora e adicione a faca depois.", a2y="Sim. A faca mais acessível nos exemplos é a {kname} por cerca de {kp}. O montador decide quanto vai para a faca e quanto para as armas.",
  q3="Qual cor de set é a mais barata com {B}?", a3="Nos exemplos a mais barata é {cname}, cerca de {cp}; a mais cara é {xname}, cerca de {xp}. A diferença vem de quantas skins daquela cor existem no CS2.",
  q4="Onde comprar as skins?", a4="O Skinset mostra uma referência de preço para cada item e para o set, atualizada a cada 4 horas. O site não vende nada e não tem ligação com sites de caixas: monte o set aqui e compre as skins na loja que preferir.",
 ),
 "tr": dict(
  title="{B} altı güzel CS2 envanteri: tek renkte hazır setler — Skinset",
  desc="CS2'de {B} ile ne kurulur: kırmızı, mavi, mor ve diğer renklerde gerçek fiyatlı {n} örnek set, bütçeye neyin sığdığı ve skinlerin nereden alınacağı.",
  h1="{B} altı güzel CS2 envanteri", crumb="Ana sayfa", budgets="Bütçeye göre envanter",
  intro=[
   "{B}, “ucuz ama uyumlu” bütçedir. Bıçak ve eldivene yer yok, ama altı ana silahın hepsi tek renkte skin giyebilir. Kural: AK-47, M4 ve AWP'de tek vurgu, tabancalar aynı tonda. Böylece ucuz bir envanter bile kasa düşüşlerinden oluşan rastgele bir yığın değil, planlı bir set gibi görünür.",
   "{B} ile seçenekler başlar: altı ana silah düşüşlerden belirgin şekilde iyi skinler alır, AK-47 ve AWP'ye tanınan desenler sığar. Bıçak ve eldiven henüz yok — en ucuz bıçak bütün bütçeden pahalı. Şimdi temiz bir silah seti kur, bıçağı sonra ekle.",
   "{B}, bıçak ve eldivenin sete sığmaya başladığı eşiktir. Uygun fiyatlı modeller olur (Gut, Navaja, Shadow Daggers, aşınmış eldivenler), ama envanter tamamdır: bıçak, eldiven ve tek renkte altı silah. Aralığın üstüne yaklaştıkça paranın çoğu bıçağa gider.",
   "{B} ile bıçak ve eldiven setin merkezine geçer: popüler bıçak modelleri ve iyi durumda eldivenler, silahlar renkten taviz vermeden aynı tonda. Envanterin pahalı ve bütün göründüğü seviye budur.",
   "{B} premium bir bütçedir. Oluşturucu renge uyan en pahalı skinleri seçer: Karambit ve Butterfly seviyesinde bıçaklar, Sport ve Specialist eldivenler, AK-47 ve AWP'de en iyi desenler. Sınır artık para değil, CS2'de o renkte kaç skin olduğudur."],
  data="Aşağıdaki örneklerde oluşturucu bu bütçeyle {mn} ile {mx} arasında harcıyor (ortalama {avg}). Aralarındaki en pahalı eşya {topp} fiyatla {top}.",
  ex_h="{B} altı örnek setler", ex_p="Bunlar Skinset oluşturucusunun bu bütçe için otomatik kurduğu setler, fiyatlar {date} tarihli. “Oluşturucuda aç” tam olarak bu seti yükler; sonra tek tek slotları değiştirip aşınmayı seçebilirsin.",
  total="Toplam", open="Oluşturucuda aç", nofit="bütçeye sığmıyor",
  tab_h="{B} bütçede her slot ne kadar", tab_c=["Slot", "Genelde", "Aralık"],
  how_h="Bütçe nasıl dağıtılır", how="Önce her silaha bir minimum ayrılır, sonra en ucuz fiyatı sığarsa bıçak ve eldiven, sonra seviyeler sırayla yükselir: önce bıçak ve eldiven, sonra AK-47, M4 ve AWP, sonra tabancalar. Böylece set “bir pahalı AK ve gerisi boş” değil, dengeli olur.",
  oth="Diğer bütçeler", col="Renge göre setler", colpre="Set", blog="Okumaya değer",
  faq_h="Sık sorulan sorular",
  q1="CS2'de {B} ile ne alınır?", a1n="Altı ana silah (AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) tek renkte, ortalama {avg}. Bıçak ve eldiven bu bütçeye sığmaz.", a1y="Tam bir envanter: bıçak, eldiven ve tek renkte altı ana silah. Böyle bir set ortalama {avg}, bunun yaklaşık {kn} kadarı bıçağa gider.",
  q2="{B} ile bıçak alınır mı?", a2n="Hayır: örneklerdeki en ucuz bıçak yaklaşık {kmin}, bütçeden fazla. Şimdi silahları tek renkte kur, bıçağı sonra ekle — set yine uyumlu kalır.", a2y="Evet. Örneklerdeki en uygun bıçak yaklaşık {kp} fiyatla {kname}. Oluşturucu bıçağa ve silahlara ne kadar ayrılacağına kendisi karar verir.",
  q3="{B} bütçede en ucuz set rengi hangisi?", a3="Örneklerde en ucuzu yaklaşık {cp} ile {cname}, en pahalısı yaklaşık {xp} ile {xname}. Fark, CS2'de o renkte kaç skin olduğundan gelir.",
  q4="Skinler nereden alınır?", a4="Skinset her eşya ve tüm set için 4 saatte bir güncellenen fiyat rehberi gösterir. Site bir şey satmaz, kasa siteleriyle ilgisi yoktur: seti burada kur, skinleri istediğin pazar yerinden al.",
 ),
 "pl": dict(
  title="Ładny ekwipunek CS2 do {B}: gotowe zestawy w jednym kolorze — Skinset",
  desc="Co można złożyć w CS2 za {B}: {n} przykładowych zestawów w czerwieni, niebieskim, fiolecie i innych kolorach z prawdziwymi cenami, co mieści się w budżecie i gdzie kupić skiny.",
  h1="Ładny ekwipunek CS2 do {B}", crumb="Start", budgets="Ekwipunek według budżetu",
  intro=[
   "{B} to budżet „tanio, ale w jednym kolorze”. Nie zmieści się nóż ani rękawice, za to wszystkie sześć głównych broni może mieć skiny w jednej barwie. Zasada: jeden akcent na AK-47, M4 i AWP, pistolety w tym samym tonie. Dzięki temu nawet tani ekwipunek wygląda jak przemyślany zestaw, a nie przypadkowe dropy ze skrzynek.",
   "Przy {B} pojawia się wybór: sześć głównych broni dostaje skiny wyraźnie lepsze niż dropy, a na AK-47 i AWP starcza na rozpoznawalne wzory. Noża i rękawic jeszcze nie ma — najtańszy nóż kosztuje więcej niż cały budżet. Zbuduj teraz czysty zestaw broni, a nóż dokup później.",
   "{B} to próg, od którego w zestawie mieszczą się nóż i rękawice. Będą to tańsze modele (Gut, Navaja, Shadow Daggers, rękawice w zużytym stanie), ale ekwipunek jest kompletny: nóż, rękawice i sześć broni w jednym kolorze. Im bliżej górnej granicy, tym więcej pieniędzy idzie na nóż.",
   "Przy {B} nóż i rękawice stają się centrum zestawu: popularne modele noży i rękawice w dobrym stanie, a bronie dobrane w tonie bez kompromisów w kolorze. Na tym poziomie ekwipunek wygląda drogo i spójnie.",
   "{B} to budżet premium. Kreator wybiera najdroższe skiny pasujące do koloru: noże klasy Karambit i Butterfly, rękawice Sport i Specialist, topowe wzory na AK-47 i AWP. Ograniczeniem nie są już pieniądze, tylko to, ile skinów w tym kolorze istnieje w CS2."],
  data="W przykładach poniżej kreator wydaje przy tym budżecie od {mn} do {mx} (średnio {avg}). Najdroższy przedmiot wśród nich to {top} za {topp}.",
  ex_h="Przykładowe zestawy do {B}", ex_p="To zestawy, które kreator Skinset składa automatycznie na ten budżet, ceny z {date}. „Otwórz w kreatorze” wczytuje dokładnie ten zestaw — potem możesz wymieniać pojedyncze sloty i zmieniać stan.",
  total="Razem", open="Otwórz w kreatorze", nofit="nie mieści się w budżecie",
  tab_h="Ile kosztuje każdy slot przy budżecie {B}", tab_c=["Slot", "Zwykle", "Zakres"],
  how_h="Jak dzielony jest budżet", how="Najpierw każda broń dostaje minimum, potem nóż i rękawice, jeśli ich najniższa cena się mieści, potem poziomy rosną po kolei: najpierw nóż i rękawice, potem AK-47, M4 i AWP, potem pistolety. Dzięki temu zestaw jest zrównoważony, a nie „jedno drogie AK i nic więcej”.",
  oth="Inne budżety", col="Zestawy według koloru", colpre="Zestaw", blog="Warto przeczytać",
  faq_h="Pytania i odpowiedzi",
  q1="Co można kupić w CS2 za {B}?", a1n="Sześć głównych broni (AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) w jednym kolorze, średnio około {avg}. Nóż i rękawice nie mieszczą się w tym budżecie.", a1y="Pełny ekwipunek: nóż, rękawice i sześć głównych broni w jednym kolorze. Średnio taki zestaw kosztuje {avg}, z czego około {kn} idzie na nóż.",
  q2="Czy za {B} kupię nóż?", a2n="Nie: najtańszy nóż w przykładach kosztuje około {kmin}, więcej niż budżet. Złóż teraz bronie w jednym kolorze, a nóż dodaj później.", a2y="Tak. Najtańszy nóż w przykładach to {kname} za około {kp}. Kreator sam decyduje, ile przeznaczyć na nóż, a ile na bronie.",
  q3="Który kolor zestawu jest najtańszy przy {B}?", a3="W przykładach najtańszy jest {cname} — około {cp}, najdroższy {xname} — około {xp}. Różnica wynika z tego, ile skinów w danym kolorze jest w CS2.",
  q4="Gdzie kupić skiny?", a4="Skinset pokazuje orientacyjne ceny każdego przedmiotu i całego zestawu, aktualizowane co 4 godziny. Strona nic nie sprzedaje i nie ma nic wspólnego ze skrzynkami: złóż zestaw tutaj, a skiny kup na dowolnym rynku.",
 ),
}
DATEF = {"ru": "%d.%m.%Y", "en": "%b %d, %Y", "de": "%d.%m.%Y", "pt": "%d/%m/%Y", "tr": "%d.%m.%Y", "pl": "%d.%m.%Y"}

# статьи блога по теме бюджета
def blog_links(lang, slugs):
    P = json.load(open(os.path.join(ROOT, "blog/posts.json"), encoding="utf-8")); P = P if isinstance(P, list) else P["posts"]
    out = []
    for sl in slugs:
        p = next((x for x in P if x.get("slug") == sl), None)
        if not p: continue
        tt = p["title"] if lang == "ru" else (p.get("tr", {}).get(lang) or {}).get("title")
        if tt: out.append((f"{PRE[lang]}/blog/{sl}/", tt))
    return out


BLOGS = ["krasivyj-inventar-cs2-za-5000-rubley", "samye-deshevye-nozhi-cs2", "kachestvo-skinov-cs2-fn-mw-ft-ww-bs"]


CSS = """<style data-bp>
.seo-set{border:1px solid var(--line);padding:12px 14px;margin:10px 0;background:rgba(255,255,255,.02)}
.seo-set h3{margin:0 0 10px;font:600 .9rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;display:flex;align-items:center;gap:8px}
.seo-set h3 i{width:12px;height:12px;background:linear-gradient(135deg,var(--c0) 50%,var(--c1,var(--c0)) 50%);transform:rotate(45deg);border:1px solid rgba(255,255,255,.25)}
.seo-set ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:6px 14px;font-size:.86rem}
.seo-set li{display:flex;align-items:center;gap:8px;min-width:0}
.seo-set li img{width:54px;height:40px;object-fit:contain;flex:none;filter:drop-shadow(0 4px 6px rgba(0,0,0,.5))}
.seo-set li span{display:flex;flex-direction:column;min-width:0}
.seo-set li b{font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seo-set li small{color:var(--soft);font-size:.76rem}
.seo-set .est{margin-top:10px;font-size:.84rem;color:var(--soft);display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center}
.seo-set .est b{color:var(--ink)}
.seo-set .est a{font:600 .7rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;padding:8px 10px;border:1px solid var(--line2);color:var(--ink);text-decoration:none}
.seo-set .est a:hover{border-color:var(--pick);color:var(--pick)}
.seo-tab{width:100%;border-collapse:collapse;margin:10px 0;font-size:.88rem}
.seo-tab th,.seo-tab td{border:1px solid var(--line);padding:7px 10px;text-align:left}
.seo-tab th{font:600 .72rem/1.2 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}
.seo-crumbs{font-size:.8rem;color:var(--soft);margin-bottom:8px}.seo-crumbs a{color:var(--soft)}
.seo-chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;padding:0;list-style:none}
.seo-chips a{display:inline-block;padding:7px 10px;border:1px solid var(--line2);color:var(--ink);text-decoration:none;font-size:.84rem}
.seo-chips a.on{border-color:var(--pick);color:var(--pick)}
</style>"""

# ---------------- данные ----------------
IMG = {}
for r in json.load(open(os.path.join(ROOT, "admin/skins-api.json"))):
    IMG.setdefault((r[0], r[5] if len(r) > 5 else ""), r[1]); IMG.setdefault((r[0], ""), r[1])


def img(weapon, skin):
    m = re.match(r"(.*?)\s*\((.*)\)$", skin)
    base, ph = (m.group(1), m.group(2)) if m else (skin, "")
    n = weapon.replace("★ ", "") + " | " + base
    return IMG.get((n, ph)) or IMG.get((n, "")) or ""


SETS = json.load(open(os.path.join(ROOT, "data/budget-sets.json")))
META = {}
try: META = json.load(open(os.path.join(ROOT, "data/prices-meta.json")))
except Exception: pass


WIKI = {"ru": "/skiny/", "en": "/en/skins/", "de": "/de/skins/", "pt": "/pt/skins/", "tr": "/tr/skinler/", "pl": "/pl/skiny/"}
WIKIL = {"ru": "Справочник скинов CS2", "en": "CS2 skin guide", "de": "CS2-Skin-Guide", "pt": "Guia de skins de CS2", "tr": "CS2 skin rehberi", "pl": "Przewodnik po skinach CS2"}
try:
    _WN = set(json.load(open(os.path.join(ROOT, "data/wiki-index.json"))))
except Exception:
    _WN = set()


def wiki_url(lang, name):
    """ссылка на вики-страницу скина или None"""
    if name not in _WN: return None
    s = name.lower().replace("★", "").replace("|", " ").replace("&", " and ").replace("'", "")
    return WIKI[lang] + re.sub(r"[^a-z0-9]+", "-", s).strip("-") + "/"


def sets_for(rub):
    k = str(int(round(rub)))
    return [[r for r in SETS[str(p)][k] if r[1]] for p in range(9)]


def page(lang, n, tpl, date):
    rate, lst = BUD[lang]; t = T[lang]; rub = int(round(n * rate))
    B = money(lang, n); loc = lambda r: money(lang, r / rate)
    S = sets_for(rub)
    tots = [sum(x[3] for x in s) for s in S]
    avg = statistics.mean(tots)
    allit = [(x, p) for p, s in enumerate(S) for x in s]
    top = max(allit, key=lambda z: z[0][3])[0]
    knives = [x for s in S for x in s if x[0] == "knife"]
    hasknife = len(knives) >= 5
    url = SITE + path(lang, n)
    title = t["title"].format(B=B); desc = t["desc"].format(B=B, n=9)
    # --- примеры
    blocks = []
    for p, s in enumerate(S):
        c = PCOL[p]; sty = f"--c0:{c[0]}" + (f";--c1:{c[1]}" if len(c) > 1 else "")
        lis = []
        for sid in ["knife", "gloves", "ak", "m4", "awp", "deagle", "usp", "glock"]:
            x = next((y for y in s if y[0] == sid), None)
            if not x:
                continue
            name = f"{x[1].replace('★ ', '')} | {x[2]}"; im = img(x[1], x[2])
            pic = f'<img src="{e(im)}" alt="{e(name)}" loading="lazy" width="54" height="40">' if im else ""
            wu = wiki_url(lang, name)
            lis.append(f'<li>{pic}<span><b>{f'<a href="{wu}">{e(name)}</a>' if wu else e(name)}</b><small>{e(x[4] or "")} · {e(loc(x[3]))}</small></span></li>')
        setq = quote(";".join(f"{x[1]}|{x[2]}" for x in s), safe="")
        href = f"{PRE[lang]}/{CP[lang][p]}/?budget={rub}&set={setq}"
        blocks.append(f'<div class="seo-set" style="{sty}"><h3><i></i>{e(PNAMES[lang][p])}</h3><ul>{"".join(lis)}</ul>'
                      f'<div class="est"><span>{e(t["total"])}: <b>≈ {e(loc(tots[p]))}</b></span><a href="{e(href)}">{e(t["open"])} →</a></div></div>')
    # --- таблица слотов
    rows = []
    for sid in ["knife", "gloves", "ak", "m4", "awp", "deagle", "usp", "glock"]:
        v = [x[3] for s in S for x in s if x[0] == sid]
        if len(v) < 5:
            rows.append(f"<tr><td>{e(slotname(lang, sid))}</td><td colspan=2>{e(t['nofit'])}</td></tr>"); continue
        rows.append(f"<tr><td>{e(slotname(lang, sid))}</td><td>{e(loc(statistics.median(v)))}</td><td>{e(loc(min(v)))} – {e(loc(max(v)))}</td></tr>")
    tab = f'<table class="seo-tab"><thead><tr>{"".join(f"<th>{e(c)}</th>" for c in t["tab_c"])}</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    # --- FAQ
    ci, xi = tots.index(min(tots)), tots.index(max(tots))
    fm = dict(B=B, avg=loc(avg), cname=PNAMES[lang][ci].lower() if lang != "de" else PNAMES[lang][ci], cp=loc(tots[ci]),
              xname=PNAMES[lang][xi].lower() if lang != "de" else PNAMES[lang][xi], xp=loc(tots[xi]))
    if hasknife:
        kmn = min(knives, key=lambda x: x[3])
        fm.update(kn=loc(statistics.median([x[3] for x in knives])), kname=f"{kmn[1].replace('★ ', '')} | {kmn[2]}", kp=loc(kmn[3]))
    else:
        kall = [x[3] for k in SETS["0"] for p in range(9) for x in SETS[str(p)][k] if x[1] and x[0] == "knife" and x[3] > 0]
        fm.update(kmin=loc(min(kall)))
    faq = [(t["q1"].format(**fm), (t["a1y"] if hasknife else t["a1n"]).format(**fm)),
           (t["q2"].format(**fm), (t["a2y"] if hasknife else t["a2n"]).format(**fm)),
           (t["q3"].format(**fm), t["a3"].format(**fm)),
           (t["q4"], t["a4"])]
    # --- ссылки
    oth = "".join(f'<li><a href="{path(lang, m)}"{" class=on" if m == n else ""}>{e(t["h1"].format(B=money(lang, m)).replace("Красивый инвентарь CS2", "Инвентарь").replace("Good-looking CS2 loadout", "Loadout").replace("Schönes CS2-Inventar", "Inventar").replace("Inventário bonito de CS2", "Inventário").replace(" altı güzel CS2 envanteri", " altı envanter").replace("Ładny ekwipunek CS2", "Ekwipunek"))}</a></li>' for m in lst)
    cols = "".join(f'<li><a href="{PRE[lang]}/{CP[lang][p]}/?budget={rub}">{e(PNAMES[lang][p])}</a></li>' for p in range(9))
    blog = "".join(f'<li><a href="{h}">{e(a)}</a></li>' for h, a in blog_links(lang, BLOGS))
    home = (PRE[lang] or "") + "/"
    seo = (f'<section class="seo collapsed" id="seo"><button class="seo-tg" id="seoTg" type="button" aria-expanded="false" data-o="{{O}}" data-c="{{C}}"><span>{{O}}</span><i></i></button>\n      <div class="seo-in">\n'
           f'<nav class="seo-crumbs"><a href="{home}">{e(t["crumb"])}</a> › {e(t["budgets"])} › {e(B)}</nav>'
           f'<h1>{e(t["h1"].format(B=B))}</h1><div id="seoColor" hidden></div><ul id="seoLinks" hidden></ul>\n'
           f'<p>{e(t["intro"][tier(rub)].format(B=B))}</p>\n'
           f'<p>{e(t["data"].format(mn=loc(min(tots)), mx=loc(max(tots)), avg=loc(avg), top=top[1].replace("★ ", "") + " | " + top[2], topp=loc(top[3])))}</p>\n'
           f'<h2>{e(t["ex_h"].format(B=B))}</h2><p>{e(t["ex_p"].format(date=date))}</p>\n{"".join(blocks)}\n'
           f'<h2>{e(t["tab_h"].format(B=B))}</h2>{tab}\n'
           f'<h2>{e(t["how_h"])}</h2><p>{e(t["how"])}</p>\n'
           f'<h2>{e(t["faq_h"])}</h2>' + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq) + "\n"
           f'<h2>{e(t["oth"])}</h2><ul class="seo-chips">{oth}</ul>\n'
           f'<h2>{e(t["col"])}</h2><ul class="seo-chips">{cols}</ul>\n'
           + (f'<h2>{e(t["blog"])}</h2><ul class="seo-chips">{blog}</ul>\n' if blog else "") +
           '      </div>\n    </section>')
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": t["crumb"], "item": SITE + home},
              {"@type": "ListItem", "position": 2, "name": t["h1"].format(B=B), "item": url}]}]
    s = tpl
    i = s.find('<section class="seo'); j = s.find("</section>", i) + len("</section>")
    m = re.search(r'data-o="([^"]*)" data-c="([^"]*)"', s[i:j])
    s = s[:i] + seo.replace("{O}", m.group(1)).replace("{C}", m.group(2)) + s[j:]
    s = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(title)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(desc)}">', s, count=1)
    s = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{e(title)}">', s, count=1)
    s = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{e(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s, count=1)
    s = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", s)
    s = s.replace('<link rel="canonical"', f'<link rel="alternate" hreflang="{HREFLANG[lang]}" href="{url}">\n<link rel="canonical"', 1)
    # hero h1 → h2 (h1 теперь в SEO-блоке)
    s = re.sub(r'<h1>(.*?)</h1>', r'<h2 class="hero-h">\1</h2>', s, count=1, flags=re.S)
    # JSON-LD главной → FAQ этой страницы
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld) + CSS + "</head>", 1)
    s = re.sub(r'<script>window\.PAGE_ROUTE="home";', f'<script>window.PAGE_ROUTE="home";window.PAGE_BUDGET={rub};', s, count=1)
    return s


def main():
    d = datetime.date.today()
    made = []
    for lang, (rate, lst) in BUD.items():
        tpl = open(os.path.join(ROOT, HOMEF[lang]), encoding="utf-8").read()
        assert not re.search(r"window\.PAGE_(BUDGET|PRESET)=\d", tpl)
        date = d.strftime(DATEF[lang])
        for n in lst:
            out = os.path.join(ROOT, path(lang, n).strip("/"), "index.html")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(page(lang, n, tpl, date))
            made.append(path(lang, n))
    # ссылки «под бюджет» на главных
    for lang, (rate, lst) in BUD.items():
        f = os.path.join(ROOT, HOMEF[lang]); s = open(f, encoding="utf-8").read(); t = T[lang]
        short = lambda m: t["h1"].format(B=money(lang, m)).replace("Красивый инвентарь CS2", "Инвентарь").replace("Good-looking CS2 loadout", "Loadout").replace("Schönes CS2-Inventar", "Inventar").replace("Inventário bonito de CS2", "Inventário").replace(" altı güzel CS2 envanteri", " altı envanter").replace("Ładny ekwipunek CS2", "Ekwipunek")
        line = f'<p class="seo-budgets"><b>{e(t["budgets"])}:</b> ' + " · ".join(f'<a href="{path(lang, m)}">{e(short(m))}</a>' for m in lst) + "</p>"
        line += f'\n        <p class="seo-wiki"><a href="{WIKI[lang]}"><b>{e(WIKIL[lang])}</b></a></p>'
        s = re.sub(r'\s*<p class="seo-wiki">.*?</p>', "", s)
        if 'class="seo-budgets"' in s:
            s = re.sub(r'<p class="seo-budgets">.*?</p>', line, s, count=1, flags=re.S)
        else:
            s = s.replace('<ul class="seo-links" id="seoLinks">', line + '\n        <ul class="seo-links" id="seoLinks">', 1)
        open(f, "w", encoding="utf-8").write(s)
    # sitemap
    sm = os.path.join(ROOT, "sitemap.xml"); x = open(sm, encoding="utf-8").read()
    add = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for p in made if f"<loc>{SITE}{p}</loc>" not in x)
    x = x.replace("</urlset>", add + "</urlset>"); open(sm, "w", encoding="utf-8").write(x)
    print(len(made), "pages")


if __name__ == "__main__":
    main()
