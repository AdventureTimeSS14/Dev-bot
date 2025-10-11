import random
from bot_init import bot

'''Команда, для проверки работы бота'''
@bot.command(name="check")
async def check_command(ctx):
    responses = ["Да, я тут!", "Работаю!", "Привет!", "На связи!"]
    await ctx.send(random.choice(responses))