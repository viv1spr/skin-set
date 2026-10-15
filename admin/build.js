// Node: node admin/build.js  — rebuilds blog pages, index, rss, sitemap from blog/posts.json
const fs=require("fs"),path=require("path");const E=require("./engine.js");E.setSkins(JSON.parse(fs.readFileSync(path.join(__dirname,"skins-min.json"),"utf8")));
const root=path.join(__dirname,"..");const posts=JSON.parse(fs.readFileSync(path.join(root,"blog/posts.json"),"utf8"));
const tpl=fs.readFileSync(path.join(root,"blog/_template.html"),"utf8"),itpl=fs.readFileSync(path.join(root,"blog/_index_template.html"),"utf8");
for(const p of posts){const d=path.join(root,"blog",p.slug);if(p.draft){if(fs.existsSync(d))fs.rmSync(d,{recursive:true});continue}fs.mkdirSync(d,{recursive:true});fs.writeFileSync(path.join(d,"index.html"),E.buildPost(tpl,p,posts))}
fs.writeFileSync(path.join(root,"blog/index.html"),E.buildIndex(itpl,posts));
fs.writeFileSync(path.join(root,"blog/rss.xml"),E.buildRss(posts));
fs.writeFileSync(path.join(root,"sitemap.xml"),E.buildSitemap(fs.readFileSync(path.join(root,"sitemap.xml"),"utf8"),posts));
console.log("built",posts.filter(p=>!p.draft).length,"posts");
