# Discord Бот Adventure Time: Установка и запуск
# Автор: @Schrodinger71

[![Deploy Discord Bot](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/deploy.yml)
[![Flake8 test](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/flake8-linter.yml/badge.svg)](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/flake8-linter.yml)
[![Linter Python Code](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/python-linter.yml/badge.svg)](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/python-linter.yml)

Этот бот разработан командой Adventure Time SS14 в **образовательных целях** для изучения и тестирования возможностей Discord API и разработки ботов. **Он не предназначен для коммерческого использования.**

**Этот бот использует библиотеку g4f исключительно для демонстрационных и образовательных целей.**

**Мы придерживаемся всех правил Discord и несем полную ответственность за его использование.**


## Установка

### 1. Клонирование репозитория:
```bash
git clone https://github.com/AdventureTimeSS14/Dev-bot.git
```

### 2. Установка зависимостей:
```bash
cd Dev-bot
pip install -r requirements.txt
```

### 3. Создание конфигурационного файла:
Создайте файл `.env` рядом с `main.py` и добавьте следующие переменные (по необходимости):

```
(Для управление дискорд ботом в целом)
DISCORD_KEY=***

(Основной для GitHub)
GITHUB=***

(Для акшонов GitHub)
ACTION_GITHUB=***

(Организация пост запросов для ss14)
POST_USERNAME_DEV=***
POST_PASSWORD_DEV=***
POST_USERNAME_MRP=***
POST_PASSWORD_MRP=***
POST_AUTHORIZATION_DEV=***
POST_AUTHORIZATION_MRP=***
POST_USER_AGENT=***

(Нужно для взаимодейтсвия с сервером ss14 посредством Post запросов [ServerApi.cs](https://github.com/AdventureTimeSS14/space_station_ADT/blob/master/Content.Server/Administration/ServerApi.cs))
POST_ADMIN_API=***
POST_ADMIN_NAME=***
POST_ADMIN_GUID=***

(Конфиг от БД ss14)
DB_HOST=***
DB_DATABASE=***
DB_USER=***
DB_PASSWORD=***
DB_PORT=***

(от MariaDB, не обязательно)
USER=***
PASSWORD=***
HOST=***
PORT=32769
DATABASE=***
```


## Запуск

### Запуск бота:
```bash
python main.py
```

### Уведомления и логирование:
- Логи о запуске, перезапуске и завершении работы отправляются в лог-канал Discord.
- Уведомления об изменениях на сервере или статусе бота.

## Полезная информация

- **Токен Discord** является конфиденциальной информацией. Не делитесь им с другими.
- Убедитесь, что у вас установлен **Python 3.10** или выше.
- Если вы столкнулись с проблемами, ознакомьтесь с документацией [Discord API](https://discord.com/developers/docs/intro).

**P.S.** Если вы нашли баг или у вас есть предложения, отправьте Pull Request или создайте Issue в репозитории.
