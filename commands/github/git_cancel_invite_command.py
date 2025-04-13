import disnake
import requests
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import ACTION_GITHUB, AUTHOR


def cancel_invitation_by_login(login: str):
    """Отменяет приглашение по логину пользователя в организацию GitHub."""
    url = f'https://api.github.com/orgs/{AUTHOR}/invitations'
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {ACTION_GITHUB}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        # Получаем список всех приглашений
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        invitations = response.json()

        # Ищем приглашение по логину пользователя
        for invitation in invitations:
            if invitation['login'] == login:
                invitation_id = invitation['id']
                # Отправляем запрос на отмену приглашения
                cancel_url = f'https://api.github.com/orgs/{AUTHOR}/invitations/{invitation_id}'
                cancel_response = requests.delete(cancel_url, headers=headers)
                cancel_response.raise_for_status()

                if cancel_response.status_code == 204:
                    return f"✅ Приглашение для пользователя `{login}` было отменено."
                else:
                    return f"❌ Ошибка при отмене приглашения для пользователя `{login}`."

        return f"❌ Приглашение для пользователя `{login}` не найдено."
    except requests.RequestException as e:
        return f"❌ Ошибка при отмене приглашения: {e}"

@bot.command(
    name="git_cancel_invite",
    help="Отменяет приглашение для пользователя по его логину на GitHub."
)
@has_any_role_by_keys("server_admin_post")
async def git_cancel_invite(ctx, login: str):
    """
    Команда для отмены приглашения для пользователя по его логину на GitHub.
    Параметры:
    - login: Логин пользователя, для которого нужно отменить приглашение.
    """
    result = cancel_invitation_by_login(login)
    await ctx.send(result)
