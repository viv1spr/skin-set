# -*- coding: utf-8 -*-
"""Оценка инвентаря CS2 по ссылке на профиль Steam.
Запуск: python3 admin/inventory_page.py  → /ocenka-inventarya/ и /en/inventory-value/
Инвентарь — воркер auth.skin-set.com/invp (публичный инвентарь, кэш 15 мин).
Цены — prices-all.json (все предметы по market_hash_name, ветка prices) + prices.json (скины по качествам) как запасной вариант.
"""
import json, os, sys, html, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa
from pagegrid import GRID_CSS  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/ocenka-inventarya/", "en": "/en/inventory-value/"}
BUILDER = {"ru": "/", "en": "/en/"}
FLOAT = {"ru": "/float-kalkulyator-cs2/", "en": "/en/cs2-float-calculator/"}

T = {
 "ru": dict(
   title="Сколько стоит инвентарь CS2 — оценка инвентаря КС 2 по ссылке Steam",
   desc="Узнай, сколько стоит твой инвентарь CS2 (КС 2): вставь ссылку на профиль Steam — бесплатно посчитаем стоимость в рублях по живым ценам, покажем самые дорогие скины, ножи, перчатки и кейсы. Без входа и регистрации.",
   lead_s="Узнай стоимость инвентаря КС 2 в рублях по живым ценам площадок и посмотри самые дорогие скины. Бесплатно, без пароля.",
   h1="Сколько стоит инвентарь CS2", kick="Оценка инвентаря · бесплатно · без входа", home="Главная",
   lead="Вставь ссылку на профиль Steam, SteamID или ссылку на обмен — посчитаем стоимость инвентаря CS2 в рублях по живым ценам торговых площадок и покажем самые дорогие предметы. Входить в Steam не нужно: мы читаем только открытый инвентарь.",
   L=dict(ph="Ссылка на профиль Steam или SteamID", go="Оценить", wait="Считаем инвентарь…", total="Стоимость инвентаря", items="предметов", valued="оценено",
          unv="Без цены: {n} — обычно это медали, значки и предметы, которые нельзя продать", top="Самые дорогие предметы", all="Весь инвентарь", show="Показать все {n}",
          cats={"knife": "Ножи", "gloves": "Перчатки", "skin": "Скины оружия", "case": "Кейсы и капсулы", "sticker": "Наклейки", "agent": "Агенты", "other": "Другое"},
          priv="Инвентарь закрыт. В Steam: профиль → Редактировать профиль → Приватность → «Инвентарь: открытый», затем попробуй снова через пару минут.",
          nf="Профиль не найден. Проверь ссылку: подойдёт steamcommunity.com/id/ник, steamcommunity.com/profiles/7656… или ссылка на обмен.",
          empty="В инвентаре нет предметов CS2, которые можно оценить.", many="Слишком много проверок подряд. Подожди 10 минут и попробуй снова.",
          err="Steam сейчас не отвечает. Попробуй ещё раз через минуту.", bad="Вставь ссылку на профиль Steam или SteamID64",
          src="Цены — минимальные на торговых площадках (Lis-Skins, Skinport), обновляются каждые 5 минут. В Steam цены обычно на 15–30% выше из-за комиссии.",
          cta="Собрать сет в цвет твоего ножа", cta2="Подберём оружие, перчатки и агента под цвет — в пределах бюджета", buy="Купить", share="Ссылка на оценку скопирована",
          copy="Скопировать ссылку", qty="шт.", est="≈", steam="Войти через Steam", steam2="и сразу оценить свой инвентарь", mine="Оценить мой инвентарь", or_="или по ссылке на профиль", other="Проверить другой профиль", trust=["Бесплатно", "Без пароля и API-ключа", "Цены каждые 5 минут"], ex="Пример оценки", exi="нож, перчатки и AK-47", exn="Инвентарь игрока", steps_h="Как это работает", steps=[("Войди или вставь ссылку", "Steam-вход или ссылка на любой открытый профиль"), ("Считаем по живым ценам", "Каждый предмет — по минимальной цене на площадках"), ("Смотри и собирай сет", "Топ дорогих скинов и сет в цвет твоего ножа")], more_h="Подробнее об оценке инвентаря"),
   sec=[
    ("Как узнать стоимость инвентаря CS2", "1. Открой свой профиль в Steam и скопируй адрес страницы — например, steamcommunity.com/id/nickname или steamcommunity.com/profiles/76561198… 2. Вставь ссылку в поле выше и нажми «Оценить». 3. Через несколько секунд увидишь общую стоимость инвентаря КС 2 в рублях, сколько предметов оценено и какие скины самые дорогие. Подходит и ссылка на обмен (trade link), и просто ник из адреса профиля. Можно проверить и чужой инвентарь — если он открыт."),
    ("Где взять ссылку на профиль Steam", "В клиенте Steam нажми на свой ник → «Профиль», затем правой кнопкой по пустому месту страницы → «Скопировать адрес». В браузере ссылка видна в адресной строке. SteamID64 — 17 цифр, начинается с 7656119; его показывает адрес профиля, если ты не задавал свой ник. Ссылку на обмен найдёшь в Steam: Инвентарь → Предложения обмена → «Кто может отправлять мне предложения обмена»."),
    ("Как открыть инвентарь, если он скрыт", "Если видишь «Инвентарь закрыт», зайди в Steam: профиль → «Редактировать профиль» → «Настройки приватности» и поставь «Инвентарь: открытый». Основной профиль тоже должен быть открытым. Steam применяет настройку не сразу — подожди пару минут. Открытый инвентарь безопасен: другие видят предметы, но забрать их без твоего подтверждения в Steam Guard нельзя."),
    ("Как считается стоимость", "Для каждого предмета берём минимальную цену продажи на крупных торговых площадках — Lis-Skins и Skinport — с учётом качества (Factory New, Minimal Wear, Field-Tested, Well-Worn, Battle-Scarred), StatTrak и сувенирных версий. Цены обновляются каждые 5 минут. Учитываются ножи, перчатки, скины оружия, кейсы, капсулы, наклейки, агенты, нашивки и граффити. Предметы в трейд-бане тоже считаются — продать их можно после окончания блокировки."),
    ("Почему стоимость отличается от Steam и других сервисов", "Торговая площадка Steam берёт комиссию 15%, а деньги с неё нельзя вывести, поэтому цены там обычно на 15–30% выше, чем на сторонних площадках. Сервисы, которые выкупают скины моментально, наоборот, платят на 10–40% меньше рынка. Мы показываем рыночную цену — столько стоит такой же предмет у самого дешёвого продавца прямо сейчас."),
    ("Что не входит в оценку", "Оценка не учитывает наклейки, вклеенные в оружие, точный float и редкие паттерны (например, Blue Gem у Case Hardened или фазы Doppler: Ruby, Sapphire и Emerald стоят в разы дороже обычных). Такие предметы оцениваются по цене обычной версии, поэтому реальная стоимость может быть выше. Узнать качество по float поможет [калькулятор float](" + FLOAT["ru"] + ")."),
    ("Что делать дальше", "Знаешь стоимость — можно собрать из инвентаря цельный сет. В [конструкторе Skinset](/) выбери цвет своего ножа или перчаток, и мы подберём к ним оружие и агента той же гаммы в пределах бюджета. Дешёвые варианты на разные суммы — в подборках «[инвентарь CS2 за 5000 рублей](/inventar-cs2-za-5000-rubley/)» и «[за 30000 рублей](/inventar-cs2-za-30000-rubley/)»."),
   ],
   faq=[("Это бесплатно и безопасно?", "Да. Оценка бесплатная, вход через Steam не нужен: мы читаем только открытый инвентарь по ссылке, как любой посетитель твоего профиля. Пароль, Steam Guard и API-ключ никогда не нужны — если сайт их просит, это мошенники."),
        ("Почему пишет, что инвентарь закрыт?", "В настройках приватности Steam инвентарь скрыт. Поставь «Инвентарь: открытый» в разделе «Настройки приватности» профиля и подожди пару минут."),
        ("Можно ли узнать стоимость чужого инвентаря?", "Да, если у человека открыт профиль и инвентарь: вставь ссылку на его профиль Steam."),
        ("Как часто обновляются цены?", "Цены на площадках обновляются каждые 5 минут, сам инвентарь кэшируется на 15 минут — новые предметы появятся в оценке примерно через четверть часа."),
        ("Учитываются ли наклейки и float?", "Наклейки на оружии и точный float — нет: предмет оценивается по минимальной цене его качества. Отдельные наклейки в инвентаре учитываются."),
        ("Сколько стоит средний инвентарь CS2?", "У большинства игроков инвентарь стоит от нескольких сотен до нескольких тысяч рублей — основную стоимость обычно дают нож и перчатки. Один нож почти всегда дороже всех остальных скинов вместе."),
        ("Почему у меня оценено не всё?", "Медали, значки за операции, монеты и подарочные предметы нельзя продать, поэтому у них нет цены. Также могут не оцениться очень редкие предметы, которых сейчас никто не продаёт.")],
   faq_h="Вопросы и ответы", note="Skinset не связан с Valve и Steam. Цены — ориентир по торговым площадкам, не предложение о покупке."),
 "en": dict(
   title="CS2 Inventory Value Checker — How Much Is My CS2 Inventory Worth?",
   desc="Free CS2 inventory value checker: paste your Steam profile link to see what your CS2 inventory is worth at live market prices, plus your most expensive skins, knives, gloves and cases. No login needed.",
   lead_s="See what your CS2 inventory is worth at live marketplace prices, plus your most valuable skins. Free, no password.",
   h1="CS2 inventory value", kick="Inventory value · free · no login", home="Home",
   lead="Paste a Steam profile link, SteamID or trade link to see what your CS2 inventory is worth at live marketplace prices and which items are the most valuable. No Steam login: we only read the public inventory.",
   L=dict(ph="Steam profile link or SteamID", go="Check value", wait="Checking inventory…", total="Inventory value", items="items", valued="priced",
          unv="No price: {n}, usually medals, coins and items that can't be sold", top="Most valuable items", all="Full inventory", show="Show all {n}",
          cats={"knife": "Knives", "gloves": "Gloves", "skin": "Weapon skins", "case": "Cases & capsules", "sticker": "Stickers", "agent": "Agents", "other": "Other"},
          priv="This inventory is private. In Steam: Profile → Edit Profile → Privacy Settings → Inventory: Public, then try again in a couple of minutes.",
          nf="Profile not found. Use steamcommunity.com/id/name, steamcommunity.com/profiles/7656… or a trade link.",
          empty="No CS2 items that can be priced.", many="Too many checks in a row. Wait 10 minutes and try again.",
          err="Steam isn't responding right now. Try again in a minute.", bad="Paste a Steam profile link or SteamID64",
          src="Prices are the lowest marketplace listings (Lis-Skins, Skinport), refreshed every 5 minutes. Steam Market prices are usually 15–30% higher because of fees.",
          cta="Build a set to match your knife", cta2="We'll match weapons, gloves and an agent to its color, within budget", buy="Buy", share="Link copied",
          copy="Copy link", qty="pcs", est="≈", steam="Sign in through Steam", steam2="and check your own inventory instantly", mine="Check my inventory", or_="or paste a profile link", other="Check another profile", trust=["Free", "No password or API key", "Prices every 5 min"], ex="Example result", exi="knife, gloves and AK-47", exn="Player inventory", steps_h="How it works", steps=[("Sign in or paste a link", "Steam sign-in or a link to any public profile"), ("We price every item", "Lowest live marketplace price per item"), ("See it and build a set", "Top items and a set to match your knife")], more_h="More about inventory value"),
   sec=[
    ("How to check your CS2 inventory value", "1. Open your Steam profile and copy the page address, e.g. steamcommunity.com/id/nickname or steamcommunity.com/profiles/76561198… 2. Paste it above and press “Check value”. 3. In a few seconds you'll see the total value of your CS2 inventory, how many items were priced and which skins are worth the most. Trade links and vanity names work too, and you can check anyone's inventory as long as it's public."),
    ("Where to find your Steam profile link", "In the Steam client click your name → Profile, then right-click an empty spot → Copy Page URL. In a browser it's in the address bar. A SteamID64 is 17 digits starting with 7656119. Your trade link is under Inventory → Trade Offers → Who can send me trade offers."),
    ("How to make your inventory public", "If you see “inventory is private”, go to Steam: Profile → Edit Profile → Privacy Settings and set Inventory to Public (your profile must be public too). Steam takes a couple of minutes to apply it. A public inventory is safe: people can see your items but can't take them without your Steam Guard confirmation."),
    ("How the value is calculated", "Each item is priced at the lowest current listing on major marketplaces (Lis-Skins and Skinport), by exact wear (Factory New to Battle-Scarred), StatTrak and Souvenir versions. Prices refresh every 5 minutes. Knives, gloves, weapon skins, cases, capsules, stickers, agents, patches and graffiti all count, including items on trade hold."),
    ("Why it differs from Steam and other checkers", "The Steam Community Market takes a 15% fee and its balance can't be withdrawn, so prices there are usually 15–30% higher than on third-party marketplaces. Instant-sell services pay 10–40% below market. We show the market price: what the same item costs from the cheapest seller right now."),
    ("What isn't included", "Applied stickers, exact float and rare patterns (Case Hardened blue gems, Doppler phases: Ruby, Sapphire and Emerald are worth several times more) aren't priced separately; such items are valued as the regular version, so the real value can be higher. Use our [float calculator](" + FLOAT["en"] + ") to check wear by float."),
    ("What next", "Once you know your inventory's value, turn it into a matching loadout: in the [Skinset builder](/en/) pick your knife or gloves color and we'll match weapons and an agent in the same palette within your budget."),
   ],
   faq=[("Is it free and safe?", "Yes. It's free and needs no Steam login: we only read the public inventory, like any visitor to your profile. No site ever needs your password, Steam Guard code or API key to check a value; if one asks, it's a scam."),
        ("Why does it say my inventory is private?", "Your Steam privacy settings hide it. Set Inventory to Public under Privacy Settings and wait a couple of minutes."),
        ("Can I check someone else's inventory?", "Yes, if their profile and inventory are public: paste their Steam profile link."),
        ("How often are prices updated?", "Marketplace prices refresh every 5 minutes; the inventory itself is cached for 15 minutes."),
        ("Are stickers and float included?", "Applied stickers and exact float aren't; each item is valued at the lowest price for its wear. Loose stickers in the inventory are counted."),
        ("Why weren't all my items priced?", "Medals, operation coins, badges and gifts can't be sold, so they have no price. Very rare items with no current listings may also be unpriced.")],
   faq_h="FAQ", note="Skinset is not affiliated with Valve or Steam. Prices are a marketplace guide, not an offer to buy."),
}

CSS = """.iv{max-width:1120px}.iv-hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:34px;align-items:center;margin:6px 0 26px}
.iv-hero .pg-h{margin-bottom:10px}.iv-hero .pg-l{max-width:520px;margin-bottom:0}
.iv-tool{margin-top:22px;background:linear-gradient(180deg,#17171f,#121218);border:1px solid var(--line,#26262f);padding:20px;position:relative}
.iv-tool::before{content:"";position:absolute;left:0;top:0;width:44px;height:3px;background:var(--pick,#c4161c)}
.iv-st{display:flex;align-items:center;gap:14px;width:100%;box-sizing:border-box;padding:14px 18px;background:linear-gradient(90deg,#1b2838,#2a475e);border:1px solid #3d6c8d;color:#fff;text-decoration:none;cursor:pointer;font:inherit;text-align:left}
.iv-st:hover{border-color:#66c0f4}.iv-st svg{width:30px;height:30px;flex:none}.iv-st img{width:40px;height:40px;flex:none;border:1px solid #66c0f4}.iv-st b{display:block;font:700 1rem/1.2 var(--hud);letter-spacing:.06em;text-transform:uppercase}.iv-st small{color:#a9c6db;font-size:.82rem}.iv-st i{margin-left:auto;font-style:normal;font-size:1.3rem;color:#66c0f4}
.iv-or{display:flex;align-items:center;gap:12px;margin:16px 0 12px;font:600 .7rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--soft,#888)}.iv-or::before,.iv-or::after{content:"";flex:1;height:1px;background:var(--line,#26262f)}
.iv-form{display:flex;gap:8px}.iv-form input{flex:1;min-width:0;height:48px;padding:0 14px;background:#0d0d12;border:1px solid var(--line2,#33333d);color:#fff;font:500 .98rem/1 var(--body,inherit)}
.iv-form input:focus{outline:none;border-color:var(--pick,#c4161c)}.iv-form button{height:48px;padding:0 22px;background:var(--pick,#c4161c);border:0;color:#fff;font:700 .92rem/1 var(--hud);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;clip-path:polygon(9px 0,100% 0,calc(100% - 9px) 100%,0 100%)}
.iv-form button:disabled{opacity:.6;cursor:wait}.iv-trust{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:14px;font-size:.78rem;color:var(--soft,#999)}.iv-trust span::before{content:"✓";color:#2ecc71;margin-right:6px}
.iv-msg{min-height:0;font-size:.9rem;color:var(--soft,#aaa);margin-top:10px}.iv-msg:empty{display:none}.iv-msg.bad{color:#ff8a80}
.iv-hero{align-items:stretch}.iv-pvw{position:relative;min-height:440px}
.iv-pv{position:absolute;inset:0;display:flex;flex-direction:column;background:linear-gradient(180deg,#17171f,#111117);border:1px solid var(--line,#26262f);padding:20px 22px 16px;box-shadow:0 30px 60px rgba(0,0,0,.45)}
.iv-pv::before{content:"";position:absolute;left:0;top:0;width:44px;height:3px;background:var(--pick,#c4161c)}
.iv-pv .hd{display:flex;justify-content:space-between;align-items:center;gap:10px;font:600 .66rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--soft,#999)}
.iv-pv .who{display:flex;align-items:center;gap:8px;font:600 .82rem/1.2 var(--body,inherit);letter-spacing:0;text-transform:none;color:#fff;min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}.iv-pv .who img{width:26px;height:26px;border:1px solid var(--line2,#33333d)}.iv-pv .cn{letter-spacing:.06em;white-space:nowrap}
.iv-pv .tot{font:700 2.5rem/1 var(--hud);color:#fff;margin:12px 0 14px}.iv-pv .bar{display:flex;height:6px;gap:2px;flex:none}.iv-pv .bar i{display:block;height:100%;min-width:3px}
.iv-pv .lg{display:flex;flex-wrap:wrap;gap:4px 14px;margin:9px 0 10px;font-size:.74rem;color:var(--soft,#aaa)}.iv-pv .lg b{color:#fff;font-weight:600}.iv-pv .lg span::before{content:"";display:inline-block;width:8px;height:8px;margin-right:6px;background:var(--c)}
.iv-pv .rows{flex:1;min-height:0;overflow-y:auto;margin:0 -10px;padding:0 10px;scrollbar-width:thin;scrollbar-color:#33333d transparent}
.iv-pv .row{display:flex;align-items:center;gap:12px;padding:7px 0;border-top:1px solid var(--line,#26262f)}.iv-pv .row img,.iv-pv .row .ph{width:72px;height:54px;object-fit:contain;flex:none;font-size:0}.iv-pv .row .ph{background:#101017}
.iv-pv .row div{flex:1;min-width:0}.iv-pv .row b{display:block;font-size:.88rem;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.iv-pv .row small{display:block;font-size:.73rem;color:var(--soft,#999);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.iv-pv .pr{text-align:right;flex:none}.iv-pv .pr em{display:block;font-style:normal;font-weight:700;color:#2ecc71;font-size:.92rem;white-space:nowrap}.iv-pv .pr i{font-style:normal;color:var(--soft,#777)}.iv-pv .pr a{font-size:.72rem;color:#ff5cb0}
.iv-pv .iv-cta{margin-top:10px;flex:none;padding:12px 16px}.iv-pv .iv-cta b{font-size:.9rem}.iv-pv .iv-src{margin:10px 0 4px;font-size:.7rem;line-height:1.4}
.iv-pv.busy .tot,.iv-pv.busy .rows,.iv-pv.busy .bar{opacity:.35;transition:opacity .2s}.iv-pv.busy .hd{color:#fff}
.iv-res{margin:0 0 30px;scroll-margin-top:80px}.iv-res[hidden]{display:none}.iv-sum{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;background:var(--panel,#14141b);border:1px solid var(--line,#26262f);padding:18px}
.iv-sum img{width:64px;height:64px;border:1px solid var(--line2,#33333d)}.iv-sum .nm{font-size:.9rem;color:var(--soft,#aaa)}.iv-sum .tt{font:700 2.4rem/1.05 var(--hud);color:#fff;margin:4px 0}.iv-sum .tt small{font-size:.86rem;color:var(--soft,#aaa);font-family:var(--body,inherit);font-weight:500;margin-left:8px}
.iv-sum .ag{background:none;border:1px solid var(--line2,#33333d);color:#fff;padding:9px 14px;cursor:pointer;font:600 .74rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase}
.iv-cats{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-top:8px}.iv-cats div{background:#101017;border:1px solid var(--line,#26262f);padding:10px 12px}.iv-cats b{display:block;font:700 1.05rem/1.2 var(--hud);color:#fff}.iv-cats span{font-size:.76rem;color:var(--soft,#aaa)}
.iv-cta{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-top:8px;padding:14px 18px;background:linear-gradient(90deg,rgba(196,22,28,.2),rgba(196,22,28,.04));border:1px solid rgba(196,22,28,.45);color:#fff;text-decoration:none}.iv-cta b{display:block;font:700 1rem/1.2 var(--hud);text-transform:uppercase;letter-spacing:.04em}.iv-cta small{color:var(--soft,#bbb)}.iv-cta i{font-style:normal;font-size:1.4rem}
.iv-res h3{margin:22px 0 10px;font:700 .8rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--soft,#aaa)}.iv-l{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px}.iv-it{display:flex;gap:10px;align-items:center;background:var(--panel,#14141b);border:1px solid var(--line,#26262f);padding:8px 10px;min-width:0}
.iv-it img{font-size:0;color:transparent}.iv-it img,.iv-it .ph{width:72px;height:54px;object-fit:contain;flex:none}.iv-it .ph{background:#101017}.iv-it div{min-width:0;flex:1}.iv-it b{display:block;font-size:.86rem;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.iv-it small{display:block;font-size:.74rem;color:var(--soft,#999);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.iv-it em{font-style:normal;font-weight:700;color:#2ecc71;font-size:.9rem}.iv-it a{font-size:.74rem;color:#ff5cb0;margin-left:6px}.iv-it.k{border-color:rgba(228,174,57,.45)}
.iv-more{margin-top:10px;background:none;border:1px solid var(--line2,#33333d);color:#fff;padding:10px 16px;cursor:pointer;font:600 .8rem/1 var(--hud);letter-spacing:.06em;text-transform:uppercase}.iv-src{margin-top:12px;font-size:.76rem;color:var(--soft,#888)}
.iv-how{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:8px 0 34px;counter-reset:s}.iv-how div{background:var(--panel,#14141b);border:1px solid var(--line,#26262f);padding:16px 18px;counter-increment:s}.iv-how div::before{content:"0" counter(s);display:block;font:700 1.5rem/1 var(--hud);color:var(--pick,#c4161c);margin-bottom:8px}.iv-how b{display:block;font:700 .95rem/1.25 var(--hud);text-transform:uppercase;letter-spacing:.03em;color:#fff}.iv-how span{font-size:.84rem;color:var(--soft,#aaa)}
.iv-sh{font:700 .8rem/1 var(--hud)!important;letter-spacing:.14em;text-transform:uppercase;color:var(--soft,#aaa)!important;margin:0 0 12px!important}.iv-sh::before,.iv-sh::after{display:none!important}
.iv-acc{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:34px;align-items:start}.iv-acc details{background:var(--panel,#14141b);border:1px solid var(--line,#26262f)}.iv-acc summary{list-style:none;cursor:pointer;padding:14px 44px 14px 16px;position:relative}.iv-acc summary::-webkit-details-marker{display:none}
.iv-acc summary::after{content:"+";position:absolute;right:16px;top:50%;transform:translateY(-50%);font-size:1.3rem;color:var(--soft,#888)}.iv-acc details[open] summary::after{content:"−"}
.iv-acc summary h2,.iv-acc summary h3{margin:0!important;padding:0!important;font:600 .98rem/1.3 var(--body,inherit)!important;letter-spacing:0!important;text-transform:none!important;color:#fff}.iv-acc summary h2::before,.iv-acc summary h2::after{display:none!important}
.iv-acc .bd{padding:0 16px 14px;font-size:.9rem;line-height:1.6;color:var(--soft,#bbb)}.iv-acc .bd p{margin:0}.iv-acc .bd ol{margin:0;padding-left:20px}.iv-acc .bd li{margin:3px 0}
@media(max-width:900px){.iv-hero{grid-template-columns:1fr;gap:16px}.iv-pvw{min-height:0;display:none}.iv-pvw:has(.has){display:block}.iv-pv{position:relative;inset:auto;height:72vh;scroll-margin-top:70px}.iv-how{grid-template-columns:1fr}.iv-acc{grid-template-columns:1fr}}
@media(max-width:760px){.iv-tool{padding:14px}.iv-form{flex-direction:column}.iv-form input{flex:none}.iv-form button{width:100%}.iv-sum{grid-template-columns:auto 1fr;gap:12px}.iv-sum .ag{grid-column:1/-1}.iv-sum img{width:48px;height:48px}.iv-sum .tt{font-size:1.9rem}.iv-cats{grid-template-columns:1fr 1fr}.iv-l{grid-template-columns:1fr}.iv-cta{padding:12px 14px}}"""

JS = r"""(function(){var L=window.IVL,RATE=window.IVRATE,CUR=window.IVCUR,API="https://auth.skin-set.com/invp?id=";
var W={"Factory New":"FN","Minimal Wear":"MW","Field-Tested":"FT","Well-Worn":"WW","Battle-Scarred":"BS"};
function fmt(usd){var v=usd*RATE;return CUR==="₽"?Math.round(v).toLocaleString("ru-RU")+" ₽":"$"+(v<100?v.toFixed(2):Math.round(v).toLocaleString("en-US"))}
function esc(t){return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;")}
var f=document.getElementById("ivF"),inp=document.getElementById("ivI"),btn=f.querySelector("button"),msg=document.getElementById("ivM");
var ALL=null,P=null,IMG=null,t5=Math.floor(Date.now()/300000);
function j(u){return fetch(u).then(function(r){if(!r.ok)throw 0;return r.json()})}
var RAW="https://raw.githubusercontent.com/viv1spr/skin-set/prices/";
var prices=Promise.all([j(RAW+"prices-all.json?t="+t5).catch(function(){return j("/data/prices-all.json").catch(function(){return null})}),j(RAW+"prices.json?t="+t5).catch(function(){return j("/data/prices.json").catch(function(){return {}})}),j("/data/skin-img.json").catch(function(){return []})]).then(function(a){ALL=a[0]||{};P=a[1]||{};IMG={};(a[2]||[]).forEach(function(x){IMG[x[0].replace(/^★\s*/,"")]=x[1]})});
/* ссылка на обмен → SteamID64 */
function norm(s){s=String(s||"").trim();var m=s.match(/[?&]partner=(\d+)/);if(m){try{return (BigInt(m[1])+76561197960265728n).toString()}catch(e){}}s=s.replace(/[?#].*$/,"").replace(/\/(inventory|home|games)\/?.*$/i,"").replace(/\/+$/,"");return s}
function cat(n){if(/^★/.test(n))return /Gloves|Hand Wraps/.test(n)?"gloves":"knife";if(/^Sticker \|/.test(n))return "sticker";if(/ Case$| Capsule$|Package$|Case Key$| Pass$|^Sealed Graffiti|Terminal$/.test(n))return /Graffiti/.test(n)?"other":"case";if(/ \| .*\((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/.test(n))return "skin";if(/ \| /.test(n)&&!/^(Patch|Music Kit|Charm|Sealed Graffiti)/.test(n))return "agent";return "other"}
function price(n){var k=n.replace(/^★\s*/,"");if(ALL[k])return ALL[k];var m=k.match(/^(StatTrak™ |Souvenir )?(.+?) \((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/);if(!m||/^Souvenir/.test(m[1]||""))return 0;var r=P[m[2]]||P[m[2]+" (Phase 2)"];if(!r)return 0;var w=W[m[3]];return m[1]?((r.stw||{})[w]||0):((r.w||{})[w]||0)}
function base(n){return n.replace(/^★\s*/,"").replace(/^(StatTrak™ |Souvenir )/,"").replace(/ \((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/,"")}
function img(n){var b=base(n);return IMG&&(IMG[b]||IMG[b+" (Phase 2)"])}
function card(x){var im=img(x.n),parts=x.n.replace(/^★\s*/,"").split(" | "),wm=x.n.match(/\(([^)]+)\)$/);var q=encodeURIComponent(x.n.replace(/^★\s*/,""));
 return '<div class="iv-it'+(x.c==="knife"||x.c==="gloves"?" k":"")+'">'+(im?'<img src="https://community.akamai.steamstatic.com/economy/image/'+im+'/96fx72f" alt="'+esc(x.n)+'" loading="lazy">':'<span class="ph"></span>')+'<div><b>'+esc(parts[1]?parts[1].replace(/ \([^)]*\)$/,""):parts[0])+'</b><small>'+esc([parts[1]?parts[0]:"",wm&&W[wm[1]]?W[wm[1]]:"",x.q>1?x.q+" "+L.qty:""].filter(Boolean).join(" · "))+'</small>'+(x.p?'<em>'+fmt(x.p*x.q)+'</em>':'<small>—</small>')+(x.p&&(x.c==="knife"||x.c==="gloves"||x.c==="skin")?'<a href="https://cs.money/market/buy/?search='+q+'&utm_source=mediabuy&utm_medium=skin-set&utm_campaign=market&utm_content=inventory" target="_blank" rel="noopener sponsored">'+L.buy+'</a>':'')+'</div></div>'}
function say(t,bad){msg.textContent=t||"";msg.className="iv-msg"+(bad?" bad":"")}
var pv=document.getElementById("ivPv"),COL={knife:"#e4ae39",skin:"#c4161c",gloves:"#4f7bff",case:"#2ecc71",sticker:"#b05cff",agent:"#ff8a3d",other:"#6b6b78"};
function row(x){var im=img(x.n),parts=x.n.replace(/^★\s*/,"").split(" | "),wm=x.n.match(/\(([^)]+)\)$/),q=encodeURIComponent(x.n.replace(/^★\s*/,""));
 var nm=parts[1]?parts[1].replace(/ \([^)]*\)$/,""):parts[0],sub=[parts[1]?parts[0]:"",wm&&W[wm[1]]?W[wm[1]]:"",x.q>1?x.q+" "+L.qty:""].filter(Boolean).join(" · ");
 var buy=x.p&&(x.c==="knife"||x.c==="gloves"||x.c==="skin");
 return '<div class="row">'+(im?'<img src="https://community.akamai.steamstatic.com/economy/image/'+im+'/152fx114f" alt="" loading="lazy">':'<span class="ph"></span>')+'<div><b>'+esc(nm)+'</b><small>'+esc(sub)+'</small></div><span class="pr">'+(x.p?'<em>'+fmt(x.p*x.q)+'</em>':'<i>—</i>')+(buy?'<a href="https://cs.money/market/buy/?search='+q+'&utm_source=mediabuy&utm_medium=skin-set&utm_campaign=market&utm_content=inventory" target="_blank" rel="noopener sponsored">'+L.buy+'</a>':'')+'</span></div>'}
function run(id){id=norm(id);if(!id||id.length<2){say(L.bad,1);return}btn.disabled=true;say("");pv.classList.add("busy");pv.querySelector(".hd").firstChild.textContent=L.wait;
 Promise.all([fetch(API+encodeURIComponent(id)).then(function(r){return r.json().catch(function(){return{}}).then(function(d){d._s=r.status;return d})}),prices]).then(function(a){var d=a[0];btn.disabled=false;pv.classList.remove("busy");
  function fail(t){say(t,1);pv.querySelector(".hd").firstChild.textContent=pv.classList.contains("has")?L.total:L.ex}
  if(d._s===429)return fail(L.many);if(d._s===404||d.error==="profile")return fail(L.nf);if(d.private)return fail(L.priv);if(d.error)return fail(L.err);
  var it=(d.items||[]).map(function(z){var n=z[0],q=z[1]||1;return{n:n,q:q,p:price(n),c:cat(n)}});if(!it.length)return fail(L.empty);
  it.sort(function(x,y){return y.p*y.q-x.p*x.q});var tot=0,cnt=0,vc=0,un=0,C={};it.forEach(function(x){cnt+=x.q;if(x.p){tot+=x.p*x.q;vc+=x.q;C[x.c]=(C[x.c]||0)+x.p*x.q}else un+=x.q});
  var ks=Object.keys(L.cats).filter(function(k){return C[k]}).sort(function(a,b){return C[b]-C[a]});
  var bar=ks.map(function(k){return '<i style="width:'+(C[k]/tot*100).toFixed(1)+'%;background:'+COL[k]+'" title="'+L.cats[k]+'"></i>'}).join("");
  var lg=ks.map(function(k){return '<span style="--c:'+COL[k]+'">'+L.cats[k]+' <b>'+fmt(C[k])+'</b></span>'}).join("");
  var kn=it.filter(function(x){return x.c==="knife"&&x.p})[0],gl=it.filter(function(x){return x.c==="gloves"&&x.p})[0];var setq=[kn,gl].filter(Boolean).map(function(x){return base(x.n).replace(" | ","|")}).join(";");
  pv.innerHTML='<div class="hd"><span class="who">'+(d.a?'<img src="'+esc(d.a)+'" alt="">':'')+esc(d.n||d.sid||"")+'</span><span class="cn">'+cnt+' '+L.items+(un?' · '+vc+' '+L.valued:'')+'</span></div>'
   +'<div class="tot">'+fmt(tot)+'</div><div class="bar">'+bar+'</div><div class="lg">'+lg+'</div>'
   +'<div class="rows">'+it.map(row).join("")+'<p class="iv-src">'+L.src+'</p></div>'
   +'<a class="iv-cta" href="'+window.IVB+(setq?'?set='+encodeURIComponent(setq):'')+'"><b>'+L.cta+'</b><i>→</i></a>';
  pv.classList.add("has");say("");if(innerWidth<900){try{pv.scrollIntoView({behavior:"smooth",block:"start"})}catch(e){}}
  try{if(!ME||ME.sid!==d.sid)history.replaceState(null,"","?id="+encodeURIComponent(d.sid||id))}catch(e){}
 }).catch(function(){btn.disabled=false;pv.classList.remove("busy");say(L.err,1)})}
f.addEventListener("submit",function(ev){ev.preventDefault();run(inp.value)});
/* вход через Steam: токен кладёт общий скрипт шапки в localStorage skinset_steam */
var stb=document.getElementById("ivSt"),ME=null,tok=null;try{tok=localStorage.getItem("skinset_steam")}catch(e){}
stb.href="https://auth.skin-set.com/login?r="+encodeURIComponent(location.origin+location.pathname);
function meBtn(){stb.innerHTML=(ME.a?'<img src="'+esc(ME.a)+'" alt="">':'')+'<span><b>'+L.mine+'</b><small>'+esc(ME.n||"")+'</small></span><i>→</i>';stb.removeAttribute("href");stb.setAttribute("role","button");stb.onclick=function(ev){ev.preventDefault();inp.value="";run(ME.sid)}}
var q=new URLSearchParams(location.search).get("id");
if(tok){fetch("https://auth.skin-set.com/me?t="+encodeURIComponent(tok)).then(function(r){return r.ok?r.json():null}).then(function(d){if(d&&d.sid){ME=d;meBtn();if(!q)run(d.sid)}}).catch(function(){})}
if(q){inp.value=q;run(q)}})()"""


def mdlinks(s):
    s = e(s)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)


IMGS = {x[0].replace("★ ", ""): x[1] for x in json.load(open(os.path.join(ROOT, "data/skin-img.json")))}


def build(lang):
    t = T[lang]; L = t["L"]; url = URL[lang]
    rate, cur = (90, "₽") if lang == "ru" else (1, "$")
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": t["h1"], "url": SITE + url, "description": t["desc"], "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
           "inLanguage": lang, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
          {"@context": "https://schema.org", "@type": "HowTo", "name": t["sec"][0][0], "step": [{"@type": "HowToStep", "text": x.strip()} for x in re.split(r"\d\. ", t["sec"][0][1]) if x.strip()]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": t["home"], "item": SITE + HOME[lang]}, {"@type": "ListItem", "position": 2, "name": t["h1"], "item": SITE + url}]}]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'

    def para(h, p):
        if re.match(r"1\. ", p):
            steps = [x.strip() for x in re.split(r"\d\. ", p) if x.strip()]
            m = re.match(r"(.+?\.)\s+(.+)$", steps[-1]); tail = ""
            if m: steps[-1], tail = m.group(1), m.group(2)
            inner = "<ol>" + "".join(f"<li>{mdlinks(x)}</li>" for x in steps) + "</ol>" + (f"<p>{mdlinks(tail)}</p>" if tail else "")
        else:
            inner = f"<p>{mdlinks(p)}</p>"
        return f'<details><summary><h2>{e(h)}</h2></summary><div class="bd">{inner}</div></details>'
    secs = "".join(para(h, p) for h, p in t["sec"])
    faqs = "".join(f'<details><summary><h3>{e(q)}</h3></summary><div class="bd"><p>{e(a)}</p></div></details>' for q, a in t["faq"])
    I = "https://community.akamai.steamstatic.com/economy/image/{}/152fx114f"
    EXI = [("Karambit | Fade", "FN", 1403.96), ("Sport Gloves | Vice", "FT", 311.86), ("AK-47 | Fire Serpent", "FT", 615.34)]
    def money(v):
        v = v * rate
        return f"{round(v):,}".replace(",", " ") + " ₽" if cur == "₽" else f"${round(v):,}"
    tot = sum(x[2] for x in EXI)
    rows = "".join(f'<div class="row"><img src="{I.format(IMGS[n])}" alt="" width="76" height="57"><div><b>{e(n.split(" | ")[1])}</b><small>{e(n.split(" | ")[0])} · {w}</small></div><span class="pr"><em>{money(v)}</em></span></div>' for n, w, v in EXI if n in IMGS)
    cats = [(L["cats"]["knife"], 1403.96, "#e4ae39"), (L["cats"]["skin"], 615.34, "#c4161c"), (L["cats"]["gloves"], 311.86, "#4f7bff")]
    bar = "".join(f'<i style="width:{v/tot*100:.1f}%;background:{c}"></i>' for _, v, c in cats)
    lg = "".join(f'<span style="--c:{c}">{e(k)}</span>' for k, _, c in cats)
    pv = f'<div class="hd">{e(L["ex"])}<span class="cn">{e(L["exi"])}</span></div><div class="tot">{money(tot)}</div><div class="bar">{bar}</div><div class="lg">{lg}</div><div class="rows">{rows}</div>'
    SV = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-9.96 9.17l5.35 2.21a2.8 2.8 0 0 1 1.6-.5h.16l2.38-3.45v-.05a3.77 3.77 0 1 1 3.77 3.77h-.09l-3.4 2.42v.13a2.83 2.83 0 0 1-5.62.47L2.4 14.7A10 10 0 1 0 12 2Zm-4.72 15.2-1.23-.51a2.13 2.13 0 1 0 1.17-2.92l1.27.53a1.57 1.57 0 1 1-1.2 2.9Zm9.5-7.3a2.51 2.51 0 1 0-2.5 2.52 2.52 2.52 0 0 0 2.5-2.52Zm-4.39 0a1.89 1.89 0 1 1 1.89 1.89 1.89 1.89 0 0 1-1.89-1.89Z"/></svg>'
    body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav>'
            f'<section class="iv-hero"><div><span class="pg-eb"><i></i>{e(t["kick"])}</span><h1 class="pg-h">{e(t["h1"])}</h1><p class="lead pg-l">{e(t["lead_s"])}</p>'
            f'<div class="iv-tool"><a class="iv-st" id="ivSt" href="https://auth.skin-set.com/login">{SV}<span><b>{e(L["steam"])}</b><small>{e(L["steam2"])}</small></span><i>→</i></a>'
            f'<div class="iv-or">{e(L["or_"])}</div>'
            f'<form class="iv-form" id="ivF" autocomplete="off"><input id="ivI" name="id" type="text" inputmode="url" spellcheck="false" placeholder="{e(L["ph"])}" aria-label="{e(L["ph"])}"><button type="submit">{e(L["go"])}</button></form>'
            f'<div class="iv-msg" id="ivM" role="status"></div><div class="iv-trust">{"".join(f"<span>{e(x)}</span>" for x in L["trust"])}</div></div></div>'
            f'<div class="iv-pvw"><div class="iv-pv" id="ivPv" aria-live="polite">{pv}</div></div></section>'
                        f'<h2 class="iv-sh">{e(L["steps_h"])}</h2><div class="iv-how">{"".join(f"<div><b>{e(a)}</b><span>{e(b)}</span></div>" for a, b in L["steps"])}</div>'
            f'<p class="iv-sh">{e(L["more_h"])}</p><div class="iv-acc">{secs}</div>'
            f'<h2 class="iv-sh">{e(t["faq_h"])}</h2><div class="iv-acc">{faqs}</div><p class="note">{e(t["note"])}</p>'
            f'<script>window.IVL={json.dumps(L, ensure_ascii=False)};window.IVRATE={rate};window.IVCUR={json.dumps(cur)};window.IVB={json.dumps(BUILDER[lang])};</script><script>{JS}</script>')
    h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}{GRID_CSS}</style></head>")
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="iv pg">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


def main():
    for lang in URL:
        f = os.path.join(ROOT, URL[lang].strip("/"), "index.html"); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(build(lang))
    sm = os.path.join(ROOT, "sitemap.xml"); xml = open(sm, encoding="utf-8").read()
    for u in URL.values():
        if f"<loc>{SITE}{u}</loc>" not in xml:
            xml = xml.replace("</urlset>", f"  <url><loc>{SITE}{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n</urlset>")
    open(sm, "w", encoding="utf-8").write(xml)
    print("ok")


if __name__ == "__main__":
    main()
