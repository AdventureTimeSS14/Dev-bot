"""
Модуль команды new_team
"""

import disnake

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def new_team(ctx, user: disnake.Member, *roles: disnake.Role):
    """
    Команда для назначения пользователя на должность в команде.
    Требует две роли: <роль отдела> и <роль должности>.
    """
    # Проверка на наличие ровно двух ролей
    if len(roles) != 2:
        await ctx.send(
            "❌ Ошибка: Укажите ровно две роли: <роль отдела> и <роль должности>."
        )
        return

    # Получаем роли
    role_department, role_position = roles
    assigned_roles = []

    # Проверяем и добавляем роли
    for role in [role_department, role_position]:
        if role in user.roles:
            await ctx.send(
                f"❌ У {user.mention} уже есть роль **{role.name}**."
            )
        else:
            try:
                await user.add_roles(role)
                assigned_roles.append(role.name)
            except disnake.Forbidden:
                await ctx.send(
                    f"⚠️ У бота нет прав для добавления роли **{role.name}** у {user.mention}."
                )
            except disnake.HTTPException as e:
                await ctx.send(
                    f"❌ Ошибка при добавлении роли **{role.name}**: {str(e)}"
                )
            except Exception as e:
                await ctx.send(
                    f"❌ Произошла ошибка при добавлении роли **{role.name}**: {str(e)}"
                )

    # Отправляем сообщение об успешных действиях, если роли были добавлены
    if assigned_roles:
        await ctx.send(
            f"✅ Роли успешно добавлены для {user.mention}: {', '.join(assigned_roles)}."
        )

    # Если были успешно добавлены обе роли, отправляем Embed в канал для уведомлений
    if len(assigned_roles) == 2:
        admin_channel = bot.get_channel(ADMIN_TEAM)
        if admin_channel:
            embed = disnake.Embed(
                title="Назначение на должность",
                description=(
                    f"{ctx.author.mention}({ctx.author.display_name}) "
                    f"назначает {user.mention}({user.display_name})"
                ),
                color=role_position.color,
            )
            embed.add_field(
                name="Отдел", value=f"**{role_department.name}**", inline=False
            )
            embed.add_field(
                name="Должность",
                value=f"**{role_position.name}**",
                inline=False,
            )
            embed.set_author(
                name=ctx.author.name, icon_url=ctx.author.avatar.url
            )

            await admin_channel.send(embed=embed)
