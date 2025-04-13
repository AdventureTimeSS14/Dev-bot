import disnake
import requests
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import ACTION_GITHUB, AUTHOR


def invite_to_github_org(username_or_email):
    """Приглашает пользователя в организацию GitHub."""
    url = f'https://api.github.com/orgs/{AUTHOR}/invitations'
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {ACTION_GITHUB}"
    }

    # Попытка получить ID пользователя по логину
    response = requests.get(f'https://api.github.com/users/{username_or_email}', headers=headers)
    if response.status_code == 200:
        invitee_id = response.json()['id']
        data = {"invitee_id": invitee_id}
    else:
        # Если логин не найден, используем email
        data = {"email": username_or_email}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return f"✅ Приглашение отправлено пользователю {username_or_email}."
    except requests.RequestException as e:
        print(f"❌ Ошибка при отправке приглашения: {e}")
        return f"❌ Не удалось отправить приглашение пользователю {username_or_email}."

def remove_from_github_org(username):
    """Удаляет пользователя из организации GitHub."""
    url = f'https://api.github.com/orgs/{AUTHOR}/memberships/{username}'
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {ACTION_GITHUB}"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return f"✅ Пользователь {username} был удален из организации."
    except requests.RequestException as e:
        print(f"❌ Ошибка при удалении пользователя: {e}")
        return f"❌ Не удалось удалить пользователя {username} из организации."

@bot.command(
    name="git_invite",
    help="Приглашает пользователя в организацию GitHub по логину."
)
@has_any_role_by_keys("server_admin_post")
async def git_invite(ctx, username: str):
    """
    Команда для отправки приглашения пользователю в организацию на GitHub.
    """
    result = invite_to_github_org(username)
    await ctx.send(result)
@bot.command(
    name="git_remove",
    help="Удаляет пользователя из организации GitHub."
)
@has_any_role_by_keys("server_admin_post")
async def git_remove_team(ctx, username: str):
    """
    Команда для удаления пользователя из организации на GitHub.
    """
    result = remove_from_github_org(username)
    await ctx.send(result)
