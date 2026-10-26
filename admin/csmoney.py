# -*- coding: utf-8 -*-
"""Партнёрские ссылки CS.MONEY (название бренда пишем только так: CS.MONEY).
Для предмета: market/buy/?search=<«AK-47 | Slate (Factory New)»> + UTM. Фаза Doppler в поиск не идёт."""
import re
from urllib.parse import quote

UTM = "utm_source=mediabuy&utm_medium=skin-set&utm_campaign=market&utm_content=link"
MARKET = "https://cs.money/market/buy/?" + UTM
WEAR_FULL = {"FN": "Factory New", "MW": "Minimal Wear", "FT": "Field-Tested", "WW": "Well-Worn", "BS": "Battle-Scarred"}
PHASE_RE = r"\s*\((?:Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$"
REL = 'target="_blank" rel="noopener sponsored"'
BUY = {"ru": "Купить на", "en": "Buy on", "de": "Kaufen bei", "pt": "Comprar na", "tr": "Satın al:", "pl": "Kup na"}


def url(name, wear=None):
    n = re.sub(PHASE_RE, "", name.replace("★ ", "").strip())
    if wear: n += f" ({WEAR_FULL.get(wear, wear)})"
    return "https://cs.money/market/buy/?search=" + quote(n, safe="") + "&" + UTM


# JS-выражение для шаблонов (переменная с полным названием скина → ссылка)
def js(var):
    return ('https://cs.money/market/buy/?search=${encodeURIComponent(String(' + var + ').replace(/★\\s*/,"").replace(/\\s*\\((Phase \\d|Ruby|Sapphire|Emerald|Black Pearl)\\)$/,""))}&' + UTM)

LABEL = {"ru": "Купить на CS.MONEY", "en": "Buy on CS.MONEY", "de": "Bei CS.MONEY kaufen", "pt": "Comprar na CS.MONEY", "tr": "CS.MONEY'de satın al", "pl": "Kup na CS.MONEY"}
