# # https://discord.com/channels/1225126931532353568/1226254116368683088
# # https://discord.com/channels/1175915376559792189/1241692667214168166
# # https://discord.com/channels/1030160796401016883/1030919482266357852
# # https://discord.com/channels/1097181193939730453/1241728803949252618
# # https://discord.com/channels/1163557601838121022/1165229071093993532
# # https://discord.com/channels/837289702369263676/1157956566213992468
# # https://discord.com/channels/1286594744432066562/1306191493530128454
# # https://discord.com/channels/1051873590301184031/1264636346610221068
# # https://discord.com/channels/1222332535628103750/1226163026210717696
# # https://discord.com/channels/1111698541841240164/1112658022859284500
# # https://discord.com/channels/1040938900039929917/1234367190040318053
# # https://discord.com/channels/1218680995021066301/1222240214995701760
# # https://discord.com/channels/1174575355370160190/1175578453567864863
# # https://discord.com/channels/919301044784226385/921498847862214666
# # https://discord.com/channels/1354120935225167883/1358791362773913853

import asyncio
import random

import discord
from discord.ext import commands

from config import DISCORD_TOKEN_USER

CHANNELS_TO_CHECK = [
    ("1225126931532353568", "1226254116368683088"), # [Space Cats]
    ("1175915376559792189", "1241692667214168166"), # [Space Stories - Colonial Marines]
    ("1030160796401016883", "1030919482266357852"), # [МЁРТВЫЙ КОСМОС]
    ("1097181193939730453", "1241728803949252618"), # [SS220]
    ("1163557601838121022", "1165229071093993532"), # [Adventure Space]
    ("837289702369263676", "1157956566213992468"),  # [🐟  Рыбья Станция]
    ("1286594744432066562", "1306191493530128454"), # [Corvax Wega [18+]]
    ("1051873590301184031", "1264636346610221068"), # [FIRE STATION 2.0]
    ("1222332535628103750", "1226163026210717696"), # [Corvax Forge]
    ("1111698541841240164", "1112658022859284500"), # [Space Stories]
    ("1040938900039929917", "1234367190040318053"), # [Imperial 2.0 — SS14]
    ("1218680995021066301", "1222240214995701760"), # [Starshine — Space Station 14]
    ("1174575355370160190", "1175578453567864863"), # [SUNRISE]
    ("919301044784226385", "921498847862214666"),   # [SS14 RU Community]
    ("1354120935225167883", "1358791362773913853"), # [Space Dream - [MRP][18+][SS14]]
]

async def search_bans_in_multiple_channels(username: str):
    result = []
    permanent_ban_count = 0
    total_bans = 0

    temp_bot = commands.Bot(command_prefix="!", self_bot=True)

    @temp_bot.event
    async def on_ready():
        nonlocal result, permanent_ban_count, total_bans
        for guild_id_str, channel_id_str in CHANNELS_TO_CHECK:
            guild_id = int(guild_id_str)
            channel_id = int(channel_id_str)

            guild = temp_bot.get_guild(guild_id)
            if not guild:
                result.append(f"❌ Гильдия `{guild_id}` не найдена.")
                continue

            try:
                channel = guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
            except discord.NotFound:
                result.append(f"❌ Канал `{channel_id}` не найден в **{guild.name}**.")
                continue

            found = 0
            compact_lines = []

            async for message in channel.history(limit=5000):
                for embed in message.embeds:
                    match = False
                    content_to_check = []

                    for attr in ["title", "description"]:
                        value = getattr(embed, attr, "") or ""
                        content_to_check.append(value)
                        if username.lower() in value.lower():
                            match = True
                            break

                    if not match:
                        for field in embed.fields:
                            content_to_check.append(field.name)
                            content_to_check.append(field.value)
                            if username.lower() in field.name.lower() or username.lower() in field.value.lower():
                                match = True
                                break

                    if match:
                        found += 1
                        total_bans += 1

                        # Проверка на перманентный бан
                        for text in content_to_check:
                            if any(perm in text.lower() for perm in ["навсегда", "перманентный бан"]):
                                permanent_ban_count += 1
                                break

                        short = f"• {message.created_at.strftime('%m/%d %H:%M')} — "
                        issuer = "неизвестно"
                        reason = ""

                        for field in embed.fields:
                            if "выдал" in field.name.lower():
                                issuer = field.value
                            elif "наказание" in field.name.lower():
                                issuer = field.value
                            elif "причина" in field.name.lower():
                                reason = field.value.split("\n")[0].strip()

                        if embed.description:
                            for line in embed.description.splitlines():
                                if "выдал" in line.lower():
                                    issuer = line.split(":", 1)[-1].strip()
                                if username.lower() in line.lower() or "причина" in line.lower():
                                    reason = line.strip()

                        short += f"{issuer}: {reason[:60]}".strip()
                        compact_lines.append(short)

            if found == 0:
                result.append(f"🌐 {guild.name} — ✅ Чисто")
            else:
                result.append(f"🌐 {guild.name} — ⚠ {found} бан(ов):")
                result.extend(compact_lines)

            await asyncio.sleep(random.randint(6, 9))

        result.append("✅ Поиск завершен.")
        await temp_bot.close()

    await temp_bot.start(DISCORD_TOKEN_USER)
    status_message = result[-1]
    messages = result[:-1]
    return messages, status_message, permanent_ban_count, total_bans
