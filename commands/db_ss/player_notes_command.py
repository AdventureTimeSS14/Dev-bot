import disnake
import psycopg2
from bot_init import bot
from config import (
    WHITELIST_ROLE_ID_ADMINISTRATION_POST
)
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id
from datetime import datetime

# Команда для получения заметок об игроке
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def player_notes(ctx, *, user_name: str):
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(**DB_PARAMS)
        cursor = connection.cursor()

        # SQL-запрос для получения заметок об игроке
        cursor.execute('''
            SELECT 
                admin_notes.admin_notes_id,
                admin_notes.created_at,
                admin_notes.message,
                admin_notes.severity,
                admin_notes.secret,
                admin_notes.last_edited_at,
                admin_notes.last_edited_by_id,
                player.player_id,
                player.last_seen_user_name,
                admin.created_by_name
            FROM admin_notes
            INNER JOIN player ON admin_notes.player_user_id = player.user_id
            LEFT JOIN (
                SELECT user_id AS created_by_id, last_seen_user_name AS created_by_name
                FROM player
            ) AS admin ON admin_notes.created_by_id = admin.created_by_id
            WHERE player.last_seen_user_name = %s;
        ''', (user_name,))

        result = cursor.fetchall()

        if result:
            embeds = []  # Список для хранения всех эмбедов
            embed = disnake.Embed(
                title=f'Заметки об игроке: {user_name}',
                description=f'Найдено заметок: {len(result)}',
                color=disnake.Color.dark_red()
            )

            # Форматируем каждую заметку в Embed
            for idx, note in enumerate(result):
                note_id, created_at, message, severity, secret, last_edited_at, last_edited_by_id, player_id, last_seen_user_name, created_by_name = note

                # Убираем все \n из сообщения
                message = message.replace('\n', ' ') if message else 'Нет сообщения'
                
                # Запрос для получения username редактора
                cursor.execute('''
                    SELECT last_seen_user_name
                    FROM player
                    WHERE user_id = %s;
                ''', (last_edited_by_id,))
                editor_name_result = cursor.fetchone()
                editor_name = editor_name_result[0] if editor_name_result else "Неизвестно"

                created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'Не указано'
                last_edited_at = last_edited_at.strftime('%Y-%m-%d %H:%M:%S') if last_edited_at else 'Не указано'

                # Определяем, нужно ли выводить информацию о редактировании
                edit_info = ''
                if created_at != last_edited_at:
                    edit_info = (
                        f'**🕒 Последнее редактирование**: {last_edited_at}\n'
                        f'**✏️ Редактор**: {editor_name}\n'
                    )

                embed.add_field(
                    name=f'📕 Заметка ID {note_id}',
                    value=(
                        f'**📅 Дата создания**: {created_at}\n'
                        f'**👤 Администратор**: {created_by_name or "Неизвестно"}\n'
                        f'**💬 Сообщение**: {message}\n'
                        f'{edit_info}\n\n'
                    ),
                    inline=False
                )
                
                embed.set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )

                # Если добавлено 5 полей или это последняя заметка, завершаем текущий эмбед
                if len(embed.fields) == 5 or idx == len(result) - 1:
                    embed.set_footer(text="Информация предоставлена администрацией")
                    embed.timestamp = datetime.now()
                    embeds.append(embed)
                    embed = disnake.Embed(
                        title=f'Заметки об игроке: {user_name}',
                        color=disnake.Color.dark_red()
                    )

            # Отправляем все эмбеды по очереди
            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.send(f'Заметки об игроке {user_name} не найдены.')

        # Закрытие соединения
        cursor.close()
        connection.close()

    except Exception as e:
        await ctx.send(f"Произошла ошибка при получении данных: {e}")
        print(f"Ошибка: {e}")
