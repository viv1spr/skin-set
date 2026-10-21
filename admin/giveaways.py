# -*- coding: utf-8 -*-
"""Страница «Розыгрыши» на 6 языках. Данные розыгрышей живут в воркере (/gw), здесь — только оболочка.
python3 admin/giveaways.py
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "admin"))
e = lambda s: html.escape(str(s), quote=True)

PATH = {"ru": "/rozygryshi/", "en": "/en/giveaways/", "de": "/de/gewinnspiele/", "pt": "/pt/sorteios/", "tr": "/tr/cekilisler/", "pl": "/pl/konkursy/"}
SKP = {"ru": "/skiny/", "en": "/en/skins/", "de": "/de/skins/", "pt": "/pt/skins/", "tr": "/tr/skinler/", "pl": "/pl/skiny/"}
TAB = {"ru": "Розыгрыши", "en": "Giveaways", "de": "Gewinnspiele", "pt": "Sorteios", "tr": "Çekilişler", "pl": "Konkursy"}
W = "https://auth.skin-set.com"
TW = "https://www.twitch.tv/viv1stop"

T = {
 "ru": dict(hl="скины", title="Розыгрыш скинов CS2 от viv1stop — Skinset", desc="Бесплатный розыгрыш скинов CS2: войди через Steam, оставь трейд-ссылку и участвуй.",
   kick="Розыгрыш", h1="Разыгрываем скины CS2", lead="Бесплатно: войди через Steam, оставь трейд-ссылку — и ты в игре. Победителей выбираем в прямом эфире на Twitch.",
   prizes="Призы", prize="Приз", left="До конца", d="д", h="ч", m="мин", s="с", part="Участников", ended="Розыгрыш завершён", soon="Скоро старт",
   login="Войти через Steam и участвовать", trade="Твоя трейд-ссылка Steam", tradeHelp="Где взять трейд-ссылку?", code="Кодовое слово со стрима", codeHint="+1 шанс к победе. Слово называю на стримах.",
   go="Участвовать", inn="Ты участвуешь", chances="шансов", addCode="Добавить кодовое слово", saved="Готово! Удачи", winners="Победители", winFor="Приз",
   err=dict(trade="Это не похоже на трейд-ссылку. Скопируй её целиком со страницы Steam.", tradeOwner="Трейд-ссылка от другого аккаунта Steam. Нужна ссылка того аккаунта, с которого ты вошёл.",
            code="Неверное кодовое слово — проверь, что написал как на стриме.", ended="Розыгрыш уже закончился.", auth="Сессия Steam устарела — войди ещё раз.", net="Не получилось связаться с сервером. Попробуй ещё раз."),
   rules_h="Правила", rules=["Участвовать можно один раз с одного аккаунта Steam.", "Трейд-ссылка должна быть от того же аккаунта, с которого ты вошёл.", "Победителей выбираем случайно в прямом эфире после окончания таймера. Один человек — один приз.", "Приз отправляем трейдом в течение 24 часов (если у скина временный запрет на обмен — сразу после его окончания).", "Участие бесплатное. Никаких депозитов и пополнений."],
   tw="Смотреть стрим", twp="Победителей выбираем в прямом эфире на стримах viv1stop.", st="StatTrak™", crumbs="Главная"),
 "en": dict(hl="giveaway", title="CS2 skin giveaway by viv1stop — Skinset", desc="Free CS2 skin giveaway: sign in with Steam, add your trade link and you're in.",
   kick="Giveaway", h1="CS2 skin giveaway", lead="Free: sign in with Steam, add your trade link and you're in. Winners are drawn live on Twitch.",
   prizes="Prizes", prize="Prize", left="Ends in", d="d", h="h", m="min", s="s", part="Participants", ended="Giveaway ended", soon="Starts soon",
   login="Sign in with Steam to enter", trade="Your Steam trade link", tradeHelp="Where do I find my trade link?", code="Code word from the stream", codeHint="+1 chance to win. I say the word on stream.",
   go="Enter", inn="You're in", chances="chances", addCode="Add code word", saved="Done! Good luck", winners="Winners", winFor="Prize",
   err=dict(trade="That doesn't look like a trade link. Copy the whole link from Steam.", tradeOwner="This trade link belongs to another Steam account. Use the link of the account you signed in with.",
            code="Wrong code word — check it matches the stream.", ended="This giveaway has ended.", auth="Steam session expired — please sign in again.", net="Couldn't reach the server. Try again."),
   rules_h="Rules", rules=["One entry per Steam account.", "The trade link must belong to the account you signed in with.", "Winners are drawn at random live on stream after the timer ends. One person — one prize.", "Prizes are sent via trade within 24 hours (if a skin is trade-locked, right after the lock ends).", "Entry is free. No deposits, no top-ups."],
   tw="Watch the stream", twp="Winners are drawn live on viv1stop's streams.", st="StatTrak™", crumbs="Home"),
 "de": dict(hl="zu gewinnen", title="CS2-Skin-Gewinnspiel von viv1stop — Skinset", desc="Kostenloses CS2-Skin-Gewinnspiel: mit Steam anmelden, Trade-Link eintragen und dabei sein.",
   kick="Gewinnspiel", h1="CS2-Skins zu gewinnen", lead="Kostenlos: mit Steam anmelden, Trade-Link eintragen — fertig. Die Gewinner werden live auf Twitch gezogen.",
   prizes="Preise", prize="Preis", left="Endet in", d="T", h="Std", m="Min", s="s", part="Teilnehmer", ended="Gewinnspiel beendet", soon="Startet bald",
   login="Mit Steam anmelden und mitmachen", trade="Dein Steam-Trade-Link", tradeHelp="Wo finde ich meinen Trade-Link?", code="Codewort aus dem Stream", codeHint="+1 Gewinnchance. Das Wort nenne ich im Stream.",
   go="Mitmachen", inn="Du bist dabei", chances="Chancen", addCode="Codewort hinzufügen", saved="Fertig! Viel Glück", winners="Gewinner", winFor="Preis",
   err=dict(trade="Das sieht nicht wie ein Trade-Link aus. Kopiere den ganzen Link aus Steam.", tradeOwner="Der Trade-Link gehört zu einem anderen Steam-Konto.",
            code="Falsches Codewort.", ended="Das Gewinnspiel ist beendet.", auth="Steam-Sitzung abgelaufen — bitte erneut anmelden.", net="Server nicht erreichbar. Versuch es nochmal."),
   rules_h="Regeln", rules=["Eine Teilnahme pro Steam-Konto.", "Der Trade-Link muss zum angemeldeten Konto gehören.", "Die Gewinner werden nach Ablauf live im Stream zufällig gezogen. Eine Person — ein Preis.", "Preise werden innerhalb von 24 Stunden per Trade verschickt (bei Handelssperre direkt danach).", "Teilnahme kostenlos. Keine Einzahlungen."],
   tw="Zum Stream", twp="Die Gewinner werden live in den Streams von viv1stop gezogen.", st="StatTrak™", crumbs="Start"),
 "pt": dict(hl="Sorteio", title="Sorteio de skins de CS2 do viv1stop — Skinset", desc="Sorteio grátis de skins de CS2: entre com a Steam, adicione seu link de troca e participe.",
   kick="Sorteio", h1="Sorteio de skins de CS2", lead="Grátis: entre com a Steam, adicione seu link de troca e pronto. Os vencedores são sorteados ao vivo na Twitch.",
   prizes="Prêmios", prize="Prêmio", left="Termina em", d="d", h="h", m="min", s="s", part="Participantes", ended="Sorteio encerrado", soon="Começa em breve",
   login="Entrar com a Steam e participar", trade="Seu link de troca da Steam", tradeHelp="Onde encontro meu link de troca?", code="Palavra-código da live", codeHint="+1 chance de ganhar. Digo a palavra nas lives.",
   go="Participar", inn="Você está participando", chances="chances", addCode="Adicionar palavra-código", saved="Pronto! Boa sorte", winners="Vencedores", winFor="Prêmio",
   err=dict(trade="Isso não parece um link de troca. Copie o link inteiro da Steam.", tradeOwner="Esse link de troca é de outra conta Steam.",
            code="Palavra-código errada.", ended="O sorteio já terminou.", auth="Sessão da Steam expirou — entre de novo.", net="Não foi possível contatar o servidor. Tente de novo."),
   rules_h="Regras", rules=["Uma participação por conta Steam.", "O link de troca deve ser da conta com que você entrou.", "Os vencedores são sorteados ao vivo depois do fim do timer. Uma pessoa — um prêmio.", "Os prêmios são enviados por troca em até 24 horas (se houver bloqueio de troca, logo após o fim dele).", "Participação grátis. Sem depósitos."],
   tw="Assistir à live", twp="Os vencedores são sorteados ao vivo nas lives do viv1stop.", st="StatTrak™", crumbs="Início"),
 "tr": dict(hl="çekilişi", title="viv1stop CS2 skin çekilişi — Skinset", desc="Ücretsiz CS2 skin çekilişi: Steam ile giriş yap, takas bağlantını ekle ve katıl.",
   kick="Çekiliş", h1="CS2 skin çekilişi", lead="Ücretsiz: Steam ile giriş yap, takas bağlantını ekle — hepsi bu. Kazananlar Twitch'te canlı yayında seçilir.",
   prizes="Ödüller", prize="Ödül", left="Bitişe", d="g", h="sa", m="dk", s="sn", part="Katılımcı", ended="Çekiliş bitti", soon="Yakında başlıyor",
   login="Steam ile giriş yap ve katıl", trade="Steam takas bağlantın", tradeHelp="Takas bağlantımı nereden bulurum?", code="Yayındaki anahtar kelime", codeHint="+1 kazanma şansı. Kelimeyi yayında söylüyorum.",
   go="Katıl", inn="Katıldın", chances="şans", addCode="Anahtar kelime ekle", saved="Tamam! Bol şans", winners="Kazananlar", winFor="Ödül",
   err=dict(trade="Bu bir takas bağlantısına benzemiyor. Steam'den bağlantının tamamını kopyala.", tradeOwner="Bu takas bağlantısı başka bir Steam hesabına ait.",
            code="Yanlış anahtar kelime.", ended="Çekiliş sona erdi.", auth="Steam oturumu sona erdi — tekrar giriş yap.", net="Sunucuya ulaşılamadı. Tekrar dene."),
   rules_h="Kurallar", rules=["Her Steam hesabı bir kez katılabilir.", "Takas bağlantısı giriş yaptığın hesaba ait olmalı.", "Kazananlar süre bitince canlı yayında rastgele seçilir. Kişi başı bir ödül.", "Ödüller 24 saat içinde takasla gönderilir (takas kilidi varsa kilit bitince).", "Katılım ücretsiz. Para yatırma yok."],
   tw="Yayını izle", twp="Kazananlar viv1stop yayınlarında canlı seçilir.", st="StatTrak™", crumbs="Ana sayfa"),
 "pl": dict(hl="Konkurs", title="Konkurs skinów CS2 od viv1stop — Skinset", desc="Darmowy konkurs skinów CS2: zaloguj się przez Steam, dodaj link do wymiany i bierz udział.",
   kick="Konkurs", h1="Konkurs skinów CS2", lead="Za darmo: zaloguj się przez Steam, dodaj link do wymiany — i gotowe. Zwycięzców losujemy na żywo na Twitchu.",
   prizes="Nagrody", prize="Nagroda", left="Do końca", d="d", h="godz", m="min", s="s", part="Uczestników", ended="Konkurs zakończony", soon="Wkrótce start",
   login="Zaloguj się przez Steam i weź udział", trade="Twój link do wymiany Steam", tradeHelp="Gdzie znaleźć link do wymiany?", code="Hasło ze streama", codeHint="+1 szansa na wygraną. Hasło podaję na streamach.",
   go="Biorę udział", inn="Bierzesz udział", chances="szanse", addCode="Dodaj hasło", saved="Gotowe! Powodzenia", winners="Zwycięzcy", winFor="Nagroda",
   err=dict(trade="To nie wygląda na link do wymiany. Skopiuj cały link ze Steam.", tradeOwner="Ten link do wymiany należy do innego konta Steam.",
            code="Złe hasło.", ended="Konkurs już się zakończył.", auth="Sesja Steam wygasła — zaloguj się ponownie.", net="Nie udało się połączyć z serwerem. Spróbuj ponownie."),
   rules_h="Zasady", rules=["Jedno zgłoszenie na konto Steam.", "Link do wymiany musi należeć do konta, którym się zalogowałeś.", "Zwycięzców losujemy na żywo po końcu odliczania. Jedna osoba — jedna nagroda.", "Nagrody wysyłamy wymianą w ciągu 24 godzin (przy blokadzie wymiany — zaraz po jej końcu).", "Udział darmowy. Bez wpłat."],
   tw="Oglądaj stream", twp="Zwycięzców losujemy na żywo na streamach viv1stop.", st="StatTrak™", crumbs="Start"),
}
WEAR = {"FN": "Factory New", "MW": "Minimal Wear", "FT": "Field-Tested", "WW": "Well-Worn", "BS": "Battle-Scarred"}
RCOL = {"Consumer Grade": "#b0c3d9", "Industrial Grade": "#5e98d9", "Mil-Spec Grade": "#4b69ff", "Restricted": "#8847ff", "Classified": "#d32ce6", "Covert": "#eb4b4b", "Extraordinary": "#e4ae39"}

CSS = r"""
.gw{max-width:1100px;margin:0 auto;padding:26px 24px 60px}
.gw .crumbs{font-size:.85rem;color:var(--soft);margin-bottom:14px}.gw .crumbs a{color:var(--soft)}
.gw-hero{display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:center;margin-bottom:26px}
.gw h1{margin:14px 0 10px;font:700 clamp(2rem,4.6vw,3.4rem)/1 var(--hud);text-transform:uppercase}
.gw .lead{color:var(--soft);font-size:1.05rem;margin:0}
.gw-timer{background:rgba(14,15,17,.8);border:1px solid var(--line2);border-top:3px solid var(--pick);padding:18px 20px}
.gw-timer small{display:block;font:600 .74rem/1 var(--hud);letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin-bottom:10px}
.gw-timer .cd{display:flex;gap:8px}.gw-timer .cd div{flex:1;text-align:center;background:rgba(255,255,255,.04);border:1px solid var(--line);padding:10px 4px}
.gw-timer .cd b{display:block;font:700 2rem/1 var(--hud)}.gw-timer .cd span{font-size:.75rem;color:var(--soft)}
.gw-timer .pc{margin-top:12px;color:var(--soft);font-size:.92rem}.gw-timer .pc b{color:var(--ink);font:700 1.2rem var(--hud)}
.gw h2{margin:34px 0 14px;font:700 1.5rem/1 var(--hud);text-transform:uppercase}
.gw h2::before{content:"";display:block;width:40px;height:4px;background:var(--pick);margin-bottom:12px}
.gw-prizes{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.gw-p{position:relative;background:linear-gradient(170deg,rgba(255,255,255,.07),rgba(255,255,255,.015));border:1px solid var(--line2);border-bottom:3px solid var(--rc);padding:14px 14px 16px;clip-path:polygon(12px 0,100% 0,100% calc(100% - 12px),calc(100% - 12px) 100%,0 100%,0 12px)}
.gw-p .no{position:absolute;top:10px;left:12px;font:600 .7rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.gw-p .stt{position:absolute;top:8px;right:10px;padding:3px 6px;background:#cf6a32;color:#fff;font:700 .66rem/1 var(--hud);letter-spacing:.06em}
.gw-p .im{height:150px;display:grid;place-items:center;margin:14px 0 8px;position:relative}
.gw-p .im::before{content:"";position:absolute;inset:12% 18%;background:radial-gradient(closest-side,var(--rc),transparent);opacity:.25}
.gw-p img{position:relative;max-width:100%;max-height:150px;object-fit:contain;filter:drop-shadow(0 12px 14px rgba(0,0,0,.6))}
.gw-p .w{color:var(--soft);font-size:.82rem}.gw-p .s{font:700 1.25rem/1.15 var(--hud);text-transform:uppercase;margin:2px 0 6px}
.gw-p .f{font-size:.8rem;color:var(--dim)}
.gw-p .win{display:flex;align-items:center;gap:10px;margin-top:12px;padding:8px 10px;background:rgba(228,174,57,.12);border:1px solid rgba(228,174,57,.5)}
.gw-p .win img{width:32px;height:32px;max-height:none;filter:none}.gw-p .win b{color:#ffd36a}.gw-p .win small{display:block;color:var(--soft);font-size:.72rem}
.gw-box{background:rgba(14,15,17,.85);border:1px solid var(--line2);padding:20px;margin-top:6px}
.gw-box label{display:block;font:600 .78rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;color:var(--soft);margin:14px 0 8px}
.gw-box label:first-child{margin-top:0}
.gw-box input{width:100%;height:46px;padding:0 14px;background:rgba(255,255,255,.04);border:1px solid var(--line2);color:var(--ink);font:400 .95rem var(--body);outline:none}
.gw-box input:focus{border-color:#2d73ff}
.gw-box .hint{font-size:.82rem;color:var(--dim);margin-top:6px}.gw-box .hint a{color:#66c0f4}
.gw-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;height:52px;padding:0 26px;margin-top:16px;border:0;background:linear-gradient(90deg,#06bfff,#2d73ff);color:#fff;font:700 .95rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;cursor:pointer;text-decoration:none;box-shadow:0 8px 22px rgba(45,115,255,.35);clip-path:polygon(8px 0,100% 0,100% calc(100% - 8px),calc(100% - 8px) 100%,0 100%,0 8px)}
.gw-btn:hover{filter:brightness(1.12)}.gw-btn svg{width:22px;height:22px}.gw-btn[disabled]{opacity:.6;cursor:wait}
.gw-ok{display:flex;align-items:center;gap:12px;font:600 1.1rem var(--hud);text-transform:uppercase;letter-spacing:.06em;color:#7dffb0}
.gw-ok i{width:30px;height:30px;border-radius:50%;background:#1d9b5a;display:grid;place-items:center;font-style:normal;color:#fff}
.gw-ok small{color:var(--soft);font:400 .9rem var(--body);text-transform:none;letter-spacing:0}
.gw-err{margin-top:12px;padding:10px 12px;border:1px solid rgba(235,75,75,.6);background:rgba(235,75,75,.12);color:#ffb3b3;font-size:.9rem}
.gw-msg{padding:16px;text-align:center;color:var(--soft)}
.gw-tw{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:22px;padding:16px 18px;background:linear-gradient(135deg,rgba(145,70,255,.18),rgba(14,15,17,.75) 70%);border:1px solid rgba(145,70,255,.4)}
.gw-tw p{margin:0;color:var(--soft)}.gw-tw a{flex:none;display:inline-flex;align-items:center;gap:8px;padding:10px 16px;background:#9146ff;color:#fff;font:600 .85rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;text-decoration:none}
.gw ol.rules{margin:0;padding-left:20px;color:var(--soft);display:grid;gap:8px}

/* праздничное оформление */
body{background:radial-gradient(900px 520px at 75% -8%,rgba(228,174,57,.22),transparent 62%),radial-gradient(700px 480px at -10% 30%,rgba(196,22,28,.16),transparent 60%),#0b0c0f}
.gw{position:relative}
.gw::before{content:"";position:absolute;inset:0 0 auto 0;height:420px;pointer-events:none;z-index:-1;opacity:.55;
 background-image:radial-gradient(circle,#ffd36a 1.6px,transparent 2px),radial-gradient(circle,#ff5cb0 1.4px,transparent 2px),radial-gradient(circle,#66c0f4 1.4px,transparent 2px),radial-gradient(circle,#e4ae39 1.2px,transparent 1.8px);
 background-size:140px 120px,190px 150px,230px 170px,90px 110px;background-position:10px 20px,60px 70px,120px 30px,40px 90px;animation:gwConf 18s linear infinite;-webkit-mask:linear-gradient(#000,transparent);mask:linear-gradient(#000,transparent)}
@keyframes gwConf{to{background-position:10px 140px,60px 220px,120px 200px,40px 200px}}
.gw .kick{background:linear-gradient(90deg,#e4ae39,#ffd36a);color:#1a1205}
.gw h1 em{color:#ffd36a;font-style:normal;text-shadow:0 0 30px rgba(255,200,80,.45)}
.gw-timer{border-top-color:#e4ae39;box-shadow:0 0 0 1px rgba(228,174,57,.15),0 20px 50px rgba(228,174,57,.08)}
.gw-timer .cd b{color:#ffe08a}
.gw h2::before{background:linear-gradient(90deg,#e4ae39,#ffd36a)}
.gw-p{box-shadow:0 0 0 1px rgba(228,174,57,.08)}.gw-p:hover{transform:translateY(-3px);transition:transform .2s}
@media (prefers-reduced-motion:reduce){.gw::before{animation:none}}

/* шапка по центру, таймер полосой под текстом */
.gw-hero{display:flex!important;flex-direction:column;align-items:center;text-align:center;margin:10px auto 30px;max-width:820px}
.gw-hero .lead{max-width:640px;margin:0 auto}
.gw-hero .gw-timer{display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;margin-top:22px;padding:12px 16px;background:rgba(14,15,17,.7);border:1px solid rgba(228,174,57,.45);border-top-width:1px;box-shadow:0 10px 40px rgba(228,174,57,.12)}
.gw-hero .gw-timer small{margin:0;color:#e9cf8f}
.gw-hero .gw-timer .cd{gap:6px}.gw-hero .gw-timer .cd div{min-width:64px;padding:8px 6px;background:rgba(228,174,57,.08);border-color:rgba(228,174,57,.3)}
.gw-hero .gw-timer .cd b{font-size:1.7rem}
@media(max-width:560px){.gw-hero .gw-timer{width:100%;gap:10px}.gw-hero .gw-timer .cd{width:100%}.gw-hero .gw-timer .cd div{min-width:0}}
@media(max-width:860px){.gw-hero{grid-template-columns:1fr}.gw-prizes{grid-template-columns:1fr}.gw-p .im{height:110px;margin:10px 0 4px}.gw-p img{max-height:110px}.gw{padding:18px 14px 40px}.gw-tw{flex-direction:column;align-items:flex-start}.gw-btn{width:100%}}
"""

JS = r"""(()=>{const L=window.GWL,W=__W__,IMG=__IMG__,RC=__RC__;const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const LS=(k,v)=>{try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){return null}};
try{const m=location.hash.match(/steam=([^&]+)/);if(m){const v=decodeURIComponent(m[1]);if(v!=="cancel"&&v!=="error")LS("skinset_steam",v);history.replaceState(null,"",location.pathname+location.search)}}catch(e){}
const tok=()=>LS("skinset_steam");let G=null,ME=null,MINE={},now0=0,t0=0;
const STEAM='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-9.96 9.17l5.35 2.21a2.8 2.8 0 0 1 1.6-.5h.16l2.38-3.45v-.05a3.77 3.77 0 1 1 3.77 3.77h-.09l-3.4 2.42v.13a2.83 2.83 0 0 1-5.62.47L2.4 14.7A10 10 0 1 0 12 2Zm-4.72 15.2-1.23-.51a2.13 2.13 0 1 0 1.17-2.92l1.27.53a1.57 1.57 0 1 1-1.2 2.9Zm9.5-7.3a2.51 2.51 0 1 0-2.5 2.52 2.52 2.52 0 0 0 2.5-2.52Zm-4.39 0a1.89 1.89 0 1 1 1.89 1.89 1.89 1.89 0 0 1-1.89-1.89Z"/></svg>';
const active=g=>g.status!=="ended"&&srvNow()<g.ends&&srvNow()>=(g.starts||0);const srvNow=()=>now0+(Date.now()-t0);
let CAT=null;async function ensureImgs(){if(G.items.every(it=>IMG[it.n])||CAT)return;try{CAT=await (await fetch("/data/catalog.json")).json();const RN=["Consumer Grade","Industrial Grade","Mil-Spec Grade","Restricted","Classified","Covert","Extraordinary","Contraband"];for(const x of CAT)if(!IMG[x.n])IMG[x.n]={i:x.i.startsWith("http")?x.i:"https://community.akamai.steamstatic.com/economy/image/"+x.i+"/360fx360f",r:RN[x.r]};prizes()}catch(e){}}
function prizes(){const g=G;$("#gwPrizes").innerHTML=g.items.map((it,i)=>{const im=IMG[it.n]||{};const w=(g.winners||[]).find(x=>x.i===i);const [wp,sk]=it.n.split(" | ");
 return `<div class="gw-p" style="--rc:${RC[im.r]||"#8847ff"}"><span class="no">${esc(L.prize)} #${i+1}</span>${it.st?`<span class="stt">${esc(L.st)}</span>`:""}<div class="im">${im.i?`<img src="${esc(im.i)}" alt="${esc(it.n)}">`:""}</div><div class="w">${esc(wp)}</div><div class="s">${esc(sk||"")}</div><div class="f">${esc(L.wear[it.w]||it.w||"")}${it.f!=null?" · Float "+Number(it.f).toFixed(4):""}</div>${w?`<div class="win">${w.a?`<img src="${esc(w.a)}" alt="">`:""}<div><small>${esc(L.winners)}</small><b>${esc(w.n)}</b></div></div>`:""}</div>`}).join("")}
function timer(){const g=G;if(!g)return;const el=$("#gwCd");const pc="";
 if(!active(g)){el.innerHTML=`<small>${esc(srvNow()<(g.starts||0)?L.soon:L.ended)}</small>`+pc;return}
 let s=Math.max(0,Math.floor((g.ends-srvNow())/1000));const d=Math.floor(s/86400);s%=86400;const h=Math.floor(s/3600);s%=3600;const m=Math.floor(s/60);s%=60;
 el.innerHTML=`<small>${esc(L.left)}</small><div class="cd">${[[d,L.d],[h,L.h],[m,L.m],[s,L.s]].map(([v,u])=>`<div><b>${String(v).padStart(2,"0")}</b><span>${esc(u)}</span></div>`).join("")}</div>`+pc}
function box(err){const g=G,b=$("#gwBox");const me=MINE[g.id];
 if(!active(g)){b.innerHTML=`<div class="gw-msg">${esc(L.ended)}</div>`;return}
 if(!tok()){b.innerHTML=`<a class="gw-btn" href="${W}/login?r=${encodeURIComponent(location.origin+location.pathname)}">${STEAM}${esc(L.login)}</a>`;return}
 if(me){b.innerHTML=`<div class="gw-ok"><i>✓</i><div>${esc(L.inn)}<br><small>${esc(L.saved)}</small></div></div>`+(err?`<div class="gw-err">${esc(err)}</div>`:"");bind(me);return}
 b.innerHTML=`<label for="gwTrade">${esc(L.trade)}</label><input id="gwTrade" placeholder="https://steamcommunity.com/tradeoffer/new/?partner=…&token=…" value="${esc(LS("skinset_trade")||"")}" autocomplete="off"><div class="hint"><a href="https://steamcommunity.com/my/tradeoffers/privacy#trade_offer_access_url" target="_blank" rel="noopener">${esc(L.tradeHelp)}</a></div>`
  +`<button class="gw-btn" id="gwGo">${esc(L.go)}</button>`+(err?`<div class="gw-err">${esc(err)}</div>`:"");bind(null)}
function bind(me){const go=$("#gwGo");if(!go)return;go.onclick=async()=>{const trade=me?me.trade:($("#gwTrade").value||"").trim();const code=($("#gwCode")||{}).value||"";
 go.disabled=true;try{const r=await fetch(W+"/gw/enter",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({t:tok(),id:G.id,trade,code})});const j=await r.json().catch(()=>({}));
  if(!r.ok){if(j.error==="auth")LS("skinset_steam",null);box(L.err[j.error]||L.err.net);return}
  LS("skinset_trade",trade);MINE[G.id]={tk:j.tk,code:j.code,trade};G.count=j.count;timer();box()}catch(e){box(L.err.net)}}}
function winners(){const ws=(G.winners||[]);$("#gwWinH").hidden=!ws.length}
async function load(){try{const r=await fetch(W+"/gw");const j=await r.json();now0=j.now||Date.now();t0=Date.now();
  const list=j.list||[];G=list.find(x=>x.status!=="ended"&&now0<x.ends)||list[list.length-1];if(!G){$("#gwBox").innerHTML=`<div class="gw-msg">${esc(L.ended)}</div>`;return}
  if(tok()){try{const m=await fetch(W+"/gw/me?t="+encodeURIComponent(tok()));if(m.status===401)LS("skinset_steam",null);else MINE=(await m.json()).mine||{}}catch(e){}}
  prizes();timer();box();setInterval(timer,1000);ensureImgs()}catch(e){$("#gwBox").innerHTML=`<div class="gw-err">${esc(L.err.net)}</div>`}}
load()})();"""


def build(lang):
    from skins_wiki import head, header, FOOT, HREFLANG, SITE, HOME
    import navmore
    t = T[lang]
    api = {}
    for r in json.load(open(os.path.join(ROOT, "admin/skins-api.json"))):
        api.setdefault(r[0], r)
    # картинки для известных скинов (призы задаются в воркере; добавим все скины, чтобы новые розыгрыши тоже работали)
    wanted = ["AK-47 | Nouveau Rouge", "M4A1-S | Emphorosaur-S", "Desert Eagle | Serpent Strike"]
    img = {n: {"i": api[n][1], "r": api[n][2]} for n in wanted if n in api}
    canon = SITE + PATH[lang]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{PATH[l]}">' for l in PATH) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{PATH["en"]}">'
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": t["h1"], "url": canon, "description": t["desc"]}]
    gl = dict(t, wear=WEAR); gl.pop("title"); gl.pop("desc")
    js = JS.replace("__W__", json.dumps(W)).replace("__IMG__", json.dumps(img, ensure_ascii=False)).replace("__RC__", json.dumps(RCOL))
    h = head(lang, t["title"], t["desc"], canon, alts, ld).replace("</head>", f"<style>{CSS}</style></head>")
    tw_svg = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M4 2 2 6v15h5v3h3l3-3h4l5-5V2H4zm16 13-3 3h-5l-3 3v-3H6V4h14v11zM15 7h2v5h-2V7zm-5 0h2v5h-2V7z"/></svg>'
    page = h + f"""
<body>
{header(lang, PATH)}
<main class="gw">
<nav class="crumbs"><a href="{HOME[lang]}">{e(t['crumbs'])}</a> › {e(TAB[lang])}</nav>
<div class="gw-hero"><span class="kick">{e(t['kick'])}</span><h1>{e(t["h1"]).replace(e(t["hl"]), "<em>" + e(t["hl"]) + "</em>", 1)}</h1><p class="lead">{e(t['lead'])}</p><div class="gw-timer" id="gwCd"><small>&nbsp;</small></div></div>
<h2>{e(t['prizes'])}</h2><div class="gw-prizes" id="gwPrizes"></div>
<div id="gwWinH" hidden></div>
<h2>{e(t['go'])}</h2><div class="gw-box" id="gwBox"><div class="gw-msg">…</div></div>
<div class="gw-tw"><p>{e(t['twp'])}</p><a href="{TW}" target="_blank" rel="noopener">{tw_svg}{e(t['tw'])}</a></div>
<h2>{e(t['rules_h'])}</h2><ol class="rules">{''.join(f'<li>{e(r)}</li>' for r in t['rules'])}</ol>
</main>
<footer><p>{e(FOOT[lang])}</p></footer>
<script>window.GWL={json.dumps(gl, ensure_ascii=False)};</script>
<script>{js}</script>
</body>
</html>
"""
    from about import LANG_JS
    page = page.replace("</body>", LANG_JS + "</body>", 1)
    page = page.replace(f'<a href="{SKP[lang]}" class=on>', f'<a href="{SKP[lang]}">', 1).replace(f'<a href="{PATH[lang]}">', f'<a href="{PATH[lang]}" class=on>', 1)
    return navmore.fix(page)


def add_nav():
    """вкладка «Розыгрыши» в меню после «Скины»"""
    import glob
    SK = {"ru": "/skiny/", "en": "/en/skins/", "de": "/de/skins/", "pt": "/pt/skins/", "tr": "/tr/skinler/", "pl": "/pl/skiny/"}
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
        if "/admin/" in f: continue
        s = open(f, encoding="utf-8").read()
        if "data-gw" in s or any(f'<a href="{PATH[l]}"' in s[:s.find("</header>")] for l in PATH): continue
        o = s
        for l in PATH:
            s = re.sub(r'(<nav class="tabs"[^>]*>.*?<a href="' + re.escape(SK[l]) + r'"[^>]*>[^<]*</a>)',
                       lambda m: m.group(1) + f'<a href="{PATH[l]}" data-gw>{TAB[l]}</a>', s, count=1, flags=re.S)
        if s != o: open(f, "w", encoding="utf-8").write(s); n += 1
    return n


def main():
    for lang in PATH:
        out = os.path.join(ROOT, PATH[lang].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(build(lang))
    print("pages ok; nav updated in", add_nav(), "files")


if __name__ == "__main__":
    main()
