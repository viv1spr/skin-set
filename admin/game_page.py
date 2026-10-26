# -*- coding: utf-8 -*-
"""Мини-игра «Что дороже?» (higher or lower по ценам скинов CS2) — отдельная «игровая» страница.
python3 admin/game_page.py — пишет data/game.json и страницы /igra-chto-dorozhe/, /en/higher-or-lower-cs2/.
Данные: data/catalog.json + data/prices.json (цены по качеству в $, картинки Steam)."""
import json, os, sys, html, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
from skins_wiki import head, header, FOOT, HOME, SITE, HREFLANG, WIKI  # noqa
from about import LANG_JS  # noqa
import navmore  # noqa
import csmoney  # noqa

e = lambda s: html.escape(str(s), quote=True)
URL = {"ru": "/igra-chto-dorozhe/", "en": "/en/higher-or-lower-cs2/"}
WEARS = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
MINP = 0.5  # $

# звания по длине серии (как ранги в CS:GO)
RANKS = {
 "ru": [(0, "Серебро"), (2, "Серебро — Элита"), (4, "Золотая звезда"), (6, "Магистр золотой звезды"), (8, "Магистр-хранитель"),
        (11, "Заслуженный магистр-хранитель"), (14, "Легендарный беркут"), (17, "Великий магистр высшего ранга"), (20, "Всемирная элита")],
 "en": [(0, "Silver"), (2, "Silver Elite"), (4, "Gold Nova"), (6, "Gold Nova Master"), (8, "Master Guardian"),
        (11, "Distinguished Master Guardian"), (14, "Legendary Eagle"), (17, "Supreme Master First Class"), (20, "Global Elite")],
}
RCOL = ["#9aa4b1", "#c0c8d2", "#e4ae39", "#ffcf4a", "#4b9bff", "#62b6ff", "#a970ff", "#d24bff", "#ff4b6e"]

T = {
 "ru": dict(
  title="Что дороже? Игра по скинам CS2 — угадай, какой скин дороже | Skinset",
  desc="Мини-игра по скинам CS2: два скина — какой дороже? Угадывай цены ножей, перчаток и пушек подряд, поднимай звание до Всемирной элиты и ставь рекорд. Реальные цены рынка.",
  h1="Что дороже?", sub="Угадай цену скина CS2", tag="Мини-игра Skinset",
  intro="Цена левого скина известна. Правый — дороже или дешевле? Угадывай подряд, поднимай звание от Серебра до Всемирной элиты.",
  play="Играть", hi="Дороже", lo="Дешевле", vs="VS", streak="Серия", best="Рекорд", rank="Звание", next="до",
  again="Ещё раз", over="Мимо!", res="Серия: {n}", newbest="🏆 Новый рекорд!", rankup="Новое звание", share="Поделиться", copied="Скопировано!",
  buy="Купить на CS.MONEY", sharetxt="Угадал {n} цен скинов CS2 подряд и дошёл до звания «{r}» в игре «Что дороже?» 🔥 Побьёшь? ",
  loading="Загружаю скины…", fs="На весь экран", gate_h="Войди, чтобы играть дальше", gate_p="Бесплатные попытки закончились. Войди через Steam — это бесплатно и занимает 10 секунд, а игра станет безлимитной.", gate_b="Войти через Steam", keys="Клавиши: ↑ дороже, ↓ дешевле", sound="Звук",
  cats=[("all", "Все"), ("knife", "Ножи"), ("gloves", "Перчатки"), ("guns", "Пушки")],
  cur=["", " ₽"], rate=90, was="стоит", ladder="Звания",
  how_h="Как играть", how=["Слева скин с известной ценой, справа — с неизвестной.", "Нажми «Дороже» или «Дешевле» (или стрелки ↑/↓ на клавиатуре).", "Угадал — правый скин переезжает налево и появляется новый. Ошибся — серия обнуляется.", "Чем длиннее серия, тем ближе цены и выше звание: от Серебра до Всемирной элиты за 20 ответов подряд."],
  faq=[("Откуда цены?", "Это минимальные цены на рынке для указанного качества (Factory New, Field-Tested и т. д.). Они обновляются каждые 4 часа — те же цены, что в конструкторе Skinset."),
       ("Где сохраняется рекорд?", "В твоём браузере. Если почистить данные сайта или зайти с другого устройства, рекорд начнётся заново."),
       ("Почему один и тот же скин стоит по-разному?", "Цена сильно зависит от качества: Factory New часто в разы дороже Battle-Scarred. Поэтому в игре всегда указано качество.")],
  more="Собери свой сет", more_p="Понравились скины? Собери из них инвентарь в одном цвете в конструкторе."),
 "en": dict(
  title="Higher or Lower: CS2 skin price game — which skin costs more? | Skinset",
  desc="A CS2 skin price game: two skins — which one costs more? Guess knife, glove and gun prices in a row, rank up from Silver to Global Elite and set a record. Real market prices.",
  h1="Higher or Lower", sub="Guess the CS2 skin price", tag="Skinset mini-game",
  intro="You know the left skin's price. Is the right one higher or lower? Guess in a row and rank up from Silver to Global Elite.",
  play="Play", hi="Higher", lo="Lower", vs="VS", streak="Streak", best="Best", rank="Rank", next="to",
  again="Play again", over="Miss!", res="Streak: {n}", newbest="🏆 New record!", rankup="Rank up", share="Share", copied="Copied!",
  buy="Buy on CS.MONEY", sharetxt="I guessed {n} CS2 skin prices in a row and hit {r} in Higher or Lower 🔥 Can you beat it? ",
  loading="Loading skins…", fs="Fullscreen", gate_h="Sign in to keep playing", gate_p="Your free tries are used up. Sign in with Steam — it's free and takes 10 seconds — and play without limits.", gate_b="Sign in with Steam", keys="Keys: ↑ higher, ↓ lower", sound="Sound",
  cats=[("all", "All"), ("knife", "Knives"), ("gloves", "Gloves"), ("guns", "Guns")],
  cur=["$", ""], rate=1, was="costs", ladder="Ranks",
  how_h="How to play", how=["The left skin's price is shown, the right one is hidden.", "Press Higher or Lower (or the ↑/↓ keys).", "Right — the right skin moves left and a new one appears. Wrong — your streak resets.", "The longer the streak, the closer the prices and the higher your rank: Silver to Global Elite in 20 in a row."],
  faq=[("Where do the prices come from?", "They're the lowest market prices for the stated wear (Factory New, Field-Tested, etc.), updated every 4 hours — the same prices as in the Skinset builder."),
       ("Where is my record saved?", "In your browser. Clearing site data or switching devices resets it."),
       ("Why does the same skin have different prices?", "Wear matters a lot: Factory New is often several times pricier than Battle-Scarred, so the game always shows the wear.")],
  more="Build your set", more_p="Like these skins? Build a matching loadout from them in the builder."),
}

CSS = r"""
body{background:#07080c}
.gm{--ct:#3a7bff;--t:#ff8a1f;--ok:#2bd673;--bad:#ff3b4a;max-width:none!important;padding:0!important}
.gm-stage{position:relative;overflow:hidden;height:calc(100vh - 64px);height:calc(100svh - 64px);min-height:560px;display:flex;flex-direction:column;padding:14px 18px 12px;background:
 radial-gradient(900px 500px at 15% 40%,rgba(58,123,255,.18),transparent 60%),radial-gradient(900px 500px at 85% 40%,rgba(255,138,31,.16),transparent 60%),
 linear-gradient(180deg,#0b0d14,#07080c)}
.gm-stage::before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:44px 44px;mask-image:radial-gradient(ellipse at center,#000 30%,transparent 80%);pointer-events:none}
.gm-in{position:relative;width:100%;max-width:none;margin:0;flex:1;display:flex;flex-direction:column;min-height:0}
.gm-stage:fullscreen{height:100vh;padding:18px 24px 14px}
.gm-hud{position:relative;display:grid;grid-template-columns:1fr auto 1fr;align-items:stretch;margin-bottom:12px;min-height:74px;
 background:linear-gradient(180deg,rgba(20,24,36,.92),rgba(10,12,18,.92));border:1px solid rgba(255,255,255,.08);
 clip-path:polygon(14px 0,calc(100% - 14px) 0,100% 14px,100% 100%,0 100%,0 14px);box-shadow:inset 0 1px 0 rgba(255,255,255,.06)}
.gm-hud::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:linear-gradient(90deg,var(--ct),transparent 35%,transparent 65%,var(--t))}
.gm-hud .l{display:flex;align-items:center;gap:4px;padding:0 16px}
.gm-hud .l button{height:34px;padding:0 14px;background:rgba(255,255,255,.04);border:0;color:#8f8a7f;font:700 .74rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;cursor:pointer;
 clip-path:polygon(8px 0,100% 0,calc(100% - 8px) 100%,0 100%);transition:background .15s,color .15s}
.gm-hud .l button:hover{color:#fff;background:rgba(255,255,255,.1)}
.gm-hud .l button.on{background:linear-gradient(180deg,#ff6a3d,#e8402a);color:#fff;text-shadow:0 1px 0 rgba(0,0,0,.3)}
.gm-score{position:relative;display:flex;align-items:center;justify-content:center;gap:16px;padding:0 44px;margin:-1px 0;
 background:linear-gradient(180deg,#1b0f0a,#0c0706);border-left:1px solid rgba(255,138,31,.35);border-right:1px solid rgba(255,138,31,.35);
 clip-path:polygon(0 0,100% 0,calc(100% - 22px) 100%,22px 100%)}
.gm-score::after{content:"";position:absolute;left:22px;right:22px;bottom:0;height:3px;background:linear-gradient(90deg,transparent,#ff8a1f,transparent)}
.gm-score .cur{display:flex;flex-direction:column;align-items:center;line-height:1}
.gm-score small{font:700 .6rem/1 var(--hud);letter-spacing:.32em;text-transform:uppercase;color:#ff9d4d;margin-bottom:3px}
.gm-score #gs{font:700 3rem/1 var(--hud);color:#fff;font-variant-numeric:tabular-nums;text-shadow:0 0 24px rgba(255,120,40,.65),0 2px 0 #000}
.gm-score #gs.bump{animation:gmBump .45s ease}
.gm-score .fl{font-size:1.5rem;filter:drop-shadow(0 0 8px rgba(255,120,30,.8));opacity:0;transform:scale(.4);transition:opacity .25s,transform .25s}
.gm-score.hot .fl{opacity:1;transform:none;animation:gmFl 1s ease-in-out infinite alternate}
.gm-score .bs{display:flex;flex-direction:column;align-items:center;gap:3px;padding-left:16px;border-left:1px solid rgba(255,255,255,.1)}
.gm-score .bs small{color:#8f8a7f}.gm-score #gb{font:700 1.3rem/1 var(--hud);color:#ffcf4a}
.gm-hud .r{display:flex;justify-content:flex-end;align-items:center;gap:14px;padding:0 14px 0 16px}
.gm-rank{display:flex;align-items:center;gap:12px;min-width:0}
.gm-rank .em{width:46px;height:52px;flex:none;filter:drop-shadow(0 0 10px var(--rk,#9aa4b1))}
.gm-rank .em path.sh{fill:#0d1018;stroke:var(--rk,#9aa4b1);stroke-width:2.5}.gm-rank .em path.cv{fill:var(--rk,#9aa4b1)}
.gm-rank .tx{min-width:0}.gm-rank .tx small{display:block;font:700 .58rem/1 var(--hud);letter-spacing:.28em;text-transform:uppercase;color:#8f8a7f;margin-bottom:3px}
.gm-rank b{display:block;font:700 .95rem/1.1 var(--hud);letter-spacing:.06em;text-transform:uppercase;color:var(--rk,#c0c8d2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:240px}
.gm-xp{display:flex;gap:3px;margin-top:6px;width:200px}.gm-xp i{flex:1;height:7px;background:rgba(255,255,255,.1);transform:skewX(-20deg);transition:background .25s,box-shadow .25s}
.gm-xp i.on{background:var(--rk,#9aa4b1);box-shadow:0 0 8px var(--rk,#9aa4b1)}
.gm-rank #grx{display:block;margin-top:4px;font-size:.66rem;color:#8f8a7f;white-space:nowrap}
.gm-rank.up .em{animation:gmBump .6s ease}
.gm-snd{width:40px;height:40px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);color:#c9c4b8;cursor:pointer;font-size:1rem;clip-path:polygon(8px 0,100% 0,100% calc(100% - 8px),calc(100% - 8px) 100%,0 100%,0 8px)}
.gm-snd:hover{background:rgba(255,255,255,.1);color:#fff}
@keyframes gmFl{from{transform:translateY(0) scale(1)}to{transform:translateY(-2px) scale(1.12)}}
.gm-arena{position:relative;flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:0;border-radius:18px;overflow:hidden;border:1px solid rgba(255,255,255,.1);box-shadow:0 30px 80px rgba(0,0,0,.6)}
.gm-card{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px 26px 22px;min-height:0;transition:background .25s}
.gm-card.a{background:linear-gradient(160deg,rgba(58,123,255,.22),rgba(12,16,30,.95) 60%)}
.gm-card.b{background:linear-gradient(200deg,rgba(255,138,31,.2),rgba(30,16,10,.95) 60%)}
.gm-card .rar{pointer-events:none;position:absolute;inset:auto 0 0 0;height:4px;background:var(--rc,#e8402a);box-shadow:0 0 20px var(--rc,#e8402a)}
.gm-card .im{width:100%;max-width:640px;flex:1 1 auto;min-height:90px;display:grid;place-items:center;position:relative}
.gm-card .im::before{content:"";position:absolute;inset:12%;border-radius:50%;background:radial-gradient(circle,var(--rc,#e8402a) 0%,transparent 65%);opacity:.35;filter:blur(18px)}
.gm-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 18px 24px rgba(0,0,0,.6));transition:transform .3s}
.gm-card:hover img{transform:scale(1.04) rotate(-2deg)}
.gm-card .wp{font:600 .8rem/1 var(--hud);letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.6);margin-top:6px}
.gm-card .nm{font:700 clamp(1.4rem,2.6vw,2.1rem)/1.05 var(--hud);text-transform:uppercase;margin:6px 0 8px;color:#fff}
.gm-card .wr{display:inline-block;padding:4px 10px;border-radius:999px;background:rgba(255,255,255,.1);font:600 .72rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:#ddd}
.gm-card .was{margin-top:16px;font:500 .8rem/1 var(--hud);letter-spacing:.2em;text-transform:uppercase;color:rgba(255,255,255,.55)}
.gm-card .pr{font:700 clamp(2.2rem,5vw,4.4rem)/1 var(--hud);color:#ffd36a;text-shadow:0 0 24px rgba(255,200,80,.35);margin-top:6px;font-variant-numeric:tabular-nums;min-height:1em}
.gm-card .pr.q{color:rgba(255,255,255,.25);text-shadow:none}
.gm-card .bt{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%;max-width:520px;margin-top:16px}
.gm-card .bt button{height:58px;border:0;border-radius:12px;font:700 1.15rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;transition:transform .12s,filter .12s;box-shadow:0 8px 0 rgba(0,0,0,.35)}
.gm-card .bt .h{background:linear-gradient(180deg,#33e07f,#16a957)}.gm-card .bt .l{background:linear-gradient(180deg,#ff5868,#d01f31)}
.gm-card .bt button:hover{filter:brightness(1.1);transform:translateY(-2px)}.gm-card .bt button:active{transform:translateY(3px);box-shadow:0 3px 0 rgba(0,0,0,.35)}
.gm-card .bt button:disabled{opacity:.45;pointer-events:none}
.gm-card .bt kbd{font:600 .72rem/1 var(--hud);padding:3px 6px;border-radius:5px;background:rgba(0,0,0,.25);opacity:.8}
.gm-card .by{margin-top:14px;font:600 .72rem/1 var(--hud);letter-spacing:.08em;color:#ff8ccc;text-decoration:none;opacity:.85}
.gm-card.b:not(.shown) .by{visibility:hidden}
.gm-card.ok{background:linear-gradient(200deg,rgba(43,214,115,.35),rgba(8,30,18,.95) 60%)}
.gm-card.bad{background:linear-gradient(200deg,rgba(255,59,74,.38),rgba(34,8,10,.95) 60%)}
.gm-vs{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:3;width:84px;height:84px;border-radius:50%;display:grid;place-items:center;background:#0b0d14;border:3px solid rgba(255,255,255,.9);font:700 1.5rem/1 var(--hud);color:#fff;box-shadow:0 0 0 8px rgba(0,0,0,.35),0 0 40px rgba(255,255,255,.25);animation:gmPulse 2s ease-in-out infinite;transition:background .2s,border-color .2s}
.gm-vs.ok{background:var(--ok);border-color:#fff;animation:none}.gm-vs.bad{background:var(--bad);border-color:#fff;animation:none}
.gm-plus{position:absolute;left:50%;top:38%;transform:translateX(-50%);font:700 2.4rem/1 var(--hud);color:var(--ok);text-shadow:0 0 20px rgba(43,214,115,.7);pointer-events:none;z-index:4;animation:gmUp .8s ease forwards}
.gm-toast{position:absolute;left:50%;top:14px;transform:translateX(-50%);z-index:5;padding:10px 18px;border-radius:999px;background:linear-gradient(90deg,#ffcf4a,#ff8a1f);color:#1a1205;font:700 .9rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;box-shadow:0 10px 30px rgba(255,160,40,.45);animation:gmToast 2.2s ease forwards;white-space:nowrap}
.gm-arena.shake{animation:gmShake .45s ease}
.gm-arena.slide .gm-card.a,.gm-arena.slide .gm-card.b{animation:gmIn .4s ease}
.gm-start,.gm-over{position:absolute;inset:0;z-index:6;display:none;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;background:rgba(5,6,10,.82);backdrop-filter:blur(8px)}
.gm-start.on,.gm-over.on{display:flex}
.gm-start>*,.gm-over>*{flex-shrink:0}.gm-start,.gm-over{overflow:auto;justify-content:safe center}
@media(max-height:780px){.gm-start .gm-ladder{display:none}.gm-start p{margin-bottom:26px}}
.gm-start .tg{font:600 .78rem/1 var(--hud);letter-spacing:.3em;text-transform:uppercase;color:#ff8a1f;margin-bottom:18px}
.gm-start h1{margin:0;font:700 clamp(2.6rem,7vw,5rem)/1.05 var(--hud);text-transform:uppercase;background:linear-gradient(90deg,#6aa6ff,#fff 45%,#ffb15c);-webkit-background-clip:text;background-clip:text;color:transparent}
.gm-start .su{font:600 1rem/1.2 var(--hud);letter-spacing:.2em;text-transform:uppercase;color:#c9c4b8;margin:14px 0 22px}
.gm-start p{max-width:540px;color:#b9b4a7;margin:0 0 34px;font-size:1.05rem;line-height:1.6}
.gm-go{height:64px;padding:0 54px;border:0;border-radius:14px;background:linear-gradient(180deg,#ff6a3d,#e8402a);color:#fff;font:700 1.35rem/1 var(--hud);letter-spacing:.16em;text-transform:uppercase;cursor:pointer;box-shadow:0 10px 0 #8f1f12,0 20px 50px rgba(232,64,42,.45);transition:transform .12s}
.gm-go:hover{transform:translateY(-2px)}.gm-go:active{transform:translateY(5px);box-shadow:0 5px 0 #8f1f12}
.gm-ladder{display:flex;gap:10px 8px;flex-wrap:wrap;justify-content:center;margin-top:34px;max-width:680px}
.gm-ladder span{padding:7px 12px;border-radius:999px;border:1px solid currentColor;font:600 .66rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;opacity:.85}
.gm-start .bst{margin-top:24px;color:#ffcf4a;font:600 .9rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase}
.gm-over h2::before,.gm-over h2::after{display:none!important}.gm-over .st{border:0!important;padding:0!important;background:none!important}
.gm-over h2{margin:0;font:700 clamp(2.6rem,7vw,4.4rem)/1 var(--hud);text-transform:uppercase;color:var(--bad);text-shadow:0 0 30px rgba(255,59,74,.5)}
.gm-over .st{font:700 1.6rem/1 var(--hud);margin:12px 0 4px;color:#fff}
.gm-over .rk{font:600 1rem/1.2 var(--hud);letter-spacing:.1em;text-transform:uppercase;margin:4px 0}
.gm-over .nb{color:#ffcf4a;font:700 1.1rem/1 var(--hud);margin:8px 0;min-height:1.1rem}
.gm-over .ans{color:#b9b4a7;margin:6px 0 18px;max-width:560px}
.gm-over .acts{display:flex;gap:12px;flex-wrap:wrap;justify-content:center}
.gm-over .sh{height:64px;padding:0 26px;border-radius:14px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.06);color:#fff;font:700 1rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;cursor:pointer}
.gm-gate h2{color:#fff!important;text-shadow:none!important;font-size:clamp(1.8rem,4.5vw,3rem)!important}.gm-gate .gi{font-size:2.6rem;margin-bottom:10px}
.gm-stm{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;background:linear-gradient(180deg,#2a8fd8,#1a5fa8)!important;box-shadow:0 10px 0 #0f3a66,0 20px 50px rgba(42,143,216,.4)!important}
.gm-ld{position:absolute;inset:0;display:grid;place-items:center;color:#b9b4a7;z-index:7;background:#07080c}
.gm-keys{text-align:center;color:#6f6a60;font-size:.8rem;margin-top:8px}
.gm-info{max-width:900px;margin:0 auto;padding:40px 20px 60px}
.gm-info h2{font:600 1.25rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;margin:30px 0 12px}
.gm-info ol{padding-left:20px;color:var(--soft)}.gm-info h3{font-size:1.02rem;margin:16px 0 4px}.gm-info p{color:var(--soft);margin:0}
@keyframes gmPulse{0%,100%{box-shadow:0 0 0 8px rgba(0,0,0,.35),0 0 30px rgba(255,255,255,.2)}50%{box-shadow:0 0 0 8px rgba(0,0,0,.35),0 0 55px rgba(255,255,255,.45)}}
@keyframes gmBump{0%{transform:scale(1)}40%{transform:scale(1.45)}100%{transform:scale(1)}}
@keyframes gmUp{from{opacity:1;transform:translate(-50%,0)}to{opacity:0;transform:translate(-50%,-60px)}}
@keyframes gmToast{0%{opacity:0;transform:translate(-50%,-14px)}12%,80%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;transform:translate(-50%,-10px)}}
@keyframes gmShake{0%,100%{transform:none}20%{transform:translateX(-12px)}40%{transform:translateX(10px)}60%{transform:translateX(-6px)}80%{transform:translateX(4px)}}
@keyframes gmIn{from{opacity:.2;transform:translateX(30px)}to{opacity:1;transform:none}}
@media(max-width:980px){.gm-hud{grid-template-columns:1fr auto;grid-template-areas:"s r" "l l";clip-path:none}.gm-hud .l{grid-area:l;justify-content:center;padding:8px;border-top:1px solid rgba(255,255,255,.06)}.gm-score{grid-area:s;justify-self:start;clip-path:polygon(0 0,100% 0,calc(100% - 18px) 100%,0 100%);padding:6px 34px 6px 18px}.gm-hud .r{grid-area:r}.gm-xp{width:120px}.gm-rank b{max-width:140px;font-size:.8rem}}
@media(max-width:640px){.gm-stage{padding:10px 8px 18px;min-height:0;height:auto}.gm-arena{flex:none}.gm-card .im{max-height:none}.gm-arena{grid-template-columns:1fr;border-radius:14px}.gm-card{min-height:0;padding:14px 12px 16px;flex-direction:row;flex-wrap:wrap;text-align:left;align-items:center;gap:0 12px}
 .gm-card .im{width:42%;max-width:none;flex:none;aspect-ratio:4/3;min-height:0}.gm-card .tx{flex:1;min-width:0}.gm-card .nm{font-size:1.15rem}.gm-card .was{margin-top:8px;font-size:.66rem}.gm-card .pr{font-size:1.9rem}
 .gm-card .bt{max-width:none;grid-template-columns:1fr 1fr;margin-top:12px;flex-basis:100%}.gm-card .bt button{height:56px;font-size:1rem}.gm-card .bt kbd{display:none}.gm-card .by{flex-basis:100%;text-align:center;margin-top:10px}
 .gm-vs{width:50px;height:50px;font-size:.95rem;top:var(--vsy,50%);left:21%}.gm-ladder{display:none}.gm-score #gs{font-size:2.1rem}.gm-score{gap:10px;padding:6px 26px 6px 12px}.gm-score .bs{padding-left:10px}.gm-rank .em{width:34px;height:40px}.gm-rank .tx small,.gm-rank #grx{display:none}.gm-xp{width:72px}.gm-rank b{max-width:96px;font-size:.7rem}.gm-hud .r{gap:6px;padding:0 8px}.gm-snd{width:32px;height:32px}.gm-hud .l button{padding:0 10px;font-size:.66rem}#gfs{display:none}.gm-score .bs small{font-size:.5rem;letter-spacing:.18em;white-space:nowrap}.gm-xp{width:64px}.gm-keys{display:none}}
@media(max-width:640px){
 .gm-stage{height:calc(100vh - 56px);height:calc(100svh - 56px);min-height:540px;padding:8px 8px 10px}
 .gm-hud{min-height:0;margin-bottom:8px}.gm-score{padding:6px 26px 6px 12px}.gm-score #gs{font-size:1.9rem}
 .gm-arena{flex:1;min-height:0;grid-template-columns:1fr;grid-template-rows:1fr 1fr}
 .gm-card{flex-direction:column;flex-wrap:nowrap;align-items:center;justify-content:center;text-align:center;padding:10px 12px 12px;gap:0;min-height:0}
 .gm-card .im{width:100%;max-width:none;flex:1 1 auto;min-height:56px;aspect-ratio:auto}
 .gm-card .tx{flex:none;width:100%}
 .gm-card .wp{font-size:.62rem;margin-top:2px;letter-spacing:.18em}.gm-card .nm{font-size:1.15rem;margin:2px 0 4px}.gm-card .wr{font-size:.6rem;padding:3px 8px}
 .gm-card .was{display:none}.gm-card .pr{font-size:1.9rem;margin-top:6px}
 .gm-card .bt{flex:none;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;max-width:none}.gm-card .bt button{height:50px;font-size:.95rem}
 .gm-card .by{position:absolute;top:8px;right:10px;margin:0;font-size:.58rem;z-index:2}.gm-card.b:not(.shown) .by{display:none}
 .gm-vs{left:50%;top:var(--vsy,50%);width:46px;height:46px;font-size:.85rem;border-width:2px}
 .gm-start h1{font-size:2.6rem}.gm-start .su{font-size:.8rem;margin:10px 0 16px}.gm-start p{font-size:.95rem;margin-bottom:24px}.gm-go{height:58px;padding:0 40px;font-size:1.15rem}
 .gm-over h2{font-size:2.6rem}.gm-over .ans{font-size:.85rem}.gm-over .sh,.gm-over .gm-go{height:54px}
}
@media (prefers-reduced-motion:reduce){.gm *{animation:none!important;transition:none!important}}
"""

JS = r"""<script>(()=>{
const L=__L__,RK=__RK__,RC=__RCOL__,CUR=__CUR__,RATE=__RATE__,UTM="__UTM__",IMG="https://community.akamai.steamstatic.com/economy/image/",WN=__WN__,RAR=["#b0c3d9","#5e98d9","#4b69ff","#8847ff","#d32ce6","#eb4b4b","#e4ae39","#e4ae39"];
const $=s=>document.querySelector(s),ar=$("#gma");let D=[],pool=[],A=null,B=null,streak=0,best=0,busy=false,mode="all",snd=true,ac=null;
try{best=+localStorage.getItem("gm_best")||0;snd=localStorage.getItem("gm_snd")!=="0"}catch(e){}
const FREE=2,logged=()=>{try{const m=location.hash.match(/steam=([^&]+)/);if(m&&!/^(cancel|error)$/.test(m[1]))return true;return !!localStorage.getItem("skinset_steam")}catch(e){return false}};
const lost=v=>{try{if(v!==undefined)localStorage.setItem("gm_lost",v);return +localStorage.getItem("gm_lost")||0}catch(e){return 0}};
const gated=()=>!logged()&&lost()>=FREE;
function gate(){$("#gstm").href="https://auth.skin-set.com/login?r="+encodeURIComponent(location.origin+location.pathname);$("#gso").classList.remove("on");$("#gst").classList.remove("on");$("#ggate").classList.add("on")}
const fmt=v=>{v=v*RATE;const n=v>=100?Math.round(v):Math.round(v*100)/100;return CUR[0]+n.toLocaleString(RATE===1?"en-US":"ru-RU")+CUR[1]};
const rIdx=n=>{let i=0;RK.forEach((r,k)=>{if(n>=r[0])i=k});return i};
const csm=x=>"https://cs.money/market/buy/?search="+encodeURIComponent(x[0].replace(/\s*\((Phase \d|Ruby|Sapphire|Emerald|Black Pearl)\)$/,"")+" ("+WN[x[1]]+")")+"&"+UTM;
function beep(f,d,t){if(!snd)return;try{ac=ac||new (window.AudioContext||window.webkitAudioContext)();const o=ac.createOscillator(),g=ac.createGain();o.type=t||"sine";o.frequency.value=f;g.gain.setValueAtTime(.0001,ac.currentTime);g.gain.exponentialRampToValueAtTime(.12,ac.currentTime+.01);g.gain.exponentialRampToValueAtTime(.0001,ac.currentTime+d);o.connect(g).connect(ac.destination);o.start();o.stop(ac.currentTime+d)}catch(e){}}
const sOk=()=>{beep(660,.12);setTimeout(()=>beep(990,.16),90)},sBad=()=>{beep(180,.35,"sawtooth")},sUp=()=>[523,659,784,1047].forEach((f,i)=>setTimeout(()=>beep(f,.15,"triangle"),i*90));
function setPool(){pool=mode==="all"?D:D.filter(x=>mode==="guns"?!["knife","gloves"].includes(x[4]):x[4]===mode)}
function pick(ref){const minR=Math.max(1.1,3-streak*0.16),maxR=Math.max(2,25-streak*1.4);
  for(let t=0;t<500;t++){const c=pool[Math.random()*pool.length|0];if(!ref)return c;if(c[0]===ref[0])continue;const r=Math.max(c[2],ref[2])/Math.min(c[2],ref[2]);if(r>=minR&&r<=maxR)return c}
  for(let t=0;t<500;t++){const c=pool[Math.random()*pool.length|0];if(c[0]!==ref[0]&&Math.abs(c[2]-ref[2])/ref[2]>0.05)return c}return pool[0]}
function card(el,x,show){el.classList.remove("ok","bad");el.classList.toggle("shown",!!show);el.style.setProperty("--rc",RAR[x[5]]||"#e8402a");
  const [w,...s]=x[0].split(" | ");el.querySelector(".im").innerHTML=`<img src="${IMG+x[3]}/360fx270f" alt="${x[0]}" width="360" height="270">`;
  el.querySelector(".wp").textContent=w.replace("★ ","");el.querySelector(".nm").textContent=s.join(" | ")||x[0];el.querySelector(".wr").textContent=WN[x[1]];
  const p=el.querySelector(".pr");p.textContent=show?fmt(x[2]):"???";p.classList.toggle("q",!show);el.querySelector(".by").href=csm(x)}
function hud(bump){const c=$("#gs");c.textContent=streak;$("#gb").textContent=best;if(bump){c.classList.remove("bump");void c.offsetWidth;c.classList.add("bump")}
  const i=rIdx(streak),nx=RK[i+1],rk=$("#grk");document.documentElement.style.setProperty("--rk",RC[i]);$("#grn").textContent=RK[i][1];
  if(rk.dataset.i!==String(i)){if(rk.dataset.i){rk.classList.remove("up");void rk.offsetWidth;rk.classList.add("up")}rk.dataset.i=i;
    const n=i%3+1,y0=i<3?20:i<6?16:12;$("#grc").innerHTML=Array.from({length:n},(_,k)=>`<path class="cv" d="M11 ${y0+k*8}l12 6 12-6v4l-12 6-12-6z"/>`).join("")+(i>=6?`<path class="cv" d="M23 8l2.4 4.8 5.3.8-3.8 3.7.9 5.3-4.8-2.5-4.8 2.5.9-5.3-3.8-3.7 5.3-.8z"/>`:"")}
  const seg=nx?nx[0]-RK[i][0]:1,done=nx?streak-RK[i][0]:1;$("#grp").innerHTML=Array.from({length:seg},(_,k)=>`<i class="${k<done?"on":""}"></i>`).join("");
  $("#grx").textContent=nx?L.next+" «"+nx[1]+"»: "+(nx[0]-streak):"MAX";$("#gsc").classList.toggle("hot",streak>=3)}
function draw(slide){card($("#ca"),A,true);card($("#cb"),B,false);$("#gmv").className="gm-vs";$("#gmv").textContent=L.vs;
  $("#cb .bt").querySelectorAll("button").forEach(b=>b.disabled=false);ar.style.setProperty("--vsy",$("#ca").offsetHeight+"px");if(slide){ar.classList.remove("slide");void ar.offsetWidth;ar.classList.add("slide")}}
function start(){if(gated()){gate();return}streak=0;setPool();A=pick();B=pick(A);$("#gso").classList.remove("on");$("#gst").classList.remove("on");hud();draw(true)}
function count(el,to,cb){const t0=performance.now(),d=650;const f=t=>{const k=Math.min(1,(t-t0)/d);el.textContent=fmt(to*(0.15+0.85*(1-Math.pow(1-k,3))));if(k<1)requestAnimationFrame(f);else{el.textContent=fmt(to);cb()}};requestAnimationFrame(f)}
function toast(t){const d=document.createElement("div");d.className="gm-toast";d.textContent=t;ar.appendChild(d);setTimeout(()=>d.remove(),2300)}
function guess(hi){if(busy||!A||$("#ggate").classList.contains("on"))return;busy=true;$("#cb .bt").querySelectorAll("button").forEach(b=>b.disabled=true);
  const p=$("#cb .pr");p.classList.remove("q");$("#cb").classList.add("shown");beep(440,.05,"square");
  count(p,B[2],()=>{const ok=hi?B[2]>=A[2]:B[2]<=A[2];$("#cb").classList.add(ok?"ok":"bad");const v=$("#gmv");v.className="gm-vs "+(ok?"ok":"bad");v.textContent=ok?"✓":"✕";
    if(ok){sOk();const pl=document.createElement("div");pl.className="gm-plus";pl.textContent="+1";ar.appendChild(pl);setTimeout(()=>pl.remove(),850);
      const r0=rIdx(streak);streak++;if(streak>best){best=streak;try{localStorage.setItem("gm_best",best)}catch(e){}}hud(true);
      if(rIdx(streak)>r0){setTimeout(sUp,200);toast(L.rankup+": "+RK[rIdx(streak)][1])}else if(streak%5===0)toast("🔥 x"+streak);
      setTimeout(()=>{busy=false;A=B;B=pick(A);draw(true)},800)}
    else{sBad();ar.classList.remove("shake");void ar.offsetWidth;ar.classList.add("shake");
      setTimeout(()=>{busy=false;if(!logged())lost(lost()+1);const nb=streak>0&&streak>=best;const i=rIdx(streak);$("#gor").textContent=L.res.replace("{n}",streak);
        const rk=$("#gok");rk.textContent=RK[i][1];rk.style.color=RC[i];$("#gob").textContent=nb?L.newbest:"";
        $("#goa").textContent=B[0]+" ("+WN[B[1]]+") — "+fmt(B[2])+" · "+A[0]+" ("+WN[A[1]]+") — "+fmt(A[2]);$("#gso").classList.add("on");$("#gagain").focus()},900)}})}
document.querySelector(".gm").addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;
  if(b.dataset.g)guess(b.dataset.g==="h");else if(b.id==="gagain"||b.id==="ggo")start();
  else if(b.dataset.m){mode=b.dataset.m;document.querySelectorAll("[data-m]").forEach(x=>x.classList.toggle("on",x===b));if(D.length)start()}
  else if(b.id==="gfs"){const st=document.querySelector(".gm-stage");if(document.fullscreenElement)document.exitFullscreen();else if(st.requestFullscreen)st.requestFullscreen().catch(()=>{});else if(st.webkitRequestFullscreen)st.webkitRequestFullscreen()}
  else if(b.id==="gsnd"){snd=!snd;b.textContent=snd?"🔊":"🔇";try{localStorage.setItem("gm_snd",snd?"1":"0")}catch(e){}}
  else if(b.id==="gshare"){const txt=L.sharetxt.replace("{n}",streak).replace("{r}",RK[rIdx(streak)][1])+location.href;if(navigator.share){navigator.share({text:txt}).catch(()=>{})}else if(navigator.clipboard){navigator.clipboard.writeText(txt).then(()=>{b.textContent=L.copied})}}});
document.addEventListener("keydown",e=>{if(e.target.closest&&e.target.closest("input,textarea"))return;
  if($("#ggate").classList.contains("on"))return;if($("#gso").classList.contains("on")||$("#gst").classList.contains("on")){if(e.key==="Enter"||e.key===" "){e.preventDefault();start()}return}
  if(e.key==="ArrowUp"){e.preventDefault();guess(true)}else if(e.key==="ArrowDown"){e.preventDefault();guess(false)}});
$("#gsnd").textContent=snd?"🔊":"🔇";$("#gb").textContent=best;$("#gstb").textContent=best?L.best+": "+best:"";
fetch("/data/game.json").then(r=>r.json()).then(j=>{D=j.d.map(x=>(x[3]=j.i[x[3]],x));setPool();A=pick();B=pick(A);hud();draw();$("#gld").remove()}).catch(()=>{$("#gld").textContent="—"});
})()</script>"""


def data():
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json")))
    try:
        P = json.load(open(os.path.join(ROOT, "data/prices.json")))
    except Exception:
        P = {}
    out = []; imgs = []; ii = {}
    rnd = random.Random(7)
    for x in cat:
        if not x.get("i"): continue
        n = x["n"]
        live = (P.get(n) or {}).get("w") or {}
        wp = [(k, live.get(w) or x["p"][k]) for k, w in enumerate(["FN", "MW", "FT", "WW", "BS"])]
        wp = [(k, v) for k, v in wp if v and v >= MINP]
        if not wp: continue
        for k, v in rnd.sample(wp, min(2, len(wp))):  # до 2 качеств на скин
            if x["i"] not in ii: ii[x["i"]] = len(imgs); imgs.append(x["i"])
            out.append([n, k, round(v, 2), ii[x["i"]], x["c"], x.get("r", 0)])
    json.dump({"i": imgs, "d": out}, open(os.path.join(ROOT, "data/game.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return len(out)


def side(t, k):
    b = k == "b"
    return (f'<div class="gm-card {k}" id="c{k}"><div class="im"></div><div class="tx"><div class="wp"></div><div class="nm"></div><span class="wr"></span>'
            f'<div class="was">{e(t["was"])}</div><div class="pr"></div></div>'
            + (f'<div class="bt"><button class="h" data-g="h">▲ {e(t["hi"])}</button><button class="l" data-g="l">▼ {e(t["lo"])}</button></div>' if b else "")
            + f'<a class="by" target="_blank" rel="noopener sponsored">{e(t["buy"])} →</a><span class="rar"></span></div>')


def build():
    n = data()
    for lang, url in URL.items():
        t = T[lang]; rk = RANKS[lang]
        L = {k: t[k] for k in ("res", "newbest", "copied", "sharetxt", "rankup", "vs", "next", "best")}
        js = (JS.replace("__L__", json.dumps(L, ensure_ascii=False)).replace("__RK__", json.dumps(rk, ensure_ascii=False)).replace("__RCOL__", json.dumps(RCOL))
              .replace("__CUR__", json.dumps(t["cur"], ensure_ascii=False)).replace("__RATE__", str(t["rate"])).replace("__UTM__", csmoney.UTM).replace("__WN__", json.dumps(WEARS)))
        ladder = "".join(f'<span style="color:{RCOL[i]}">{e(r[1])} · {r[0]}</span>' for i, r in enumerate(rk))
        game = (f'<section class="gm-stage"><div class="gm-in">'
                '<div class="gm-hud"><div class="l">' + "".join(f'<button data-m="{k}"{" class=on" if k == "all" else ""}>{e(l)}</button>' for k, l in t["cats"]) + '</div>'
                f'<div class="gm-score" id="gsc"><span class="fl">🔥</span><div class="cur"><small>{e(t["streak"])}</small><b id="gs">0</b></div><div class="bs"><small>🏆 {e(t["best"])}</small><b id="gb">0</b></div></div>'
                f'<div class="r"><div class="gm-rank" id="grk" title="{e(t["rank"])}"><svg class="em" viewBox="0 0 46 52" aria-hidden="true"><path class="sh" d="M23 2 43 10v18c0 11-8 18-20 22C11 46 3 39 3 28V10z"/><g id="grc"></g></svg>'
                f'<div class="tx"><small>{e(t["rank"])}</small><b id="grn">{e(rk[0][1])}</b><div class="gm-xp" id="grp"></div><span id="grx"></span></div></div>'
                f'<button class="gm-snd" id="gsnd" aria-label="{e(t["sound"])}">🔊</button><button class="gm-snd" id="gfs" aria-label="{e(t["fs"])}" title="{e(t["fs"])}">⛶</button></div></div>'
                f'<div class="gm-arena" id="gma">{side(t, "a")}{side(t, "b")}<div class="gm-vs" id="gmv">{e(t["vs"])}</div>'
                f'<div class="gm-start on" id="gst"><div class="tg">{e(t["tag"])}</div><h1>{e(t["h1"])}</h1><div class="su">{e(t["sub"])}</div><p>{e(t["intro"])}</p>'
                f'<button class="gm-go" id="ggo">▶ {e(t["play"])}</button><div class="bst" id="gstb"></div><div class="gm-ladder">{ladder}</div></div>'
                f'<div class="gm-over" id="gso"><h2>{e(t["over"])}</h2><div class="st" id="gor"></div><div class="rk" id="gok"></div><div class="nb" id="gob"></div><div class="ans" id="goa"></div>'
                f'<div class="acts"><button class="gm-go" id="gagain">↻ {e(t["again"])}</button><button class="sh" id="gshare">{e(t["share"])}</button></div></div>'
                f'<div class="gm-over gm-gate" id="ggate"><div class="gi">🔒</div><h2>{e(t["gate_h"])}</h2><p class="ans">{e(t["gate_p"])}</p><div class="acts"><a class="gm-go gm-stm" id="gstm" href="https://auth.skin-set.com/login">{e(t["gate_b"])}</a></div></div>'
                f'<div class="gm-ld" id="gld">{e(t["loading"])}</div></div>'
                f'<div class="gm-keys">{e(t["keys"])}</div></div></section>')
        info = (f'<section class="gm-info"><h2>{e(t["how_h"])}</h2><ol>' + "".join(f"<li>{e(x)}</li>" for x in t["how"]) + "</ol>"
                + f'<h2>{e(t["ladder"])}</h2><p>' + " → ".join(f"{e(r[1])} ({r[0]})" for r in rk) + "</p>"
                + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in t["faq"])
                + f'<h2>{e(t["more"])}</h2><p>{e(t["more_p"])} <a href="{HOME[lang]}">{e(t["more"])} →</a></p></section>')
        alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{URL[l]}">' for l in URL) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{URL["en"]}">'
        ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": t["h1"], "url": SITE + url, "description": t["desc"]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}]
        h = head(lang, t["title"], t["desc"], SITE + url, alts, ld).replace("</head>", f"<style>{CSS}</style></head>")
        p = h + f'\n<body>\n{header(lang, {l: URL.get(l, URL["en"]) for l in HOME})}\n<main class="gm">\n{game}{info}{js}\n</main>\n<footer><p>{e(FOOT[lang])}</p></footer>\n</body>\n</html>\n'
        p = p.replace(f'<a href="{WIKI[lang]}" class=on>', f'<a href="{WIKI[lang]}">', 1)
        p = navmore.fix(p.replace("</body>", LANG_JS + "</body>", 1))
        d = os.path.join(ROOT, url.strip("/")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(p)
    sp = os.path.join(ROOT, "sitemap.xml"); s = open(sp, encoding="utf-8").read()
    for url in URL.values():
        if f"<loc>{SITE}{url}</loc>" not in s:
            s = s.replace("</urlset>", f"  <url><loc>{SITE}{url}</loc></url>\n</urlset>")
    open(sp, "w", encoding="utf-8").write(s)
    print(n, "game items")


if __name__ == "__main__":
    build()
