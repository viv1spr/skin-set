// Node: node admin/build.js  — rebuilds blog pages (all languages), indexes, rss, sitemap from blog/posts.json
const fs=require("fs"),path=require("path");const E=require("./engine.js");
const root=path.join(__dirname,"..");E.setSkins(JSON.parse(fs.readFileSync(path.join(__dirname,"skins-api.json"),"utf8")));
const LANGS=JSON.parse(fs.readFileSync(path.join(root,"blog/_langs.json"),"utf8"));E.setLangs(LANGS);try{E.setPrices(JSON.parse(fs.readFileSync(path.join(root,"data/prices.json"),"utf8")))}catch(e){}
const posts=JSON.parse(fs.readFileSync(path.join(root,"blog/posts.json"),"utf8"));
let n=0;
for(const lang of Object.keys(LANGS)){const suf=lang==="ru"?"":"."+lang;const dir=path.join(root,LANGS[lang].blog.replace(/^\//,""));
  const tpl=fs.readFileSync(path.join(root,"blog/_template"+suf+".html"),"utf8"),itpl=fs.readFileSync(path.join(root,"blog/_index_template"+suf+".html"),"utf8");
  fs.mkdirSync(dir,{recursive:true});
  for(const p of posts){const d=path.join(dir,p.slug);const html=p.draft?null:E.buildPost(tpl,p,posts,lang);if(!html){if(fs.existsSync(d))fs.rmSync(d,{recursive:true});continue}fs.mkdirSync(d,{recursive:true});fs.writeFileSync(path.join(d,"index.html"),html);n++}
  fs.writeFileSync(path.join(dir,"index.html"),E.buildIndex(itpl,posts,lang));fs.writeFileSync(path.join(dir,"rss.xml"),E.buildRss(posts,lang))}
fs.writeFileSync(path.join(root,"sitemap.xml"),E.buildSitemap(fs.readFileSync(path.join(root,"sitemap.xml"),"utf8"),posts));
console.log("built",n,"post pages");
