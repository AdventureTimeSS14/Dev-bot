import disnake
from disnake.ext import tasks

from bot_init import bot
from config import LOG_CHANNEL_ID
from modules.command_usage import get_top_commands


@tasks.loop(minutes=30)
async def report_top_commands():
	"""Периодически отправляет топ команд в лог-канал."""
	channel = bot.get_channel(LOG_CHANNEL_ID)
	if not channel:
		print(f"❌ Не найден лог-канал {LOG_CHANNEL_ID} для отчёта топа команд")
		return

	top = get_top_commands(10)
	if not top:
		return

	lines = [f"`{i+1:>2}.` /{name} — **{count}**"
	         for i, (name, count) in enumerate(top)]

	embed = disnake.Embed(
		title="📈 Топ команд за всё время",
		description="\n".join(lines),
		color=disnake.Color.blurple()
	)

	try:
		await channel.send(embed=embed)
	except Exception as e:
		print(f"[report_top_commands] Ошибка отправки отчёта: {e}")


