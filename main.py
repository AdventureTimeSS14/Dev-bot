import os

from disnake import Intents
from disnake.ext.commands import Bot

from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("DISCORD_KEY")

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

bot.run(KEY)