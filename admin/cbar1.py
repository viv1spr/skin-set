# -*- coding: utf-8 -*-
"""Мобильный конструктор: категории оружия в одну строку (короткие подписи). python3 admin/cbar1.py"""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORT = {
 "ru": dict(prem="Ножи", pist="Пистолеты", rifle="Винтовки", snip="Снайп.", smg="ПП", shot="Дробов.", lmg="Пулем."),
 "en": dict(prem="Knife", pist="Pistols", rifle="Rifles", snip="Snipers", smg="SMGs", shot="Shotguns", lmg="MGs"),
 "de": dict(prem="Messer", pist="Pistolen", rifle="Gewehre", snip="Sniper", smg="MPs", shot="Schrot", lmg="MGs"),
 "pt": dict(prem="Facas", pist="Pistolas", rifle="Rifles", snip="Snipers", smg="SMGs", shot="Escop.", lmg="Metral."),
 "tr": dict(prem="Bıçak", pist="Tabanca", rifle="Tüfek", snip="Keskin", smg="SMG", shot="Pompalı", lmg="Makineli"),
 "pl": dict(prem="Noże", pist="Pistolety", rifle="Karabiny", snip="Snajp.", smg="PM", shot="Strzelby", lmg="KM"),
}
LANGOF = {"ru": "ru", "en": "en", "de": "de", "pt-BR": "pt", "pt": "pt", "tr": "tr", "pl": "pl"}


def css(lang):
    return ('<style id="cbar1">@media(max-width:700px){'
            '.cbar{display:flex!important;flex-wrap:nowrap!important;overflow-x:auto!important;overflow-y:hidden!important;gap:5px!important;padding:6px 12px 8px!important;scrollbar-width:none;-webkit-overflow-scrolling:touch}'
            '.cbar::-webkit-scrollbar{display:none}'
            '.cbar>.cb-d,.cbar>.cb-i{flex:0 0 calc((100% - 15px) / 3.5)!important;min-width:0}'
            '.cb-d>.cb-i,.cbar>.cb-i{width:100%;height:50px!important;padding:5px 4px 4px!important;gap:4px!important;justify-content:center}'
            '.cbar .cb-i svg{width:24px!important;height:10px!important}'
            '.cbar .cb-i span{font:600 .74rem/1.1 var(--hud)!important;letter-spacing:.03em!important;white-space:normal!important;display:-webkit-box!important;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}'
            '.cbar .cb-i em{top:3px!important;right:3px!important;padding:2px 5px!important;font-size:.62rem!important;line-height:1!important}'
            '.cbar .cb-m{position:fixed!important;bottom:auto!important;right:auto!important;width:max-content;min-width:190px;max-width:calc(100vw - 24px);max-height:55vh;overflow-y:auto;z-index:120}'
            '}</style>'
            '<script id="cbar1js">(()=>{const mq=matchMedia("(max-width:700px)");const place=()=>{if(!mq.matches)return;const d=document.querySelector(".cbar .cb-d.open");if(!d)return;const b=d.querySelector(".cb-i"),m=d.querySelector(".cb-m");if(!b||!m)return;const r=b.getBoundingClientRect();const w=m.offsetWidth;m.style.setProperty("top",(r.bottom+4)+"px","important");m.style.setProperty("left",Math.max(12,Math.min(r.left,innerWidth-w-12))+"px","important")};'
            'document.addEventListener("click",e=>{if(e.target.closest(".cbar"))requestAnimationFrame(place)},true);document.addEventListener("click",e=>{if(e.target.closest(".cbar .cb-i"))setTimeout(place,0)});'
            'addEventListener("scroll",place,{passive:true});addEventListener("resize",place);let SL=0,pend=0;document.addEventListener("scroll",e=>{if(e.target.classList&&e.target.classList.contains("cbar")){SL=e.target.scrollLeft;place()}},{passive:true,capture:true});const fixUp=()=>{pend=0;const c=document.querySelector(".cbar");if(c&&mq.matches&&Math.abs(c.scrollLeft-SL)>1)c.scrollLeft=SL;place()};const start=()=>new MutationObserver(()=>{if(!pend)pend=requestAnimationFrame(fixUp)}).observe(document.body,{childList:true,subtree:true});document.body?start():addEventListener("DOMContentLoaded",start)})();</script>')


def main():
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
        if "/admin/" in f: continue
        s = open(f, encoding="utf-8").read()
        if 'id="cbarCss"' not in s: continue
        m = re.search(r'<html lang="([^"]+)"', s); lang = LANGOF.get(m.group(1) if m else "ru", "ru")
        o = re.sub(r'<style id="cbar1">.*?</style>(<script id="cbar1js">.*?</script>)?', "", s, flags=re.S)
        i = o.find("</style>", o.find('id="cbarCss"')) + len("</style>")
        o = o[:i] + css(lang) + o[i:]
        if o != s: open(f, "w", encoding="utf-8").write(o); n += 1
    print(n)


if __name__ == "__main__":
    main()
