import discord
from discord.ext import commands
from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM
from discord.ext.commands import RoleNotFound, MemberNotFound

# Ваш кастомный конвертер для ролей
class RoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        role = discord.utils.get(ctx.guild.roles, name=argument)
        if role is None:
            raise RoleNotFound(argument)
        return role

# Ваш кастомный конвертер для участников
class MemberConverter(commands.Converter):
    async def convert(self, ctx, argument):
        member = discord.utils.get(ctx.guild.members, name=argument)
        if member is None:
            member = discord.utils.get(ctx.guild.members, nick=argument)  # пробуем найти по никнейму
        if member is None:
            raise MemberNotFound(argument)
        return member


@bot.command(name="tweak_team")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def tweak_team(
    ctx: commands.Context,
    user: str,  # Изменим на строку, чтобы использовать кастомный конвертер
    old_role: str,  # Также строка, чтобы использовать кастомный конвертер
    new_role: str,  # Также строка, чтобы использовать кастомный конвертер
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

    # Перехватим ошибки на этапе конвертации участников и ролей
    try:
        # Преобразуем пользователя с использованием кастомного конвертера
        user_obj = await MemberConverter().convert(ctx, user)
        # Преобразуем роли с использованием кастомного конвертера
        old_role_obj = await RoleConverter().convert(ctx, old_role)
        new_role_obj = await RoleConverter().convert(ctx, new_role)
    except MemberNotFound as e:
        await ctx.send(f"❌ Ошибка: Пользователь не найден - {str(e)}")
        return
    except RoleNotFound as e:
        await ctx.send(f"❌ Ошибка: Роль не найдена - {str(e)}")
        return

    # Проверка на допустимость причины
    if not reason or len(reason.strip()) < 5:
        await ctx.send("❌ Причина должна быть указана и содержать хотя бы 5 символов.")
        return

    # Проверка наличия старой роли у пользователя
    if old_role_obj not in user_obj.roles:
        await ctx.send(f"❌ У {user_obj.name} нет роли **{old_role_obj.name}**. Убедитесь, что роль указана верно.")
        return

    try:
        # Удаление старой роли и добавление новой
        await user_obj.remove_roles(old_role_obj, reason=reason)
        await user_obj.add_roles(new_role_obj, reason=reason)

        # Определяем тип действия: повышение или понижение
        action = "Повышение в должности" if old_role_obj < new_role_obj else "Понижение в должности"
        action_description = (
            f"{ctx.author.mention} {'повышает' if old_role_obj < new_role_obj else 'понижает'} {user_obj.mention}."
        )
        color = new_role_obj.color  # Цвет для Embed сообщения

        # Создаем Embed сообщение для лог-канала
        embed = discord.Embed(
            title=action,
            description=action_description,
            color=color,
        )
        embed.add_field(name="Старая должность", value=f"**{old_role_obj.name}**", inline=False)
        embed.add_field(name="Новая должность", value=f"**{new_role_obj.name}**", inline=False)
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"Изменение роли произведено {ctx.author}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

        # Отправляем Embed в лог-канал и подтверждение в канал команды
        await admin_channel.send(embed=embed)
        await ctx.send(f"✅ Роль **{old_role_obj.name}** была успешно заменена на **{new_role_obj.name}** у {user_obj.name}. Причина: {reason}")

    except discord.Forbidden:
        await ctx.send("⚠️ У бота нет прав для изменения ролей. Пожалуйста, проверьте права бота.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Произошла ошибка при изменении ролей: {e}")
        print(f"Ошибка при изменении ролей: {e}")
    except Exception as e:
        await ctx.send(f"❌ Возникла ошибка: {e}")
        print("Ошибка при выполнении команды tweak_team:", e)
