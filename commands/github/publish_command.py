import disnake
import requests
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import ACTION_GITHUB, AUTHOR, REPOSITORIES, WHITELIST_ROLE_ID


# Функция для запуска GitHub Actions workflow
def trigger_github_action(repository, branch):
    """Запускает GitHub Actions для указанного репозитория и ветки."""
    url = f'https://api.github.com/repos/{AUTHOR}/{REPOSITORIES[repository]}/actions/workflows/publish-adt.yml/dispatches'
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {ACTION_GITHUB}"
    }
    
    data = {
        "ref": branch,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Проверка на успешность запроса
        return True
    except requests.RequestException as e:
        print(f"❌ Ошибка при запуске GitHub Action: {e}")
        return False

@bot.command(
    name="publish",
    help="Запускает GitHub Actions workflow для указанной ветки репозитория. По умолчанию используется репозиторий 'n'."
)
@has_any_role_by_id(WHITELIST_ROLE_ID)
async def publish(ctx, branch: str, repository: str = "n"):
    """
    Команда для запуска GitHub Actions для репозитория 'n' или 'o'. 
    Если не указан репозиторий, по умолчанию будет выбран 'n'.
    """
    if repository not in ['n', 'o']:
        await ctx.send("❌ Указан неверный репозиторий. Используйте 'n' или 'o'.")
        return

    # Проверка правильности ветки
    if not branch:
        await ctx.send("❌ Укажите ветку для запуска действия.")
        return

    # Запуск GitHub Actions
    success = trigger_github_action(repository, branch)

    # Создаём Embed с красивым дизайном
    embed = disnake.Embed(
        title="GitHub Actions - Запуск Publish",
        description=f"**Репозиторий**: `{REPOSITORIES[repository]}`\n**Ветка**: `{branch}`",
        color=disnake.Color.green() if success else disnake.Color.red(),
        timestamp=disnake.utils.utcnow()
    )

    # Эмодзи и стили
    embed.set_thumbnail(url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    # Если успешно
    if success:
        embed.add_field(
            name="✅ Запуск успешен!",
            value="GitHub Actions publish-adt.yml для указанной ветки был успешно запущен.",
            inline=False
        )
    else:
        embed.add_field(
            name="❌ Ошибка",
            value="Не удалось запустить GitHub Actions. Проверьте правильность данных или настройки токена.",
            inline=False
        )

    # Отправляем Embed в канал
    await ctx.send(embed=embed)
