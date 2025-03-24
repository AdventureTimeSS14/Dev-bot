import disnake
import mariadb

from bot_init import bot
from commands.dbCommand.get_db_connection import get_db_connection
from commands.misc.check_roles import has_any_role_by_id
from config import LOG_CHANNEL_ID, WHITELIST_ROLE_ID_ADMINISTRATION_POST


@bot.command(name="db_status")
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def db_status(ctx):
    """
    Команда для проверки состояния подключения к базе данных MariaDB.
    """
    conn = None
    try:
        # Подключаемся к базе данных
        conn = get_db_connection()

        # Создаем embed для успешного подключения
        embed = disnake.Embed(
            title="Статус БД",
            description="Успешно подключено к базе данных MariaDB!",
            color=disnake.Color.green(),
        )
        embed.add_field(
            name="Статус сервера",
            value="Соединение открыто" if conn.open else "Соединение закрыто",
            inline=False,
        )

        # Отправляем сообщение в канал
        await ctx.send(embed=embed)

        # Логируем успешное подключение
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"✅ Успешное подключение к БД MariaDB. "
                f"Запрошено пользователем: {ctx.author}.\n_ _"
            )

    except mariadb.Error as db_error:
        # Создаем embed для ошибки подключения
        embed = disnake.Embed(
            title="Ошибка подключения",
            description="Не удалось подключиться к базе данных MariaDB.",
            color=disnake.Color.red(),
        )
        embed.add_field(name="Ошибка", value=str(db_error), inline=False)

        # Отправляем сообщение об ошибке в канал
        await ctx.send(embed=embed)

        # Логируем ошибку
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Ошибка подключения к БД MariaDB: {db_error}. "
                f"Запрошено пользователем: {ctx.author}.\n_ _"
            )

    except Exception as e:
        # Общая обработка исключений
        embed = disnake.Embed(
            title="Ошибка",
            description="Произошла непредвиденная ошибка при подключении к базе данных.",
            color=disnake.Color.red(),
        )
        embed.add_field(name="Детали ошибки", value=str(e), inline=False)

        # Отправляем сообщение об ошибке в канал
        await ctx.send(embed=embed)

        # Логируем ошибку
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Непредвиденная ошибка при подключении к БД MariaDB: {e}. "
                f"Запрошено пользователем: {ctx.author}.\n_ _"
            )

    finally:
        # Закрываем соединение, если оно было успешно установлено
        if conn and conn.open:
            conn.close()
            print("Соединение с базой данных закрыто.")
