import disnake
from disnake.ext import tasks
from datetime import datetime
from bot_init import bot

# ID каналов
LOG_CHANNEL_ID = 1041654367712976966  # Канал логов
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
async def count_admin_messages():
    global EMBED_MESSAGE_ID
    channel_static_admin = bot.get_channel(STATIC_ADMIN_CHANNEL_ID)
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel or not channel_static_admin:
        print("Каналы не найдены!")
        return

    # Определяем диапазон дат (текущий месяц)
    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_year = today.strftime("%B %Y")  # Название месяца и год

    # Словарь для хранения количества сообщений
    admin_messages = {nick: 0 for nick in ADMIN_NICKS}

    # Поиск эмбедов по нику
    async for message in channel.history(limit=4000, after=first_day_of_month):
        for embed in message.embeds:
            # Проверяем заголовок, описание и поля эмбеда
            for admin_nick in ADMIN_NICKS:
                if (embed.title and admin_nick.lower() in embed.title.lower()) or \
                   (embed.description and admin_nick.lower() in embed.description.lower()):
                    admin_messages[admin_nick] += 1
                    continue

                # Проверяем поля эмбеда
                for field in embed.fields:
                    if admin_nick.lower() in field.name.lower() or admin_nick.lower() in field.value.lower():
                        admin_messages[admin_nick] += 1
                        break

    # Формируем текст для описания в эмбеде
    sorted_admins = sorted(admin_messages.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "\n".join(f"**{i+1}. {admin}** — {count} ахелпов" for i, (admin, count) in enumerate(sorted_admins))

    # Формируем эмбед
    embed = disnake.Embed(
        title=f"Топ активных админов за {month_year}",
        description=f"📊 **Рейтинг админов по количеству найденных ахелпов:**\n\n{leaderboard_text}",
        color=disnake.Color.green()
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
    await count_admin_messages()
