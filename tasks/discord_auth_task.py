import disnake
from disnake import TextInputStyle
from disnake.ext import tasks

from bot_init import bot


# Класс для модального окна
class NicknameModal(disnake.ui.Modal):
    """
        Класс модального окна для привязки аккаунта
    """
    def __init__(self):
        components = [
            disnake.ui.TextInput(
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
            Обработка ввода текста и сохранение данных в БД
        """
        nickname = inter.text_values["nickname_input"]
        discord_id = inter.author.id

        # Сохранение данных в базу данных
        # Чекаем сколько дис акку времени
        # . . .
        # get_creation_date(uuid) чекаем когда создан акк через API Визов
        # . . .
        # чекаем есть ли он у нас в бд, ПО ИДЕЕ должен быть если пытался присоединяться
        # . . .
        # проверяем привязан ли он уже, если уже привязан,
        # то мне в тех канал отправлять, о такой попытке
        # . . .
        # Ну и мне в тех канал тоже можно, что если привязали
        # . . .
        # Запись в БД
        # . . .
        # . . .

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
