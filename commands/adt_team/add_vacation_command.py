"""
Модуль команды add_vacation
"""

import disnake

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, VACATION_ROLE, HEAD_DISCORD_ADMIN


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def add_vacation(ctx, user: disnake.Member, end_date: str, reason: str):
    """
    Выдача отпуска пользователю. Добавляется роль отпуска с указанием срока и причины.
    """
    # Получаем роль отпуска
    role_vacation = ctx.guild.get_role(VACATION_ROLE)
    if not role_vacation:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя уже роль отпуска
    if role_vacation in user.roles:
        await ctx.send(
            f"❌ {user.mention} уже имеет роль {role_vacation.name}."
        )
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    try:
        # Добавляем роль отпуска пользователю
        await user.add_roles(role_vacation)
        await ctx.send(
            f"✅ Роль {role_vacation.name} успешно добавлена {user.mention}."
        )

        # Создаем Embed для уведомления в админ-канале
        embed = disnake.Embed(
            title="Выдача отпуска",
            description=(
                f"{ctx.author.mention}({ctx.author.display_name}) "
                f"выдал(а) отпуск для {user.mention}({user.display_name})."
            ),
            color=disnake.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(
            name="Срок отпуска", value=f"**{end_date}**", inline=True
        )
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Желаем хорошего отдыха!")

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

    except disnake.Forbidden:
        await ctx.send(
            "⚠️ Ошибка: У бота недостаточно прав для добавления роли."
        )
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось добавить роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
