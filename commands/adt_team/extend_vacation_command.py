"""
Модуль команды extend_vacation
"""

import disnake
from datetime import date

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from commands.dbCommand.get_db_connection import get_db_connection
from config import ADMIN_TEAM, HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN, VACATION_ROLE

@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def extend_vacation(ctx, user: disnake.Member, new_end_date: str, *, reason: str):
    """
    Продление отпуска пользователю. Обновляется срок отпуска и причина.
    Формат даты: дд.мм.гггг (например, 22.02.2025)
    """
    # Получаем роль отпуска
    role_vacation = ctx.guild.get_role(int(VACATION_ROLE))
    if not role_vacation:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя роль отпуска
    if role_vacation not in user.roles:
        await ctx.send(f"❌ {user.mention} не имеет роли {role_vacation.name}, поэтому продлить отпуск невозможно.")
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(int(ADMIN_TEAM))
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    try:
        # Очистка и проверка формата даты
        new_end_date = new_end_date.strip('"\' ')
        day, month, year = map(int, new_end_date.split('.'))
        vacation_end = date(year, month, day)

        # Проверяем, что дата не в прошлом
        if vacation_end < date.today():
            await ctx.send("❌ Ошибка: Новая дата окончания отпуска не может быть в прошлом.")
            return

        # Форматируем для SQL
        sql_date = vacation_end.strftime('%Y-%m-%d')

    except ValueError:
        await ctx.send("❌ Ошибка: Неверный формат даты. Используйте дд.мм.гггг (например, 22.02.2025)")
        return
    except Exception as e:
        await ctx.send(f"❌ Критическая ошибка: {str(e)}")
        print(f"[extend_vacation] Ошибка парсинга даты: {str(e)}")
        return

    conn = None
    cursor = None

    try:
        # Подключение к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Обновление записи в БД
        cursor.execute("UPDATE vacation_team SET data_end_vacation = %s, reason = %s WHERE discord_id = %s",
                       (sql_date, reason, user.id))
        conn.commit()

        # Создаем Embed для уведомления в админ-канале
        embed = disnake.Embed(
            title="Продление отпуска",
            description=f"{ctx.author.mention} ({ctx.author.name}) продлил(а) отпуск для {user.mention} ({user.name}).",
            color=disnake.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Новый срок отпуска", value=f"**{new_end_date}**", inline=True)
        embed.add_field(name="Причина продления", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text="Желаем хорошего продолжения отдыха!")

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

        # Ответ пользователю
        await ctx.send(f"✅ Срок отпуска {user.mention} был успешно продлен до {new_end_date}.")

    except disnake.Forbidden:
        await ctx.send("⚠️ Ошибка: У бота недостаточно прав для отправки уведомлений.")
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось продлить отпуск. Подробнее: {e}")
    except Exception as e:
        print(f"[extend_vacation] Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
