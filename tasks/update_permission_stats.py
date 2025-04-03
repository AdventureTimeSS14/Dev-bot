from datetime import datetime

import disnake
import psycopg2
from disnake.ext import tasks

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import (DB_HOST, DB_PASSWORD, DB_PORT,
                                              DB_USER)
from commands.misc.check_roles import has_any_role_by_id
from config import MOSCOW_TIMEZONE, WHITELIST_ROLE_ID_ADMINISTRATION_POST

# Настройки БД
DB_PARAMS_SS14 = {
    'database': 'ss14',
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}

DB_PARAMS_SS14_DEV = {
    'database': 'ss14_dev',
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}

# Роли
ROLES = {
    1054908932868538449: "Руководство",
    1248667383334178902: "Администрация",
    1060191651538145420: "Разработка",
    1084143714110275614: "Мапперы",
    1155055955214614558: "Спрайтеры",
    1192426911905874152: "Медиа",
    1167921041222406306: "Сторожилы на отдыхе",
}

# Функция запроса пользователей из discord_user
def fetch_discord_users():
    conn = psycopg2.connect(**DB_PARAMS_SS14)
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id, user_id FROM public.discord_user")
    discord_users = cursor.fetchall()
    cursor.close()
    conn.close()
    return {str(d_id): u_id for d_id, u_id in discord_users}

# Функция запроса администраторов из указанной БД
def fetch_admins(db_params):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.user_id, p.last_seen_user_name, a.title, ar.name
        FROM public.admin a
        JOIN public.admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
        LEFT JOIN public.player p ON a.user_id = p.user_id
    """)
    admins = cursor.fetchall()
    cursor.close()
    conn.close()
    return {user_id: (nickname, title, rank) for user_id, nickname, title, rank in admins}

# ID сообщения для обновления
message_id = 1357300582603292874
message_id_admin = 1357300771602829424

# Задача обновления статистики раз в 12 часов
@tasks.loop(hours=12)
async def update_leaderboard():
    channel = bot.get_channel(1357300045862404266)  # 🌍▏permission-adt-team

    discord_users = fetch_discord_users()
    admins_ss14 = fetch_admins(DB_PARAMS_SS14)
    admins_ss14_dev = fetch_admins(DB_PARAMS_SS14_DEV)

    # Запрос для "Руководства"
    role_id = 1054908932868538449
    role_name = ROLES.get(role_id)
    members = [m for m in channel.guild.members if any(r.id == role_id for r in m.roles)]

    # Формируем данные для администраторов
    admin_data = []
    for member in members:
        discord_id = str(member.id)
        user_id = discord_users.get(discord_id)

        if user_id:
            mrp_status = "✅" if user_id in admins_ss14 else "❌"
            dev_status = "✅" if user_id in admins_ss14_dev else "❌"
            
            # Получаем данные из соответствующих баз
            mrp_nickname, mrp_title, mrp_rank = admins_ss14.get(user_id, ("Неизвестно", "-", "-"))
            dev_nickname, dev_title, dev_rank = admins_ss14_dev.get(user_id, ("Неизвестно", "-", "-"))

            # Используем никнейм из MRP, если он есть, иначе из DEV
            nickname = mrp_nickname if mrp_nickname != "Неизвестно" else dev_nickname
            # Используем title из MRP, если пользователь есть в MRP, иначе из DEV
            title = mrp_title if user_id in admins_ss14 else dev_title

            admin_data.append(
                {
                    "discord_name": f"<@{member.id}>",
                    "nickname": nickname,
                    "title": title,
                    "mrp_status": mrp_status,
                    "dev_status": dev_status,
                    "mrp_rank": mrp_rank if user_id in admins_ss14 else "Не установлен",
                    "dev_rank": dev_rank if user_id in admins_ss14_dev else "Не установлен",
                }
            )
        else:
            admin_data.append(
                {
                    "discord_name": f"<@{member.id}>",
                    "nickname": "Неизвестно",
                    "title": "Не привязан",
                    "mrp_status": "❌",
                    "dev_status": "❌",
                    "mrp_rank": "Не установлен",
                    "dev_rank": "Не установлен",
                }
            )

    # Сортируем по рангу на MRP (можно добавить сортировку по Dev, если требуется)
    sorted_admins = sorted(admin_data, key=lambda x: (x["mrp_rank"], x["dev_rank"]), reverse=True)

    # Формируем таблицу с отступами
    leaderboard_text = "```\n"
    for i, admin in enumerate(sorted_admins):
        leaderboard_text += (
            f"{i+1:>2}. {admin['discord_name']} | {admin['nickname']} \n"
            f"   Title: {admin['title']} \n"
            f"   Mrp: {admin['mrp_status']} ({admin['mrp_rank']}) \n"
            f"   Dev: {admin['dev_status']} ({admin['dev_rank']}) \n\n"
        )
    leaderboard_text += "```"

    # Формируем эмбед
    embed = disnake.Embed(
        title=f"📌 {role_name} - Статистика",
        description=f"**Рейтинг permission для роли {role_name}**:\n\n{leaderboard_text}",
        color=disnake.Color.gold(),
        timestamp=datetime.now(MOSCOW_TIMEZONE)
    )
    embed.set_footer(
        text="Данные из базы SS14 | Последнее обновление",
        icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
    )

    # Обновление существующего сообщения
    message = await channel.fetch_message(message_id)
    await message.edit(embed=embed)

# Задача обновления статистики раз в 12 часов
@tasks.loop(hours=12)
async def update_adminboard_perm():
    channel = bot.get_channel(1357300045862404266)  # 🌍▏permission-adt-team

    discord_users = fetch_discord_users()
    admins_ss14 = fetch_admins(DB_PARAMS_SS14)
    admins_ss14_dev = fetch_admins(DB_PARAMS_SS14_DEV)

    # Запрос для "Администрация"
    role_id = 1248667383334178902
    role_name = ROLES.get(role_id)
    members = [m for m in channel.guild.members if any(r.id == role_id for r in m.roles)]

    # Формируем данные для администраторов
    admin_data = []
    for member in members:
        discord_id = str(member.id)
        user_id = discord_users.get(discord_id)

        if user_id:
            mrp_status = "✅" if user_id in admins_ss14 else "❌"
            dev_status = "✅" if user_id in admins_ss14_dev else "❌"
            
            # Получаем данные из соответствующих баз
            mrp_nickname, mrp_title, mrp_rank = admins_ss14.get(user_id, ("Неизвестно", "-", "-"))
            dev_nickname, dev_title, dev_rank = admins_ss14_dev.get(user_id, ("Неизвестно", "-", "-"))

            # Используем никнейм из MRP, если он есть, иначе из DEV
            nickname = mrp_nickname if mrp_nickname != "Неизвестно" else dev_nickname
            # Используем title из MRP, если пользователь есть в MRP, иначе из DEV
            title = mrp_title if user_id in admins_ss14 else dev_title

            admin_data.append(
                {
                    "discord_name": f"<@{member.id}>",
                    "nickname": nickname,
                    "title": title,
                    "mrp_status": mrp_status,
                    "dev_status": dev_status,
                    "mrp_rank": mrp_rank if user_id in admins_ss14 else "Не установлен",
                    "dev_rank": dev_rank if user_id in admins_ss14_dev else "Не установлен",
                }
            )
        else:
            admin_data.append(
                {
                    "discord_name": f"<@{member.id}>",
                    "nickname": "Неизвестно",
                    "title": "Не привязан",
                    "mrp_status": "❌",
                    "dev_status": "❌",
                    "mrp_rank": "Не установлен",
                    "dev_rank": "Не установлен",
                }
            )

    # Сортируем по рангу на MRP (можно добавить сортировку по Dev, если требуется)
    sorted_admins = sorted(admin_data, key=lambda x: (x["mrp_rank"], x["dev_rank"]), reverse=True)

    # Формируем таблицу с отступами
    leaderboard_text = "```\n"
    for i, admin in enumerate(sorted_admins):
        leaderboard_text += (
            f"{i+1:>2}. {admin['discord_name']} | {admin['nickname']} \n"
            f"   Title: {admin['title']} \n"
            f"   Mrp: {admin['mrp_status']} ({admin['mrp_rank']}) \n"
            f"   Dev: {admin['dev_status']} ({admin['dev_rank']}) \n\n"
        )
    leaderboard_text += "```"

    # Формируем эмбед
    embed = disnake.Embed(
        title=f"📌 {role_name} - Статистика",
        description=f"**Рейтинг permission для роли {role_name}**:\n\n{leaderboard_text}",
        color=disnake.Color.red(),
        timestamp=datetime.now(MOSCOW_TIMEZONE)
    )
    embed.set_footer(
        text="Данные из базы SS14 | Последнее обновление",
        icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
    )

    # Обновление существующего сообщения
    message = await channel.fetch_message(message_id_admin)
    await message.edit(embed=embed)
