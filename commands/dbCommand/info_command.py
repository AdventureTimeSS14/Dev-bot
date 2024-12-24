import discord
import mariadb
from discord.ext import commands

from bot_init import bot
from config import DATABASE, HOST, LOG_CHANNEL_ID, PASSWORD, PORT, USER

COLOR = discord.Color.dark_purple()


@bot.command(name="db_info")
async def db_info(ctx):
    """
    Команда для получения информации о базе данных MariaDB.
    """
    conn = None
    try:
        # Устанавливаем соединение с базой данных
        conn = mariadb.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=int(PORT),
            database=DATABASE,
        )

        # Создаем embed для ответа
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else None
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)
        embed = discord.Embed(
            title="Информация о базе данных",
            description=f"Подключение к базе данных {DATABASE} выполнено успешно!",
            color=COLOR,
        )

        # Добавляем общую информацию
        embed.add_field(
            name="Статус соединения",
            value="Соединение открыто" if conn.open else "Соединение закрыто",
            inline=False,
        )
        embed.add_field(name="Хост", value=HOST, inline=True)
        embed.add_field(name="Порт", value=PORT, inline=True)
        embed.add_field(name="Имя пользователя", value=USER, inline=True)

        # Выполняем запросы к базе данных
        cursor = conn.cursor()

        # Запрос версии сервера
        cursor.execute("SELECT VERSION()")
        server_version = cursor.fetchone()
        embed.add_field(name="Версия MariaDB", value=server_version[0], inline=False)

        # Запрос списка таблиц
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if tables:
            table_list = "\n".join([table[0] for table in tables])
            embed.add_field(name="Список таблиц", value=table_list, inline=False)
        else:
            embed.add_field(name="Список таблиц", value="В базе данных нет таблиц.", inline=False)

        # Отправляем embed-ответ
        await ctx.send(embed=embed)

    except mariadb.Error as db_error:
        # Обработка ошибок базы данных
        error_embed = discord.Embed(
            title="Ошибка подключения к базе данных",
            description=str(db_error),
            color=discord.Color.red(),
        )
        await ctx.send(embed=error_embed)

        # Логируем ошибку в лог-канал
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Ошибка подключения к базе данных: {db_error}. Запрошено пользователем {ctx.author}.\n_ _"
            )

    except Exception as e:
        # Общая обработка ошибок
        error_embed = discord.Embed(
            title="Ошибка",
            description=f"Произошла непредвиденная ошибка: {e}",
            color=discord.Color.red(),
        )
        await ctx.send(embed=error_embed)

        # Логируем ошибку в лог-канал
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ Непредвиденная ошибка при выполнении команды db_info: {e}. Запрошено пользователем {ctx.author}.\n_ _"
            )

    finally:
        # Закрываем соединение с базой данных
        if conn and conn.open:
            conn.close()
            print("Соединение с базой данных закрыто.")
