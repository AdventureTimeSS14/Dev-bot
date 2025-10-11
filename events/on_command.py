from datetime import datetime

from bot_init import bot
from template_embed import embed_log
from disnake import Embed
from dataConfig import LOG_CHANNEL_ID

@bot.event
async def on_command(ctx):
    embed = Embed(title=embed_log["title"], color=embed_log["color"])
    for field in embed_log["fields"]:
        embed.add_field(name=field["name"], value=eval(field["value"]), inline=field["inline"])
        
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)