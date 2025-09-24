import asyncio

import aiohttp
from typing import Optional

from bot_init import bot
from config import LOG_CHANNEL_ID

_session: aiohttp.ClientSession | None = None

async def get_http_session() -> aiohttp.ClientSession:
	global _session
	current_loop = asyncio.get_running_loop()

	# Create a new session if none exists or it is explicitly closed
	if _session is None or _session.closed:
		_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
		return _session

	# If the existing session is bound to a different or closed loop, recreate it
	session_loop = getattr(_session, "_loop", None)
	if session_loop is None or session_loop.is_closed() or session_loop is not current_loop:
		try:
			await _session.close()
		except Exception:
			pass
		_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))

	return _session

async def close_http_session() -> None:
	global _session
	if _session and not _session.closed:
		await _session.close()


async def send_log(message: str, *, embed: Optional[object] = None) -> None:
    """
    Отправляет лог-сообщение в Discord-канал LOG_CHANNEL_ID.
    При ошибке отправки выводит сообщение в консоль.
    """
    try:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel is not None:
            if embed is not None:
                await channel.send(content=message or None, embed=embed)
            else:
                await channel.send(message)
        else:
            print(f"❌ Не удалось найти канал логов {LOG_CHANNEL_ID}. Сообщение: {message}")
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения в лог-канал: {e}. Сообщение: {message}")
