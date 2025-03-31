import base64
import json

import discord
import requests

from bot_init import bot
from config import AUTHOR, GITHUB, REPO_NAME

FILE_PATH = ".github/workflows/deploy.yml"
BRANCH = "main"


@bot.command()
async def bot_branch(ctx, branch: str):
    """
        Делает коммит в файл запуска акшона бота
    """
    if branch not in ["main", "dev"]:
        await ctx.send("❌ Укажите ветку: `main` или `dev`")
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

    # Обновляем строку с `if: github.ref == 'refs/heads/...'`
    new_content = []
    for line in decoded_content.split("\n"):
        if line.strip().startswith("if: github.ref == 'refs/heads/"):
            new_content.append(f"    if: github.ref == 'refs/heads/{branch}'")
        else:
            new_content.append(line)

    updated_content = "\n".join(new_content)
    encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

    # Создаем коммит с обновленным файлом
    data = {
        "message": f"🔄 Автообновление: смена ветки на {branch}",
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }

    commit_response = requests.put(url, headers=headers, json=data)
    if commit_response.status_code == 200 or commit_response.status_code == 201:
        await ctx.send(f"✅ Файл `deploy.yml` обновлен! Ветка для деплоя: `{branch}`")
    else:
        await ctx.send("❌ Ошибка обновления `deploy.yml`")
