from datetime import datetime

import disnake
from disnake.ext import tasks

from bot_init import bot, ss14_db
from config import MOSCOW_TIMEZONE

# ID каналов
LOG_CHANNEL_ID = 1041654367712976966  # Канал логов ахелпов
BAN_CHANNEL_ID = 1291023511607054387  # Канал логов банов
STATIC_ADMIN_CHANNEL_ID = 1352637128961556580  # Канал для вывода статистики
EMBED_MESSAGE_ID = 1352638882310656051


async def get_valid_admins_with_role(guild, role_id):
    # Получаем всех админов из базы
    all_admins = ss14_db.fetch_admins()
    
    # Фильтруем только тех, у кого есть discord_id
    discord_admins = [(nick, int(discord_id)) for nick, _, _, discord_id in all_admins if discord_id]

    # Проверяем наличие роли у каждого пользователя
    role = guild.get_role(role_id)
    if not role:
        print("Роль не найдена")
        return []

    valid_admins = []
    for nick, discord_id in discord_admins:
        member = guild.get_member(discord_id)
        if member and role in member.roles:
            valid_admins.append(nick)

    return valid_admins

# Функция для поиска сообщений админов и обновления эмбеда
async def count_admin_actions():
    global EMBED_MESSAGE_ID
    channel_static_admin = bot.get_channel(STATIC_ADMIN_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    ban_channel = bot.get_channel(BAN_CHANNEL_ID)

    if not log_channel or not ban_channel or not channel_static_admin:
        print("Каналы не найдены!")
        return

    guild = log_channel.guild
    admin_nicks = await get_valid_admins_with_role(guild, role_id=1248667383334178902)

    if not admin_nicks:
        print("Нет админов с нужной ролью")
        return

    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_year = today.strftime("%B %Y")

    admin_actions = {nick: {"ахелпы": 0, "баны": 0} for nick in admin_nicks}

    async for message in log_channel.history(limit=4000, after=first_day_of_month):
        for embed in message.embeds:
            for admin_nick in admin_nicks:
                if any(admin_nick.lower() in (getattr(embed, attr, "") or "").lower() for attr in ["title", "description"]):
                    admin_actions[admin_nick]["ахелпы"] += 1
                    continue
                for field in embed.fields:
                    if admin_nick.lower() in field.name.lower() or admin_nick.lower() in field.value.lower():
                        admin_actions[admin_nick]["ахелпы"] += 1
                        break

    async for message in ban_channel.history(limit=4000, after=first_day_of_month):
        for embed in message.embeds:
            for admin_nick in admin_nicks:
                if any(admin_nick.lower() in (getattr(embed, attr, "") or "").lower() for attr in ["title", "description"]):
                    admin_actions[admin_nick]["баны"] += 1
                    continue
                for field in embed.fields:
                    if admin_nick.lower() in field.name.lower() or admin_nick.lower() in field.value.lower():
                        admin_actions[admin_nick]["баны"] += 1
                        break

    # Формируем текст для эмбеда в виде таблицы
    sorted_admins = sorted(admin_actions.items(), key=lambda x: (x[1]["ахелпы"], x[1]["баны"]), reverse=True)
    # Находим максимальную длину ника
    max_nick_length = max(len(admin) for admin in admin_actions.keys())
    # Формируем текст для лидерборда
    leaderboard_text = "```\n" + "\n".join(
        f"{i+1:>2}. {admin:<{max_nick_length}} | ахелпы {data['ахелпы']:>3} | баны {data['баны']:>3}"
        for i, (admin, data) in enumerate(sorted_admins)
    ) + "\n```"

    # Формируем эмбед
    embed = disnake.Embed(
        title=f"📊 Топ админов за {month_year}",
        description=f"**Рейтинг по ахелпам 🆘 и банам 🔨:**\n\n{leaderboard_text}",
        color=disnake.Color.red(),
        timestamp=datetime.now(MOSCOW_TIMEZONE)
    )

    # Устанавливаем подпись (футер)
    embed.set_footer(
        text="Adventure Time SS14 MRP Server | Данные могут отличаться, точность не 100% | Последнее обновление", 
        icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
    )

    # Получаем сообщение с эмбедом и редактируем его
    if EMBED_MESSAGE_ID:
        try:
            msg = await channel_static_admin.fetch_message(EMBED_MESSAGE_ID)
            await msg.edit(embed=embed)
            return
        except disnake.NotFound:
            print("Сообщение не найдено, создаем новое!")
    
    # Если нет сохраненного сообщения, создаем новое и сохраняем его ID
    new_msg = await channel_static_admin.send(embed=embed)
    EMBED_MESSAGE_ID = new_msg.id

# Запуск задачи на обновление каждые 2 часа
@tasks.loop(hours=2)
async def update_admin_stats():
    await count_admin_actions()
