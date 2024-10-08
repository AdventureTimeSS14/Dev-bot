[![Deploy Discord Bot](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/AdventureTimeSS14/Dev-bot/actions/workflows/deploy.yml)

## Дискорд бот от разработки Adventure Time: Установка и Запуск

Этот бот разработан командой Adventure Time SS14 в **образовательных целях** для изучения и тестирования возможностей Discord API и разработки ботов. **Он не предназначен для коммерческого использования.**

**Этот бот использует библиотеку g4f исключительно для демонстрационных и образовательных целей.**

**Мы придерживаемся всех правил Discord и несем полную ответственность за его использование.**

### 1. Клонирование репозитория:
```shell
git clone https://github.com/AdventureTimeSS14/Dev-bot.git
```
### 2. Установка зависимостей:
```shell
cd Dev-bot
pip install -r requirements.txt
```

### 3. Создание конфигурационного файла:

Создайте файл .env рядом с main.py и вставьте в него свой токен Discord, PROXY и GITHUB:

```.env
 DISCORD_KEY=*****
 PROXY=*****
 GITHUB=*****
```
 

### 4. Запуск бота:
```shell
python main.py
```

### Важно:

- Токен Discord является конфиденциальной информацией. Не делитесь им с другими.
- Убедитесь, что у вас есть установленный Python и pip.
- Если вы столкнулись с проблемами, ознакомьтесь с документацией Discord API.

### Дополнительные замечания:

- Этот бот может быть использован для различных задач, и в будущем будет дорабатываться.
