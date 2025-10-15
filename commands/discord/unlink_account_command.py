from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_TOP_HEADS
from disnake.ext.commands import has_any_role

'''Команда для отвязки аккаунта'''
@has_any_role(*ROLE_ACCESS_TOP_HEADS)
@bot.command(name="unlink_account")
async def unlink_account_command(ctx, discord_id: str = None):
    if discord_id is None:
        discord_id = str(ctx.author.id)

    if not await ss14_db.is_linked(discord_id):
        await ctx.send("Аккаунт не привязан.")
        return

    success, message = await ss14_db.unlink_user(discord_id)
    await ctx.send(message)