"""
Модуль команды extend_vacation
"""

import disnake

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, VACATION_ROLE


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def extend_vacation(
    ctx, user: disnake.Member, new_end_date: str, reason: str
):
    """
    Продление отпуска пользователю. Обновляется срок отпуска и причина.
    """
    # Получаем роль отпуска
    role_vacation = ctx.guild.get_role(VACATION_ROLE)
    if not role_vacation:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя роль отпуска
    if role_vacation not in user.roles:
        await ctx.send(
            f"❌ {user.mention} не имеет роли {role_vacation.name}, "
            "поэтому продлить отпуск невозможно."
        )
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    try:
        # Создаем Embed для уведомления в админ-канале
        embed = disnake.Embed(
            title="Продление отпуска",
            description=(
                f"{ctx.author.mention}({ctx.author.display_name}) "
                f"продлил(а) отпуск для {user.mention}({user.display_name})."
            ),
            color=disnake.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(
            name="Новый срок отпуска", value=f"**{new_end_date}**", inline=True
        )
        embed.add_field(
            name="Причина продления", value=f"**{reason}**", inline=False
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Желаем хорошего продолжения отдыха!")

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

        # Ответ пользователю
        await ctx.send(
            f"✅ Срок отпуска {user.mention} был успешно продлен до {new_end_date}."
        )

    except disnake.Forbidden:
        await ctx.send(
            "⚠️ Ошибка: У бота недостаточно прав для отправки уведомлений."
        )
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось продлить отпуск. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
