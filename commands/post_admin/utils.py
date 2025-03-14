import asyncio
import json  # Для сериализации данных

import aiohttp


async def send_server_request(ctx, url, post_data, headers, retries=3):
    """
    Универсальная асинхронная функция для отправки запроса на сервер.
    Повторяет запрос в случае ошибок.
    """
    try:
        async with aiohttp.ClientSession() as session:
            for attempt in range(retries):
                try:
                    # Сериализуем данные в JSON
                    json_data = json.dumps(post_data)
                    headers["Content-Length"] = str(len(json_data))  # Устанавливаем Content-Length на основе сериализованных данных
                    
                    async with session.post(url, data=json_data, headers=headers) as response:
                        # Проверка успешного ответа
                        if response.status == 200:
                            return True, await response.text()
                        else:
                            return False, f"Ошибка сервера: {response.status} - {await response.text()}"
                except aiohttp.ClientConnectionError as e:
                    # Обработка проблем с соединением
                    await ctx.send(f"Ошибка соединения (попытка {attempt + 1}): {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(2)  # Задержка перед повторной попыткой
                    else:
                        return False, f"Ошибка соединения после {retries} попыток: {e}"
                except aiohttp.ClientResponseError as e:
                    # Ошибка на стороне сервера (например, сервер вернул ошибку)
                    return False, f"Ошибка ответа сервера: {e.status} - {e.message}"
                except asyncio.TimeoutError:
                    # Ошибка таймаута
                    await ctx.send(f"Таймаут при попытке {attempt + 1} на сервере {url}")
                    if attempt < retries - 1:
                        await asyncio.sleep(2)  # Задержка перед повторной попыткой
                    else:
                        return False, "Таймаут при соединении."
                except Exception as e:
                    # Общая ошибка
                    return False, f"Неизвестная ошибка: {str(e)}"
            return False, "Неудачная попытка подключения после нескольких попыток."
    except Exception as e:
        return False, f"Не удалось выполнить запрос: {str(e)}"

def get_field_value(data, keys, default="Не задано"):
    """
    Функция для безопасного извлечения значения из вложенной структуры данных.
    Если значение не найдено, возвращается default.
    """
    try:
        for key in keys:
            data = data.get(key, {})
            if not data:
                return default
        return data if data else default
    except Exception as e:
        print(f"Ошибка извлечения данных: {e}")
        return default
