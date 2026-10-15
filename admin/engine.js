/* Skinset blog engine: markdown -> html, post/index/rss/sitemap builders.
   Works in browser (window.Engine) and Node (module.exports). */
(function(root,factory){if(typeof module==="object"&&module.exports)module.exports=factory();else root.Engine=factory();})(this,function(){
const SITE="https://skin-set.com";
const PRESETS=[["Красный с чёрным","krasnye-skiny-cs2","#c4161c"],["Синий","sinie-skiny-cs2","#1f4fd6"],["Розовый","rozovye-skiny-cs2","#ff5fa8"],["Фиолетовый","fioletovye-skiny-cs2","#8a5cf6"],["Зелёный","zelenye-skiny-cs2","#1fbf5a"],["Золото","zolotye-skiny-cs2","#d4a63a"],["Оранжевый с белым","oranzhevye-skiny-cs2","#ff6a1f"],["Бирюза","biryuzovye-skiny-cs2","#19c3c3"],["Чёрно-белый","cherno-belye-skiny-cs2","#e8e8e8"]];
const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
function translit(s){const m={а:"a",б:"b",в:"v",г:"g",д:"d",е:"e",ё:"e",ж:"zh",з:"z",и:"i",й:"y",к:"k",л:"l",м:"m",н:"n",о:"o",п:"p",р:"r",с:"s",т:"t",у:"u",ф:"f",х:"h",ц:"c",ч:"ch",ш:"sh",щ:"sch",ъ:"",ы:"y",ь:"",э:"e",ю:"yu",я:"ya"};
  return s.toLowerCase().split("").map(c=>m[c]!==undefined?m[c]:c).join("").replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,70)}
function inline(t){
  t=esc(t);
  t=t.replace(/`([^`]+)`/g,"<code>$1</code>");
  t=t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g,'<img src="$2" alt="$1" loading="lazy">');
  t=t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,(m,a,u)=>'<a href="'+u+'"'+(/^https?:\/\//.test(u)&&!u.includes("skin-set.com")?' target="_blank" rel="noopener'+(/dmarket|lis-skins/.test(u)?' sponsored':'')+'"':'')+'>'+a+'</a>');
  t=t.replace(/\*\*([^*]+)\*\*/g,"<b>$1</b>").replace(/(^|[^*])\*([^*\n]+)\*/g,"$1<i>$2</i>");
  return t}
function shortcode(line){
  // [cta color=3 budget=10000 text="..."]  [cta url=/... text="..."]
  const m=line.match(/^\[cta\s+([^\]]*)\]$/);if(!m)return null;
  const a={};m[1].replace(/(\w+)=("([^"]*)"|(\S+))/g,(x,k,v,q,p)=>{a[k]=q!==undefined?q:p;return""});
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
    if(/^\[cta\s/.test(l)){flush();const h=shortcode(l.trim());if(h){out.push(h);continue}}
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
function dateHuman(iso){const d=new Date(iso);const M=["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"];return d.getDate()+" "+M[d.getMonth()]+" "+d.getFullYear()}
function fill(tpl,map){return tpl.replace(/\{\{(\w+)\}\}/g,(m,k)=>map[k]!==undefined?map[k]:"")}
function card(p){const c0=p.color!==undefined&&PRESETS[+p.color]?PRESETS[+p.color][2]:"var(--pick)";
  return '<a class="post-card" href="/blog/'+esc(p.slug)+'/" style="--c0:'+c0+'"><b>'+esc(p.title)+'</b><p>'+esc(p.desc||"")+'</p><small>'+dateHuman(p.date)+'</small></a>'}
function buildPost(tpl,p,all){
  const body=md(p.md||"");const url=SITE+"/blog/"+p.slug+"/";
  const others=all.filter(x=>x.slug!==p.slug&&!x.draft).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,3).map(card).join("")||'<a class="post-card" href="/cvetovye-sety-skinov-cs2/"><b>Цветовые сеты скинов CS2</b><p>9 готовых наборов в одном цвете</p></a>';
  const ld=JSON.stringify({"@context":"https://schema.org","@type":"Article","headline":p.title,"description":p.desc||"","datePublished":p.date,"dateModified":p.updated||p.date,"author":{"@type":"Person","name":"viv1stop","url":"https://www.twitch.tv/viv1stop"},"publisher":{"@type":"Organization","name":"Skinset","url":SITE},"mainEntityOfPage":url});
  const ctaUrl=p.color!==undefined&&PRESETS[+p.color]?"/"+PRESETS[+p.color][1]+"/"+(p.budget?"?budget="+p.budget:""):"/";
  return fill(tpl,{TITLE:esc(p.seoTitle||(p.title+" — Skinset")),DESC:esc(p.desc||""),URL:url,LD:ld,H1:esc(p.title),LEAD:esc(p.lead||p.desc||""),DATE_HUMAN:dateHuman(p.date),READ:readMin(p.md||""),BODY:body,CTA_URL:ctaUrl,OTHER:others})}
function buildIndex(tpl,all){const list=all.filter(p=>!p.draft).sort((a,b)=>b.date.localeCompare(a.date)).map(card).join("")||"<p>Скоро здесь появятся статьи.</p>";return fill(tpl,{LIST:list})}
function buildRss(all){const items=all.filter(p=>!p.draft).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,30).map(p=>"<item><title>"+esc(p.title)+"</title><link>"+SITE+"/blog/"+p.slug+"/</link><guid>"+SITE+"/blog/"+p.slug+"/</guid><pubDate>"+new Date(p.date).toUTCString()+"</pubDate><description>"+esc(p.desc||"")+"</description></item>").join("\n");
  return '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Блог Skinset</title><link>'+SITE+'/blog/</link><description>Гайды по скинам CS2</description>\n'+items+'\n</channel></rss>\n'}
function buildSitemap(oldXml,all){const today=new Date().toISOString().slice(0,10);
  const keep=(oldXml.match(/<url>.*?<\/url>/gs)||[]).filter(u=>!u.includes(SITE+"/blog/"));
  const blog=['  <url><loc>'+SITE+'/blog/</loc><lastmod>'+today+'</lastmod></url>'].concat(all.filter(p=>!p.draft).map(p=>'  <url><loc>'+SITE+'/blog/'+p.slug+'/</loc><lastmod>'+(p.updated||p.date).slice(0,10)+'</lastmod></url>'));
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+keep.map(u=>"  "+u).join("\n")+"\n"+blog.join("\n")+"\n</urlset>\n"}
return {PRESETS,esc,translit,md,buildPost,buildIndex,buildRss,buildSitemap,readMin,dateHuman};
});
