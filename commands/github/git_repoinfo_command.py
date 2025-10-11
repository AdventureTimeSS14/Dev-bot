import aiohttp

from bot_init import bot
from disnake import Embed
from dataConfig import USER_KEY_GITHUB
from template_embed import embed_repoinfo

@bot.command(name="git_repoinfo")
async def git_repoinfo_command(ctx):
    url = "https://api.github.com/repos/AdventureTimeSS14/space_station_ADT"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                await ctx.send(f"Ошибка {resp.status}")
                return
            data = await resp.json()

        pr_url = f"{url}/pulls?state=open"
        async with session.get(pr_url, headers=headers) as resp:
            pr_data = await resp.json()
            pr_count = len(pr_data)

        # Контрибьютеры
        contrib_url = f"{url}/contributors"
        async with session.get(contrib_url, headers=headers) as resp:
            contrib_data = await resp.json()
            contrib_count = len(contrib_data)

    embed = Embed(title=embed_repoinfo["title"], description=eval(embed_repoinfo["description"]), color=embed_repoinfo["color"])
    for field in embed_repoinfo["fields"]:
        value = eval(field["value"])
        embed.add_field(name=field["name"], value=value, inline=field["inline"])

    await ctx.send(embed=embed)