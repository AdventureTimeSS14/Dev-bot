import disnake
import sqlite3

from bot_init import bot
from commands.dbCommand.get_sqlite_connection import get_sqlite_connection
from commands.misc.check_roles import has_any_role_by_keys
from config import LOG_CHANNEL_ID

COLOR = disnake.Color.dark_purple()


@bot.command(name="db_info")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def db_info(ctx):
    """
    Информация о базе данных SQLite (vacations.sqlite3).
    """
    conn = None
    cursor = None
    try:
        # Соединение с SQLite
        conn = get_sqlite_connection()
        cursor = conn.cursor()

        avatar_url = ctx.author.avatar.url if ctx.author.avatar else None
        embed = disnake.Embed(
            title="Информация о базе данных",
            description="Подключение к локальной базе данных SQLite выполнено успешно!",
            color=COLOR,
        )
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)

        # Версия SQLite (библиотеки)
        embed.add_field(name="Версия SQLite", value=sqlite3.sqlite_version, inline=False)

        # Список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        if tables:
            embed.add_field(name="Список таблиц", value="\n".join(tables), inline=False)
        else:
            embed.add_field(name="Список таблиц", value="В базе данных нет таблиц.", inline=False)

        # Пример статистики по таблице vacation_team
        if "vacation_team" in tables:
            cursor.execute("SELECT COUNT(1) FROM vacation_team")
            total = cursor.fetchone()[0]
            embed.add_field(name="vacation_team: записей", value=str(total), inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        error_embed = disnake.Embed(
            title="Ошибка",
            description=f"Произошла непредвиденная ошибка: {e}",
            color=disnake.Color.red(),
        )
        await ctx.send(embed=error_embed)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Непредвиденная ошибка при выполнении команды db_info: {e}. "
                f"Запрошено пользователем {ctx.author}.\n_ _"
            )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
