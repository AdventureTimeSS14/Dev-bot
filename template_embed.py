embed_status = {
   "title": "Статус сервера",
    "color": 0x00ff00,
    "fields": [
        {"name": "Название", "value": "data['name']", "inline": False},
        {"name": "Игроки", "value": "data['players']", "inline": False},
        {"name": "Максимум игроков", "value": "data['soft_max_players']", "inline": False},
        {"name": "Карта", "value": "data['map']", "inline": False},
        {"name": "Статус", "value": "'Раунд идёт' if data['run_level'] == 1 else 'Неизвестно'", "inline": False},
        {"name": "Раунд ID", "value": "data['round_id']", "inline": False},
        {"name": "Режим", "value": "data['preset']", "inline": False},
        {"name": "Бункер", "value": "data['panic_bunker']", "inline": False}
    ]
}

embed_log = {
    "title": "Использование команды",
    "color": 0x0099ff,
    "fields": [
        {"name": "Команда", "value": "ctx.command", "inline": False},
        {"name": "Пользователь", "value": "ctx.author", "inline": False},
        {"name": "ID пользователя", "value": "ctx.author.id", "inline": False},
        {"name": "Время", "value": "datetime.now().strftime('%Y-%m-%d %H:%M:%S')", "inline": False},
        {"name": "Использованная команда", "value": "ctx.message.jump_url", "inline": False}
    ]
}

embed_publish_status = {
    "title": "Статус workflow publish-adt.yml",
    "fields": [
        {"name": "Статус", "value": "translated_status", "inline": False},
        {"name": "Ветка", "value": "branch", "inline": False},
        {"name": "Пользователь", "value": "user", "inline": False}
    ]
}

embed_repoinfo = {
    "title": "Общая информация о репозитории space_station_ADT",
    "description": "data['description']",
    "color": 0x00ff00,
    "fields": [
        {"name": "Звёзды", "value": "str(data['stargazers_count'])", "inline": False},
        {"name": "Форки", "value": "str(data['forks_count'])", "inline": False},
        {"name": "Issues", "value": "str(data['open_issues_count'])", "inline": False},
        {"name": "Открытые PR", "value": "str(pr_count)", "inline": False},
        {"name": "Контрибьютеры", "value": "str(contrib_count)", "inline": False},
        {"name": "Создан", "value": "data['created_at'][:10]", "inline": False},
        {"name": "Обновлён", "value": "data['updated_at'][:10]", "inline": False},
        {"name": "Ссылка", "value": "data['html_url']", "inline": False}
    ]
}

embed_git_team = {
    "title": "Участники организации AdventureTimeSS14",
    "color": 0x00ff00,
    "fields": [
        {"name": "Участники", "value": "'\\n'.join([m['login'] for m in members]) or 'Нет'", "inline": False}
    ]
}

embed_branch = {
    "title": "Ветки репозитория space_station_ADT",
    "color": 0x00ff00,
    "fields": [
        {"name": "Ветки", "value": "'\\n\\n'.join([b['name'] for b in branches]) or 'Нет веток'", "inline": False}
    ]
}

embed_git_invite = {
    "title": "Результат приглашения в организацию AdventureTimeSS14",
    "color": 0x00ff00,
    "fields": [
        {"name": "Пользователь", "value": "username", "inline": False},
        {"name": "Статус", "value": "result", "inline": False}
    ]
}

embed_git_remove = {
    "title": "Результат удаления из организации AdventureTimeSS14",
    "color": 0x00ff00,
    "fields": [
        {"name": "Пользователь", "value": "username", "inline": False},
        {"name": "Статус", "value": "result", "inline": False}
    ]
}

embed_git_help = {
    "title": "Список Git-команд бота",
    "color": 0x0099ff,
    "description": "Префикс: `&`",
    "fields": [
        {"name": "&publish <branch>. По умолчанию master", "value": "Отправляет запрос на паблиш ветки.", "inline": False},
        {"name": "&publish_status", "value": "Показывает статус последнего запуска GitHub Actions workflow publish-adt.yml.", "inline": False},
        {"name": "&update <mrp/dev>. По умолчанию mrp", "value": "Обновляет сервер.", "inline": False},
        {"name": "&restart <mrp/dev>. По умолчанию mrp", "value": "Перезагружает сервер.", "inline": False},
        {"name": "&git_repoinfo", "value": "Показывает информацию о репозитории.", "inline": False},
        {"name": "&git_team", "value": "Показывает участников организации AdventureTimeSS14.", "inline": False},
        {"name": "&git_invite <username>", "value": "Приглашает пользователя в организацию.", "inline": False},
        {"name": "&git_remove <username>", "value": "Удаляет пользователя из организации.", "inline": False},
        {"name": "&add_maint <username>", "value": "Добавляет участника в команду adt_maintainer.", "inline": False},
        {"name": "&del_maint <username>", "value": "Удаляет участника из команды adt_maintainer.", "inline": False},
        {"name": "&branch", "value": "Показывает список веток репозитория.", "inline": False},
    ]
}

embed_admin_info = {
    "title": "Информация о сервере SS14",
    "color": 0x3498db,
    "fields": [
        {"name": "ID Раунда", "value": 'data.get("RoundId", "Не задано")', "inline": False},
        {"name": "Название карты", "value": 'data.get("Map", {}).get("Name", "Не задано")', "inline": False},
        {"name": "MOTD", "value": 'data.get("MOTD", "Нет сообщения")', "inline": False},
        {"name": "Геймпресет", "value": 'data.get("GamePreset", "Не задано")', "inline": False},
        {"name": "Игроки", "value": '"\\n".join([f"{p.get(\"Name\", \"?\")} - {\"Админ\" if p.get(\"IsAdmin\") else \"Игрок\"} ({p.get(\"PingUser\", \"?\")} ms)" for p in data.get("Players", []) if not p.get("IsDeadminned")]) or "Нет игроков"', "inline": False},
        {"name": "Деадмины", "value": '"\\n".join([f"{p.get(\"Name\", \"?\")} ({p.get(\"PingUser\", \"?\")} ms)" for p in data.get("Players", []) if p.get("IsDeadminned")]) or "Нет"', "inline": False},
        {"name": "Активные админы", "value": '"\\n".join([f"{p.get(\"Name\", \"?\")}" for p in data.get("Players", []) if p.get("IsAdmin") and not p.get("IsDeadminned")]) or "Нет"', "inline": False},
        {"name": "Правила игры", "value": '"\\n".join(data.get("GameRules", [])) or "Нет правил"', "inline": False},
        {"name": "Panic Bunker", "value": '"\\n".join([f"{k}: {v}" for k, v in data.get("PanicBunker", {}).items() if v is not None]) or "Не активирован"', "inline": False},
    ]
}

embed_admin_help = {
    "title": "Список админ-команд бота",
    "color": 0xFF0000,
    "description": "Префикс: `&`",
    "fields": [
        {"name": "Управление правами", "value": '&admin <nickname> — Проверка прав админа.\n&add_permission <username> \"<title>\" \"<permission>\" <server> — Добавить права на сервере DEV/MRP.\n&del_permission <username> <server> — Удалить права на сервере DEV/MRP.\n&tweak_permission <username> \"<title>\" \"<permission>\" <server> — Изменить права на сервере DEV/MRP.', "inline": False},
        {"name": "Информация о игроке", "value": '&check_nick <nickname> — Проверка на мультиаккаунт.\n&get_ckey <Discord id> — Получить ckey по ID дискорда.\n&notelist <nickname> — Заметки игрока.\n&banlist <nickname> — Банлист игрока.', "inline": False},
        {"name": "Баны и модерация", "value": '&ban <nickname> \"<reason>\" <time> в минутах — Выдает бан игроку.\n&kick <nickname> \"<reason>\" — Кик.\n&pardon <ban_id> — Разбанивает игрока.', "inline": False},
        {"name": "Сервер", "value": '&status <mrp/dev> (по умолчанию mrp) - Информация о сервере\n&admin_info — Подробная информация о сервере.\n&bunker <on/off> — Включает/выключает бункер.\n&restart <server> — Рестарт сервера.', "inline": False},
    ]
}