import disnake
from disnake.ext import tasks

from bot_init import bot
from config import SS14_ADDRESS, SS14_RUN_LEVELS
from events.update_status import get_ss14_server_status_second


@tasks.loop(seconds=30)
async def update_status_presence():
    """
    Обновление Rich Presence бота.
    """
    status_data = await get_ss14_server_status_second(SS14_ADDRESS)
    if not status_data:
        await bot.change_presence(
            activity=disnake.Game(name="Ошибка при получении статуса")
        )
        return

    # Формируем строку для статуса
    count = status_data.get("players", "?")
    countmax = status_data.get("soft_max_players", "?")
    name = status_data.get("name", "Неизвестно")
    preset = status_data.get("preset", "?")
    round_id = status_data.get("round_id", "?")
    run_level = SS14_RUN_LEVELS.get(status_data.get("run_level"), "Неизвестно")

    status_state = (
        f"Игроков: {count}/{countmax} | "
        f"Режим: {preset} | Раунд: {round_id} | "
        f"Статус: {run_level}"
    )
    activity = disnake.Activity(
        type=disnake.ActivityType.playing, name=name, state=status_state
    )
    await bot.change_presence(activity=activity)
