# -*- coding: utf-8 -*-
"""Мини-игра «Что дороже?» (higher or lower по ценам скинов CS2).
python3 admin/game_page.py — пишет data/game.json и страницы /igra-chto-dorozhe/, /en/higher-or-lower-cs2/.
Данные: data/catalog.json (цены по качеству в $, картинки Steam)."""
import json, os, sys, html, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa
from pagegrid import GRID_CSS  # noqa
import csmoney  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/igra-chto-dorozhe/", "en": "/en/higher-or-lower-cs2/"}
WEARS = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
MINP = 0.5  # $

T = {
 "ru": dict(
  title="Что дороже? Игра по скинам CS2 — угадай, какой скин дороже | Skinset",
  desc="Мини-игра по скинам CS2: два скина — какой дороже? Угадывай цены ножей, перчаток и пушек подряд и ставь рекорд. Реальные цены рынка, обновляются каждые 4 часа.",
  kick="Мини-игра", h1="Что дороже?", lead="Перед тобой два скина CS2. Цена первого известна — угадай, второй дороже или дешевле. Каждый правильный ответ — +1 к серии, ошибка — игра заново. Чем дальше, тем ближе цены.",
  hi="Дороже", lo="Дешевле", vs="или", streak="Серия", best="Рекорд", start="Играть", again="Ещё раз", over="Мимо!",
  res="Твоя серия: {n}", newbest="Новый рекорд!", share="Поделиться", copied="Скопировано!", buy="Купить на CS.MONEY",
  sharetxt="Угадал {n} цен скинов CS2 подряд в игре «Что дороже?» 🔥 Побьёшь? ", loading="Загружаю скины…",
  cats=[("all", "Все скины"), ("knife", "Ножи"), ("gloves", "Перчатки"), ("guns", "Оружие")], mode="Режим",
  cur=["", " ₽"], rate=90,
  how_h="Как играть", how=["Слева скин с известной ценой, справа — с неизвестной.", "Нажми «Дороже» или «Дешевле» — угадай, сколько стоит второй скин.", "Угадал — второй скин становится первым и появляется новый. Ошибся — серия обнуляется.", "С каждым правильным ответом цены становятся ближе друг к другу — играть сложнее."],
  faq=[("Откуда цены?", "Это минимальные цены на рынке для указанного качества (Factory New, Field-Tested и т. д.). Они обновляются каждые 4 часа — те же цены, что в конструкторе Skinset."),
       ("Где сохраняется рекорд?", "В твоём браузере. Если почистить данные сайта или зайти с другого устройства, рекорд начнётся заново."),
       ("Почему один и тот же скин стоит по-разному?", "Цена сильно зависит от качества: Factory New часто в разы дороже Battle-Scarred. Поэтому в игре всегда указано качество.")],
  more="Собери свой сет", more_p="Понравились скины? Собери из них инвентарь в одном цвете в конструкторе.", home="Главная"),
 "en": dict(
  title="Higher or Lower: CS2 skin price game — which skin costs more? | Skinset",
  desc="A CS2 skin price game: two skins — which one is more expensive? Guess knife, glove and gun prices in a row and set a record. Real market prices, updated every 4 hours.",
  kick="Mini-game", h1="Higher or Lower", lead="Two CS2 skins. You know the price of the first one — guess whether the second costs more or less. Every right answer adds +1 to your streak, a miss starts over. The further you go, the closer the prices.",
  hi="Higher", lo="Lower", vs="or", streak="Streak", best="Best", start="Play", again="Play again", over="Miss!",
  res="Your streak: {n}", newbest="New record!", share="Share", copied="Copied!", buy="Buy on CS.MONEY",
  sharetxt="I guessed {n} CS2 skin prices in a row in Higher or Lower 🔥 Can you beat it? ", loading="Loading skins…",
  cats=[("all", "All skins"), ("knife", "Knives"), ("gloves", "Gloves"), ("guns", "Guns")], mode="Mode",
  cur=["$", ""], rate=1,
  how_h="How to play", how=["The left skin's price is shown, the right one is hidden.", "Press Higher or Lower to guess the second skin's price.", "Right — the second skin moves left and a new one appears. Wrong — your streak resets.", "With every right answer the prices get closer, so it gets harder."],
  faq=[("Where do the prices come from?", "They're the lowest market prices for the stated wear (Factory New, Field-Tested, etc.), updated every 4 hours — the same prices as in the Skinset builder."),
       ("Where is my record saved?", "In your browser. Clearing site data or switching devices resets it."),
       ("Why does the same skin have different prices?", "Wear matters a lot: Factory New is often several times pricier than Battle-Scarred, so the game always shows the wear.")],
  more="Build your set", more_p="Like these skins? Build a matching loadout from them in the builder.", home="Home"),
}

CSS = """
.gm .modes{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.gm .modes button{padding:9px 14px;background:rgba(255,255,255,.04);border:1px solid var(--line);color:var(--soft);font:600 .78rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
.gm .modes button.on{background:var(--pick,#e8402a);border-color:var(--pick,#e8402a);color:#fff}
.gm .bar{display:flex;gap:18px;align-items:center;margin:0 0 14px;font:600 .9rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}
.gm .bar b{font-size:1.6rem;color:#fff;margin-left:6px;letter-spacing:0}
.gm .bar .bs b{color:#ffcf4a}
.gm .arena{display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:stretch}
.gm .card{position:relative;display:flex;flex-direction:column;border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));padding:16px;min-height:380px;transition:border-color .2s,transform .2s}
.gm .card .im{flex:1;display:grid;place-items:center;min-height:180px;background:radial-gradient(ellipse at center,var(--rc,#e8402a)22 0%,transparent 70%)}
.gm .card img{width:100%;max-width:330px;aspect-ratio:4/3;object-fit:contain;filter:drop-shadow(0 10px 18px rgba(0,0,0,.5))}
.gm .card .wp{font:500 .78rem/1.2 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--soft);margin-top:10px}
.gm .card .nm{font:600 1.3rem/1.15 var(--hud);margin:4px 0 2px}
.gm .card .wr{font-size:.85rem;color:var(--dim)}
.gm .card .pr{margin-top:12px;font:700 2rem/1 var(--hud);min-height:2rem}
.gm .card .pr.q{color:var(--dim)}
.gm .card .bt{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
.gm .card .bt button{height:52px;border:0;font:700 1rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:#fff;cursor:pointer;clip-path:polygon(8px 0,100% 0,100% calc(100% - 8px),calc(100% - 8px) 100%,0 100%,0 8px)}
.gm .card .bt .h{background:#1f9d55}.gm .card .bt .l{background:#c4161c}
.gm .card .bt button:hover{filter:brightness(1.15)}.gm .card .bt button:disabled{opacity:.5;cursor:default}
.gm .card .by{display:none;margin-top:10px;font:600 .72rem/1 var(--hud);letter-spacing:.08em;color:#ff8ccc;text-decoration:none}
.gm .card.shown .by{display:inline-block}
.gm .card.ok{border-color:#1f9d55}.gm .card.bad{border-color:#c4161c}
.gm .vs{display:grid;place-items:center}
.gm .vs span{width:54px;height:54px;border-radius:50%;display:grid;place-items:center;background:#16161d;border:1px solid var(--line);font:700 .8rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}
.gm .ov{display:none;margin:18px 0 0;padding:22px;border:1px solid #c4161c;background:rgba(196,22,28,.08);text-align:center}
.gm .ov.on{display:block}
.gm .ov h2{margin:0 0 6px;font:700 1.8rem/1 var(--hud);text-transform:uppercase}
.gm .ov p{margin:6px 0;color:var(--soft);font-size:1.05rem}.gm .ov .nb{color:#ffcf4a;font-weight:700}
.gm .ov .acts{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:14px}
.gm .ov button,.gm .ov a{height:48px;padding:0 22px;display:inline-flex;align-items:center;border:0;font:700 .9rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:#fff;background:var(--pick,#e8402a);cursor:pointer;text-decoration:none}
.gm .ov .sh{background:#16161d;border:1px solid var(--line)}
.gm .ld{padding:60px 0;text-align:center;color:var(--soft)}
.gm .info{margin-top:40px}.gm .info h2{font:600 1.2rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;margin:28px 0 10px}
.gm .info ol{padding-left:20px;color:var(--soft)}.gm .info h3{font-size:1rem;margin:16px 0 4px}.gm .info p{color:var(--soft);margin:0}
@keyframes gmIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}.gm .card.new{animation:gmIn .35s ease}
@media(max-width:760px){.gm .arena{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}.gm .card{min-width:0;overflow:hidden}.gm .vs{display:none}.gm .card{min-height:0;padding:10px}.gm .card .im{min-height:0}.gm .card img{max-width:170px}.gm .card .wp{font-size:.64rem;margin-top:6px}.gm .card .nm{font-size:.98rem}.gm .card .wr{font-size:.74rem}.gm .card .pr{font-size:1.25rem;margin-top:8px;min-height:1.25rem}.gm .card .bt{grid-template-columns:1fr;gap:6px;margin-top:8px}.gm .card .bt button{height:44px;font-size:.86rem}.gm .card .by{font-size:.62rem}.gm .modes button{padding:8px 10px;font-size:.7rem}}
"""

JS = r"""<script>(()=>{
const L=__L__,CUR=__CUR__,RATE=__RATE__,UTM="__UTM__",IMG="https://community.akamai.steamstatic.com/economy/image/",WN=__WN__,RC=["#b0c3d9","#5e98d9","#4b69ff","#8847ff","#d32ce6","#eb4b4b","#e4ae39","#e4ae39"];
const $=s=>document.querySelector(s);let D=[],pool=[],A=null,B=null,streak=0,best=0,busy=false,mode="all";
try{best=+localStorage.getItem("gm_best")||0}catch(e){}
const fmt=v=>{v=v*RATE;const n=v>=100?Math.round(v):Math.round(v*100)/100;return CUR[0]+n.toLocaleString(RATE===1?"en-US":"ru-RU")+CUR[1]};
const name=x=>x[0]+" ("+WN[x[1]]+")";
const csm=x=>"https://cs.money/market/buy/?search="+encodeURIComponent(x[0].replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,"")+" ("+WN[x[1]]+")")+"&"+UTM;
function setPool(){pool=mode==="all"?D:D.filter(x=>mode==="guns"?!["knife","gloves"].includes(x[4]):x[4]===mode)}
function pick(ref){// чем длиннее серия, тем ближе цены
  const minR=Math.max(1.12,3-streak*0.18),maxR=Math.max(2.2,25-streak*1.5);
  for(let t=0;t<400;t++){const c=pool[Math.random()*pool.length|0];if(!ref)return c;if(c[0]===ref[0])continue;const r=Math.max(c[2],ref[2])/Math.min(c[2],ref[2]);if(r>=minR&&r<=maxR)return c}
  for(let t=0;t<400;t++){const c=pool[Math.random()*pool.length|0];if(c[0]!==ref[0]&&Math.abs(c[2]-ref[2])/ref[2]>0.05)return c}
  return pool[0]}
function card(el,x,show){el.className="card new";el.style.setProperty("--rc",RC[x[5]]||"#e8402a");
  const [w,...s]=x[0].split(" | ");el.querySelector(".im").innerHTML=`<img src="${IMG+x[3]}/360fx270f" alt="${x[0]}" width="330" height="248">`;
  el.querySelector(".wp").textContent=w.replace("★ ","");el.querySelector(".nm").textContent=s.join(" | ")||x[0];el.querySelector(".wr").textContent=WN[x[1]];
  const p=el.querySelector(".pr");p.textContent=show?fmt(x[2]):"?";p.classList.toggle("q",!show);el.classList.toggle("shown",!!show);el.querySelector(".by").href=csm(x);
  setTimeout(()=>el.classList.remove("new"),400)}
function draw(){$("#gs").textContent=streak;$("#gb").textContent=best;card($("#ca"),A,true);card($("#cb"),B,false);$("#cb .bt").hidden=false;$("#cb .bt").querySelectorAll("button").forEach(b=>b.disabled=false)}
function start(){streak=0;setPool();A=pick();B=pick(A);$("#ov").classList.remove("on");draw()}
function count(el,to,cb){const t0=performance.now(),d=700;const f=t=>{const k=Math.min(1,(t-t0)/d);el.textContent=fmt(to*(0.2+0.8*k*k));if(k<1)requestAnimationFrame(f);else{el.textContent=fmt(to);cb()}};requestAnimationFrame(f)}
function guess(hi){if(busy)return;busy=true;$("#cb .bt").querySelectorAll("button").forEach(b=>b.disabled=true);
  const p=$("#cb .pr");p.classList.remove("q");$("#cb").classList.add("shown");
  count(p,B[2],()=>{const ok=hi?B[2]>=A[2]:B[2]<=A[2];$("#cb").classList.add(ok?"ok":"bad");
    setTimeout(()=>{busy=false;if(ok){streak++;if(streak>best){best=streak;try{localStorage.setItem("gm_best",best)}catch(e){}}A=B;B=pick(A);draw()}
      else{const nb=streak>0&&streak>=best;$("#ovr").textContent=L.res.replace("{n}",streak);$("#ovb").textContent=nb?L.newbest:"";$("#ov").classList.add("on");$("#cb .bt").hidden=true;$("#ov").scrollIntoView({behavior:"smooth",block:"nearest"})}},ok?650:300)})}
document.querySelector(".gm").addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;
  if(b.dataset.g)guess(b.dataset.g==="h");else if(b.id==="again")start();else if(b.dataset.m){mode=b.dataset.m;document.querySelectorAll(".modes button").forEach(x=>x.classList.toggle("on",x===b));start()}
  else if(b.id==="share"){const txt=L.sharetxt.replace("{n}",streak)+location.href;if(navigator.share){navigator.share({text:txt}).catch(()=>{})}else{navigator.clipboard&&navigator.clipboard.writeText(txt).then(()=>{b.textContent=L.copied})}}});
fetch("/data/game.json").then(r=>r.json()).then(j=>{D=j.d.map(x=>(x[3]=j.i[x[3]],x));$("#ld").remove();$("#ar").hidden=false;start()}).catch(()=>{$("#ld").textContent="—"});
})()</script>"""


def data():
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json")))
    prices = {}
    try:
        P = json.load(open(os.path.join(ROOT, "data/prices.json")))
    except Exception:
        P = {}
    out = []; imgs = []; ii = {}
    rnd = random.Random(7)
    for x in cat:
        if not x.get("i"): continue
        n = x["n"]
        live = (P.get(n) or {}).get("w") or {}
        wp = [(k, live.get(w) or x["p"][k]) for k, w in enumerate(["FN", "MW", "FT", "WW", "BS"])]
        wp = [(k, v) for k, v in wp if v and v >= MINP]
        if not wp: continue
        # до 2 качеств на скин — больше разнообразия цен
        for k, v in rnd.sample(wp, min(2, len(wp))):
            if x["i"] not in ii: ii[x["i"]] = len(imgs); imgs.append(x["i"])
            out.append([n, k, round(v, 2), ii[x["i"]], x["c"], x.get("r", 0)])
    json.dump({"i": imgs, "d": out}, open(os.path.join(ROOT, "data/game.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return len(out)


def build():
    n = data()
    for lang, url in URL.items():
        t = T[lang]
        L = {k: t[k] for k in ("res", "newbest", "copied", "sharetxt")}
        js = (JS.replace("__L__", json.dumps(L, ensure_ascii=False)).replace("__CUR__", json.dumps(t["cur"], ensure_ascii=False))
              .replace("__RATE__", str(t["rate"])).replace("__UTM__", csmoney.UTM).replace("__WN__", json.dumps(WEARS)))
        side = lambda i, hidden: (f'<div class="card" id="c{i}"><div class="im"></div><div class="wp"></div><div class="nm"></div><div class="wr"></div><div class="pr"></div>'
                                  + (f'<div class="bt"><button class="h" data-g="h">▲ {e(t["hi"])}</button><button class="l" data-g="l">▼ {e(t["lo"])}</button></div>' if hidden else "")
                                  + f'<a class="by" target="_blank" rel="noopener sponsored">{e(t["buy"])} →</a></div>')
        body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav><span class="pg-eb"><i></i>{e(t["kick"])}</span>'
                f'<h1 class="pg-h">{e(t["h1"])}</h1><p class="pg-l">{e(t["lead"])}</p>'
                '<div class="modes">' + "".join(f'<button data-m="{k}"{" class=on" if k == "all" else ""}>{e(l)}</button>' for k, l in t["cats"]) + '</div>'
                f'<div class="bar"><span>{e(t["streak"])}<b id="gs">0</b></span><span class="bs">{e(t["best"])}<b id="gb">0</b></span></div>'
                f'<div class="ld" id="ld">{e(t["loading"])}</div>'
                f'<div class="arena" id="ar" hidden>{side("a", False)}<div class="vs"><span>{e(t["vs"])}</span></div>{side("b", True)}</div>'
                f'<div class="ov" id="ov"><h2>{e(t["over"])}</h2><p id="ovr"></p><p class="nb" id="ovb"></p><div class="acts"><button id="again">{e(t["again"])}</button><button class="sh" id="share">{e(t["share"])}</button></div></div>'
                f'<section class="info"><h2>{e(t["how_h"])}</h2><ol>' + "".join(f"<li>{e(x)}</li>" for x in t["how"]) + "</ol>"
                + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in t["faq"])
                + f'<h2>{e(t["more"])}</h2><p>{e(t["more_p"])} <a href="{HOME[lang]}">{e(t["more"])} →</a></p></section>' + js)
        alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
        ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": t["h1"], "url": SITE + url, "description": t["desc"]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}]
        h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}{GRID_CSS}</style></head>")
        p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="gm pg">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
        p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
        p = navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))
        d = os.path.join(ROOT, url.strip("/")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(p)
    # sitemap
    sp = os.path.join(ROOT, "sitemap.xml"); s = open(sp, encoding="utf-8").read()
    for url in URL.values():
        if f"<loc>{SITE}{url}</loc>" not in s:
            s = s.replace("</urlset>", f"  <url><loc>{SITE}{url}</loc></url>\n</urlset>")
    open(sp, "w", encoding="utf-8").write(s)
    print(n, "game items")


if __name__ == "__main__":
    build()
