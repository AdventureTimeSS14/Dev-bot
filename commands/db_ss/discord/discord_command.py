import disnake
from disnake import Option

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM, WHITELIST_ROLE_ID_ADMINISTRATION_POST


@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def get_ckey(ctx, discordUser: disnake.Member):
    """Получить ckey (ник в SS14) пользователя по его Discord."""
    try:
        user_id = ss14_db.get_user_id_by_discord_id(str(discordUser.id))
        if not user_id:
            await ctx.send(f"❌ Пользователь {discordUser.mention} не привязан к SS14!")
            return

        userName = ss14_db.get_username_by_user_id(user_id)
        if not userName:
            await ctx.send(f"⚠ Никнейм не найден в базе данных.")
            return

        await ctx.send(
            f"🔹 **Discord:** {discordUser.nick} (ID: {discordUser.id})\n"
            f"🔹 **SS14 ник:** `{userName}`"
        )
    except Exception as e:
        await ctx.send(f"🚫 Ошибка при получении данных: `{str(e)}`")
        raise

@bot.slash_command(name="dis_linc", description="Привязывает игрового пользователя к Discord.")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def linc_dis(
    inter: disnake.ApplicationCommandInteraction,
    nickname: str = Option(
            name="nickname",
            description="Никнейм в игре",
            required=True
            ),
    discord: disnake.Member = Option(
                name="discord",
                description="Пинг или имя в Discord",
                required=True
            )
):
    """
    Привязывает игрового пользователя к Discord.
    
    Использование: /linc_dis <ник в игре> <пинг или имя в Discord>
    """

    # Получаем данные игрока из базы
    player_data = ss14_db.fetch_player_data(nickname)

    if not player_data:
        await inter.response.send_message(f"❌ Игрок с ником `{nickname}` не найден в базе данных.")
        return

    player_id, user_id, *_ = player_data
    discord_id = discord.id

    # Проверяем, не привязан ли уже этот
    # пользователь или дискорд-аккаунт
    if ss14_db.is_user_linked(user_id, discord_id):
        await inter.response.send_message(
            "⚠️ Этот Discord-аккаунт или "
            "игровой профиль уже привязан."
        )
        return

    # Привязываем пользователя
    ss14_db.link_user_to_discord(user_id, discord_id)

    await inter.response.send_message(
        f"✅ Игровой профиль `{nickname}` успешно "
        f"привязан к {discord.mention}."
    )


@bot.slash_command(name="dis_unlink", description="Удаляет привязку Discord-аккаунта.")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def unlink_dis(
    inter: disnake.ApplicationCommandInteraction,
    discord: disnake.Member = Option(name="discord", description="Пинг Discord", required=True)
):
    """
    Удаляет привязку Discord-аккаунта.
    
    Использование: /unlink_dis <пинг Discord>
    """

    result = ss14_db.unlink_user_from_discord(discord)

    if result:
        await inter.response.send_message(f"✅ Привязка для {discord.mention} удалена.")
    else:
        await inter.response.send_message(f"❌ Привязка для {discord.mention} не найдена.")
