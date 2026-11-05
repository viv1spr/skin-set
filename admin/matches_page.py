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
from pagegrid import GRID_CSS  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/matchi-cs2/", "en": "/en/cs2-matches/"}
W = "https://auth.skin-set.com"
T = {
 "ru": dict(title="Матчи КС 2 сегодня: расписание, результаты и трансляции CS2 — Skinset",
   desc="Матчи КС 2 (CS2) сегодня и завтра: расписание, live-счёт, результаты и ссылки на трансляции. NAVI, Spirit, Vitality, FURIA и другие — IEM, BLAST, PGL, мейджоры.",
   h1="Матчи КС 2 сегодня", kick="Live · обновляется сам",
   lead="Профессиональные матчи Counter-Strike 2: что идёт прямо сейчас, расписание и результаты. Время — по твоему часовому поясу.",
   home="Главная", note="Данные о матчах: PandaScore. Skinset не связан с организаторами турниров.",
   faq_h="Вопросы и ответы",
   faq=[("Где смотреть матчи CS2?", "У каждого идущего и предстоящего матча есть кнопка трансляции — обычно это Twitch или YouTube организатора турнира. Русскоязычные трансляции показываем первыми."),
        ("Как часто обновляется счёт?", "Идущие матчи обновляются примерно раз в минуту, расписание и результаты — раз в несколько минут."),
        ("Какие турниры здесь есть?", "Все профессиональные турниры, которые отслеживает PandaScore: мейджоры, IEM, BLAST, PGL, ESL Pro League и турниры поменьше. Переключатель «Только топ» оставляет турниры уровней S и A."),
        ("Что значат S, A, B, C, D у турнира?", "Это уровень турнира. S — мейджоры и самые крупные события вроде IEM и BLAST с топ-командами, A — крупные турниры, B–D — региональные лиги, квалификации и онлайн-кубки."),
        ("Что такое BO1, BO3 и BO5?", "Формат матча: сколько карт играют. BO1 — одна карта, BO3 — до двух побед из трёх карт, BO5 — до трёх побед, обычно в гранд-финалах."),
        ("В каком часовом поясе время матчей?", "Время показано по часовому поясу твоего устройства, поэтому переводить ничего не нужно.")],
   L=dict(live="Сейчас идут", up="Предстоящие", past="Результаты", top="Только топ-турниры", watch="Смотреть", vs="vs", tbd="TBD", bo="BO", today="Сегодня", tomorrow="Завтра", yesterday="Вчера",
          empty_live="Сейчас никто не играет — загляни в «Предстоящие».", empty="Матчей не найдено.", load="Загружаем матчи…", notoken="Матчи скоро появятся — подключаем источник данных.", err="Не удалось загрузить матчи, попробуй позже.", all="Показать все турниры", notop="Топ-турниров в этом списке сейчас нет — показываем все матчи.", s_live="Live сейчас", s_today="Матчей сегодня", s_tours="Турниров", s_main="Главный турнир", feat="Главный матч", starts="Начало через", h="ч", mn="мин", now="Идёт сейчас", tours_h="Турниры сейчас", matches="матчей", next="Следующий", allt="Все турниры", res_h="Последние результаты", sched_h="Расписание матчей КС 2")),
 "en": dict(title="CS2 matches today: schedule, live scores, results and streams — Skinset",
   desc="Pro CS2 matches: who's playing now, today's and tomorrow's schedule, and results. Majors, IEM, BLAST, PGL — scores and streams.",
   h1="CS2 matches today", kick="Live · auto-updating",
   lead="Professional Counter-Strike 2 matches: what's live right now, the schedule and results. Times are shown in your time zone.",
   home="Home", note="Match data: PandaScore. Skinset is not affiliated with tournament organizers.",
   faq_h="FAQ",
   faq=[("Where can I watch CS2 matches?", "Every live and upcoming match has a stream button — usually the organizer's Twitch or YouTube channel."),
        ("How often do scores update?", "Live matches refresh about once a minute; schedule and results every few minutes."),
        ("Which tournaments are covered?", "All pro tournaments tracked by PandaScore: Majors, IEM, BLAST, PGL, ESL Pro League and smaller events. The “Top only” switch keeps S and A tier events."),
        ("What do S, A, B, C, D tiers mean?", "Tournament level. S is Majors and the biggest events like IEM and BLAST with top teams, A is big tournaments, B–D are regional leagues, qualifiers and online cups."),
        ("What do BO1, BO3 and BO5 mean?", "Match format: how many maps are played. BO1 is one map, BO3 is first to two maps, BO5 is first to three, usually in grand finals."),
        ("What time zone are match times in?", "Times are shown in your device's time zone, so there's nothing to convert.")],
   L=dict(live="Live now", up="Upcoming", past="Results", top="Top tournaments only", watch="Watch", vs="vs", tbd="TBD", bo="BO", today="Today", tomorrow="Tomorrow", yesterday="Yesterday",
          empty_live="No matches live right now — check “Upcoming”.", empty="No matches found.", load="Loading matches…", notoken="Matches are coming soon — we're connecting the data source.", err="Couldn't load matches, try again later.", all="Show all tournaments", notop="No top-tier matches in this list right now — showing all matches.", s_live="Live now", s_today="Matches today", s_tours="Tournaments", s_main="Main event", feat="Match of the day", starts="Starts in", h="h", mn="min", now="Live now", tours_h="Tournaments now", matches="matches", next="Next", allt="All tournaments", res_h="Latest results", sched_h="CS2 match schedule")),
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
.mx-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:22px 0 0}
.mx-stats div{padding:14px 16px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));border:1px solid var(--line,rgba(255,255,255,.1))}
.mx-stats b{display:block;font:700 1.9rem/1 var(--hud)}.mx-stats small{display:block;margin-top:6px;font:600 .68rem/1.2 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}
.mx-stats .lvb b{color:#ff6a50}.mx-stats .mn b{font-size:1.15rem;line-height:1.15;padding-top:6px}
.mx-feat{position:relative;margin:14px 0 0;padding:20px 22px;background:radial-gradient(80% 140% at 50% 0%,rgba(232,64,42,.28),transparent 60%),linear-gradient(160deg,#17181d,#0c0d10);border:1px solid rgba(232,64,42,.45);cursor:pointer}
.mx-feat .hd{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;font:600 .74rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase;color:#ff8a70}
.mx-feat .hd span{color:var(--soft);letter-spacing:.08em}
.mx-feat .row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,auto) minmax(0,1fr);gap:16px;align-items:center;margin-top:16px}
.mx-feat .tm{display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center;min-width:0}.mx-feat .tm img,.mx-feat .tm .ph{width:76px;height:76px;object-fit:contain}.mx-feat .tm .ph{background:rgba(255,255,255,.06);border-radius:6px}
.mx-feat .tm b{font:700 1.35rem/1.1 var(--hud);text-transform:uppercase;overflow-wrap:break-word;word-break:normal;max-width:100%}
.mx-feat .mid{text-align:center;max-width:300px}.mx-feat .mid b{display:block;font:700 2.4rem/1 var(--hud)}.mx-feat .mid small{display:block;margin-top:8px;font:600 .72rem/1.3 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--soft)}
.mx-feat .mid .cd{color:#ffd36a}.mx-feat .ft{display:flex;justify-content:center;gap:10px;margin-top:16px}
.mx-tr{display:flex;gap:10px;overflow-x:auto;padding-bottom:8px;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.25) transparent}.mx-tr::-webkit-scrollbar{height:6px}.mx-tr::-webkit-scrollbar-track{background:transparent}.mx-tr::-webkit-scrollbar-thumb{background:rgba(255,255,255,.22);border-radius:3px}
.mx-tr button{flex:none;min-width:190px;max-width:230px;text-align:left;padding:12px 14px;background:rgba(255,255,255,.04);border:1px solid var(--line,rgba(255,255,255,.1));color:var(--ink,#fff);cursor:pointer;font:inherit}
.mx-tr button:hover,.mx-tr button.on{border-color:#e8402a;background:rgba(232,64,42,.1)}
.mx-tr .tn{display:flex;align-items:center;gap:8px}.mx-tr .tn img,.mx-tr .tn .lg{width:26px;height:26px;object-fit:contain;flex:none}.mx-tr .tn .lg{display:grid;place-items:center;background:rgba(255,255,255,.08);font:700 .7rem var(--hud)}
.mx-tr .tn b{font:700 .92rem/1.15 var(--hud);text-transform:uppercase;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.mx-tr small{display:block;margin-top:8px;font-size:.78rem;color:var(--soft)}
.tier{display:inline-block;padding:2px 6px;font:700 .62rem/1 var(--hud);letter-spacing:.06em;margin-left:auto;flex:none}
.tier.s{background:rgba(228,174,57,.25);color:#ffd36a}.tier.a{background:rgba(232,64,42,.22);color:#ff8a70}.tier.b{background:rgba(102,192,244,.2);color:#8fd0ff}.tier.c,.tier.d{background:rgba(255,255,255,.08);color:var(--soft)}
.mx-res{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.mx-res a{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:10px;align-items:center;padding:9px 12px;background:rgba(255,255,255,.03);border:1px solid var(--line,rgba(255,255,255,.08));color:var(--ink,#fff);text-decoration:none;font-size:.9rem}
.mx-res a span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.mx-res a span:last-child{text-align:right}.mx-res a b{font:700 1rem var(--hud)}.mx-res .w{color:#2bd67b}
@media(max-width:760px){.mx-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.mx-feat .tm img,.mx-feat .tm .ph{width:52px;height:52px}.mx-feat .tm b{font-size:1rem}.mx-feat .mid b{font-size:1.8rem}.mx-feat .mid{max-width:120px}.mx-feat .mid small{font-size:.62rem;letter-spacing:.06em}.mx-feat{padding:16px 12px}.mx-res{grid-template-columns:1fr}}
"""
JS = r"""(()=>{const L=window.MTL,W=__W__,lang=document.documentElement.lang;const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const LS=(k,v)=>{try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}};
let tab="up",top=LS("mt_top")!=="0",D={},timer=null,TF=null;const tk=m=>(((m.l||{}).n||"")+" "+(m.se||"")).trim();const TRK={s:0,a:1,b:2,c:3,d:4};const PL=n=>{if(lang!=="ru")return n+" "+(n===1?"match":"matches");const a=n%10,b=n%100;return n+" "+(a===1&&b!==11?"матч":a>=2&&a<=4&&(b<12||b>14)?"матча":"матчей")};
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
 let list=(d.list||[]).filter(m=>(m.b||m.e)&&(tab!=="past"||(m.st==="finished"&&m.s.some(x=>x.s>0))));if(TF)list=list.filter(m=>tk(m)===TF);const all=list.length;let auto=false;if(top&&!TF){const f=list.filter(TOP);if(!f.length&&tab!=="live"&&all){auto=true}else list=f}
 if(!list.length){box.innerHTML='<div class="mt-msg">'+esc(tab==="live"?L.empty_live:L.empty)+(top&&all?'<br><br><button class="lnk" id="mtAll" style="background:none;border:0;color:#66c0f4;cursor:pointer;text-decoration:underline;font:inherit">'+esc(L.all)+' ('+all+')</button>':'')+'</div>';const b=$("#mtAll");if(b)b.onclick=()=>{top=false;$("#mtTop").checked=false;LS("mt_top","0");draw()};return}
 let h=auto?'<p class="mt-auto">'+esc(L.notop)+'</p>':"",cur="";for(const m of list){const dn=tab==="live"?"":dayName(tab==="past"?(m.e||m.b):m.b);if(dn!==cur){cur=dn;if(dn)h+='<div class="day">'+esc(dn)+'</div>'}h+=row(m)}box.innerHTML=h}
async function load(t,force){const map={live:"running",up:"upcoming",past:"past"};if(D[t]&&!force)return;try{const r=await fetch(W+"/matches?type="+map[t]);D[t]=await r.json()}catch(e){D[t]={error:"net"}}
 if(t==="live"){const n=(D.live.list||[]).filter(m=>!top||TOP(m)).length;$("#mtN").textContent=n?n:"";}if(t==="live"||t==="up")renderTop();if(t===tab)draw()}
$("#mtList").addEventListener("click",e=>{if(e.target.closest("a"))return;const r=e.target.closest(".m[data-id]");if(r)location.href=location.pathname.replace(/\/$/,"")+"/match/?id="+r.dataset.id});
$("#mtList").addEventListener("keydown",e=>{if(e.key==="Enter"){const r=e.target.closest(".m[data-id]");if(r)location.href=location.pathname.replace(/\/$/,"")+"/match/?id="+r.dataset.id}});
$("#mtTabs").addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;tab=b.dataset.t;$("#mtTabs").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));draw();load(tab)});
const tp=$("#mtTop");tp.checked=top;tp.onchange=()=>{top=tp.checked;LS("mt_top",top?"1":"0");load("live");draw()};

function cd(b){const ms=new Date(b)-Date.now();if(ms<=0)return L.now;const h=Math.floor(ms/36e5),mi=Math.floor(ms%36e5/6e4);return L.starts+" "+(h?h+" "+L.h+" ":"")+mi+" "+L.mn}
function logo(t){return t&&t.i?'<img src="'+esc(t.i)+'" alt="">':'<span class="ph"></span>'}
function renderTop(){const lv=(D.live&&D.live.list)||[],up=(D.up&&D.up.list)||[];if(!D.live&&!D.up)return;const all=lv.concat(up);
 const td=new Date().toDateString();const nToday=lv.length+up.filter(m=>m.b&&new Date(m.b).toDateString()===td).length;
 const T={};for(const m of all){const k=tk(m);if(!k)continue;const o=T[k]||(T[k]={k,n:k,i:(m.l||{}).i,tier:(m.tier||"d").toLowerCase(),c:0,b:m.b||""});o.c++;if(m.b&&(!o.b||m.b<o.b))o.b=m.b}
 const tl=Object.values(T).sort((a,b)=>(TRK[a.tier]??5)-(TRK[b.tier]??5)||(a.b<b.b?-1:1));
 const st=$("#mxStats");if(st)st.innerHTML='<div class="lvb"><b>'+lv.length+'</b><small>'+esc(L.s_live)+'</small></div><div><b>'+nToday+'</b><small>'+esc(L.s_today)+'</small></div><div><b>'+tl.length+'</b><small>'+esc(L.s_tours)+'</small></div><div class="mn"><b>'+esc(tl[0]?tl[0].n:"—")+'</b><small>'+esc(L.s_main)+'</small></div>';
 const f=lv.find(TOP)||up.find(TOP)||lv[0]||up[0];const fe=$("#mxFeat");
 if(f&&fe){const a=f.t[0],b=f.t[1];const sa=a&&(f.s.find(x=>x.id===a.id)||{}).s,sb=b&&(f.s.find(x=>x.id===b.id)||{}).s;const live=f.st==="running";const stage=(f.name||"").includes(":")?f.name.split(":")[0]:"";
  fe.dataset.id=f.id;fe.innerHTML='<div class="hd">'+(live?'<span class="lv"><i></i>LIVE</span>':esc(L.feat))+'<span>'+esc(tk(f))+(stage?" · "+esc(stage):"")+'</span></div><div class="row"><div class="tm">'+logo(a)+'<b>'+esc(a?a.n:L.tbd)+'</b></div><div class="mid"><b>'+(live&&sa!=null?sa+" : "+sb:"vs")+'</b><small class="cd" data-b="'+esc(f.b||"")+'">'+esc(live?L.now:(f.b?new Date(f.b).toLocaleString(lang,{weekday:"short",day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"})+" · "+cd(f.b):""))+'</small><small>BO'+(f.bo||"?")+'</small></div><div class="tm">'+logo(b)+'<b>'+esc(b?b.n:L.tbd)+'</b></div></div>'+(f.tv&&f.tv.length?'<div class="ft">'+stream(f)+'</div>':'')}
 const tr=$("#mxTours");if(tr)tr.innerHTML=(TF?'<button data-k=""><span class="tn"><b>'+esc(L.allt)+'</b></span><small>×</small></button>':'')+tl.slice(0,10).map(o=>'<button data-k="'+esc(o.k)+'"'+(TF===o.k?' class="on"':'')+'><span class="tn">'+(o.i?'<img src="'+esc(o.i)+'" alt="">':'<span class="lg">'+esc(o.n.slice(0,2).toUpperCase())+'</span>')+'<b>'+esc(o.n)+'</b><i class="tier '+o.tier+'">'+o.tier.toUpperCase()+'</i></span><small>'+PL(o.c)+(o.b?' · '+esc(L.next)+' '+new Date(o.b).toLocaleString(lang,{day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"}):'')+'</small></button>').join("")}
document.addEventListener("click",e=>{const b=e.target.closest("#mxTours button");if(b){TF=b.dataset.k||null;if(TF&&tab==="past"){}renderTop();draw();const h=$("#schedH");if(h)h.scrollIntoView({behavior:"smooth",block:"start"});return}
 const f=e.target.closest("#mxFeat");if(f&&!e.target.closest("a")&&f.dataset.id)location.href=location.pathname.replace(/\/$/,"")+"/match/?id="+f.dataset.id});
setInterval(()=>{const c=document.querySelector("#mxFeat .cd[data-b]");if(c&&c.dataset.b&&new Date(c.dataset.b)>Date.now())renderTop()},30000);
(async()=>{await load("live");const n=(D.live&&D.live.list||[]).filter(m=>!top||TOP(m)).length;if(n){tab="live";$("#mtTabs").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.t==="live"))}draw();load("up");load("past")})();
setInterval(()=>{load("live",true)},60000);setInterval(()=>{load("up",true)},300000)})();"""


import csmoney  # noqa
PRO_SKINS = ["AWP | Asiimov", "M4A1-S | Printstream", "Desert Eagle | Blaze", "USP-S | Kill Confirmed", "AK-47 | Bloodsport", "★ Butterfly Knife | Doppler (Phase 2)"]
PRO_T = {"ru": ("Скины, которыми играют про-игроки", "Что у s1mple, NiKo, ZywOo, donk и других — в нашем разборе", "/blog/skiny-pro-igrokov-cs2/", "Купить на CS.MONEY"),
         "en": ("Skins the pros play with", "What s1mple, NiKo, ZywOo, donk and others use — full breakdown", "/en/blog/skiny-pro-igrokov-cs2/", "Buy on CS.MONEY")}
PRO_CSS = (".pro{margin:30px 0 8px}.pro h2{margin:0 0 6px}.pro p.sub{margin:0 0 14px;color:var(--soft)}.pro p.sub a{color:var(--ink,#fff)}"
           ".pro .gr{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}@media(max-width:1000px){.pro .gr{grid-template-columns:repeat(3,minmax(0,1fr))}}"
           ".pro .it{display:flex;flex-direction:column;gap:8px;padding:12px;background:rgba(255,255,255,.04);border:1px solid var(--line,rgba(255,255,255,.1))}"
           ".pro .it img{width:100%;aspect-ratio:4/3;object-fit:contain;filter:drop-shadow(0 8px 10px rgba(0,0,0,.5))}.pro .it b{font:700 .86rem/1.15 var(--hud);text-transform:uppercase}"
           ".pro .it a.cm{margin-top:auto;padding:8px;text-align:center;font:700 .72rem/1 var(--hud);letter-spacing:.06em;text-transform:uppercase;color:#fff;text-decoration:none;background:linear-gradient(90deg,rgba(255,21,154,.25),#16161d);border:1px solid #ff159a}"
           ".pro .it a.cm:hover{background:rgba(255,21,154,.4)}@media(max-width:700px){.pro .gr{grid-template-columns:repeat(2,minmax(0,1fr))}}")


def pro_block(lang):
    h, sub, blog, buy = PRO_T.get(lang, PRO_T["en"])
    if lang not in ("ru", "en"): blog = PRO_T["en"][2]
    imgs = {}
    for r in json.load(open(os.path.join(ROOT, "data/skin-img.json"))):
        k = r[0] + (f" ({r[2]})" if len(r) > 2 and r[2] else ""); imgs.setdefault(k, r[1])
    items = ""
    for n in PRO_SKINS:
        hsh = imgs.get(n) or imgs.get(n.split(" (")[0])
        img = f'<img src="https://community.akamai.steamstatic.com/economy/image/{hsh}/360fx270f" alt="{e(n)}" loading="lazy">' if hsh else ""
        items += f'<div class="it">{img}<b>{e(n.replace("★ ", ""))}</b><a class="cm" href="{csmoney.url(n)}" {csmoney.REL}>{e(buy)}</a></div>'
    return f'<section class="pro"><h2>{e(h)}</h2><p class="sub"><a href="{blog}">{e(sub)} →</a></p><div class="gr">{items}</div></section>'


import urllib.request
SNAPF = os.path.join(ROOT, "data/matches-snap.json")
TR = {"s": 0, "a": 1, "b": 2, "c": 3, "d": 4}


def snapshot():
    out = {}
    try:
        for k, t in (("live", "running"), ("up", "upcoming"), ("past", "past")):
            req = urllib.request.Request(W + "/matches?type=" + t, headers={"User-Agent": "skinset-build"})
            out[k] = json.load(urllib.request.urlopen(req, timeout=20)).get("list", [])
        json.dump(out, open(SNAPF, "w"))
    except Exception as ex:
        print("matches snapshot failed:", ex)
        try: out = json.load(open(SNAPF))
        except Exception: out = {"live": [], "up": [], "past": []}
    return out


def _tz(lang):
    return (datetime.timezone(datetime.timedelta(hours=3)), "МСК") if lang == "ru" else (datetime.timezone.utc, "UTC")


def _dt(iso, lang):
    tz, _ = _tz(lang)
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz)


def _logo(t, cls=""):
    return f'<img src="{e(t["i"])}" alt="" loading="lazy">' if t and t.get("i") else '<span class="ph"></span>'


def _pl(lang, n):
    if lang != "ru": return f"{n} match" + ("" if n == 1 else "es")
    a, b = n % 10, n % 100
    return f"{n} " + ("матч" if a == 1 and b != 11 else "матча" if 2 <= a <= 4 and not 12 <= b <= 14 else "матчей")


def tkey(m):
    return ((m.get("l") or {}).get("n", "") + " " + (m.get("se") or "")).strip()


def srv_top(lang, D):
    t = T[lang]; L = t["L"]; tz, tzn = _tz(lang)
    live, up = D.get("live", []), D.get("up", [])
    today = datetime.datetime.now(tz).date()
    n_today = sum(1 for m in up if m.get("b") and _dt(m["b"], lang).date() == today) + len(live)
    allm = live + up
    tours = {}
    for m in allm:
        k = tkey(m)
        if not k: continue
        o = tours.setdefault(k, {"k": k, "n": k, "i": (m.get("l") or {}).get("i"), "tier": (m.get("tier") or "d").lower(), "c": 0, "b": m.get("b") or ""})
        o["c"] += 1
        if m.get("b") and (not o["b"] or m["b"] < o["b"]): o["b"] = m["b"]
    tl = sorted(tours.values(), key=lambda o: (TR.get(o["tier"], 5), o["b"]))
    main = tl[0]["n"] if tl else "—"
    stats = (f'<div class="mx-stats" id="mxStats"><div class="lvb"><b>{len(live)}</b><small>{e(L["s_live"])}</small></div><div><b>{n_today}</b><small>{e(L["s_today"])}</small></div>'
             f'<div><b>{len(tl)}</b><small>{e(L["s_tours"])}</small></div><div class="mn"><b>{e(main)}</b><small>{e(L["s_main"])}</small></div></div>')
    top = lambda m: (m.get("tier") or "").lower() in ("s", "a")
    f = next((m for m in live if top(m)), None) or next((m for m in up if top(m)), None) or (live[0] if live else (up[0] if up else None))
    feat = ""
    if f:
        a = f["t"][0] if len(f["t"]) > 0 else None; b = f["t"][1] if len(f["t"]) > 1 else None
        when = L["now"] if f.get("st") == "running" else (_dt(f["b"], lang).strftime("%d.%m · %H:%M ") + tzn if f.get("b") else "")
        stage = (f.get("name") or "").split(":")[0] if ":" in (f.get("name") or "") else ""
        feat = (f'<div class="mx-feat" id="mxFeat" data-id="{f["id"]}"><div class="hd">{e(L["feat"])}<span>{e(tkey(f))}{(" · " + e(stage)) if stage else ""}</span></div><div class="row">'
                f'<div class="tm">{_logo(a)}<b>{e(a["n"] if a else L["tbd"])}</b></div><div class="mid"><b>vs</b><small class="cd">{e(when)}</small><small>BO{f.get("bo") or "?"}</small></div>'
                f'<div class="tm">{_logo(b)}<b>{e(b["n"] if b else L["tbd"])}</b></div></div></div>')
    trs = "".join(f'<button data-k="{e(o["k"])}"><span class="tn">{(f"<img src=\"{e(o["i"])}\" alt=\"\">" if o["i"] else "<span class=\"lg\">" + e(o["n"][:2].upper()) + "</span>")}<b>{e(o["n"])}</b><i class="tier {o["tier"]}">{o["tier"].upper()}</i></span><small>{_pl(lang, o["c"])}{(" · " + e(L["next"]) + " " + _dt(o["b"], lang).strftime("%d.%m %H:%M")) if o["b"] else ""}</small></button>' for o in tl[:10])
    tours_html = f'<h2>{e(L["tours_h"])}</h2><div class="mx-tr" id="mxTours">{trs}</div>'
    return stats + feat + tours_html


def srv_list(lang, D):
    t = T[lang]; L = t["L"]; tz, tzn = _tz(lang)
    up = [m for m in D.get("up", []) if m.get("b")]
    topl = [m for m in up if (m.get("tier") or "").lower() in ("s", "a")]
    lst = (topl or up)[:20]
    h, cur = "", ""
    for m in lst:
        d = _dt(m["b"], lang); dn = d.strftime("%d.%m.%Y")
        if dn != cur: cur = dn; h += f'<div class="day">{dn}</div>'
        a = m["t"][0] if m["t"] else None; b = m["t"][1] if len(m["t"]) > 1 else None
        nm = lambda x: f'{_logo(x)}<b>{e(x["n"] if x else L["tbd"])}</b>'
        h += (f'<div class="m" data-id="{m["id"]}"><div class="tm">{d.strftime("%H:%M")}<small>BO{m.get("bo") or ""}</small></div><div class="tt">{nm(a)}</div><div class="sc"><span style="color:var(--dim);font-size:1rem">vs</span></div>'
              f'<div class="tt r">{nm(b)}</div><div class="ev"><span>{e(tkey(m))}</span>{"<em>" + e((m.get("tier") or "").upper()) + "</em>" if m.get("tier") else ""}</div><span></span></div>')
    return h or f'<div class="mt-msg">{e(L["load"])}</div>'


def srv_results(lang, D):
    L = T[lang]["L"]
    past = [m for m in D.get("past", []) if m.get("st") == "finished" and len(m.get("t", [])) == 2 and any((x.get("s") or 0) > 0 for x in m.get("s", []))]
    past.sort(key=lambda m: (TR.get((m.get("tier") or "d").lower(), 5), -(datetime.datetime.fromisoformat((m.get("e") or m.get("b") or "2000-01-01T00:00:00Z").replace("Z", "+00:00")).timestamp())))
    out = ""
    for m in past[:16]:
        a, b = m["t"]; sa = next((x["s"] for x in m["s"] if x["id"] == a["id"]), 0); sb = next((x["s"] for x in m["s"] if x["id"] == b["id"]), 0)
        out += f'<a href="{URL[lang]}match/?id={m["id"]}"><span class="{"w" if sa > sb else ""}">{e(a["n"])}</span><b>{sa} : {sb}</b><span class="{"w" if sb > sa else ""}">{e(b["n"])}</span></a>'
    return f'<h2>{e(L["res_h"])}</h2><div class="mx-res">{out}</div>' if out else ""


def build(lang, D=None):
    D = D or {"live": [], "up": [], "past": []}
    t = T[lang]; url = URL[lang]; L = t["L"]
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": t["h1"], "url": SITE + url, "description": t["desc"]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
    body = (f'<nav class="crumbs"><a href="{HOME[lang]}">{e(t["home"])}</a> › {e(t["h1"])}</nav><span class="mt-kick pg-eb"><i></i>{e(t["kick"])}</span><h1 class="pg-h">{e(t["h1"])}</h1><p class="lead pg-l">{e(t["lead"])}</p>'
            + srv_top(lang, D) + f'<h2 id="schedH">{e(L["sched_h"])}</h2><div class="mt-bar"><div class="mt-tabs" id="mtTabs"><button data-t="live"><span class="lv"><i></i></span>{e(L["live"])} <b id="mtN"></b></button><button data-t="up" class="on">{e(L["up"])}</button><button data-t="past">{e(L["past"])}</button></div>'
            f'<label class="mt-top"><input type="checkbox" id="mtTop"> {e(L["top"])}</label></div><div id="mtList">' + srv_list(lang, D) + '</div>'
            + srv_results(lang, D) + pro_block(lang) + f'<h2>{e(t["faq_h"])}</h2><div class="faq">{"".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in t["faq"])}</div><p class="note">{e(t["note"])}</p>'
            f'<script>window.MTL={json.dumps(L, ensure_ascii=False)};</script><script>{JS.replace("__W__", json.dumps(W))}</script>')
    h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}{GRID_CSS}{PRO_CSS}</style></head>")
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="mt pg">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


DT = {
 "ru": dict(title="Матч CS2: счёт, карты и составы — Skinset", back="← Все матчи", maps="Карты", map="Карта", won="победа", lineups="Составы", watch_h="Трансляции", tour="Турнир", start="Начало", fmt="Формат",
   st={"not_started": "Скоро", "running": "LIVE", "finished": "Завершён", "canceled": "Отменён", "postponed": "Перенесён"}, nomaps="Подробности по картам появятся после начала матча.", nost="Детальная статистика игроков и карт пока недоступна.",
   h2h="Последние встречи", nf="Матч не найден.", load="Загружаем матч…", forfeit="техническая победа", tbd="Будет известно позже", vs="vs", upd="Обновляется автоматически", nolineup="Состав пока неизвестен", decider="если понадобится", dur="мин", soon="Скоро", series="Серия", pool_h="Маппул CS2", pool_note="Пики и баны становятся известны прямо перед матчем. Вот 7 карт, из которых команды выбирают.", mapn="Карта", notpl="не понадобилась"),
 "en": dict(title="CS2 match: score, maps and lineups — Skinset", back="← All matches", maps="Maps", map="Map", won="win", lineups="Lineups", watch_h="Streams", tour="Tournament", start="Start", fmt="Format",
   st={"not_started": "Upcoming", "running": "LIVE", "finished": "Finished", "canceled": "Canceled", "postponed": "Postponed"}, nomaps="Map details will appear once the match starts.", nost="Detailed player and map stats are not available yet.",
   h2h="Recent meetings", nf="Match not found.", load="Loading match…", forfeit="forfeit", tbd="To be decided", vs="vs", upd="Updates automatically", nolineup="Lineup not available yet", decider="if needed", dur="min", soon="Upcoming", series="Series", pool_h="CS2 map pool", pool_note="Picks and bans are revealed right before the match. These are the 7 maps teams can play.", mapn="Map", notpl="not played"),
}
DCSS = """
.srs{display:grid;grid-template-columns:auto 1fr auto auto;gap:14px;align-items:center;padding:12px 16px;margin-bottom:10px;background:rgba(255,255,255,.035);border:1px solid var(--line,rgba(255,255,255,.1))}
.srs span{display:flex;align-items:center;gap:8px;font:700 .95rem var(--hud);text-transform:uppercase}.srs img{width:24px;height:24px;object-fit:contain}.srs>b{font:700 1.5rem/1 var(--hud);min-width:64px;text-align:right}
.srs .bar{display:flex;gap:4px}.srs .bar i{flex:1;height:8px;background:rgba(255,255,255,.1)}.srs .bar i.a{background:#e8402a}.srs .bar i.b{background:#2d73ff}.srs .bar i.lv{background:#ffd36a;animation:mtP 1.4s infinite}
.gm2{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.g2{position:relative;min-height:150px;padding:14px;display:flex;flex-direction:column;background:#101116 center/cover no-repeat;border:1px solid var(--line,rgba(255,255,255,.1));border-top:3px solid #444}
.g2.wa{border-top-color:#e8402a}.g2.wb{border-top-color:#2d73ff}.g2.running{border-top-color:#ffd36a}.g2.not_started{opacity:.75}
.g2 .n{font:600 .7rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--soft);text-shadow:0 1px 6px #000}.g2 .mp{margin-top:6px;font:700 1.2rem/1 var(--hud);text-transform:uppercase}
.g2 .stt{margin-top:auto;display:flex;align-items:center;gap:8px;flex-wrap:wrap}.g2 .stt img{width:26px;height:26px;object-fit:contain}.g2 .stt b{font:700 1rem var(--hud);text-transform:uppercase}.g2 .stt small{width:100%;color:var(--soft);font-size:.8rem}
.lvp{display:inline-flex;align-items:center;gap:6px;font:700 .9rem var(--hud);color:#ffd36a}.lvp i{width:8px;height:8px;border-radius:50%;background:#ff3b2e;animation:mtP 1.4s infinite}
.pool{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px}.pool div{aspect-ratio:4/3;display:flex;align-items:flex-end;padding:8px;background:center/cover no-repeat;border:1px solid var(--line,rgba(255,255,255,.1))}.pool b{font:700 .85rem/1 var(--hud);text-transform:uppercase;text-shadow:0 2px 8px #000}
@media(max-width:700px){.pool{grid-template-columns:repeat(4,minmax(0,1fr))}.srs{grid-template-columns:1fr auto;}.srs .bar{grid-column:1/-1;order:3}.srs span:nth-of-type(2){display:none}}

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
 const POOL=[["Dust II","dust2"],["Mirage","mirage"],["Inferno","inferno"],["Nuke","nuke"],["Ancient","ancient"],["Anubis","anubis"],["Cache","cache"]];
 const mimg=n=>{const k=(POOL.find(x=>n&&x[0].toLowerCase().replace(/\s/g,"")===String(n).toLowerCase().replace(/\s|de_/g,""))||[])[1];return k?"/img/maps/"+k+".jpg":""};
 const bo=m.bo||(m.g||[]).length||1;const G=[];for(let i=1;i<=bo;i++)G.push((m.g||[]).find(g=>g.p===i)||{p:i,st:"not_started"});
 const wins=id=>G.filter(g=>g.st==="finished"&&g.w===id).length;
 h+='<h2>'+esc(L.maps)+'</h2>';
 if(a&&b&&bo>1)h+='<div class="srs"><span>'+(a.i?'<img src="'+esc(a.i)+'" alt="">':'')+esc(a.a||a.n)+'</span><div class="bar">'+G.map(g=>'<i class="'+(g.st==="finished"?(g.w===a.id?"a":"b"):g.st==="running"?"lv":"")+'"></i>').join("")+'</div><span>'+esc(b.a||b.n)+(b.i?'<img src="'+esc(b.i)+'" alt="">':'')+'</span><b>'+wins(a.id)+' : '+wins(b.id)+'</b></div>';
 h+='<div class="gm2">'+G.map(g=>{const wt=m.t.find(t=>t.id===g.w);const img=g.map?mimg(g.map.n):"";const dec=g.p===bo&&bo>1&&g.st==="not_started";
  const state=g.st==="finished"?(wt?(wt.i?'<img src="'+esc(wt.i)+'" alt="">':'')+'<b>'+esc(wt.n)+'</b><small>'+esc(L.won)+(g.len?' · '+Math.round(g.len/60)+' '+esc(L.dur):'')+'</small>':'<b>—</b>'):g.st==="running"?'<span class="lvp"><i></i>LIVE</span>':'<small>'+esc(fin?L.notpl:(dec?L.decider:L.soon))+'</small>';
  return'<div class="g2 '+(g.st||"")+(wt?(wt.id===(a&&a.id)?" wa":" wb"):"")+'"'+(img?' style="background-image:linear-gradient(0deg,rgba(8,9,12,.92),rgba(8,9,12,.35)),url('+img+')"':'')+'><span class="n">'+esc(L.mapn)+' '+g.p+'</span><span class="mp">'+esc(g.map?g.map.n:"")+'</span><div class="stt">'+state+'</div></div>'}).join("")+'</div>';
 if(!fin&&!G.some(g=>g.map))h+='<h2>'+esc(L.pool_h)+'</h2><p class="note" style="margin-top:0">'+esc(L.pool_note)+'</p><div class="pool">'+POOL.map(([n,k])=>'<div style="background-image:linear-gradient(0deg,rgba(8,9,12,.85),rgba(8,9,12,.1) 60%),url(/img/maps/'+k+'.jpg)"><b>'+esc(n)+'</b></div>').join("")+'</div>';
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
    h = head(lang, t["title"], t["title"], SITE + url, "", []).replace("</head>", f'<meta name="robots" content="noindex,follow"><style>{DCSS}{GRID_CSS}</style></head>')
    p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="md pg">\n{body}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
    p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
    return navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))


def main():
    D = snapshot()
    for lang in URL:
        f = os.path.join(ROOT, URL[lang].strip("/"), "index.html"); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(build(lang, D))
        f2 = os.path.join(ROOT, (URL[lang] + "match/").strip("/"), "index.html"); os.makedirs(os.path.dirname(f2), exist_ok=True)
        open(f2, "w", encoding="utf-8").write(build_detail(lang))
    sm = os.path.join(ROOT, "sitemap.xml"); xml = open(sm, encoding="utf-8").read()
    for u in URL.values():
        if f"<loc>{SITE}{u}</loc>" not in xml: xml = xml.replace("</urlset>", f"  <url><loc>{SITE}{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n</urlset>")
    open(sm, "w", encoding="utf-8").write(xml)
    print("ok")


if __name__ == "__main__":
    main()
