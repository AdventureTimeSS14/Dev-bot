from datetime import datetime

import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys
from config import MOSCOW_TIMEZONE


# Команда поиска админа
@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def admin(ctx, nickname: str):
    """
    Проверяет, есть ли админ с таким ником в базе MRP и DEV.
    Использование: &admin <NickName>
    """
    mrp_admin_info = ss14_db.fetch_admin_info(nickname)
    dev_admin_info = ss14_db.fetch_admin_info(nickname, db_name='dev')

    if not mrp_admin_info and not dev_admin_info:
        embed = disnake.Embed(
            title="❌ Администратор не найден",
            description=f"**Пользователь** `{nickname}` **отсутствует в списке администраторов**.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Поиск выполнен в базах SS14 MRP & DEV", icon_url="https://i.imgur.com/6Y5xG0X.png")
        await ctx.send(embed=embed)
        return

    # Определяем текущую дату и время
    current_time = datetime.now(MOSCOW_TIMEZONE)

    # Создаем эмбед с улучшенным оформлением
    embed = disnake.Embed(
        title=f"🔧 **Информация об администраторе** `{nickname}`",
        color=disnake.Color.gold(),
        timestamp=current_time
    )

    if mrp_admin_info:
        embed.add_field(
            name="🟢 **MRP**",
            value=f"🏷 **Титул:** `{mrp_admin_info[0]}`\n🎖 **Ранг:** `{mrp_admin_info[1]}`",
            inline=False
        )

    if dev_admin_info:
        if mrp_admin_info:
            embed.add_field(name="──────────────────", value="⠀", inline=False)
        embed.add_field(
            name="🔵 **DEV**",
            value=f"🏷 **Титул:** `{dev_admin_info[0]}`\n🎖 **Ранг:** `{dev_admin_info[1]}`",
            inline=False
        )

    embed.set_footer(text="Данные взяты из базы SS14", icon_url="https://i.imgur.com/6Y5xG0X.png")

    await ctx.send(embed=embed)
