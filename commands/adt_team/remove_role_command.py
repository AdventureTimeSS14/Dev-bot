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
        role = get(ctx.guild.roles, name=argument)
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
async def remove_role(ctx, user: str, *role_names: str):
    """
    Команда для снятия указанных ролей у пользователя.
    """
    # Проверяем, были ли указаны роли
    if not role_names:
        await ctx.send("❌ Вы не указали роли для снятия. Используйте команду следующим образом: `&remove_role @User Role1 Role2`")
        return

    removed_roles = []
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
            if role not in user_obj.roles:
                await ctx.send(f"❌ У {user_obj.name} нет роли '{role.name}'. Убедитесь, что роль правильно указана.")
                continue

            try:
                # Пытаемся снять роль
                await user_obj.remove_roles(role)
                removed_roles.append(role.name)
            except discord.Forbidden:
                await ctx.send(f"⚠️ У бота нет прав для снятия роли '{role.name}' у {user_obj.name}.")
            except discord.HTTPException as e:
                await ctx.send(f"❌ Ошибка при снятии роли '{role.name}': {str(e)}")
            except Exception as e:
                await ctx.send(f"❌ Произошла неизвестная ошибка при снятии роли '{role.name}': {str(e)}")

        except RoleNotFound as e:
            errors.append(f"❌ Роль '{role_name}' не найдена на сервере.")

    # Обрабатываем успешные действия и ошибки
    if removed_roles:
        await ctx.send(f"✅ Роли успешно сняты у {user_obj.name}: {', '.join(removed_roles)}.")

    if errors:
        # Отправляем сообщения об ошибках
        for error in errors:
            await ctx.send(error)
