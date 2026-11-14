# -*- coding: utf-8 -*-
"""Калькулятор float CS2: float → качество, цены скина по всем качествам (обычный и StatTrak), где переплата.
Запуск: python3 admin/float_calc.py  → /float-kalkulyator-cs2/ и /en/cs2-float-calculator/
Список скинов — из data/catalog.json, цены — живые (ветка prices, запасной вариант /data/prices.json).
"""
import json, os, sys, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa
from pagegrid import GRID_CSS  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/float-kalkulyator-cs2/", "en": "/en/cs2-float-calculator/"}
T = {
 "ru": dict(title="Калькулятор float CS2: качество скина по флоату и цены по всем качествам — Skinset",
   desc="Калькулятор float для CS2 (КС 2): введи флоат — узнаешь качество (FN, MW, FT, WW, BS). Выбери скин — увидишь живые цены по всем качествам, StatTrak и где переплата.",
   h1="Калькулятор float CS2", kick="Float · качество · цена", home="Главная",
   lead="Введи float, чтобы узнать качество скина, или выбери скин — покажем живые цены по всем качествам, StatTrak-версию и сколько стоит каждый шаг вверх по качеству.",
   L=dict(fl="Float скина", flph="например 0,1534", wear="Качество", next_up="До лучшего качества", next_dn="До худшего качества", none="—",
          sk="Скин", skph="Начни вводить: карамбит допплер, AK Redline",nf="Ничего не нашли — попробуй по-английски",frm="от", reg="Обычный", st="StatTrak", na="нет", cheap="дешевле всего", step="Шаг вверх", buy="Купить",
          src="Цены живые, обновляются несколько раз в день. Минимальная цена на площадках, без наклеек.", open="Страница скина →", empty="Выбери скин, чтобы увидеть цены",
          names={"FN": "Factory New · Прямо с завода", "MW": "Minimal Wear · Немного поношенное", "FT": "Field-Tested · После полевых испытаний", "WW": "Well-Worn · Поношенное", "BS": "Battle-Scarred · Закалённое в боях"},
          bad="Float — число от 0 до 1"),
   sec=[("Как пользоваться", "Float — число от 0 до 1, которое задаётся скину при выпадении и больше не меняется. Скопируй float из окна осмотра в игре или из карточки предмета на площадке и вставь в поле выше: калькулятор покажет качество и сколько осталось до соседнего. Ниже выбери скин — увидишь минимальные цены по каждому качеству и сколько стоит переход на ступень выше."),
        ("Границы качеств", "Factory New — 0,00–0,07, Minimal Wear — 0,07–0,15, Field-Tested — 0,15–0,38, Well-Worn — 0,38–0,45, Battle-Scarred — 0,45–1,00. У многих скинов диапазон float уже: например, AWP | Asiimov начинается с 0,18, поэтому FN и MW у него нет, а Doppler и Fade заканчиваются на 0,08 и бывают только FN и MW."),
        ("Где выгодно экономить", "Медианный скин в Factory New стоит почти в 4 раза дороже Field-Tested. Если шаг вверх по качеству стоит в разы дороже, а скин тёмный или матовый, бери качество пониже: в игре разницу почти никто не заметит. Подробнее — в статьях «[Качество скинов CS2](/blog/kachestvo-skinov-cs2-fn-mw-ft-ww-bs/)» и «[Float и паттерн](/blog/float-i-pattern-skinov-cs2/)».")],
   faq=[("Какое качество у float 0,15?", "Ровно 0,15 — это уже Field-Tested: Minimal Wear заканчивается на 0,15, граница относится к следующему качеству."),
        ("Можно ли изменить float скина?", "Нет. Float задаётся при выпадении и не меняется, сколько бы ты ни играл."),
        ("Почему у скина нет Factory New?", "У скина ограничен диапазон float. Например, AWP | Asiimov выпадает только с float от 0,18, поэтому бывает лишь в FT, WW и BS."),
        ("Где взять float своего скина?", "Осмотри скин в инвентаре CS2 — float показан в окне осмотра. На торговых площадках он указан в карточке предмета.")],
   faq_h="Вопросы и ответы", note="Skinset не связан с Valve. Цены — ориентир по торговым площадкам."),
 "en": dict(title="CS2 Float Calculator: Skin Wear by Float and Prices for Every Wear — Skinset",
   desc="CS2 float calculator: enter a float to get the wear (FN, MW, FT, WW, BS). Pick a skin to see live prices for every wear, StatTrak, and where you overpay.",
   h1="CS2 float calculator", kick="Float · wear · price", home="Home",
   lead="Enter a float to get the skin's wear, or pick a skin to see live prices for every wear, the StatTrak version, and what each step up in wear costs.",
   L=dict(fl="Skin float", flph="e.g. 0.1534", wear="Wear", next_up="To better wear", next_dn="To worse wear", none="—",
          sk="Skin", skph="Start typing: Karambit Doppler, AK Redline",nf="Nothing found",frm="from", reg="Regular", st="StatTrak", na="none", cheap="cheapest", step="Step up", buy="Buy",
          src="Live prices, refreshed several times a day. Lowest marketplace price, no stickers.", open="Skin page →", empty="Pick a skin to see prices",
          names={"FN": "Factory New", "MW": "Minimal Wear", "FT": "Field-Tested", "WW": "Well-Worn", "BS": "Battle-Scarred"},
          bad="Float is a number from 0 to 1"),
   sec=[("How to use it", "Float is a number from 0 to 1 set when a skin drops; it never changes. Copy the float from the in-game inspect window or a marketplace listing and paste it above: the calculator shows the wear and how far you are from the next one. Then pick a skin to see the lowest price for each wear and what moving one step up costs."),
        ("Wear boundaries", "Factory New 0.00–0.07, Minimal Wear 0.07–0.15, Field-Tested 0.15–0.38, Well-Worn 0.38–0.45, Battle-Scarred 0.45–1.00. Many skins have a narrower range: AWP | Asiimov starts at 0.18, so it has no FN or MW, while Doppler and Fade end at 0.08 and only come in FN and MW."),
        ("Where to save", "The median skin in Factory New costs almost 4× its Field-Tested price. If a step up costs several times more and the skin is dark or matte, go lower: almost nobody will notice in game. More in our guides to [CS2 wear](/en/blog/kachestvo-skinov-cs2-fn-mw-ft-ww-bs/) and [float and pattern](/en/blog/float-i-pattern-skinov-cs2/).")],
   faq=[("What wear is float 0.15?", "Exactly 0.15 is already Field-Tested: Minimal Wear ends at 0.15 and the boundary belongs to the next wear."),
        ("Can a skin's float change?", "No. Float is set on drop and stays the same however much you play."),
        ("Why does a skin have no Factory New?", "Its float range is capped. AWP | Asiimov only drops with float 0.18 and above, so it comes in FT, WW and BS only."),
        ("Where do I find my skin's float?", "Inspect the skin in your CS2 inventory; the float is shown in the inspect window. Marketplaces list it on the item card.")],
   faq_h="FAQ", note="Skinset is not affiliated with Valve. Prices are a marketplace guide."),
}

CSS = """.fc{max-width:980px}.fc-box{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:22px 0}
.fc-card{background:var(--panel,#14141b);border:1px solid var(--line,#26262f);padding:18px}.fc-card label{display:block;font:600 .72rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--soft,#aaa);margin-bottom:10px}
.fc-card input{width:100%;box-sizing:border-box;height:48px;padding:0 14px;background:#0d0d12;border:1px solid var(--line2,#33333d);color:#fff;font:600 1.2rem/1 var(--body,inherit)}.fc-card input:focus{outline:none;border-color:var(--pick,#c4161c)}
.fc-w{margin-top:14px;font:700 1.5rem/1.1 var(--hud);text-transform:uppercase}.fc-w small{display:block;margin-top:6px;font:500 .85rem/1.3 var(--body,inherit);text-transform:none;color:var(--soft,#aaa)}
.fc-bar{position:relative;display:flex;height:30px;margin-top:16px;cursor:ew-resize;touch-action:none;user-select:none}.fc-bar span{box-sizing:border-box;pointer-events:none}.fc-bar span{display:flex;align-items:center;justify-content:center;font:600 .66rem/1 var(--hud);color:#fff;border-right:1px solid #0d0d12;opacity:.5}.fc-bar span.on{opacity:1}
.fc-bar i{position:absolute;top:-7px;bottom:-7px;width:4px;margin-left:-1px;background:#fff;box-shadow:0 0 0 2px #0d0d12;pointer-events:none}.fc-bar i::after{content:"";position:absolute;left:50%;top:-6px;width:14px;height:14px;margin-left:-7px;background:#fff;border:2px solid #0d0d12;border-radius:50%}
.fc-near{display:flex;gap:10px;margin-top:12px;font-size:.85rem;color:var(--soft,#aaa)}.fc-near b{color:#fff}
.fc-t{width:100%;border-collapse:collapse;margin-top:14px}.fc-t th,.fc-t td{padding:9px 8px;border-bottom:1px solid var(--line,#26262f);text-align:left;font-size:.92rem}.fc-t th{font:600 .68rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:var(--soft,#aaa)}
.fc-t td{white-space:nowrap}.fc-t td.n{white-space:nowrap}.fc-box{align-items:start}.fc-t tr.cur td{background:rgba(255,255,255,.06);color:#fff}.fc-t tr.cur td:first-child{box-shadow:inset 3px 0 0 var(--pick,#c4161c)}.fc-t em{font-style:normal;font-size:.68rem;color:#2ecc71;margin-left:6px;letter-spacing:.02em}.fc-t .up{font-size:.78rem;color:var(--soft,#aaa)}.fc-t a{color:#ff5cb0}
.fc-sk{display:flex;align-items:center;gap:12px;margin-top:14px}.fc-sk img{width:110px;height:82px;object-fit:contain}.fc-sk b{display:block;font-size:1.05rem}.fc-sk a{font-size:.85rem}
.fc-ac{position:absolute;left:18px;right:18px;top:84px;z-index:30;max-height:420px;overflow-y:auto;background:#14141b;border:1px solid var(--line2,#33333d);box-shadow:0 18px 40px rgba(0,0,0,.6)}.fc-ac[hidden]{display:none}
.fc-ac button{display:flex;align-items:center;gap:12px;width:100%;padding:7px 12px;background:none;border:0;border-bottom:1px solid rgba(255,255,255,.05);color:#fff;text-align:left;cursor:pointer;font:inherit}.fc-ac button.on,.fc-ac button:hover{background:rgba(255,255,255,.07)}
.fc-ac img,.fc-ac .ph{width:64px;height:48px;object-fit:contain;flex:none}.fc-ac .nm{flex:1;min-width:0}.fc-ac .nm b{display:block;font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fc-ac .nm small{color:var(--soft,#999);font-size:.78rem}
.fc-ac em{font-style:normal;font-size:.82rem;color:#2ecc71;white-space:nowrap}.fc-ac-none{padding:12px;color:var(--soft,#999);font-size:.88rem}
.fc-src{margin-top:10px;font-size:.78rem;color:var(--soft,#888)}
@media(max-width:760px){.fc-box{grid-template-columns:1fr}.fc-box>*{min-width:0}.fc-card{padding:14px}.fc-near{flex-direction:column;gap:4px}.fc-t th,.fc-t td{padding:8px 3px;font-size:.8rem}.fc-t th{font-size:.58rem;letter-spacing:.04em}}"""

JS = r"""(function(){var L=window.FCL,CAT=window.FCCAT,W=["FN","MW","FT","WW","BS"],B=[0,.07,.15,.38,.45,1],COL=["#2ecc71","#7bc96f","#e3b341","#e67e22","#c0392b"];
var RATE=window.FCRATE,CUR=window.FCCUR,P=null;function fmt(usd){var v=usd*RATE;return CUR==="₽"?Math.round(v).toLocaleString("ru-RU")+" ₽":"$"+(v<10?v.toFixed(2):Math.round(v).toLocaleString("en-US"))}
var fi=document.getElementById("fcF"),wo=document.getElementById("fcW"),bar=document.getElementById("fcBar"),nr=document.getElementById("fcNear");
function wearOf(f){for(var i=0;i<5;i++)if(f<B[i+1]||i===4)return i}
var CURW=null;function onF(){var s=fi.value.replace(",",".").trim(),f=parseFloat(s);var pw=CURW;CURW=null;var sp=bar.querySelectorAll("span");sp.forEach(function(x){x.classList.remove("on")});
 if(!s){if(pw&&P)show();wo.innerHTML=L.none;nr.innerHTML="";bar.querySelector("i").style.display="none";return}
 if(isNaN(f)||f<0||f>1){wo.innerHTML='<small>'+L.bad+'</small>';nr.innerHTML="";bar.querySelector("i").style.display="none";return}
 var i=wearOf(f);CURW=W[i];if(pw!==CURW&&typeof show==="function"&&P)show();wo.innerHTML=W[i]+'<small>'+L.names[W[i]]+'</small>';sp[i].classList.add("on");var m=bar.querySelector("i");m.style.display="";m.style.left="calc("+(f*100)+"% - 1px)";
 var a=i>0?(f-B[i]).toFixed(4):null,b=i<4?(B[i+1]-f).toFixed(4):null;nr.innerHTML=(a!==null?'<span>'+L.next_up+': <b>−'+a+'</b></span>':'')+(b!==null?'<span>'+L.next_dn+': <b>+'+b+'</b></span>':'')}
fi.addEventListener("input",onF);
var drag=false;function setX(ev){var r=bar.getBoundingClientRect(),f=Math.min(1,Math.max(0,(ev.clientX-r.left)/r.width));fi.value=f.toFixed(4);onF()}
bar.addEventListener("pointerdown",function(ev){drag=true;try{bar.setPointerCapture(ev.pointerId)}catch(x){}setX(ev);ev.preventDefault()});
bar.addEventListener("pointermove",function(ev){if(drag)setX(ev)});["pointerup","pointercancel"].forEach(function(t){bar.addEventListener(t,function(){drag=false})});
bar.addEventListener("keydown",function(ev){var f=parseFloat(fi.value.replace(",","."))||0,d=ev.shiftKey?.05:.005;if(ev.key==="ArrowRight"){fi.value=Math.min(1,f+d).toFixed(4);onF();ev.preventDefault()}if(ev.key==="ArrowLeft"){fi.value=Math.max(0,f-d).toFixed(4);onF();ev.preventDefault()}});
var si=document.getElementById("fcS"),out=document.getElementById("fcOut");
function show(){var n=si.value.trim();var c=CAT.find(function(x){return x[0].toLowerCase()===n.toLowerCase()});if(!c||!P){out.innerHTML='<p class="fc-src">'+L.empty+'</p>';return}
 var r=P[c[0]]||{},w=r.w||{},sw=r.stw||{};var best=null;W.forEach(function(k){if(w[k]&&(best===null||w[k]<w[best]))best=k});
 var rows=W.map(function(k,i){var v=w[k],s=sw[k];var up="";if(v&&i>0){for(var j=i-1;j>=0;j--)if(w[W[j]]){up='<span class="up">×'+(w[W[j]]/v).toFixed(1).replace(".",CUR==="₽"?",":".")+'</span>';break}}
  var q=encodeURIComponent(c[0].replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,"")+" ("+({FN:"Factory New",MW:"Minimal Wear",FT:"Field-Tested",WW:"Well-Worn",BS:"Battle-Scarred"})[k]+")");
  return '<tr'+(k===CURW?' class="cur"':'')+'><td class="n"><b>'+k+'</b></td><td>'+(v?fmt(v)+(k===best?'<em title="'+L.cheap+'">'+L.cheap+'</em>':''):L.na)+'</td><td>'+(s?fmt(s):'—')+'</td><td>'+up+'</td><td>'+(v?'<a href="https://cs.money/market/buy/?search='+q+'&utm_source=mediabuy&utm_medium=skin-set&utm_campaign=market&utm_content=link" target="_blank" rel="noopener sponsored">CS.MONEY</a>':'')+'</td></tr>'}).join("");
 var im=IMG&&IMG[c[0]];out.innerHTML='<div class="fc-sk">'+(im?'<img src="https://community.akamai.steamstatic.com/economy/image/'+im+'/256fx192f" alt="'+c[0].replace(/"/g,"&quot;")+'">':'')+'<div><b>'+c[0]+'</b>'+(c[1]?'<a href="'+c[1]+'">'+L.open+'</a>':'')+'</div></div><table class="fc-t"><thead><tr><th>'+L.wear+'</th><th>'+L.reg+'</th><th>'+L.st+'</th><th>'+L.step+'</th><th></th></tr></thead><tbody>'+rows+'</tbody></table><p class="fc-src">'+L.src+'</p>'}
/* поиск скина: свой выпадающий список с картинками и ценами, понимает русские названия */
var AL={"калаш":"ak-47","ак47":"ak-47","ак":"ak-47","авп":"awp","эвп":"awp","м4а4":"m4a4","м4а1":"m4a1-s","м4":"m4","дигл":"desert eagle","дигл":"desert eagle","юсп":"usp-s","усп":"usp-s","глок":"glock-18","карамбит":"karambit","керамбит":"karambit","бабочка":"butterfly","баттерфляй":"butterfly","байонет":"bayonet","штык":"bayonet","м9":"m9 bayonet","талон":"talon","флип":"flip","фальшион":"falchion","кукри":"kukri","скелет":"skeleton","нож":"knife","перчатки":"gloves","перчи":"gloves","спорт":"sport","драйвер":"driver","спец":"specialist","мото":"moto","гидра":"hydra",
 "допплер":"doppler","доплер":"doppler","гамма":"gamma","фейд":"fade","азимов":"asiimov","редлайн":"redline","вулкан":"vulcan","лор":"lore","драгон":"dragon","сапфир":"sapphire","рубин":"ruby","изумруд":"emerald","жемчуг":"black pearl","паутина":"crimson web","кейс":"case hardened","тигр":"tiger tooth","мрамор":"marble fade","гунгнир":"gungnir","хоул":"howl","вой":"howl","нео":"neon","принтстрим":"printstream","слотер":"slaughter","хайпер":"hyper beast","огненный":"fire serpent","пандора":"pandora","вайс":"vice","кримсон":"crimson","кимоно":"kimono","хедж":"hedge maze","неон":"neon","эмеральд":"emerald","сапфировый":"sapphire","рубиновый":"ruby","фаза":"phase","атомик":"atomic","бокс":"box"};
var ALK=Object.keys(AL);var norm=function(t){t=String(t).toLowerCase().replace(/ё/g,"е").replace(/[★|()]/g," ");t=t.replace(/[а-я][а-я0-9]*/g,function(w){if(AL[w])return AL[w];if(w.length>=2){for(var i=0;i<ALK.length;i++)if(ALK[i].indexOf(w)===0)return AL[ALK[i]]}return w});return t.replace(/-/g," ").replace(/\s+/g," ").trim()};
var IDX=CAT.map(function(c,i){return{c:c,i:i,t:norm(c[0]),w:norm(c[0].split(" | ")[0])}});
var box=document.createElement("div");box.className="fc-ac";box.hidden=true;si.parentNode.style.position="relative";si.insertAdjacentElement("afterend",box);var res=[],hi=0;
function minP(n){var r=P&&P[n];if(!r||!r.w)return null;var v=null;W.forEach(function(k){if(r.w[k]&&(v===null||r.w[k]<v))v=r.w[k]});return v}
function search(q){var qn=norm(q);if(!qn)return[];var tk=qn.split(" ");var out=[];IDX.forEach(function(x){var ok=true,sc=0;for(var j=0;j<tk.length;j++){var k=tk[j],p=x.t.indexOf(k);if(p<0){ok=false;break}sc+=p===0?0:(x.t.charAt(p-1)===" "?1:3)}if(!ok)return;if(x.w.indexOf(qn)===0)sc-=2;if(x.t===qn)sc-=10;out.push([sc,x.i,x.c])});out.sort(function(a,b){return a[0]-b[0]||a[1]-b[1]});return out.slice(0,12).map(function(z){return z[2]})}
function esc(t){return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;")}
function draw(){if(!res.length){box.innerHTML='<div class="fc-ac-none">'+L.nf+'</div>';box.hidden=!si.value.trim();return}
 box.innerHTML=res.map(function(c,i){var im=IMG&&IMG[c[0]],pp=minP(c[0]),parts=c[0].split(" | ");return '<button type="button" data-i="'+i+'"'+(i===hi?' class="on"':'')+'>'+(im?'<img src="https://community.akamai.steamstatic.com/economy/image/'+im+'/96fx72f" alt="" loading="lazy">':'<span class="ph"></span>')+'<span class="nm"><b>'+esc(parts[1]||parts[0])+'</b><small>'+esc(parts[1]?parts[0]:"")+'</small></span>'+(pp?'<em>'+L.frm+' '+fmt(pp)+'</em>':'')+'</button>'}).join("");box.hidden=false}
function pick(c){si.value=c[0];box.hidden=true;show();try{history.replaceState(null,"","?skin="+encodeURIComponent(c[0])+(fi.value?"&float="+encodeURIComponent(fi.value):""))}catch(e){}}
si.addEventListener("input",function(){res=search(si.value);hi=0;draw()});
si.addEventListener("focus",function(){si.select();if(si.value.trim()){res=search(si.value);hi=0;draw()}});
si.addEventListener("keydown",function(e){if(box.hidden||!res.length)return;if(e.key==="ArrowDown"){hi=(hi+1)%res.length;draw();e.preventDefault()}else if(e.key==="ArrowUp"){hi=(hi-1+res.length)%res.length;draw();e.preventDefault()}else if(e.key==="Enter"){pick(res[hi]);e.preventDefault()}else if(e.key==="Escape"){box.hidden=true}});
box.addEventListener("mousedown",function(e){var b=e.target.closest("[data-i]");if(b){e.preventDefault();pick(res[+b.dataset.i])}});
document.addEventListener("click",function(e){if(e.target!==si&&!box.contains(e.target))box.hidden=true});
var IMG=null;fetch("/data/skin-img.json").then(function(r){return r.json()}).then(function(a){IMG={};a.forEach(function(x){IMG[x[0].replace(/^★\s*/,"")]=x[1]});if(P)show()}).catch(function(){});
function load(){var t=Math.floor(Date.now()/60000);return fetch("https://raw.githubusercontent.com/viv1spr/skin-set/prices/prices.json?t="+t).then(function(r){if(!r.ok)throw 0;return r.json()}).catch(function(){return fetch("/data/prices.json").then(function(r){return r.json()})})}
load().then(function(p){P=p;var q=new URLSearchParams(location.search).get("skin");if(q)si.value=q;else if(!si.value)si.value=CAT.some(function(x){return x[0]==="AK-47 | Redline"})?"AK-47 | Redline":"";show()});
var qf=new URLSearchParams(location.search).get("float");if(qf){fi.value=qf}onF()})()"""


def catalog(lang):
    d = json.load(open(os.path.join(ROOT, "data/catalog.json")))
    base = WIKI[lang]
    return [[x["n"], (base + x["u"] + "/") if x.get("u") else ""] for x in d]


def build(lang):
    t = T[lang]; L = t["L"]; url = URL[lang]
    cat = catalog(lang)
    rate, cur = (90, "₽") if lang == "ru" else (1, "$")
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": t["h1"], "url": SITE + url, "description": t["desc"], "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
    bar = "".join(f'<span style="width:{w}%;background:{c}">{k}</span>' for k, w, c in (("FN", 7, "#2ecc71"), ("MW", 8, "#7bc96f"), ("FT", 23, "#e3b341"), ("WW", 7, "#e67e22"), ("BS", 55, "#c0392b"))) + '<i style="display:none"></i>'

    def mdlinks(s):
        import re
        s = e(s)
        return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    secs = "".join(f"<h2>{e(h)}</h2><p>{mdlinks(p)}</p>" for h, p in t["sec"])
    body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav><span class="pg-eb"><i></i>{e(t["kick"])}</span><h1 class="pg-h">{e(t["h1"])}</h1><p class="lead pg-l">{e(t["lead"])}</p>'
            f'<div class="fc-box"><div class="fc-card"><label for="fcF">{e(L["fl"])}</label><input id="fcF" inputmode="decimal" autocomplete="off" placeholder="{e(L["flph"])}">'
            f'<div class="fc-w" id="fcW">{e(L["none"])}</div><div class="fc-bar" id="fcBar" tabindex="0" role="slider" aria-valuemin="0" aria-valuemax="1">{bar}</div><div class="fc-near" id="fcNear"></div></div>'
            f'<div class="fc-card"><label for="fcS">{e(L["sk"])}</label><input id="fcS" autocomplete="off" spellcheck="false" placeholder="{e(L["skph"])}"><div id="fcOut"><p class="fc-src">{e(L["empty"])}</p></div></div></div>'
            + secs + f'<h2>{e(t["faq_h"])}</h2><div class="faq">{"".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in t["faq"])}</div><p class="note">{e(t["note"])}</p>'
            f'<script>window.FCL={json.dumps(L, ensure_ascii=False)};window.FCCAT={json.dumps(cat, ensure_ascii=False, separators=(",", ":"))};window.FCRATE={rate};window.FCCUR={json.dumps(cur)};</script><script>{JS}</script>')
    h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}{GRID_CSS}</style></head>")
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="fc pg">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
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
