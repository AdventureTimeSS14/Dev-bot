import disnake
import psycopg2
from datetime import datetime
import pytz
from bot_init import bot
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST
from commands.db_ss.setup_db_ss14_mrp import DB_USER, DB_PORT, DB_HOST, DB_PASSWORD
from commands.misc.check_roles import has_any_role_by_id

# Функция для поиска админа в базе
def fetch_admin_info(nickname, server):
    db_name = "ss14" if server.lower() == "mrp" else "ss14_dev"

    DB_PARAMS = {
        'database': db_name,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT
    }

    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT a.title, ar.name
    FROM public.admin a
    JOIN public.admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
    JOIN public.player p ON a.user_id = p.user_id
    WHERE p.last_seen_user_name ILIKE %s
    """

    cursor.execute(query, (nickname,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result  # (title, rank_name) или None

# Команда поиска админа
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def admin(ctx, nickname: str):
    """
    Проверяет, есть ли админ с таким ником в базе MRP и DEV.
    Использование: &admin <NickName>
    """

    mrp_info = fetch_admin_info(nickname, "mrp")
    dev_info = fetch_admin_info(nickname, "dev")

    if not mrp_info and not dev_info:
        embed = disnake.Embed(
            title="❌ Администратор не найден",
            description=f"**Пользователь** `{nickname}` **отсутствует в списке администраторов**.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Поиск выполнен в базах SS14 MRP & DEV", icon_url="https://i.imgur.com/6Y5xG0X.png")
        await ctx.send(embed=embed)
        return

    # Определяем текущую дату и время
    tz = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(tz)

    # Создаем эмбед с улучшенным оформлением
    embed = disnake.Embed(
        title=f"🔧 **Информация об администраторе** `{nickname}`",
        color=disnake.Color.gold(),
        timestamp=current_time
    )

    if mrp_info:
        embed.add_field(
            name="🟢 **MRP**",
            value=f"🏷 **Титул:** `{mrp_info[0]}`\n🎖 **Ранг:** `{mrp_info[1]}`",
            inline=False
        )

    if dev_info:
        if mrp_info:
            embed.add_field(name="──────────────────", value="⠀", inline=False)  # Разделитель
        embed.add_field(
            name="🔵 **DEV**",
            value=f"🏷 **Титул:** `{dev_info[0]}`\n🎖 **Ранг:** `{dev_info[1]}`",
            inline=False
        )

    embed.set_footer(text="Данные взяты из базы SS14", icon_url="https://i.imgur.com/6Y5xG0X.png")

    await ctx.send(embed=embed)
