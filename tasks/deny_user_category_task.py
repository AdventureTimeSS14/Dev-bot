import logging

import disnake
from disnake.ext import tasks

from bot_init import bot
from config import BLOCKED_CATEGORY_ID, BLOCKED_USER_ID, MY_USER_ID


async def _enforce_overwrites_for_channel(channel: disnake.abc.GuildChannel, member: disnake.Member) -> bool:
    try:
        overwrites = channel.overwrites or {}
        current = overwrites.get(member)

        deny_overwrite = disnake.PermissionOverwrite(
            view_channel=False,
            read_messages=False,
            connect=False,
            speak=False,
            send_messages=False,
            send_messages_in_threads=False,
            create_public_threads=False,
            create_private_threads=False,
        )

        if current != deny_overwrite:
            await channel.set_permissions(member, overwrite=deny_overwrite, reason="Security enforcement: blocked user from category")
            return True
        return False
    except disnake.Forbidden:
        logging.warning("Forbidden when setting overwrites for channel %s", getattr(channel, 'id', 'unknown'))
        return False
    except disnake.HTTPException as e:
        logging.error("HTTPException when setting overwrites for channel %s: %s", getattr(channel, 'id', 'unknown'), e)
        return False


@tasks.loop(minutes=5)
async def enforce_category_block() -> None:
    for guild in bot.guilds:
        try:
            member = guild.get_member(BLOCKED_USER_ID) or await guild.fetch_member(BLOCKED_USER_ID)
        except disnake.NotFound:
            continue
        except disnake.HTTPException:
            continue

        category = guild.get_channel(BLOCKED_CATEGORY_ID)
        if not isinstance(category, (disnake.CategoryChannel,)):
            continue

        changed = False
        if await _enforce_overwrites_for_channel(category, member):
            changed = True

        for ch in category.channels:
            if await _enforce_overwrites_for_channel(ch, member):
                changed = True

        if changed:
            try:
                user = bot.get_user(MY_USER_ID) or await bot.fetch_user(MY_USER_ID)
                if user:
                    mention = f"<@{member.id}>"
                    cat_ref = f"{category.name} ({category.id})"
                    await user.send(
                        content=(
                            f"🔒 Обнаружены и исправлены попытки доступа для {mention} в категории {cat_ref}.\n"
                            f"Права восстановлены: deny view/connect/speak/send/messages/threads."
                        )
                    )
            except disnake.Forbidden:
                logging.warning("Cannot send DM to owner for enforcement notification")
            except disnake.HTTPException as e:
                logging.error("Failed to send DM for enforcement notification: %s", e)


@enforce_category_block.before_loop
async def before_enforce_category_block():
    await bot.wait_until_ready()


