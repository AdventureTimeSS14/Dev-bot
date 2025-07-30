from disnake.ext import commands

from config import MY_USER_ID, ROLE_WHITELISTS

GUILD_ID = 901772674865455115  # ID твоего сервера

BLOCKED_USER_ID = 725633890726838282 # Каш
BLOCKED_KEYS_FOR_USER = {"whitelist_role_id_administration_post", "general_adminisration_role"}

def has_any_role_by_keys(*whitelist_keys):
    """
    Декоратор для проверки, имеет ли пользователь одну из указанных ролей по ключам.
    Если пользователь — это MY_USER_ID, доступ разрешён всегда.
    При отказе выводятся названия нужных ролей без пинга.
    """
    async def predicate(ctx):
        if ctx.author.id == MY_USER_ID:
            return True

        # Блокируем пользователя, если ключи команды пересекаются с запрещёнными
        if ctx.author.id == BLOCKED_USER_ID:
            if any(key in BLOCKED_KEYS_FOR_USER for key in whitelist_keys):
                await ctx.send("❌ У вас нет доступа к этой команде.")
                return False

        user_role_ids = [role.id for role in ctx.author.roles]

        # Собираем все разрешённые ID ролей по ключам
        allowed_role_ids = set()
        for key in whitelist_keys:
            allowed_role_ids.update(ROLE_WHITELISTS.get(key, []))

        # Если хотя бы одна из ролей у пользователя есть — пропускаем
        if any(role_id in allowed_role_ids for role_id in user_role_ids):
            return True

        # Если команда выполнена на указанном сервере — показываем имена ролей
        if ctx.guild and ctx.guild.id == GUILD_ID:
            role_names = []
            for role_id in allowed_role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_names.append(role.name)

            if role_names:
                formatted_roles = ", ".join(f"`{name}`" for name in role_names)
                await ctx.send(f"❌ У вас нет доступа к этой команде.\nТребуемые роли: {formatted_roles}")
            else:
                await ctx.send("❌ У вас нет доступа к этой команде. (Роли не найдены)")
        else:
            await ctx.send("❌ У вас нет доступа к этой команде.")

        return False

    return commands.check(predicate)
