from datetime import datetime

import disnake
from disnake.ext import tasks

from bot_init import bot

# ID каналов
LOG_CHANNEL_ID = 1041654367712976966  # Канал логов ахелпов
BAN_CHANNEL_ID = 1291023511607054387  # Канал логов банов
STATIC_ADMIN_CHANNEL_ID = 1352637128961556580  # Канал для вывода статистики
EMBED_MESSAGE_ID = 1352638882310656051

# Список ников админов
ADMIN_NICKS = [
    "Pangaari", "Mina0", "kiwi_fruit", "Syrel", "Legion_159", "Estrie", "RevengenRat", "LightSurvivor", "meesooruu", 
    "Mr_NIkolos", "saint_madman", "SuperUltraGigachad", "KriTs", "Xalem", "Green_Lama", "Pushnidze", "Jmurik01", 
    "Korpraali", "Doc7", "Dark_Plague111", "maksim21612", "Daxim", "vadi_al", "moon_so_red", "WaRz", "Prunt", 
    "Shtrudel1", "Carneline", "Lokotyasha", "KOT_PILOT558", "QFci", "0Kermit0"
]

# Функция для поиска сообщений админов и обновления эмбеда
async def count_admin_actions():
    global EMBED_MESSAGE_ID
    channel_static_admin = bot.get_channel(STATIC_ADMIN_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    ban_channel = bot.get_channel(BAN_CHANNEL_ID)
    if not log_channel or not ban_channel or not channel_static_admin:
        print("Каналы не найдены!")
        return

    # Определяем диапазон дат (текущий месяц)
    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_year = today.strftime("%B %Y")  # Название месяца и год

    # Словарь для хранения количества ахелпов и банов
    admin_actions = {nick: {"ахелпы": 0, "баны": 0} for nick in ADMIN_NICKS}

    # Подсчёт ахелпов
    async for message in log_channel.history(limit=4000, after=first_day_of_month):
        for embed in message.embeds:
            for admin_nick in ADMIN_NICKS:
                if any(admin_nick.lower() in (getattr(embed, attr, "") or "").lower() for attr in ["title", "description"]):
                    admin_actions[admin_nick]["ахелпы"] += 1
                    continue
                for field in embed.fields:
                    if admin_nick.lower() in field.name.lower() or admin_nick.lower() in field.value.lower():
                        admin_actions[admin_nick]["ахелпы"] += 1
                        break

    # Подсчёт банов
    async for message in ban_channel.history(limit=4000, after=first_day_of_month):
        for embed in message.embeds:
            for admin_nick in ADMIN_NICKS:
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
        color=disnake.Color.red()
    )

    # Устанавливаем подпись (футер)
    embed.set_footer(
        text="Adventure Time SS14 MRP Server | Данные могут отличаться, точность не 100%", 
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
