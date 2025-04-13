import requests
from disnake import Color, Embed

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from commands.post_admin.utils import get_field_value
from config import (ADDRESS_MRP, POST_ADMIN_HEADERS,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST)


@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def game_rules(ctx):
    """
    Команда для получения информации о текущих правилах игры.
    Включает список доступных игровых правил на сервере SS14.
    """
    
    url = f"http://{ADDRESS_MRP}:1212/admin/game_rules"  # Измените на актуальный endpoint
    
    response = requests.get(url, headers=POST_ADMIN_HEADERS)

    
    # Обработка ответа
    if response.status_code == 200:
        data = response.json()

        # Создание Embed для красивого вывода
        embed = Embed(
            title="Игровые правила сервера SS14",
            description="Данная команда выводит список правил на сервере.",
            color=Color.green()
        )
        
        # Получаем список правил
        game_rules = get_field_value(data, ["GameRules"], default=[])
        
        # Разбиение списка на несколько частей, если он слишком длинный
        chunk_size = 10  # Максимальное количество правил в одном поле
        for i in range(0, len(game_rules), chunk_size):
            chunk = "\n".join(game_rules[i:i + chunk_size])
            embed.add_field(name=f"Правила (часть {i // chunk_size + 1})", value=chunk, inline=False)
        
        # Отправка Embed в канал
        await ctx.send(embed=embed)
        
    else:
        # Если запрос не успешен
        await ctx.send(f"Ошибка запроса: {response.status_code}, {response.text}")