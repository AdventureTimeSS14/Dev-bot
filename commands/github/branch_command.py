import aiohttp

from bot_init import bot
from disnake import Embed
from dataConfig import USER_KEY_GITHUB
from template_embed import embed_branch

@bot.command(name="branch")
async def branch_command(ctx):
    url = f"https://api.github.com/repos/AdventureTimeSS14/space_station_ADT/branches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await ctx.send(f"Ошибка {resp.status}: {await resp.text()}")
                    return
                branches = await resp.json()

        embed = Embed(title=embed_branch["title"], color=embed_branch["color"])
        for field in embed_branch["fields"]:
            value = eval(field["value"], {"branches": branches})
            embed.add_field(name=field["name"], value=f"`{value}`", inline=field["inline"])

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")