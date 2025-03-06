import disnake
import psycopg2
from bot_init import bot
from config import (
    WHITELIST_ROLE_ID_ADMINISTRATION_POST,
)
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id
from datetime import datetime, timedelta  # Импортируем timedelta

# Команда для получения временной статистики игрока
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def player_stats(ctx, *, user_name: str):
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(**DB_PARAMS)
        cursor = connection.cursor()

        # Один SQL-запрос для получения временной статистики игрока по имени
        cursor.execute('''
            SELECT 
                play_time.tracker,
                play_time.time_spent
            FROM player
            INNER JOIN play_time ON player.user_id = play_time.player_id
            WHERE player.last_seen_user_name = %s;
        ''', (user_name,))

        result = cursor.fetchall()

        if result:
            # Подготовка к отправке данных в ответе
            embeds = []  # Список для хранения всех эмбедов
            embed = disnake.Embed(
                title=f'Временная статистика игрока: {user_name}',
                description=f'Найдено {len(result)} записей',
                color=disnake.Color.green()
            )

            # Форматируем каждую запись временной статистики
            for idx, record in enumerate(result):
                tracker, time_spent = record

                # Проверка типа time_spent и извлечение данных из timedelta
                if isinstance(time_spent, timedelta):
                    total_seconds = time_spent.total_seconds()
                    total_days = int(total_seconds // 86400)  # 86400 секунд в дне
                    total_hours = int((total_seconds % 86400) // 3600)
                    total_minutes = int((total_seconds % 3600) // 60)
                else:
                    # Если time_spent не timedelta, пытаемся разобрать как строку
                    time_parts = time_spent.split(':')
                    total_hours, total_minutes, total_seconds = map(float, time_parts)
                    total_days = 0  # Учитываем только часы, минуты и секунды

                # Формируем строку в требуемом формате
                time_str = f'{total_days:04};{total_hours:02};{total_minutes:02}'

                embed.add_field(
                    name=f'Роль: {tracker}',
                    value=f'Время наиграно: {time_str}\n',
                    inline=True
                )
                embed.set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )

                # Добавление эмбедов
                if len(embed.fields) == 20 or idx == len(result) - 1:
                    embed.set_footer(text="Сбор информации из базы данных")
                    embed.timestamp = datetime.now()
                    embeds.append(embed)
                    embed = disnake.Embed(
                        title=f'Временная статистика игрока: {user_name}',
                        color=disnake.Color.green()
                    )

            # Отправляем все эмбеды по очереди
            for e in embeds:
                await ctx.send(embed=e)

        else:
            await ctx.send(f'Временная статистика для игрока {user_name} не найдена.')

        # Закрытие соединения
        cursor.close()
        connection.close()

    except Exception as e:
        await ctx.send(f"Произошла ошибка при получении данных: {e}")
        print(f"Ошибка: {e}")
