import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import ADMIN_TEAM


@bot.command(name="tweak_team")
@has_any_role_by_keys("head_adt_team", "head_discord_admin")
async def tweak_team(
    ctx: commands.Context,
    user: disnake.Member,
    old_role: disnake.Role,
    new_role: disnake.Role,
    reason: str,
):
    """
    Команда для изменения роли пользователя.
    Позволяет заменить одну роль другой с указанием причины.
    """

    # Проверка канала для логирования
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await ctx.send("❌ Не удалось найти канал для логирования.")
        return

    # Проверка на существование участника
    if not user:
        await ctx.send(
            "❌ Не смогла найти участника. "
            "Пожалуйста, убедитесь, что имя пользователя указано правильно."
        )
        return

    # Проверка наличия старой роли у пользователя
    if old_role not in user.roles:
        await ctx.send(
            f"❌ У {user.name} нет роли **{old_role.name}**. Убедитесь, что роль указана верно."
        )
        return

    # Проверка на допустимость причины
    if not reason or len(reason.strip()) < 5:
        await ctx.send(
            "❌ Причина должна быть указана и содержать хотя бы 5 символов."
        )
        return

    try:
        # Удаление старой роли и добавление новой
        await user.remove_roles(old_role, reason=reason)
        await user.add_roles(new_role, reason=reason)

        # Определяем тип действия: повышение или понижение
        action = (
            "Повышение в должности"
            if old_role < new_role
            else "Понижение в должности"
        )
        action_description = f"{ctx.author.mention} ({ctx.author.name}) {'повышает' if old_role < new_role else 'понижает'} {user.mention} ({user.name})." # pylint: disable=C0301
        color = new_role.color  # Цвет для Embed сообщения

        # Создаем Embed сообщение для лог-канала
        embed = disnake.Embed(
            title=action,
            description=action_description,
            color=color,
        )
        embed.add_field(
            name="Старая должность", value=f"**{old_role.name}**", inline=False
        )
        embed.add_field(
            name="Новая должность", value=f"**{new_role.name}**", inline=False
        )
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(
            text=f"Изменение роли произведено {ctx.author}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )

        # Отправляем Embed в лог-канал и подтверждение в канал команды
        await admin_channel.send(embed=embed)
        await ctx.send(
            f"✅ Роль **{old_role.name}** была успешно заменена на **{new_role.name}** у {user.name}. Причина: {reason}" # pylint: disable=C0301
        )

    except disnake.Forbidden:
        await ctx.send(
            "⚠️ У бота нет прав для изменения ролей. Пожалуйста, проверьте права бота."
        )
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Произошла ошибка при изменении ролей: {e}")
        print(f"Ошибка при изменении ролей: {e}")
    except Exception as e:
        await ctx.send(f"❌ Возникла ошибка: {e}")
        print("Ошибка при выполнении команды tweak_team:", e)
