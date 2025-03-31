"""
Этот модуль инициализирует бота для работы с Discord.
Настроены необходимые параметры для запуска и обработки команд.
И менеджеры для работы с БД
"""

import disnake
from disnake.ext import commands
from modules.database_manager_class import DatabaseManagerSS14, DatabaseManagerSponsor

intents = disnake.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="&",
    help_command=None,
    intents=intents,
    test_guilds=[901772674865455115],
    sync_commands=True,
)

# Инициализация менеджеров БД
db_main = DatabaseManagerSS14("main")
db_dev = DatabaseManagerSS14("dev")
db_sponsor = DatabaseManagerSponsor()
