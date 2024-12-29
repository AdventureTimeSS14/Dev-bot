from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

import aiohttp
import dateutil.parser
import discord

# Определение уровней игры для SS14
SS14_RUN_LEVELS = {0: "Лобби", 1: "Раунд идёт", 2: "Окончание раунда..."}


async def get_ss14_server_status_second(address: str) -> dict:
    """
    Получает статус игры с сервера SS14.
    """
    url = get_ss14_status_url(address)
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


def get_ss14_status_url(url: str) -> str:
    """
    Преобразует адрес сервера в корректный URL.
    """
    if url.startswith("ss14://"):
        url = "http://" + url[7:]  # Убираем ss14:// и добавляем http://

    parsed = urlparse(url, allow_fragments=False)
    port = parsed.port or 1212  # Если порт не указан, используем 1212
    return urlunparse(
        ("http", f"{parsed.hostname}:{port}", parsed.path, "", "", "")
    )


def create_status_embed(
    address: str, status_data: dict, author=None
) -> discord.Embed:
    """
    Создаёт Embed с информацией о статусе сервера.
    """
    embed = discord.Embed(color=discord.Color.dark_blue())
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
    fields = {
        "Игроков": f"{status_data.get('players', '?')}/{status_data.get('soft_max_players', '?')}",
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


def create_error_embed(address: str) -> discord.Embed:
    """
    Создаёт Embed для ошибок.
    """
    embed = discord.Embed(color=discord.Color.red())
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
