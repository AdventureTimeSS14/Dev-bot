import disnake

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM


async def get_log_channel():
    """
    Проверяет наличие канала для логирования.
    """
    channel = bot.get_channel(ADMIN_TEAM)
    if not channel:
        return None
    return channel


async def check_user(ctx, user):
    """
    Проверяет, существует ли указанный участник на сервере.
    """
    if not user:
        await ctx.send(
            "❌ Не смогла найти участника. Пожалуйста, убедитесь, что имя пользователя "
            "указано правильно."
        )
        return False
    return True


async def check_roles(ctx, roles):
    """
    Проверяет существование указанных ролей на сервере.
    """
    invalid_roles = [role.name for role in roles if role not in ctx.guild.roles]
    if invalid_roles:
        await ctx.send(
            f"❌ Не удалось найти роль(и): **{', '.join(invalid_roles)}**. "
            f"Убедитесь, что роли существуют на сервере."
        )
        return False
    return True


async def check_reason(ctx, reason):
    """
    Проверяет, что причина указана и ее длина больше 5 символов.
    """
    if not reason or len(reason.strip()) < 5:
        await ctx.send(
            "❌ Причина должна быть указана и содержать хотя бы 5 символов."
        )
        return False
    return True


async def remove_roles_from_user(user, roles):
    """
    Удаляет указанные роли у пользователя.
    """
    removed_roles = []
    errors = []
    for role in roles:
        if role in user.roles:
            try:
                await user.remove_roles(role)
                removed_roles.append(role)
            except Exception as e:
                errors.append(
                    f"❌ Ошибка при удалении роли **{role.name}**: {str(e)}"
                )
        else:
            errors.append(f"❌ У {user.name} нет роли **{role.name}**.")
    return removed_roles, errors


async def send_results(ctx, removed_roles, errors):
    """
    Отправляет результаты удаления ролей или ошибки в канал.
    """
    if removed_roles:
        role_names = ", ".join([role.name for role in removed_roles])
        await ctx.send(f"✅ Роль(и) успешно сняты: {role_names}")

    if errors:
        for error in errors:
            await ctx.send(error)


# Основная команда
@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def remove_team(
    ctx,
    user: disnake.Member,
    role_dep: disnake.Role,
    role_job: disnake.Role,
    *,
    reason: str,
):
    """
    Команда для снятия сотрудника с должности.
    """
    # Проверяем канал для логирования
    channel_get = await get_log_channel()
    if not channel_get:
        await ctx.send("❌ Не удалось найти канал для логирования действий.")
        return

    # Проверка пользователя
    if not await check_user(ctx, user):
        return

    # Проверка ролей
    if not await check_roles(ctx, [role_dep, role_job]):
        return

    # Проверка причины
    if not await check_reason(ctx, reason):
        return

    # Удаляем роли
    removed_roles, errors = await remove_roles_from_user(
        user, [role_dep, role_job]
    )

    # Отправляем результаты
    await send_results(ctx, removed_roles, errors)

    # Если обе роли успешно удалены, отправляем Embed
    if len(removed_roles) == 2:
        embed = disnake.Embed(
            title="Снятие с должности",
            description=(
                f"{ctx.author.mention}({ctx.author.display_name}) "
                f"снял(а) с должности {user.mention}({user.display_name})."
            ),
            color=role_job.color,
        )
        embed.add_field(
            name="Отдел:", value=f"**{role_dep.name}**", inline=False
        )
        embed.add_field(
            name="Должность:", value=f"**{role_job.name}**", inline=False
        )
        embed.add_field(name="Причина:", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        await channel_get.send(embed=embed)
    else:
        await ctx.send("❌ Не удалось снять все указанные роли.")
