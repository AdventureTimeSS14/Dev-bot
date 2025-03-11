from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

import requests
import aiohttp
import dateutil.parser
import disnake
import time

# Определение уровней игры для SS14
SS14_RUN_LEVELS = {0: "Лобби", 1: "Раунд идёт", 2: "Окончание раунда..."}


async def get_ss14_server_status_second(address: str) -> dict:
    """
    Получает статус игры с сервера SS14.
    Если сервер не отвечает на порту 1212, пытается на порту 1211.
    """
    url = get_ss14_status_url(address, 1212)
    try:
        # Пытаемся запросить с порта 1212
        status = await fetch_status(url)
        if status is None:
            # Если не удалось получить статус с порта 1212, пробуем порт 1211
            print("Пробуем подключиться к порту 1211...")
            url = get_ss14_status_url(address, 1211)
            status = await fetch_status(url)
        return status
    except Exception as e:
        print(f"Ошибка при получении статуса с сервера SS14: {e}")
        return None

async def fetch_status(url: str) -> dict:
    """
    Функция для запроса статуса с указанного URL.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url + "/status") as resp:
                if resp.status != 200:
                    raise aiohttp.ClientResponseError(
                        resp.request_info,
                        resp.history,
                        status=resp.status
                    )
                return await resp.json()
    except aiohttp.ClientError as e:
        print(f"Ошибка при получении статуса с сервера SS14: {e}")
        return None

def get_ss14_status_url(url: str, port: int) -> str:
    """
    Преобразует адрес сервера в корректный URL с указанным портом.
    """
    # Если адрес начинается с ss14://, преобразуем в http://
    if url.startswith("ss14://"):
        url = "http://" + url[7:]

    parsed = urlparse(url, allow_fragments=False)
    return urlunparse(
        ("http", f"{parsed.hostname}:{port}", parsed.path, "", "", "")
    )

# async def fetch_metrics(url: str, retries=3, delay=15) -> dict:
#     """
#     Запрашивает метрики с повторами в случае ошибки.
#     """
#     for attempt in range(retries):
#         try:
#             print(f"Попытка {attempt+1}: Получаю метрики с {url}...")
#             response = requests.get(url, timeout=15)
#             response.raise_for_status()
#             print("Метрики успешно получены.")
#             return parse_metrics(response.text)
#         except (requests.Timeout, requests.ConnectionError) as e:
#             print(f"Ошибка: {e} (попытка {attempt+1})")
#             time.sleep(delay)
#     print("Не удалось получить метрики после нескольких попыток.")
#     return {}

# def parse_metrics(metrics_text: str) -> dict:
#     """
#     Парсит текст метрик Prometheus и возвращает значения интересующих метрик.
#     """
#     metrics = {}
#     for line in metrics_text.splitlines():
#         if line.startswith("join_queue_count"):
#             metrics["join_queue_count"] = int(line.split()[-1])
#         elif line.startswith("join_queue_bypass_count"):
#             metrics["join_queue_bypass_count"] = int(line.split()[-1])
#     return metrics

def create_status_embed(
    address: str, status_data: dict, author=None
) -> disnake.Embed:
    """
    Создаёт Embed с информацией о статусе сервера.
    """
    embed = disnake.Embed(color=disnake.Color.dark_blue())
    embed.title = status_data.get("name", "Неизвестно")
    embed.set_footer(text=f"Адрес: {address}")

    # Получаем и добавляем информацию о сервере
    embed_fields = get_embed_fields(status_data)
    for name, value in embed_fields.items():
        embed.add_field(name=name, value=value, inline=False)

    # Добавляем время раунда, если оно есть
    starttimestr = status_data.get("round_start_time")
    if starttimestr:
        starttime = dateutil.parser.isoparse(starttimestr)
        delta = datetime.now(timezone.utc) - starttime
        time_str = format_time_delta(delta)
        embed.add_field(
            name="Время раунда", value=", ".join(time_str), inline=False
        )

    if author:
        embed.set_author(name=author.name, icon_url=author.avatar.url)

    return embed


def get_embed_fields(status_data: dict) -> dict:
    """
    Создаёт словарь с полями для Embed.
    """
    # metrics_url = "http://193.164.18.155:1212/metrics"
    # metrics = await fetch_metrics(metrics_url)

    fields = {
        "Игроков": f"{status_data.get('players', '?')}/{status_data.get('soft_max_players', '?')}",
        # "Игроков в очереди": metrics.get("join_queue_count", "Недоступно"),
        "Раунд": status_data.get("round_id", "?"),
        "Карта": status_data.get("map", "Неизвестно"),
        "Режим игры": status_data.get("preset", "?"),
        "Статус": SS14_RUN_LEVELS.get(status_data.get("run_level", None), "Неизвестно"),
        "Бункер": "Включен" if status_data.get("panic_bunker") else "Отключен",
    }
    return fields


def format_time_delta(delta) -> list:
    """
    Форматирует разницу во времени для отображения.
    """
    time_str = []
    if delta.days > 0:
        time_str.append(f"{delta.days} дней")
    hours, minutes = divmod(delta.seconds, 3600)
    if hours > 0:
        time_str.append(f"{hours} часов")
    time_str.append(f"{minutes // 60} минут")
    return time_str


def create_error_embed(address: str) -> disnake.Embed:
    """
    Создаёт Embed для ошибок.
    """
    embed = disnake.Embed(color=disnake.Color.red())
    embed.title = "Ошибка получения данных"
    embed.set_footer(text=f"Адрес: {address}")

    fields = [
        "Игроков",
        "Статус",
        "Время раунда",
        "Раунд",
        "Карта",
        "Режим игры",
        "Бункер",
    ]
    for field in fields:
        embed.add_field(name=field, value="Error!", inline=False)

    return embed
