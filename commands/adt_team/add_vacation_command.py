import discord
from discord.ext import commands
from discord.ext.commands import RoleNotFound, MemberNotFound

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, VACATION_ROLE


class RoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        # Проверка на ID роли (если это число)
        if argument.isdigit():
            role = discord.utils.get(ctx.guild.roles, id=int(argument))
            if role:
                return role

        # Если это не ID, пытаемся найти роль по имени
        role = discord.utils.get(ctx.guild.roles, name=argument)
        if role:
            return role

        # Если не нашли роль по ID или имени
        raise RoleNotFound(argument)


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
async def add_vacation(ctx, user: MemberConverter, end_date: str, reason: str):
    """
    Выдача отпуска пользователю. Добавляется роль отпуска с указанием срока и причины.
    """
    # Получаем роль отпуска с использованием кастомного конвертера
    try:
        role_vacation = await RoleConverter().convert(ctx, VACATION_ROLE)
    except RoleNotFound:
        await ctx.send("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя уже роль отпуска
    if role_vacation in user.roles:
        await ctx.send(f"❌ {user.mention} уже имеет роль {role_vacation.name}.")
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await ctx.send("❌ Ошибка: Канал уведомлений не найден.")
        return

    try:
        # Добавляем роль отпуска пользователю
        await user.add_roles(role_vacation)
        await ctx.send(f"✅ Роль {role_vacation.name} успешно добавлена {user.mention}.")

        # Создаем Embed для уведомления в админ-канале
        embed = discord.Embed(
            title="Выдача отпуска",
            description=f"{ctx.author.mention} выдал(а) отпуск для {user.mention}.",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Срок отпуска", value=f"**{end_date}**", inline=True)
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Желаем хорошего отдыха!")

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("⚠️ Ошибка: У бота недостаточно прав для добавления роли.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось добавить роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await ctx.send("❌ Произошла непредвиденная ошибка.")
