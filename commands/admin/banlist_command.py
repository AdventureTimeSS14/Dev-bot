from bot_init import bot, ss14_db
import disnake
from dataConfig import ROLE_ACCESS_ADMIN
from disnake.ext.commands import has_any_role

'''Команда для просмотра всех банов на сервере'''
@has_any_role(*ROLE_ACCESS_ADMIN)
@bot.command(name="banlist")
async def banlist_command(ctx, nickname: str):
    bans = await ss14_db.search_ban_player(nickname)

    if not bans:
        embed = disnake.Embed(title="Баны не найдены", description=f"{nickname} без банов.", color=0xFF0000)
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Баны {nickname} ({len(bans)})", color=0xFF8C00)
    
    for ban in bans:
        ban_id, ban_time, exp_time, reason, admin_name, unban_time, unban_admin = ban

        ban_time_str = ban_time.strftime("%Y-%m-%d %H:%M:%S") if ban_time else "?"
        exp_str = exp_time.strftime("%Y-%m-%d %H:%M:%S") if exp_time else "Постоянно"
        info = f"**Дата:** {ban_time_str}\n**Истекает:** {exp_str}\n**Причина:** {reason}\n**Админ:** {admin_name or '?'}"
        if unban_time:
            unban_str = unban_time.strftime("%Y-%m-%d %H:%M:%S")
            info += f"\n**Разбан:** {unban_str} ({unban_admin or '?'})"
        embed.add_field(name=f"---------------\nБан #{ban_id}", value=info, inline=False)

    await ctx.send(embed=embed)