from datetime import datetime

import disnake
import requests

from config import AUTHOR, GLOBAL_SESSION, REPOSITORIES

async def fetch_github_data(url):
    """Делает GET-запрос и возвращает JSON-ответ."""
    try:
        response = GLOBAL_SESSION.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"❌ Ошибка при запросе к GitHub API: {e}")
        return None

def get_pr_status(pr_data):
    """Возвращает статус PR и цвет для Embed."""
    state = pr_data['state']
    merged = pr_data.get('merged', False)
    draft = pr_data.get('draft', False)

    if state == 'closed' and merged:
        return "Замерджен 💜", disnake.Color.purple()
    elif state == 'closed' and not merged:
        return "Закрыт ❌", disnake.Color.red()
    elif state == 'open' and draft:
        return "В драфте ⚙️", disnake.Color.darker_gray()
    elif state == 'open':
        return "Открыт ✅", disnake.Color.green()

    return "Неизвестный статус ❓", disnake.Color.default()

async def get_reviewers(pr_url):
    """Возвращает список логинов ревьюеров (назначенных и одобривших)."""
    reviews_url = f"{pr_url}/reviews"
    reviews_data = await fetch_github_data(reviews_url)

    if not reviews_data:
        return [], []

    # Назначенные ревьюеры
    requested_reviewers = {r['login'] for r in reviews_data if 'state' not in r}

    # Одобрившие PR
    approved_reviewers = {r['user']['login'] for r in reviews_data if r['state'] == 'APPROVED'}

    return requested_reviewers, approved_reviewers

def format_labels(labels):
    """Форматирует метки GitHub для Embed."""
    return ', '.join(f"[{label['name']}]" for label in labels) if labels else "Нет меток 🏷️"

async def get_github_link(repo_code, number):
    """Проверяет существование GitHub issue или PR и возвращает ссылку или Embed."""
    repo_name = REPOSITORIES.get(repo_code)
    if not repo_name:
        print(f"⚠️ Репозиторий с кодом {repo_code} не найден.")
        return None

    base_api_url = f"https://api.github.com/repos/{AUTHOR}/{repo_name}"
    pr_url = f"{base_api_url}/pulls/{number}"

    pr_data = await fetch_github_data(pr_url)
    if not pr_data:
        issue_url = f"{base_api_url}/issues/{number}"
        issue_data = await fetch_github_data(issue_url)
        return f"[{repo_name} Issue {number}]({issue_data['html_url']})" if issue_data else None

    # Определяем статус и цвет Embed
    state_description, embed_color = get_pr_status(pr_data)

    embed = disnake.Embed(
        title=f"PR #{number} - {pr_data['title']}",
        color=embed_color
    )
    embed.add_field(name="Статус PR", value=state_description, inline=True)
    embed.add_field(name="Создатель PR 👨‍💻", value=pr_data['user']['login'], inline=True)

    # Получаем ревьюеров
    requested_reviewers, approved_reviewers = await get_reviewers(pr_url)
    embed.add_field(
        name="Ревьюеры 🔍",
        value=", ".join(requested_reviewers) or "Нет",
        inline=True
    )
    embed.add_field(
        name="Одобрение 🌟",
        value=", ".join(approved_reviewers) or "Нет одобрений",
        inline=True
    )

    # Метки
    embed.add_field(
        name="Метки 🏷️",
        value=format_labels(pr_data.get('labels', [])),
        inline=True
    )

    # Количество комментариев
    embed.add_field(
        name="Комментарии 💬",
        value=pr_data['comments'],
        inline=True
    )

    # Ссылка на PR
    embed.add_field(
        name="Ссылка на PR 🔗",
        value=f"[Перейти в PR]({pr_data['html_url']})",
        inline=False
    )

    return embed
