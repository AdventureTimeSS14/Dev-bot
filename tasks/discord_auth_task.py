import disnake
import psycopg2
from disnake import TextInputStyle
from disnake.ext import tasks
from disnake.ui import TextInput

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.get_creation_date import get_creation_date

TECH_CHANNEL_ID = 1351438736356937778  # ID техканала для логов


def fetch_player_data(user_name):
    """
        Функция поиска пользователя в БД
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT player_id, user_id, first_seen_time, last_seen_user_name
    FROM player
    WHERE last_seen_user_name = %s
    """
    cursor.execute(query, (user_name,))
    result = cursor.fetchone()

    # Если не нашли в player, ищем в connection_log
    if result is None:
        query = """
        SELECT connection_log_id, user_id, user_name
        FROM connection_log
        WHERE user_name = %s
        """
        cursor.execute(query, (user_name,))
        result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def is_user_linked(user_id, discord_id):
    """
        Функция проверки привязан ли уже пользователь
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT * FROM discord_user WHERE user_id = %s AND discord_id = %s
    """
    cursor.execute(query, (user_id, discord_id))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None

def link_user_to_discord(user_id, discord_id):
    """
        Функция записи данных в БД
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    INSERT INTO discord_user (user_id, discord_id)
    VALUES (%s, %s)
    """
    cursor.execute(query, (user_id, discord_id))
    conn.commit()

    cursor.close()
    conn.close()


class NicknameModal(disnake.ui.Modal):
    """
        Класс модального окна
    """
    def __init__(self):
        components = [
            TextInput(
                label="Введите ваш никнейм в игре",
                placeholder="Ваш никнейм в SS14",
                custom_id="nickname_input",
                style=TextInputStyle.short,
                max_length=50,
            )
        ]
        super().__init__(title="Привязка аккаунта SS14", components=components)

    async def callback(self, inter: disnake.ModalInteraction): # pylint: disable=W0221
        """
            Действия при нажатии кнопки
        """
        nickname = inter.text_values["nickname_input"]
        discord_id = str(inter.author.id)
        tech_channel = inter.bot.get_channel(TECH_CHANNEL_ID)

        if tech_channel is None:
            print("Ошибка: tech_channel не найден. Проверь ID или права доступа.")
            return  # Прерываем выполнение

        # Проверяем, есть ли пользователь в БД player
        player_data = fetch_player_data(nickname)
        if not player_data:
            await inter.response.send_message(
                "❌ Ваш аккаунт не найден в базе данных. Попробуйте позже!",
                ephemeral=True,
            )
            await tech_channel.send(
                f"⚠️ Пользователь <@{discord_id}> ({discord_id}) пытался "
                f"привязать несуществующий аккаунт **{nickname}**."
            )
            return

        user_id = ""

        if len(player_data) == 4:  # Это значит, что данные пришли из таблицы player
            player_id, user_id, first_seen_time, last_seen_user_name = player_data
        if len(player_data) == 3:  # Это значит, что данные пришли из таблицы connection_log
            connection_log_id, user_id, user_name = player_data

        # Проверяем, не привязан ли уже пользователь
        if is_user_linked(user_id, discord_id):
            await tech_channel.send(
                f"⚠️ Пользователь <@{discord_id}> ({discord_id}) пытался "
                f"повторно привязать аккаунт **{nickname}**."
            )
            await inter.response.send_message(
                "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна.",
                ephemeral=True,
            )
            return

        # Получаем дату создания аккаунта
        creation_date = get_creation_date(user_id)

        # Записываем привязку в БД
        link_user_to_discord(user_id, discord_id)

        # Отправляем лог в техканал
        await tech_channel.send(
            f"✅ **Привязка аккаунта**\n"
            f"> **Никнейм:** {nickname}\n"
            f"> **Discord ID:** {discord_id}\n"
            f"> **SS14 ID:** `{user_id}`\n"
            f"> **Дата создания аккаунта:** {creation_date}"
        )

        # Отправляем сообщение пользователю
        await inter.response.send_message(
            embed=disnake.Embed(
                title="✅ Привязка завершена!",
                description=f"Ваш никнейм **{nickname}** успешно привязан.",
                color=disnake.Color.green(),
            ),
            ephemeral=True,
        )


# Класс для кнопки
class RegisterButton(disnake.ui.View):
    """
        Регистрация кнопки
    """
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="🔗 Привязать аккаунт", style=disnake.ButtonStyle.primary)
    async def register(self, button: disnake.ui.Button, inter: disnake.MessageInteraction): # pylint: disable=W0613
        """
            Вызов модального окна
        """
        await inter.response.send_modal(NicknameModal())


@tasks.loop(hours=12)
async def discord_auth_update():
    """
    Задача, выполняющаяся каждые 12 часов. Очищает канал от последних 10 сообщений
    и отправляет сообщение с кнопкой для привязки аккаунта SS14.
    """
    channel = bot.get_channel(1351213738774237184)  # ID канала
    if channel:
        await channel.purge(limit=10)
        embed = disnake.Embed(
            title="🔗 Привязка аккаунта SS14",
            description=(
                "Для игры на сервере вам необходимо привязать свой аккаунт SS14.\n"
                "Нажмите кнопку ниже, затем введите ваш никнейм в игре."
            ),
            color=disnake.Color.blue(),
        )
        embed.set_footer(
            text="Adventure Time SS14",
            icon_url=(
                "https://media.discordapp.net/attachments/"
                "1255118642442403986/1351231449470079046/icon"
                "-256x256.png?ex=67d99fda&is=67d84e5a&hm=5843e1"
                "d7e0f726d77e4882f66e9fdadcabea8f9fd4f6f26212327"
                "e986f22ed5d&=&format=webp&quality=lossless&widt"
                "h=288&height=288"
            )
        )

        await channel.send(embed=embed, view=RegisterButton())
