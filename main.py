import os
import requests

from disnake import Intents
from disnake.ext.commands import Bot, has_role

from dataConfig import USER_KEY_GITHUB, DISCORD_KEY

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

'''Команда, дублирующая текст пользователя'''
@bot.command(name="print")
async def print_command(ctx, *, text: str):
    await ctx.send(f"{ctx.author.mention}: {text}")

@has_role(1060264704838209586)
@bot.command(name="publish")
async def publish_command(ctx, branch: str = "master"):

    if not branch:
        await ctx.send("Не указана ветка для паблиша")

    # TODO: Поменять репу на АДТ
    url = f"https://api.github.com/repos/AdventureTimeSS14/Dev-bot/actions/workflows/test_action.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {USER_KEY_GITHUB}"
    }
    
    data = {
        "ref": branch,
    }

    try:
        response = requests.post(url=url, headers=headers, json=data)

        if response.status_code == 204:
            await ctx.send(f"Код {response.status_code}. Запрос на паблиш отправлен")
        else:
            await ctx.send(f"Код {response.status_code}. Запрос на паблиш не отправлен")

    except Exception as e:
        await ctx.send(f"Ошибка при отправке запроса: {e}")

bot.run(DISCORD_KEY)