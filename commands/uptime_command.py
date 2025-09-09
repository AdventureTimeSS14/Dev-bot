"""
Модуль команды для получения времени работы и времени до завершения работы бота
"""

import time
from datetime import timedelta

from bot_init import bot
from config import TIME_SHUTDOWSE


@bot.command()
async def uptime(ctx):
    """
    Команда для вывода времени работы бота и оставшегося времени до отключения.
    """
    if not hasattr(bot, "start_time") or bot.start_time is None:
        await ctx.send("Бот еще не запущен.")
        return

    # Вычисляем прошедшее время с момента старта
    elapsed_time = time.time() - bot.start_time
    elapsed_time_str = format_time(int(elapsed_time))

    # Вычисляем оставшееся время до отключения
    remaining_time = TIME_SHUTDOWSE - elapsed_time
    if (
        remaining_time < 0
    ):  # Если оставшееся время отрицательное, бот должен быть отключен
        remaining_time_str = "Время истекло."
    else:
        remaining_time_str = format_time(int(remaining_time))

    # Отправляем сообщение с информацией
    await ctx.send(
        f"⏱ **Время работы бота:** {elapsed_time_str}"
    )


def format_time(seconds):
    """
    Форматирует время в удобный вид (дни, часы, минуты, секунды).
    """
    time_delta = timedelta(seconds=seconds)
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} дней")
    if hours > 0:
        parts.append(f"{hours} часов")
    if minutes > 0:
        parts.append(f"{minutes} минут")
    if seconds > 0:
        parts.append(f"{seconds} секунд")

    return ", ".join(parts)
