import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys

from .github_processor import (create_embed_list, fetch_github_data,
                               send_embeds, validate_repository)


@bot.command(name="milestones")
@has_any_role_by_keys("whitelist_role_id")
async def milestones(ctx, repo_key: str):
    """
    Команда для получения списка Milestones в GitHub репозитории.

    Аргументы:
    ctx -- контекст команды
    repo_key -- ключ репозитория для поиска

    Возвращает:
    Отправляет список milestones в чат.
    """
    repository_name = await validate_repository(ctx, repo_key)
    if not repository_name:
        return

    url = f"https://api.github.com/repos/{repository_name}/milestones"
    milestones_data = await fetch_github_data(url)

    if not milestones_data:
        await ctx.send("Milestones не найдены.")
        return

    milestones_list = [
        {
            "title": milestone["title"],
            "url": milestone["url"],
            "due_date": milestone["due_on"],
            "completion": (
                f"{(milestone['closed_issues'] / (milestone['open_issues'] + milestone['closed_issues'])) * 100:.2f}%" # pylint: disable=C0301
                if milestone["open_issues"] + milestone["closed_issues"] > 0
                else "0%"
            ),
            "open_issues": milestone["open_issues"],
            "closed_issues": milestone["closed_issues"],
        }
        for milestone in milestones_data
    ]

    embed_list = await create_embed_list(
        f"Список Milestones. \nРепозиторий: {repository_name}",
        milestones_list,
        disnake.Color.blue(),
        lambda milestone: {
            "name": milestone["title"],
            "value": (
                f"Ссылка: {milestone['url']}\n"
                f"Дата завершения: {milestone['due_date']}\n"
                f"Закрытые задачи: {milestone['closed_issues']}\n"
                f"Открытые задачи: {milestone['open_issues']}\n"
                f"Процент выполнения: {milestone['completion']}"
            ),
            "inline": False,
        },
    )

    await send_embeds(ctx, embed_list)


@milestones.error
async def milestones_error(ctx, error):
    """
    Обработчик ошибок для команды milestones.

    Аргументы:
    ctx -- контекст команды
    error -- объект ошибки
    """
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Вы не указали ключ к репозиторию. Указать ключ к репозиторию можно следующим "
            "образом: `&milestones n`, `&milestones o`"
        )
