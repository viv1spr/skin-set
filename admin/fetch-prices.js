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
const stripPhase=n=>n.replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,"");
const phaseOf=n=>(n.match(/\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/)||[])[1]||null;
async function dmarket(name){
  const star=isStar.get(name)||/Gloves|Hand Wraps|Knife|Bayonet|Karambit|Daggers/.test(name);
  const title=(star?"★ ":"")+stripPhase(name);const ph=phaseOf(name);
  const url="https://api.dmarket.com/exchange/v1/market/items?gameId=a8db&currency=USD&limit=20&orderBy=price&orderDir=asc&title="+encodeURIComponent(title);
  const r=await fetch(url,{headers:{"Accept":"application/json","User-Agent":"skin-set.com price bot"}});if(!r.ok)throw new Error("dm "+r.status);
  const j=await r.json();const objs=(j.objects||[]).filter(o=>o.title===title&&!/StatTrak|Souvenir/.test(o.title));
  const cand=ph?objs.filter(o=>((o.extra||{}).phase||"").toLowerCase().replace("-"," ")===ph.toLowerCase().replace("-"," ")):objs;
  const prices=cand.map(o=>+((o.price||{}).USD||0)/100).filter(x=>x>0);return prices.length?Math.min(...prices):null}
async function lisAll(){
  for(const u of ["https://lis-skins.com/market_export_json/api_csgo_full.json","https://lis-skins.com/market_export_json/csgo.json"]){
    try{const r=await fetch(u,{headers:{"User-Agent":"skin-set.com price bot"}});if(!r.ok)continue;const j=await r.json();const list=Array.isArray(j)?j:(j.items||j.data||[]);const m=new Map();
      for(const it of list){const n=(it.name||it.market_hash_name||"").replace("★ ","");const p=+(it.price||it.min_price||it.price_usd||0);if(!n||!p)continue;if(/StatTrak|Souvenir/.test(n))continue;if(!m.has(n)||m.get(n)>p)m.set(n,p)}
      if(m.size)return m}catch(e){console.log("lis",u,e.message)}}
  return new Map()}
(async()=>{
  const lis=await lisAll();console.log("lis items",lis.size);
  let ok=0,fail=0;
  for(let i=0;i<names.length;i++){const n=names[i];const rec={...(out[n]||{})};
    try{const p=await dmarket(n);if(p!=null){rec.dm=p;ok++}else fail++}catch(e){fail++;if(/429/.test(e.message))await sleep(5000)}
    const lp=lis.get(n)||lis.get(stripPhase(n));if(lp)rec.ls=lp;
    if(rec.dm||rec.ls){rec.t=now;out[n]=rec}
    if(i%50===0)console.log(i,"/",names.length,"ok",ok,"fail",fail);await sleep(350)}
  fs.mkdirSync(path.join(root,"data"),{recursive:true});fs.writeFileSync(path.join(root,"data/prices.json"),JSON.stringify(out));
  console.log("done",Object.keys(out).length,"priced; dm ok",ok,"fail",fail)})();
