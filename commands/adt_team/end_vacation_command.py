"""
Модуль команды end_vacation
"""

import disnake

from bot_init import bot
from commands.dbCommand.get_db_connection import get_db_connection
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN, VACATION_ROLE


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def end_vacation(ctx, user: disnake.Member):
    """
    Завершает отпуск указанного пользователя, удаляя роль отпуска и удаляя запись из базы данных.
    """
    # Получаем роль отпуска
    role_vacation = ctx.guild.get_role(int(VACATION_ROLE))
    if not role_vacation:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли роль отпуска у пользователя
    if role_vacation not in user.roles:
        await ctx.send(f"❌ У {user.mention} нет роли {role_vacation.name}.")
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(int(ADMIN_TEAM))
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    conn = None
    cursor = None

    try:
        # Подключение к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Удаление записи из БД
        cursor.execute("DELETE FROM vacation_team WHERE discord_id = %s", (user.id,))
        conn.commit()

        # Удаляем роль отпуска у пользователя
        await user.remove_roles(role_vacation)
        await ctx.send(
            f"✅ Роль {role_vacation.name} успешно снята с {user.mention} и запись удалена из БД."
        )

        # Создаем Embed для уведомления в админ-канал
        embed = disnake.Embed(
            title="Окончание отпуска",
            description=(
                f"{ctx.author.mention} ({ctx.author.name}) "
                f"завершил(а) отпуск для {user.mention} ({user.name})."
            ),
            color=disnake.Color.purple(),
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Действие", value="Закрытие отпуска.", inline=False)

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

    except disnake.Forbidden:
        await ctx.send("⚠️ Ошибка: У бота недостаточно прав для снятия роли.")
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось снять роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
