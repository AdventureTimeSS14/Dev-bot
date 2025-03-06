import disnake
import psycopg2
from datetime import datetime
import pytz
from bot_init import bot
from config import (
    WHITELIST_ROLE_ID_ADMINISTRATION_POST
)
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id

# Функция запроса данных о банах игрока
def fetch_banlist(nick_name):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT 
        sb.server_ban_id, 
        sb.ban_time, 
        sb.expiration_time, 
        sb.reason, 
        COALESCE(p.last_seen_user_name, 'Неизвестно') AS admin_nickname,
        ub.unban_time,
        COALESCE(p2.last_seen_user_name, 'Неизвестно') AS unban_admin_nickname
    FROM server_ban sb
    LEFT JOIN player p ON sb.banning_admin = p.user_id
    LEFT JOIN server_unban ub ON sb.server_ban_id = ub.ban_id
    LEFT JOIN player p2 ON ub.unbanning_admin = p2.user_id
    WHERE sb.player_user_id = (
        SELECT user_id FROM player WHERE last_seen_user_name = %s
    )
    ORDER BY sb.ban_time DESC
    """
    cursor.execute(query, (nick_name,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Команда для бота
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def banlist(ctx, *, nick_name: str):
    """
    Получает информацию о банах игрока по его нику.
    Использование: &banlist <NickName>
    """
    bans = fetch_banlist(nick_name)

    # Если банов нет
    if not bans:
        embed = disnake.Embed(
            title="🚫 Баны не найдены",
            description=f"Игрок **{nick_name}** не имеет активных банов.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    # Получаем текущее время в часовой зоне UTC+3
    tz = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(tz)

    # Подсчитываем общее количество банов
    total_bans = len(bans)

    # Создаем Embed с инфой о банах
    embed = disnake.Embed(
        title=f"🔍 Баны игрока {nick_name} (Общее количество: {total_bans})",
        color=disnake.Color.orange(),
        timestamp=current_time
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.set_footer(text=f"Информация предоставлена из БД.")

    # Добавляем поля с банами и разбанами
    for ban in bans:
        ban_id, ban_time, expiration_time, reason, admin_nickname, unban_time, unban_admin_nickname = ban
        
        ban_time_str = ban_time.strftime("%Y-%m-%d %H:%M:%S") if ban_time else "Неизвестно"
        exp_time_str = expiration_time.strftime("%Y-%m-%d %H:%M:%S") if expiration_time else "Постоянный бан"

        # Начинаем строить информацию о бане
        ban_info = (
            f"📅 **Дата бана:** `{ban_time_str}`\n"
            f"⏳ **Истекает:** `{exp_time_str}`\n"
            f"📜 **Причина:** `{reason}`\n"
            f"👮 **Админ:** `{admin_nickname}`"
        )

        # Если бан был снят
        if unban_time:
            unban_time_str = unban_time.strftime("%Y-%m-%d %H:%M:%S")
            ban_info += (
                f"\n\n✅ **Бан был снят!**\n"
                f"🕒 **Дата разбана:** `{unban_time_str}`\n"
                f"🔓 **Разбанил:** `{unban_admin_nickname}`"
            )

        embed.add_field(
            name=f"🛑 Бан ID: `{ban_id}`",
            value=ban_info,
            inline=False
        )

    await ctx.send(embed=embed)
