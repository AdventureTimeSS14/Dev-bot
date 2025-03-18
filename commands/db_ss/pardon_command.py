from datetime import datetime

import disnake
import psycopg2
import pytz

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST


# Функция для получения user_id по discord_id
def get_user_id_by_discord_id(discord_id: str):
    """
    Ищет user_id по discord_id в таблице discord_user.

    :param discord_id: Идентификатор Discord пользователя.
    :return: user_id, если найден, иначе None.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM discord_user WHERE discord_id = %s", (discord_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None

# Функция проверки, является ли user_id администратором
def is_admin(user_id: int):
    """
    Проверяет, является ли user_id администратором.

    :param user_id: ID пользователя в игре.
    :return: True, если пользователь администратор, иначе False.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM admin WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None


def pardon_ban(ban_id, admin_user_id):
    """
    Функция для снятия бана с указанного ID.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # Проверяем, существует ли бан с таким ID
    cursor.execute("SELECT 1 FROM server_ban WHERE server_ban_id = %s", (ban_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return False, f"❌ Ошибка: Бан с ID `{ban_id}` не существует."

    # Проверяем, был ли уже снят бан
    cursor.execute("SELECT 1 FROM server_unban WHERE ban_id = %s", (ban_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, f"⚠️ Бан с ID `{ban_id}` уже был снят ранее."

    # Получаем last_seen_user_name (имя последнего входа администратора)
    cursor.execute(
        "SELECT last_seen_user_name FROM player WHERE user_id = %s",
        (admin_user_id,)
    )
    admin_data = cursor.fetchone()

    if not admin_data:
        cursor.close()
        conn.close()
        return False, ("❌ Ошибка: Администратор с user_id "
                       f"`{admin_user_id}` не найден в базе игроков."
                        )

    admin_name = admin_data[0]  # last_seen_user_name администратора

    # Получаем текущее время в часовом поясе Europe/Moscow
    tz = pytz.timezone("Europe/Moscow")
    unban_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " +0300"

    # Вставляем новую запись в server_unban
    cursor.execute(
        """
        INSERT INTO server_unban (ban_id, unbanning_admin, unban_time)
        VALUES (%s, %s, %s::timestamptz)
        """,
        (ban_id, admin_user_id, unban_time)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return True, f"✅ Бан с ID `{ban_id}` успешно снят администратором `{admin_name}`."


# Команда для Discord-бота
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def pardon(ctx, ban_id: int):
    """
    Разбанивает игрока по ID бана.
    Использование: &pardon <ban_id>
    """
    discord_id = str(ctx.author.id)

    # Проверяем привязку Discord-аккаунта
    user_id = get_user_id_by_discord_id(discord_id)
    if not user_id:
        await ctx.send(
            "⚠️ Ваш дискорд-аккаунт не привязан к игровому. "
            "Пожалуйста, привяжите его здесь: "
            "https://discord.com/channels/901772674865455115/1351213738774237184"
        )
        return

    # Проверяем, является ли пользователь администратором
    if not is_admin(user_id):
        await ctx.send("❌ Ошибка: Вы не являетесь администратором в базе МРП.")
        return

    # Выполняем разбан
    success, message = pardon_ban(ban_id, user_id)

    # Создаем Embed для ответа
    color = disnake.Color.green() if success else disnake.Color.red()
    embed = disnake.Embed(
        title="🔓 Разбан игрока",
        description=message,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_author(
        name=ctx.author.display_name,
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    embed.set_footer(text="Операция выполнена через БД.")

    await ctx.send(embed=embed)
