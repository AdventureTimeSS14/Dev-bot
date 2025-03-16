"""
Модуль содержащий команду add_role
"""

import disnake
from disnake.utils import get

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def add_role(ctx, user: disnake.Member, *role_names: str):
    """
    Добавляет одну или несколько ролей указанному пользователю.
    """
    if not role_names:
        await ctx.send(
            "❌ Пожалуйста, укажите хотя бы одну роль для добавления."
        )
        return

    # Переменная для подсчета успешно добавленных ролей
    added_roles = []
    errors = []

    for role_name in role_names:
        # Ищем роль по имени
        role = get(ctx.guild.roles, name=role_name)

        if not role:
            errors.append(f"❌ Роль '{role_name}' не найдена на сервере.")
            continue

        if role in user.roles:
            errors.append(f"ℹ️ {user.mention} уже имеет роль '{role.name}'.")
            continue

        try:
            # Добавляем роль пользователю
            await user.add_roles(role)
            added_roles.append(role.name)
        except disnake.Forbidden:
            errors.append(
                f"⚠️ У бота недостаточно прав для добавления роли '{role.name}' "
                f"пользователю {user.mention}."
            )
        except disnake.HTTPException as e:
            print(f"Ошибка при добавлении роли '{role.name}': {e}")
            errors.append(
                f"❌ Не удалось добавить роль '{role.name}' для {user.mention} из-за ошибки: {e}"
            )

    # Если добавлены роли, выводим итоговое сообщение
    if added_roles:
        roles_list = ", ".join(added_roles)
        await ctx.send(
            f"✅ Роли ({roles_list}) успешно добавлены для {user.mention}."
        )

    # Если есть ошибки
    if errors:
        await ctx.send("\n".join(errors))

    # Если не удалось добавить ни одной роли
    if not added_roles and not errors:
        await ctx.send(
            f"❌ Не удалось добавить ни одной роли для {user.mention}. "
            "Проверьте права и правильность ввода ролей."
        )
