import disnake
import requests
from disnake.ext import commands

from bot_init import bot
from config import ACTION_GITHUB, AUTHOR


def get_pending_invitations(page=1, per_page=30, role="all"):
    """Получает список ожидающих приглашений в организацию GitHub."""
    url = f'https://api.github.com/orgs/{AUTHOR}/invitations'
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {ACTION_GITHUB}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    params = {
        "page": page,
        "per_page": per_page,
        "role": role
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        invitations = response.json()

        if not invitations:
            return "❌ Нет ожидающих приглашений в организацию."

        # Формируем список логинов пользователей с ожидающими приглашениями
        pending_invitations = [invitation['login'] for invitation in invitations]

        if not pending_invitations:
            return "❌ Нет ожидающих приглашений в организацию."

        return pending_invitations
    except requests.RequestException as e:
        return f"❌ Ошибка при получении приглашений: {e}"

@bot.command(
    name="git_pending_invites",
    help="Выводит список пользователей с ожидающими приглашениями в организацию на GitHub."
)
async def git_pending_invites(ctx, page: int = 1, per_page: int = 30, role: str = "all"):
    """
    Команда для вывода списка пользователей с ожидающими приглашениями в организацию на GitHub.
    Параметры:
    - page: Номер страницы для получения результатов.
    - per_page: Количество результатов на странице.
    - role: Фильтрует приглашения по роли.
    """
    pending_invitations = get_pending_invitations(page, per_page, role)

    if isinstance(pending_invitations, str):
        await ctx.send(pending_invitations)
        return

    # Создаем Embed для красивого отображения
    embed = disnake.Embed(
        title="📝 Ожидающие приглашения в организацию на GitHub",
        description=f"**Организация**: `{AUTHOR}`\n\n**Ожидающие приглашения**:\n",
        color=disnake.Color.dark_grey(),
        timestamp=disnake.utils.utcnow()
    )

    # Форматируем список с пользователями
    formatted_invitations = ""
    for invitation in pending_invitations:
        formatted_invitations += f"• **{invitation}**\n"  # добавляем имя пользователя с жирным шрифтом и буллет-точкой

    # Проверяем длину текста и сокращаем, если необходимо
    if len(formatted_invitations) > 2000:
        formatted_invitations = formatted_invitations[:2000] + "..."  # если слишком много данных, обрезаем

    # Добавляем список приглашений в Embed
    embed.add_field(name="Пользователи", value=formatted_invitations, inline=False)

    # Добавляем footer с дополнительной информацией
    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    # Отправляем Embed в канал
    await ctx.send(embed=embed)
