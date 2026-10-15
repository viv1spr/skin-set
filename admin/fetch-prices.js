// Node 18+: fetches current minimum prices from DMarket (public API) and Lis-Skins (public export)
// for every skin in the site database and writes data/prices.json  { "Weapon | Skin": {dm: usd, ls: usd, t: epoch} }
const fs=require("fs"),path=require("path");
const root=path.join(__dirname,"..");
const base=JSON.parse(fs.readFileSync(path.join(root,"data/skins-base.json"),"utf8"));
let extra=[];try{extra=JSON.parse(fs.readFileSync(path.join(root,"data/skins-extra.json"),"utf8")).map(e=>e[1].replace("★ ","")+" | "+e[2])}catch(e){}
const names=[...new Set([...base,...extra])];
const api=JSON.parse(fs.readFileSync(path.join(root,"admin/skins-api.json"),"utf8"));
const isStar=new Map(api.map(r=>[r[0]+(r[5]?" ("+r[5]+")":""),r[4]==="Gloves"||r[4]==="Knives"]));
const old=(()=>{try{return JSON.parse(fs.readFileSync(path.join(root,"data/prices.json"),"utf8"))}catch(e){return {}}})();
const out={...old};const now=Date.now();
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const META={started:new Date().toISOString(),dm:{ok:0,fail:0,samples:[]},ls:{},sp:{}};
async function probe(tag,url,opts){try{const r=await fetch(url,opts);const t=await r.text();META[tag+"_probe"]=META[tag+"_probe"]||[];META[tag+"_probe"].push({url,status:r.status,ctype:r.headers.get("content-type"),len:t.length,head:t.slice(0,400)});return {r,t}}catch(e){META[tag+"_probe"]=META[tag+"_probe"]||[];META[tag+"_probe"].push({url,error:String(e)});return null}}
const stripPhase=n=>n.replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,"");
const phaseOf=n=>(n.match(/\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/)||[])[1]||null;
async function dmarket(name){
  const star=isStar.get(name)||/Gloves|Hand Wraps|Knife|Bayonet|Karambit|Daggers/.test(name);
  const title=(star?"★ ":"")+stripPhase(name);const ph=phaseOf(name);
  const url="https://api.dmarket.com/exchange/v1/market/items?gameId=a8db&currency=USD&limit=20&orderBy=price&orderDir=asc&title="+encodeURIComponent(title);
  const r=await fetch(url,{headers:{"Accept":"application/json","User-Agent":"Mozilla/5.0 (compatible; skin-set.com price bot)"}});const txt=await r.text();
  if(META.dm.samples.length<3)META.dm.samples.push({title,status:r.status,head:txt.slice(0,500)});if(!r.ok)throw new Error("dm "+r.status);
  const j=JSON.parse(txt);const objs=(j.objects||[]).filter(o=>o.title===title&&!/StatTrak|Souvenir/.test(o.title));
  const cand=ph?objs.filter(o=>((o.extra||{}).phase||"").toLowerCase().replace("-"," ")===ph.toLowerCase().replace("-"," ")):objs;
  const prices=cand.map(o=>+((o.price||{}).USD||0)/100).filter(x=>x>0);return prices.length?Math.min(...prices):null}
async function lisAll(){
  const urls=["https://lis-skins.com/market_export_json/api_csgo_full.json","https://lis-skins.com/market_export_json/csgo.json","https://lis-skins.ru/market_export_json/csgo.json"];
  for(const u of urls){const p=await probe("ls",u,{headers:{"User-Agent":"Mozilla/5.0 (compatible; skin-set.com price bot)","Accept":"application/json"}});if(!p||!p.r.ok)continue;
    try{const j=JSON.parse(p.t);const list=Array.isArray(j)?j:(j.items||j.data||[]);const m=new Map();
      for(const it of list){const n=(it.name||it.market_hash_name||"").replace("★ ","").replace(/\s*\((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/,"");const p2=+(it.price||it.min_price||it.price_usd||0);if(!n||!p2)continue;if(/StatTrak|Souvenir/.test(n))continue;if(!m.has(n)||m.get(n)>p2)m.set(n,p2)}
      META.ls={url:u,items:list.length,names:m.size,sample:list.slice(0,2)};if(m.size)return m}catch(e){META.ls={url:u,parseError:String(e)}}}
  return new Map()}
/* запасной ориентир: Skinport (публичное API, все предметы одним запросом) */
async function skinport(){const p=await probe("sp","https://api.skinport.com/v1/items?app_id=730&currency=USD&tradable=0",{headers:{"Accept-Encoding":"br","Accept":"application/json","User-Agent":"Mozilla/5.0 (compatible; skin-set.com price bot)"}});
  const m=new Map();if(!p||!p.r.ok)return m;try{const list=JSON.parse(p.t);for(const it of list){let n=(it.market_hash_name||"").replace("★ ","");if(/StatTrak|Souvenir/.test(n))continue;n=n.replace(/\s*\((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/,"");const v=+(it.min_price||0);if(!v)continue;if(!m.has(n)||m.get(n)>v)m.set(n,v)}META.sp={items:list.length,names:m.size}}catch(e){META.sp={parseError:String(e)}}return m}
(async()=>{
  const lis=await lisAll();console.log("lis items",lis.size);const sp=await skinport();console.log("skinport",sp.size);
  let ok=0,fail=0;
  for(let i=0;i<names.length;i++){const n=names[i];const rec={...(out[n]||{})};
    if(META.dm.fail<40||META.dm.ok>0){try{const p=await dmarket(n);if(p!=null){rec.dm=p;ok++;META.dm.ok++}else{fail++;META.dm.fail++}}catch(e){fail++;META.dm.fail++;META.dm.lastError=String(e.message||e);if(/429/.test(e.message))await sleep(5000)}}
    const lp=lis.get(n)||lis.get(stripPhase(n));if(lp)rec.ls=lp;const spp=sp.get(n)||sp.get(stripPhase(n));if(spp)rec.sp=spp;
    if(rec.dm||rec.ls||rec.sp){rec.t=now;out[n]=rec}
    if(i%50===0)console.log(i,"/",names.length,"ok",ok,"fail",fail);if(!(META.dm.fail>=40&&META.dm.ok===0))await sleep(350)}
  fs.mkdirSync(path.join(root,"data"),{recursive:true});fs.writeFileSync(path.join(root,"data/prices.json"),JSON.stringify(out));META.finished=new Date().toISOString();META.priced=Object.keys(out).length;fs.writeFileSync(path.join(root,"data/prices-meta.json"),JSON.stringify(META,null,1));
  console.log("done",Object.keys(out).length,"priced; dm ok",ok,"fail",fail)})();
