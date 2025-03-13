import disnake
import psycopg2
from datetime import datetime
import pytz
from bot_init import bot
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST, POST_ADMIN_NAME
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id

# Фиксированный админ, который выполняет разбан
UNBANNING_ADMIN = POST_ADMIN_NAME

# Функция разбана
def pardon_ban(ban_id, adminName):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # Проверяем, существует ли бан с таким ban_id в таблице server_ban
    cursor.execute("SELECT 1 FROM server_ban WHERE server_ban_id = %s", (ban_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return False, f"❌ Ошибка: Бан с ID `{ban_id}` не существует."

    # Получаем user_id разбанивающего админа
    cursor.execute(
        "SELECT user_id FROM player WHERE last_seen_user_name = %s",
        (adminName,)
    )
    admin_result = cursor.fetchone()

    if not admin_result:
        cursor.close()
        conn.close()
        return False, f"❌ Ошибка: администратор `{adminName}` не найден в БД."

    unbanning_admin_id = admin_result[0]

    # Проверяем, есть ли уже разбан
    cursor.execute("SELECT 1 FROM server_unban WHERE ban_id = %s", (ban_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, f"⚠️ Бан с ID `{ban_id}` уже был снят ранее."

    # Получаем текущее время в часовом поясе Europe/Moscow
    tz = pytz.timezone("Europe/Moscow")
    unban_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " +0300"

    # Вставляем новую запись в server_unban
    cursor.execute(
        """
        INSERT INTO server_unban (ban_id, unbanning_admin, unban_time)
        VALUES (%s, %s, %s::timestamptz)
        """,
        (ban_id, unbanning_admin_id, unban_time)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return True, f"✅ Бан с ID `{ban_id}` успешно снят администратором `{adminName}`."

# Команда для Discord-бота
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def pardon(ctx, ban_id: int, adminName: str = UNBANNING_ADMIN):
    """
    Разбанивает игрока по ID бана.
    Использование: &pardon <ban_id>
    """
    success, message = pardon_ban(ban_id, adminName)

    # Создаем Embed для ответа
    color = disnake.Color.green() if success else disnake.Color.red()
    embed = disnake.Embed(
        title="🔓 Разбан игрока",
        description=message,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.set_footer(text="Операция выполнена через БД.")

    await ctx.send(embed=embed)
