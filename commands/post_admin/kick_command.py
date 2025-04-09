import json

import requests

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_id
from config import (ADDRESS_MRP, POST_ADMIN_API,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)


@bot.command(name="kick")
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)
async def kick_command(ctx, nickName: str, reason: str):
    """
    Отправляет запрос на кик игрока через API сервера.
    Args:
        ctx (commands.Context): информация о вызывающем пользователе и канале.
        nickName (str): Никнейм игрока, который будет кикнут с сервера.
        reason (str): Причина кика.
    """

    discord_id = str(ctx.author.id)

    # Проверяем привязку Discord-аккаунта
    admin_user_id = ss14_db.get_user_id_by_discord_id(discord_id)
    if not admin_user_id:
        await ctx.send(
            "⚠️ Ваш Discord-аккаунт не привязан к игровому. "
            "Пожалуйста, привяжите его здесь: "
            "https://discord.com/channels/901772674865455115/1351213738774237184"
        )
        return

    # Проверяем, является ли пользователь администратором
    if not ss14_db.is_admin(admin_user_id):
        await ctx.send("❌ Ошибка: Вы не являетесь администратором в базе МРП.")
        return

    # Получаем никнейм по user_id
    adminName = ss14_db.get_username_by_user_id(admin_user_id)
    if not adminName:
        await ctx.send("⚠️ Ваш аккаунт SS14 не найден в БД МРП сервера.")
        return

    url = f"http://{ADDRESS_MRP}:1212/admin/actions/kick"

    # Проверяем, есть ли пользователь в БД player
    guidTarget_data = ss14_db.fetch_player_data(nickName)
    if not guidTarget_data or len(guidTarget_data) != 4:
        await ctx.send("❌ Пользователь не найден в базе данных")
        return

    player_id, user_id, first_seen_time, last_seen_user_name = guidTarget_data

    post_data = {
        "Guid": str(user_id),
        "Reason": reason,
    }

    actor_data = {
        "Guid": str(admin_user_id),
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

        await ctx.send(f"✅ Запрос на Кик успешно отправлен!")

    except requests.exceptions.Timeout:
        await ctx.send("🕒 Сервер не ответил за 5 секунд. Попробуйте позже.")
    except requests.exceptions.ConnectionError as e:
        await ctx.send(f"🔌 Ошибка подключения: {str(e)}")
    except requests.exceptions.HTTPError as e:
        await ctx.send(f"❌ Ошибка сервера: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await ctx.send(f"⚠️ Неизвестная ошибка: {str(e)}")
