import disnake
import requests

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from commands.post_admin.utils import get_field_value
from config import (ADDRESS_MRP, POST_ADMIN_HEADERS,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)


@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)
async def admin_info(ctx):
    """
    Команда для получения информации о текущем состоянии администраторского интерфейса.
    Включает данные о текущей игре, игроках, настроенных правилах и других параметрах.
    """

    url = f"http://{ADDRESS_MRP}:1212/admin/info"

    response = requests.get(url, headers=POST_ADMIN_HEADERS)

    # Логируем полный ответ для отладки
    # print(f"Response Status Code: {response.status_code}")
    # print(f"Response Text: {response.text}")

    if response.status_code == 200:
        data = response.json()

        embed = disnake.Embed(
            title="Информация о сервере SS14",
            description="Данная команда выводит информацию о текущем состоянии сервера Mrp в подробном виде SS14.",
            color=disnake.Color.blue()
        )

        # Основные данные
        embed.add_field(name="ID Раунда", value=get_field_value(data, ["RoundId"]), inline=False)
        embed.add_field(name="Название карты", value=get_field_value(data, ["Map", "Name"]), inline=False)
        embed.add_field(name="MOTD (Сообщение дня)", value=get_field_value(data, ["MOTD"], default="Нет сообщения"), inline=False)
        embed.add_field(name="Геймпресет", value=get_field_value(data, ["GamePreset"]), inline=False)
        
        # Обработка списка игроков
        players = data.get("Players", [])

        def format_player(player):
            """Форматирование информации об игроке, убирая 'Null' у AdminTitle."""
            role = "Админ" if player["IsAdmin"] else "Игрок"
            ping = f"({player['PingUser']} ms)" if "PingUser" in player else ""

            # Проверяем, что AdminTitle не "Null" (как строка) и не пустой
            admin_title = f" ({player['AdminTitle']})" if player.get("AdminTitle") and player["AdminTitle"] != "Null" else ""

            return f"**{player['Name']}** - {role}{admin_title} {ping}".strip()

        if players:
            player_list = [format_player(p) for p in players if not p["IsDeadminned"]]
            deadminned_list = [format_player(p) for p in players if p["IsDeadminned"]]

            def split_list(lst, max_length=1024):
                """Разбивает длинный список строк на части, чтобы не превышать лимит Discord."""
                chunks, chunk = [], ""
                for item in lst:
                    if len(chunk) + len(item) + 1 > max_length:
                        chunks.append(chunk)
                        chunk = item
                    else:
                        chunk += f"\n{item}"
                if chunk:
                    chunks.append(chunk)
                return chunks

            # Добавляем игроков
            for i, chunk in enumerate(split_list(player_list)):
                embed.add_field(name="Игроки на сервере" if i == 0 else f"Игроки (часть {i+1})", value=chunk, inline=False)

            # Добавляем деадминов
            for i, chunk in enumerate(split_list(deadminned_list)):
                embed.add_field(name="Игроки в деадмине" if i == 0 else f"Деадмины (часть {i+1})", value=chunk, inline=False)
        else:
            embed.add_field(name="Игроки на сервере", value="Нет игроков", inline=False)

        # Активные администраторы
        active_admins = [format_player(p) for p in players if p["IsAdmin"] and not p["IsDeadminned"]]
        embed.add_field(name="Активные администраторы", value="\n".join(active_admins) if active_admins else "Нет активных администраторов", inline=False)

        # Правила игры
        game_rules = get_field_value(data, ["GameRules"], default="Нет доступных правил")
        game_rules_text = "\n".join(game_rules) if isinstance(game_rules, list) else game_rules
        for i, chunk in enumerate(split_list([game_rules_text])):
            embed.add_field(name="Правила игры" if i == 0 else f"Правила (часть {i+1})", value=chunk, inline=False)

        # Паника (Panic Bunker)
        panic_bunker_info = data.get("PanicBunker", {})
        panic_status = "\n".join(f"{key}: {value}" for key, value in panic_bunker_info.items() if value is not None) if panic_bunker_info else "Не активирован"
        embed.add_field(name="Panic Bunker", value=panic_status, inline=False)
        
        await ctx.send(embed=embed)
        
    else:
        await ctx.send(f"Ошибка запроса: {response.status_code}, {response.text}")
