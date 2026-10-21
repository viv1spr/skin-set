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
    lab = "".join(f'.cbar .cb-i[data-cat="{k}"] span::after{{content:"{v}"}}' for k, v in SHORT[lang].items())
    return ('<style id="cbar1">@media(max-width:700px){'
            '.cbar{grid-auto-flow:column!important;grid-template-columns:none!important;grid-auto-columns:minmax(0,1fr)!important;gap:3px!important;padding:6px 8px 8px!important}'
            '.cb-d>.cb-i,.cbar>.cb-i{height:42px!important;padding:5px 1px 4px!important;gap:4px!important;justify-content:center}'
            '.cbar .cb-i svg{width:20px!important;height:8px!important}'
            '.cbar .cb-i span{display:block!important;font-size:0!important;line-height:1!important;-webkit-line-clamp:unset!important;white-space:nowrap;overflow:visible!important}'
            '.cbar .cb-i span::after{font:600 .56rem/1 var(--hud);letter-spacing:.02em;white-space:nowrap}'
            '.cbar .cb-i em{top:2px!important;right:2px!important;padding:1px 3px!important;font-size:.5rem!important;line-height:1!important}'
            '.cbar>.cb-d .cb-m{left:0!important;right:auto!important}.cbar>.cb-d:nth-child(n+4) .cb-m{left:auto!important;right:0!important}'
            + lab + '}@media(max-width:360px){.cbar .cb-i span::after{font-size:.5rem}}</style>')


def main():
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
        if "/admin/" in f: continue
        s = open(f, encoding="utf-8").read()
        if 'id="cbarCss"' not in s: continue
        m = re.search(r'<html lang="([^"]+)"', s); lang = LANGOF.get(m.group(1) if m else "ru", "ru")
        o = re.sub(r'<style id="cbar1">.*?</style>', "", s, flags=re.S)
        i = o.find("</style>", o.find('id="cbarCss"')) + len("</style>")
        o = o[:i] + css(lang) + o[i:]
        if o != s: open(f, "w", encoding="utf-8").write(o); n += 1
    print(n)


if __name__ == "__main__":
    main()
