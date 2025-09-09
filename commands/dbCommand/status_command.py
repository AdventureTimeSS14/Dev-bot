import sqlite3

import disnake

from bot_init import bot
from commands.dbCommand.get_sqlite_connection import get_sqlite_connection
from commands.misc.check_roles import has_any_role_by_keys
from config import LOG_CHANNEL_ID


@bot.command(name="db_status")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def db_status(ctx):
    """
    Проверяет состояние локальной базы данных SQLite.
    """
    conn = None
    cursor = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()

        # Быстрый ping-запрос
        cursor.execute("SELECT 1")
        _ = cursor.fetchone()

        embed = disnake.Embed(
            title="Статус БД",
            description="Успешное подключение к базе данных SQLite.",
            color=disnake.Color.green(),
        )
        embed.add_field(name="Версия SQLite", value=sqlite3.sqlite_version, inline=False)

        await ctx.send(embed=embed)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"✅ SQLite доступна. Запрошено пользователем: {ctx.author}.\n_ _"
            )

    except Exception as e:
        embed = disnake.Embed(
            title="Ошибка",
            description="Не удалось подключиться к базе данных SQLite.",
            color=disnake.Color.red(),
        )
        embed.add_field(name="Детали ошибки", value=str(e), inline=False)
        await ctx.send(embed=embed)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Ошибка подключения к SQLite: {e}. Запрошено пользователем: {ctx.author}.\n_ _"
            )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
