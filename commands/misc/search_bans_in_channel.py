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
import os
import pickle
import random

import discord
from discord.ext import commands

from config import DISCORD_TOKEN_USER

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

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

SEMAPHORE_LIMIT = 3

def get_cache_path(channel_id):
    return os.path.join(CACHE_DIR, f"{channel_id}_messages.pkl")

def load_cache(channel_id):
    path = get_cache_path(channel_id)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return []

def save_cache(channel_id, messages):
    path = get_cache_path(channel_id)
    with open(path, "wb") as f:
        pickle.dump(messages, f)

async def process_guild(guild_id_str, channel_id_str, username, bot, semaphore, shared_data, force_update=False):
    async with semaphore:
        guild_id = int(guild_id_str)
        channel_id = int(channel_id_str)

        guild = bot.get_guild(guild_id)
        if not guild:
            shared_data["result"].append(f"❌ Гильдия `{guild_id}` не найдена.")
            return

        try:
            channel = guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
        except discord.NotFound:
            shared_data["result"].append(f"❌ Канал `{channel_id}` не найден в **{guild.name}**.")
            return

        if not force_update:
            cached_embeds = load_cache(channel_id)
            last_cached_time = cached_embeds[-1]["created_at"] if cached_embeds else None
        else:
            cached_embeds = []
            last_cached_time = None

        new_messages = []

        try:
            async for msg in channel.history(limit=5000, after=last_cached_time):
                new_messages.append({
                    "created_at": msg.created_at,
                    "embeds": [embed.to_dict() for embed in msg.embeds]
                })
        except discord.errors.HTTPException as e:
            if e.status == 429:
                retry_after = getattr(e, 'retry_after', 10)
                wait_time = float(retry_after) if isinstance(retry_after, (int, float)) else 10
                shared_data["result"].append(
                    f"⏳ Rate Limit в **{guild.name}**, ждём {wait_time:.1f} сек..."
                )
                await asyncio.sleep(wait_time + random.uniform(1, 3))
                await process_guild(guild_id_str, channel_id_str, username, bot, semaphore, shared_data)
                return
            else:
                shared_data["result"].append(f"❌ Ошибка в {guild.name}: {str(e)}")
                return

        if new_messages:
            cached_embeds.extend(new_messages)
            save_cache(channel_id, cached_embeds)

        found = 0
        compact_lines = []

        for msg in cached_embeds:
            created_at = msg["created_at"]
            for raw_embed in msg["embeds"]:
                embed = discord.Embed.from_dict(raw_embed)
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
                    shared_data["total_bans"] += 1

                    for text in content_to_check:
                        if any(perm in text.lower() for perm in ["навсегда", "перманентный бан"]):
                            shared_data["permanent_ban_count"] += 1
                            break

                    short = f"• {created_at.strftime('%m/%d %H:%M')} — "
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
            shared_data["result"].append(f"🌐 {guild.name} — ✅ Чисто")
        else:
            shared_data["result"].append(f"🌐 {guild.name} — ⚠ {found} бан(ов):")
            shared_data["result"].extend(compact_lines)

        await asyncio.sleep(random.uniform(1, 2))

async def search_bans_in_multiple_channels(username: str, force_update: bool = False):
    result = []
    shared_data = {
        "result": result,
        "permanent_ban_count": 0,
        "total_bans": 0,
    }

    # Обязательные intents для discord.py v2+
    temp_bot = commands.Bot(command_prefix="!", self_bot=True)

    @temp_bot.event
    async def on_ready():
        semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

        tasks = [
            process_guild(guild_id, channel_id, username, temp_bot, semaphore, shared_data, force_update)
            for guild_id, channel_id in CHANNELS_TO_CHECK
        ]

        await asyncio.gather(*tasks)
        shared_data["result"].append("✅ Поиск завершен.")
        await temp_bot.close()

    await temp_bot.start(DISCORD_TOKEN_USER)

    status_message = result[-1]
    messages = result[:-1]
    return messages, status_message, shared_data["permanent_ban_count"], shared_data["total_bans"]
