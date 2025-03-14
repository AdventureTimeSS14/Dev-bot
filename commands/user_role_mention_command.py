"""
Модуль команды для получения все никнеймов относящихся к введённой роли.
"""

import disnake

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM)
async def user_role_mention(ctx, *role_names: str):
    """
    Команда для получения списка пользователей с заданной ролью по имени.
    """
    # Формируем имя роли из переданных аргументов
    role_name = " ".join(role_names).strip()

    if not role_name:
        await ctx.send(
            "❌ **Вы не указали название роли.**\n"
            "Используйте команду так: `&user_role_mention <название роли>`."
        )
        return

    # Ищем роль в списке ролей сервера
    role = disnake.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"❌ **Роль '{role_name}' не найдена на сервере.**")
        return

    # Получаем список пользователей с этой ролью
    members_with_role = [member for member in role.members]

    try:
        if members_with_role:
            members_count = len(members_with_role)
            members_list = "\n".join([f"👤 **{member.mention}**" for member in members_with_role])

            await ctx.send(
                f"✅ **Пользователи с ролью '{role.name}':** ({members_count})\n\n"
                f"{members_list}"
            )
        else:
            await ctx.send(f"⚠️ **Нет пользователей с ролью '{role.name}'.**")

    except disnake.errors.HTTPException as e:
        # Если ошибка превышения лимита, показываем только первых 50 пользователей
        if e.code == 50035:  # Проверка на ошибку из-за превышения лимита
            members_to_display = members_with_role[:50]  # Ограничиваем до 50 пользователей
            members_count = len(members_with_role)
            members_list = "\n".join([f"👤 **{member.mention}**" for member in members_to_display])

            message = f"✅ **Пользователи с ролью '{role.name}':** ({members_count})\n\n"
            message += members_list

            # Если пользователей больше 10, добавим информацию о количестве оставшихся
            if members_count > 50:
                message += f"\n\n⚠️ **И ещё {members_count - 50} пользователей...**"

            await ctx.send(message)
