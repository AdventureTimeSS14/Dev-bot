import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST

COLOR = disnake.Color.dark_purple()

# Список команд и их описаний для работы с базой данных
DB_COMMANDS = [
    {
        "name": "&db_info",
        "description": "Выводит всю основную информацию о базе данных.",
    },
    {
        "name": "&db_status",
        "description": "Сообщает статус подключения к MariaDB.",
    },
]


@bot.command(name="db_help")
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def db_help(ctx: commands.Context):
    """
    Выводит список доступных команд для работы с базой данных.
    """
    try:
        # Создаем embed
        embed = disnake.Embed(
            title="Команды для управления MariaDB",
            description="Список доступных команд для работы с базой данных:",
            color=COLOR,
        )

        # Добавляем каждую команду из списка DB_COMMANDS
        for command in DB_COMMANDS:
            embed.add_field(
                name=command["name"], value=command["description"], inline=False
            )

        # Устанавливаем автора embed
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else None
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)

        # Отправляем embed
        await ctx.send(embed=embed)

    except Exception as e:
        # Логируем и обрабатываем ошибку
        error_message = (
            f"❌ Произошла ошибка при выполнении команды `db_help`: {e}\n"
            f"Пользователь: {ctx.author} (ID: {ctx.author.id})"
        )
        print(error_message)  # Логирование в консоль
        await ctx.send(
            "Произошла ошибка при выполнении команды. Пожалуйста, попробуйте позже."
        )
