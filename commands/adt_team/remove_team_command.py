import discord
from discord.ext import commands
from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM
from discord.ext.commands import RoleNotFound, MemberNotFound


class RoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        role = discord.utils.get(ctx.guild.roles, name=argument)
        if role is None:
            raise RoleNotFound(argument)
        return role


class MemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        # Если это ID (число), пробуем найти участника по ID
        if argument.isdigit():
            member = discord.utils.get(ctx.guild.members, id=int(argument))
            if member:
                return member
        
        # Если это пинг (например, @juuungaruk), пробуем найти участника по упоминанию
        member = discord.utils.get(ctx.guild.members, mention=argument)
        if member:
            return member

        # Если это никнейм, пробуем найти по никнейму
        member = discord.utils.get(ctx.guild.members, nick=argument)
        if member:
            return member

        # Если не нашли участника по ID, пингу или нику, выбрасываем исключение
        raise MemberNotFound(argument)


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def remove_team(ctx, user: str, role_dep: str, role_job: str, *, reason: str):
    """
    Команда для снятия сотрудника с должности.
    """
    # Проверяем, существует ли канал для логирования
    channel_get = bot.get_channel(ADMIN_TEAM)
    if not channel_get:
        await ctx.send("❌ Не удалось найти канал для логирования действий.")
        return

    removed_roles = []
    errors = []

    # Перехватим ошибки на этапе конвертации участников и ролей
    try:
        # Преобразуем пользователя с использованием кастомного конвертера
        user_obj = await MemberConverter().convert(ctx, user)
        # Преобразуем роли с использованием кастомного конвертера
        role_dep_obj = await RoleConverter().convert(ctx, role_dep)
        role_job_obj = await RoleConverter().convert(ctx, role_job)
    except MemberNotFound as e:
        await ctx.send(f"❌ Ошибка: Пользователь не найден - {str(e)}")
        return
    except RoleNotFound as e:
        await ctx.send(f"❌ Ошибка: Роль не найдена - {str(e)}")
        return

    # Проверка причины
    if not reason or len(reason.strip()) < 5:
        await ctx.send("❌ Причина должна быть указана и содержать хотя бы 5 символов.")
        return

    # Проверяем и удаляем роли у пользователя
    for role in [role_dep_obj, role_job_obj]:
        if role in user_obj.roles:
            try:
                await user_obj.remove_roles(role)
                removed_roles.append(role)
            except Exception as e:
                # Если ошибка при удалении роли, добавляем ее в ошибки
                errors.append(f"❌ Ошибка при удалении роли **{role.name}**: {str(e)}")
        else:
            errors.append(f"❌ У {user_obj.name} нет роли **{role.name}**.")

    # Обрабатываем результаты
    if removed_roles:
        role_names = ", ".join([role.name for role in removed_roles])
        await ctx.send(f"✅ Роль(и) успешно сняты: {role_names}")
    
    if errors:
        # Отправляем ошибки в канал
        for error in errors:
            await ctx.send(error)

    # Если обе роли успешно удалены, отправляем Embed в тот же канал
    if len(removed_roles) == 2:
        embed = discord.Embed(
            title="Снятие с должности",
            description=f"{ctx.author.mention} снял с должности {user_obj.mention}.",
            color=role_job_obj.color,
        )
        embed.add_field(name="Отдел:", value=f"**{role_dep_obj.name}**", inline=False)
        embed.add_field(name="Должность:", value=f"**{role_job_obj.name}**", inline=False)
        embed.add_field(name="Причина:", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        await channel_get.send(embed=embed)
    else:
        await ctx.send("❌ Не удалось снять все указанные роли.")
