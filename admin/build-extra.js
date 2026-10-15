// Node 20 + sharp: adds every CS2 skin missing from the builder (new cases, gloves, knives) to data/skins-extra.json,
// with main colors extracted from the official image. Existing entries are kept (manual fixes survive).
const fs=require("fs"),path=require("path");const sharp=require("sharp");
const root=path.join(__dirname,"..");
const api=JSON.parse(fs.readFileSync(path.join(__dirname,"skins-api.json"),"utf8"));
const base=new Set(JSON.parse(fs.readFileSync(path.join(root,"data/skins-base.json"),"utf8")).map(x=>x.toLowerCase()));
let extra=[];try{extra=JSON.parse(fs.readFileSync(path.join(root,"data/skins-extra.json"),"utf8"))}catch(e){}
const have=new Set([...base,...extra.map(e=>(e[1].replace("★ ","")+" | "+e[2]).toLowerCase())]);
const SLOT={"AK-47":"ak","M4A4":"m4","M4A1-S":"m4","AWP":"awp","Desert Eagle":"deagle","USP-S":"usp","Glock-18":"glock","P250":"p250","Five-SeveN":"fiveseven","Tec-9":"tec9","CZ75-Auto":"cz75","R8 Revolver":"r8","Dual Berettas":"duals","P2000":"p2000","MAC-10":"mac10","MP9":"mp9","MP7":"mp7","MP5-SD":"mp5","UMP-45":"ump","P90":"p90","PP-Bizon":"bizon","FAMAS":"famas","Galil AR":"galil","SG 553":"sg553","AUG":"aug","SSG 08":"ssg","SCAR-20":"scar","G3SG1":"g3","Nova":"nova","XM1014":"xm","MAG-7":"mag7","Sawed-Off":"sawed","M249":"m249","Negev":"negev"};
const slotOf=r=>r[4]==="Gloves"?"gloves":r[4]==="Knives"?"knife":SLOT[r[3]]||null;
function tierOf(r){const [name,,rar,weapon,cat]=r;const pat=(name.split(" | ")[1]||"").toLowerCase();
  if(cat==="Gloves")return 4;
  if(cat==="Knives"){const top=/doppler|fade|lore|tiger tooth|autotronic|slaughter|crimson web|marble/.test(pat);const prem=/karambit|m9 bayonet|butterfly|talon|skeleton/i.test(weapon);const cheap=/gut|navaja|shadow daggers/i.test(weapon);if(prem)return top?5:4;if(cheap)return 3;return top?4:3}
  const big=/^(AK-47|AWP|M4A4|M4A1-S)$/.test(weapon);if(/contraband/i.test(rar))return 5;if(/covert/i.test(rar))return big?3:2;if(/classified/i.test(rar))return 2;if(/restricted/i.test(rar))return big?2:1;return 1}
function rgb2lab(r,g,b){let [x,y,z]=[r/255,g/255,b/255].map(v=>v>.04045?Math.pow((v+.055)/1.055,2.4):v/12.92);[x,y,z]=[(x*.4124+y*.3576+z*.1805)/.95047,(x*.2126+y*.7152+z*.0722),(x*.0193+y*.1192+z*.9505)/1.08883].map(t=>t>.008856?Math.cbrt(t):7.787*t+16/116);return [116*y-16,500*(x-y),200*(y-z)]}
const hex=(r,g,b)=>"#"+[r,g,b].map(v=>Math.round(v).toString(16).padStart(2,"0")).join("");
async function colorsOf(url){const r=await fetch(url);if(!r.ok)throw new Error("img "+r.status);const buf=Buffer.from(await r.arrayBuffer());
  const {data,info}=await sharp(buf).resize(128,96,{fit:"inside"}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  const bins=new Map();let tot=0;for(let i=0;i<data.length;i+=4){if(data[i+3]<140)continue;const R=data[i],G=data[i+1],B=data[i+2];const k=((R>>4)<<8)|((G>>4)<<4)|(B>>4);const e=bins.get(k)||{n:0,r:0,g:0,b:0};e.n++;e.r+=R;e.g+=G;e.b+=B;bins.set(k,e);tot++}
  if(!tot)return null;let cl=[...bins.values()].map(e=>({n:e.n,r:e.r/e.n,g:e.g/e.n,b:e.b/e.n}));cl.forEach(e=>e.lab=rgb2lab(e.r,e.g,e.b));cl.sort((a,b)=>b.n-a.n);
  const out=[];for(const e of cl){const h=out.find(o=>Math.hypot(o.lab[0]-e.lab[0],o.lab[1]-e.lab[1],o.lab[2]-e.lab[2])<16);if(h){const n=h.n+e.n;h.r=(h.r*h.n+e.r*e.n)/n;h.g=(h.g*h.n+e.g*e.n)/n;h.b=(h.b*h.n+e.b*e.n)/n;h.n=n;h.lab=rgb2lab(h.r,h.g,h.b)}else out.push({...e});if(out.length>40)break}
  out.forEach(o=>{const mx=Math.max(o.r,o.g,o.b),mn=Math.min(o.r,o.g,o.b);const sat=mx?(mx-mn)/mx:0;const light=(mx+mn)/510;o.score=(o.n/tot)*(0.25+sat*1.6)*(light<.08?.35:1)});
  out.sort((a,b)=>b.score-a.score);return out.filter(o=>o.n/tot>0.025).slice(0,3).map(o=>hex(o.r,o.g,o.b))}
(async()=>{const todo=api.filter(r=>slotOf(r)&&!have.has((r[0]+(r[5]?" ("+r[5]+")":"")).toLowerCase()));let ok=0,fail=0;
  const work=async()=>{while(todo.length){const r=todo.shift();try{const c=await colorsOf(r[1]);if(c&&c.length){const star=r[4]==="Gloves"||r[4]==="Knives";extra.push([slotOf(r),(star?"★ ":"")+r[3],r[0].split(" | ").slice(1).join(" | ")+(r[5]?" ("+r[5]+")":""),tierOf(r),c,r[1],r[6]||""]);ok++}else fail++}catch(e){fail++}}};
  await Promise.all(Array.from({length:8},work));fs.writeFileSync(path.join(root,"data/skins-extra.json"),JSON.stringify(extra));console.log("extra skins:",extra.length,"added",ok,"failed",fail)})();
