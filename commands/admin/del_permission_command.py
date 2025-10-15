from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_HEADS
from disnake.ext.commands import has_any_role

@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="del_permission")
async def del_permission_command(ctx, username: str, server: str = "mrp"):

    if not await ss14_db.get_admin_permission(username, db_name=server):
        await ctx.send(f"Пользователь {username} не имеет права на {server.upper()}")
        return

    name_db = "mrp" if server.lower() == "mrp" else "dev"

    guid = await ss14_db.get_player_guid(username, name_db)
    if not guid:
        await ctx.send(f"Пользователь {username} не найден в БД {name_db.upper()}")
        return

    answer, message = await ss14_db.del_permission_admin(guid, username, name_db)

    if not answer:
        await ctx.send(f"Ошибка: {message}")
        return
    
    await ctx.send(f"{message}")