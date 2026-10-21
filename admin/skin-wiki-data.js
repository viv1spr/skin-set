// node admin/skin-wiki-data.js  (нужен локальный сервер на :8811 из корня) → data/wiki-sets.json
const {chromium}=require(process.env.PW||'/opt/npm-tools/node_modules/playwright');
const fs=require('fs');const names=JSON.parse(fs.readFileSync(__dirname+'/../data/skins-base.json','utf8'));
// + все скины, которые попадают в примеры сетов на страницах бюджетов
try{const B=JSON.parse(fs.readFileSync(__dirname+'/../data/budget-sets.json','utf8'));for(const p in B)for(const k in B[p])for(const r of B[p][k])if(r[1]){const n=r[1].replace('★ ','')+' | '+r[2];if(!names.includes(n))names.push(n)}}catch(e){}
(async()=>{const br=await chromium.launch(process.env.PW?{}:{executablePath:'/opt/pw-browsers/chromium'});
const pg=await br.newPage();await pg.route(/steamstatic|githubusercontent|auth\.skin-set|googleapis|gstatic/,r=>r.abort());
await pg.goto(process.env.BASE||'http://localhost:8811/');
await pg.waitForFunction(()=>window.PRICES&&SKINS.some(s=>s.priceRub),null,{timeout:30000});
const out=await pg.evaluate(names=>{const key=s=>s.weapon.replace("★ ","")+" | "+s.skin;const by={};SKINS.forEach(s=>by[key(s)]=by[key(s)]||s);
 const hex=c=>c;const res={};
 const lab=PRESETS.map(p=>p.c.map(hexToLab));
 const row=s=>[s.slot,s.weapon,s.skin,Math.round(s.priceRub||PRICE_MID[s.tier]||0),s.wearShown||""];
 for(const n of names){const s=by[n];if(!s)continue;
  const cols=s.colors.slice(0,2);state.colors=[...cols];state.preset=-1;state.hidden=[];state.extra=[];state.wear="any";state.wearBy={};
  const slotId=s.slot;const p=s.priceRub||PRICE_MID[s.tier]||0;
  const run=b=>{state.budgetRub=b;state.budget=b==null?5:tierFor(b);state.locked={[slotId]:s.i};state.offset={};state.frozen=null;state.hist={};
    if(!active().some(a=>a.id===slotId))state.extra=[slotId];render();return active().map(sl=>{const c=current(sl.id);return c?row(c.s):null}).filter(Boolean)};
  const cheap=run(Math.round(p+Math.max(3000,p*.35)));const lux=run(null);state.extra=[];
  // похожие: тот же слот, ближе всего по цвету
  const T=s.colors.slice(0,2).map(hexToLab);
  const sim=SKINS.filter(x=>x.slot===s.slot&&key(x)!==n).map(x=>[score(x,T),x]).sort((a,b)=>a[0]-b[0]).slice(0,8).map(z=>key(z[1]));
  // ближайший пресет
  const pd=lab.map((L,i)=>[score(s,L),i]).sort((a,b)=>a[0]-b[0]);
  res[n]={slot:s.slot,w:s.weapon,sk:s.skin,c:s.colors,cheap,lux,sim,preset:pd[0][1],p:Math.round(p)}}
 return res},names);
fs.writeFileSync(__dirname+'/../data/wiki-sets.json',JSON.stringify(out));console.log(Object.keys(out).length);await br.close()})();
