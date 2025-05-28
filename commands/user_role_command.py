"""
Модуль команды для получения все никнеймов относящихся к введённой роли.
"""

import disnake

from bot_init import bot
from config import VACATION_ROLE


@bot.command()
async def user_role(ctx, *role_names: str):
    """
    Команда для получения списка пользователей с заданной ролью по имени.
    Показывает статус отпуска, если у пользователя есть роль 'Отпуск' (по ID).
    """
    # Формируем имя роли из переданных аргументов
    role_name = " ".join(role_names).strip()

    if not role_name:
        await ctx.send(
            ":x: **Вы не указали название роли.**\n"
            "Используйте команду так: `&user_role <название роли>`."
        )
        return

    # Ищем роль в списке ролей сервера
    role = disnake.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f":x: **Роль '{role_name}' не найдена на сервере.**")
        return

    # ID роли "Отпуск"
    vacation_role_id = VACATION_ROLE
    vacation_role = ctx.guild.get_role(vacation_role_id)

    # Получаем список пользователей с этой ролью
    members_with_role = [f":bust_in_silhouette: **{member.name}**{' (в отпуске)' if vacation_role in member.roles else ''}" for member in role.members]

    try:
        if members_with_role:
            members_count = len(members_with_role)
            members_list = "\n".join(members_with_role)

            await ctx.send(
                f":white_check_mark: **Пользователи с ролью '{role.name}':** ({members_count})\n\n"
                f"{members_list}"
            )
        else:
            await ctx.send(f":warning: **Нет пользователей с ролью '{role.name}'.**")

    except disnake.errors.HTTPException as e:
        # Если ошибка превышения лимита, показываем только первых 35 пользователей
        if e.code == 50035:  # Проверка на ошибку из-за превышения лимита
            members_to_display = members_with_role[:35]
            members_count = len(members_with_role)
            members_list = "\n".join(members_to_display)

            message = f":white_check_mark: **Пользователи с ролью '{role.name}':** ({members_count})\n\n"
            message += members_list

            # Если пользователей больше 10, добавим информацию о количестве оставшихся
            if members_count > 35:
                message += f"\n\n:warning: **И ещё {members_count - 35} пользователей...**"

            await ctx.send(message)
