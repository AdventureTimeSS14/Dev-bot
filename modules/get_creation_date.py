from datetime import datetime

import requests


def get_creation_date(uuid):
    """
        используем апи визардов для отслеживание - когда была создана учётная запись
    """
    url = f"https://auth.spacestation14.com/api/query/userid?userid={uuid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()  # Парсинг JSON

        player_date = data.get('createdTime', 'Дата создания не найдена')
        date_obj = datetime.fromisoformat(player_date)
        creation_date_unix = int(date_obj.timestamp())  # Преобразование в Unix-время

        return f'<t:{creation_date_unix}:f>'  # Форматирование в метку времени Discord

    except requests.exceptions.HTTPError as err:
        return f"Ошибка при запросе API: {err}"
    except requests.exceptions.RequestException as err:
        return f"Ошибка соединения: {err}"
    except ValueError:
        return "Ошибка при разборе ответа API (неправильный формат JSON)"
    except Exception as err:
        return f"Произошла ошибка: {err}"
