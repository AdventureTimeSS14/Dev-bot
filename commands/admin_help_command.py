import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from components.button_help_components import (action_row_bug_report,
                                               action_row_button_help)
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST

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
        "name": "📝 &player_notes <NickName>",
        "description": "Выводит список всех заметок игрока.",
    },
    {
        "name": "🔍 &check_nick <NickName>",
        "description": "Проверяет на мультиаккаунт игрока.",
    },
    {
        "name": "🛑 &banlist <NickName>",
        "description": "Выводит список банов игрока.",
    },
    {
        "name": "🔓 &pardon <ban_id>",
        "description": (
            "Разбанивает пользователя по id его серверного бана.(не путать с "
            "разбаном для ролей)."
        ),
    },
    {
        "name": "📂 &uploads [<mrp/dev>](default: mrp)",
        "description": (
            "Выводит логи загрузок файлов ogg? в "
            "виде списка. Можно указать mrp или dev."
        ),
    },
    {
        "name": "👥 &profiles <NickName>",
        "description": "Выводит список персонажей игрока с общей информацией о них.",
    },
    {
        "name": "🎃 &admin <NickName>",
        "description": "Показывает имеет ли данный пользователь права на mrp & dev сервере.",
    },
    {
        "name": "👑 &admins [<mrp/dev>](default: mrp)",
        "description": "Выводит список админов на mrp или dev указывая title и админ ранг.",
    },
    {
        "name": "📥 &perm_add <NickName> \"<Title>\" \"<AdminRank>\" [<Mrp/Dev>](default: mrp)",
        "description": (
            "Добавляет нового администратора в таблицу администраторов, "
            "на мрп или деве.***(Если аргументы из более одного слова, "
            "заключаем в кавычки)***"
        ),
    },
    {
        "name": "📤 &perm_del <NickName> [<Mrp/Dev>](default: mrp)",
        "description": "Удаляет пользователя из таблицы администраторов, на мрп или деве.",
    },
    {
        "name": "♻️ &perm_tweak <NickName> \"<Title>\" \"<AdminRank>\" [<Mrp/Dev>](default: mrp)",
        "description": (
            "Изменяет пользователю админские права, на мрп или деве.***"
            "(Если аргументы из более одного слова, заключаем в кавычки)***"
        ),
    },
    {
        "name": "🏷️ &admin_rank [<Mrp/Dev>](default: mrp)",
        "description": "Выводит список допустимых админ рангов. Мрп или Дев сервера.",
    },
    {
        "name": "👮‍♂️ &playtime",
        "description": (
            "Выводит список всех допустимых <ProtoPlayTimeTracker> "
            "таймтрекеров сборки ADT."
        ),
    },
    {
        "name": "⏱️ &player_stats <NickName>",
        "description": "Выводит информацию о времени на всех наигранных ролях игрока.",
    },
    {
        "name": "⏱ &playtime_addrole <NickName> <ProtoPlayTimeTracker> <Time>",
        "description": (
            "Добавляет указанное количество времени игроку для "
            "определённой должности. Укажите никнейм игрока, идентификатор "
            "должности (ProtoIdJob) и количество времени (в минутах). "
            "‼️ Минуты можно ввести отрицательные, тогда время будет убавлено!!"
        ),
    },
    {
        "name": "💯 &playtime_generalrole <NickName>",
        "description": (
            "Добавляет общее время игроку для открытия "
            "всех стандартных должностей (кроме глав и СБ). "
            "Укажите никнейм игрока."
        ),
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

        # Добавляем изображение икону : D
        embed.set_thumbnail(
            url=(
                "https://media.discordapp.net/attachme"
                "nts/1255118642442403986/135308226898126"
                "4555/229_20250311204105.png?ex=67e05b8f&i"
                "s=67df0a0f&hm=d516adce879449d2f3268ca0881aa"
                "c9fed48ef23530d2953afaf74b9ff503779&=&form"
                "at=webp&quality=lossless&width=281&height=394"
            )
        )

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
