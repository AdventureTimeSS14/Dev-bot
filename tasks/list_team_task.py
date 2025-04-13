from disnake import Embed
from disnake.ext import commands, tasks
from disnake.utils import get

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys

roles_team = [
    # Список ролей и их ID
    # Руководство проекта
    ("Создатель проекта", 1116612861993689251),
    ("Хост", 1233048689996726378),
    ("Зам. создателя проекта", 1127152229439246468),
    ("Куратор проекта", 1060264704838209586),
    ("Руководство проекта", 1054908932868538449),
    # Администрация
    ("Главный администратор", 1254021066796302366),
    ("Старший администратор", 1223228123370229770),
    ("Инструктор администрации", 1248665270051143721),
    ("Наблюдатель администрации", 1248666127949893747),
    ("Администратор", 1248665281748795392),
    ("Младший администратор", 1248665288283525272),
    ("Стажёр администрации", 1248665294944342016),
    # Департамент обжалования
    ("Глава департамента обжалования", 1183135960951697478),
    ("Департамент обжалований", 1084459980419240016),
    # Дискорд модерация
    ("Старший дискорд администратор", 1123894677712679015),
    ("Дискорд администратор", 1116562622976897085),
    # Спец роли администрации
    ("Следящий за СБ", 1093798766370373753),
    ("Следящий за командованием", 1108433417785319474),
    ("Следящий за юрдепом", 1204346674009612368),
    ("Перенос времени", 1216123834697252914),
    # Маппинг отдел
    ("Главный маппер", 1148669166128205926),
    ("Зам главного маппера", 1160695278429556796),
    ("Менеджер мапперов", 1274863861505462303),
    ("Старший маппер", 1258007009673089086),
    ("Маппер", 1062660322386784307),
    ("Маппер стажёр", 1062451564058521610),
    # Вики отдел
    ("Глава вики", 1084832292893118546),
    ("Тех ассистент вики", 1290374832676012135),
    ("Лоровед вики", 1270498576740647032),
    ("Редактор вики", 1084840686303580191),
    ("Стажёр вики", 1270425756820045845),
    ("Вики советчик", 1098963106694168576),
    # Спрайт отдел
    ("Ведущий спрайтер", 1089903271902183516),
    ("Зам ведущего спрайтера", 1150155484893040720),
    ("Спрайтер наставник", 1257007633936814090),
    ("Спрайтер", 1084170638811484221),
    ("Младший спрайтер", 1154869038720225402),
    ("Полу-спрайтер", 1173683325098012762),
    # Отдел Квентологии
    ("Ведущий квентолог", 1154778008255733842),
    ("Квентолог", 1168747891016347690),
    # Отдел Разработки
    ("Руководство отдела разработки", 1266161300036390913),
    ("Глава разработки", 1054583381024854106),
    ("Технический администратор", 1113669851475623976),
    ("Техлид разработки", 1266161509449465988),
    ("Тимлид разработки", 1266161403686031481),
    ("Проджект менеджер", 1224087058838978650),
    # ("Старший разработчик", 1173709647950118994),
    ("Разработчик", 1054583841060306944),
    ("Младший разработчик", 1173709090694889513),
    ("Тестировщик", 1266164443327234110),
    ("Менеджер разработки", 1266164436100452443),
    # ("Инактивный разработчик", 1173711388951203911),
    ("Maintainer", 1338486326328164352),
    ("Кодинг", 1321350645998944256),
    ("Прототипинг", 1321351353347604550),
    # Ютуберы
    ("Ютуберы", 1192427200964735087),
]

# Определяем цвет для каждой категории
color_map = {
    "Руководство": 0xFFFFFF,  # Белый
    "Отдел Администрации": 0xFF0000,  # Красный
    "Департамент обжалования": 0xFF0000,  # Красный
    "Дискорд Администрация": 0xAAFFCF,  # Ярко-зеленый салатовый
    "Спец роли администрации": 0xFF0000,  # Красный
    "Отдел Маппинга": 0xFFA500,  # Оранжевый
    "Отдел Вики": 0x0000FF,  # Синий
    "Отдел Спрайтинга": 0xFFC0CB,  # Розовый
    "Отдел Квентологии": 0xA52A2A,  # Коричневый
    "Отдел Разработки": 0x00FF00,  # Зеленый
    "Отдел Медиа": 0xFF0000,  # Красный
}

# Группируем роли по категориям
roles_by_category = {
    "Руководство": [
        ("Создатель проекта", 1116612861993689251),
        ("Хост", 1233048689996726378),
        ("Зам. создателя проекта", 1127152229439246468),
        ("Куратор проекта", 1060264704838209586),
        ("Руководство проекта", 1054908932868538449),
    ],
    "Отдел Администрации": [
        ("Главный администратор", 1254021066796302366),
        ("Старший администратор", 1223228123370229770),
        ("Инструктор администрации", 1248665270051143721),
        ("Наблюдатель администрации", 1248666127949893747),
        ("Администратор", 1248665281748795392),
        ("Младший администратор", 1248665288283525272),
        ("Стажёр администрации", 1248665294944342016),
    ],
    "Департамент обжалования": [
        ("Глава департамента обжалования", 1183135960951697478),
        ("Департамент обжалований", 1084459980419240016),
    ],
    "Дискорд Администрация": [
        ("Старший дискорд администратор", 1123894677712679015),
        ("Дискорд администратор", 1116562622976897085),
    ],
    "Спец роли администрации": [
        ("Следящий за СБ", 1093798766370373753),
        ("Следящий за командованием", 1108433417785319474),
        ("Следящий за юрдепом", 1204346674009612368),
        ("Перенос времени", 1216123834697252914),
    ],
    "Отдел Маппинга": [
        ("Главный маппер", 1148669166128205926),
        ("Зам главного маппера", 1160695278429556796),
        ("Менеджер мапперов", 1274863861505462303),
        ("Старший маппер", 1258007009673089086),
        ("Маппер", 1062660322386784307),
        ("Маппер стажёр", 1062451564058521610),
    ],
    "Отдел Вики": [
        ("Бюрократ вики", 1084832292893118546),
        ("Тех ассистент вики", 1290374832676012135),
        ("Лоровед вики", 1270498576740647032),
        ("Редактор вики", 1084840686303580191),
        ("Стажёр вики", 1270425756820045845),
        ("Вики советчик", 1098963106694168576),
    ],
    "Отдел Спрайтинга": [
        ("Ведущий спрайтер", 1089903271902183516),
        ("Зам ведущего спрайтера", 1150155484893040720),
        ("Спрайтер наставник", 1257007633936814090),
        ("Спрайтер", 1084170638811484221),
        ("Младший спрайтер", 1154869038720225402),
        ("Полу-спрайтер", 1173683325098012762),
    ],
    "Отдел Квентологии": [
        ("Ведущий квентолог", 1154778008255733842),
        ("Квентолог", 1168747891016347690),
    ],
    "Отдел Разработки": [
        ("Руководство отдела разработки", 1266161300036390913),
        ("Глава разработки", 1054583381024854106),
        ("Технический администратор", 1113669851475623976),
        ("Техлид разработки", 1266161509449465988),
        ("Тимлид разработки", 1266161403686031481),
        ("Проджект менеджер", 1224087058838978650),
        # ("Старший разработчик", 1173709647950118994),
        ("Разработчик", 1054583841060306944),
        ("Младший разработчик", 1173709090694889513),
        ("Тестировщик", 1266164443327234110),
        ("Менеджер разработки", 1266164436100452443),
        # ("Инактивный разработчик", 1173711388951203911),
        ("Maintainer", 1338486326328164352),
        ("Кодинг", 1321350645998944256),
        ("Прототипинг", 1321351353347604550),
    ],
    "Отдел Медиа": [("Ютуберы", 1192427200964735087)],
}

@bot.command(name="list_team")
@has_any_role_by_keys("head_adt_team")
async def list_team(ctx):
    """
    Команда для отображения состава команды по категориям.
    """
    await ctx.channel.purge(limit=15)

    # Обработка каждой категории
    for category, roles_team in roles_by_category.items(): # pylint: disable=W0621
        color = color_map.get(category, 0xFFFFFF)  # Выбор цвета
        embed = Embed(
            title=category,
            color=color,
            description=f"**👑 Состав команды в категории: {category}**",
        )

        # Добавляем иконку или изображение для каждой категории
        embed.set_thumbnail(
            url="https://example.com/your_icon.png"
        )  # Замените на свой URL изображения

        # Заголовок с эмодзи и стилями
        embed.add_field(
            name=f"**🌟 {category} Роли**",
            value="Все участники в данной категории:",
            inline=False,
        )

        for role_name, role_id in roles_team:
            role = get(ctx.guild.roles, id=role_id)
            if role:
                # Получаем URL иконки роли (если она есть)
                role_icon_url = role.icon.url if role.icon else None

                members = [f"<@{member.id}>" for member in role.members]
                members_count = len(members)

                if members_count > 1:
                    field_value = ", ".join(members)
                    embed.add_field(
                        name=f"**{role_name}** ({members_count})",
                        value=field_value,
                        inline=False,
                    )
                elif members_count == 1:
                    field_value = members[0]
                    embed.add_field(
                        name=f"**{role_name}**",
                        value=f"{field_value}",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"**❌ {role_name}**",
                        value="Нет участников",
                        inline=False,
                    )

                # Если есть значок роли, добавляем его как изображение
                if role_icon_url:
                    embed.set_thumbnail(url=role_icon_url)

            else:
                embed.add_field(
                    name=f"**❌ {role_name}**",
                    value="Роль не найдена",
                    inline=False,
                )

        await ctx.send(embed=embed)


@list_team.error
async def list_team_error(ctx, error):
    """
    Обработчик ошибок для команды list_team.

    Аргументы:
    ctx - контекст команды
    error - объект ошибки
    """
    if isinstance(error, commands.CheckFailure):
        await ctx.send("🚫 У вас нет прав на использование этой команды.")
    else:
        await ctx.send(f"❗ Произошла ошибка: {error}")


@tasks.loop(hours=12)
async def list_team_task(): # pylint: disable=R0912
    """
    Задача, выполняющаяся каждые 12 часов. Очищает канал от последних 15 сообщений.
    Ожидается, что ID канала уже известен. Выводит полный список команды.
    """
    channel = bot.get_channel(1297158288063987752)  # ID канала
    if channel:
        await channel.purge(limit=15)

        for category, roles_team in roles_by_category.items(): # pylint: disable=W0621
            color = color_map.get(category, 0xFFFFFF)  # Выбор цвета
            embed = Embed(
                title=category,
                color=color,
                description=f"**👑 Состав команды в категории: {category}**",
            )

            embed.set_thumbnail(
                url="https://example.com/your_icon.png"
            )  # Замените на свой URL изображения

            # Добавляем поле для заголовка
            embed.add_field(
                name=f"**🌟 {category} Роли**",
                value="Все участники в данной категории:",
                inline=False,
            )

            for role_name, role_id in roles_team:
                role = get(channel.guild.roles, id=role_id)
                if role:
                    role_icon_url = role.icon.url if role.icon else None
                    members = [f"<@{member.id}>" for member in role.members]
                    members_count = len(members)

                    if members_count > 1:
                        embed.add_field(
                            name=f"**{role_name}** ({members_count})",
                            value=", ".join(members),
                            inline=False,
                        )
                    elif members_count == 1:
                        embed.add_field(
                            name=f"**{role_name}**",
                            value=f"{members[0]}",
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"**❌ {role_name}**",
                            value="Нет участников",
                            inline=False,
                        )

                    # Если у роли есть иконка, добавляем её
                    if role_icon_url:
                        embed.set_thumbnail(url=role_icon_url)

                else:
                    embed.add_field(
                        name=f"**❌ {role_name}**",
                        value="Роль не найдена",
                        inline=False,
                    )

            # Добавление иконки для Вики Отдела
            if category == "Отдел Вики":
                viki_editor_role = get(channel.guild.roles, id=1084840686303580191)
                if viki_editor_role and viki_editor_role.icon:
                    embed.set_thumbnail(url=viki_editor_role.icon.url)

            if category == "Отдел Маппинга":
                mapper_role = get(channel.guild.roles, id=1062660322386784307)
                if mapper_role and mapper_role.icon:
                    embed.set_thumbnail(url=mapper_role.icon.url)

            if category == "Отдел Администрации":
                admin_role = get(channel.guild.roles, id=1248665281748795392)
                if admin_role and admin_role.icon:
                    embed.set_thumbnail(url=admin_role.icon.url)

            await channel.send(embed=embed)


# 1116612861993689251 - создатель проекта
# 1233048689996726378 - хост
# 1127152229439246468 - зам создателя
# 1060264704838209586 - Куратор проекта
# 1054908932868538449 - руководство проекта

# администрация
# 1254021066796302366 - главный админ
# 1223228123370229770 - старший админ
# 1248665270051143721 - инструктор администрации
# 1248666127949893747 - наблюдатель администрации
# 1248665281748795392 - админситратор
# 1248665288283525272 - мл админситратор
# 1248665294944342016 - стажёр администрации

# Департамент обжалования
# 1183135960951697478 - глава департамента обжалования
# 1084459980419240016 - департамент обжалований

# Дискорд модерация
# 1123894677712679015 - старший дискорд админситратор
# 1116562622976897085 - дискорд администратор

# Спец роли администрации
# 1093798766370373753 - следящий за СБ
# 1108433417785319474 - следящий за командованием
# 1204346674009612368 - следящий за юрдепом
# 1216123834697252914 - перенос времени

# Маппинг отдел
# 1148669166128205926 - главный маппер
# 1160695278429556796 - зам главного маппера
# 1274863861505462303 - менеджер мапперов
# 1258007009673089086 - старший маппер
# 1062660322386784307 - маппер
# 1062451564058521610 - маппер стажёр

# Вики отдел
# 1084832292893118546 - глава вики
# 1290374832676012135 - тех ассистент вики
# 1270498576740647032 - лоровед вики
# 1084840686303580191 - редактор вики
# 1270425756820045845 - стажёр вики
# 1098963106694168576 - вики советчик

# Спрайт отдел
# 1089903271902183516 - ведущий спрайтер
# 1150155484893040720 - зам ведущего спарйтера
# 1257007633936814090 - Спрайтер наставник
# 1084170638811484221 - Спрайтер
# 1154869038720225402 - Младший спрайтер
# 1173683325098012762 - Полу-Спрайтер

# Отдел Квентологии
# 1154778008255733842 - ведущий квентолог
# 1168747891016347690 - квентолог

# Отдел Разработки
# 1266161300036390913 - руководство отдела разработки
# 1054583381024854106 - главный разработчик
# 1266161509449465988 - Tech Lead
# 1266161403686031481 - Team Lead
# 1224087058838978650 - Project Manager
# 1173709647950118994 - Senior Developer
# 1054583841060306944 - Middle Developer
# 1173709090694889513 - Junior Developer
# 1266164443327234110 - QA Engineer
# 1173711388951203911 - Inactive Developer

# Ютуберы
# 1192427200964735087 - ютуберы
