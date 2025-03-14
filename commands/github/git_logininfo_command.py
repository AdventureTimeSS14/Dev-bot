import asyncio

import aiohttp
import disnake
from disnake.ext import commands

from bot_init import bot
from config import ACTION_GITHUB, AUTHOR, REPOSITORIES

GRAPHQL_URL = "https://api.github.com/graphql"

# Запрос для получения информации о пулл-реквестах
graphql_query = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(states: [OPEN, CLOSED, MERGED], first: 100, after: $cursor) {
      edges {
        node {
          title
          url
          state
          mergedAt
          createdAt
          author {
            login
          }
          reviews(first: 10) {
            totalCount
          }
          comments(first: 10) {
            totalCount
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

async def get_github_pull_requests_graphql(username, repo):
    """Получает пулл-реквесты, связанные с пользователем в репозитории через GraphQL API."""
    headers = {
        "Authorization": f"Bearer {ACTION_GITHUB}",
        "Content-Type": "application/json",
    }

    all_pull_requests = []
    cursor = None
    has_next_page = True
    
    while has_next_page:
        variables = {
            "owner": AUTHOR,
            "repo": repo,
            "username": username,
            "cursor": cursor
        }

        data = {
            "query": graphql_query,
            "variables": variables
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(GRAPHQL_URL, json=data, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Проверяем наличие ключа 'data'
                    if 'data' not in result:
                        print(f"❌ Ошибка API: нет данных в ответе. Ответ: {result}")
                        return []

                    # Обрабатываем пулл-реквесты
                    pull_requests = result['data']['repository']['pullRequests']['edges']
                    for pr in pull_requests:
                        node = pr['node']
                        if node['author']['login'] == username:
                            pr_data = {
                                'url': node['url'],
                                'state': node['state'],
                                'merged_at': node['mergedAt'],
                                'reviews': node['reviews']['totalCount'],
                                'comments': node['comments']['totalCount']
                            }
                            all_pull_requests.append(pr_data)

                    # Обновляем курсор для следующей страницы
                    page_info = result['data']['repository']['pullRequests']['pageInfo']
                    has_next_page = page_info['hasNextPage']
                    cursor = page_info['endCursor']

            except aiohttp.ClientError as e:
                print(f"❌ Ошибка при выполнении запроса: {e}")
                return []

    return all_pull_requests

# Функция для получения информации о пользователе
async def get_github_user_info(username):
    """Получает информацию о пользователе GitHub."""
    url = f'https://api.github.com/users/{username}'
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {ACTION_GITHUB}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                user_info = await response.json()
                if not user_info:
                    print(f"❌ Нет данных о пользователе {username}")
                    return None
                return user_info
    except aiohttp.ClientError as e:
        print(f"❌ Ошибка при получении информации о пользователе: {e}")
        return None

@bot.command(
    name="git_logininfo",
    help="Выводит краткую статистику о пользователе и его вкладе в репозиторий."
)
async def git_logininfo(ctx, username: str):
    """
    Команда для вывода статистики пользователя по логину и его вкладе в репозиторий.
    """
    print(f"Получение информации о пользователе {username}...")

    # Получаем информацию о пользователе
    user_info = await get_github_user_info(username)

    if not user_info:
        await ctx.send("❌ Не удалось получить информацию о пользователе. Проверьте правильность логина.")
        return

    # Получаем пулл-реквесты для пользователя
    repo = 'space_station_ADT'  # Указываем репозиторий
    print(f"Получение пулл-реквестов для пользователя {username} из репозитория {repo}...")

    user_pull_requests = await get_github_pull_requests_graphql(username, repo)

    if not user_pull_requests:
        print(f"❌ Нет пулл-реквестов для пользователя {username} в репозитории {repo}.")
        await ctx.send(f"❌ Нет пулл-реквестов для пользователя {username} в репозитории {repo}.")
        return

    # Инициализируем счетчики для различных типов пулл-реквестов
    merged_prs = 0
    closed_prs = 0
    open_prs = 0
    draft_prs = 0
    total_reviews = 0
    total_discussions = 0
    total_prs = len(user_pull_requests)

    # Обрабатываем пулл-реквесты
    for pr in user_pull_requests:
        pr_state = pr['state']
        pr_url = pr['url']
        print(f"Обрабатываем пулл-реквест: {pr_url}, состояние: {pr_state}")

        # Подсчитываем количество пулл-реквестов по состояниям
        if pr_state == 'MERGED':
            merged_prs += 1
        if pr_state == 'CLOSED':  # Если пулл-реквест был закрыт
            closed_prs += 1
        if pr_state == 'OPEN':  # Если пулл-реквест открыт
            open_prs += 1
        if pr_state == 'DRAFT':  # Если пулл-реквест в драфте
            draft_prs += 1

        total_reviews += pr['reviews']
        total_discussions += pr['comments']

    # Создаём Embed с красивым дизайном
    embed = disnake.Embed(
        title=f"Информация о пользователе GitHub: {username} 👤",
        description=f"**Имя пользователя**: `{username}`\n**Организация**: `{AUTHOR}`",
        color=disnake.Color.green(),
        timestamp=disnake.utils.utcnow()
    )

    # Добавляем основную информацию о пользователе
    embed.add_field(
        name="📝 Основная информация",
        value=f"**Имя**: {user_info.get('name', 'Не указано')}\n"
              f"**Подписки**: {user_info.get('following', 'Не указано')}\n"
              f"**Подписчики**: {user_info.get('followers', 'Не указано')}\n"
              f"**Репозитории**: {user_info.get('public_repos', 'Не указано')}",
        inline=False
    )

    # Добавляем информацию о вкладе в репозиторий
    embed.add_field(
        name="🔧 Вклад в репозиторий",
        value=f"**Общее количество пулл-реквестов**: {total_prs}\n"
              f"**Замерженные пулл-реквесты**: {merged_prs}\n"
              f"**Закрытые пулл-реквесты**: {closed_prs}\n"
              f"**Открытые пулл-реквесты**: {open_prs}\n"
              f"**Пулл-реквесты в драфте**: {draft_prs}\n"
              f"**Общее количество ревью**: {total_reviews}\n"
              f"**Общее количество дискуссий**: {total_discussions}",
        inline=False
    )

    # Добавляем аватар пользователя
    embed.set_thumbnail(url=user_info.get('avatar_url', 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'))
    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
    
    # Отправляем Embed в канал
    await ctx.send(embed=embed)