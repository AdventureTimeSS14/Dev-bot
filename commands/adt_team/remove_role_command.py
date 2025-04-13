"""
Модуль команды remove_role
"""

import disnake
from disnake.utils import get

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys


@bot.command()
@has_any_role_by_keys("head_adt_team", "head_discord_admin")
async def remove_role(ctx, user: disnake.Member, *role_names: str):
    """
    Команда для снятия указанных ролей у пользователя.
    """
    # Проверяем, были ли указаны роли
    if not role_names:
        await ctx.send(
            "❌ Вы не указали роли для снятия. "
            "Используйте команду следующим образом: "
            "`&remove_role @User Role1 Role2`"
        )
        return

    removed_roles = []

    # Проверяем и обрабатываем каждую роль
    for role_name in role_names:
        # Ищем роль на сервере
        role = get(ctx.guild.roles, name=role_name)

        if role is None:
            await ctx.send(f"❌ Роль '{role_name}' не найдена на сервере.")
            continue

        # Проверяем, есть ли у пользователя эта роль
        if role not in user.roles:
            await ctx.send(
                f"❌ У {user.name} нет роли '{role.name}'. "
                f"Убедитесь, что роль правильно указана."
            )
            continue

        try:
            # Пытаемся снять роль
            await user.remove_roles(role)
            removed_roles.append(role.name)
        except disnake.Forbidden:
            await ctx.send(
                f"⚠️ У бота нет прав для снятия роли '{role.name}' у {user.name}."
            )
        except disnake.HTTPException as e:
            await ctx.send(f"❌ Ошибка при снятии роли '{role.name}': {str(e)}")
        except Exception as e:
            await ctx.send(
                f"❌ Произошла неизвестная ошибка "
                f"при снятии роли '{role.name}': {str(e)}"
            )

    # Отправляем сообщение об успешных действиях, если были сняты роли
    if removed_roles:
        await ctx.send(
            f"✅ Роли успешно сняты у {user.name}: {', '.join(removed_roles)}."
        )
