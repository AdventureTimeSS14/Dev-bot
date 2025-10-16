from bot_init import bot, ss14_db

import uuid

@bot.command(name="link_account")
async def link_command(ctx, guid: str, ds_id: str):
    if await ss14_db.is_linked(ds_id):
        await ctx.send("Уже привязан.")
        return

    try:
        uuid.UUID(guid)
    except ValueError:
        await ctx.send(f"Невалидный UID {guid} (символов: {len(guid)})")
        return

    success, message = await ss14_db.link_user(guid, ds_id)
    await ctx.send(f"Ошибка: {message}" if not success else message)