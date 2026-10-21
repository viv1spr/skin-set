# Генератор посадочной страницы «О проекте» на 6 языках.
# Запуск: python3 admin/about.py  (из корня репозитория)
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TW = "https://www.twitch.tv/viv1stop"
TG = "https://t.me/Vivistop"

PATHS = {"ru": "/o-proekte/", "en": "/en/about/", "de": "/de/ueber-uns/", "pt": "/pt/sobre/", "tr": "/tr/hakkimizda/", "pl": "/pl/o-projekcie/"}
HOME = {"ru": "/", "en": "/en/", "de": "/de/", "pt": "/pt/", "tr": "/tr/", "pl": "/pl/"}
HREFLANG = {"ru": "ru", "en": "en", "de": "de", "pt": "pt-BR", "tr": "tr", "pl": "pl"}
NAV = {
 "ru": [("/", "Конструктор"), ("/skiny/", "Скины"), ("/rozygryshi/", "Розыгрыши"), ("/kak-rabotaet/", "Как работает"), ("/gde-kupit/", "Площадки"), ("/sety/", "Сеты"), ("/blog/", "Блог")],
 "en": [("/en/", "Builder"), ("/en/skins/", "Skins"), ("/en/giveaways/", "Giveaways"), ("/en/how-it-works/", "How it works"), ("/en/where-to-buy/", "Marketplaces"), ("/en/loadouts/", "Loadouts"), ("/en/blog/", "Blog")],
 "de": [("/de/", "Builder"), ("/de/skins/", "Skins"), ("/de/gewinnspiele/", "Gewinnspiele"), ("/de/so-funktionierts/", "So funktioniert's"), ("/de/wo-kaufen/", "Marktplätze"), ("/de/loadouts/", "Loadouts"), ("/de/blog/", "Blog")],
 "pt": [("/pt/", "Montador"), ("/pt/skins/", "Skins"), ("/pt/sorteios/", "Sorteios"), ("/pt/como-funciona/", "Como funciona"), ("/pt/onde-comprar/", "Lojas"), ("/pt/sets/", "Sets"), ("/pt/blog/", "Blog")],
 "tr": [("/tr/", "Oluşturucu"), ("/tr/skinler/", "Skinler"), ("/tr/cekilisler/", "Çekilişler"), ("/tr/nasil-calisir/", "Nasıl çalışır"), ("/tr/nereden-alinir/", "Pazar yerleri"), ("/tr/setler/", "Setler"), ("/tr/blog/", "Blog")],
 "pl": [("/pl/", "Kreator"), ("/pl/skiny/", "Skiny"), ("/pl/konkursy/", "Konkursy"), ("/pl/jak-to-dziala/", "Jak to działa"), ("/pl/gdzie-kupic/", "Rynki"), ("/pl/zestawy/", "Zestawy"), ("/pl/blog/", "Blog")],
}
CP = {
 "ru": ["krasnye-skiny-cs2","sinie-skiny-cs2","rozovye-skiny-cs2","fioletovye-skiny-cs2","zelenye-skiny-cs2","zolotye-skiny-cs2","oranzhevye-skiny-cs2","biryuzovye-skiny-cs2","cherno-belye-skiny-cs2"],
 "en": ["red-black-cs2-skins","blue-cs2-skins","pink-cs2-skins","purple-cs2-skins","green-cs2-skins","gold-cs2-skins","orange-cs2-skins","teal-cs2-skins","black-white-cs2-skins"],
 "de": ["rot-schwarze-cs2-skins","blaue-cs2-skins","pinke-cs2-skins","lila-cs2-skins","gruene-cs2-skins","goldene-cs2-skins","orange-cs2-skins","tuerkise-cs2-skins","schwarz-weisse-cs2-skins"],
 "pt": ["skins-vermelhas-cs2","skins-azuis-cs2","skins-rosas-cs2","skins-roxas-cs2","skins-verdes-cs2","skins-douradas-cs2","skins-laranjas-cs2","skins-turquesa-cs2","skins-preto-branco-cs2"],
 "tr": ["kirmizi-cs2-skinleri","mavi-cs2-skinleri","pembe-cs2-skinleri","mor-cs2-skinleri","yesil-cs2-skinleri","altin-cs2-skinleri","turuncu-cs2-skinleri","turkuaz-cs2-skinleri","siyah-beyaz-cs2-skinleri"],
 "pl": ["czerwone-skiny-cs2","niebieskie-skiny-cs2","rozowe-skiny-cs2","fioletowe-skiny-cs2","zielone-skiny-cs2","zlote-skiny-cs2","pomaranczowe-skiny-cs2","turkusowe-skiny-cs2","czarno-biale-skiny-cs2"],
}
PCOL = [["#c4161c","#1a1a1a"],["#1f4fd6"],["#ff5cb0"],["#6a2bb5"],["#1d9b5a"],["#d4af37"],["#f26a1b","#f4f4f4"],["#00c2c7"],["#f4f4f4","#1a1a1a"]]
PNAMES = {
 "ru": ["Красный с чёрным","Синий","Розовый","Фиолетовый","Зелёный","Золото","Оранжевый с белым","Бирюза","Чёрно-белый"],
 "en": ["Red & black","Blue","Pink","Purple","Green","Gold","Orange & white","Teal","Black & white"],
 "de": ["Rot-Schwarz","Blau","Pink","Lila","Grün","Gold","Orange-Weiß","Türkis","Schwarz-Weiß"],
 "pt": ["Vermelho e preto","Azul","Rosa","Roxo","Verde","Dourado","Laranja e branco","Turquesa","Preto e branco"],
 "tr": ["Kırmızı-siyah","Mavi","Pembe","Mor","Yeşil","Altın","Turuncu-beyaz","Turkuaz","Siyah-beyaz"],
 "pl": ["Czerwono-czarny","Niebieski","Różowy","Fioletowy","Zielony","Złoty","Pomarańczowo-biały","Turkusowy","Czarno-biały"],
}
PICK = {"ru":"Или сразу выбери цвет:","en":"Or pick a color right away:","de":"Oder wähle direkt eine Farbe:","pt":"Ou escolha uma cor agora:","tr":"Ya da hemen bir renk seç:","pl":"Albo od razu wybierz kolor:"}
TAKE = {"ru":"Собрать такой сет →","en":"Build this set →","de":"Dieses Set bauen →","pt":"Montar este set →","tr":"Bu seti kur →","pl":"Zbuduj ten zestaw →"}
ABOUT_LABEL = {"ru": "О проекте", "en": "About", "de": "Über uns", "pt": "Sobre", "tr": "Hakkında", "pl": "O projekcie"}

T = {
"ru": dict(
 title="Skinset — подбор скинов CS2 по цвету | О проекте и авторе viv1stop",
 desc="Skinset — бесплатный конструктор инвентаря CS2 в одном цвете: нож, перчатки и оружие под цвет и бюджет, живые цены, вход через Steam. Проект стримера viv1stop.",
 kicker="Бесплатный конструктор для CS2", h1="Собери инвентарь CS2<br><em>в одном цвете</em>",
 lead="Skinset за секунды подбирает нож, перчатки и всё оружие под выбранный цвет и твой бюджет. С живыми ценами, качеством и кнопкой покупки у каждого скина.",
 cta="Открыть конструктор", cta2="Смотреть стрим",
 stats=[("2 000+", "скинов с ценами"), ("5 мин", "обновление цен"), ("6", "языков"), ("Steam", "вход и инвентарь")],
 how_h="Как это работает", how=[("Выбери цвет", "Один или два — например, красный с чёрным. Скины подбираются по реальным цветам картинки, а не по названию."), ("Укажи бюджет", "Сумма на весь сет: нож и перчатки получают большую часть, винтовки — среднюю, пистолеты — остаток."), ("Доведи до идеала", "Закрепляй удачное, остальное перемешивай, выбирай качество от FN до BS. Цена сета пересчитывается сразу."), ("Покупай или делись", "У каждого скина — кнопка покупки на маркете. Сет можно скопировать, сохранить картинкой или опубликовать в ленту.")],
 feat_h="Что умеет Skinset", feat=[("Подбор по цвету", "Сравниваем цвета каждого скина с твоей палитрой и показываем самые точные совпадения."), ("Бюджет на весь сет", "Распределяем сумму между слотами по важности и держим итог в рамках."), ("Живые цены", "Цены и качество обновляются каждые 5 минут, видно, сколько стоит каждый предмет и весь сет."), ("Свой инвентарь", "Войди через Steam — сайт найдёт скины, которые у тебя уже есть, и соберёт сет вокруг них."), ("Лента сетов", "Публикуй свои сеты, смотри и лайкай чужие, бери понравившиеся себе в один клик."), ("Гайды и подборки", "Блог с готовыми цветными сетами, сочетаниями и инвентарями под любой бюджет.")],
 me_h="Автор — стример viv1stop", me_p="Привет! Я Вова, стримлю Counter-Strike на Twitch. Skinset появился из стримов: зрители постоянно просили собрать им красивый инвентарь в одной гамме и под их деньги. Теперь это может сделать каждый — за пару кликов и бесплатно.",
 me_stats=[("≈370", "зрителей в среднем"), ("17 000+", "фолловеров"), ("60 ч", "эфира в месяц")], me_cta="Перейти на Twitch",
 p_h="Для маркетплейсов и брендов", p_p="Skinset приводит игроков, которые уже выбрали конкретные скины и готовы их купить. Открыт к партнёрствам:",
 p_list=["Кнопка покупки и цены вашей площадки в карточках скинов", "Интеграция на стримах: сборка сетов с вашими лотами в прямом эфире", "Статьи и подборки в блоге на 6 языках", "Розыгрыши и промокоды для аудитории"], p_cta="Написать в Telegram",
 faq_h="Частые вопросы", faq=[("Skinset бесплатный?", "Да, полностью. Мы зарабатываем на партнёрских ссылках маркетов — для тебя цена не меняется."), ("Откуда цены?", "С крупных маркетплейсов, обновляются каждые 5 минут. Точная цена и наличие — на площадке."), ("Зачем входить через Steam?", "Чтобы сайт видел твой открытый инвентарь CS2 и собирал сет вокруг скинов, которые у тебя уже есть. Пароль вводится только на сайте Steam."), ("Это официальный сайт Valve?", "Нет, это фанатский проект, не связанный с Valve.")],
 foot="Skinset — фанатский проект, не связан с Valve. Counter-Strike и названия предметов принадлежат их правообладателям."),
"en": dict(
 title="Skinset — CS2 skins by color | About the project and streamer viv1stop",
 desc="Skinset is a free CS2 loadout builder: knife, gloves and weapons matched to one color and your budget, with live prices and Steam login. Made by streamer viv1stop.",
 kicker="Free CS2 loadout builder", h1="Build a CS2 loadout<br><em>in one color</em>",
 lead="Skinset picks a knife, gloves and every weapon to match your color and budget in seconds — with live prices, wear and a buy button for every skin.",
 cta="Open the builder", cta2="Watch the stream",
 stats=[("2,000+", "skins with prices"), ("5 min", "price updates"), ("6", "languages"), ("Steam", "login & inventory")],
 how_h="How it works", how=[("Pick a color", "One or two — say, red and black. Skins are matched by the actual colors of their images, not by name."), ("Set a budget", "One amount for the whole set: knife and gloves get the biggest share, rifles the middle, pistols the rest."), ("Fine-tune it", "Lock what you like, shuffle the rest, choose wear from FN to BS. The set price updates instantly."), ("Buy or share", "Every skin has a marketplace buy button. Copy the set, save it as an image or publish it to the feed.")],
 feat_h="What Skinset can do", feat=[("Color matching", "We compare every skin's colors to your palette and show the closest matches."), ("Whole-set budget", "The budget is split between slots by importance and the total stays within limits."), ("Live prices", "Prices and wear update every 5 minutes — see the cost of each item and the whole set."), ("Your inventory", "Sign in with Steam and the site finds skins you already own and builds the set around them."), ("Community sets", "Publish your sets, browse and like others, take any set for yourself in one click."), ("Guides", "A blog with ready-made color sets, combos and loadouts for any budget.")],
 me_h="Made by streamer viv1stop", me_p="Hi! I'm Vova and I stream Counter-Strike on Twitch. Skinset was born on stream: viewers kept asking me to build them a good-looking one-color loadout that fits their budget. Now anyone can do it in a couple of clicks, for free.",
 me_stats=[("≈370", "average viewers"), ("17,000+", "followers"), ("60 h", "live per month")], me_cta="Go to Twitch",
 p_h="For marketplaces and brands", p_p="Skinset brings players who have already picked specific skins and are ready to buy them. Open to partnerships:",
 p_list=["Your buy button and prices on skin cards", "Stream integrations: building sets with your listings live", "Articles and guides in the blog in 6 languages", "Giveaways and promo codes for the audience"], p_cta="Message on Telegram",
 faq_h="FAQ", faq=[("Is Skinset free?", "Yes, completely. We earn from marketplace affiliate links — your price doesn't change."), ("Where do prices come from?", "From major marketplaces, updated every 5 minutes. Exact price and availability are on the marketplace."), ("Why sign in with Steam?", "So the site can see your public CS2 inventory and build a set around skins you already own. You only enter your password on Steam."), ("Is this an official Valve site?", "No, it's a fan project not affiliated with Valve.")],
 foot="Skinset is a fan project, not affiliated with Valve. Counter-Strike and item names belong to their respective owners."),
"de": dict(
 title="Skinset — CS2-Skins nach Farbe | Über das Projekt und Streamer viv1stop",
 desc="Skinset ist ein kostenloser CS2-Loadout-Builder: Messer, Handschuhe und Waffen in einer Farbe und passend zum Budget, mit Live-Preisen und Steam-Login. Vom Streamer viv1stop.",
 kicker="Kostenloser CS2-Loadout-Builder", h1="Dein CS2-Loadout<br><em>in einer Farbe</em>",
 lead="Skinset wählt in Sekunden Messer, Handschuhe und alle Waffen passend zu deiner Farbe und deinem Budget — mit Live-Preisen, Zustand und Kauf-Button für jeden Skin.",
 cta="Builder öffnen", cta2="Stream ansehen",
 stats=[("2.000+", "Skins mit Preisen"), ("5 Min", "Preis-Updates"), ("6", "Sprachen"), ("Steam", "Login & Inventar")],
 how_h="So funktioniert's", how=[("Farbe wählen", "Eine oder zwei — etwa Rot und Schwarz. Skins werden nach den echten Farben des Bildes ausgewählt, nicht nach Namen."), ("Budget festlegen", "Ein Betrag für das ganze Set: Messer und Handschuhe bekommen den größten Teil, Gewehre die Mitte, Pistolen den Rest."), ("Feinschliff", "Fixiere, was dir gefällt, mische den Rest, wähle den Zustand von FN bis BS. Der Set-Preis wird sofort neu berechnet."), ("Kaufen oder teilen", "Jeder Skin hat einen Kauf-Button. Set kopieren, als Bild speichern oder im Feed veröffentlichen.")],
 feat_h="Was Skinset kann", feat=[("Farbabgleich", "Wir vergleichen die Farben jedes Skins mit deiner Palette und zeigen die besten Treffer."), ("Budget fürs ganze Set", "Das Budget wird nach Wichtigkeit auf die Slots verteilt, die Summe bleibt im Rahmen."), ("Live-Preise", "Preise und Zustände werden alle 5 Minuten aktualisiert."), ("Dein Inventar", "Mit Steam anmelden — die Seite findet deine Skins und baut das Set um sie herum."), ("Community-Sets", "Veröffentliche Sets, like andere und übernimm jedes Set mit einem Klick."), ("Guides", "Blog mit fertigen Farbsets, Kombinationen und Loadouts für jedes Budget.")],
 me_h="Vom Streamer viv1stop", me_p="Hi! Ich bin Vova und streame Counter-Strike auf Twitch. Skinset ist im Stream entstanden: Zuschauer wollten ständig ein schönes Loadout in einer Farbe passend zu ihrem Budget. Jetzt kann das jeder — mit ein paar Klicks und kostenlos.",
 me_stats=[("≈370", "Zuschauer im Schnitt"), ("17.000+", "Follower"), ("60 Std", "live pro Monat")], me_cta="Zu Twitch",
 p_h="Für Marktplätze und Marken", p_p="Skinset bringt Spieler, die bereits konkrete Skins ausgewählt haben und kaufbereit sind. Offen für Partnerschaften:",
 p_list=["Euer Kauf-Button und eure Preise auf den Skin-Karten", "Stream-Integrationen: Sets live mit euren Angeboten bauen", "Artikel und Guides im Blog in 6 Sprachen", "Gewinnspiele und Promocodes"], p_cta="Auf Telegram schreiben",
 faq_h="Häufige Fragen", faq=[("Ist Skinset kostenlos?", "Ja. Wir verdienen an Partnerlinks der Marktplätze — dein Preis ändert sich nicht."), ("Woher kommen die Preise?", "Von großen Marktplätzen, alle 5 Minuten aktualisiert. Genaue Preise und Verfügbarkeit auf dem Marktplatz."), ("Warum mit Steam anmelden?", "Damit die Seite dein öffentliches CS2-Inventar sieht und Sets um deine Skins baut. Das Passwort gibst du nur bei Steam ein."), ("Ist das eine offizielle Valve-Seite?", "Nein, ein Fanprojekt ohne Verbindung zu Valve.")],
 foot="Skinset ist ein Fanprojekt und nicht mit Valve verbunden. Counter-Strike und Itemnamen gehören ihren Rechteinhabern."),
"pt": dict(
 title="Skinset — skins de CS2 por cor | Sobre o projeto e o streamer viv1stop",
 desc="Skinset é um montador gratuito de inventário de CS2: faca, luvas e armas em uma cor e no seu orçamento, com preços ao vivo e login Steam. Criado pelo streamer viv1stop.",
 kicker="Montador grátis de inventário CS2", h1="Monte seu inventário CS2<br><em>em uma cor</em>",
 lead="O Skinset escolhe faca, luvas e todas as armas na cor e no orçamento que você quiser em segundos — com preços ao vivo, desgaste e botão de compra em cada skin.",
 cta="Abrir o montador", cta2="Ver a live",
 stats=[("2.000+", "skins com preço"), ("5 min", "atualização de preços"), ("6", "idiomas"), ("Steam", "login e inventário")],
 how_h="Como funciona", how=[("Escolha a cor", "Uma ou duas — por exemplo, vermelho e preto. As skins são escolhidas pelas cores reais da imagem, não pelo nome."), ("Defina o orçamento", "Um valor para o set todo: faca e luvas ficam com a maior parte, rifles com o meio e pistolas com o resto."), ("Ajuste", "Fixe o que gostou, embaralhe o resto, escolha o desgaste de FN a BS. O preço do set atualiza na hora."), ("Compre ou compartilhe", "Cada skin tem botão de compra. Copie o set, salve como imagem ou publique no feed.")],
 feat_h="O que o Skinset faz", feat=[("Combinação por cor", "Comparamos as cores de cada skin com a sua paleta e mostramos as mais próximas."), ("Orçamento do set", "O valor é dividido entre os slots por importância e o total fica no limite."), ("Preços ao vivo", "Preços e desgaste atualizados a cada 5 minutos."), ("Seu inventário", "Entre com a Steam e o site encontra as skins que você já tem e monta o set ao redor delas."), ("Sets da comunidade", "Publique seus sets, curta os de outros e pegue qualquer um com um clique."), ("Guias", "Blog com sets prontos por cor, combinações e inventários para todo orçamento.")],
 me_h="Criado pelo streamer viv1stop", me_p="Oi! Eu sou o Vova e faço live de Counter-Strike na Twitch. O Skinset nasceu na live: os viewers sempre pediam um inventário bonito em uma cor e no orçamento deles. Agora qualquer um faz isso em poucos cliques, de graça.",
 me_stats=[("≈370", "viewers em média"), ("17.000+", "seguidores"), ("60 h", "de live por mês")], me_cta="Ir para a Twitch",
 p_h="Para marketplaces e marcas", p_p="O Skinset traz jogadores que já escolheram skins específicas e estão prontos para comprar. Aberto a parcerias:",
 p_list=["Seu botão de compra e preços nos cards das skins", "Integrações na live: montar sets com seus anúncios ao vivo", "Artigos e guias no blog em 6 idiomas", "Sorteios e cupons para o público"], p_cta="Falar no Telegram",
 faq_h="Perguntas frequentes", faq=[("O Skinset é grátis?", "Sim. Ganhamos com links de afiliado dos marketplaces — o seu preço não muda."), ("De onde vêm os preços?", "De grandes marketplaces, atualizados a cada 5 minutos. Preço exato e disponibilidade no marketplace."), ("Por que entrar com a Steam?", "Para o site ver seu inventário público de CS2 e montar o set ao redor das suas skins. A senha é digitada só na Steam."), ("É um site oficial da Valve?", "Não, é um projeto de fã sem ligação com a Valve.")],
 foot="Skinset é um projeto de fã, sem ligação com a Valve. Counter-Strike e nomes de itens pertencem aos seus donos."),
"tr": dict(
 title="Skinset — renge göre CS2 skinleri | Proje ve yayıncı viv1stop hakkında",
 desc="Skinset ücretsiz bir CS2 envanter oluşturucu: bıçak, eldiven ve silahlar tek renkte ve bütçene göre, canlı fiyatlar ve Steam girişi ile. Yayıncı viv1stop'un projesi.",
 kicker="Ücretsiz CS2 envanter oluşturucu", h1="CS2 envanterini<br><em>tek renkte kur</em>",
 lead="Skinset seçtiğin renk ve bütçeye göre bıçak, eldiven ve tüm silahları saniyeler içinde seçer — canlı fiyatlar, aşınma ve her skin için satın al butonu ile.",
 cta="Oluşturucuyu aç", cta2="Yayını izle",
 stats=[("2.000+", "fiyatlı skin"), ("5 dk", "fiyat güncellemesi"), ("6", "dil"), ("Steam", "giriş ve envanter")],
 how_h="Nasıl çalışır", how=[("Renk seç", "Bir veya iki — örneğin kırmızı ve siyah. Skinler isme göre değil, görselin gerçek renklerine göre seçilir."), ("Bütçe belirle", "Tüm set için tek tutar: bıçak ve eldiven en büyük payı, tüfekler ortayı, tabancalar kalanı alır."), ("İnce ayar yap", "Beğendiğini sabitle, gerisini karıştır, FN'den BS'ye aşınma seç. Set fiyatı anında güncellenir."), ("Satın al veya paylaş", "Her skinde satın al butonu var. Seti kopyala, görsel olarak kaydet veya akışta paylaş.")],
 feat_h="Skinset neler yapar", feat=[("Renk eşleştirme", "Her skinin renklerini paletinle karşılaştırıp en yakınlarını gösteririz."), ("Tüm set için bütçe", "Bütçe önem sırasına göre slotlara dağıtılır, toplam sınırda kalır."), ("Canlı fiyatlar", "Fiyatlar ve aşınmalar 5 dakikada bir güncellenir."), ("Kendi envanterin", "Steam ile gir — site sahip olduğun skinleri bulur ve seti onların etrafında kurar."), ("Topluluk setleri", "Setlerini paylaş, diğerlerini beğen, istediğin seti tek tıkla al."), ("Rehberler", "Hazır renk setleri, kombinler ve her bütçeye envanterler içeren blog.")],
 me_h="Yayıncı viv1stop'un projesi", me_p="Selam! Ben Vova, Twitch'te Counter-Strike yayını yapıyorum. Skinset yayında doğdu: izleyiciler sürekli bütçelerine uygun, tek renkte güzel bir envanter istiyordu. Artık herkes birkaç tıkla ve ücretsiz yapabiliyor.",
 me_stats=[("≈370", "ortalama izleyici"), ("17.000+", "takipçi"), ("60 sa", "aylık yayın")], me_cta="Twitch'e git",
 p_h="Pazar yerleri ve markalar için", p_p="Skinset, belirli skinleri seçmiş ve almaya hazır oyuncular getirir. İş birliklerine açığız:",
 p_list=["Skin kartlarında sizin satın al butonunuz ve fiyatlarınız", "Yayın entegrasyonları: ilanlarınızla canlı set kurma", "Blogda 6 dilde makaleler ve rehberler", "İzleyicilere çekilişler ve promosyon kodları"], p_cta="Telegram'dan yaz",
 faq_h="Sık sorulan sorular", faq=[("Skinset ücretsiz mi?", "Evet. Pazar yerlerinin ortaklık linklerinden kazanırız — senin fiyatın değişmez."), ("Fiyatlar nereden geliyor?", "Büyük pazar yerlerinden, 5 dakikada bir güncellenir. Kesin fiyat ve stok pazar yerinde."), ("Neden Steam ile giriş?", "Site açık CS2 envanterini görüp seti sahip olduğun skinlerin etrafında kursun diye. Şifreni sadece Steam'de girersin."), ("Bu resmi bir Valve sitesi mi?", "Hayır, Valve ile bağlantısı olmayan bir hayran projesi.")],
 foot="Skinset bir hayran projesidir, Valve ile bağlantılı değildir. Counter-Strike ve eşya adları sahiplerine aittir."),
"pl": dict(
 title="Skinset — skiny CS2 według koloru | O projekcie i streamerze viv1stop",
 desc="Skinset to darmowy kreator ekwipunku CS2: nóż, rękawice i broń w jednym kolorze i w Twoim budżecie, z cenami na żywo i logowaniem przez Steam. Projekt streamera viv1stop.",
 kicker="Darmowy kreator ekwipunku CS2", h1="Zbuduj ekwipunek CS2<br><em>w jednym kolorze</em>",
 lead="Skinset w kilka sekund dobiera nóż, rękawice i całą broń do wybranego koloru i budżetu — z cenami na żywo, stanem i przyciskiem zakupu przy każdym skinie.",
 cta="Otwórz kreator", cta2="Zobacz stream",
 stats=[("2000+", "skinów z cenami"), ("5 min", "aktualizacja cen"), ("6", "języków"), ("Steam", "logowanie i ekwipunek")],
 how_h="Jak to działa", how=[("Wybierz kolor", "Jeden lub dwa — np. czerwony z czarnym. Skiny dobieramy po prawdziwych kolorach obrazka, nie po nazwie."), ("Ustal budżet", "Jedna kwota na cały zestaw: nóż i rękawice dostają największą część, karabiny środek, pistolety resztę."), ("Dopracuj", "Przypnij to, co pasuje, resztę przetasuj, wybierz stan od FN do BS. Cena zestawu liczy się od razu."), ("Kup lub udostępnij", "Każdy skin ma przycisk zakupu. Skopiuj zestaw, zapisz jako obrazek albo opublikuj w feedzie.")],
 feat_h="Co potrafi Skinset", feat=[("Dobór koloru", "Porównujemy kolory każdego skina z Twoją paletą i pokazujemy najlepsze dopasowania."), ("Budżet na zestaw", "Kwota jest dzielona między sloty według ważności, suma mieści się w limicie."), ("Ceny na żywo", "Ceny i stany aktualizowane co 5 minut."), ("Twój ekwipunek", "Zaloguj się przez Steam — strona znajdzie Twoje skiny i zbuduje zestaw wokół nich."), ("Zestawy społeczności", "Publikuj zestawy, lajkuj inne, bierz dowolny jednym kliknięciem."), ("Poradniki", "Blog z gotowymi zestawami kolorów, połączeniami i ekwipunkami na każdy budżet.")],
 me_h="Autor — streamer viv1stop", me_p="Cześć! Jestem Vova i streamuję Counter-Strike na Twitchu. Skinset powstał na streamach: widzowie ciągle prosili o ładny ekwipunek w jednym kolorze i w ich budżecie. Teraz każdy zrobi to w kilka kliknięć, za darmo.",
 me_stats=[("≈370", "widzów średnio"), ("17 000+", "obserwujących"), ("60 h", "na żywo miesięcznie")], me_cta="Przejdź na Twitch",
 p_h="Dla rynków i marek", p_p="Skinset przyprowadza graczy, którzy wybrali już konkretne skiny i są gotowi je kupić. Jesteśmy otwarci na współpracę:",
 p_list=["Wasz przycisk zakupu i ceny na kartach skinów", "Integracje na streamach: budowanie zestawów z Waszymi ofertami na żywo", "Artykuły i poradniki na blogu w 6 językach", "Konkursy i kody promocyjne dla widzów"], p_cta="Napisz na Telegramie",
 faq_h="Częste pytania", faq=[("Czy Skinset jest darmowy?", "Tak. Zarabiamy na linkach partnerskich rynków — Twoja cena się nie zmienia."), ("Skąd są ceny?", "Z dużych rynków, aktualizowane co 5 minut. Dokładna cena i dostępność na rynku."), ("Po co logować się przez Steam?", "Żeby strona widziała Twój publiczny ekwipunek CS2 i budowała zestaw wokół Twoich skinów. Hasło wpisujesz tylko na Steam."), ("Czy to oficjalna strona Valve?", "Nie, to projekt fanowski niezwiązany z Valve.")],
 foot="Skinset to projekt fanowski, niezwiązany z Valve. Counter-Strike i nazwy przedmiotów należą do ich właścicieli."),
}

def showcase():
    d = json.load(open(os.path.join(ROOT, "data/skins-extra.json"), encoding="utf-8"))
    want = [("★ Bayonet", "Doppler (Ruby)"), ("★ Driver Gloves", "Brocade Crane"), ("M4A4", "Bullet Rain"), ("USP-S", "Bleeding Edge"), ("Glock-18", "Royal Legion")]
    out = []
    for w, sk in want:
        for r in d:
            if r[1] == w and r[2] == sk and r[5]:
                out.append((w.replace("★ ", ""), sk, r[5])); break
    return out

ICONS = ["M12 3a9 9 0 1 0 0 18c1 0 1.5-.7 1.5-1.4 0-.4-.2-.7-.4-1-.2-.3-.4-.6-.4-1 0-.8.6-1.4 1.4-1.4H16a5 5 0 0 0 5-5c0-4.4-4-8.2-9-8.2Z|M7.5 11.5h.01M9.5 7.5h.01M14.5 7.5h.01",
         "M3 7h18v12H3z|M3 10h18|M16 14h2", "M3 17l6-6 4 4 8-8|M14 7h7v7", "M4 7h16v12H4z|M9 7V5h6v2", "M12 21s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.6-7 10-7 10Z", "M5 4h11l3 3v13H5z|M8 9h8M8 13h8M8 17h5"]

def icon(i):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + "".join(f'<path d="{p}"/>' for p in ICONS[i].split("|")) + "</svg>"

CSS = r"""
:root{--pick:#c4161c;--ink:#f3f1ea;--soft:#b9b4a7;--dim:#7d786d;--line:rgba(255,255,255,.1);--line2:rgba(255,255,255,.18);--hud:"Oswald","Arial Narrow",Impact,sans-serif;--body:"Roboto Condensed","Arial Narrow",system-ui,sans-serif}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);font:400 16px/1.55 var(--body);background:#0b0c0f;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;z-index:-1;background:radial-gradient(900px 600px at 80% -10%,rgba(196,22,28,.28),transparent 60%),radial-gradient(700px 500px at -10% 40%,rgba(110,40,200,.18),transparent 60%),repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 48px),#0b0c0f}
a{color:inherit}
.hud{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:12px;height:62px;padding:0 24px;background:rgba(10,11,13,.86);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.logo{display:flex;align-items:center;gap:10px;font:700 1.35rem/1 var(--hud);letter-spacing:.06em;text-transform:uppercase;font-style:italic;text-decoration:none}
.logo svg{width:30px;height:30px}
.tabs{display:flex;margin:0 auto;height:100%}
.tabs a{display:flex;align-items:center;padding:0 18px;font:500 .95rem/1 var(--hud);letter-spacing:.08em;text-transform:uppercase;color:var(--soft);text-decoration:none;border-bottom:3px solid transparent}
.tabs a:hover{color:var(--ink)}.tabs a.on{color:var(--ink);border-bottom-color:var(--pick)}
.langs{position:relative}
.lbtn{display:inline-flex;align-items:center;gap:7px;height:34px;padding:0 10px;background:rgba(255,255,255,.04);border:1px solid var(--line2);color:var(--ink);font:600 .74rem/1 var(--hud);letter-spacing:.08em;cursor:pointer}
.lbtn svg{width:15px;height:15px;opacity:.8}
.lmenu{display:none;position:absolute;right:0;top:calc(100% + 6px);min-width:170px;padding:6px;background:#15171c;border:1px solid var(--line2);box-shadow:0 18px 40px rgba(0,0,0,.55)}
.langs.open .lmenu{display:block}
.lmenu a{display:flex;justify-content:space-between;padding:9px 10px;color:var(--soft);text-decoration:none}
.lmenu a:hover,.lmenu a.on{background:rgba(255,255,255,.06);color:var(--ink)}
.lmenu small{font:600 .68rem/1 var(--hud);letter-spacing:.08em;color:var(--dim)}
main{max-width:1180px;margin:0 auto;padding:0 24px}
section{padding:72px 0}
.hero{display:grid;grid-template-columns:1.05fr 1fr;gap:48px;align-items:center;padding-top:64px}
.kick{display:inline-block;font:600 .8rem/1 var(--hud);letter-spacing:.18em;text-transform:uppercase;background:var(--pick);color:#fff;padding:7px 14px 8px;clip-path:polygon(8px 0,100% 0,calc(100% - 8px) 100%,0 100%)}
h1{margin:18px 0 18px;font:700 clamp(2.4rem,5.4vw,4.4rem)/1 var(--hud);text-transform:uppercase;letter-spacing:.01em}
h1 em,h2 em{font-style:normal;color:var(--pick);text-shadow:0 0 40px rgba(196,22,28,.45)}
.lead{font-size:1.15rem;color:var(--soft);max-width:54ch;margin:0 0 28px}
.btns{display:flex;flex-wrap:wrap;gap:12px}
.btn{display:inline-flex;align-items:center;gap:10px;height:52px;padding:0 26px;font:600 1rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;text-decoration:none;clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px);transition:filter .15s}
.btn:hover{filter:brightness(1.15)}
.btn.p{background:var(--pick);color:#fff;box-shadow:0 10px 30px rgba(196,22,28,.35)}
.btn.s{background:rgba(145,70,255,.16);border:1px solid rgba(145,70,255,.5);color:#d9c2ff}
.btn svg{width:18px;height:18px}
.set{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}
.pick{margin-top:26px}.pick small{display:block;color:var(--soft);font:500 .82rem/1 var(--hud);letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px}.sws{display:flex;flex-wrap:wrap;gap:8px}.sws a{width:42px;height:42px;border:1px solid rgba(255,255,255,.25);clip-path:polygon(7px 0,100% 0,100% calc(100% - 7px),calc(100% - 7px) 100%,0 100%,0 7px);transition:transform .15s,border-color .15s}.sws a:hover{transform:translateY(-3px) scale(1.08);border-color:#fff}
.setwrap{display:block;text-decoration:none;color:inherit}.setwrap .take{display:flex;justify-content:center;margin-top:10px;font:600 .9rem/1 var(--hud);letter-spacing:.1em;text-transform:uppercase;color:var(--pick)}.setwrap:hover .take{color:#ff4b52}.setwrap:hover .sk{border-color:rgba(255,255,255,.35)}
.sk{position:relative;transition:transform .2s,border-color .2s;background:linear-gradient(160deg,rgba(255,255,255,.07),rgba(255,255,255,.015));border:1px solid var(--line2);border-bottom:3px solid var(--pick);padding:12px 10px 10px;clip-path:polygon(12px 0,100% 0,100% calc(100% - 12px),calc(100% - 12px) 100%,0 100%,0 12px);animation:up .6s both}
.sk:nth-child(1){grid-column:span 6}.sk:nth-child(2){grid-column:span 6}.sk:nth-child(n+3){grid-column:span 2}
.sk img{display:block;width:100%;height:120px;object-fit:contain;filter:drop-shadow(0 10px 14px rgba(0,0,0,.6))}
.sk:nth-child(n+3) img{height:70px}
.sk b{display:block;font:600 .95rem/1.1 var(--hud);text-transform:uppercase;letter-spacing:.03em;margin-top:6px}
.sk small{color:var(--dim);font-size:.78rem}
.setwrap .sk:hover{transform:translateY(-4px)}.sk:nth-child(2){animation-delay:.1s}.sk:nth-child(3){animation-delay:.2s}.sk:nth-child(4){animation-delay:.3s}.sk:nth-child(5){animation-delay:.4s}
@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.stats{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);background:rgba(14,15,17,.6)}
.stats div{padding:22px 20px;border-left:1px solid var(--line)}.stats div:first-child{border-left:0}
.stats b{display:block;font:700 2rem/1 var(--hud);color:var(--ink)}
.stats span{color:var(--soft);font-size:.9rem;text-transform:uppercase;letter-spacing:.06em}
h2{margin:0 0 28px;font:700 clamp(1.7rem,3.2vw,2.5rem)/1.05 var(--hud);text-transform:uppercase;letter-spacing:.02em}
h2::before{content:"";display:block;width:44px;height:4px;background:var(--pick);margin-bottom:14px}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;counter-reset:s}
.card{background:rgba(14,15,17,.72);border:1px solid var(--line);padding:22px;clip-path:polygon(14px 0,100% 0,100% calc(100% - 14px),calc(100% - 14px) 100%,0 100%,0 14px)}
.card h3{margin:0 0 8px;font:600 1.15rem/1.15 var(--hud);text-transform:uppercase;letter-spacing:.03em}
.card p{margin:0;color:var(--soft)}
.steps .card::before{counter-increment:s;content:counter(s);display:grid;place-items:center;width:34px;height:34px;margin-bottom:14px;background:var(--pick);color:#fff;font:700 1rem/1 var(--hud);clip-path:polygon(6px 0,100% 0,100% calc(100% - 6px),calc(100% - 6px) 100%,0 100%,0 6px)}
.feats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.feats svg{width:30px;height:30px;color:var(--pick);margin-bottom:12px}
.me{display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:center;background:linear-gradient(135deg,rgba(145,70,255,.18),rgba(14,15,17,.75) 60%);border:1px solid rgba(145,70,255,.35);padding:36px;clip-path:polygon(18px 0,100% 0,100% calc(100% - 18px),calc(100% - 18px) 100%,0 100%,0 18px)}
.me p{color:var(--soft);font-size:1.08rem;margin:0 0 22px}
.me .ms{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.me .ms div{background:rgba(0,0,0,.3);border:1px solid var(--line);padding:16px}
.me .ms b{display:block;font:700 1.8rem/1 var(--hud);color:#d9c2ff}
.me .ms span{color:var(--soft);font-size:.85rem}
.part{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:start}
.part ul{list-style:none;margin:0 0 24px;padding:0;display:grid;gap:10px}
.part li{display:flex;gap:12px;align-items:flex-start;background:rgba(14,15,17,.72);border:1px solid var(--line);padding:14px 16px}
.part li::before{content:"";flex:none;width:10px;height:10px;margin-top:7px;background:var(--pick);transform:rotate(45deg)}
.part p{color:var(--soft);font-size:1.08rem;margin:0 0 22px}
.btn.tg{background:#229ed9;color:#fff}
details{background:rgba(14,15,17,.72);border:1px solid var(--line);margin-bottom:10px}
summary{cursor:pointer;padding:18px 20px;font:600 1.05rem/1.2 var(--hud);text-transform:uppercase;letter-spacing:.03em;list-style:none;display:flex;justify-content:space-between;gap:12px}
summary::after{content:"+";color:var(--pick);font-size:1.4rem;line-height:.8}
details[open] summary::after{content:"−"}
details p{margin:0;padding:0 20px 18px;color:var(--soft)}
.final{text-align:center;padding:72px 0 88px}
.final h2::before{margin-left:auto;margin-right:auto}
footer{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--dim);font-size:.85rem}
footer a{color:var(--soft)}
@media(max-width:960px){.hero,.me,.part{grid-template-columns:1fr}.steps{grid-template-columns:1fr 1fr}.feats{grid-template-columns:1fr 1fr}.stats{grid-template-columns:1fr 1fr}.stats div:nth-child(3){border-left:0}.stats div:nth-child(n+3){border-top:1px solid var(--line)}}
@media(max-width:700px){.sws{flex-wrap:nowrap;gap:5px}.sws a{flex:1 1 0;width:auto;height:auto;aspect-ratio:1;max-width:42px}.hud{padding:0 14px;height:auto;flex-wrap:wrap;padding-top:10px}.tabs{order:3;width:100%;margin:6px -14px 0;overflow-x:auto;height:44px}.tabs a{padding:0 12px;font-size:.85rem;white-space:nowrap}.langs{margin-left:auto}main{padding:0 16px}section{padding:48px 0}.hero{padding-top:36px;gap:28px}.steps,.feats{grid-template-columns:1fr}.me{padding:24px}.me .ms b{font-size:1.4rem}.btn{height:48px;padding:0 20px;font-size:.92rem}.sk img{height:90px}.sk:nth-child(n+3) img{height:56px}}
"""

LANG_JS = '<script>(()=>{const L=document.querySelector(".langs"),b=L.querySelector(".lbtn");b.onclick=e=>{e.stopPropagation();L.classList.toggle("open")};document.addEventListener("click",e=>{if(!L.contains(e.target))L.classList.remove("open")})})();</script>'
LNAMES = {"ru": "Русский", "en": "English", "de": "Deutsch", "pt": "Português", "tr": "Türkçe", "pl": "Polski"}

def build(lang, items):
    t = T[lang]; e = html.escape
    url = "https://skin-set.com" + PATHS[lang]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="https://skin-set.com{PATHS[l]}">' for l in PATHS) + f'<link rel="alternate" hreflang="x-default" href="https://skin-set.com{PATHS["en"]}">'
    nav = "".join(f'<a href="{h}">{e(n)}</a>' for h, n in NAV[lang]) + f'<a href="{PATHS[lang]}" class="on">{e(ABOUT_LABEL[lang])}</a>'
    lm = "".join(f'<a href="{PATHS[l]}" hreflang="{HREFLANG[l]}"{" class=on" if l == lang else ""}><span>{LNAMES[l]}</span><small>{l.upper()}</small></a>' for l in PATHS)
    tw_svg = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 2 2 6v15h5v3h3l3-3h4l5-5V2H4zm16 13-3 3h-5l-3 3v-3H6V4h14v11zM15 7h2v5h-2V7zm-5 0h2v5h-2V7z"/></svg>'
    tg_svg = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.9 4.3 18.7 19.4c-.2 1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-5 9.1-8.2c.4-.4-.1-.6-.6-.2L6.2 13 1.4 11.5c-1-.3-1-1 .2-1.5L20.6 2.9c.9-.3 1.6.2 1.3 1.4Z"/></svg>'
    sets = "".join(f'<div class="sk"><img src="{e(img)}" alt="{e(w)} | {e(sk)}" loading="eager" onerror="this.style.visibility=\'hidden\'"><b>{e(sk)}</b><small>{e(w)}</small></div>' for w, sk, img in items)
    from urllib.parse import quote
    setq = quote(';'.join(f'{w}|{sk}' for w, sk, img in items), safe='')
    def bgc(c): return c[0] if len(c)==1 else f'linear-gradient(135deg,{c[0]} 50%,{c[1]} 50%)'
    swatches = ''.join(f'<a href="{HOME[lang]}{CP[lang][i]}/" title="{e(PNAMES[lang][i])}" aria-label="{e(PNAMES[lang][i])}" style="background:{bgc(c)}"></a>' for i, c in enumerate(PCOL))
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}
    org_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Skinset", "url": "https://skin-set.com" + HOME[lang], "applicationCategory": "GameApplication", "operatingSystem": "Web", "inLanguage": HREFLANG[lang], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "description": t["desc"], "author": {"@type": "Person", "name": "viv1stop", "url": TW, "sameAs": [TW, TG]}}
    og = f"https://skin-set.com/img/og-{lang}.png"
    return f"""<!doctype html>
<html lang="{HREFLANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['desc'])}">
<link rel="canonical" href="{url}">
{alts}
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:title" content="{e(t['title'])}"><meta property="og:description" content="{e(t['desc'])}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0c0f">
<link rel="icon" type="image/svg+xml" href="/img/favicon.svg"><link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Roboto+Condensed:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(org_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="hud">
  <a class="logo" href="{HOME[lang]}"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 26 L12 6 H20 L28 26 H22 L16 12 L10 26 Z" fill="#e8402a"/><path d="M11 20 H21 L23 26 H9 Z" fill="#fff" opacity=".9"/></svg>Skinset</a>
  <nav class="tabs">{nav}</nav>
  <div class="langs"><button class="lbtn" type="button" aria-haspopup="menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg><span>{lang.upper()}</span></button><div class="lmenu">{lm}</div></div>
</header>
<main>
  <section class="hero">
    <div>
      <span class="kick">{e(t['kicker'])}</span>
      <h1>{t['h1']}</h1>
      <p class="lead">{e(t['lead'])}</p>
      <div class="btns"><a class="btn p" href="{HOME[lang]}">{e(t['cta'])} →</a><a class="btn s" href="{TW}" target="_blank" rel="noopener">{tw_svg}{e(t['cta2'])}</a></div>
      <div class="pick"><small>{e(PICK[lang])}</small><div class="sws">{swatches}</div></div>
    </div>
    <a class="setwrap" href="{HOME[lang]}{CP[lang][0]}/?set={setq}"><div class="set">{sets}</div><span class="take">{e(TAKE[lang])}</span></a>
  </section>
  <div class="stats">{''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in t['stats'])}</div>
  <section><h2>{e(t['how_h'])}</h2><div class="steps">{''.join(f'<div class="card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in t['how'])}</div></section>
  <section style="padding-top:0"><h2>{e(t['feat_h'])}</h2><div class="feats">{''.join(f'<div class="card">{icon(i)}<h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(t['feat']))}</div></section>
  <section style="padding-top:0"><div class="me"><div><h2>{e(t['me_h'])}</h2><p>{e(t['me_p'])}</p><a class="btn s" href="{TW}" target="_blank" rel="noopener">{tw_svg}{e(t['me_cta'])}</a></div><div class="ms">{''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in t['me_stats'])}</div></div></section>
  <section style="padding-top:0" id="partners"><div class="part"><div><h2>{e(t['p_h'])}</h2><p>{e(t['p_p'])}</p><a class="btn tg" href="{TG}" target="_blank" rel="noopener">{tg_svg}{e(t['p_cta'])}</a></div><ul>{''.join(f'<li>{e(x)}</li>' for x in t['p_list'])}</ul></div></section>
  <section style="padding-top:0"><h2>{e(t['faq_h'])}</h2>{''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in t['faq'])}</section>
  <section class="final"><h2>{t['h1']}</h2><div class="btns" style="justify-content:center"><a class="btn p" href="{HOME[lang]}">{e(t['cta'])} →</a></div></section>
</main>
<footer><p>{e(t['foot'])}</p><p><a href="{TG}" target="_blank" rel="noopener">Telegram @Vivistop</a> · <a href="{TW}" target="_blank" rel="noopener">Twitch viv1stop</a></p></footer>
{LANG_JS}
</body>
</html>
"""

if __name__ == "__main__":
    items = showcase()
    for lang in PATHS:
        p = os.path.join(ROOT, PATHS[lang].strip("/"), "index.html")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        import navmore; open(p, "w", encoding="utf-8").write(navmore.fix(build(lang, items)))
        print("wrote", p)
