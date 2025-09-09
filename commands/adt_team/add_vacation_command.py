import re
from datetime import date

import disnake

from bot_init import bot, sqlite_vacations_db
from commands.misc.check_roles import has_any_role_by_keys
from config import ADMIN_TEAM, VACATION_ROLE


@bot.command()
@has_any_role_by_keys("head_adt_team", "head_discord_admin")
async def add_vacation(ctx, user: disnake.Member, end_date: str, *, reason: str):
    """
    Выдача отпуска пользователю. Добавляется роль отпуска с указанием срока и причины.
    Формат даты: дд.мм.гггг (например, 22.02.2025)
    """
    try:
        # Очистка и проверка формата даты
        end_date = end_date.strip('"\' ')
        day, month, year = map(int, end_date.split('.'))
        vacation_end = date(year, month, day) 

        # Проверяем, что дата не в прошлом
        if vacation_end < date.today():
            await ctx.send("❌ Ошибка: Дата окончания отпуска не может быть в прошлом.")
            return
        
        # Форматируем для SQL
        sql_date = vacation_end.strftime('%Y-%m-%d')

    except ValueError:
        await ctx.send("❌ Ошибка: Неверный формат даты. Используйте дд.мм.гггг (например, 22.02.2025)")
        return
    except Exception as e:
        await ctx.send(f"❌ Критическая ошибка: {str(e)}")
        print(f"[add_vacation] Ошибка парсинга даты: {str(e)}")
        return

    # Получаем роль отпуска
    role_vacation = ctx.guild.get_role(int(VACATION_ROLE))  
    if not role_vacation:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя уже роль отпуска
    if role_vacation in user.roles:
        await ctx.send(f"❌ {user.mention} уже имеет роль {role_vacation.name}.")
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(int(ADMIN_TEAM))
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    conn = None
    cursor = None

    try:
        # Сохранение через менеджер
        sqlite_vacations_db.add_or_update_vacation(user.id, sql_date, reason)

        # Добавляем роль пользователю
        await user.add_roles(role_vacation)
        await ctx.send(f"✅ Роль {role_vacation.name} успешно добавлена {user.mention}.")

        # Создаем Embed для уведомления
        embed = disnake.Embed(
            title="Выдача отпуска",
            description=f"{ctx.author.mention} ({ctx.author.name}) выдал(а) отпуск для {user.mention} ({user.name}).",
            color=disnake.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Срок отпуска", value=f"**{end_date}**", inline=True)
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text="Желаем хорошего отдыха!")

        # Отправка Embed в админ-канал
        await admin_channel.send(embed=embed)

    except disnake.Forbidden:
        await ctx.send("⚠️ Ошибка: У бота недостаточно прав для добавления роли.")
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось добавить роль. Подробнее: {e}")
    except Exception as e:
        print(f"[add_vacation] Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
