import discord
import mariadb
from discord.ext import commands

from bot_init import bot
from config import DATABASE, HOST, LOG_CHANNEL_ID, PASSWORD, PORT, USER


@bot.command(name="db_status")
async def db_status(ctx):
    """
    Команда для проверки состояния подключения к базе данных MariaDB.
    """
    conn = None
    try:
        # Подключаемся к базе данных
        conn = mariadb.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=int(PORT),
            database=DATABASE
        )

        # Создаем embed для успешного подключения
        embed = discord.Embed(
            title="Статус БД",
            description="Успешно подключено к базе данных MariaDB!",
            color=discord.Color.green(),
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
            await log_channel.send(f"✅ Успешное подключение к БД MariaDB. Запрошено пользователем: {ctx.author}.\n_ _")

    except mariadb.Error as db_error:
        # Создаем embed для ошибки подключения
        embed = discord.Embed(
            title="Ошибка подключения",
            description="Не удалось подключиться к базе данных MariaDB.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Ошибка", value=str(db_error), inline=False)

        # Отправляем сообщение об ошибке в канал
        await ctx.send(embed=embed)

        # Логируем ошибку
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Ошибка подключения к БД MariaDB: {db_error}. Запрошено пользователем: {ctx.author}.\n_ _"
            )

    except Exception as e:
        # Общая обработка исключений
        embed = discord.Embed(
            title="Ошибка",
            description="Произошла непредвиденная ошибка при подключении к базе данных.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Детали ошибки", value=str(e), inline=False)

        # Отправляем сообщение об ошибке в канал
        await ctx.send(embed=embed)

        # Логируем ошибку
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Непредвиденная ошибка при подключении к БД MariaDB: {e}. Запрошено пользователем: {ctx.author}.\n_ _"
            )

    finally:
        # Закрываем соединение, если оно было успешно установлено
        if conn and conn.open:
            conn.close()
            print("Соединение с базой данных закрыто.")

