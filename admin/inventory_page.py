# -*- coding: utf-8 -*-
"""«Оцени мой инвентарь»: стоимость скинов, оценка сочетаемости цветов, советы и карточка для шеринга.
Запуск: python3 admin/inventory_page.py   → /ocenka-inventarya/ и /en/inventory-value/
Данные в браузере: воркер /inv (свой инвентарь после входа через Steam) или /invp?id= (любой открытый профиль),
/data/catalog.json (цвета, слоты, картинки), /data/prices.json (цены по износу).
"""
import json, os, sys, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from about import LANG_JS, CP  # noqa
import navmore  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/ocenka-inventarya/", "en": "/en/inventory-value/"}
W = "https://auth.skin-set.com"

T = {
 "ru": dict(title="Оценка инвентаря CS2: сколько стоит и насколько стильный — Skinset",
   desc="Узнай стоимость инвентаря CS2 и оценку его стиля: сочетаются ли нож, перчатки и оружие по цвету. Советы, что докупить, и картинка, чтобы поделиться. Бесплатно, вход через Steam.",
   h1="Оцени свой инвентарь CS2", kick="Бесплатно · за 10 секунд",
   lead="Считаем, сколько стоят твои скины, и ставим оценку стилю: насколько нож, перчатки и оружие сочетаются по цвету. Покажем, какой предмет выбивается и что докупить, чтобы инвентарь выглядел как один сет.",
   login="Войти через Steam", mine="Оценить мой инвентарь", or_="или вставь ссылку на любой открытый профиль Steam", ph="https://steamcommunity.com/id/… или /profiles/7656…", check="Оценить",
   home="Главная", how_h="Как считается оценка", faq_h="Вопросы и ответы",
   how=["<b>Стиль (55%)</b> — насколько ключевые предметы (нож, перчатки, AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) попадают в одну цветовую гамму. Чёрный, белый и серый подходят ко всему.",
        "<b>Комплектность (25%)</b> — сколько из 8 главных слотов заняты скинами.",
        "<b>Стоимость (20%)</b> — общая цена скинов по текущим минимальным ценам рынка; растёт логарифмически, поэтому дешёвый, но стильный инвентарь может обогнать дорогой и пёстрый."],
   faq=[("Это безопасно?", "Да. Мы только читаем открытый список предметов через Steam — как любой сайт-оценщик. Вход через Steam идёт на официальной странице Steam, пароль мы не видим, трейды и доступ к аккаунту не запрашиваем."),
        ("Почему пишет, что инвентарь скрыт?", "В настройках приватности Steam включи «Инвентарь: открытый». Изменения применяются сразу, иногда до нескольких минут."),
        ("Почему стоимость отличается от других сайтов?", "Мы берём минимальную цену на рынке для каждого износа, а для StatTrak™ — цену обычной версии (поэтому стоимость помечена «≈»). Кейсы, стикеры и агенты в стоимость пока не входят."),
        ("Можно оценить инвентарь друга или стримера?", "Да — вставь ссылку на его профиль Steam. Профиль и инвентарь должны быть открытыми.")],
   L=dict(change="Сменить", addmine="Добавить", addany="Добавить предмет вручную", clr="Сбросить добавленные", search="Поиск: Karambit, Butterfly, AK-47 Redline…", hold="Скины в трейд-бане (защита обмена 7 дней) Steam никому не показывает — добавь их вручную или нажми «Сменить» на слоте.", login="Войти через Steam", mine="Оценить мой инвентарь", load="Загружаем инвентарь…", priv="Инвентарь скрыт. Открой его в настройках приватности Steam и попробуй ещё раз.", nf="Профиль не найден — проверь ссылку.", err="Steam не ответил, попробуй через минуту.", empty="В инвентаре нет скинов CS2.",
          score="Оценка", value="Стоимость скинов", items="Предметов", skins="скинов", palette="Гамма", complete="Комплект", set_h="Твой сет", empty_slot="пусто", off="выбивается",
          improve_h="Как улучшить", improve_p="Что заменить или докупить, чтобы инвентарь выглядел как один сет:", replace="Заменить", add="Добавить", total="Всего ≈", builder="Собрать этот сет в конструкторе →",
          top_h="Самое дорогое", share_h="Поделиться результатом", dl="Скачать картинку", share="Поделиться", copy="Скопировать ссылку", copied="Ссылка скопирована", again="Оценить другой профиль",
          lv=["Сборная солянка", "Есть над чем поработать", "Хороший инвентарь", "Отличный сет", "Легендарный сет"], st="StatTrak™ считаем по цене обычной версии.",
          fam=["Красный", "Синий", "Розовый", "Фиолетовый", "Зелёный", "Золотой", "Оранжевый", "Бирюзовый", "Чёрно-белый"],
          slots=dict(knife="Нож", gloves="Перчатки", ak="AK-47", m4="M4", awp="AWP", deagle="Desert Eagle", usp="USP-S / P2000", glock="Glock-18"), card_t="Оценка инвентаря CS2", perfect="Сет уже собран идеально — менять нечего!")),
 "en": dict(title="CS2 inventory value & style rating — Skinset",
   desc="Check your CS2 inventory value and get a style score: do your knife, gloves and weapons match in color? Tips on what to buy and a shareable image. Free, sign in with Steam.",
   h1="Rate your CS2 inventory", kick="Free · takes 10 seconds",
   lead="We calculate what your skins are worth and rate your style: how well your knife, gloves and weapons match in color. We'll show which item clashes and what to add so the inventory looks like one set.",
   login="Sign in with Steam", mine="Rate my inventory", or_="or paste a link to any public Steam profile", ph="https://steamcommunity.com/id/… or /profiles/7656…", check="Rate",
   home="Home", how_h="How the score works", faq_h="FAQ",
   how=["<b>Style (55%)</b> — how well the key items (knife, gloves, AK-47, M4, AWP, Desert Eagle, USP-S, Glock-18) share one color palette. Black, white and gray go with everything.",
        "<b>Completeness (25%)</b> — how many of the 8 key slots have a skin.",
        "<b>Value (20%)</b> — total skin value at current lowest market prices; it grows logarithmically, so a cheap but stylish inventory can beat an expensive mess."],
   faq=[("Is it safe?", "Yes. We only read the public item list through Steam, like any inventory checker. Steam sign-in happens on Steam's official page; we never see your password and never ask for trades or account access."),
        ("Why does it say my inventory is private?", "Set “Inventory: Public” in your Steam privacy settings. It applies right away, sometimes within a few minutes."),
        ("Why is the value different from other sites?", "We use the lowest market price for each wear, and the regular-version price for StatTrak™ (hence “≈”). Cases, stickers and agents are not included yet."),
        ("Can I rate a friend's or streamer's inventory?", "Yes, paste a link to their Steam profile. The profile and inventory must be public.")],
   L=dict(change="Change", addmine="Add", addany="Add an item manually", clr="Clear added", search="Search: Karambit, Butterfly, AK-47 Redline…", hold="Steam hides trade-protected skins (7-day trade hold) from everyone — add them manually or hit “Change” on a slot.", login="Sign in with Steam", mine="Rate my inventory", load="Loading inventory…", priv="This inventory is private. Make it public in Steam privacy settings and try again.", nf="Profile not found — check the link.", err="Steam didn't respond, try again in a minute.", empty="No CS2 skins in this inventory.",
          score="Score", value="Skin value", items="Items", skins="skins", palette="Palette", complete="Loadout", set_h="Your loadout", empty_slot="empty", off="clashes",
          improve_h="How to improve", improve_p="What to swap or add so the inventory looks like one set:", replace="Swap", add="Add", total="Total ≈", builder="Build this set in the builder →",
          top_h="Most valuable", share_h="Share your result", dl="Download image", share="Share", copy="Copy link", copied="Link copied", again="Rate another profile",
          lv=["Total chaos", "Room to improve", "Good inventory", "Great set", "Legendary set"], st="StatTrak™ priced as the regular version.",
          fam=["Red", "Blue", "Pink", "Purple", "Green", "Gold", "Orange", "Teal", "Black & white"],
          slots=dict(knife="Knife", gloves="Gloves", ak="AK-47", m4="M4", awp="AWP", deagle="Desert Eagle", usp="USP-S / P2000", glock="Glock-18"), card_t="CS2 inventory rating", perfect="Your set is already perfect — nothing to change!")),
}

CSS = """
html,body{overflow-x:clip}
.iv{max-width:1100px;margin:0 auto;padding:22px 24px 60px}
.iv .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:14px}.iv .crumbs a{color:var(--soft)}
.iv h1::before,.iv h2::before{display:none!important}
.iv-hero{position:relative;padding:34px 34px 30px;background:radial-gradient(90% 120% at 100% 0%,rgba(232,64,42,.35),transparent 60%),radial-gradient(60% 90% at 0% 100%,rgba(102,192,244,.12),transparent 60%),linear-gradient(160deg,#16171b,#0c0d10);border:1px solid var(--line2,rgba(255,255,255,.14))}
.iv-kick{display:inline-block;padding:6px 10px;background:rgba(255,255,255,.08);font:600 .72rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase;color:#ffd36a}
.iv h1{margin:12px 0 10px;font:700 clamp(2rem,5vw,3.4rem)/1 var(--hud);text-transform:uppercase}
.iv .lead{color:var(--soft);max-width:720px;margin:0 0 20px}
.iv-act{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.bt{display:inline-flex;align-items:center;gap:10px;height:50px;padding:0 22px;border:0;cursor:pointer;text-decoration:none;font:700 .9rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:#fff;background:linear-gradient(90deg,#06bfff,#2d73ff);box-shadow:0 8px 22px rgba(45,115,255,.3)}
.bt svg{width:22px;height:22px}.bt.r{background:linear-gradient(90deg,#e8402a,#ff6a3d);box-shadow:0 8px 22px rgba(232,64,42,.3)}.bt.g{background:rgba(255,255,255,.06);border:1px solid var(--line2,rgba(255,255,255,.2));box-shadow:none}
.bt:hover{filter:brightness(1.1)}.bt[disabled]{opacity:.6;cursor:wait}
.iv-or{margin:18px 0 8px;font-size:.86rem;color:var(--dim)}
.iv-in{display:flex;gap:8px;max-width:680px}.iv-in input{flex:1;min-width:0;height:50px;padding:0 14px;background:rgba(255,255,255,.05);border:1px solid var(--line2,rgba(255,255,255,.18));color:var(--ink,#fff);font:400 .95rem var(--body,inherit);outline:none}.iv-in input:focus{border-color:#2d73ff}
.iv-msg{margin-top:16px;padding:12px 14px;border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--soft)}.iv-msg.err{border-color:rgba(235,75,75,.6);background:rgba(235,75,75,.1);color:#ffb3b3}
.res{margin-top:22px}
.r-top{display:grid;grid-template-columns:280px 1fr;gap:14px}
.r-score{position:relative;padding:22px;background:linear-gradient(170deg,rgba(255,255,255,.07),rgba(255,255,255,.015));border:1px solid var(--line2,rgba(255,255,255,.14));text-align:center;--fc:#e8402a}
.r-user{display:flex;align-items:center;gap:10px;justify-content:center;margin-bottom:12px;font:600 .95rem var(--hud);letter-spacing:.04em}.r-user img{width:34px;height:34px;border-radius:2px}
.ring{position:relative;width:170px;height:170px;margin:0 auto}.ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.ring b{position:absolute;inset:0;display:grid;place-items:center;font:700 3.6rem/1 var(--hud)}.ring b small{display:block;font-size:.8rem;color:var(--dim);letter-spacing:.14em;margin-top:-30px}
.r-lv{margin-top:10px;font:700 1.15rem var(--hud);text-transform:uppercase;letter-spacing:.06em;color:var(--fc)}
.r-kpi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.k{padding:16px 18px;background:rgba(255,255,255,.04);border:1px solid var(--line,rgba(255,255,255,.1))}
.k small{display:block;font:600 .72rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin-bottom:10px}
.k b{font:700 1.9rem/1 var(--hud)}.k span{display:block;margin-top:6px;font-size:.82rem;color:var(--soft)}.k i.sw{display:inline-block;width:20px;height:20px;vertical-align:-3px;margin-right:8px;border:1px solid rgba(255,255,255,.3)}
.bar{height:6px;margin-top:10px;background:rgba(255,255,255,.08)}.bar i{display:block;height:100%;background:var(--fc,#e8402a)}
.iv h2{margin:30px 0 12px;font:700 1.35rem/1 var(--hud);text-transform:uppercase}
.slots{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.sl{position:relative;padding:10px 12px 12px;background:rgba(255,255,255,.04);border:1px solid var(--line,rgba(255,255,255,.1));border-bottom:3px solid var(--c,#444);min-width:0}
.sl.e{border-style:dashed;border-bottom-width:1px;opacity:.6}.sl.off{box-shadow:inset 0 0 0 1px rgba(255,93,93,.5)}
.sl small{font:600 .68rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.sl .im{height:84px;display:grid;place-items:center;margin:6px 0}.sl img{max-width:100%;max-height:84px;object-fit:contain;filter:drop-shadow(0 6px 8px rgba(0,0,0,.55))}
.sl b{display:block;font:600 .86rem/1.2 var(--body,inherit);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sl span{font-size:.78rem;color:var(--soft)}
.sl .tg{position:absolute;top:8px;right:8px;padding:3px 6px;background:#ff5d5d;color:#fff;font:700 .62rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase}
.hold{margin:-4px 0 12px;font-size:.88rem;color:var(--soft)}.lnk{background:none;border:0;padding:0;color:#66c0f4;font:inherit;cursor:pointer;text-decoration:underline}
.sl-add{padding:8px 12px;background:rgba(255,255,255,.06);border:1px dashed rgba(255,255,255,.3);color:var(--ink,#fff);font:600 .76rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;cursor:pointer}.sl-add:hover{border-color:#e8402a;color:#ff8a70}
.sl.e{opacity:1}.sl.e b,.sl.e span,.sl.e small{opacity:.6}
.pk{position:fixed;inset:0;z-index:400;background:rgba(0,0,0,.7);display:grid;place-items:center;padding:16px}.pk[hidden]{display:none}
.pk-in{width:min(640px,100%);max-height:86vh;display:flex;flex-direction:column;background:#131417;border:1px solid var(--line2,rgba(255,255,255,.18))}
.pk-h{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid var(--line,rgba(255,255,255,.1))}.pk-h b{font:700 1rem var(--hud);text-transform:uppercase;letter-spacing:.08em}
.pk-x{background:none;border:0;color:#fff;font-size:1.6rem;cursor:pointer}
.pk-in input{margin:12px 16px;height:44px;padding:0 12px;background:rgba(255,255,255,.05);border:1px solid var(--line2,rgba(255,255,255,.18));color:#fff;font-size:.95rem;outline:none}
.pk-l{overflow:auto;padding:0 16px 16px;display:grid;gap:6px}
.pk-i{display:grid;grid-template-columns:64px minmax(0,1fr);gap:10px;align-items:center;padding:8px;background:rgba(255,255,255,.035)}.pk-i img{width:64px;height:46px;object-fit:contain}.pk-i b{display:block;font-size:.9rem;margin-bottom:6px}
.pk-w{display:flex;flex-wrap:wrap;gap:4px}.pk-w button{padding:5px 7px;background:rgba(255,255,255,.06);border:1px solid var(--line2,rgba(255,255,255,.16));color:var(--soft);font-size:.74rem;cursor:pointer}.pk-w button:hover{background:#e8402a;color:#fff;border-color:#e8402a}
.sl-ed{position:absolute;top:6px;right:6px;display:flex;gap:4px;opacity:0;transition:opacity .15s;z-index:2}.sl:hover .sl-ed,.sl:focus-within .sl-ed{opacity:1}
.sl-ch,.sl-rm{padding:5px 8px;background:rgba(10,11,14,.85);border:1px solid rgba(255,255,255,.25);color:#fff;font:600 .68rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;cursor:pointer}.sl-ch:hover{border-color:#e8402a;color:#ff8a70}.sl-rm:hover{background:#c62f22}
@media(hover:none){.sl-ed{opacity:1}}
.sl .tg{top:auto!important;bottom:56px}
.sug{display:grid;gap:8px}
.sg{display:grid;grid-template-columns:70px 64px minmax(0,1fr) auto;gap:12px;align-items:center;padding:10px 14px;background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1));color:var(--ink,#fff);text-decoration:none}
.sg em{font-style:normal;font:700 .7rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:#2bd67b}.sg em.rp{color:#ffd36a}
.sg img{width:64px;height:46px;object-fit:contain}.sg b{display:block;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sg small{color:var(--dim);font-size:.78rem}.sg strong{font:700 1rem var(--hud)}
.tot{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-top:12px}
.tot span{font:700 1.2rem var(--hud)}
.top5{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}
.share{display:grid;grid-template-columns:minmax(0,1.3fr) 1fr;gap:18px;align-items:center}
.share canvas{width:100%;height:auto;border:1px solid var(--line2,rgba(255,255,255,.14))}
.share .acts{display:flex;flex-direction:column;gap:10px;align-items:flex-start}
.iv .how{color:var(--soft);display:grid;gap:8px;padding-left:20px;max-width:860px}.iv .faq h3{margin:16px 0 6px;font:600 1.05rem var(--hud)}.iv .faq p{margin:0;color:var(--soft);max-width:860px}
.iv .note{font-size:.8rem;color:var(--dim)}
@media(max-width:860px){.r-top{grid-template-columns:1fr}.slots{grid-template-columns:repeat(2,minmax(0,1fr))}.top5{grid-template-columns:repeat(2,minmax(0,1fr))}.share{grid-template-columns:1fr}}
@media(max-width:600px){.k{min-width:0;padding:12px}.k b{font-size:1.3rem;overflow-wrap:anywhere}.k i.sw{width:14px;height:14px}.iv-in input{flex:none}.iv{padding:16px 14px 40px}.iv-hero{padding:22px 16px}.iv-in{flex-direction:column}.bt{justify-content:center;width:100%}.sg{grid-template-columns:56px minmax(0,1fr) auto}.sg em{display:none}.sg img{width:56px}}
"""

JS = r"""(()=>{const L=window.IVL,W=__W__,lang=document.documentElement.lang,BUILD=__BUILD__,WIKI=__WIKI__,R=__RATE__,CUR=__CUR__;const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const LS=(k,v)=>{try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){return null}};
let fresh=false;try{const m=location.hash.match(/steam=([^&]+)/);if(m){fresh=true;const v=decodeURIComponent(m[1]);if(v!=="cancel"&&v!=="error")LS("skinset_steam",v);history.replaceState(null,"",location.pathname+location.search)}}catch(e){}
const tok=()=>LS("skinset_steam");const fmt=new Intl.NumberFormat(lang,{maximumFractionDigits:R>=50?0:0});const M=usd=>CUR[0]+fmt.format(Math.round(usd*R))+CUR[1];
const IMG=i=>i.startsWith("http")?i:"https://community.akamai.steamstatic.com/economy/image/"+i+"/360fx360f";
const WEAR={"Factory New":"FN","Minimal Wear":"MW","Field-Tested":"FT","Well-Worn":"WW","Battle-Scarred":"BS"};
const FAMC=["#d62a2a","#2f6fe0","#ff5cb0","#7a3bd1","#21a35f","#d4af37","#f27a1b","#14c2c7","#e8e8e8"];
const SLOTS=["knife","gloves","ak","m4","awp","deagle","usp","glock"];
function slotOf(c){if(c.c==="knife")return"knife";if(c.c==="gloves")return"gloves";return{"AK-47":"ak","M4A4":"m4","M4A1-S":"m4","AWP":"awp","Desert Eagle":"deagle","USP-S":"usp","P2000":"usp","Glock-18":"glock"}[c.w]||null}
function hsl(hex){const n=parseInt(hex.slice(1),16),r=(n>>16&255)/255,g=(n>>8&255)/255,b=(n&255)/255,mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2;let h=0,s=0;if(mx!==mn){const d=mx-mn;s=l>.5?d/(2-mx-mn):d/(mx+mn);h=mx===r?(g-b)/d+(g<b?6:0):mx===g?(b-r)/d+2:(r-g)/d+4;h*=60}return[h,s,l]}
function fam(hex){const[h,s,l]=hsl(hex);if(s<.2||l<.12||l>.9)return 8;if(h<14||h>=340)return 0;if(h<38)return 6;if(h<66)return 5;if(h<160)return 4;if(h<196)return 7;if(h<252)return 1;if(h<290)return 3;return 2}
const ADJ={"0-6":1,"0-2":1,"6-5":1,"1-7":1,"1-3":1,"3-2":1,"7-4":1};const adj=(a,b)=>ADJ[a+"-"+b]||ADJ[b+"-"+a];
let CAT=null,P=null;async function data(){if(!CAT){const[c,p]=await Promise.all([fetch("/data/catalog.json").then(r=>r.json()),fetch("/data/prices.json").then(r=>r.json())]);CAT=new Map();for(const x of c){if(!CAT.has(x.n))CAT.set(x.n,x);const b=x.n.replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,"");if(!CAT.has(b))CAT.set(b,x)}CAT.list=c;P=p}}
function parse(name){let st=/StatTrak™/.test(name);let n=name.replace(/^★\s*/,"").replace(/StatTrak™\s*/,"").replace(/^Souvenir\s+/,"");let w=null;const m=n.match(/\s*\((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/);if(m){w=WEAR[m[1]];n=n.slice(0,m.index)}return{n,w,st}}
function price(n,w){const p=P[n];if(!p||!p.w)return 0;if(w&&p.w[w])return p.w[w];const v=Object.values(p.w);return v.length?Math.min(...v):0}
function cprice(c){const v=(c.p||[]).filter(Boolean);return v.length?Math.min(...v):0}
function rate(items){const own=[];let value=0,cnt=0,other=0,st=false;
 for(const[name,k,mi]of items){const q=parse(name);const c=CAT.get(q.n);if(!c){other+=k;continue}const v=price(q.n,q.w)||price(c.n,q.w);value+=v*k;cnt+=k;if(q.st)st=true;own.push({mi,c,w:q.w,v,st:q.st,slot:slotOf(c)})}
 const best={};for(const o of own){if(!o.slot)continue;const b=best[o.slot],man=o.mi!=null;if(!b||(man&&b.mi==null)||(man&&b.mi!=null&&o.mi>b.mi)||(!man&&b.mi==null&&o.v>b.v))best[o.slot]=o}
 const lo=SLOTS.map(s=>best[s]).filter(Boolean);
 const fw=Array(9).fill(0);for(const o of lo){const h=o.c.h||[];h.forEach((x,i)=>fw[fam(x)]+=(i?.3/(h.length-1||1):.7)*(o.slot==="knife"||o.slot==="gloves"?1.5:1))}
 const nn=fw.slice(0,8);let dom=nn.indexOf(Math.max(...nn));if(Math.max(...nn)<.01)dom=8;
 let hs=0;for(const o of lo){const f=fam((o.c.h||["#888"])[0]);o.f=f;const m=f===dom?1:f===8?.75:adj(f,dom)?.55:(o.c.h||[]).slice(1).some(x=>fam(x)===dom)?.5:0;o.m=m;hs+=m}
 const harmony=lo.length?hs/lo.length:0,complete=lo.length/8,vs=Math.min(1,Math.log10(value+1)/Math.log10(5000));
 const score=Math.round(100*(.55*harmony*(lo.length>=2?1:.5)+.25*complete+.2*vs));
 // советы
 const avg=lo.length?lo.reduce((a,o)=>a+o.v,0)/lo.length:5;const sugg=[];
 const pick=(slot,exclude)=>{const c=CAT.list.filter(x=>slotOf(x)===slot&&x.h&&x.h.length&&fam(x.h[0])===dom&&cprice(x)>0&&x.n!==exclude);if(!c.length)return null;
   if(slot==="knife"||slot==="gloves")return c.sort((a,b)=>cprice(a)-cprice(b))[0];return c.sort((a,b)=>Math.abs(Math.log(cprice(a)/Math.max(1,avg)))-Math.abs(Math.log(cprice(b)/Math.max(1,avg))))[0]};
 for(const o of lo)if(o.m<.5){const x=pick(o.slot,o.c.n);if(x)sugg.push({t:"rp",slot:o.slot,from:o,c:x,v:cprice(x)})}
 for(const s of SLOTS)if(!best[s]&&sugg.length<6){const x=pick(s);if(x)sugg.push({t:"add",slot:s,c:x,v:cprice(x)})}
 const top=own.slice().sort((a,b)=>b.v-a.v).slice(0,5);
 return{value,cnt,other,st,best,lo,dom,harmony,complete,score,sugg,top}}
function lv(s){return L.lv[s>=90?4:s>=75?3:s>=60?2:s>=40?1:0]}
function render(r,u){const fc=FAMC[r.dom];const box=$("#ivRes");const C=2*Math.PI*72;
 const slots=SLOTS.map(s=>{const o=r.best[s];if(!o)return'<div class="sl e"><small>'+esc(L.slots[s])+'</small><div class="im"><button class="sl-add" data-s="'+s+'">+ '+esc(L.addmine)+'</button></div><b>—</b><span>'+esc(L.empty_slot)+'</span></div>';
  const h=(o.c.h||["#666"])[0];return'<a class="sl'+(o.m<.5?" off":"")+'" style="--c:'+h+';color:inherit;text-decoration:none" href="'+WIKI+o.c.u+'/"><small>'+esc(L.slots[s])+'</small><span class="sl-ed"><button class="sl-ch" data-s="'+s+'" title="'+esc(L.change)+'">'+esc(L.change)+'</button>'+(o.mi!=null?'<button class="sl-rm" data-rm="'+o.mi+'" title="×">×</button>':'')+'</span>'+(o.m<.5?'<span class="tg">'+esc(L.off)+'</span>':'')+'<div class="im"><img src="'+esc(IMG(o.c.i))+'" alt="" loading="lazy"></div><b>'+esc(o.c.s)+'</b><span>'+esc(o.c.w)+(o.w?" · "+o.w:"")+(o.v?" · "+M(o.v):"")+'</span></a>'}).join("");
 const sg=r.sugg.map(x=>'<a class="sg" href="'+WIKI+x.c.u+'/"><em class="'+(x.t==="rp"?"rp":"")+'">'+esc(x.t==="rp"?L.replace:L.add)+'</em><img src="'+esc(IMG(x.c.i))+'" alt="" loading="lazy"><span><b>'+esc(x.c.n)+'</b><small>'+esc(L.slots[x.slot])+(x.from?" · ← "+esc(x.from.c.n):"")+'</small></span><strong>'+M(x.v)+'</strong></a>').join("");
 const tot=r.sugg.reduce((a,x)=>a+x.v,0);
 const setq=SLOTS.map(s=>{const sg=r.sugg.find(x=>x.slot===s);const c=sg?sg.c:(r.best[s]&&r.best[s].c);return c?((c.c==="knife"||c.c==="gloves"?"★ ":"")+c.w+"|"+c.s):null}).filter(Boolean).join(";");
 const top=r.top.map(o=>'<a class="sl" style="--c:'+((o.c.h||["#666"])[0])+';color:inherit;text-decoration:none" href="'+WIKI+o.c.u+'/"><small>'+esc(o.c.w)+'</small><div class="im"><img src="'+esc(IMG(o.c.i))+'" alt="" loading="lazy"></div><b>'+esc(o.c.s)+'</b><span>'+(o.st?"StatTrak™ · ":"")+(o.w||"")+(o.v?" · "+M(o.v):"")+'</span></a>').join("");
 box.innerHTML='<div class="r-top"><div class="r-score" style="--fc:'+fc+'"><div class="r-user">'+(u.a?'<img src="'+esc(u.a)+'" alt="">':'')+'<span>'+esc(u.n||"Steam")+'</span></div><div class="ring"><svg viewBox="0 0 160 160"><circle cx="80" cy="80" r="72" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="12"/><circle cx="80" cy="80" r="72" fill="none" stroke="'+fc+'" stroke-width="12" stroke-linecap="butt" stroke-dasharray="'+C+'" stroke-dashoffset="'+C*(1-r.score/100)+'"/></svg><b>'+r.score+'</b></div><div class="r-lv">'+esc(lv(r.score))+'</div></div>'
  +'<div class="r-kpi"><div class="k"><small>'+esc(L.value)+'</small><b>≈ '+M(r.value)+'</b><span>'+r.cnt+' '+esc(L.skins)+(r.st?' · '+esc(L.st):'')+'</span></div><div class="k"><small>'+esc(L.palette)+'</small><b><i class="sw" style="background:'+fc+'"></i>'+esc(L.fam[r.dom])+'</b><div class="bar" style="--fc:'+fc+'"><i style="width:'+Math.round(r.harmony*100)+'%"></i></div><span>'+Math.round(r.harmony*100)+'%</span></div>'
  +'<div class="k"><small>'+esc(L.complete)+'</small><b>'+r.lo.length+' / 8</b><div class="bar" style="--fc:'+fc+'"><i style="width:'+r.complete*100+'%"></i></div></div><div class="k"><small>'+esc(L.items)+'</small><b>'+(r.cnt+r.other)+'</b><span>'+r.cnt+' '+esc(L.skins)+'</span></div></div></div>'
  +'<h2>'+esc(L.set_h)+'</h2><p class="hold">'+esc(L.hold)+' <button class="lnk" data-s="">'+esc(L.addany)+'</button>'+(ADD.length?' · <button class="lnk" id="ivClr">'+esc(L.clr)+' ('+ADD.length+')</button>':'')+'</p><div class="slots">'+slots+'</div>'
  +'<h2>'+esc(L.improve_h)+'</h2>'+(r.sugg.length?'<p style="color:var(--soft);margin:0 0 10px">'+esc(L.improve_p)+'</p><div class="sug">'+sg+'</div><div class="tot"><span>'+esc(L.total)+' '+M(tot)+'</span><a class="bt r" href="'+BUILD[r.dom]+'?set='+encodeURIComponent(setq)+'">'+esc(L.builder)+'</a></div>':'<p style="color:var(--soft)">'+esc(L.perfect)+'</p>')
  +(top?'<h2>'+esc(L.top_h)+'</h2><div class="top5">'+top+'</div>':'')
  +'<h2>'+esc(L.share_h)+'</h2><div class="share"><canvas id="ivCv" width="1200" height="630"></canvas><div class="acts"><button class="bt r" id="ivDl">'+esc(L.dl)+'</button><button class="bt g" id="ivSh">'+esc(L.share)+'</button><button class="bt g" id="ivCp">'+esc(L.copy)+'</button><button class="bt g" id="ivAg">'+esc(L.again)+'</button></div></div>';
 box.hidden=false;box.scrollIntoView({behavior:"smooth",block:"start"});card(r,u,fc);
 const qs="?id="+u.sid+(ADD.length?"&add="+encodeURIComponent(ADD.map(a=>a.join("~")).join(";")):"");const link=location.origin+location.pathname+qs;history.replaceState(null,"",location.pathname+qs);
 box.querySelectorAll("[data-s]").forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();picker(b.dataset.s)});box.querySelectorAll("[data-rm]").forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();ADD.splice(+b.dataset.rm,1);saveAdd();rerun()});const cl=$("#ivClr");if(cl)cl.onclick=()=>{ADD=[];saveAdd();rerun()};
 $("#ivCp").onclick=async()=>{try{await navigator.clipboard.writeText(link);$("#ivCp").textContent=L.copied}catch(e){}};
 $("#ivAg").onclick=()=>{$("#ivId").focus();scrollTo({top:0,behavior:"smooth"})};
 const blob=()=>new Promise(res=>$("#ivCv").toBlob(res,"image/png"));
 $("#ivDl").onclick=async()=>{const b=await blob();const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="skinset-inventory-"+r.score+".png";a.click()};
 $("#ivSh").onclick=async()=>{try{const b=await blob();const f=new File([b],"skinset.png",{type:"image/png"});if(navigator.canShare&&navigator.canShare({files:[f]}))await navigator.share({files:[f],text:L.card_t+": "+r.score+"/100 — "+link});else await navigator.share({text:L.card_t+": "+r.score+"/100",url:link})}catch(e){$("#ivCp").click()}}}
function loadImg(u){return new Promise(res=>{const i=new Image();i.crossOrigin="anonymous";i.onload=()=>res(i);i.onerror=()=>res(null);i.src="https://images.weserv.nl/?w=360&url="+encodeURIComponent(u.replace(/^https?:\/\//,""))})}
async function card(r,u,fc){const cv=$("#ivCv"),x=cv.getContext("2d");const g=x.createLinearGradient(0,0,1200,630);g.addColorStop(0,"#16171b");g.addColorStop(1,"#0b0c0f");x.fillStyle=g;x.fillRect(0,0,1200,630);
 const rg=x.createRadialGradient(1050,60,10,1050,60,620);rg.addColorStop(0,fc+"88");rg.addColorStop(1,"transparent");x.fillStyle=rg;x.fillRect(0,0,1200,630);
 x.fillStyle="#e8402a";x.font="700 30px Oswald, Arial Narrow, sans-serif";x.fillText("SKINSET",60,78);x.fillStyle="rgba(255,255,255,.55)";x.font="500 22px Oswald, Arial Narrow, sans-serif";x.fillText(L.card_t.toUpperCase(),190,78);
 x.fillStyle="#fff";x.font="700 44px Oswald, Arial Narrow, sans-serif";x.fillText((u.n||"Steam").slice(0,22),60,160);
 x.lineWidth=22;x.strokeStyle="rgba(255,255,255,.1)";x.beginPath();x.arc(190,370,120,0,Math.PI*2);x.stroke();x.strokeStyle=fc;x.beginPath();x.arc(190,370,120,-Math.PI/2,-Math.PI/2+Math.PI*2*r.score/100);x.stroke();
 x.fillStyle="#fff";x.textAlign="center";x.font="700 96px Oswald, Arial Narrow, sans-serif";x.fillText(String(r.score),190,398);x.font="600 22px Oswald, sans-serif";x.fillStyle=fc;x.fillText(lv(r.score).toUpperCase(),190,540);x.textAlign="left";
 x.fillStyle="rgba(255,255,255,.55)";x.font="600 20px Oswald, sans-serif";x.fillText(L.value.toUpperCase(),380,250);x.fillText(L.palette.toUpperCase(),760,250);
 x.fillStyle="#fff";x.font="700 48px Oswald, sans-serif";x.fillText("≈ "+M(r.value),380,305);x.fillStyle=fc;x.fillRect(760,268,30,30);x.fillStyle="#fff";x.fillText(L.fam[r.dom],802,305);
 x.fillStyle="rgba(255,255,255,.4)";x.font="500 20px sans-serif";x.fillText("skin-set.com",1010,595);
 const its=SLOTS.map(s=>r.best[s]).filter(Boolean).slice(0,6);const imgs=await Promise.all(its.map(o=>loadImg(IMG(o.c.i)))).catch(()=>[]);
 its.forEach((o,i)=>{const X=380+i*125,Y=360;x.fillStyle="rgba(255,255,255,.05)";x.fillRect(X,Y,113,100);x.fillStyle=(o.c.h||["#666"])[0];x.fillRect(X,Y+96,113,4);const im=imgs[i];if(im){const s=Math.min(100/im.width,84/im.height);x.drawImage(im,X+(113-im.width*s)/2,Y+8+(84-im.height*s)/2,im.width*s,im.height*s)}});
 const av=u.a?await loadImg(u.a):null;if(av)x.drawImage(av,1060,105,80,80)}
let ADD=[],LAST=null;const WN={FN:"Factory New",MW:"Minimal Wear",FT:"Field-Tested",WW:"Well-Worn",BS:"Battle-Scarred"};
function loadAdd(sid){const q=new URLSearchParams(location.search).get("add");if(q){ADD=q.split(";").map(x=>x.split("~")).filter(a=>a[0]);return}try{ADD=JSON.parse(LS("iv_add_"+sid)||"[]")}catch(e){ADD=[]}}
function saveAdd(){if(LAST)LS("iv_add_"+LAST.sid,JSON.stringify(ADD))}
function rerun(){if(!LAST)return;const res=rate(LAST.items.concat(ADD.map((a,i)=>[a[0]+(a[1]?" ("+WN[a[1]]+")":""),1,i])));render(res,LAST.u)}
function picker(slot){let ov=$("#ivPk");if(!ov){ov=document.createElement("div");ov.id="ivPk";ov.className="pk";document.body.appendChild(ov)}
 ov.innerHTML='<div class="pk-in"><div class="pk-h"><b>'+esc(slot?L.slots[slot]:L.addany)+'</b><button class="pk-x">×</button></div><input placeholder="'+esc(L.search)+'" autocomplete="off"><div class="pk-l"></div></div>';ov.hidden=false;
 const inp=ov.querySelector("input"),lst=ov.querySelector(".pk-l");const close=()=>{ov.hidden=true};ov.querySelector(".pk-x").onclick=close;ov.onclick=e=>{if(e.target===ov)close()};
 const show=()=>{const q=inp.value.trim().toLowerCase().split(/\s+/).filter(Boolean);const r=CAT.list.filter(x=>(!slot||slotOf(x)===slot)&&q.every(w=>x.n.toLowerCase().includes(w))).sort((a,b)=>cprice(b)-cprice(a)).slice(0,40);
  lst.innerHTML=r.map((x,i)=>'<div class="pk-i"><img src="'+esc(IMG(x.i))+'" alt="" loading="lazy"><span><b>'+esc(x.n+(x.ph&&!x.n.includes("(")?" ("+x.ph+")":""))+'</b><span class="pk-w">'+["FN","MW","FT","WW","BS"].map((w,k)=>x.p&&x.p[k]?'<button data-i="'+i+'" data-w="'+w+'">'+w+' · '+M(x.p[k])+'</button>':"").join("")+'</span></span></div>').join("");
  lst.querySelectorAll("button[data-w]").forEach(b=>b.onclick=()=>{const x=r[+b.dataset.i];if(slot)ADD=ADD.filter(a=>{const c=CAT.get(a[0]);return !c||slotOf(c)!==slot});ADD.push([x.n,b.dataset.w]);saveAdd();close();rerun()})};
 inp.oninput=show;show();setTimeout(()=>inp.focus(),50)}
async function run(kind,id){const msg=$("#ivMsg");msg.hidden=false;msg.className="iv-msg";msg.textContent=L.load;$("#ivRes").hidden=true;
 try{const url=kind==="me"?W+"/inv?t="+encodeURIComponent(tok()):W+"/invp?id="+encodeURIComponent(id);const[r]=await Promise.all([fetch(url),data()]);const j=await r.json();
  if(r.status===401){LS("skinset_steam",null);msg.textContent="";msg.hidden=true;btns();return}
  if(j.error==="profile"){msg.className="iv-msg err";msg.textContent=L.nf;return}
  if(j.private){msg.className="iv-msg err";msg.textContent=L.priv;return}if(j.error){msg.className="iv-msg err";msg.textContent=L.err;return}
  const items=j.items&&j.items.length?j.items:(j.names||[]).map(n=>[n,1]);LAST={items,u:null,sid:j.sid};loadAdd(j.sid);const res=rate(items.concat(ADD.map((a,i)=>[a[0]+(a[1]?" ("+WN[a[1]]+")":""),1,i])));if(!res.cnt){msg.className="iv-msg err";msg.textContent=L.empty;return}
  let u={n:j.n,a:j.a,sid:j.sid};if(kind==="me"){try{const m=await (await fetch(W+"/me?t="+encodeURIComponent(tok()))).json();u={n:m.n,a:m.a,sid:m.sid}}catch(e){}}
  LAST.u=u;LAST.sid=u.sid||j.sid;msg.hidden=true;render(res,u)}catch(e){msg.className="iv-msg err";msg.textContent=L.err}}
function btns(){const a=$("#ivAct");a.innerHTML=tok()?'<button class="bt r" id="ivMe">'+esc(L.mine)+'</button>':'<a class="bt" href="'+W+'/login?r='+encodeURIComponent(location.origin+location.pathname)+'">'+__STEAM__+esc(L.login)+'</a>';const b=$("#ivMe");if(b)b.onclick=()=>run("me")}
btns();$("#ivGo").onclick=()=>{const v=$("#ivId").value.trim();if(v)run("id",v)};$("#ivId").addEventListener("keydown",e=>{if(e.key==="Enter")$("#ivGo").click()});
const q=new URLSearchParams(location.search).get("id");if(q){$("#ivId").value=q;run("id",q)}else if(tok()&&fresh){run("me")}})();"""

STEAM = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-9.96 9.17l5.35 2.21a2.8 2.8 0 0 1 1.6-.5h.16l2.38-3.45v-.05a3.77 3.77 0 1 1 3.77 3.77h-.09l-3.4 2.42v.13a2.83 2.83 0 0 1-5.62.47L2.4 14.7A10 10 0 1 0 12 2Zm-4.72 15.2-1.23-.51a2.13 2.13 0 1 0 1.17-2.92l1.27.53a1.57 1.57 0 1 1-1.2 2.9Zm9.5-7.3a2.51 2.51 0 1 0-2.5 2.52 2.52 2.52 0 0 0 2.5-2.52Zm-4.39 0a1.89 1.89 0 1 1 1.89 1.89 1.89 1.89 0 0 1-1.89-1.89Z"/></svg>'


def build(lang):
    t = T[lang]; url = URL[lang]
    build_urls = [f"{HOME[lang]}{c}/" for c in CP[lang]]
    js = (JS.replace("__W__", json.dumps(W)).replace("__BUILD__", json.dumps(build_urls)).replace("__WIKI__", json.dumps(WIKI[lang]))
          .replace("__RATE__", "90" if lang == "ru" else "1").replace("__CUR__", json.dumps(["", " ₽"] if lang == "ru" else ["$", ""])).replace("__STEAM__", json.dumps(STEAM)))
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": t["h1"], "url": SITE + url, "applicationCategory": "GameApplication", "operatingSystem": "Web", "description": t["desc"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
    body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav>'
            f'<section class="iv-hero"><span class="iv-kick">{e(t["kick"])}</span><h1>{e(t["h1"])}</h1><p class="lead">{e(t["lead"])}</p>'
            f'<div class="iv-act" id="ivAct"></div><p class="iv-or">{e(t["or_"])}</p>'
            f'<div class="iv-in"><input id="ivId" type="text" placeholder="{e(t["ph"])}" autocomplete="off"><button class="bt g" id="ivGo" type="button">{e(t["check"])}</button></div>'
            f'<div class="iv-msg" id="ivMsg" hidden></div></section>'
            f'<div class="res" id="ivRes" hidden></div>'
            f'<h2>{e(t["how_h"])}</h2><ul class="how">{"".join(f"<li>{x}</li>" for x in t["how"])}</ul>'
            f'<h2>{e(t["faq_h"])}</h2><div class="faq">{"".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in t["faq"])}</div>'
            f'<script>window.IVL={json.dumps(t["L"], ensure_ascii=False)};</script><script>{js}</script>')
    h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}</style></head>")
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="iv">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


def main():
    for lang in URL:
        f = os.path.join(ROOT, URL[lang].strip("/"), "index.html"); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(build(lang))
    sm = os.path.join(ROOT, "sitemap.xml"); xml = open(sm, encoding="utf-8").read()
    import datetime
    for u in URL.values():
        if f"<loc>{SITE}{u}</loc>" not in xml: xml = xml.replace("</urlset>", f"  <url><loc>{SITE}{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n</urlset>")
    open(sm, "w", encoding="utf-8").write(xml)
    print("ok")


if __name__ == "__main__":
    main()
