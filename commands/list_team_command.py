import discord
from discord import Color, Embed
from discord.ext import commands, tasks
from discord.ext.tasks import loop
from discord.utils import get  # Убедитесь, что этот импорт присутствует

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import WHITELIST_ROLE_ID

roles = [
    # Список ролей и их ID
    # Руководство проекта
    ("Создатель проекта", 1116612861993689251),
    ("Хост", 1233048689996726378),
    ("Зам создателя", 1127152229439246468),
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
    ("Главный разработчик", 1054583381024854106),
    ("Tech Lead", 1266161509449465988),
    ("Team Lead", 1266161403686031481),
    ("Project Manager", 1224087058838978650),
    ("Senior Developer", 1173709647950118994),
    ("Middle Developer", 1054583841060306944),
    ("Junior Developer", 1173709090694889513),
    ("QA Engineer", 1266164443327234110),
    ("Inactive Developer", 1173711388951203911),

    # Ютуберы
    ("Ютуберы", 1192427200964735087)
]

# Определяем цвет для каждой категории
color_map = {
    "Руководство": 0xFFFFFF,  # Белый
    "Отдел Администрации": 0xff0000, # Красный
    "Департамент обжалования": 0xFF0000,  # Красный
    "Дискорд Администрация": 0xaaffcf,  # Ярко-зеленый салатовый
    "Спец роли администрации": 0xff0000,  # Красный
    "Отдел Маппинга": 0xffa500,  # Оранжевый
    "Отдел Вики": 0x0000FF,  # Синий
    "Отдел Спрайтинга": 0xffc0cb,  # Розовый
    "Отдел Квентологии": 0xA52A2A,  # Коричневый
    "Отдел Разработки": 0x00FF00,  # Зеленый
    "Отдел Медиа": 0xff0000  # Красный
}

# Группируем роли по категориям
roles_by_category = {
    "Руководство": [
        ("Создатель проекта", 1116612861993689251),
        ("Хост", 1233048689996726378),
        ("Зам создателя", 1127152229439246468),
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
        ("Head Of Development", 1054583381024854106),
        ("TechLead Developer", 1266161509449465988),
        ("TeamLead Developer", 1266161403686031481),
        ("Project Manager", 1224087058838978650),
        ("Senior Developer", 1173709647950118994),
        ("Middle Developer", 1054583841060306944),
        ("Junior Developer", 1173709090694889513),
        ("QA Engineer", 1266164443327234110),
        ("Inactive Developer", 1173711388951203911),
    ],
    "Отдел Медиа": [
        ("Ютуберы", 1192427200964735087)
    ]
}

# 1297158288063987752

@bot.command(name='list_team')
@has_any_role_by_id(WHITELIST_ROLE_ID)
async def list_team(ctx):
    deleted = await ctx.channel.purge(limit=100)
    # Обработка каждой категории
    for category, roles in roles_by_category.items():
        color = color_map.get(category, 0xFFFFFF)
        print(f"Категория: {category}, Цвет: {hex(color)}")  # Логирование цвета
        
        embed = Embed(title=category, color=color)
        
        for role_name, role_id in roles:
            role = get(ctx.guild.roles, id=role_id)
            if role:
                members = [f"<@{member.name()}>" for member in role.members]  # Пинг участников
                if members:
                    embed.add_field(name=role_name, value=', '.join(members.name), inline=False)
                else:
                    embed.add_field(name=role_name, value='Нет участников', inline=False)
            else:
                print(f"Роль не найдена: {role_name}")

        await ctx.send(embed=embed)

@list_team.error
async def list_team(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Не могу идентифицировать вас в базе данных команды разработки Adventure Time, вы не имеете права пользоваться этой командой.")
        
@tasks.loop(hours=12)
async def list_team_task():
    channel = bot.get_channel(1297158288063987752)
    if channel:
        deleted = await channel.purge(limit=100)

        for category, roles in roles_by_category.items():
            color = color_map.get(category, 0xFFFFFF)
            print(f"Категория: {category}, Цвет: {hex(color)}")

            embed = Embed(title=category, color=color)

            for role_name, role_id in roles:
                role = get(channel.guild.roles, id=role_id)
                if role:
                    members = [f"<@{member.id}>" for member in role.members]  # Ping members
                    if members:
                        embed.add_field(name=role_name, value=', '.join(members), inline=False)
                    else:
                        embed.add_field(name=role_name, value='Нет участников', inline=False)
                else:
                    print(f"Роль не найдена: {role_name}")

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
