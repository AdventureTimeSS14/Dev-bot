import sys

import requests
from disnake.ext import tasks

from bot_init import bot
from commands.misc.shutdows_deff import shutdown_def
from config import AUTHOR, GITHUB, LOG_CHANNEL_ID

OWNER = AUTHOR
REPO = "Dev-bot"  # Название вашего репозитория
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/commits"

# Заголовки для аутентификации
headers = {
    "Authorization": f"token {GITHUB}",
    "Accept": "application/vnd.github.v3+json",
}

last_commit_sha = None

def get_commit_details(commit_sha: str):
    """
    Получает подробности коммита с использованием его SHA.
    """
    try:
        commit_details_response = requests.get(
            f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{commit_sha}",
            headers=headers, timeout=10  # Добавлен timeout
        )
        commit_details_response.raise_for_status()
        return commit_details_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении деталей коммита {commit_sha}: {e}")
        return None


async def check_for_new_commit():
    """
    Проверяет наличие нового коммита в репозитории.
    """
    global last_commit_sha # pylint: disable=W0603
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)  # Добавлен timeout
        response.raise_for_status()  # Проверка на ошибки HTTP

        commits = response.json()

        if not commits:
            print("Нет коммитов в репозитории.")
            return False, None  # Возвращаем False и None, если коммитов нет

        # Получаем SHA последнего коммита
        latest_commit_sha = commits[0]["sha"]
        commit_message = commits[0]["commit"]["message"]  # Сообщение коммита
        commit_url = commits[0]["html_url"]  # URL для просмотра коммита на GitHub

        # Получаем подробности коммита, включая диффы
        commit_details = get_commit_details(latest_commit_sha)
        if not commit_details:
            return False, None

        # Извлекаем информацию о добавленных и удалённых строках
        additions = commit_details["stats"]["additions"]
        deletions = commit_details["stats"]["deletions"]

        # Получаем информацию об авторах и соавторах
        author = commit_details["commit"]["author"]["name"]
        committer = commit_details["commit"]["committer"]["name"]
        coauthors = []
        for author_line in commit_message.splitlines():
            if "Co-authored-by" in author_line:
                coauthors.append(author_line)

        # Проверяем, если SHA текущего коммита отличается от сохранённого, то это новый коммит
        if last_commit_sha is None:
            # Это первый запуск, сохраняем SHA последнего коммита и ничего не делаем
            last_commit_sha = latest_commit_sha
            return False, None  # Не новый коммит на первом запуске

        # Если SHA изменился, значит есть новый коммит
        if latest_commit_sha != last_commit_sha:
            last_commit_sha = latest_commit_sha  # Обновляем последний SHA
            print(f"Новый коммит найден! SHA: {latest_commit_sha}")
            return True, {
                "message": commit_message,
                "sha": latest_commit_sha,
                "url": commit_url,
                "additions": additions,
                "deletions": deletions,
                "author": author,
                "committer": committer,
                "coauthors": coauthors,
            }

        # Если SHA не изменился, то коммит не новый
        print("Новых коммитов нет.")
        return False, None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к GitHub API: {e}")
        sys.exit(1)


@tasks.loop(seconds=50)
async def monitor_commits():
    """
    Проверяет наличие новых коммитов каждые 50 секунд.
    При обнаружении нового коммита, перезапускает бота.
    """
    new_commit_found, commit_data = await check_for_new_commit()

    if new_commit_found:
        print("Перезапуск бота из-за нового коммита.")

        # Получаем данные о последнем коммите
        commit_message = commit_data["message"]
        commit_sha = commit_data["sha"]
        commit_url = commit_data["url"]
        additions = commit_data["additions"]
        deletions = commit_data["deletions"]
        author = commit_data["author"]
        committer = commit_data["committer"]
        coauthors = commit_data["coauthors"]

        message = (
            f"**Обнаружен новый коммит!** Перезапуск бота для обновления...\n\n"
            f"**Сообщение коммита**: {commit_message}\n"
            f"**SHA**: {commit_sha}\n"
            f"**URL**: `{commit_url}`\n\n"
            f"**Автор**: {author}\n"
            f"**Коммиттер**: {committer}\n"
        )

        if coauthors:
            message += "**Соавторы**:\n" + "\n".join(coauthors) + "\n"

        message += "\n**Изменения**:\n```diff\n"
        message += "+ Добавлено строк: " + str(additions) + "\n"
        message += "- Удалено строк: " + str(deletions) + "\n"
        message += "```"

        # Отправляем сообщение в Discord канал о новом коммите
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(message)

        # # Отправляем личное сообщение владельцу
        # try:
        #     user = bot.get_user(MY_USER_ID) or await bot.fetch_user(MY_USER_ID)
        #     if user:
        #         await user.send(message)
        # except Exception:  # noqa: BLE001 — уведомление не критично для рестарта
        #     pass

        await shutdown_def()

        # Завершаем работу бота
        await bot.close()
        sys.exit(0)
