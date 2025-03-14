from disnake import MessageType

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM


@bot.command(name="media_clear")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def media_clear(ctx, count: int):
    """
    Команда для удаления сообщений без медиафайлов.

    Аргументы:
    count (int) — количество сообщений для проверки и удаления.
    """
    try:
        deleted = 0
        async for message in ctx.channel.history(limit=count):
            # Пропускаем системные сообщения
            if message.type not in (MessageType.default, MessageType.reply):
                continue

            # Проверяем, содержит ли сообщение вложения (медиа, файлы и т. д.)
            if (
                not message.attachments
                and not message.content.startswith("https://tenor.com")
                and not message.content.startswith("https://youtube.com")
            ):
                await message.delete()
                deleted += 1

        await ctx.send(f"✅ Удалено {deleted} сообщений без медиафайлов.", delete_after=5)

    except Exception as e:
        print(f"❌ Ошибка при удалении сообщений: {e}")
        await ctx.send(f"❌ Произошла ошибка при удалении сообщения: {message} Проверьте логи.")
