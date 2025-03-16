"""
Модуль предназначенный для общих комманд бота
"""
import disnake

from bot_init import bot


@bot.command(name="ping", help="Проверяет задержку бота.")
async def ping(ctx):
    """
    Команда для проверки задержки бота.
    """
    latency = round(bot.latency * 1000)  # Вычисляем задержку в миллисекундах
    emoji = (
        "🏓" if latency < 100 else "🐢"
    )  # Выбираем эмодзи в зависимости от задержки
    await ctx.send(f"{emoji} Pong! Задержка: **{latency}ms**")

@bot.command(name="git")
async def git_info(ctx):
    """
    Выводит информацию о репозиториях проекта.
    """
    # Создаем Embed
    embed = disnake.Embed(
        title="📚 Репозитории AdventureTimeSS14",
        description="Список основных репозиториев проекта:",
        color=disnake.Color.blue()
    )

    # Добавляем поля с информацией о репозиториях
    embed.add_field(
        name="🚀 Основной репозиторий (новая сборка)",
        value="[space_station_ADT](https://github.com/AdventureTimeSS14/space_station_ADT)",
        inline=False
    )
    embed.add_field(
        name="🛠️ Старый репозиторий (бывшая сборка)",
        value="[space_station](https://github.com/AdventureTimeSS14/space_station)",
        inline=False
    )
    embed.add_field(
        name="🤖 Репозиторий Discord-бота",
        value="[Dev-bot](https://github.com/AdventureTimeSS14/Dev-bot)",
        inline=False
    )

    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    # Отправляем Embed
    await ctx.send(embed=embed)

@bot.command(name="wiki")
async def wiki_info(ctx):
    """
    Выводит ссылки на основные разделы вики проекта.
    """
    # Создаем Embed с красивым оформлением
    embed = disnake.Embed(
        title="📖 Вики AdventureStation",
        description="Основные разделы вики. Выберите нужный:",
        color=disnake.Color.green()
    )

    sections = [
        ("🏠 Заглавная", "Заглавная_страница"),
        ("📋 Рабочие процедуры", "Стандартные_рабочие_процедуры"),
        ("⚖️ Корпоративный закон", "Корпоративный_закон"),
        ("👔 Командный состав", "Процедуры_командного_состава"),
        ("🛡️ Безопасность", "Процедуры_службы_безопасности"),
        ("⚖️ Юридический отдел", "Процедуры_юридического_отдела"),
        ("📟 Тен-коды", "Тен-коды"),
        ("🚫 Контрабанда", "Контрабанда"),
        ("📄 Бюрократия", "Бюрократическая_работа"),
        ("📊 Навыки", "Таблица_навыков")
    ]

    # Формируем список ссылок в одном поле для компактности
    wiki_url = "https://wiki.adventurestation.space/"
    embed.add_field(
        name="🔗 Ссылки на разделы",
        value="\n".join([f"[{name}]({wiki_url}{link})" for name, link in sections]),
        inline=False
    )

    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
