import disnake
import requests

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import (ADDRESS_MRP, POST_ADMIN_HEADERS,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST)


@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def admin_presets(ctx):
    """
    Команда для получения информации о доступных геймпресетах.
    Включает список всех доступных пресетов и их описание.
    """
    
    url = f"http://{ADDRESS_MRP}:1212/admin/presets"
    
    response = requests.get(url, headers=POST_ADMIN_HEADERS)

    
    # Обработка ответа
    if response.status_code == 200:
        data = response.json()

        # Создание Embed для красивого вывода
        embed = disnake.Embed(
            title="Доступные Геймпресеты",
            description="Данная команда выводит информацию о всех доступных геймпресетах на сервере.",
            color=disnake.Color.blue()
        )

        # Список пресетов
        presets = data.get("Presets", [])

        if presets:
            presets_list = []
            for preset in presets:

                # Получаем название и описание, если они существуют
                name = preset.get('ModeTitle', 'Без названия')
                description = preset.get('Description', 'Описание отсутствует')
                preset_id = preset.get('Id', 'Без ID')

                presets_list.append(f"**{name}** (ID: {preset_id}): {description}")

            # Разделение текста на части, если нужно
            def split_text(text, max_length=1024):
                """Функция для разделения текста на части, чтобы не превышать лимит символов."""
                chunks = []
                while len(text) > max_length:
                    split_idx = text.rfind("\n", 0, max_length)  # Разделить по последнему \n, чтобы не обрывать слово
                    chunks.append(text[:split_idx])
                    text = text[split_idx + 1:]
                chunks.append(text)  # Остаток
                return chunks

            # Разделяем список пресетов на части
            preset_chunks = split_text("\n".join(presets_list))

            # Добавляем все части в Embed
            for i, chunk in enumerate(preset_chunks):
                embed.add_field(name=f"Геймпресеты" if i == 0 else f"Геймпресеты (часть {i+1})", value=chunk, inline=False)
        else:
            embed.add_field(name="Геймпресеты", value="Нет доступных пресетов", inline=False)

        # Отправка Embed в канал
        await ctx.send(embed=embed)

    else:
        # Если запрос не успешен
        await ctx.send(f"Ошибка запроса: {response.status_code}, {response.text}")
