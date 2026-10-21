# -*- coding: utf-8 -*-
"""Убирает «Как работает», «Сеты» и «Площадки» из верхнего меню в выпадающее «Ещё».
python3 admin/navmore.py  — пройтись по всем страницам сайта (идемпотентно).
Генераторы вызывают fix(html) перед записью.
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGOF = {"ru": "ru", "en": "en", "de": "de", "pt-BR": "pt", "pt": "pt", "tr": "tr", "pl": "pl"}
MORE = {
    "ru": ["/kak-rabotaet/", "/sety/", "/gde-kupit/"], "en": ["/en/how-it-works/", "/en/loadouts/", "/en/where-to-buy/"],
    "de": ["/de/so-funktionierts/", "/de/loadouts/", "/de/wo-kaufen/"], "pt": ["/pt/como-funciona/", "/pt/sets/", "/pt/onde-comprar/"],
    "tr": ["/tr/nasil-calisir/", "/tr/setler/", "/tr/nereden-alinir/"], "pl": ["/pl/jak-to-dziala/", "/pl/zestawy/", "/pl/gdzie-kupic/"],
}
LABEL = {"ru": "Ещё", "en": "More", "de": "Mehr", "pt": "Mais", "tr": "Daha fazla", "pl": "Więcej"}

CSS = """<style id="tmore-css">
.tabs .tmore{display:flex;align-items:center;gap:7px;padding:0 16px;background:none;border:0;border-left:1px solid var(--line);color:var(--soft);font:500 .9rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;cursor:pointer;white-space:nowrap;position:relative;height:100%;flex:0 0 auto}
.tabs .tmore:hover,.tabs .tmore.open{color:var(--ink)}
.tabs .tmore i{width:7px;height:7px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg) translateY(-2px);transition:transform .15s}
.tabs .tmore.open i{transform:rotate(-135deg) translateY(-1px)}
.tabs .tmore.on{color:var(--ink)}.tabs .tmore.on::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:var(--pick)}
.tmenu{position:fixed;z-index:200;min-width:200px;padding:6px;background:#15171c;border:1px solid var(--line2,rgba(255,255,255,.18));box-shadow:0 18px 40px rgba(0,0,0,.55)}
.tmenu[hidden]{display:none}
.tmenu a{display:block;padding:11px 12px;color:var(--soft,#b9b4a7);text-decoration:none;font:500 .92rem/1 var(--hud,sans-serif);letter-spacing:.08em;text-transform:uppercase;white-space:nowrap}
.tmenu a:hover,.tmenu a.on{background:rgba(255,255,255,.06);color:var(--ink,#fff)}
@media(max-width:900px){.tabs .tmore{padding:0 12px;font-size:.78rem;border-left:0}}
</style>"""
JS = """<script id="tmore-js">(()=>{const b=document.getElementById("tmore"),m=document.getElementById("tmenu");if(!b||!m)return;
const p=location.pathname;let on=false;m.querySelectorAll("a").forEach(a=>{if(p.startsWith(a.getAttribute("href"))){a.classList.add("on");on=true}});if(on)b.classList.add("on");
const place=()=>{const r=b.getBoundingClientRect();const w=m.offsetWidth;m.style.top=(r.bottom+4)+"px";m.style.left=Math.max(8,Math.min(r.left,innerWidth-w-8))+"px"};
const close=()=>{m.hidden=true;b.classList.remove("open");b.setAttribute("aria-expanded","false")};
b.addEventListener("click",e=>{e.stopPropagation();if(m.hidden){m.hidden=false;place();b.classList.add("open");b.setAttribute("aria-expanded","true")}else close()});
document.addEventListener("click",e=>{if(!m.contains(e.target))close()});addEventListener("resize",close);addEventListener("scroll",()=>{if(!m.hidden)place()},{passive:true});
document.addEventListener("keydown",e=>{if(e.key==="Escape")close()});
const t=b.closest(".tabs");if(t)t.addEventListener("scroll",()=>{if(!m.hidden)place()},{passive:true})})();</script>"""


def undo(s):
    """вернуть ссылки из «Ещё» обратно в меню (на место кнопки)"""
    m = re.search(r'<div class="tmenu" id="tmenu"[^>]*>(.*?)</div>', s, re.S)
    if not m: return s
    links = m.group(1)
    s = s.replace(m.group(0), "", 1)
    s = re.sub(r'<button class="tmore" id="tmore".*?</button>', lambda _: links, s, count=1, flags=re.S)
    s = re.sub(r'<style id="tmore-css">.*?</style>', "", s, count=1, flags=re.S)
    s = re.sub(r'<script id="tmore-js">.*?</script>', "", s, count=1, flags=re.S)
    return s


def fix(s):
    if 'id="tmenu"' in s: return s
    m = re.search(r'<html lang="([^"]+)"', s)
    lang = LANGOF.get(m.group(1) if m else "ru", "ru")
    nm = re.search(r'<nav class="tabs"[^>]*>.*?</nav>', s, re.S)
    if not nm: return s
    nav = nm.group(0); items = []
    for href in MORE[lang]:
        a = re.search(r'<a href="' + re.escape(href) + r'"[^>]*>.*?</a>', nav, re.S)
        if a:
            items.append(re.sub(r'\s(class="on"|class=on)', "", a.group(0)))
            nav = nav.replace(a.group(0), "", 1)
    if not items: return s
    btn = f'<button class="tmore" id="tmore" type="button" aria-haspopup="menu" aria-expanded="false"><span>{LABEL[lang]}</span><i></i></button>'
    if '<a class="twitch"' in nav: nav = nav.replace('<a class="twitch"', btn + '<a class="twitch"', 1)
    else: nav = nav.replace("</nav>", btn + "</nav>")
    s = s[:nm.start()] + nav + s[nm.end():]
    menu = f'<div class="tmenu" id="tmenu" role="menu" hidden>{"".join(items)}</div>'
    s = s.replace("</head>", CSS + "</head>", 1)
    i = s.rfind("</body>")
    return s[:i] + menu + JS + s[i:]


def main():
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
        if "/admin/" in f: continue
        s = open(f, encoding="utf-8").read(); o = fix(undo(s)) if "--redo" in __import__("sys").argv else fix(s)
        if o != s: open(f, "w", encoding="utf-8").write(o); n += 1
    print(n, "files")


if __name__ == "__main__":
    main()
