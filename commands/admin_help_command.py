import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from components.button_help_components import (action_row_bug_report,
                                               action_row_button_help)

COLOR = disnake.Color.dark_red()

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
        "name": "👢 &kick <NickName> <Reason>",
        "description": "Отправляет POST запрос на кик указанного пользователя.",
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
        "name": "🔨 &ban <NickName> <Reason> <Minutes>",
        "description": "POST запрос на серверный бан. 0 — для пермабана.",
    },
    {
        "name": "🔓 &pardon <ban_id>",
        "description": "Разбан по ID серверного бана (не роли).",
    },
    {
        "name": "📂 &uploads [<mrp/dev>](default: mrp)",
        "description": "Выводит логи загрузок файлов.",
    },
    {
        "name": "👥 &profiles <NickName>",
        "description": "Выводит список персонажей игрока.",
    },
    {
        "name": "🚹 &profile_id <profile_id>",
        "description": "Подробная инфа по id профиля.",
    },
    {
        "name": "👤 &find_char \"<char_name>\" [<mrp/dev>](default: mrp)",
        "description": "Поиск никнейма игрока по имени персонажа.",
    },
    {
        "name": "🔮 &get_ckey <discord>",
        "description": "Получить ckey игрока по Discord.",
    },
    {
        "name": "🎃 &admin <NickName>",
        "description": "Проверяет, есть ли права у игрока.",
    },
    {
        "name": "🎬 &replay <round_id>",
        "description": "Загружает реплей указанного раунда на Google Drive и присылает ссылку на скачивание.",
    },
    {
        "name": "👑 &admins [<mrp/dev>](default: mrp)",
        "description": "Список админов и их ранги.",
    },
    {
        "name": "📥 &perm_add <NickName> \"<Title>\" \"<AdminRank>\" [<mrp/dev>](default: mrp)",
        "description": "Добавляет админа (аргументы в кавычках).",
    },
    {
        "name": "📤 &perm_del <NickName> [<mrp/dev>](default: mrp)",
        "description": "Удаляет администратора.",
    },
    {
        "name": "♻️ &perm_tweak <NickName> \"<Title>\" \"<AdminRank>\" [<mrp/dev>](default: mrp)",
        "description": "Изменяет права администратора.",
    },
    {
        "name": "🏷️ &admin_rank [<mrp/dev>](default: mrp)",
        "description": "Список допустимых админ рангов.",
    },
    {
        "name": "👮‍♂️ &playtime",
        "description": "Список доступных ProtoPlayTimeTracker.",
    },
    {
        "name": "⏱️ &player_stats <NickName>",
        "description": "Вывести наигранное время игрока по ролям.",
    },
    {
        "name": "⏱ &playtime_addrole <NickName> <Proto> <Time>",
        "description": "Добавляет или убавляет время игроку по роли.",
    },
    {
        "name": "💯 &playtime_generalrole <NickName>",
        "description": "Добавляет общее время для открытия стандартных ролей.",
    },
]

@bot.command(name="admin_help")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def admin_help(ctx: commands.Context):
    """
    Выводит список доступных команд для администрирования сервером.
    """
    try:
        # Собираем все команды в одну строку
        command_list_text = "\n".join(
            f"**{cmd['name']}** — {cmd['description']}" for cmd in ADMIN_COMMANDS
        )

        # Создаём embed
        embed = disnake.Embed(
            title="🔧 Команды для администрирования",
            description=command_list_text,
            color=COLOR,
        )

        # Автор
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else None
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)

        # Иконка
        embed.set_thumbnail(
            url=(
                "https://media.discordapp.net/attachments/1255118642442403986/"
                "1353082268981264555/229_20250311204105.png?ex=67e05b8f&is=67df0a0f&"
                "hm=d516adce879449d2f3268ca0881aac9fed48ef23530d2953afaf74b9ff503779&=&"
                "format=webp&quality=lossless&width=281&height=394"
            )
        )

        # Отправка
        await ctx.send(embed=embed, components=[action_row_button_help, action_row_bug_report])

    except Exception as e:
        # Обработка ошибок
        error_message = (
            f"❌ Ошибка в `admin_help`: {e}\n"
            f"Пользователь: {ctx.author} (ID: {ctx.author.id})"
        )
        print(error_message)
        await ctx.send(
            "Произошла ошибка при выполнении команды. Попробуйте позже."
        )
