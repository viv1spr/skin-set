# -*- coding: utf-8 -*-
"""Общая сетка служебных страниц (Обновления, Рынок, Матчи) — как у блога: колонка 980px, eyebrow, заголовок и лид."""
GRID_CSS = """
.pg{max-width:980px!important;margin:0 auto!important;padding:34px 20px 60px!important}
.pg>.crumbs{display:none}
.pg .pg-eb{display:flex!important;gap:12px;align-items:flex-start;margin:0 0 12px!important;padding:0!important;background:none!important;border:0!important;font:500 .78rem/1.45 var(--hud)!important;letter-spacing:.16em!important;text-transform:uppercase;color:var(--soft)!important}
.pg .pg-eb::before{content:"";flex:none;margin-top:.68em;width:28px;height:2px;background:var(--pick,#e8402a)}
.pg .pg-eb i{display:none!important}
.pg h1.pg-h{margin:0 0 10px!important;font:600 clamp(1.8rem,4vw,2.8rem)/1.05 var(--hud)!important;letter-spacing:.04em!important;text-transform:uppercase}
.pg .pg-l{color:var(--soft)!important;font-size:1.05rem!important;max-width:62ch!important;margin:0 0 28px!important}
@media(max-width:600px){.pg{padding:24px 20px 40px!important}}
"""
