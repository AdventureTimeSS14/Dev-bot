import aiohttp

from bot_init import bot
from dataConfig import USER_KEY_GITHUB, ROLE_ACCESS_HEADS
from disnake.ext.commands import has_any_role


@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="add_maint")
async def add_maint_command(ctx, github_login: str):
    url = f"https://api.github.com/orgs/AdventureTimeSS14/teams/adt_maintainer/memberships/{github_login}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}",
    }
    data = {"role": "maintainer"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    await ctx.send(f"Участник {github_login} добавлен в команду adt_maintainer.")
                else:
                    await ctx.send(f"Ошибка {resp.status}: {await resp.text()}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")