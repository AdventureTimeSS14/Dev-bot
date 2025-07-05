import random
import re

import disnake
import requests
from fuzzywuzzy import fuzz

from bot_init import bot, ss14_db
from commands.misc.search_bans_in_channel import \
    search_bans_in_multiple_channels
from config import ADDRESS_MRP, ADMIN_TEAM, LOG_CHANNEL_ID, POST_ADMIN_HEADERS
from data import JsonData
from events.utils import get_github_link
from modules.get_creation_date import get_creation_date


@bot.event
async def on_message(message):
    """
    Обработчик сообщений бота.
    """
    # Игнорируем сообщения от самого бота
    if message.author == bot.user:
        return

    # Обработка команд
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # Ответ на упоминание бота
    if f"<@{bot.user.id}>" in message.content:
        await call_mention(message)
        await handle_mention(message)
        return

    # Проверка сообщений в канале для удаления
    if message.channel.id == ADMIN_TEAM:
        await handle_message_deletion(message)

    if message.channel.id == 1309262152586235964:
        await send_ahat_message_post(message)
        # TODO: Сломалось, отключаю поиск банов
        # await check_new_player(message)

    # Проверка на шаблон GitHub issue/PR
    await handle_github_pattern(message)

    await check_time_transfer_with_fuzz(message)

    # await check_vpn_promotion(message) # ЗАпрещено 6-ым правилом политики Разработчиков


async def send_ahat_message_post(message):
    """
    Если в логах а-чата замечено сообщение от пользователя
    Создается пост запрос, и отправляется в игру
    """
    if message.author.id == 1309279443943948328: # Игнорим ВэбХукк
        return
    # url = f"http://{ADDRESS_DEV}:1211/admin/actions/a_chat" # DEV
    url = f"http://{ADDRESS_MRP}:1212/admin/actions/a_chat"
    post_data = {
        "Message": f"{message.content}",
        "NickName": f"{message.author.name}"
    }
    try:
        response = requests.post(url, json=post_data, headers=POST_ADMIN_HEADERS, timeout=5)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    else:
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)


async def check_new_player(message):
    if "**Оповещение: ЗАШЁЛ НОВИЧОК** (" in message.content and ")" in message.content:
        adminchat_channel = bot.get_channel(1309262152586235964)
        if not adminchat_channel:
            print("Канал с 1309262152586235964 не найден")
            return

        start_index = message.content.find("(") + 1
        end_index = message.content.find(")")
        nickname = message.content[start_index:end_index]

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        ban_channel = bot.get_channel(1291023511607054387)

        if not log_channel or not ban_channel:
            print("Не удалось найти один из каналов логов или банов.")
            return

        await log_channel.send(f"Зашёл новый игрок: `{nickname}`\n🔍 Ищу баны по нику...")

        # 🔒 Проверка: был ли уже забанен ранее
        async for msg in ban_channel.history(limit=5000):
            for embed in msg.embeds:
                text = " ".join([
                    embed.title or "",
                    embed.description or "",
                    *(f"{field.name} {field.value}" for field in embed.fields)
                ]).lower()
                if nickname.lower() in text:
                    # Формируем сообщение со ссылкой на оригинальное сообщение о бане
                    ban_message = (
                        f"⛔ Игрок `{nickname}` уже был забанен ранее:\n"
                        f"• Сервер: {msg.guild.name if msg.guild else 'Unknown'}\n"
                        f"• Канал: {msg.channel.mention if isinstance(msg.channel, disnake.TextChannel) else '#'+str(msg.channel)}\n"
                        f"• Дата: {msg.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                        f"• [Ссылка на сообщение]({msg.jump_url})"
                    )
                    await log_channel.send(ban_message)
                    return

        try:
            search_results = await search_bans_in_multiple_channels(nickname)
            if not search_results:
                await log_channel.send("⚠ Произошла ошибка при поиске.")
                return

            messages, status_message, permanent_bans_count, total_bans = search_results
            if not messages:
                await log_channel.send(status_message)
                return

            if permanent_bans_count:
                reason = (
                    "Перманентная блокировка для коммуникации. "
                    "Подозрение на набег. Для разбана обратитесь в канал обжалований."
                )
                url = f"http://{ADDRESS_MRP}:1212/admin/actions/server_ban"
                post_data = {
                    "NickName": nickname,
                    "Reason": reason,
                    "Time": "0"
                }
                try:
                    response = requests.post(url, json=post_data, headers=POST_ADMIN_HEADERS, timeout=5)
                    response.raise_for_status()
                    await log_channel.send(f"✅ Запрос на бан `{nickname}` успешно отправлен!")
                except requests.exceptions.Timeout:
                    await log_channel.send("🕒 Сервер не ответил за 5 секунд. Попробуйте позже.")
                except requests.exceptions.ConnectionError as e:
                    await log_channel.send(f"🔌 Ошибка подключения: {str(e)}")
                except requests.exceptions.HTTPError as e:
                    await log_channel.send(f"❌ Ошибка сервера: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    await log_channel.send(f"⚠️ Неизвестная ошибка: {str(e)}")

                message_for_adminchat = f"🔒 Игрок `{nickname}` получил **перманентный бан** (найдено {permanent_bans_count} пермабан(ов))."
                await log_channel.send(message_for_adminchat)
                await adminchat_channel.send(message_for_adminchat)

            elif total_bans:
                message_adminchat = (
                    f"⚠ ВНИМАНИЕ! Новый игрок ({nickname}) "
                    f"имеет {total_bans} бан(а) на сторонних проектах! "
                    "БУДЬТЕ ВНИМАТЕЛЬНЫ! ^_^"
                )
                url = f"http://{ADDRESS_MRP}:1212/admin/actions/a_chat"
                post_data = {
                    "Message": message_adminchat,
                    "NickName": "Астра BOT"
                }

                await adminchat_channel.send(message_adminchat)

                try:
                    response = requests.post(url, json=post_data, headers=POST_ADMIN_HEADERS, timeout=5)
                    response.raise_for_status()
                except requests.exceptions.Timeout:
                    await log_channel.send("🕒 Сервер не ответил за 5 секунд при отправке сообщения в a-chat.")
                except requests.exceptions.RequestException as e:
                    await log_channel.send(f"Request failed: {e}")
                else:
                    await log_channel.send(f"⚠ Игрок `{nickname}` имеет {total_bans} бан(а), **но перманентных нет**.")
                    await log_channel.send(f"Status Code: {response.status_code}")
                    await log_channel.send(f"Response Text: {response.text}")

            else:
                await log_channel.send(f"✅ Игрок `{nickname}` чист — **банов не найдено**.")

        except Exception as e:
            await log_channel.send(f"⚠ Ошибка при автоматической проверке банов: {str(e)}")


async def handle_message_deletion(message):
    """
    Обрабатывает удаление сообщений в определенном канале и логирует информацию.
    """
    await message.delete()

    user = message.author
    dm_message = (
        "Ваше сообщение было удалено. Пожалуйста, соблюдайте структуру сообщений канала. "
        "Используйте команду `&team_help` для получения сведений."
    )

    # Логируем в канал LOG_CHANNEL_ID
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        print(f"❌ Не удалось найти канал с ID {LOG_CHANNEL_ID} для логов.")
        return

    try:
        # Отправляем ЛС пользователю
        await user.send(dm_message)

        # Логируем информацию о сообщении
        log_message = (
            f"{user.mention}, ваше сообщение было удалено. "
            "Пожалуйста, соблюдайте правила и структуру канала. "
            "Используйте `&team_help` для получения инструкций."
        )
        await log_channel.send(log_message)

        # Логируем причину удаления
        log_message = (
            f"❌ Сообщение пользователя {user.mention} "
            f"было удалено в канале {message.channel.mention}. "
            "Причина: нарушение правил."
        )
        await log_channel.send(log_message)

    except disnake.Forbidden:
        # Если не удается отправить ЛС (например, заблокировали бота)
        await log_channel.send(
            f"⚠️ Не удалось отправить ЛС пользователю {user.mention}."
        )

async def call_mention(message):
    """
    Обрабатывает упоминания бота и отвечает на определённые фразы.
    """
    text_without_mention = message.content.replace(
        f"<@{bot.user.id}>", ""
    ).strip()
    data = JsonData()

    # Проверяем вариации фраз из JsonData
    for variation in data.get_data("call_bot"):
        if fuzz.token_sort_ratio(text_without_mention.lower(), variation) > 80:
            # Список возможных мурчаний
            meow_responses = [
                "Мурррр?",
                "Мрья?! >~<",
                "Мрррр",
                "Мря? Я здеся 😽",
                "Мррр, как я тебя услышала?! 😸",
                "Мррр, что за вкусняшки принес?",
                "Мяу, ну что, погладим меня? 😻",
                "Мррр, ты меня разбудил!",
                "Мяууууу, где моя вкусняшка?!",
                "Мррр, не трогай моё место на диване! >_<",
            ]

            # Выбираем случайный ответ из списка
            responce = random.choice(meow_responses)

            await message.channel.send(responce)
            break


async def handle_mention(message):
    """
    Обрабатывает упоминания бота и отвечает на определённые фразы.
    """
    text_without_mention = message.content.replace(
        f"<@{bot.user.id}>", ""
    ).strip()
    data = JsonData()

    # Проверяем вариации фраз из JsonData
    for variation in data.get_data("hug_variations"):
        if fuzz.token_sort_ratio(text_without_mention.lower(), variation) > 80:
            await message.channel.send("*Обнимает в ответ.*")
            break

async def check_vpn_promotion(message):
    """
    Проверяет наличие фраз, связанных с VPN, используя fuzz.partial_token_sort_ratio.
    Если найдено совпадение — предлагает написать в Telegram-бота.
    """
    vpn_phrases = [
        "vpn",
        "хочу vpn",
        "ищу vpn",
        "нужен vpn",
        "рекомендую vpn",
        "что за vpn",
        "посоветуйте vpn",
        "впн",
        "хочу впн",
        "ищу впн",
        "нужен впн",
        "рекомендую впн",
        "что за впн",
        "посоветуйте впн",
        "в п н",
        "v p n",
    ]

    content = message.content.lower()
    for phrase in vpn_phrases:
        if fuzz.token_set_ratio(content, phrase) > 80:
            response = (
                "Упоминаете VPN? Могу порекомендовать\n"
                "**🛡 HellflareVPN 🔥 — щит и огонь из Нидерландов!**\n"
                "Наш VPN‑сервис обеспечивает **конфиденциальность**, **надежное шифрование** и безопасный интернет.\n"
                "Установить просто — пишите в Telegram `@HellflareVPN_Bot`."
            )
            await message.channel.send(response)
            break

async def handle_github_pattern(message):
    """
    Проверяет наличие шаблона GitHub issue/PR в сообщении и отправляет ссылку на него.
    """
    match = re.search(r"\[(n?|o)(\d+)\]", message.content)  # Добавлен необязательный префикс 'n'
    if match:
        repo_code, number = match.groups()
        # Если 'n' не найдено, то присваиваем 'n' по умолчанию
        repo_code = 'n' if not repo_code else repo_code
        embed_or_str = await get_github_link(repo_code, number)

        # Если получен embed (объект disnake.Embed)
        if isinstance(embed_or_str, disnake.Embed):
            await message.channel.send(embed=embed_or_str)
        elif isinstance(embed_or_str, str):
            # Отправка строки как обычного сообщения
            await message.channel.send(embed=disnake.Embed(description=embed_or_str))
        else:
            await message.channel.send("Не удалось получить информацию о PR или Issue.")


async def check_time_transfer_with_fuzz(message):
    """
    Проверяет наличие фраз, связанных с переносом времени, используя fuzz.
    """
    time_transfer_phrases = [
        "а где перенос времени",
        "где перенести время",
        "как перевести время",
        "перенос времени на роли",
        "перенос времени",
        "перенос времени с проекта",
        "Тут есть перенос времени",
        "я хочу понять где перенести время на этом проекте",
        "я хочу понять где перенести время",
        "хочу понять где перенести время",
        "я могу наскребать время с других серверов?"
        "время с других серверов?"
    ]

    # Проходим по каждой фразе и проверяем на совпадения с помощью fuzz
    for phrase in time_transfer_phrases:
        if fuzz.token_sort_ratio(message.content.lower(), phrase) > 80:
            # Ответ бота
            response = (
                "Вы говорите о переносе времени? "
                "Для таких вопросов ты можешь обратиться в следующий канал: "
                "https://discord.com/channels/901772674865455115/1341819793451384852"
            )

            # Отправляем ответ в канал
            await message.channel.send(response)
            break
