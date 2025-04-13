from disnake.ext import commands

from config import MY_USER_ID, ROLE_WHITELISTS


def has_any_role_by_keys(*whitelist_keys):
    """
    Декоратор для проверки, имеет ли пользователь одну из указанных ключей групп ролей.
    Если пользователь имеет ID MY_USER_ID, доступ всегда разрешён.

    :param whitelist_keys: Ключи через запятую, доступ к которым проверяется.
    :return: Декоратор команды.
    """
    async def predicate(ctx):
        if ctx.author.id == MY_USER_ID:
            return True

        user_role_ids = [role.id for role in ctx.author.roles]

        # Объединяем все разрешённые роли из переданных ключей
        allowed_roles = set()
        for key in whitelist_keys:
            allowed_roles.update(ROLE_WHITELISTS.get(key, []))

        if any(role_id in allowed_roles for role_id in user_role_ids):
            return True

        await ctx.send("❌ У вас нет доступа к этой команде.")
        return False

    return commands.check(predicate)