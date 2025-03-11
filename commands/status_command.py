"""
Модуль команды для получения статуса сервера ss14
"""

from bot_init import bot
from config import SS14_ADDRESS, SS14_ADDRESS_DEV
from events.update_status import (
    create_status_embed,
    get_ss14_server_status_second,
)

# Команда для получения статуса
@bot.command(name="status")
async def get_status_command(ctx, server_name: str = None):
    """
    Команда для получения статуса сервера SS14 в чате Discord.
    Можно указать сервер, например: &status dev или &status mrp.
    """
    try:
        # Установка адреса по умолчанию (если сервер не указан)
        if server_name is None:
            address = SS14_ADDRESS  # Основной адрес по умолчанию
        elif server_name.lower() == "dev":
            address = SS14_ADDRESS_DEV  # Адрес для dev сервера
        elif server_name.lower() == "mrp":
            address = SS14_ADDRESS  # Адрес для mrp сервера
        else:
            await ctx.send("❌ Некорректное имя сервера. Используйте 'dev' или 'mrp'.")
            return

        # Получаем данные статуса с выбранного сервера
        print(f"Попытка подключения к серверу: {address}")
        status_data = await get_ss14_server_status_second(address)

        # Если данные не получены, уведомляем пользователя
        if not status_data:
            await ctx.send("❌ Ошибка при получении статуса с сервера.")
            return

        # Создаем Embed сообщение с использованием данных
        embed = create_status_embed(address, status_data, ctx.author)
        await ctx.send(embed=embed)

    except Exception as e:
        # Обработка любых ошибок
        print(f"❌ Произошла ошибка в команде 'status': {e}")
        await ctx.send(
            "❌ Произошла ошибка при выполнении команды. Повторите позже."
        )
