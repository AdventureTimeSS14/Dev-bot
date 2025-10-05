import aiohttp

from datetime import datetime
from disnake import Intents, Embed
from disnake.ext.commands import Bot, has_role

from template_embed import embed_status, embed_log

from dataConfig import USER_KEY_GITHUB, DISCORD_KEY, ROLE_ACCESS_HEADS, LOG_CHANNEL_ID

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

'''Команда, дублирующая текст пользователя'''
@bot.command(name="print")
async def print_command(ctx, *, text: str):
    await ctx.send(f"{ctx.author.mention}: {text}")


'''Команда для отправки паблиша какой-либо ветки'''
@has_role(ROLE_ACCESS_HEADS)
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
        address = "193.164.18.155"
        port = "1212"
    elif server.lower() == "dev":
        address = "5.180.174.139"
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
    
bot.run(DISCORD_KEY)