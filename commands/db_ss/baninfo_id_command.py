from datetime import datetime

import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys
from config import MOSCOW_TIMEZONE


@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post", "general_adminisration_role")
async def baninfo_id(ctx, ban_id: str):
    """
    Получает полную информацию о бане по его ID.
    Использование: &baninfo_id <BanID>
    """
    ban_info = ss14_db.get_baninfo_by_ban_id(ban_id)

    if not ban_info:
        embed = disnake.Embed(
            title="🚫 Бан не найден",
            description=f"Бан с ID **{ban_id}** не существует.",
            color=disnake.Color.red(),
            timestamp=datetime.now(MOSCOW_TIMEZONE)
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=embed)
        return

    player_user_id, address, ban_time, expiration_time, reason, banning_admin, round_id = ban_info
    
    player_username = ss14_db.get_username_by_user_id(player_user_id)
    admin_username = ss14_db.get_username_by_user_id(banning_admin)

    # Форматирование времени
    ban_time_str = ban_time.strftime("%Y-%m-%d %H:%M:%S") if ban_time else "Неизвестно"
    exp_time_str = expiration_time.strftime("%Y-%m-%d %H:%M:%S") if expiration_time else "Постоянный бан"

    embed = disnake.Embed(
        title=f"🛑 Информация о бане ID: {ban_id}",
        color=disnake.Color.orange(),
        timestamp=datetime.now(MOSCOW_TIMEZONE)
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    # Основная информация
    embed.add_field(
        name="👤 Игрок",
        value=f"`{player_username}`",
        inline=True
    )
    embed.add_field(
        name="🌐 IP-адрес",
        value=f"`{address}`" if address else "`Неизвестно`",
        inline=True
    )
    embed.add_field(
        name="🎮 Раунд",
        value=f"`{round_id}`" if round_id else "`Неизвестно`",
        inline=True
    )
    
    # Временные данные
    embed.add_field(
        name="📅 Дата бана",
        value=f"`{ban_time_str}`",
        inline=True
    )
    embed.add_field(
        name="⏳ Истекает",
        value=f"`{exp_time_str}`",
        inline=True
    )
    
    # Причина и админ
    embed.add_field(
        name="👮 Администратор",
        value=f"`{admin_username}`" if banning_admin else "`Система`",
        inline=True
    )
    embed.add_field(
        name="📜 Причина",
        value=f"```\n{reason}\n```" if reason else "`Не указана`",
        inline=False
    )

    await ctx.send(embed=embed)
