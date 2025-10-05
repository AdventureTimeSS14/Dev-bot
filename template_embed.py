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