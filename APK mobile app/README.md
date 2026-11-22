# APK mobile app — «Кабинет репетитора»

Android-приложение для репетиторов, работающих с ботом «Репетитор ЕГЭ».

## Файл

- `kabinet-repetitora.apk` — сборка приложения (~800 КБ)

Файл **лежит в этой папке и коммитится в git** (`.gitignore` делает для него исключение),
его копия лежит в `Telegram Mini App/docs/` — она попадает в Docker-образ (CI проверяет,
что копии идентичны). Если файла здесь нет — скачивание не заработает ни на одном деплое:
положите сборку сюда с именем `kabinet-repetitora.apk`, скопируйте в `Telegram Mini App/docs/`
и закоммитьте.

## Сведения

| | |
|---|---|
| Название | Кабинет репетитора |
| Пакет | `ru.kabinet.tutor` (dev-сборка: `ru.kabinet.tutor.dev`) |
| Deep link | `kabinet://` (dev: `kabinet-dev://`) |
| Доступен для скачивания | `https://<ваш-хост>/apk` (маршрут `api_apk` в `Telegram Mini App/bot.py`) |

Маршрут `/apk` ищет файл по порядку: переменная `APK_FILE` → `Telegram Mini App/docs/kabinet-repetitora.apk`
(кладёт `deploy.sh` перед Docker-сборкой) → `APK mobile app/kabinet-repetitora.apk` (эта папка).
Если файла нет в деплое — `/apk` перенаправляет на релиз `apk-latest` репозитория на GitHub
(его поддерживает `.github/workflows/release.yml`, адрес переключается переменной `APK_FALLBACK_URL`).

## Установка

1. Скопируйте `kabinet-repetitora.apk` на Android-устройство
2. Разрешите установку из неизвестных источников
3. Запустите установку

Приложение авторизуется через JWT-токен standalone-приложения (см. `Telegram Mini App/auth.py`).
