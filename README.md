# Репетитор ЕГЭ — Telegram-бот, Mini App и Android-приложение

Учебный проект для подготовки к ЕГЭ/ОГЭ: Telegram-бот с проверкой сочинений, базой материалов и личным кабинетом репетитора.

Код перенесён из рабочего деплоя на Render (сервис `tutor-bot`).

## Структура репозитория

```
├── Telegram Mini App/     # Telegram-бот + веб-приложение (Mini App «Кабинет»)
│   ├── bot.py             # основной бот и HTTP-сервер (aiogram + aiohttp)
│   ├── auth.py            # авторизация: Telegram Mini App (initData) и standalone (JWT)
│   ├── billing.py         # биллинг через Яндекс Облако (IAM-токен, PS256)
│   ├── essay*.py          # проверка и отчёты по сочинениям (PDF/HTML)
│   ├── assist.py          # AI-ассистент
│   ├── chatfiles.py, chatprompt.py  # работа с файлами и промптами в чате
│   ├── matlib.py, matnav.py         # библиотека и навигация по материалам
│   ├── webtools.py, ocrverify.py, fipicache.py, kimi.py
│   ├── docs/index.html    # фронтенд Mini App (SPA, русский интерфейс)
│   ├── materials/         # материалы ЕГЭ/ОГЭ (сочинения 2027)
│   ├── knowledge/         # база знаний
│   ├── assets/, fonts/    # статика: логотипы, шрифты, CSS/JS отчётов
│   ├── Dockerfile         # сборка образа
│   ├── deploy.sh          # скрипт деплоя
│   └── requirements.txt   # зависимости Python
└── APK mobile app/        # Android-приложение «Кабинет репетитора»
    ├── kabinet-repetitora.apk
    └── README.md
```

## Технологии

- **Python 3.12** — основной язык
- **aiogram 3.31** — Telegram Bot API
- **aiohttp 3.14** — HTTP-сервер Mini App и API
- **reportlab, xhtml2pdf, pypdf, pypdfium2** — генерация PDF-отчётов
- **playwright** — рендеринг HTML → PDF
- **PyJWT + cryptography** — JWT (PS256) для биллинга Яндекс Облака

## Возможности

- ✍️ Проверка сочинений ЕГЭ/ОГЭ с подробным отчётом (PDF)
- 📚 Материалы: сочинения 2027 (ЕГЭ/ОГЭ), база знаний
- 🗓 Кабинет репетитора: расписание, недельные отчёты (PDF), отправка ученикам
- 💬 AI-ассистент и чат с файлами
- 📱 Mini App в Telegram (кнопка «Кабинет») + standalone Android-приложение

## Установка и запуск

```bash
cd "Telegram Mini App"
pip install -r requirements.txt

# обязательная переменная
export BOT_TOKEN=<токен Telegram-бота>

python bot.py
```

### Docker

```bash
cd "Telegram Mini App"
docker build -t tutor-bot .
docker run -p 8080:8080 --env-file .env tutor-bot
```

### Деплой (Render)

Сервис запускается из Dockerfile; health-check — `/`. Порт задаётся переменной `PORT`
(на Render — 10000). Самоподдержание соединения — `KEEPALIVE_SEC` (по умолчанию 180 с).

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `BOT_TOKEN` | **обязательно**, токен Telegram-бота |
| `WEBAPP_URL` | HTTPS-адрес Mini App |
| `PORT` | порт HTTP-сервера (по умолчанию 8080) |
| `APP_ENV` | `dev` — тестовая среда с пометкой DEV; пусто/`prod` — прод |
| `OWNER_ID`, `ALLOWED_IDS`, `ALLOWED_USERNAMES` | доступ к кабинету |
| `AUTH_PASSWORD_HASH`, `SESSION_DAYS` | вход по паролю и срок сессии |
| `PUBLIC_URL`, `ALLOW_ORIGIN` | публичный URL и CORS |
| `CURRENCY` | символ валюты (по умолчанию ₽) |
| `API_RATE_PER_MIN` | лимит API-запросов (по умолчанию 120/мин) |
| `YANDEX_SA_KEY` / `YANDEX_SA_KEY_FILE` | ключ сервисного аккаунта Яндекс Облака (биллинг) |
| `ESSAY_REPORT_ENGINE` | движок отчёта (`html` и др.) |
| `APK_FILE` | явный путь к APK для скачивания (иначе ищется в `docs/` и `APK mobile app/`) |
| `APK_FALLBACK_URL` | куда перенаправлять `/apk`, если файла нет в деплое (пусто — отключить, по умолчанию релиз `apk-latest` репозитория) |
| `LOG_LEVEL` | уровень логирования |

## HTTP API (кратко)

| Маршрут | Описание |
|---|---|
| `/` | Mini App (docs/index.html) |
| `/apk`, `/apk/kabinet-repetitora.apk` | скачивание Android-приложения |
| `/api/data` | данные кабинета |
| `/api/week.pdf` | недельный отчёт PDF |
| `/api/materials/{id}` | материалы |
| `/api/pdf_link`, `/api/week/send` | ссылка на PDF / отправка отчёта |
| `/login`, `/api/tglogin/*` | авторизация |

Аутентификация: `X-Init` (подпись initData Telegram Mini App) или `X-Session` (JWT standalone-приложения).

## Примечание

Маршрут `/apk` в `bot.py` ищет `kabinet-repetitora.apk` по порядку: `APK_FILE` →
`Telegram Mini App/docs/` → `../APK mobile app/` (каноническое место в репозитории).
Нет файла в деплое — `/apk` перенаправляет на релиз `apk-latest` репозитория
(`.github/workflows/release.yml` перезаливает туда файл при каждом релизе).

**Важно про APK:** файл коммитится в git (`.gitignore` делает исключение для
`APK mobile app/*.apk`). Если сборки в папке нет — скачивание работать не будет:
положите `kabinet-repetitora.apk` в `APK mobile app/` и закоммитьте. Для Docker-сборки
`deploy.sh` копирует APK в `Telegram Mini App/docs/` — так файл попадает в образ.
