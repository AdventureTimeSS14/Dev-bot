import discord
from discord.ext import commands
from discord.ext.commands import RoleNotFound, MemberNotFound

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM


# Ваш кастомный конвертер для ролей
class RoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        role = discord.utils.get(ctx.guild.roles, name=argument)
        if role is None:
            raise RoleNotFound(argument)
        return role


# Кастомный конвертер для участников
class MemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        member = discord.utils.get(ctx.guild.members, name=argument)
        if member is None:
            member = discord.utils.get(ctx.guild.members, nick=argument)  # пробуем найти по никнейму
        if member is None:
            raise MemberNotFound(argument)
        return member


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def new_team(ctx, user: str, *role_names: str):
    """
    Команда для назначения пользователя на должность в команде.
    Требует две роли: <роль отдела> и <роль должности>.
    """
    # Проверка на наличие ровно двух ролей
    if len(role_names) != 2:
        await ctx.send("❌ Ошибка: Укажите ровно две роли: <роль отдела> и <роль должности>.")
        return

    assigned_roles = []
    errors = []

    # Перехватим ошибки на этапе конвертации участника
    try:
        # Преобразуем пользователя с использованием кастомного конвертера
        user_obj = await MemberConverter().convert(ctx, user)
    except MemberNotFound as e:
        await ctx.send(f"❌ Ошибка: Пользователь не найден - {str(e)}")
        return

    # Перехватим ошибки на этапе конвертации ролей
    for role_name in role_names:
        try:
            # Преобразуем роль с использованием кастомного конвертера
            role = await RoleConverter().convert(ctx, role_name)

            # Проверяем, есть ли у пользователя эта роль
            if role in user_obj.roles:
                await ctx.send(f"❌ У {user_obj.mention} уже есть роль **{role.name}**.")
                continue

            try:
                # Пытаемся добавить роль
                await user_obj.add_roles(role)
                assigned_roles.append(role.name)
            except discord.Forbidden:
                await ctx.send(f"⚠️ У бота нет прав для добавления роли **{role.name}** у {user_obj.mention}.")
            except discord.HTTPException as e:
                await ctx.send(f"❌ Ошибка при добавлении роли **{role.name}**: {str(e)}")
            except Exception as e:
                await ctx.send(f"❌ Произошла ошибка при добавлении роли **{role.name}**: {str(e)}")

        except RoleNotFound as e:
            errors.append(f"❌ Роль '{role_name}' не найдена на сервере.")

    # Обрабатываем успешные действия и ошибки
    if assigned_roles:
        await ctx.send(f"✅ Роли успешно добавлены для {user_obj.mention}: {', '.join(assigned_roles)}.")

    if errors:
        # Отправляем сообщения об ошибках
        for error in errors:
            await ctx.send(error)

    # Если обе роли успешно добавлены, отправляем Embed в канал для уведомлений
    if len(assigned_roles) == 2:
        admin_channel = bot.get_channel(ADMIN_TEAM)
        if admin_channel:
            embed = discord.Embed(
                title="Назначение на должность",
                description=f"{ctx.author.mention} назначает {user_obj.mention}",
                color=discord.Color.green(),
            )
            embed.add_field(name="Отдел", value=f"**{assigned_roles[0]}**", inline=False)
            embed.add_field(name="Должность", value=f"**{assigned_roles[1]}**", inline=False)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

            await admin_channel.send(embed=embed)
