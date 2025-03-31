import json

import requests

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import (ADDRESS_MRP, POST_ADMIN_API,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST)
from modules.database_manager_class import (get_user_id_by_discord_id, get_username_by_user_id,
                           is_admin)


@bot.command(name="ban")
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def post_server_ban(ctx, nickName: str, reason: str, time: str):
    """
    Отправляет запрос на выдачу бана игроку через API сервера.
    Args:
        ctx (commands.Context): информация о вызывающем пользователе и канале.
        nickName (str): Никнейм игрока, которому будет выдан бан.
        reason (str): Причина бана.
        time (str): Время бана в минутах (сервер ожидает строку).
    """

    discord_id = str(ctx.author.id)

    # Проверяем привязку Discord-аккаунта
    user_id = get_user_id_by_discord_id(discord_id)
    if not user_id:
        await ctx.send(
            "⚠️ Ваш Discord-аккаунт не привязан к игровому. "
            "Пожалуйста, привяжите его здесь: "
            "https://discord.com/channels/901772674865455115/1351213738774237184"
        )
        return

    # Проверяем, является ли пользователь администратором
    if not is_admin(user_id):
        await ctx.send("❌ Ошибка: Вы не являетесь администратором в базе МРП.")
        return

    # Получаем никнейм по user_id
    adminName = get_username_by_user_id(user_id)
    if not adminName:
        await ctx.send("⚠️ Ваш аккаунт SS14 не найден в БД МРП сервера.")
        return

    # Проверка, что строка времени не пустая
    if not time.strip():
        await ctx.send("⏳ Ошибка: Время бана не может быть пустым.")
        return

    url = f"http://{ADDRESS_MRP}:1212/admin/actions/server_ban"

    post_data = {
        "NickName": nickName,
        "Reason": reason,
        "Time": time
    }

    actor_data = {
        "Guid": str(user_id),
        "Name": adminName
    }

    headers = {
        "Authorization": f"SS14Token {POST_ADMIN_API}",
        "Content-Type": "application/json",
        "Actor": json.dumps(actor_data)
    }

    # Отправляем запрос
    try:
        response = requests.post(url, json=post_data, headers=headers, timeout=5)
        response.raise_for_status()

        await ctx.send(f"✅ Запрос на Бан успешно отправлен!")

    except requests.exceptions.Timeout:
        await ctx.send("🕒 Сервер не ответил за 5 секунд. Попробуйте позже.")
    except requests.exceptions.ConnectionError as e:
        await ctx.send(f"🔌 Ошибка подключения: {str(e)}")
    except requests.exceptions.HTTPError as e:
        await ctx.send(f"❌ Ошибка сервера: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await ctx.send(f"⚠️ Неизвестная ошибка: {str(e)}")
