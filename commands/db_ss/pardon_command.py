from datetime import datetime

import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_id
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST


@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def pardon(ctx, ban_id: int):
    """
    Разбанивает игрока по ID бана.
    Использование: &pardon <ban_id>
    """
    discord_id = str(ctx.author.id)

    # Проверяем привязку Discord-аккаунта
    user_id = ss14_db.get_user_id_by_discord_id(discord_id)
    if not user_id:
        await ctx.send(
            "⚠️ Ваш дискорд-аккаунт не привязан к игровому. "
            "Пожалуйста, привяжите его здесь: "
            "https://discord.com/channels/901772674865455115/1351213738774237184"
        )
        return

    # Проверяем, является ли пользователь администратором
    if not ss14_db.is_admin(user_id):
        await ctx.send("❌ Ошибка: Вы не являетесь администратором в базе МРП.")
        return

    # Выполняем разбан
    success, message = ss14_db.pardon_ban(ban_id, user_id)

    # Создаем Embed для ответа
    color = disnake.Color.green() if success else disnake.Color.red()
    embed = disnake.Embed(
        title="🔓 Разбан игрока",
        description=message,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_author(
        name=ctx.author.display_name,
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    embed.set_footer(text="Операция выполнена через БД.")

    await ctx.send(embed=embed)
