from bot_init import bot
from disnake import Embed
from template_embed import embed_git_help

@bot.command(name="git_help")
async def git_help_command(ctx):
    embed = Embed(
        title=embed_git_help["title"],
        color=embed_git_help["color"],
        description=embed_git_help["description"]
    )
    for field in embed_git_help["fields"]:
        embed.add_field(
            name=field["name"],
            value=field["value"],
            inline=field["inline"]
        )
    await ctx.send(embed=embed)