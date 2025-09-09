"""
Этот модуль инициализирует бота для работы с Discord.
Настроены необходимые параметры для запуска и обработки команд.
И инициализация менеджеров для работы с БД
"""
from disnake import Intents
from disnake.ext.commands import Bot

from modules.database_manager_class import DatabaseManagerSS14
from modules.database_manager_sponsor import SponsorDatabaseManager
from modules.database_manager_sqlite import DatabaseManagerSQLite

intents = Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True

bot = Bot(
    command_prefix="&",
    help_command=None,
    intents=intents,
    test_guilds=[901772674865455115],
    sync_commands=True,
)

# Инициализация менеджеров БД
ss14_db = DatabaseManagerSS14()
db_sponsor = SponsorDatabaseManager()
sqlite_vacations_db = DatabaseManagerSQLite()
