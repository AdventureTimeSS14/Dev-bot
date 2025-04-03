from datetime import datetime

import disnake
import psycopg2
from disnake.ext import tasks

from bot_init import bot, ss14_db
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


async def update_role_stats(role_id: int, message_id: int, embed_color: disnake.Color):
    """
    Обновляет статистику для указанной роли
    """
    channel = bot.get_channel(1357300045862404266)  # 🌍️🛏permission-adt-team
    if not channel:
        print(f"Канал не найден: {channel}")
        return

    discord_users = fetch_discord_users()
    admins_ss14 = fetch_admins(DB_PARAMS_SS14)
    admins_ss14_dev = fetch_admins(DB_PARAMS_SS14_DEV)

    role_name = ROLES.get(role_id, "Неизвестная роль")
    members = [m for m in channel.guild.members if any(r.id == role_id for r in m.roles)]

    # Формируем данные для администраторов
    admin_data = []
    for member in members:
        discord_id = str(member.id)
        user_id = discord_users.get(discord_id)

        if user_id:
            mrp_status = "✅" if user_id in admins_ss14 else None
            dev_status = "✅" if user_id in admins_ss14_dev else None

            mrp_nickname, mrp_title, mrp_rank = admins_ss14.get(user_id, (None, None, None))
            dev_nickname, dev_title, dev_rank = admins_ss14_dev.get(user_id, (None, None, None))

            nickname = mrp_nickname or dev_nickname or ss14_db.get_username_by_user_id(user_id)
            title = mrp_title or dev_title or None
            mrp_rank = mrp_rank if mrp_status else None
            dev_rank = dev_rank if dev_status else None
        else:
            nickname = None
            title = None
            mrp_status = None
            dev_status = None
            mrp_rank = None
            dev_rank = None

        admin_data.append({
            "discord_name": f"<@{member.id}>" if nickname else None,
            "discord_id": str(member.id),
            "nickname": nickname,
            "title": title,
            "mrp_status": mrp_status,
            "dev_status": dev_status,
            "mrp_rank": mrp_rank,
            "dev_rank": dev_rank,
        })

    # Сортируем и фильтруем список
    sorted_admins = sorted(
        admin_data,
        key=lambda x: (x["mrp_rank"] or "", x["dev_rank"] or ""),
        reverse=True
    )

    # Формируем таблицу
    leaderboard_text = "```\n"
    for i, admin in enumerate(sorted_admins):
        if admin["nickname"]:
            leaderboard_text += f"{i+1:>2}. {admin['discord_name']} | {admin['nickname']}\n"
            if admin["title"]:
                leaderboard_text += f"   Title: {admin['title']}\n"
            if admin["mrp_status"]:
                leaderboard_text += f"   Mrp: {admin['mrp_status']} ({admin['mrp_rank']})\n"
            if admin["dev_status"]:
                leaderboard_text += f"   Dev: {admin['dev_status']} ({admin['dev_rank']})\n"
        else:
            leaderboard_text += f"{i+1:>2}. ID: {admin['discord_id']} - не привязан\n"
        leaderboard_text += "\n"
    leaderboard_text += "```"

    # Создаем эмбед
    embed = disnake.Embed(
        title=f"📌 {role_name} - Статистика",
        description=f"**Рейтинг permission для роли {role_name}**:\n\n{leaderboard_text[:4000]}",
        color=embed_color,
        timestamp=datetime.now(MOSCOW_TIMEZONE)
    )
    embed.set_footer(
        text="Данные из базы SS14 | Последнее обновление",
        icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
    )

    # Обновляем сообщение
    try:
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)
    except Exception as e:
        print(f"Ошибка при обновлении сообщения {message_id}: {e}")



# Конфигурация ролей и их параметров
ROLES_CONFIG = [
    {
        "role_id": 1054908932868538449,
        "role_name": "Руководство",
        "message_id": 1357323324174373055,
        "color": disnake.Color.gold()
    },
    {
        "role_id": 1248667383334178902,
        "role_name": "Администрация",
        "message_id": 1357324171880693780,
        "color": disnake.Color.red()
    },
    {
        "role_id": 1060191651538145420,
        "role_name": "Разработка",
        "message_id": 1357324253598322850,
        "color": disnake.Color.green()
    },
    {
        "role_id": 1084143714110275614,
        "role_name": "Мапперы",
        "message_id": 1357324861327802399,
        "color": disnake.Color.yellow()
    },
    {
        "role_id": 1155055955214614558,
        "role_name": "Спрайтеры",
        "message_id": 1357326482556588103,
        "color": disnake.Color.purple()
    },
    {
        "role_id": 1084840645790814310,
        "role_name": "Вики",
        "message_id": 1357326533420781841,
        "color": disnake.Color.blue()
    },
    {
        "role_id": 1192426911905874152,
        "role_name": "Медиа",
        "message_id": 1357326883309490176,
        "color": disnake.Color.red()
    },
    {
        "role_id": 1167921041222406306,
        "role_name": "Сторожилы",
        "message_id": 1357326950225543298,
        "color": disnake.Color.dark_grey()
    }
]

# Глобальный словарь ролей для быстрого доступа
ROLES = {item["role_id"]: item["role_name"] for item in ROLES_CONFIG}

# Задача обновления статистики для всех ролей
@tasks.loop(hours=12)
async def update_permission_stats():
    for role_config in ROLES_CONFIG:
        try:
            await update_role_stats(
                role_id=role_config["role_id"],
                message_id=role_config["message_id"],
                embed_color=role_config["color"]
            )
            print(f"Статистика для роли {role_config['role_name']} успешно обновлена")
        except Exception as e:
            print(f"Ошибка при обновлении статистики для роли {role_config['role_name']}: {e}")


# # Задача обновления
# @tasks.loop(hours=12)
# async def update_permission_stats():
#     await update_role_stats(
#         role_id=1054908932868538449,  # Руководство
#         message_id=message_id_head,
#         embed_color=disnake.Color.gold()
#     )
    
#     await update_role_stats(
#         role_id=1248667383334178902,  # Администрация
#         message_id=message_id_admin,
#         embed_color=disnake.Color.red()
#     )



# # Задача обновления статистики раз в 12 часов
# @tasks.loop(hours=12)
# async def update_leaderboard():
#     channel = bot.get_channel(1357300045862404266)  # 🌍▏permission-adt-team

#     discord_users = fetch_discord_users()
#     admins_ss14 = fetch_admins(DB_PARAMS_SS14)
#     admins_ss14_dev = fetch_admins(DB_PARAMS_SS14_DEV)

#     # Запрос для "Руководства"
#     role_id = 1054908932868538449
#     role_name = ROLES.get(role_id)
#     members = [m for m in channel.guild.members if any(r.id == role_id for r in m.roles)]

#     # Формируем данные для администраторов
#     admin_data = []
#     for member in members:
#         discord_id = str(member.id)
#         user_id = discord_users.get(discord_id)

#         if user_id:
#             mrp_status = "✅" if user_id in admins_ss14 else "❌"
#             dev_status = "✅" if user_id in admins_ss14_dev else "❌"
            
#             # Получаем данные из соответствующих баз
#             mrp_nickname, mrp_title, mrp_rank = admins_ss14.get(user_id, ("Неизвестно", "-", "-"))
#             dev_nickname, dev_title, dev_rank = admins_ss14_dev.get(user_id, ("Неизвестно", "-", "-"))

#             # Используем никнейм из MRP, если он есть, иначе из DEV
#             nickname = mrp_nickname if mrp_nickname != "Неизвестно" else dev_nickname
#             # Используем title из MRP, если пользователь есть в MRP, иначе из DEV
#             title = mrp_title if user_id in admins_ss14 else dev_title

#             admin_data.append(
#                 {
#                     "discord_name": f"<@{member.id}>",
#                     "nickname": nickname,
#                     "title": title,
#                     "mrp_status": mrp_status,
#                     "dev_status": dev_status,
#                     "mrp_rank": mrp_rank if user_id in admins_ss14 else "Не установлен",
#                     "dev_rank": dev_rank if user_id in admins_ss14_dev else "Не установлен",
#                 }
#             )
#         else:
#             admin_data.append(
#                 {
#                     "discord_name": f"<@{member.id}>",
#                     "nickname": "Неизвестно",
#                     "title": "Не привязан",
#                     "mrp_status": "❌",
#                     "dev_status": "❌",
#                     "mrp_rank": "Не установлен",
#                     "dev_rank": "Не установлен",
#                 }
#             )

#     # Сортируем по рангу на MRP (можно добавить сортировку по Dev, если требуется)
#     sorted_admins = sorted(admin_data, key=lambda x: (x["mrp_rank"], x["dev_rank"]), reverse=True)

#     # Формируем таблицу с отступами
#     leaderboard_text = "```\n"
#     for i, admin in enumerate(sorted_admins):
#         leaderboard_text += (
#             f"{i+1:>2}. {admin['discord_name']} | {admin['nickname']} \n"
#             f"   Title: {admin['title']} \n"
#             f"   Mrp: {admin['mrp_status']} ({admin['mrp_rank']}) \n"
#             f"   Dev: {admin['dev_status']} ({admin['dev_rank']}) \n\n"
#         )
#     leaderboard_text += "```"

#     # Формируем эмбед
#     embed = disnake.Embed(
#         title=f"📌 {role_name} - Статистика",
#         description=f"**Рейтинг permission для роли {role_name}**:\n\n{leaderboard_text}",
#         color=disnake.Color.gold(),
#         timestamp=datetime.now(MOSCOW_TIMEZONE)
#     )
#     embed.set_footer(
#         text="Данные из базы SS14 | Последнее обновление",
#         icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
#     )

#     # Обновление существующего сообщения
#     message = await channel.fetch_message(message_id)
#     await message.edit(embed=embed)

# # Задача обновления статистики раз в 12 часов
# @tasks.loop(hours=12)
# async def update_adminboard_perm():
#     channel = bot.get_channel(1357300045862404266)  # 🌍▏permission-adt-team

#     discord_users = fetch_discord_users()
#     admins_ss14 = fetch_admins(DB_PARAMS_SS14)
#     admins_ss14_dev = fetch_admins(DB_PARAMS_SS14_DEV)

#     # Запрос для "Администрация"
#     role_id = 1248667383334178902
#     role_name = ROLES.get(role_id)
#     members = [m for m in channel.guild.members if any(r.id == role_id for r in m.roles)]

#     # Формируем данные для администраторов
#     admin_data = []
#     for member in members:
#         discord_id = str(member.id)
#         user_id = discord_users.get(discord_id)

#         if user_id:
#             mrp_status = "✅" if user_id in admins_ss14 else "❌"
#             dev_status = "✅" if user_id in admins_ss14_dev else "❌"
            
#             # Получаем данные из соответствующих баз
#             mrp_nickname, mrp_title, mrp_rank = admins_ss14.get(user_id, ("Неизвестно", "-", "-"))
#             dev_nickname, dev_title, dev_rank = admins_ss14_dev.get(user_id, ("Неизвестно", "-", "-"))

#             # Используем никнейм из MRP, если он есть, иначе из DEV
#             nickname = mrp_nickname if mrp_nickname != "Неизвестно" else dev_nickname
#             # Используем title из MRP, если пользователь есть в MRP, иначе из DEV
#             title = mrp_title if user_id in admins_ss14 else dev_title

#             admin_data.append(
#                 {
#                     "discord_name": f"<@{member.id}>",
#                     "nickname": nickname,
#                     "title": title,
#                     "mrp_status": mrp_status,
#                     "dev_status": dev_status,
#                     "mrp_rank": mrp_rank if user_id in admins_ss14 else "Не установлен",
#                     "dev_rank": dev_rank if user_id in admins_ss14_dev else "Не установлен",
#                 }
#             )
#         else:
#             admin_data.append(
#                 {
#                     "discord_name": f"<@{member.id}>",
#                     "nickname": "Неизвестно",
#                     "title": "Не привязан",
#                     "mrp_status": "❌",
#                     "dev_status": "❌",
#                     "mrp_rank": "Не установлен",
#                     "dev_rank": "Не установлен",
#                 }
#             )

#     # Сортируем по рангу на MRP (можно добавить сортировку по Dev, если требуется)
#     sorted_admins = sorted(admin_data, key=lambda x: (x["mrp_rank"], x["dev_rank"]), reverse=True)

#     # Формируем таблицу с отступами
#     leaderboard_text = "```\n"
#     for i, admin in enumerate(sorted_admins):
#         leaderboard_text += (
#             f"{i+1:>2}. {admin['discord_name']} | {admin['nickname']} \n"
#             f"   Title: {admin['title']} \n"
#             f"   Mrp: {admin['mrp_status']} ({admin['mrp_rank']}) \n"
#             f"   Dev: {admin['dev_status']} ({admin['dev_rank']}) \n\n"
#         )
#     leaderboard_text += "```"

#     # Формируем эмбед
#     embed = disnake.Embed(
#         title=f"📌 {role_name} - Статистика",
#         description=f"**Рейтинг permission для роли {role_name}**:\n\n{leaderboard_text}",
#         color=disnake.Color.red(),
#         timestamp=datetime.now(MOSCOW_TIMEZONE)
#     )
#     embed.set_footer(
#         text="Данные из базы SS14 | Последнее обновление",
#         icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
#     )

#     # Обновление существующего сообщения
#     message = await channel.fetch_message(message_id_admin)
#     await message.edit(embed=embed)
