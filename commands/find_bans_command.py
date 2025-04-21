from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from commands.misc.search_bans_in_channel import \
    search_bans_in_multiple_channels


@bot.command(name="find_bans")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def find_bans(ctx, username: str):
    await ctx.send(f"🔍 Ищу баны по нику `{username}`...")

    try:
        search_results = await search_bans_in_multiple_channels(username)

        if not search_results:
            await ctx.send("⚠ Произошла ошибка при поиске.")
            return

        *messages, status_message = search_results

        if not messages:
            await ctx.send(status_message)
            return

        # Разбиваем сообщения на части по 1900 символов
        chunks = []
        current_chunk = ""
        for text in messages:
            if len(current_chunk) + len(text) > 1900:
                chunks.append(current_chunk)
                current_chunk = ""
            current_chunk += text + "\n"
        if current_chunk:
            chunks.append(current_chunk)

        for chunk in chunks:
            await ctx.send(chunk)

        await ctx.send(status_message)

    except Exception as e:
        await ctx.send(f"⚠ Произошла ошибка: {str(e)}")
