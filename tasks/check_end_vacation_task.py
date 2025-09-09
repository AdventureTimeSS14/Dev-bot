from datetime import datetime, date

import disnake
from disnake.ext import tasks
from pytz import timezone

from bot_init import bot, sqlite_vacations_db
from config import ADMIN_TEAM, LOG_CHANNEL_ID, VACATION_ROLE


@tasks.loop(hours=2)  # Запускается каждые 2 часа
async def check_end_vacation():
    # Получаем текущее время в МСК
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    moscow = timezone('Europe/Moscow')
    current_time = datetime.now(moscow)
    
    # Получаем текущую дату в формате YYYY-MM-DD
    current_date = current_time.date()  # Получаем дату без времени
    current_hour = current_time.hour

    try:
        users_to_end_vacation = sqlite_vacations_db.get_due_vacations(str(current_date))

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
            user = await bot.fetch_user(user_id)
            await log_channel.send(f"Пользователь {user.display_name}({user_id}): дата окончания отпуска {data_end_vacation}")
            print(f"Пользователь {user_id}: дата окончания отпуска {data_end_vacation}")

            # Проверяем, прошла ли дата окончания отпуска или наступила
            try:
                end_date = date.fromisoformat(str(data_end_vacation))
            except Exception:
                # Если формат неожиданный, пробуем обрезать время, если есть
                end_date = date.fromisoformat(str(data_end_vacation).split(" ")[0])

            if end_date < current_date or (end_date == current_date and current_hour >= 11):
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
                sqlite_vacations_db.remove_vacation(user_id)

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
        pass
