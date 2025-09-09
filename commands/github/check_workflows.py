import sys

import aiohttp

from bot_init import bot
from config import AUTHOR, GITHUB
from Tools import get_http_session

OWNER = AUTHOR
REPO = 'Dev-bot'
API_URL = f'https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?workflow=run_on_github.yml' # !!!!!!


# Заголовки для аутентификации
HEADERS = {
    "Authorization": f"token {GITHUB}",
    "Accept": "application/vnd.github.v3+json",
}


async def check_workflows():
    """
    Проверяет состояние запущенных GitHub Actions workflows
    и завершает работу бота,
    если обнаружено более одного процесса с состоянием 
    'in_progress' для workflow с именем 'Deploy Discord-Bot'.
    """
    try:
        session = await get_http_session()
        async with session.get(API_URL, headers=HEADERS) as response:
            if response.status != 200:
                print(
                    f"❌ Ошибка при подключении к GitHub API. Статус: {response.status}"
                )
                sys.exit(1)

            workflows = await response.json()

        # Счётчик для процессов 'in_progress'
        in_progress_count = 0  # Количество процессов со статусом 'in_progress'
        deploy_workflows = []

        # Проверяем все workflows
        for run in workflows.get("workflow_runs", []):
            run_name = run.get("name", "Неизвестно")

            # Проверяем, что имя процесса соответствует 'Deploy Discord-Bot'
            if run_name == "Deploy Discord-Bot":
                status = run.get("status", "Неизвестно")

                # Логируем информацию о процессе
                print(f"  - Название: {run_name}")
                print(f"    Статус: {status}")
                print(f"    Дата начала: {run.get('created_at', 'Неизвестно')}")
                print()

                # Если процесс в статусе 'in_progress', увеличиваем счётчик
                if status == "in_progress":
                    in_progress_count += 1
                    deploy_workflows.append(run)

        # Если более одного процесса в статусе 'in_progress', завершаем работу
        if in_progress_count > 1:
            print("❌ Обнаружено более одного запущенного workflow "
                  "'Deploy Discord-Bot'. Завершаем процесс... "
                  f"in_progress_count = {in_progress_count}\n"
                  f"Список запущенных:\n{deploy_workflows}")
            # Закрываем бота и завершаем выполнение скрипта
            await bot.close()
            sys.exit(0)

        # Логируем результаты проверки
        if in_progress_count == 0:
            print(
                "✅ Нет запущенных workflow 'Deploy Discord-Bot' "
                "в статусе 'in_progress'. Продолжаем работу."
            )
        else:
            print(
                f"⚠️ Обнаружено {in_progress_count} запущенный(ых) workflow "
                f"'Deploy Discord-Bot' в статусе 'in_progress'. Продолжаем работу."
            )

    except aiohttp.ClientError as e:
        print(f"❌ Ошибка при подключении к GitHub API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        sys.exit(1)
