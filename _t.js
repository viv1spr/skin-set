const {chromium}=require('/opt/npm-tools/node_modules/playwright');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.stack.slice(0,300)));
await p.goto('http://localhost:8768/');await p.waitForFunction(()=>window.PRICES,null,{timeout:15000});await p.waitForTimeout(800);
for(const preset of [0,1,3,4,5]) for(const B of [20000,50000,150000]){
const r=await p.evaluate(([preset,B])=>{state.premium=true;state.preset=preset;state.colors=[...PRESETS[preset].c];state.locked={};state.offset={};state.budgetRub=B;render();
 const pr=sl=>{const c=current(sl.id);return c?(c.s.priceRub||PRICE_MID[c.s.tier]):0};
 const snap=()=>Object.fromEntries(active().map(sl=>[sl.id,pr(sl)]));const tot=o=>Object.values(o).reduce((a,b)=>a+b,0);
 const s0=snap();let mx=tot(s0),mn=tot(s0),viol=0;const bad=o=>{const pm=Math.min(o.knife||Infinity,o.gloves||Infinity);return ['ak','m4','awp'].some(k=>o[k]>pm)?1:0};viol+=bad(s0);
 for(let i=0;i<25;i++){for(const sl of active())state.offset[sl.id]=(state.offset[sl.id]||0)+1;render();const o=snap();mx=Math.max(mx,tot(o));mn=Math.min(mn,tot(o));viol+=bad(o)}
 return {s0,t0:tot(s0),mx,mn,viol}},[preset,B]);
console.log(preset,B,'total',r.t0,'range',r.mn,'-',r.mx,'viol',r.viol,JSON.stringify(r.s0))}
console.log(errs.slice(0,2));await b.close()})();
