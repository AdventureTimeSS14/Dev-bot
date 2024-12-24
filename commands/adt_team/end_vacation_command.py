import discord
from discord.ext import commands
from discord.ext.commands import RoleNotFound, MemberNotFound

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, VACATION_ROLE


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
            member = discord.utils.get(ctx.guild.members, nick=argument)  # пробуем найти по никнейму
        if member is None:
            raise MemberNotFound(argument)
        return member


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def end_vacation(ctx, user: discord.Member):
    """
    Завершает отпуск указанного пользователя, удаляя роль отпуска.
    """
    # Получаем роль отпуска с использованием кастомного конвертера
    try:
        role_vacation = await RoleConverter().convert(ctx, VACATION_ROLE)
    except RoleNotFound:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли роль отпуска у пользователя
    if role_vacation not in user.roles:
        await ctx.send(f"❌ У {user.mention} нет роли {role_vacation.name}.")
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    try:
        # Удаляем роль отпуска у пользователя
        await user.remove_roles(role_vacation)
        await ctx.send(f"✅ Роль {role_vacation.name} успешно снята с {user.mention}.")

        # Создаем Embed для уведомления в админ-канал
        embed = discord.Embed(
            title="Окончание отпуска",
            description=f"{ctx.author.mention} завершил(а) отпуск для {user.mention}.",
            color=discord.Color.purple(),
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Действие", value="Закрытие отпуска", inline=False)

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("⚠️ Ошибка: У бота недостаточно прав для снятия роли.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось снять роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
