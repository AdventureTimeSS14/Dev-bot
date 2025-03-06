import disnake
from disnake.ext import commands

from bot_init import bot

from commands.misc.check_roles import has_any_role_by_id
from components.button_help_components import action_row_button_help, action_row_bug_report

from config import (
    WHITELIST_ROLE_ID_ADMINISTRATION_POST
)
COLOR = disnake.Color.dark_red()  # Красный цвет для эмбеда

# Список команд и их описаний для администрирования
ADMIN_COMMANDS = [
    {
        "name": "🛠️ &update mrp/dev",
        "description": "Отправка POST запроса на обновление МРП или дева.",
    },
    {
        "name": "🔄 &restart mrp/dev",
        "description": "Отправка POST запроса на рестарт МРП или Дева.",
    },
    {
        "name": "📜 &game_rules",
        "description": "Выводит список игровых правил.",
    },
    {
        "name": "🏰 &bunker true/false",
        "description": "Переключение бункера на МРП сервере.",
    },
    {
        "name": "⚙️ &admin_presets",
        "description": "Выводит игровые пресеты.",
    },
    {
        "name": "ℹ️ &admin_info",
        "description": "Выводит информацию о текущем раунде и перечисляет игроков на сервере.",
    },
    {
        "name": "⏱️ &player_stats <NickName>",
        "description": "Выводит информацию о времени на всех наигранных ролях игрока.",
    },
    {
        "name": "📝 &player_notes <NickName>",
        "description": "Выводит список всех заметок игрока.",
    },
    {
        "name": "🔍 &check_nick <NickName>",
        "description": "Проверяет на мультиаккаунт игрока.",
    },
    {
        "name": "🛑 &banlist <NickName>",
        "description": "Выводит список банов и разбанов игрока.",
    },
    {
        "name": "🔓 &pardon <ban_id>",
        "description": "Разбанивает пользователя по id его серверного бана.(не путать с разбанов для ролей).",
    },
    
]

@bot.command(name="admin_help")
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def admin_help(ctx: commands.Context):
    """
    Выводит список доступных команд для администрирования сервером.
    """
    try:
        # Создаем embed
        embed = disnake.Embed(
            title="Команды для администрирования 🔧",
            description="Список доступных команд для администрирования сервера:",
            color=COLOR,
        )

        # Добавляем каждую команду из списка ADMIN_COMMANDS
        for command in ADMIN_COMMANDS:
            embed.add_field(
                name=command["name"], value=command["description"], inline=False
            )

        # Устанавливаем автора embed
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else None
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)

        # Отправляем embed
        await ctx.send(embed=embed, components=[action_row_button_help, action_row_bug_report])

    except Exception as e:
        # Логируем и обрабатываем ошибку
        error_message = (
            f"❌ Произошла ошибка при выполнении команды `admin_help`: {e}\n"
            f"Пользователь: {ctx.author} (ID: {ctx.author.id})"
        )
        print(error_message)  # Логирование в консоль
        await ctx.send(
            "Произошла ошибка при выполнении команды. Пожалуйста, попробуйте позже."
        )
