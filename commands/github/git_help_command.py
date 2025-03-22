import disnake
from disnake.ext import commands

from bot_init import bot
from components.button_help_components import (action_row_bug_report,
                                               action_row_button_help)

COLOR = disnake.Color.dark_purple()

@bot.command(name="git_help")
async def git_help(ctx: commands.Context):
    """
    Выводит список доступных команд для работы с GitHub.
    """
    try:
        # Данные для команды git_help
        help_command_text = {
            "title": "🛠 Помощь по командам GitHub 💻",
            "name_1": "Основные команды:",
            "context_1": (
                "📝 **&achang <repo_key>** - Получает список пулл-реквестов, которые требуют изменений.\n"
                "🌿 **&branch <repository>** - Получает список веток репозитория. Можно указать 'n' или 'o'.\n"
                "🍴 **&forks <repo_key>** - Получает список форков заданного репозитория.\n"
                "🔧 **&pr <numer_pr>** - По указанному номеру пулл реквеста формирует и отправляет чейнжлог в дискорд канал.\n"
            ),
            "name_2": "Управление пулл-реквестами:",
            "context_2": (
                "📝 **&review <repo_key>** - Получает список пулл-реквестов, которые требуют ревью.\n"
                "🏆 **&milestones <repo_key>** - Получает список Milestones в GitHub репозитории.\n"
            ),
            "name_3": "GitHub Actions:",
            "context_3": (
                "🚀 **&publish <branch>** - Запускает GitHub Actions workflow для указанной ветки репозитория.\n"
                "📈 **&publish_status** - Выводит результаты последнего запуска GitHub Actions workflow 'publish-adt.yml'.\n"
            ),
            "name_4": "Управление участниками:",
            "context_4": (
                "📊 **&git_logininfo <username>** - Выводит краткую статистику пользователя и его вклад в репозиторий. (В РАБОТЕ)\n"
                "📂 **&git_repoinfo** - Выводит информацию о репозитории *AdventureTimeSS14/space_station_ADT*.\n"
                "👥 **&git_team** - Выводит список участников организации на GitHub.\n"
                "🛠️ **&add_maint <github_login>** - Добавляет участника в команду *adt_maintainer* на GitHub.\n"
                "🛠️ **&del_maint <github_login>** - Удаляет участника из команды *adt_maintainer* на GitHub.\n"
                "💌 **&git_invite <username>** - Приглашает пользователя в организацию GitHub.\n"
                "❌ **&git_cancel_invite <username>** - Отменяет приглашение для пользователя.\n"
                "🗑️ **&git_remove <username>** - Удаляет пользователя из организации GitHub.\n"
                "🔴 **&git_pending_invites <page> <per_page> <role>** - Выводит список пользователей с ожидающими приглашениями в организацию на GitHub.\n"
            ),
        }

        # Создаем embed-сообщение
        embed = disnake.Embed(
            title=help_command_text["title"], color=COLOR
        )

        # Добавляем каждый раздел как отдельное поле
        embed.add_field(
            name=help_command_text["name_1"],
            value=help_command_text["context_1"],
            inline=False,
        )
        embed.add_field(
            name=help_command_text["name_2"],
            value=help_command_text["context_2"],
            inline=False,
        )
        embed.add_field(
            name=help_command_text["name_3"],
            value=help_command_text["context_3"],
            inline=False,
        )
        embed.add_field(
            name=help_command_text["name_4"],
            value=help_command_text["context_4"],
            inline=False,
        )

        # Устанавливаем аватар автора embed
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else None
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)

        # Футер с деталями
        embed.set_footer(
            text=f"Запрос от {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

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
            f"❌ Произошла ошибка при выполнении команды `git_help`: {e}\n"
            f"Пользователь: {ctx.author} (ID: {ctx.author.id})"
        )
        print(error_message)  # Логирование в консоль
        await ctx.send(
            "Произошла ошибка при выполнении команды. Пожалуйста, попробуйте позже."
        )
