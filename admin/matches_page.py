# -*- coding: utf-8 -*-
"""Страница «Матчи CS2»: идущие, предстоящие и прошедшие профессиональные матчи (PandaScore через воркер /matches).
Запуск: python3 admin/matches_page.py  → /matchi-cs2/ и /en/cs2-matches/
"""
import json, os, sys, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/matchi-cs2/", "en": "/en/cs2-matches/"}
W = "https://auth.skin-set.com"
T = {
 "ru": dict(title="Матчи CS2 сегодня: расписание, результаты и live — Skinset",
   desc="Матчи CS2 профессиональных команд: кто играет сейчас, расписание на сегодня и завтра, результаты. Мейджоры, IEM, BLAST, PGL — счёт и трансляции.",
   h1="Матчи CS2", kick="Live · обновляется сам",
   lead="Профессиональные матчи Counter-Strike 2: что идёт прямо сейчас, расписание и результаты. Время — по твоему часовому поясу.",
   home="Главная", note="Данные о матчах: PandaScore. Skinset не связан с организаторами турниров.",
   faq_h="Вопросы и ответы",
   faq=[("Где смотреть матчи CS2?", "У каждого идущего и предстоящего матча есть кнопка трансляции — обычно это Twitch или YouTube организатора турнира. Русскоязычные трансляции показываем первыми."),
        ("Как часто обновляется счёт?", "Идущие матчи обновляются примерно раз в минуту, расписание и результаты — раз в несколько минут."),
        ("Какие турниры здесь есть?", "Все профессиональные турниры, которые отслеживает PandaScore: мейджоры, IEM, BLAST, PGL, ESL Pro League и турниры поменьше. Переключатель «Только топ» оставляет турниры уровней S и A.")],
   L=dict(live="Сейчас идут", up="Предстоящие", past="Результаты", top="Только топ-турниры", watch="Смотреть", vs="vs", tbd="TBD", bo="BO", today="Сегодня", tomorrow="Завтра", yesterday="Вчера",
          empty_live="Сейчас никто не играет — загляни в «Предстоящие».", empty="Матчей не найдено.", load="Загружаем матчи…", notoken="Матчи скоро появятся — подключаем источник данных.", err="Не удалось загрузить матчи, попробуй позже.", all="Показать все турниры", notop="Топ-турниров в этом списке сейчас нет — показываем все матчи.")),
 "en": dict(title="CS2 matches today: schedule, results and live scores — Skinset",
   desc="Pro CS2 matches: who's playing now, today's and tomorrow's schedule, and results. Majors, IEM, BLAST, PGL — scores and streams.",
   h1="CS2 matches", kick="Live · auto-updating",
   lead="Professional Counter-Strike 2 matches: what's live right now, the schedule and results. Times are shown in your time zone.",
   home="Home", note="Match data: PandaScore. Skinset is not affiliated with tournament organizers.",
   faq_h="FAQ",
   faq=[("Where can I watch CS2 matches?", "Every live and upcoming match has a stream button — usually the organizer's Twitch or YouTube channel."),
        ("How often do scores update?", "Live matches refresh about once a minute; schedule and results every few minutes."),
        ("Which tournaments are covered?", "All pro tournaments tracked by PandaScore: Majors, IEM, BLAST, PGL, ESL Pro League and smaller events. The “Top only” switch keeps S and A tier events.")],
   L=dict(live="Live now", up="Upcoming", past="Results", top="Top tournaments only", watch="Watch", vs="vs", tbd="TBD", bo="BO", today="Today", tomorrow="Tomorrow", yesterday="Yesterday",
          empty_live="No matches live right now — check “Upcoming”.", empty="No matches found.", load="Loading matches…", notoken="Matches are coming soon — we're connecting the data source.", err="Couldn't load matches, try again later.", all="Show all tournaments", notop="No top-tier matches in this list right now — showing all matches.")),
}
CSS = """
html,body{overflow-x:clip}
.mt{max-width:1100px;margin:0 auto;padding:22px 24px 60px}
.mt .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:14px}.mt .crumbs a{color:var(--soft)}
.mt h1::before,.mt h2::before{display:none!important}
.mt-kick{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(232,64,42,.14);border:1px solid rgba(232,64,42,.45);color:#ff8a70;font:600 .72rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase}
.mt-kick i,.lv i{width:7px;height:7px;border-radius:50%;background:#ff3b2e;animation:mtP 1.4s infinite}@keyframes mtP{50%{opacity:.25}}
.mt h1{margin:12px 0 8px;font:700 clamp(2.1rem,5vw,3.4rem)/1 var(--hud);text-transform:uppercase}
.mt .lead{color:var(--soft);max-width:720px;margin:0}
.mt-bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;margin:22px 0 14px}
.mt-tabs{display:flex;gap:6px;flex-wrap:wrap}
.mt-tabs button{display:inline-flex;align-items:center;gap:8px;padding:11px 16px;background:rgba(255,255,255,.04);border:1px solid var(--line2,rgba(255,255,255,.14));color:var(--soft);font:600 .8rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
.mt-tabs button.on{background:#e8402a;border-color:#e8402a;color:#fff}.mt-tabs button b{font-weight:700;opacity:.8}
.mt-top{display:inline-flex;align-items:center;gap:8px;font-size:.86rem;color:var(--soft);cursor:pointer;user-select:none}.mt-top input{accent-color:#e8402a;width:16px;height:16px}
.day{margin:22px 0 8px;font:700 .9rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase;color:var(--dim);display:flex;align-items:center;gap:12px}.day::after{content:"";flex:1;height:1px;background:var(--line,rgba(255,255,255,.1))}
.m{display:grid;grid-template-columns:64px minmax(0,1fr) 92px minmax(0,1fr) minmax(0,220px) 124px;gap:12px;align-items:center;padding:12px 14px;margin-bottom:6px;background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1))}
.m{cursor:pointer;transition:border-color .15s}.m:hover{border-color:rgba(255,255,255,.3)}
.m.live{border-color:rgba(232,64,42,.55);background:linear-gradient(90deg,rgba(232,64,42,.12),rgba(255,255,255,.02) 40%)}
.m .tm{font:700 .95rem var(--hud);color:var(--soft)}.m .tm small{display:block;font:600 .66rem/1 var(--hud);letter-spacing:.1em;color:var(--dim);margin-top:4px}
.lv{display:inline-flex;align-items:center;gap:6px;color:#ff6a50!important}
.tt{display:flex;align-items:center;gap:10px;min-width:0;flex-direction:row-reverse;text-align:right}.tt.r{flex-direction:row;text-align:left}
.tt img{width:30px;height:30px;object-fit:contain;flex:none}.tt .ph{width:30px;height:30px;flex:none;background:rgba(255,255,255,.06);border-radius:3px}
.tt b{font:600 .98rem/1.2 var(--body,inherit);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tt.win b{color:#fff}.tt.lose b{color:var(--dim)}
.sc{text-align:center;font:700 1.35rem/1 var(--hud)}.sc .w{color:#2bd67b}.sc .l{color:var(--dim)}.sc small{display:block;font:600 .66rem/1 var(--hud);letter-spacing:.1em;color:var(--dim);margin-top:5px}
.ev{display:flex;align-items:center;gap:8px;min-width:0;font-size:.8rem;color:var(--soft)}.ev img{width:22px;height:22px;object-fit:contain;flex:none}.ev span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ev em{flex:none;font-style:normal;padding:2px 5px;font:700 .62rem/1 var(--hud);letter-spacing:.06em;background:rgba(228,174,57,.2);color:#ffd36a}
.wt{justify-self:end;white-space:nowrap;display:inline-flex;align-items:center;gap:6px;padding:9px 12px;background:#9146ff;color:#fff;text-decoration:none;font:700 .74rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase}.wt.yt{background:#e62117}.wt:hover{filter:brightness(1.12)}
.mt-auto{margin:0 0 6px;font-size:.86rem;color:var(--dim)}
.mt-msg{padding:22px;text-align:center;color:var(--soft);background:rgba(255,255,255,.03);border:1px solid var(--line,rgba(255,255,255,.1))}
.mt .faq h3{margin:16px 0 6px;font:600 1.05rem var(--hud)}.mt .faq p{margin:0;color:var(--soft)}.mt h2{margin:34px 0 10px;font:700 1.35rem/1 var(--hud);text-transform:uppercase}
.mt .note{margin-top:24px;font-size:.8rem;color:var(--dim)}
@media(max-width:860px){.m{grid-template-columns:52px minmax(0,1fr) 70px minmax(0,1fr);row-gap:8px}.m .ev{grid-column:1/-2}.m .wt{grid-column:-2/-1}}
.tt .ts{display:none;font-style:normal}
@media(max-width:600px){.mt{padding:16px 14px 40px}.m{grid-template-columns:50px minmax(0,1fr) auto;grid-template-areas:"tm a w" "tm b w" "ev ev ev";padding:10px;gap:6px 10px}
.m .tm{grid-area:tm}.m .tt{grid-area:a;flex-direction:row;text-align:left}.m .tt.r{grid-area:b;flex-direction:row;text-align:left}.m .sc{display:none}.m .ev{grid-area:ev}.m .wt{grid-area:w;align-self:center;padding:8px 10px}
.m>span:last-child{display:none}
.tt img,.tt .ph{width:22px;height:22px}.tt b{font-size:.9rem;flex:1}.tt .ts{display:block;font:700 1rem var(--hud);margin-left:auto}.tt.win .ts{color:#2bd67b}.tt.lose .ts{color:var(--dim)}}
"""
JS = r"""(()=>{const L=window.MTL,W=__W__,lang=document.documentElement.lang;const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const LS=(k,v)=>{try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}};
let tab="up",top=LS("mt_top")!=="0",D={},timer=null;
const TOP=m=>/^(s|a)$/i.test(m.tier||"");
const fT=d=>new Date(d).toLocaleTimeString(lang,{hour:"2-digit",minute:"2-digit"});
function dayName(d){const x=new Date(d),t=new Date();const k=n=>new Date(t.getFullYear(),t.getMonth(),t.getDate()+n).toDateString();
 if(x.toDateString()===k(0))return L.today;if(x.toDateString()===k(1))return L.tomorrow;if(x.toDateString()===k(-1))return L.yesterday;return x.toLocaleDateString(lang,{weekday:"long",day:"numeric",month:"long"})}
function stream(m){const s=m.tv||[];if(!s.length)return"";const pref=s.find(x=>x.lg===(lang==="ru"?"ru":"en"))||s.find(x=>x.m)||s[0];const yt=/youtu/.test(pref.u);
 return'<a class="wt'+(yt?" yt":"")+'" href="'+esc(pref.u)+'" target="_blank" rel="noopener nofollow">▶ '+esc(L.watch)+(pref.lg?" · "+esc(pref.lg.toUpperCase()):"")+'</a>'}
function team(t,side,res,m){const sv=(m.st==="running"||m.st==="finished")&&res!=null?'<i class="ts">'+res+'</i>':"";if(!t)return'<div class="tt'+(side?" r":"")+'"><span class="ph"></span><b>'+esc(L.tbd)+'</b></div>';
 const cls=m.st==="finished"&&m.w?(m.w===t.id?" win":" lose"):"";return'<div class="tt'+(side?" r":"")+cls+'">'+(t.i?'<img src="'+esc(t.i)+'" alt="" loading="lazy">':'<span class="ph"></span>')+'<b title="'+esc(t.n)+'">'+esc(t.n)+'</b>'+sv+'</div>'}
function row(m){const a=m.t[0],b=m.t[1];const sa=a&&(m.s.find(x=>x.id===a.id)||{}).s,sb=b&&(m.s.find(x=>x.id===b.id)||{}).s;
 const live=m.st==="running",fin=m.st==="finished";
 const sc=(live||fin)&&sa!=null?'<span class="'+(fin?(sa>sb?"w":"l"):"")+'">'+sa+'</span> : <span class="'+(fin?(sb>sa?"w":"l"):"")+'">'+sb+'</span>':'<span style="color:var(--dim);font-size:1rem">'+esc(L.vs)+'</span>';
 return'<div class="m'+(live?" live":"")+'" data-id="'+m.id+'" tabindex="0" role="link"><div class="tm">'+(live?'<span class="lv"><i></i>LIVE</span>':fT(m.b||m.e))+'<small>'+(m.bo?L.bo+m.bo:"")+'</small></div>'+team(a,0,sa,m)+'<div class="sc">'+sc+'</div>'+team(b,1,sb,m)
  +'<div class="ev">'+(m.l&&m.l.i?'<img src="'+esc(m.l.i)+'" alt="" loading="lazy">':'')+'<span title="'+esc((m.l?m.l.n+" · ":"")+m.se)+'">'+esc(m.l?m.l.n:"")+(m.se?" · "+esc(m.se.replace(m.l?m.l.n:"","").trim()):"")+'</span>'+(m.tier?'<em>'+esc(String(m.tier).toUpperCase())+'</em>':'')+'</div>'+(fin||m.st==="canceled"||m.st==="postponed"?'<span></span>':stream(m))+'</div>'}
function draw(){const box=$("#mtList");const d=D[tab];if(!d){box.innerHTML='<div class="mt-msg">'+esc(L.load)+'</div>';return}
 if(d.error==="notoken"){box.innerHTML='<div class="mt-msg">'+esc(L.notoken)+'</div>';return}if(d.error){box.innerHTML='<div class="mt-msg">'+esc(L.err)+'</div>';return}
 let list=(d.list||[]).filter(m=>(m.b||m.e)&&(tab!=="past"||(m.st==="finished"&&m.s.some(x=>x.s>0))));const all=list.length;let auto=false;if(top){const f=list.filter(TOP);if(!f.length&&tab!=="live"&&all){auto=true}else list=f}
 if(!list.length){box.innerHTML='<div class="mt-msg">'+esc(tab==="live"?L.empty_live:L.empty)+(top&&all?'<br><br><button class="lnk" id="mtAll" style="background:none;border:0;color:#66c0f4;cursor:pointer;text-decoration:underline;font:inherit">'+esc(L.all)+' ('+all+')</button>':'')+'</div>';const b=$("#mtAll");if(b)b.onclick=()=>{top=false;$("#mtTop").checked=false;LS("mt_top","0");draw()};return}
 let h=auto?'<p class="mt-auto">'+esc(L.notop)+'</p>':"",cur="";for(const m of list){const dn=tab==="live"?"":dayName(tab==="past"?(m.e||m.b):m.b);if(dn!==cur){cur=dn;if(dn)h+='<div class="day">'+esc(dn)+'</div>'}h+=row(m)}box.innerHTML=h}
async function load(t,force){const map={live:"running",up:"upcoming",past:"past"};if(D[t]&&!force)return;try{const r=await fetch(W+"/matches?type="+map[t]);D[t]=await r.json()}catch(e){D[t]={error:"net"}}
 if(t==="live"){const n=(D.live.list||[]).filter(m=>!top||TOP(m)).length;$("#mtN").textContent=n?n:"";}if(t===tab)draw()}
$("#mtList").addEventListener("click",e=>{if(e.target.closest("a"))return;const r=e.target.closest(".m[data-id]");if(r)location.href=location.pathname.replace(/\/$/,"")+"/match/?id="+r.dataset.id});
$("#mtList").addEventListener("keydown",e=>{if(e.key==="Enter"){const r=e.target.closest(".m[data-id]");if(r)location.href=location.pathname.replace(/\/$/,"")+"/match/?id="+r.dataset.id}});
$("#mtTabs").addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;tab=b.dataset.t;$("#mtTabs").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));draw();load(tab)});
const tp=$("#mtTop");tp.checked=top;tp.onchange=()=>{top=tp.checked;LS("mt_top",top?"1":"0");load("live");draw()};
(async()=>{await load("live");const n=(D.live&&D.live.list||[]).filter(m=>!top||TOP(m)).length;if(n){tab="live";$("#mtTabs").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.t==="live"))}draw();load("up");load("past")})();
setInterval(()=>{load("live",true)},60000);setInterval(()=>{load("up",true)},300000)})();"""


def build(lang):
    t = T[lang]; url = URL[lang]; L = t["L"]
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": t["h1"], "url": SITE + url, "description": t["desc"]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
    body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav><span class="mt-kick"><i></i>{e(t["kick"])}</span><h1>{e(t["h1"])}</h1><p class="lead">{e(t["lead"])}</p>'
            f'<div class="mt-bar"><div class="mt-tabs" id="mtTabs"><button data-t="live"><span class="lv"><i></i></span>{e(L["live"])} <b id="mtN"></b></button><button data-t="up" class="on">{e(L["up"])}</button><button data-t="past">{e(L["past"])}</button></div>'
            f'<label class="mt-top"><input type="checkbox" id="mtTop"> {e(L["top"])}</label></div><div id="mtList"><div class="mt-msg">{e(L["load"])}</div></div>'
            f'<h2>{e(t["faq_h"])}</h2><div class="faq">{"".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in t["faq"])}</div><p class="note">{e(t["note"])}</p>'
            f'<script>window.MTL={json.dumps(L, ensure_ascii=False)};</script><script>{JS.replace("__W__", json.dumps(W))}</script>')
    h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}</style></head>")
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="mt">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


DT = {
 "ru": dict(title="Матч CS2: счёт, карты и составы — Skinset", back="← Все матчи", maps="Карты", map="Карта", won="победа", lineups="Составы", watch_h="Трансляции", tour="Турнир", start="Начало", fmt="Формат",
   st={"not_started": "Скоро", "running": "LIVE", "finished": "Завершён", "canceled": "Отменён", "postponed": "Перенесён"}, nomaps="Подробности по картам появятся после начала матча.", nost="Детальная статистика игроков и карт пока недоступна.",
   h2h="Последние встречи", nf="Матч не найден.", load="Загружаем матч…", forfeit="техническая победа", tbd="Будет известно позже", vs="vs", upd="Обновляется автоматически", nolineup="Состав пока неизвестен"),
 "en": dict(title="CS2 match: score, maps and lineups — Skinset", back="← All matches", maps="Maps", map="Map", won="win", lineups="Lineups", watch_h="Streams", tour="Tournament", start="Start", fmt="Format",
   st={"not_started": "Upcoming", "running": "LIVE", "finished": "Finished", "canceled": "Canceled", "postponed": "Postponed"}, nomaps="Map details will appear once the match starts.", nost="Detailed player and map stats are not available yet.",
   h2h="Recent meetings", nf="Match not found.", load="Loading match…", forfeit="forfeit", tbd="To be decided", vs="vs", upd="Updates automatically", nolineup="Lineup not available yet"),
}
DCSS = """
html,body{overflow-x:clip}
.md{max-width:1000px;margin:0 auto;padding:22px 24px 60px}.md .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:14px}.md .crumbs a{color:var(--soft)}
.md h2::before{display:none!important}
.mh{position:relative;padding:22px 24px;background:radial-gradient(90% 140% at 50% 0%,rgba(232,64,42,.25),transparent 60%),linear-gradient(160deg,#16171b,#0c0d10);border:1px solid var(--line2,rgba(255,255,255,.14))}
.mh .ev{display:flex;justify-content:center;align-items:center;gap:8px;font-size:.86rem;color:var(--soft);margin-bottom:16px;text-align:center}.mh .ev img{width:24px;height:24px;object-fit:contain}
.mh .row{display:grid;grid-template-columns:1fr auto 1fr;gap:18px;align-items:center}
.mh .tm{display:flex;flex-direction:column;align-items:center;gap:10px;text-align:center;min-width:0}.mh .tm img{width:88px;height:88px;object-fit:contain}.mh .tm img.flg{width:24px;height:18px;object-fit:cover}.mh .tm .ph{width:88px;height:88px;background:rgba(255,255,255,.06)}
.mh .tm b{font:700 1.4rem/1.1 var(--hud);text-transform:uppercase;overflow-wrap:anywhere}.mh .tm.lose{opacity:.55}
.mh .sc{text-align:center}.mh .sc b{display:block;font:700 3.2rem/1 var(--hud)}.mh .sc .w{color:#2bd67b}
.mh .sc span{display:inline-block;margin-top:8px;padding:5px 10px;font:700 .72rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;background:rgba(255,255,255,.08);color:var(--soft)}.mh .sc span.lv{background:#e8402a;color:#fff}
.mh .meta{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 22px;margin-top:18px;font-size:.84rem;color:var(--soft)}.mh .meta b{color:var(--ink,#fff);font-weight:600}
.md h2{margin:28px 0 12px;font:700 1.25rem/1 var(--hud);text-transform:uppercase}
.gm{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
.g{padding:14px 16px;background:rgba(255,255,255,.04);border:1px solid var(--line,rgba(255,255,255,.1));border-top:3px solid var(--c,#444)}
.g small{font:600 .7rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}.g b{display:block;margin:8px 0 4px;font:700 1.1rem var(--hud);text-transform:uppercase}.g span{font-size:.84rem;color:var(--soft)}
.ln{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.lt{background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1))}.lt h3{display:flex;align-items:center;gap:10px;margin:0;padding:12px 14px;font:700 1rem var(--hud);text-transform:uppercase;border-bottom:1px solid var(--line,rgba(255,255,255,.1))}.lt h3 img{width:26px;height:26px;object-fit:contain}
.pl{display:flex;align-items:center;gap:10px;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,.05)}.pl:last-child{border-bottom:0}.pl .fl{width:22px;display:flex}.flg{width:20px;height:15px;object-fit:cover;border-radius:2px;vertical-align:middle}.pl b{font-weight:700}.pl small{color:var(--dim);font-size:.8rem;margin-left:auto;text-align:right}
.tvs{display:flex;flex-wrap:wrap;gap:8px}.tvs a{display:inline-flex;gap:6px;align-items:center;padding:10px 14px;background:#9146ff;color:#fff;text-decoration:none;font:700 .78rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase}.tvs a.yt{background:#e62117}.tvs a.o{background:rgba(255,255,255,.08)}
.md .note,.md .msg{margin-top:12px;font-size:.84rem;color:var(--dim)}.md .msg{padding:20px;text-align:center;background:rgba(255,255,255,.03);border:1px solid var(--line,rgba(255,255,255,.1));color:var(--soft)}
.h2h .m2{display:grid;grid-template-columns:110px 1fr auto 1fr;gap:10px;align-items:center;padding:9px 14px;background:rgba(255,255,255,.03);border:1px solid var(--line,rgba(255,255,255,.08));margin-bottom:6px;font-size:.88rem;color:var(--soft);text-decoration:none}.h2h .m2 b{color:#fff}.h2h .m2 .r{text-align:right}
@media(max-width:700px){.gm{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}.g{padding:10px}.g b{font-size:.95rem;overflow-wrap:anywhere}.md{padding:16px 14px 40px}.mh{padding:18px 12px}.mh .tm img,.mh .tm .ph{width:56px;height:56px}.mh .tm b{font-size:1rem}.mh .sc b{font-size:2.4rem}.ln{grid-template-columns:1fr}.h2h .m2{grid-template-columns:80px 1fr auto 1fr;font-size:.8rem;padding:8px}}
"""
DJS = r"""(()=>{const L=window.MDL,W=__W__,lang=document.documentElement.lang,$=s=>document.querySelector(s);const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const id=new URLSearchParams(location.search).get("id");const flag=c=>c&&/^[a-z]{2}$/i.test(c)?'<img class="flg" src="https://flagcdn.com/w40/'+c.toLowerCase()+'.png" alt="'+c+'" title="'+c+'" width="20" height="15" loading="lazy">':"";
const fD=d=>d?new Date(d).toLocaleString(lang,{weekday:"short",day:"numeric",month:"long",hour:"2-digit",minute:"2-digit"}):"—";
async function load(){if(!id){$("#md").innerHTML='<div class="msg">'+esc(L.nf)+'</div>';return}let m;try{const r=await fetch(W+"/match?id="+encodeURIComponent(id));m=await r.json();if(!r.ok||m.error)throw 0}catch(e){$("#md").innerHTML='<div class="msg">'+esc(L.nf)+'</div>';return}
 const[a,b]=[m.t[0],m.t[1]];const sc=t=>t?((m.s.find(x=>x.id===t.id)||{}).s):null;const sa=sc(a),sb=sc(b),fin=m.st==="finished",live=m.st==="running";
 document.title=(a?a.n:"TBD")+" vs "+(b?b.n:"TBD")+" — "+(m.l?m.l.n:"CS2")+" | Skinset";
 const tm=(t,s)=>'<div class="tm'+(fin&&m.w&&t&&m.w!==t.id?" lose":"")+'">'+(t&&t.i?'<img src="'+esc(t.i)+'" alt="">':'<span class="ph"></span>')+'<b>'+esc(t?t.n:L.tbd)+'</b>'+(t&&t.c?'<small>'+flag(t.c)+'</small>':'')+'</div>';
 let h='<div class="mh"><div class="ev">'+(m.l&&m.l.i?'<img src="'+esc(m.l.i)+'" alt="">':'')+'<span>'+esc((m.l?m.l.n:"")+(m.se?" · "+m.se:"")+(m.tu?" · "+m.tu:""))+'</span></div><div class="row">'+tm(a)
  +'<div class="sc">'+((fin||live)&&sa!=null?'<b><span class="'+(sa>sb?"w":"")+'" style="all:unset;color:'+(fin&&sa>sb?"#2bd67b":"inherit")+'">'+sa+'</span> : <span style="all:unset;color:'+(fin&&sb>sa?"#2bd67b":"inherit")+'">'+sb+'</span></b>':'<b style="font-size:1.6rem;color:var(--dim)">'+L.vs+'</b>')+'<span class="'+(live?"lv":"")+'">'+esc(L.st[m.st]||m.st)+(m.fw?" · "+esc(L.forfeit):"")+'</span></div>'+tm(b)+'</div>'
  +'<div class="meta"><span>'+esc(L.start)+': <b>'+esc(fD(m.b))+'</b></span><span>'+esc(L.fmt)+': <b>BO'+(m.bo||"?")+'</b></span>'+(m.tier?'<span>Tier: <b>'+esc(String(m.tier).toUpperCase())+'</b></span>':'')+'</div></div>';
 const gs=(m.g||[]).filter(g=>g.st!=="not_started"||g.map);
 h+='<h2>'+esc(L.maps)+'</h2>'+(gs.length?'<div class="gm">'+gs.map(g=>{const wt=m.t.find(t=>t.id===g.w);return'<div class="g" style="--c:'+(wt?(wt===a?"#e8402a":"#2d73ff"):"#444")+'"><small>'+esc(L.map)+' '+g.p+'</small><b>'+esc(g.map?g.map.n:(wt?(wt.a||wt.n):(g.st==="running"?"LIVE":"—")))+'</b><span>'+(wt?(g.map?esc(wt.n)+" — ":"")+esc(L.won):esc(L.st[g.st]||g.st))+'</span></div>'}).join("")+'</div><p class="note">'+esc(L.nost)+'</p>':'<div class="msg">'+esc(L.nomaps)+'</div>');
 if(m.t.some(t=>t.pl&&t.pl.length))h+='<h2>'+esc(L.lineups)+'</h2><div class="ln">'+m.t.map(t=>'<div class="lt"><h3>'+(t.i?'<img src="'+esc(t.i)+'" alt="">':'')+esc(t.n)+'</h3>'+((t.pl||[]).length?"":'<div class="pl"><small style="margin:0">'+esc(L.nolineup)+'</small></div>')+(t.pl||[]).map(p=>'<div class="pl"><span class="fl">'+flag(p.c)+'</span><b>'+esc(p.n)+'</b><small>'+esc(p.f||"")+'</small></div>').join("")+'</div>').join("")+'</div>';
 if(m.tv&&m.tv.length&&!fin)h+='<h2>'+esc(L.watch_h)+'</h2><div class="tvs">'+m.tv.sort((x,y)=>(y.lg===lang)-(x.lg===lang)||y.m-x.m).map(s=>'<a class="'+(/youtu/.test(s.u)?"yt":/twitch/.test(s.u)?"":"o")+'" href="'+esc(s.u)+'" target="_blank" rel="noopener nofollow">▶ '+esc((s.lg||"").toUpperCase())+(s.o?" · official":"")+'</a>').join("")+'</div>';
 h+='<div id="h2h"></div><p class="note">'+(live?esc(L.upd)+' · ':'')+'PandaScore</p>';$("#md").innerHTML=h;
 if(a&&b){try{const p=await (await fetch(W+"/matches?type=past")).json();const hh=(p.list||[]).filter(x=>x.id!==m.id&&x.t.length===2&&x.t.some(t=>t.id===a.id)&&x.t.some(t=>t.id===b.id)).slice(0,5);
  if(hh.length)$("#h2h").innerHTML='<h2>'+esc(L.h2h)+'</h2><div class="h2h">'+hh.map(x=>{const s1=(x.s.find(y=>y.id===x.t[0].id)||{}).s,s2=(x.s.find(y=>y.id===x.t[1].id)||{}).s;return'<a class="m2" href="?id='+x.id+'"><span>'+esc(new Date(x.e||x.b).toLocaleDateString(lang))+'</span><b>'+esc(x.t[0].n)+'</b><span>'+s1+' : '+s2+'</span><b class="r">'+esc(x.t[1].n)+'</b></a>'}).join("")+'</div>'}catch(e){}}
 if(live)setTimeout(load,60000)}load()})();"""


def build_detail(lang):
    t = DT[lang]; url = URL[lang] + "match/"
    body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(T[lang]["home"])}</a> › <a href="{URL[lang]}">{e(T[lang]["h1"])}</a></nav>'
            f'<p><a href="{URL[lang]}" style="color:#66c0f4;text-decoration:none">{e(t["back"])}</a></p><div id="md"><div class="msg">{e(t["load"])}</div></div>'
            f'<script>window.MDL={json.dumps(t, ensure_ascii=False)};</script><script>{DJS.replace("__W__", json.dumps(W))}</script>')
    h = head(lang, t["title"], t["title"], SITE + url, "", []).replace("</head>", f'<meta name="robots" content="noindex,follow"><style>{DCSS}</style></head>')
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="md">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


def main():
    for lang in URL:
        f = os.path.join(ROOT, URL[lang].strip("/"), "index.html"); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(build(lang))
        f2 = os.path.join(ROOT, (URL[lang] + "match/").strip("/"), "index.html"); os.makedirs(os.path.dirname(f2), exist_ok=True)
        open(f2, "w", encoding="utf-8").write(build_detail(lang))
    sm = os.path.join(ROOT, "sitemap.xml"); xml = open(sm, encoding="utf-8").read()
    for u in URL.values():
        if f"<loc>{SITE}{u}</loc>" not in xml: xml = xml.replace("</urlset>", f"  <url><loc>{SITE}{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n</urlset>")
    open(sm, "w", encoding="utf-8").write(xml)
    print("ok")


if __name__ == "__main__":
    main()
