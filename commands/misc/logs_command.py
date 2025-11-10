from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_HEADS
from disnake.ext.commands import has_any_role

@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="logs")
async def logs_command(ctx, username: str, round_id: int, db_name: str = 'mrp'):
        guid_admin = await ss14_db.get_player_guid(username)

        if not guid_admin:
            await ctx.send("Пользователь не найден в БД.")
            return

        results = await ss14_db.get_logs_by_round(username, round_id, db_name)
        if not results:
            await ctx.send("Не найдено подозрительных логов админ арбуза🍉.")
            return

        output = "\n\n".join(f"{row['message']}" for row in results)
        chunks = [output[i:i+2000] for i in range(0, len(output), 2000)]
        for chunk in chunks:
            await ctx.send(chunk)