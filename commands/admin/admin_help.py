from bot_init import bot
from template_embed import embed_admin_help
from disnake import Embed

'''Команда для списка админ-команд'''
@bot.command(name="admin_help")
async def admin_help_command(ctx):
    embed = Embed(title=embed_admin_help["title"], color=embed_admin_help["color"], description=embed_admin_help["description"])
    for field in embed_admin_help["fields"]:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
    await ctx.send(embed=embed)