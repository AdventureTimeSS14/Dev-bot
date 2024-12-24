import sys

import requests
from discord.ext import tasks

from bot_init import bot
from commands.misc.shutdows_deff import shutdown_def
from config import AUTHOR, GITHUB, LOG_CHANNEL_ID

OWNER = AUTHOR
REPO = 'Dev-bot'  # Название вашего репозитория
API_URL = f'https://api.github.com/repos/{OWNER}/{REPO}/commits'

# Заголовки для аутентификации
headers = {
    'Authorization': f'token {GITHUB}',
    'Accept': 'application/vnd.github.v3+json',
}

last_commit_sha = None

# Функция для получения состояния последнего коммита
async def check_for_new_commit():
    global last_commit_sha
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP

        commits = response.json()

        if not commits:
            print("Нет коммитов в репозитории.")
            return False, None  # Возвращаем False и None, если коммитов нет

        # Получаем SHA последнего коммита
        latest_commit_sha = commits[0]['sha']
        commit_message = commits[0]['commit']['message']  # Сообщение коммита
        commit_url = commits[0]['html_url']  # URL для просмотра коммита на GitHub

        # Получаем подробности коммита, включая диффы
        commit_details_response = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/commits/{latest_commit_sha}', headers=headers)
        commit_details_response.raise_for_status()
        commit_details = commit_details_response.json()

        # Извлекаем информацию о добавленных и удалённых строках
        additions = commit_details['stats']['additions']
        deletions = commit_details['stats']['deletions']
        
        # Получаем информацию об авторах и соавторах
        author = commit_details['commit']['author']['name']
        committer = commit_details['commit']['committer']['name']
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
                'message': commit_message,
                'sha': latest_commit_sha,
                'url': commit_url,
                'additions': additions,
                'deletions': deletions,
                'author': author,
                'committer': committer,
                'coauthors': coauthors,
            }

        # Если SHA не изменился, то коммит не новый
        print("Новых коммитов нет.")
        return False, None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к GitHub API: {e}")
        sys.exit(1)


# Проверка о получении новых коммитах
@tasks.loop(seconds=50)
async def monitor_commits():
    new_commit_found, commit_data = await check_for_new_commit()

    if new_commit_found:
        print("Перезапуск бота из-за нового коммита.")
        
        # Получаем данные о последнем коммите
        commit_message = commit_data['message']
        commit_sha = commit_data['sha']
        commit_url = commit_data['url']
        additions = commit_data['additions']
        deletions = commit_data['deletions']
        author = commit_data['author']
        committer = commit_data['committer']
        coauthors = commit_data['coauthors']

        message = f"**Обнаружен новый коммит!** Перезапуск бота для обновления...\n\n"
        message += f"**Сообщение коммита**: {commit_message}\n"
        message += f"**SHA**: {commit_sha}\n"
        message += f"**URL**: `{commit_url}`\n\n"
        message += f"**Автор**: {author}\n"
        message += f"**Коммиттер**: {committer}\n"
        
        if coauthors:
            message += f"**Соавторы**:\n" + "\n".join(coauthors) + "\n"
        
        message += f"\n**Изменения**:\n"
        message += f"```diff\n"
        message += f"+ Добавлено строк: {additions}\n"
        message += f"- Удалено строк: {deletions}\n"
        message += f"```"
        
        # Отправляем сообщение в Discord канал о новом коммите
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(message)
            
        await shutdown_def()

        # Завершаем работу бота
        await bot.close()
        sys.exit(0)
