from bot_init import bot, ss14_db
from disnake.ext.commands import has_any_role
from dataConfig import ROLE_ACCESS_ADMIN

@has_any_role(*ROLE_ACCESS_ADMIN)
@bot.command(name="get_ckey")
async def get_ckey_command(ctx, discord_id: str):
    player_guid = await ss14_db.get_player_guid_by_discord_id(discord_id)
    if not player_guid:
        await ctx.send(f"Игрока нет в БД")
        return

    player_name = await ss14_db.get_player_name(player_guid)

    await ctx.send(f"Никнейм пользователя {discord_id} принадлежит - {player_name}")