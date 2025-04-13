import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys

from .github_processor import (create_embed_list, fetch_github_data,
                               send_embeds, validate_repository)


@bot.command(name="achang")
@has_any_role_by_keys("whitelist_role_id")
async def achang(ctx, repo_key: str):
    """
    Команда для получения списка пулл-реквестов, которые требуют изменений.
    """
    # Валидируем ключ репозитория
    repository_name = await validate_repository(ctx, repo_key)
    if not repository_name:
        return

    # Формируем URL для GitHub API
    url = f"https://api.github.com/repos/{repository_name}/pulls"
    pulls = await fetch_github_data(
        url, {"state": "open", "sort": "created", "base": "master"}
    )

    # Если нет открытых пулл-реквестов
    if not pulls:
        await ctx.send("Пулл-реквесты не найдены или не требуют изменений.")
        return

    # Фильтруем пулл-реквесты с лейблом "Status: Awaiting Changes"
    pull_requests_list = [
        {
            "title": pr.get("title", "Без названия"),
            "url": pr.get("html_url", "Нет ссылки"),
            "author": pr["user"].get("login", "Неизвестно"),
            "requested_by": [
                reviewer.get("login", "Неизвестно")
                for reviewer in pr.get("requested_reviewers", [])
            ],
        }
        for pr in pulls
        if any(
            label.get("name") == "Status: Awaiting Changes"
            for label in pr.get("labels", [])
        )
    ]

    # Если нет пулл-реквестов, требующих изменений
    if not pull_requests_list:
        await ctx.send("Нет пулл-реквестов, требующих изменений.")
        return

    # Создаем список Embed для отображения
    embed_list = await create_embed_list(
        f"Список пулл-реквестов, требующих изменений. \nРепозиторий: {repository_name}",
        pull_requests_list,
        disnake.Color.dark_gold(),
        lambda pr: {
            "name": pr["title"],
            "value": (
                f"Автор: {pr['author']}\n"
                f"Чьё ревью запрошено: "
                f"{', '.join(pr['requested_by']) if pr['requested_by'] else 'Нет запрашиваемых рецензентов'}\n" # pylint: disable=C0301
                f"Ссылка: {pr['url']}"
            ),
            "inline": False,
        },
    )

    # Отправляем Embed в канал
    await send_embeds(ctx, embed_list)


@achang.error
async def achang_error(ctx, error):
    """
    Обработчик ошибок для команды achang.
    """
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Вы не указали ключ к репозиторию. "
            "Указать ключ к репозиторию можно "
            "следующим образом: `&achang n`, `&achang o`"
        )
    else:
        await ctx.send(f"Произошла ошибка: {error}")
