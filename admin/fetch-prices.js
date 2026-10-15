// Node 20: daily prices from Lis-Skins (public export) + Skinport (public API) as fallback.
// Writes data/prices.json: { "Weapon | Skin": { ls, sp, w:{FN,MW,FT,WW,BS}, t } } (USD, min per wear across sources)
// DMarket: public endpoint retired (needs API keys) — set DM_PUBLIC/DM_SECRET secrets later to enable.
const fs=require("fs"),path=require("path");
const root=path.join(__dirname,"..");
const base=JSON.parse(fs.readFileSync(path.join(root,"data/skins-base.json"),"utf8"));
let extra=[];try{extra=JSON.parse(fs.readFileSync(path.join(root,"data/skins-extra.json"),"utf8")).map(e=>e[1].replace("★ ","")+" | "+e[2])}catch(e){}
const names=[...new Set([...base,...extra])];
const META={started:new Date().toISOString()};const UA={"User-Agent":"Mozilla/5.0 (compatible; skin-set.com price bot)","Accept":"application/json"};
const WEAR={"Factory New":"FN","Minimal Wear":"MW","Field-Tested":"FT","Well-Worn":"WW","Battle-Scarred":"BS"};
function parseName(raw){let n=(raw||"").replace("★ ","").trim();if(/StatTrak|Souvenir/.test(n))return null;let w=null;const m=n.match(/\s*\((Factory New|Minimal Wear|Field-Tested|Well-Worn|Battle-Scarred)\)$/);if(m){w=WEAR[m[1]];n=n.slice(0,m.index)}return {n,w}}
function add(map,n,w,v){if(!(v>0))return;const r=map.get(n)||{min:Infinity,w:{}};r.min=Math.min(r.min,v);if(w)r.w[w]=Math.min(r.w[w]||Infinity,v);map.set(n,r)}
async function lis(){const m=new Map();for(const u of["https://lis-skins.com/market_export_json/csgo.json","https://lis-skins.ru/market_export_json/csgo.json"]){
  try{const r=await fetch(u,{headers:UA});if(!r.ok){META["ls_"+u]=r.status;continue}const list=await r.json();for(const it of list){const p=parseName(it.name);if(p)add(m,p.n,p.w,+it.price)}META.ls={url:u,items:list.length,names:m.size};if(m.size)return m}catch(e){META["ls_err"]=String(e)}}return m}
async function skinport(){const m=new Map();try{const r=await fetch("https://api.skinport.com/v1/items?app_id=730&currency=USD&tradable=0",{headers:{...UA,"Accept-Encoding":"br"}});if(!r.ok){META.sp_status=r.status;return m}
  const list=await r.json();for(const it of list){const p=parseName(it.market_hash_name);if(p)add(m,p.n,p.w,+it.min_price)}META.sp={items:list.length,names:m.size}}catch(e){META.sp_err=String(e)}return m}
// обычные фазы Doppler/Gamma Doppler стоят примерно одинаково — берём общую цену; «камни» (Ruby, Sapphire, Emerald, Black Pearl) стоят в разы дороже, площадки их не различают в выгрузке — цену не подставляем
const stripPhase=n=>n.replace(/\s*\((Phase \d)\)$/,"");
(async()=>{
  const [L,S]=await Promise.all([lis(),skinport()]);const now=Date.now();const out={};
  for(const n of names){const a=L.get(n)||L.get(stripPhase(n)),b=S.get(n)||S.get(stripPhase(n));if(!a&&!b)continue;
    const rec={t:now};if(a)rec.ls=+a.min.toFixed(2);if(b)rec.sp=+b.min.toFixed(2);const w={};for(const k of["FN","MW","FT","WW","BS"]){const v=Math.min((a&&a.w[k])||Infinity,(b&&b.w[k])||Infinity);if(isFinite(v))w[k]=+v.toFixed(2)}if(Object.keys(w).length)rec.w=w;out[n]=rec}
  fs.writeFileSync(path.join(root,"data/prices.json"),JSON.stringify(out));
  META.finished=new Date().toISOString();META.names=names.length;META.priced=Object.keys(out).length;fs.writeFileSync(path.join(root,"data/prices-meta.json"),JSON.stringify(META,null,1));
  console.log(JSON.stringify(META))})();
