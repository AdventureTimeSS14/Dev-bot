import disnake
from disnake.ext import tasks

from bot_init import bot
from config import CHANNEL_ID_UPDATE_STATUS, SS14_ADDRESS
from events.update_status import (create_error_embed, create_status_embed,
                                  get_ss14_server_status_second)

# Определение уровней игры для SS14
SS14_RUN_LEVELS = {0: "Лобби", 1: "Раунд идёт", 2: "Окончание раунда..."}


@tasks.loop(seconds=120)
async def update_status_server_message_eddit():
    """
    Фоновая задача для обновления статуса сервера в сообщении.
    """
    channel = bot.get_channel(CHANNEL_ID_UPDATE_STATUS)
    if channel is None:
        print("Не удалось найти канал!")
        return

    try:
        message = await channel.fetch_message(1320771122433622084)
        status_data = await get_ss14_server_status_second(SS14_ADDRESS)

        if not status_data:
            embed = create_error_embed(SS14_ADDRESS)
        else:
            embed = create_status_embed(SS14_ADDRESS, status_data)

        await message.edit(embed=embed)

    except disnake.NotFound:
        print("Сообщение не найдено!")
    except disnake.Forbidden:
        print("У бота нет прав для редактирования сообщения!")
    except Exception as e:
        print(f"Ошибка при обновлении сообщения: {e}")
