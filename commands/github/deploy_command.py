import base64
import requests
from config import GITHUB, AUTHOR, REPO_NAME, SERVER_ADMIN_POST
from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id


FILE_PATH = ".github/workflows/deploy.yml"
BRANCH = "main"


@bot.command(name="deploy")
@has_any_role_by_id(SERVER_ADMIN_POST)
async def deply_command(ctx, agr: str):
    """
        Делает коммит в файл запуска акшона бота
    """
    if agr not in ["on", "off"]:
        await ctx.send("❌ Укажите: `on` или `off`")
        return

    url = f"https://api.github.com/repos/{AUTHOR}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB}"}

    # Получаем текущее содержимое файла
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        await ctx.send("❌ Ошибка получения файла `deploy.yml`")
        return

    content = response.json()
    sha = content["sha"]
    decoded_content = base64.b64decode(content["content"]).decode("utf-8")

    # Обновляем строку с `- cron: '*/10 * * * *''`
    new_content = []
    for line in decoded_content.split("\n"):
        if line.strip().startswith("- cron: '*/10 * * * *'") and agr == "off":
            new_content.append(f"    # - cron: '*/10 * * * *'")
        elif line.strip().startswith("# - cron: '*/10 * * * *'") and agr == "on":
            new_content.append(f"    - cron: '*/10 * * * *'")
        else:
            new_content.append(line)

    updated_content = "\n".join(new_content)
    encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

    # Создаем коммит с обновленным файлом
    data = {
        "message": f"🔄 Переключение режима деплоя на `{agr}`",
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }

    commit_response = requests.put(url, headers=headers, json=data)
    if commit_response.status_code == 200 or commit_response.status_code == 201:
        await ctx.send(f"✅ Файл `deploy.yml` обновлен!")
    else:
        await ctx.send("❌ Ошибка обновления `deploy.yml`")
