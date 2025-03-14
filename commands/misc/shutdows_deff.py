import disnake

from bot_init import bot
from config import (CHANNEL_ID_UPDATE_STATUS, LOG_CHANNEL_ID,
                    MESSAGE_ID_TIME_SHUTDOWS, SS14_ADDRESS)


async def shutdown_def():
    """
    Выполняет действия перед завершением работы бота:
    - Обновляет текст сообщения, информируя о завершении работы.
    - Обновляет статус и Embed-сообщение для ошибок.
    - Логирует событие в лог-канал.
    """
    try:
        # Обновляем сообщение с информацией об отключении
        await update_shutdown_message()

        # Обновляем сообщение со статусом сервера
        await update_error_status_message()

        # Устанавливаем статус бота на "Отключена"
        await update_bot_presence()

        # Отправляем сообщение в лог-канал
        await send_to_log_channel()

        print("✅ Завершение работы успешно выполнено.")
    except Exception as e:
        print(f"❌ Ошибка при выполнении shutdown_def: {e}")


async def update_shutdown_message():
    """
    Обновляет сообщение в канале, указывая, что бот отключён.
    """
    try:
        channel = bot.get_channel(CHANNEL_ID_UPDATE_STATUS)
        if not channel:
            print(f"❌ Канал с ID {CHANNEL_ID_UPDATE_STATUS} не найден.")
            return

        message = await channel.fetch_message(MESSAGE_ID_TIME_SHUTDOWS)
        await message.edit(
            content=(
                f"⚠️ **{bot.user.name} временно отключена.**\n\n"
                f"🔻 **Статус:** Отключение завершено.\n"
                "⏳ **Ожидайте повторного включения.**\n"
                "🔔 Следите за обновлениями!"
            )
        )
        print("✅ Сообщение об отключении обновлено.")
    except disnake.NotFound:
        print(f"❌ Сообщение с ID {MESSAGE_ID_TIME_SHUTDOWS} не найдено.")
    except disnake.Forbidden:
        print("❌ У бота нет прав для редактирования сообщения.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении сообщения об отключении: {e}")


async def update_error_status_message():
    """
    Обновляет сообщение со статусом сервера, указывая на ошибку.
    """
    try:
        channel = bot.get_channel(CHANNEL_ID_UPDATE_STATUS)
        if not channel:
            print(f"❌ Канал с ID {CHANNEL_ID_UPDATE_STATUS} не найден.")
            return

        message_id = 1320771122433622084  # ID сообщения о статусе сервера
        message = await channel.fetch_message(message_id)

        embed = disnake.Embed(color=disnake.Color.red())
        embed.title = "Ошибка получения данных"
        embed.add_field(name="Игроков", value="Error!", inline=False)
        embed.add_field(name="Статус", value="Error!", inline=False)
        embed.add_field(name="Время раунда", value="Error!", inline=False)
        embed.add_field(name="Раунд", value="Error!", inline=False)
        embed.add_field(name="Карта", value="Error!", inline=False)
        embed.add_field(name="Режим игры", value="Error!", inline=False)
        embed.add_field(name="Бункер", value="Error!", inline=False)
        embed.set_footer(text=f"Адрес: {SS14_ADDRESS}")

        await message.edit(embed=embed)
        print("✅ Сообщение со статусом обновлено с ошибкой.")
    except disnake.NotFound:
        print(f"❌ Сообщение со статусом с ID {message_id} не найдено.")
    except disnake.Forbidden:
        print("❌ У бота нет прав для редактирования сообщения о статусе.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении сообщения о статусе: {e}")


async def update_bot_presence():
    """
    Устанавливает статус бота на "Отключена" с ошибочными данными.
    """
    try:
        name = "Отключена!"
        status_state = (
            "Игроков: ERROR! | Режим: ERROR! | Раунд: ERROR! | Статус: ERROR!"
        )
        activity = disnake.Activity(
            type=disnake.ActivityType.unknown, name=name, state=status_state
        )
        await bot.change_presence(activity=activity)
        print("✅ Статус бота обновлён на 'Отключена'.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении статуса бота: {e}")


async def send_to_log_channel():
    """
    Отправляет сообщение в лог-канал.
    """
    try:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(
                f"⚠️ {bot.user} завершает свою работу! Перезапуск начнётся в течение 10 минут.\n_ _"
            )
        else:
            print(f"❌ Лог-канал с ID {LOG_CHANNEL_ID} не найден.")
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения в лог-канал: {e}")
