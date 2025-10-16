from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_HEADS, LOG_CHANNEL_ID, MY_DS_ID
from disnake.ext.commands import has_any_role

@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="add_permission")
async def add_permission_command(ctx, username: str, title: str, permission: str, server: str = "mrp"):

    if await ss14_db.get_admin_permission(username, db_name=server):
        await ctx.send(f"Пользователь {username} уже имеет права на {server.upper()}")
        return

    name_db = "mrp" if server.lower() == "mrp" else "dev"

    guid = await ss14_db.get_player_guid(username, name_db)
    if not guid:
        await ctx.send(f"Пользователь {username} не найден в БД {name_db.upper()}")
        return

    answer, message = await ss14_db.add_permission_admin(guid, username, title, permission, name_db)

    if not answer:
        await ctx.send(f"Ошибка: {message}")
        return
    
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"<@{MY_DS_ID}>")
    
    await ctx.send(f"{message}")