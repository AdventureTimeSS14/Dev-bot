"""
Этот модуль инициализирует бота для работы с Discord.
Настроены необходимые параметры для запуска и обработки команд.
"""

import disnake
from disnake.ext import commands

bot = commands.Bot(
    command_prefix="&",
    help_command=None,
    intents=disnake.Intents.all(),
    test_guilds=[901772674865455115]
)
