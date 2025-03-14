import re
from datetime import datetime, timezone

import disnake
from disnake.ext import tasks

from bot_init import bot
from commands.github.github_processor import fetch_github_data
from config import (AUTHOR, CHANGELOG_CHANNEL_ID, LOG_CHANNEL_ID, REPOSITORIES,
                    SECOND_UPDATE_CHANGELOG)

MAX_FIELD_LENGTH = 1024  # Максимальный размер поля для Embed

# Переменная для отслеживания последнего времени проверки
LAST_CHECK_TIME: datetime = None


def smart_truncate(text, max_length):
    """Умная обрезка текста: обрезает до максимальной длины, не разрывая слова или предложения."""
    if len(text) <= max_length:
        return text

    # Ищем последнее завершенное предложение перед обрезкой
    truncated_text = text[:max_length]
    last_period = truncated_text.rfind(".")

    if last_period == -1:  # Если нет точки, обрезаем просто по лимиту
        truncated_text = truncated_text[:max_length]
    else:
        truncated_text = truncated_text[: last_period + 1]

    return truncated_text.strip() + "..."  # Добавляем многоточие


def extract_pull_request_changes(description: str):
    """
    Извлекает текст изменений из описания пулл-реквеста.
    Очищает описание от HTML комментариев и находит изменения.
    """
    description = re.sub(r"<!--.*?-->", "", description, flags=re.DOTALL)
    match = re.search(r"(:cl:.*?|\U0001F191.*?)(\n|$)", description, re.DOTALL)

    if not match:
        return None, None  # Если описание изменений не найдено

    cl_text = match.group(1).strip()
    remaining_lines = description[match.end():].strip()
    full_description = f"{cl_text}\n{remaining_lines}" if remaining_lines else cl_text
    return full_description, match


async def send_pull_request_to_disnake(pr, description, pr_title, pr_url, coauthors):
    """
    Отправляет информацию о замерженном пулл-реквесте в Discord канал CHANGELOG.
    """
    # Создаем Embed-сообщение
    embed = disnake.Embed(
        title=f"Пулл-реквест замержен: {pr_title}",
        color=disnake.Color.dark_green(),
        timestamp=datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc), # pylint: disable=C0301
    )
    embed.add_field(name="Изменения:", value=description, inline=False)
    embed.add_field(name="Автор:", value=pr["user"]["login"], inline=False)
    pr_number = pr["number"]
    embed.add_field(
        name="Ссылка:",
        value=f"[PR #{pr_number}]({pr_url})",
        inline=False,
    )
    # Добавляем соавторов, если они есть
    if coauthors:
        coauthors_str = "\n".join(coauthors)
        embed.add_field(name="Соавторы:", value=coauthors_str, inline=False)
    embed.set_footer(text="Дата мержа")

    # Публикуем Embed в канале CHANGELOG
    changelog_channel = bot.get_channel(CHANGELOG_CHANNEL_ID)
    if changelog_channel is None:
        print(f"❌ Канал с ID {CHANGELOG_CHANNEL_ID} не найден.")
        return

    try:
        # Отправляем сообщение в CHANGELOG
        await changelog_channel.send(embed=embed)
        print(f"✅ Информация о замерженном PR #{pr_number} опубликована в CHANGELOG.")
    except disnake.Forbidden:
        print(f"❌ У бота нет прав для отправки сообщений в канал с ID {CHANGELOG_CHANNEL_ID}.")
    except disnake.HTTPException as e:
        print(f"❌ Ошибка при отправке Embed: {e}")


async def log_pull_request(pr, pr_title, pr_url, merged_at):
    """
    Логирует информацию о замерженном пулл-реквесте
    в LOG_CHANNEL с использованием Embed.
    """
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if log_channel:
        # Создание Embed сообщения
        embed = disnake.Embed(
            title="✅ Пулл-реквест замерджен",
            description=f"- **Название:** {pr_title}\n"
                        f"- **Автор:** {pr['user']['login']}\n"
                        f"- **Ссылка:** [Открыть PR #{pr['number']}]({pr_url})\n"
                        f"- **Дата мержа:** {merged_at.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            color=disnake.Color.green()  # Зеленый цвет для успешных операций
        )

        # Отправка Embed в лог-канал
        await log_channel.send(embed=embed)
    else:
        print(f"⚠️ Лог-канал с ID {LOG_CHANNEL_ID} не найден.")


@tasks.loop(seconds=SECOND_UPDATE_CHANGELOG)
async def fetch_merged_pull_requests():
    """
    Фоновая задача для проверки замерженных пулл-реквестов и публикации их в канале CHANGELOG.
    """
    global LAST_CHECK_TIME # pylint: disable=W0603

    url = f'https://api.github.com/repos/{AUTHOR}/{REPOSITORIES["n"]}/pulls?state=closed'
    pull_requests = await fetch_github_data(url, {"Accept": "application/vnd.github.v3+json"})

    if not pull_requests:
        print("❌ Пулл-реквесты не найдены или произошла ошибка при запросе.")
        return

    for pr in pull_requests:
        merged_at = pr.get("merged_at")
        if not merged_at:
            continue

        merged_at = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        if LAST_CHECK_TIME and merged_at > LAST_CHECK_TIME:
            pr_title = pr["title"]
            pr_url = pr["html_url"]
            description = pr.get("body", "").strip()
            # author_name = pr["user"]["login"]
            coauthors = pr.get("coauthors", [])

            # Извлекаем изменения из описания
            description, _ = extract_pull_request_changes(description)
            if not description:
                print(f"⚠️ Описание изменений для PR #{pr['number']} не найдено.")
                continue

            # Умная обрезка текста, если описание слишком длинное
            description = smart_truncate(description, MAX_FIELD_LENGTH)

            # Отправка PR в Discord и логирование
            await send_pull_request_to_disnake(pr, description, pr_title, pr_url, coauthors)
            await log_pull_request(pr, pr_title, pr_url, merged_at)

    # Обновляем время последней проверки
    LAST_CHECK_TIME = datetime.now(timezone.utc)
