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