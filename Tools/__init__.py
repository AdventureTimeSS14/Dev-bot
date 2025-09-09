import aiohttp

_session: aiohttp.ClientSession | None = None

async def get_http_session() -> aiohttp.ClientSession:
	global _session
	if _session is None or _session.closed:
		_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
	return _session

async def close_http_session() -> None:
	global _session
	if _session and not _session.closed:
		await _session.close()
