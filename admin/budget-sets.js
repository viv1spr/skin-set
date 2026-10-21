const {chromium}=require('/opt/npm-tools/node_modules/playwright');
const B=JSON.parse(process.argv[2]);const out={};
(async()=>{const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const pg=await br.newPage();await pg.route(/steamstatic|githubusercontent|auth\.skin-set/,r=>r.abort());
for(let p=0;p<9;p++){
 await pg.goto('(process.env.BASE||"http://localhost:8811/")');
 await pg.waitForFunction(()=>window.PRICES&&SKINS.some(s=>s.priceRub),null,{timeout:20000});
 const r=await pg.evaluate(([p,B])=>{const o={};state.preset=p;state.colors=[...PRESETS[p].c];state.hidden=[];state.extra=[];state.wear="any";state.wearBy={};
  const run=b=>{state.budgetRub=b;state.budget=b==null?5:tierFor(b);state.locked={};state.offset={};state.frozen=null;state.hist={};render();
   return active().map(sl=>{const c=current(sl.id);if(!c)return[sl.id,null];const s=c.s;const inb=!(CAPRUB&&CAPRUB[sl.id]===0);return[sl.id,s.weapon,s.skin,Math.round(s.priceRub||0),s.wearShown||"",inb]})};
  for(const b of B)o[b]=run(b);o.none=run(null);return o},[p,B]);
 out[p]=r;}
require('fs').writeFileSync(process.argv[3],JSON.stringify(out));await br.close()})();
