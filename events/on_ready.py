from bot_init import bot
from commands.github.git_fetch_pull import fetch_merged_pull_requests

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")
    bot.loop.create_task(fetch_merged_pull_requests())