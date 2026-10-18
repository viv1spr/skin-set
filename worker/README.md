# Skinset worker

Одна Cloudflare Worker-функция: вход через Steam, инвентарь CS2, трекинговые ссылки.

## Установка (один раз, ~5 минут)

1. Cloudflare → **Workers & Pages** → **Create** → **Create Worker** → имя `skinset` → **Deploy**.
2. **Edit code** → вставить весь `worker.js` → **Deploy**.
3. **Storage & Databases → KV** → **Create namespace** `skinset`.
4. Воркер → **Settings → Bindings** → **Add → KV namespace**: имя переменной `KV`, namespace `skinset`.
5. Воркер → **Settings → Variables and Secrets** → **Add** (тип *Secret*):
   - `SECRET` — длинная случайная строка (подпись входа);
   - `ADMIN_KEY` — пароль для раздела «Ссылки» в админке.
6. Открыть `https://skinset.<аккаунт>.workers.dev/health` — должно быть `kv:true, secret:true, admin:true`.
7. Админка → **Настройки** → «Адрес воркера» → вставить адрес → **Сохранить**.
   Кнопка «Войти через Steam» появится на сайте через 1–2 минуты.
8. Админка → **Ссылки** → вписать `ADMIN_KEY` → создавать ссылки.

## Маршруты

| Путь | Что делает |
|---|---|
| `/login?r=URL` | редирект на вход Steam |
| `/callback` | проверка ответа Steam, возврат на сайт с `#steam=токен` |
| `/me?t=` | ник и аватар |
| `/inv?t=` | названия скинов CS2 из инвентаря (кэш 15 мин) |
| `/hit?l=CODE&e=v\|b\|p` | счётчик: переход / клик «Купить» / публикация сета |
| `/l/CODE` | короткий редирект на сайт с меткой |
| `/api/links` | GET/POST/DELETE для админки (Bearer ADMIN_KEY) |

Бесплатный тариф: 100 000 запросов в день, KV: 1 000 записей в день (каждый переход и клик по ссылке = 1 запись).
