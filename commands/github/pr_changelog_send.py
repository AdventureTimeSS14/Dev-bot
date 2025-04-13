import re
from datetime import datetime, timezone

import disnake
import requests

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import (AUTHOR, CHANGELOG_CHANNEL_ID, REPOSITORIES,
                    WHITELIST_ROLE_ID)

MAX_FIELD_LENGTH = 1024  # Максимальный размер поля для Embed

def smart_truncate(text, max_length):
    """Умная обрезка текста: обрезает до максимальной длины, не разрывая слова или предложения."""
    if len(text) <= max_length:
        return text

    truncated_text = text[:max_length]
    last_period = truncated_text.rfind(".")
    if last_period == -1:
        return truncated_text[:max_length].strip() + "..."
    return truncated_text[:last_period + 1].strip() + "..."

def get_pr_url(pr_number):
    """Генерация URL для запроса к GitHub API по номеру пулл-реквеста."""
    return f'https://api.github.com/repos/{AUTHOR}/{REPOSITORIES["n"]}/pulls/{pr_number}'

def fetch_pr_data(url):
    """Получение данных пулл-реквеста с GitHub."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Добавлен timeout
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Ошибка при выполнении запроса к GitHub API: {e}")
        return None

def process_description(description):
    """Очищаем описание от комментариев и ищем текст изменений."""
    description = re.sub(r"<!--.*?-->", "", description, flags=re.DOTALL)
    match = re.search(r"(:cl:.*?|\U0001F191.*?)(\n|$)", description, re.DOTALL)
    if not match:
        return None, description
    cl_text = match.group(1).strip()
    remaining_lines = description[match.end():].strip()
    return cl_text, remaining_lines

@bot.command(
    name="pr",
    help="Получить информацию о замерженном пулл-реквесте по его номеру.",
)
@has_any_role_by_keys("whitelist_role_id")
async def get_pr_info(ctx, pr_number: int):
    """
    Команда для получения информации о замерженном пулл-реквесте из GitHub.
    """
    url = get_pr_url(pr_number)
    pr = fetch_pr_data(url)

    if not pr:
        await ctx.send("❌ Пулл-реквест не найден или произошла ошибка.")
        return

    # Проверяем, был ли пулл-реквест замержен
    if not pr.get("merged_at"):
        await ctx.send("❌ Этот пулл-реквест не был замержен.")
        return

    # Извлекаем данные о пулл-реквесте
    pr_data = {
        "merged_at": datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc), # pylint: disable=C0301
        "title": pr["title"],
        "url": pr["html_url"],
        "description": pr.get("body", "").strip(),
        "author_name": pr["user"]["login"],
        "coauthors": pr.get("coauthors", [])
    }

    # Обработка описания пулл-реквеста
    cl_text, remaining_lines = process_description(pr_data["description"])

    if not cl_text:
        await ctx.send("❌ Не удалось найти описание изменений.")
        return

    pr_data["description"] = f"{cl_text}\n{remaining_lines}" if remaining_lines else cl_text

    # Умная обрезка текста, если описание слишком длинное
    pr_data["description"] = smart_truncate(pr_data["description"], MAX_FIELD_LENGTH)

    # Формируем Embed для отображения данных
    embed = disnake.Embed(
        title=f"Пулл-реквест замержен: {pr_data['title']}",
        color=disnake.Color.dark_green(),
        timestamp=pr_data["merged_at"],
    )

    embed.add_field(name="Изменения:", value=pr_data["description"], inline=False)
    embed.add_field(name="Автор:", value=pr_data["author_name"], inline=False)
    embed.add_field(name="Ссылка:", value=f"[PR #{pr_number}]({pr_data['url']})", inline=False)

    if pr_data["coauthors"]:
        coauthors_str = "\n".join(pr_data["coauthors"])
        embed.add_field(name="Соавторы:", value=coauthors_str, inline=False)

    embed.set_footer(text="Дата мержа")

    # Отправляем Embed в канал с changelog
    channel = bot.get_channel(CHANGELOG_CHANNEL_ID)
    if channel is None:
        await ctx.send(f"❌ Канал с ID {CHANGELOG_CHANNEL_ID} не найден.")
        return

    try:
        message = await channel.send(embed=embed)
        await message.publish()
        await ctx.send(
            f"Информация о пулл-реквесте успешно отправлена в канал <#{CHANGELOG_CHANNEL_ID}>."
        )
    except disnake.Forbidden:
        await ctx.send("❌ У бота нет прав для отправки сообщений в указанный канал.")
    except disnake.HTTPException as e:
        print(f"❌ Ошибка при отправке Embed: {e}")
        await ctx.send("❌ Произошла ошибка при отправке информации о пулл-реквесте.")
