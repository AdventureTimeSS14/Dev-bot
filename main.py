import aiohttp
import random

from datetime import datetime
from disnake.ext import commands
from disnake import Intents, Embed
from disnake.ext.commands import Bot, has_any_role

from template_embed import embed_status, embed_log, embed_publish_status, embed_repoinfo, embed_git_team, embed_branch

from dataConfig import USER_KEY_GITHUB, DISCORD_KEY, ROLE_ACCESS_HEADS, ROLE_ACCESS_MAINTAINER, LOG_CHANNEL_ID, ADDRESS_DEV, ADDRESS_MRP, DATA_MRP, DATA_DEV, HEADERS_DEV, HEADERS_MRP

intent = Intents.all()
intent.message_content = True
intent.members = True
intent.guilds = True
intent.guild_messages = True
intent.guild_reactions = True

bot = Bot(
    help_command=None,
    command_prefix="&",
    intents=intent
)

@bot.event
async def on_command(ctx):
    # Создание эмбеда. TODO: Вынести в отдельную функцию
    embed = Embed(title=embed_log["title"], color=embed_log["color"])
    for field in embed_log["fields"]:
        embed.add_field(name=field["name"], value=eval(field["value"]), inline=field["inline"])
        
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Неизвестная команда")

'''Команда, для проверки работы бота'''
@bot.command(name="check")
async def check_command(ctx):
    responses = ["Да, я тут!", "Работаю!", "Привет!", "На связи!"]
    await ctx.send(random.choice(responses))


'''Команда для отправки паблиша какой-либо ветки'''
@has_any_role(*ROLE_ACCESS_MAINTAINER)
@bot.command(name="publish")
async def publish_command(ctx, branch: str = "master"):
    if not branch:
        await ctx.send("Не указана ветка для паблиша")
        return

    url = f"https://api.github.com/repos/AdventureTimeSS14/space_station_ADT/actions/workflows/publish-adt.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}"
    }
    
    data = {
        "ref": branch,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as resp:
                if resp.status == 204:
                    await ctx.send(f"Код {resp.status}. Запрос на паблиш отправлен")
                else:
                    await ctx.send(f"Код {resp.status}. Запрос на паблиш не отправлен")
    except Exception as e:
        await ctx.send(f"Ошибка при отправке запроса: {e}")

'''Команда для получения информации о сервере МРП/ДЕВа'''
@bot.command(name="status")
async def status_command(ctx, server: str = "mrp"):
    if server.lower() == "mrp":
        address = ADDRESS_MRP
        port = "1212"
    elif server.lower() == "dev":
        address = ADDRESS_DEV
        port = "1211"
    else:
        await ctx.send("Неверный сервер: dev или mrp")
        return

    url = f"http://{address}:{port}/status"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    # Создание эмбеда. TODO: Вынести в отдельную функцию
                    embed = Embed(title=embed_status["title"], color=embed_status["color"])
                    for field in embed_status["fields"]:
                        embed.add_field(name=field["name"], value=eval(field["value"]), inline=field["inline"])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Ошибка: код {resp.status}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")

@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="update")
async def update_command(ctx, server: str = "mrp"):

    if server.lower() == "mrp":
        address = ADDRESS_MRP
        data = DATA_MRP
        headers = HEADERS_MRP
    elif server.lower() == "dev":
        address = ADDRESS_DEV
        data = DATA_DEV
        headers = HEADERS_DEV
    else:
        await ctx.send("Неверный сервер: mrp или dev")
        return

    url = f"http://{address}:5000/instances/{server.upper()}/update"

    await ctx.send(f"Запуск обновления {server.upper()}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    await ctx.send(f"Код {resp.status}. Обновление на {server.upper()} успешно отправлено.")
                else:
                    await ctx.send(f"Код {resp.status}. Обновление на {server.upper()} сервер не отправлено")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")

@has_any_role(*ROLE_ACCESS_MAINTAINER)
@bot.command(name="publish_status")
async def publish_status_command(ctx):
    url = "https://api.github.com/repos/AdventureTimeSS14/space_station_ADT/actions/workflows/publish-adt.yml/runs"

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
            runs = data.get("workflow_runs", [])

            if not runs:
                await ctx.send("Нет запусков")
                return

            last_run = runs[0]
            run_status = last_run["status"]
            conclusion = last_run.get("conclusion")
            branch = last_run["head_branch"]
            user = last_run["actor"]["login"]

    status_map = {
        "in_progress": ("В процессе", 0xffa500),
    }

    if run_status == "completed":
        if conclusion == "success":
            translated_status, color = ("Завершено", 0x00ff00)
        else:
            translated_status, color = ("Не завершено", 0xff0000)
    else:
        translated_status, color = status_map.get(run_status, ("Неизвестно", 0x808080))

    embed = Embed(title=embed_publish_status["title"], color=color)

    for field in embed_publish_status["fields"]:
        value = eval(field["value"], {"translated_status": translated_status, "branch": branch, "user": user})
        embed.add_field(name=field["name"], value=value, inline=field["inline"])

    await ctx.send(embed=embed)

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

@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="del_maint")
async def del_maint_command(ctx, github_login: str):
    url = f"https://api.github.com/orgs/AdventureTimeSS14/teams/adt_maintainer/memberships/{github_login}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                if resp.status == 204:
                    await ctx.send(f"Участник {github_login} удалён из команды adt_maintainer.")
                else:
                    await ctx.send(f"Ошибка {resp.status}: {await resp.text()}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
    
bot.run(DISCORD_KEY)