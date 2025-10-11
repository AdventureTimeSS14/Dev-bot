import aiohttp

from bot_init import bot
from disnake import Embed
from dataConfig import USER_KEY_GITHUB
from template_embed import embed_git_team

@bot.command(name="git_team")
async def git_team_command(ctx):
    url = "https://api.github.com/orgs/AdventureTimeSS14/members"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                await ctx.send(f"Ошибка {resp.status}")
                return
            members = await resp.json()

    embed = Embed(title=embed_git_team["title"], color=embed_git_team["color"])
    for field in embed_git_team["fields"]:
        value = eval(field["value"], {"members": members})
        embed.add_field(name=field["name"], value=value, inline=field["inline"])

    await ctx.send(embed=embed)