import disnake
from disnake import Option

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM
from modules.utils import (fetch_player_data, is_user_linked,
                           link_user_to_discord, unlink_user_to_discord)

# Предположим, что у вас уже есть переменная bot, и она инициализирована

@bot.slash_command(name="dis_linc", description="Привязывает игрового пользователя к Discord.")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def linc_dis(
    inter: disnake.ApplicationCommandInteraction,
    nickname: str = Option(name="nickname", description="Никнейм в игре", required=True),
    discord: disnake.Member = Option(name="discord", description="Пинг или имя в Discord", required=True)
):
    """
    Привязывает игрового пользователя к Discord.
    
    Использование: /linc_dis <ник в игре> <пинг или имя в Discord>
    """

    # Получаем данные игрока из базы
    player_data = fetch_player_data(nickname)

    if not player_data:
        await inter.response.send_message(f"❌ Игрок с ником `{nickname}` не найден в базе данных.")
        return

    player_id, user_id, *_ = player_data
    discord_id = discord.id

    # Проверяем, не привязан ли уже этот пользователь или дискорд-аккаунт
    if is_user_linked(user_id, discord_id):
        await inter.response.send_message(f"⚠️ Этот Discord-аккаунт или игровой профиль уже привязан.")
        return

    # Привязываем пользователя
    link_user_to_discord(user_id, discord_id)

    await inter.response.send_message(f"✅ Игровой профиль `{nickname}` успешно привязан к {discord.mention}.")

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

    result = unlink_user_to_discord(discord)

    if result:
        await inter.response.send_message(f"✅ Привязка для {discord.mention} удалена.")
    else:
        await inter.response.send_message(f"❌ Привязка для {discord.mention} не найдена.")
