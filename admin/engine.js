/* Skinset blog engine: markdown -> html, post/index/rss/sitemap builders.
   Works in browser (window.Engine) and Node (module.exports). */
(function(root,factory){if(typeof module==="object"&&module.exports)module.exports=factory();else root.Engine=factory();})(this,function(){
const SITE="https://skin-set.com";
const PRESETS=[["Красный с чёрным","krasnye-skiny-cs2","#c4161c"],["Синий","sinie-skiny-cs2","#1f4fd6"],["Розовый","rozovye-skiny-cs2","#ff5fa8"],["Фиолетовый","fioletovye-skiny-cs2","#8a5cf6"],["Зелёный","zelenye-skiny-cs2","#1fbf5a"],["Золото","zolotye-skiny-cs2","#d4a63a"],["Оранжевый с белым","oranzhevye-skiny-cs2","#ff6a1f"],["Бирюза","biryuzovye-skiny-cs2","#19c3c3"],["Чёрно-белый","cherno-belye-skiny-cs2","#e8e8e8"]];
let SKINS={};let PRICES={};let CUR_LANG="ru";let USED=[];function setPrices(p){PRICES=p||{}}
const RATES={rub:90,usd:1,eur:1,brl:5.5,pln:4};
function fmtPrice(usd,cur){if(!(usd>0))return null;const v=usd*(RATES[cur]||1);const r=v>=100?Math.round(v):Math.round(v*10)/10;const n=cur==="usd"?r.toLocaleString("en-US"):r.toLocaleString("de-DE");return cur==="rub"?n.replace(/\./g," ")+" ₽":cur==="usd"?"$"+n:cur==="eur"?n+" €":cur==="brl"?"R$ "+n:n+" zł"}
function priceOf(name){const r=PRICES[name]||PRICES[name.replace("★ ","")];if(!r)return null;const v=[r.dm,r.ls].filter(x=>x>0);const w=v.length?v:[r.sp].filter(x=>x>0);return w.length?{min:Math.min(...w),dm:r.dm||null,ls:r.ls||null}:null}
function curOf(){return ((LANGS||{})[CUR_LANG]||{}).ui&&LANGS[CUR_LANG].ui.cur||"rub"}
function priceSpan(name,wear){const cur=curOf();let v=null;if(wear){const r=PRICES[name]||{};v=(r.w||{})[wear]||null}else{const p=priceOf(name);v=p?p.min:null}if(!v&&/\((Ruby|Sapphire|Emerald|Black Pearl)\)$/.test(name)){const ui=((LANGS||{})[CUR_LANG]||{}).ui||{};return '<span class="lp gem">'+esc(ui.gem||'')+'</span>'}return '<span class="lp" data-skin="'+esc(name)+'" data-cur="'+cur+'"'+(wear?' data-src="'+esc(wear)+'"':'')+'>'+(v?esc(fmtPrice(v,cur)):"…")+'</span>'}
function setSkins(m){SKINS=Array.isArray(m)?Object.fromEntries(m.map(r=>[r[0]+(r[5]?" ("+r[5]+")":""),r[1]])):(m||{})}
function skinImg(name){if(!name)return null;const n=name.replace(/★\s*/,"").trim();if(SKINS[n])return SKINS[n];const k=Object.keys(SKINS).find(x=>x.toLowerCase()===n.toLowerCase())||Object.keys(SKINS).find(x=>x.toLowerCase().startsWith(n.toLowerCase()));return k?SKINS[k]:null}
function skinFig(name,cap,small){const img=skinImg(name);if(!img)return "";USED.push(name);return '<figure class="post-skin'+(small?" sm":"")+'"><img src="'+esc(img)+'" alt="'+esc(name)+'" loading="lazy"><figcaption>'+esc(cap||name)+' · '+priceSpan(name)+'</figcaption></figure>'}
const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
function translit(s){const m={а:"a",б:"b",в:"v",г:"g",д:"d",е:"e",ё:"e",ж:"zh",з:"z",и:"i",й:"y",к:"k",л:"l",м:"m",н:"n",о:"o",п:"p",р:"r",с:"s",т:"t",у:"u",ф:"f",х:"h",ц:"c",ч:"ch",ш:"sh",щ:"sch",ъ:"",ы:"y",ь:"",э:"e",ю:"yu",я:"ya"};
  return s.toLowerCase().split("").map(c=>m[c]!==undefined?m[c]:c).join("").replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,70)}
function inline(t){
  const ph=[];t=t.replace(/\[price\s+name="([^"]+)"(?:\s+wear="(\w+)")?\]/g,(m,n,w)=>{USED.push(n);ph.push(priceSpan(n,w));return "\u0000"+(ph.length-1)+"\u0000"});
  t=esc(t);t=t.replace(/\u0000(\d+)\u0000/g,(m,i)=>ph[+i]);
  t=t.replace(/`([^`]+)`/g,"<code>$1</code>");
  t=t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g,'<img src="$2" alt="$1" loading="lazy">');
  t=t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,(m,a,u)=>'<a href="'+u+'"'+(/^https?:\/\//.test(u)&&!u.includes("skin-set.com")?' target="_blank" rel="noopener'+(/dmarket|lis-skins|avan\.market/.test(u)?' sponsored':'')+'"':'')+'>'+a+'</a>');
  t=t.replace(/\*\*([^*]+)\*\*/g,"<b>$1</b>").replace(/(^|[^*])\*([^*\n]+)\*/g,"$1<i>$2</i>");
  return t}
function attrs(str){const a={};str.replace(/(\w+)=("([^"]*)"|(\S+))/g,(x,k,v,q,p)=>{a[k]=q!==undefined?q:p;return""});return a}
function shortcode(line){
  let m;
  if((m=line.match(/^\[skin\s+([^\]]*)\]$/))){const a=attrs(m[1]);return skinFig(a.name||"",a.caption,false)||'<p><i>[картинка не найдена: '+esc(a.name||"")+']</i></p>'}
  if((m=line.match(/^\[skins\s+([^\]]*)\]$/))){const a=attrs(m[1]);const names=(a.names||"").split(";").map(x=>x.trim()).filter(Boolean);return '<div class="post-skins">'+names.map(n=>skinFig(n,null,true)).join("")+'</div>'}
  // [cta color=3 budget=10000 text="..."]  [cta url=/... text="..."]
  m=line.match(/^\[cta\s+([^\]]*)\]$/);if(!m)return null;
  const a=attrs(m[1]);
  let url=a.url||"/";let c0="var(--pick)";
  if(a.color!==undefined&&PRESETS[+a.color]){url="/"+PRESETS[+a.color][1]+"/";c0=PRESETS[+a.color][2]}
  if(a.budget)url+=(url.includes("?")?"&":"?")+"budget="+encodeURIComponent(a.budget);
  const text=a.text||"Собрать такой сет в конструкторе";const btn=a.btn||"Открыть конструктор";
  return '<div class="post-cta" style="--c0:'+c0+'"><i></i><span>'+esc(text)+'</span><a class="hudbtn" href="'+esc(url)+'">'+esc(btn)+'</a></div>'}
function md(src){
  const lines=src.replace(/\r/g,"").split("\n");let out=[],para=[],list=null,quote=[];
  const flushP=()=>{if(para.length){out.push("<p>"+inline(para.join(" "))+"</p>");para=[]}};
  const flushL=()=>{if(list){out.push("<"+list.t+">"+list.items.map(i=>"<li>"+inline(i)+"</li>").join("")+"</"+list.t+">");list=null}};
  const flushQ=()=>{if(quote.length){out.push("<blockquote>"+inline(quote.join(" "))+"</blockquote>");quote=[]}};
  const flush=()=>{flushP();flushL();flushQ()};
  for(let raw of lines){const l=raw.trimEnd();
    if(!l.trim()){flush();continue}
    let m;
    if((m=l.match(/^(#{1,4})\s+(.*)$/))){flush();const n=Math.min(4,Math.max(2,m[1].length));out.push("<h"+n+">"+inline(m[2])+"</h"+n+">");continue}
    if(/^\[(cta|skin|skins)\s/.test(l)){flush();const h=shortcode(l.trim());if(h!==null){out.push(h);continue}}
    if((m=l.match(/^>\s?(.*)$/))){flushP();flushL();quote.push(m[1]);continue}
    if((m=l.match(/^[-*]\s+(.*)$/))){flushP();flushQ();if(!list||list.t!=="ul"){flushL();list={t:"ul",items:[]}}list.items.push(m[1]);continue}
    if((m=l.match(/^\d+[.)]\s+(.*)$/))){flushP();flushQ();if(!list||list.t!=="ol"){flushL();list={t:"ol",items:[]}}list.items.push(m[1]);continue}
    if(/^\|.*\|$/.test(l)){flush();const rows=[l];out.push({table:rows});continue}
    if(out.length&&out[out.length-1].table&&/^\|/.test(l)){out[out.length-1].table.push(l);continue}
    if(/^---+$/.test(l)){flush();out.push("<hr>");continue}
    flushL();flushQ();para.push(l)}
  flush();
  return out.map(o=>{if(typeof o==="string")return o;const rows=o.table.filter(r=>!/^\|\s*-/.test(r)).map(r=>r.replace(/^\||\|$/g,"").split("|").map(c=>c.trim()));
    return "<table>"+rows.map((r,i)=>"<tr>"+r.map(c=>(i?"<td>":"<th>")+inline(c)+(i?"</td>":"</th>")).join("")+"</tr>").join("")+"</table>"}).join("\n")}
function readMin(src){return Math.max(2,Math.round(src.split(/\s+/).length/180))}
let LANGS=null;function setLangs(l){LANGS=l}
const MONTHS={ru:["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"],en:["January","February","March","April","May","June","July","August","September","October","November","December"],de:["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],pt:["de janeiro","de fevereiro","de março","de abril","de maio","de junho","de julho","de agosto","de setembro","de outubro","de novembro","de dezembro"],tr:["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"],pl:["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca","sierpnia","września","października","listopada","grudnia"]};
function dateHuman(iso,lang){lang=lang||"ru";const d=new Date(iso);const M=MONTHS[lang]||MONTHS.en;return lang==="en"?M[d.getMonth()]+" "+d.getDate()+", "+d.getFullYear():d.getDate()+" "+M[d.getMonth()]+" "+d.getFullYear()}
function fill(tpl,map){return tpl.replace(/\{\{(\w+)\}\}/g,(m,k)=>map[k]!==undefined?map[k]:"")}
/* поля поста для языка: ru — корень, остальные — p.tr[lang] */
function loc(p,lang){if(!lang||lang==="ru")return p;const t=(p.tr||{})[lang];if(!t||!t.md)return null;return {...p,title:t.title||p.title,desc:t.desc||p.desc,lead:t.lead||p.lead,seoTitle:t.seoTitle,md:t.md}}
function hasLang(p,lang){return !!loc(p,lang)}
function cfg(lang){const L=LANGS||{};return L[lang]||L.ru||{presets:{},blog:"/blog/",home:"/",ui:{}}}
function coverOf(p){return p.cover||skinImg(p.coverSkin||"")||(function(){const mm=(p.md||"").match(/\[skin\s+name="([^"]+)"/);return mm?skinImg(mm[1]):null})()||""}
function card(p,lang,big){lang=lang||"ru";const q=loc(p,lang)||p;const c=cfg(lang);const ui=c.ui||{};const c0=p.color!==undefined&&PRESETS[+p.color]?PRESETS[+p.color][2]:"var(--pick)";const cover=coverOf(p);const tag=(ui.tags||{})[p.tag||"guide"]||"";
  return '<a class="post-card'+(big?" big":"")+'" href="'+c.blog+esc(p.slug)+'/" data-tag="'+esc(p.tag||"guide")+'" style="--c0:'+c0+'"><div class="pc-art">'+(cover?'<img src="'+esc(cover)+'" alt="" loading="lazy">':"")+(tag?'<span class="pc-tag">'+esc(tag)+'</span>':"")+'</div><div class="pc-body">'+(big?'<span class="pc-feat">'+esc(ui.featured||"")+'</span>':"")+'<b>'+esc(q.title)+'</b><p>'+esc(q.desc||"")+'</p><div class="pc-meta"><span>'+dateHuman(p.date,lang)+'</span><span>'+readMin(q.md||"")+' '+esc(ui.min||"")+'</span><span class="pc-go">'+esc(ui.read_more||"")+' →</span></div></div></a>'}
function ctaUrl(p,lang){const c=cfg(lang);const pres=c.presets||{};if(p.color!==undefined&&pres[String(p.color)])return pres[String(p.color)]+(p.budget?"?budget="+p.budget:"");return c.home||"/"}
function altsFor(p){const out=[];for(const lang of Object.keys(LANGS||{ru:1})){if(hasLang(p,lang))out.push([lang==="pt"?"pt-BR":lang,SITE+cfg(lang).blog+p.slug+"/"])}
  const xd=hasLang(p,"en")?SITE+cfg("en").blog+p.slug+"/":SITE+"/blog/"+p.slug+"/";return out.map(([h,u])=>'<link rel="alternate" hreflang="'+h+'" href="'+u+'">').join("\n")+'\n<link rel="alternate" hreflang="x-default" href="'+xd+'">\n'}
function langSwitch(p,cur){return Object.keys(LANGS||{ru:1}).filter(l=>!p||hasLang(p,l)).map(l=>'<a href="'+cfg(l).blog+(p?p.slug+"/":"")+'" class="'+(l===cur?"on":"")+'" hreflang="'+(l==="pt"?"pt-BR":l)+'">'+l.toUpperCase()+'</a>').join("")}
function priceTable(names,lang){const c=cfg(lang);const ui=c.ui||{};const cur=ui.cur||"rub";const uniq=[...new Set(names)];if(!uniq.length)return "";
  const ru=lang==="ru";const qn=n=>encodeURIComponent(n.replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,""));
  const rows=uniq.map(n=>{const p=priceOf(n);const r=PRICES[n]||{};const ft=(r.w||{}).FT;if(!p&&/\((Ruby|Sapphire|Emerald|Black Pearl)\)$/.test(n))return '<tr><td>'+esc(n)+'</td><td colspan="2"><small>'+esc(ui.gem||'')+'</small></td><td class="pb"><a href="https://dmarket.com/'+(lang==="ru"?"ru/":"")+'ingame-items/item-list/csgo-skins?title='+qn(n)+'&ref=L4QnfHPvxc" target="_blank" rel="nofollow sponsored noopener">DMarket</a></td></tr>';return '<tr><td>'+esc(n)+'</td><td><span class="lp" data-skin="'+esc(n)+'" data-cur="'+cur+'">'+(p?esc(fmtPrice(p.min,cur)):"—")+'</span></td><td><span class="lp" data-skin="'+esc(n)+'" data-cur="'+cur+'" data-src="FT">'+(ft?esc(fmtPrice(ft,cur)):"—")+'</span></td><td class="pb"><a href="https://dmarket.com/'+(ru?"ru/":"")+'ingame-items/item-list/csgo-skins?title='+qn(n)+'&ref=L4QnfHPvxc" target="_blank" rel="nofollow sponsored noopener">DMarket</a></td></tr>'}).join("");
  return '<div class="post-prices"><h2 id="prices">'+esc(ui.prices||"")+'</h2><table class="pt"><thead><tr><th>'+esc(ui.item||"")+'</th><th>'+esc(ui.from||"")+'</th><th>Field-Tested</th><th></th></tr></thead><tbody>'+rows+'</tbody></table><p class="post-note">'+esc(ui.upd||"")+'</p></div>'}
function buildPost(tpl,p,all,lang){lang=lang||"ru";const q=loc(p,lang);if(!q)return null;const c=cfg(lang);const ui=c.ui||{};
  CUR_LANG=lang;USED=[];if(p.coverSkin&&skinImg(p.coverSkin))USED.push(p.coverSkin);const body=md(q.md||"")+priceTable(USED,lang);const url=SITE+c.blog+p.slug+"/";
  const others=all.filter(x=>x.slug!==p.slug&&!x.draft&&hasLang(x,lang)).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,3).map(x=>card(x,lang)).join("")||'<a class="post-card" href="'+(c.home||"/")+'"><b>Skinset</b><p>'+esc(ui.ctaDef||"")+'</p></a>';
  const ld=JSON.stringify({"@context":"https://schema.org","@type":"Article","headline":q.title,"description":q.desc||"","datePublished":p.date,"dateModified":p.updated||p.date,"inLanguage":lang,"author":{"@type":"Person","name":"viv1stop","url":"https://www.twitch.tv/viv1stop"},"publisher":{"@type":"Organization","name":"Skinset","url":SITE},"mainEntityOfPage":url});
  let n=0;const toc=[];const body2=body.replace(/<h2>(.*?)<\/h2>/g,(m,t)=>{n++;const id="s"+n;toc.push('<a href="#'+id+'">'+t+'</a>');return '<h2 id="'+id+'">'+t+'</h2>'});
  const cover=coverOf(p);const pc=p.color!==undefined&&PRESETS[+p.color]?PRESETS[+p.color]:null;const cu=ctaUrl(p,lang);
  const side='<div class="side-card"><b>'+esc(ui.toc||"")+'</b>'+(toc.length?'<nav class="toc">'+toc.join("")+'</nav>':'<p>—</p>')+'</div>'
    +'<div class="side-card cta" style="--c0:'+(pc?pc[2]:"var(--pick)")+'"><b>'+esc(ui.cta||"")+'</b><p>'+(pc?esc(pc[0])+(p.budget&&lang==="ru"?" · "+(ui.budget||"")+" "+Number(p.budget).toLocaleString("ru-RU")+" ₽":""):esc(ui.ctaDef||""))+'</p><a class="hudbtn" href="'+cu+'">'+esc(ui.open||"")+'</a></div>'
    +'<div class="side-card"><b>'+esc(ui.others||"")+'</b><div class="side-list">'+all.filter(x=>x.slug!==p.slug&&!x.draft&&hasLang(x,lang)).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,4).map(x=>'<a href="'+c.blog+esc(x.slug)+'/">'+esc(loc(x,lang).title)+'</a>').join("")+'</div></div>'
    +'<div class="side-card"><b>'+esc(ui.sections||"")+'</b><div class="side-list"><a href="'+(c.home||"/")+'">'+esc(ui.builder||"")+'</a><a href="'+(c.feed||"/sety/")+'">'+esc(ui.sets||"")+'</a><a href="'+(c.shops||"/gde-kupit/")+'">'+esc(ui.shops||"")+'</a><a href="'+(c.how||"/kak-rabotaet/")+'">'+esc(ui.how||"")+'</a></div></div>';
  return fill(tpl,{SIDE:side,COVER:cover?'<figure class="post-cover"><img src="'+esc(cover)+'" alt="'+esc(q.title)+'"></figure>':"",OG_IMAGE:cover||"https://skin-set.com/img/og-"+lang+".png",OG_TYPE:"article",ALTS:altsFor(p),LANGS:langSwitch(p,lang),
    TITLE:esc(q.seoTitle||(q.title+" — Skinset")),DESC:esc(q.desc||""),URL:url,LD:ld,H1:esc(q.title),LEAD:esc(q.lead||q.desc||""),DATE_HUMAN:dateHuman(p.date,lang),READ:readMin(q.md||""),BODY:body2,CTA_URL:cu,OTHER:others})}
function buildIndex(tpl,all,lang){lang=lang||"ru";const c=cfg(lang);const ui=c.ui||{};const posts=all.filter(p=>!p.draft&&hasLang(p,lang)).sort((a,b)=>b.date.localeCompare(a.date));
  const tags=[...new Set(posts.map(p=>p.tag||"guide"))];
  const chips=tags.length>1?'<div class="blog-tags"><button class="on" data-f="">'+esc(ui.all_t||"All")+'</button>'+tags.map(t=>'<button data-f="'+esc(t)+'">'+esc((ui.tags||{})[t]||t)+'</button>').join("")+'</div>':"";
  const list=posts.length?(card(posts[0],lang,true)+chips+'<div class="post-grid">'+posts.slice(1).map(p=>card(p,lang)).join("")+'</div>'):"<p>"+esc(ui.empty||"")+"</p>";
  const alts=Object.keys(LANGS||{ru:1}).map(l=>'<link rel="alternate" hreflang="'+(l==="pt"?"pt-BR":l)+'" href="'+SITE+cfg(l).blog+'">').join("\n")+'\n<link rel="alternate" hreflang="x-default" href="'+SITE+cfg("en").blog+'">\n';
  return fill(tpl,{LIST:list,TITLE:esc(ui.blogTitle||"Skinset Blog"),DESC:esc(ui.blogDesc||""),URL:SITE+c.blog,OG_IMAGE:"https://skin-set.com/img/og-"+lang+".png",OG_TYPE:"website",ALTS:alts,LANGS:langSwitch(null,lang),LD:JSON.stringify({"@context":"https://schema.org","@type":"Blog","name":ui.blog||"Skinset Blog","url":SITE+c.blog,"inLanguage":lang})})}
function buildRss(all,lang){lang=lang||"ru";const c=cfg(lang);const ui=c.ui||{};const items=all.filter(p=>!p.draft&&hasLang(p,lang)).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,30).map(p=>{const q=loc(p,lang);return "<item><title>"+esc(q.title)+"</title><link>"+SITE+c.blog+p.slug+"/</link><guid>"+SITE+c.blog+p.slug+"/</guid><pubDate>"+new Date(p.date).toUTCString()+"</pubDate><description>"+esc(q.desc||"")+"</description></item>"}).join("\n");
  return '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>'+esc(ui.blog||"Skinset Blog")+'</title><link>'+SITE+c.blog+'</link><description>'+esc(ui.blogH1||"")+'</description>\n'+items+'\n</channel></rss>\n'}
function buildSitemap(oldXml,all){const today=new Date().toISOString().slice(0,10);
  const keep=(oldXml.match(/<url>.*?<\/url>/gs)||[]).filter(u=>!/\/blog\//.test(u));
  const blog=[];for(const lang of Object.keys(LANGS||{ru:1})){const c=cfg(lang);blog.push('  <url><loc>'+SITE+c.blog+'</loc><lastmod>'+today+'</lastmod></url>');all.filter(p=>!p.draft&&hasLang(p,lang)).forEach(p=>blog.push('  <url><loc>'+SITE+c.blog+p.slug+'/</loc><lastmod>'+(p.updated||p.date).slice(0,10)+'</lastmod></url>'))}
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+keep.map(u=>"  "+u).join("\n")+"\n"+blog.join("\n")+"\n</urlset>\n"}
return {PRESETS,esc,translit,md,buildPost,buildIndex,buildRss,buildSitemap,readMin,dateHuman,setSkins,skinImg,setLangs,hasLang,loc,coverOf,setPrices,fmtPrice};
});
