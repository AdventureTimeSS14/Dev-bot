from bot_init import bot, ss14_db
import disnake
from dataConfig import ROLE_ACCESS_ADMIN
from disnake.ext.commands import has_any_role

'''Команда для проверки прав админа'''
@has_any_role(*ROLE_ACCESS_ADMIN)
@bot.command(name="admin")
async def admin_command(ctx, nickname: str):
    mrp_info = await ss14_db.get_admin_permission(nickname, 'mrp')
    dev_info = await ss14_db.get_admin_permission(nickname, 'dev')

    if not mrp_info and not dev_info:
        embed = disnake.Embed(title="Админ не найден", description=f"{nickname} не админ.", color=0xFF0000)
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Информация о {nickname}", color=0xFFD700)

    if mrp_info:
        embed.add_field(name="MRP", value=f"**Титул:** {mrp_info[0]}\n**Ранг:** {mrp_info[1]}", inline=False)

    if mrp_info and dev_info:
        embed.add_field(name="──────────────────", value="⠀", inline=False)

    if dev_info:
        embed.add_field(name="DEV", value=f"**Титул:** {dev_info[0]}\n**Ранг:** {dev_info[1]}", inline=False)

    await ctx.send(embed=embed)