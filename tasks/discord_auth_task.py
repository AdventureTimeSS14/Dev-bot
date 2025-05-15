import disnake
from disnake import TextInputStyle
from disnake.ext import tasks
from disnake.ui import TextInput

from bot_init import bot, ss14_db
from modules.get_creation_date import get_creation_date

CHANNEL_AUTH_DISCORD_SS14_ID = 1351213738774237184
AUTH_MESSAGE_ID = 1352243068220342362
TECH_CHANNEL_ID = 1352227442730864650  # ID техканала для логов

async def get_pinned_message(channel):
    """
    Получает закреплённое сообщение, если оно есть.
    """
    pinned_messages = await channel.pins()
    for message in pinned_messages:
        if message.author == channel.guild.me:
            return message
    return None


class NicknameModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            TextInput(
                label="Введите ваш UID аккаунта SS14",
                placeholder="Ваш UID SS14",
                custom_id="user_id_input",
                style=TextInputStyle.short,
                max_length=50,
            )
        ]
        super().__init__(title="Привязка аккаунта SS14", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(with_message=False, ephemeral=True)

        user_id_input = inter.text_values["user_id_input"].strip()
        discord_id = str(inter.author.id)
        tech_channel = inter.bot.get_channel(TECH_CHANNEL_ID)

        if tech_channel is None:
            print("Ошибка: tech_channel не найден. Проверь ID или права доступа.")
            return

        # Проверяем user_id на валидность
        if not user_id_input or not user_id_input.strip():
            await inter.send(
                "❌ Ошибка: User ID не может быть пустым.\n"
                "Пожалуйста, введите ваш User ID.",
                ephemeral=True
            )
            return

        user_id = user_id_input

        # Проверяем, есть ли пользователь в базе по user_id
        player_data = ss14_db.fetch_player_data_by_user_id(user_id)  # Понадобится метод для поиска по user_id
        if not player_data:
            try:
                user = await inter.bot.fetch_user(discord_id)
                await user.send(
                    "❌ Ваш user_id не найден в базе данных. Попробуйте позже!"
                )
                await inter.send(
                    "❌ Ваш user_id не найден в базе данных. Попробуйте позже!",
                    ephemeral=True
                )
            except disnake.Forbidden:
                print(f"⚠️ Не удалось отправить ЛС пользователю {discord_id}")

            await tech_channel.send(
                f"⚠️ Пользователь <@{discord_id}> пытался привязать несуществующий user_id **{user_id}**."
            )
            return

        # Далее — логика привязки, аналогичная твоей, с использованием user_id

        # Проверка, привязан ли уже
        if ss14_db.is_user_linked(user_id, discord_id):
            try:
                discord_user = await inter.bot.fetch_user(discord_id)
                await discord_user.send(
                    "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна."
                )
                await inter.send(
                    "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна.",
                    ephemeral=True
                )
            except disnake.Forbidden:
                print(f"⚠️ Не удалось отправить ЛС пользователю {discord_id}")

            await tech_channel.send(
                f"⚠️ Пользователь <@{discord_id}> пытался повторно привязать user_id **{user_id}**."
            )
            return

        creation_date = get_creation_date(user_id)

        ss14_db.link_user_to_discord(user_id, discord_id)
        ss14_db.link_user_to_discord(user_id, discord_id, "dev")

        await tech_channel.send(
            f"✅ **Привязка аккаунта**\n"
            f"> **Discord ID:** {discord_id}\n"
            f"> **SS14 ID:** `{user_id}`\n"
            f"> **Дата создания аккаунта SS14:** {creation_date}\n"
        )

        try:
            discord_user = await inter.bot.fetch_user(discord_id)
            await discord_user.send(
                embed=disnake.Embed(
                    title="✅ Привязка завершена!",
                    description=f"Ваш SS14 user_id **{user_id}** успешно привязан.",
                    color=disnake.Color.green(),
                )
            )
            await inter.send(
                embed=disnake.Embed(
                    title="✅ Привязка завершена!",
                    description=f"Ваш SS14 user_id **{user_id}** успешно привязан.",
                    color=disnake.Color.green(),
                ),
                ephemeral=True
            )
        except disnake.Forbidden:
            print(f"⚠️ Не удалось отправить ЛС пользователю {discord_id}")


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
    Задача, выполняющаяся каждые 12 часов.
    Редактирует сообщение и активирует кнопку привязки аккаунта
    Если не находит его, то создаёт новое и закрепляет.
    """
    channel = bot.get_channel(CHANNEL_AUTH_DISCORD_SS14_ID)  # ID канала
    if channel:
        # await channel.purge(limit=10) # удаление 10 сообщений
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

        message_id = AUTH_MESSAGE_ID

        try:
            if message_id:
                old_message = await channel.fetch_message(message_id)
                await old_message.edit(embed=embed, view=RegisterButton())
                print(f"✅ Сообщение обновлено Update Discord Auth (ID: {message_id})")
                return
        except disnake.NotFound:
            print("❌ Старое сообщение не найдено. Создаём новое...")

    # Если сообщение не найдено, ищем в закреплённых
    old_message = await get_pinned_message(channel)
    if old_message:
        await old_message.edit(embed=embed, view=RegisterButton())
        print(f"✅ Используем закреплённое сообщение Update Discord Auth (ID: {old_message.id})")
        return

    # Если старого сообщения нет, отправляем новое
    new_message = await channel.send(embed=embed, view=RegisterButton())
    await new_message.pin()  # Закрепляем его
    print(f"✅ Отправлено новое сообщение Update Discord Auth (ID: {new_message.id})")
