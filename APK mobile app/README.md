# APK mobile app — «Кабинет репетитора»

Android-приложение для репетиторов, работающих с ботом «Репетитор ЕГЭ».

## Файл

- `kabinet-repetitora.apk` — сборка приложения (~800 КБ)

## Сведения

| | |
|---|---|
| Название | Кабинет репетитора |
| Пакет | `ru.kabinet.tutor` (dev-сборка: `ru.kabinet.tutor.dev`) |
| Deep link | `kabinet://` (dev: `kabinet-dev://`) |
| Доступен для скачивания | `https://<ваш-хост>/apk` (маршрут в `Telegram Mini App/bot.py`) |

## Установка

1. Скопируйте `kabinet-repetitora.apk` на Android-устройство
2. Разрешите установку из неизвестных источников
3. Запустите установку

Приложение авторизуется через JWT-токен standalone-приложения (см. `Telegram Mini App/auth.py`).
