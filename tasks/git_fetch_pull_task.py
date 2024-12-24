import re
from datetime import datetime, timezone

import discord
from discord.ext import tasks

from bot_init import bot
from commands.github.github_processor import fetch_github_data
from config import (AUTHOR, CHANGELOG_CHANNEL_ID, LOG_CHANNEL_ID, REPOSITORIES,
                    SECOND_UPDATE_CHANGELOG)

# Переменная для отслеживания последнего времени проверки
LAST_CHECK_TIME: datetime = None


@tasks.loop(seconds=SECOND_UPDATE_CHANGELOG)
async def fetch_merged_pull_requests():
    """
    Фоновая задача для проверки замерженных пулл-реквестов и публикации их в канале CHANGELOG.
    """
    global LAST_CHECK_TIME

    # Формируем URL для получения закрытых пулл-реквестов
    url = f'https://api.github.com/repos/{AUTHOR}/{REPOSITORIES["n"]}/pulls?state=closed'

    # Получаем данные о пулл-реквестах
    pull_requests = await fetch_github_data(
        url, {"Accept": "application/vnd.github.v3+json"}
    )

    if not pull_requests:
        print("❌ Пулл-реквесты не найдены или произошла ошибка при запросе.")
        return

    # Проверяем каждый пулл-реквест
    for pr in pull_requests:
        # Проверяем, был ли пулл-реквест замержен
        merged_at = pr.get("merged_at")
        if not merged_at:
            continue

        # Преобразуем дату мержа в объект datetime
        merged_at = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )

        # Проверяем, произошел ли мерж после последнего времени проверки
        if LAST_CHECK_TIME and merged_at > LAST_CHECK_TIME:
            # Извлекаем информацию о пулл-реквесте
            pr_title = pr["title"]
            pr_url = pr["html_url"]
            description = pr.get("body", "").strip()
            author_name = pr["user"]["login"]

            # Очищаем описание от HTML-комментариев и ищем описание изменений
            description = re.sub(r"<!--.*?-->", "", description, flags=re.DOTALL)
            match = re.search(r"(:cl:.*?)(\n|$)", description, re.DOTALL)

            if not match:
                print(f"⚠️ Описание изменений для PR #{pr['number']} не найдено.")
                continue

            # Формируем текст изменений
            cl_text = match.group(1).strip()
            remaining_lines = description[match.end():].strip()
            description = f"{cl_text}\n{remaining_lines}" if remaining_lines else cl_text

            # Создаем Embed-сообщение
            embed = discord.Embed(
                title=f"✅ Пулл-реквест замержен: {pr_title}",
                color=discord.Color.dark_green(),
                timestamp=merged_at,
            )
            embed.add_field(name="Изменения:", value=description, inline=False)
            embed.add_field(name="Автор:", value=author_name, inline=False)
            pr_number = pr["number"]  # Номер пулл-реквеста
            embed.add_field(
                name="Ссылка:",
                value=f"[Открыть PR #{pr_number}]({pr_url})",
                inline=False,
            )
            embed.set_footer(text="Дата мержа")

            # Публикуем Embed в канале CHANGELOG
            changelog_channel = bot.get_channel(CHANGELOG_CHANNEL_ID)
            log_channel = bot.get_channel(LOG_CHANNEL_ID)

            if changelog_channel is None:
                print(f"❌ Канал с ID {CHANGELOG_CHANNEL_ID} не найден.")
                return

            try:
                # Отправляем сообщение в CHANGELOG
                await changelog_channel.send(embed=embed)
                print(f"✅ Информация о замерженном PR #{pr_number} опубликована в CHANGELOG.")
                
                # Логируем отправленное сообщение в LOG_CHANNEL
                if log_channel:
                    log_message = (
                        f"✅ **Пулл-реквест опубликован:**\n"
                        f"- **Название:** {pr_title}\n"
                        f"- **Автор:** {author_name}\n"
                        f"- **Ссылка:** [Открыть PR #{pr_number}]({pr_url})\n"
                        f"- **Дата мержа:** {merged_at.strftime('%Y-%m-%d %H:%M:%S')} UTC\n_ _"
                    )
                    await log_channel.send(log_message)
                else:
                    print(f"⚠️ Лог-канал с ID {LOG_CHANNEL_ID} не найден.")

            except discord.Forbidden:
                print(f"❌ У бота нет прав для отправки сообщений в канал с ID {CHANGELOG_CHANNEL_ID}.")
            except discord.HTTPException as e:
                print(f"❌ Ошибка при отправке Embed: {e}")

    # Обновляем время последней проверки
    LAST_CHECK_TIME = datetime.now(timezone.utc)
