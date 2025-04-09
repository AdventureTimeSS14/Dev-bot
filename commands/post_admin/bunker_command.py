import requests

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import (ADDRESS_MRP, POST_ADMIN_HEADERS,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)


@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)
async def bunker(ctx, toggle: str):
    # Устанавливаем адрес URL
    url = f"http://{ADDRESS_MRP}:1212/admin/actions/panic_bunker"

    # Проверяем, что toggle имеет корректное значение
    if toggle.lower() not in ["true", "false"]:
        await ctx.send("Ошибка: пожалуйста, используйте 'true' или 'false' для включения/выключения бункера.")
        return

    # Определяем значение для бункера
    bunker_bool = True if toggle.lower() == "true" else False

    # Подготовка данных для запроса
    data = {
        "game.panic_bunker.enabled": bunker_bool,
    }

    try:
        # Отправка PATCH запроса
        response = requests.patch(url, headers=POST_ADMIN_HEADERS, json=data)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            status = "включен" if bunker_bool else "выключен"
            await ctx.send(f"Паник-бункер успешно {status}.")
        else:
            await ctx.send(f"Ошибка при изменении состояния паник-бункера. Код ошибки: {response.status_code}.")
            print(f"Error: {response.status_code}, {response.text}")
    
    except requests.exceptions.RequestException as e:
        # Обработка ошибок сети
        await ctx.send(f"Произошла ошибка при отправке запроса: {str(e)}")
        print(f"Request error: {str(e)}")