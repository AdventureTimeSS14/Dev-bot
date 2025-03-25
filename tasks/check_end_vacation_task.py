from datetime import datetime

import disnake
from disnake.ext import tasks
from pytz import timezone

from bot_init import bot
from commands.dbCommand.get_db_connection import get_db_connection
from config import ADMIN_TEAM, VACATION_ROLE, LOG_CHANNEL_ID


@tasks.loop(hours=2)  # Запускается каждые 2 часа
async def check_end_vacation():
    # Получаем текущее время в МСК
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    moscow = timezone('Europe/Moscow')
    current_time = datetime.now(moscow)
    
    # Получаем текущую дату в формате YYYY-MM-DD
    current_date = current_time.date()  # Получаем дату без времени
    current_hour = current_time.hour

    # Подключаемся к базе данных
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Находим пользователей, у которых дата окончания отпуска совпадает с текущей или прошла
        cursor.execute("SELECT discord_id, data_end_vacation FROM vacation_team WHERE data_end_vacation <= %s", (current_date,))
        users_to_end_vacation = cursor.fetchall()

        if not users_to_end_vacation:
            print("❌ Нет пользователей с завершившимся отпуском.")
            await log_channel.send("❌ Нет пользователей с завершившимся отпуском.")
            return

        guild = bot.get_guild(901772674865455115)
        if not guild:
            print("❌ Ошибка: Сервер не найден")
            return

        # Получаем роль отпуска
        vacation_role = guild.get_role(VACATION_ROLE)
        if not vacation_role:
            print(f"❌ Ошибка: Роль с ID {VACATION_ROLE} не найдена")
            return

        # Получаем канал для уведомлений
        admin_channel = bot.get_channel(ADMIN_TEAM)
        if not admin_channel:
            print("❌ Ошибка: Канал уведомлений не найден.")
            return

        # Проходим по всем пользователям, чьи отпуска завершились
        for user_id, data_end_vacation in users_to_end_vacation:
            await log_channel.send(f"Пользователь {user_id}: дата окончания отпуска {data_end_vacation}")
            print(f"Пользователь {user_id}: дата окончания отпуска {data_end_vacation}")

            # Проверяем, прошла ли дата окончания отпуска или наступила
            if data_end_vacation < current_date or (data_end_vacation == current_date and current_hour >= 11):
                print(f"✅ Отпуск для пользователя {user_id} завершён: дата {data_end_vacation}, текущее время {current_time}")

                try:
                    # Используем fetch_member для гарантии получения объекта Member
                    member = await guild.fetch_member(user_id)
                except disnake.NotFound:
                    print(f"❌ Пользователь с ID {user_id} не найден на Discord.")
                    continue
                except disnake.HTTPException as e:
                    print(f"❌ Ошибка при запросе пользователя {user_id}: {e}")
                    continue

                # Удаляем запись из базы данных
                cursor.execute("DELETE FROM vacation_team WHERE discord_id = %s", (user_id,))
                conn.commit()

                if vacation_role in member.roles:
                    await member.remove_roles(vacation_role)
                    print(f"Роль {vacation_role.name} удалена у {member.display_name}")
                else:
                    print(f"У {member.display_name} нет роли {vacation_role.name}, пропускаем")
                    continue

                # Отправляем ЛС пользователю, что его отпуск завершен
                try:
                    await member.send("Ваш отпуск завершен. Роль отпуска была снята.")
                except disnake.Forbidden:
                    print(f"⚠️ Не удалось отправить сообщение пользователю {member.name}.")

                # Создаем Embed для уведомления в админ-канал
                embed = disnake.Embed(
                    title="Автозакрытие отпуска",
                    description=f"{member.mention} завершил(а) отпуск.",
                    color=disnake.Color.purple(),
                )
                embed.add_field(name="Пользователь", value=member.mention, inline=False)
                embed.add_field(name="Действие", value="Закрытие отпуска.", inline=False)

                # Отправляем Embed в админ-канал
                await admin_channel.send(embed=embed)
            else:
                print(f"❌ Отпуск для пользователя {user_id} ещё не завершён: дата {data_end_vacation}, текущее время {current_time}")

    except disnake.Forbidden:
        print("⚠️ Ошибка: У бота недостаточно прав.")
    except disnake.HTTPException as e:
        print(f"❌ Ошибка: Не удалось выполнить запрос. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
