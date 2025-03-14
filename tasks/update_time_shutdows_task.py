import time
from datetime import timedelta

import disnake
from disnake.ext import tasks

from bot_init import bot
from config import (CHANNEL_ID_UPDATE_STATUS, MESSAGE_ID_TIME_SHUTDOWS,
                    TIME_SHUTDOWSE)


@tasks.loop(seconds=11)
async def update_time_shutdows():
    """
    Задача для обновления времени работы бота и оставшегося времени до отключения,
    редактируя указанное сообщение.
    """
    channel_id = (
        CHANNEL_ID_UPDATE_STATUS  # ID канала, где нужно редактировать сообщение
    )
    message_id = (
        MESSAGE_ID_TIME_SHUTDOWS  # ID сообщения, которое нужно редактировать
    )

    # Получаем канал
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"❌ Не удалось найти канал с ID {channel_id}")
        return  # Если канал не найден, прекращаем выполнение

    try:
        # Получаем сообщение по ID
        message = await channel.fetch_message(message_id)

        # Проверяем, задано ли время старта бота
        if not hasattr(bot, "start_time") or bot.start_time is None:
            await message.edit(content="⏳ Время запуска бота не задано.")
            return  # Если время старта не задано, прекращаем выполнение

        # Вычисляем прошедшее время с момента старта
        elapsed_time = time.time() - bot.start_time
        elapsed_time_str = format_time(int(elapsed_time))

        # Вычисляем оставшееся время до отключения
        remaining_time = TIME_SHUTDOWSE - elapsed_time
        if remaining_time < 0:  # Если оставшееся время отрицательное
            remaining_time_str = "⛔ Время истекло."
        else:
            remaining_time_str = format_time(int(remaining_time))

        # Формируем текст для редактирования сообщения
        content = (
            f"⏱ **Время работы бота:** {elapsed_time_str}\n"
            f"⌛ **Оставшееся время до отключения:** {remaining_time_str}"
        )

        # Редактируем сообщение
        await message.edit(content=content)

    except disnake.NotFound:
        print(f"❌ Сообщение с ID {message_id} не найдено.")
    except disnake.Forbidden:
        print("❌ У бота нет прав для редактирования сообщения.")
    except Exception as e:
        print(f"❌ Произошла ошибка при редактировании сообщения: {e}")


def format_time(seconds: int) -> str:
    """
    Форматирует время в удобный вид (дни, часы, минуты, секунды).
    """
    time_delta = timedelta(seconds=seconds)
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Формируем список частей времени
    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")
    if seconds > 0:
        parts.append(f"{seconds} сек.")

    return ", ".join(parts)
