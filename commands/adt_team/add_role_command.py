import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import RoleNotFound, MemberNotFound

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM


# Кастомный конвертер для ролей
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
            raise MemberNotFound(argument)
        return member


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def add_role(ctx, user: MemberConverter, *role_names: str):
    """
    Добавляет одну или несколько ролей указанному пользователю.
    """
    if not role_names:
        await ctx.send("❌ Пожалуйста, укажите хотя бы одну роль для добавления.")
        return

    # Переменная для подсчета успешно добавленных ролей
    added_roles = []
    errors = []

    for role_name in role_names:
        # Ищем роль с использованием кастомного конвертера
        try:
            role = await RoleConverter().convert(ctx, role_name)
        except RoleNotFound:
            errors.append(f"❌ Роль '{role_name}' не найдена на сервере.")
            continue

        if role in user.roles:
            errors.append(f"ℹ️ {user.mention} уже имеет роль '{role.name}'.")
            continue

        try:
            # Добавляем роль пользователю
            await user.add_roles(role)
            added_roles.append(role.name)
        except discord.Forbidden:
            errors.append(f"⚠️ У бота недостаточно прав для добавления роли '{role.name}' пользователю {user.mention}.")
        except discord.HTTPException as e:
            print(f"Ошибка при добавлении роли '{role.name}': {e}")
            errors.append(f"❌ Не удалось добавить роль '{role.name}' для {user.mention} из-за ошибки: {e}")

    # Если добавлены роли, выводим итоговое сообщение
    if added_roles:
        roles_list = ", ".join(added_roles)
        await ctx.send(f"✅ Роли ({roles_list}) успешно добавлены для {user.mention}.")

    # Если есть ошибки
    if errors:
        await ctx.send("\n".join(errors))

    # Если не удалось добавить ни одной роли
    if not added_roles and not errors:
        await ctx.send(f"❌ Не удалось добавить ни одной роли для {user.mention}. Проверьте права и правильность ввода ролей.")
