import os
import requests

from disnake import Intents
from disnake.ext.commands import Bot, has_role

from dataConfig import GITHUB_USER_KEY, DISCORD_KEY

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

# TODO: Добавить декоратор на права доступа
@bot.command(name="publish")
async def publish_command(ctx, branch: str = "master"):

    if not branch:
        ctx.send("Не указана ветка для паблиша")

    # TODO: Поменять репу на АДТ
    url = f"https://api.github.com/repos/AdventureTimeSS14/Dev-bot/actions/workflows/test_action.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_USER_KEY}"
    }
    
    data = {
        "ref": branch,
    }

    response = requests.post(url=url, headers=headers, json=data)

    if response.status_code == 200 or 204:
        print(f"True Res stat: {response.status_code}")
        await ctx.send(f"Код: {response.status_code}. Запрос на паблиш отправлен")
    else:
        print(f"False Res stat: {response.status_code}")
        await ctx.send(f"Код: {response.status_code}. Запрос на паблиш не отправлен")

bot.run(DISCORD_KEY)