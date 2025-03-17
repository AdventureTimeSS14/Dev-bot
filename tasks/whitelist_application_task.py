import disnake
from disnake import TextInputStyle
from disnake.ext import tasks

from bot_init import bot

# ID канала с заявками
VOTE_CHANNEL_ID = 1351277093140303913
# ID канала, где висит кнопка
WL_CHANNEL_ID = 1351277164217110628


# Класс модального окна
class WhitelistApplicationModal(disnake.ui.Modal):
    """
    Форма для подачи заявки на вайтлист.
    """

    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="1. Ваш сикей (игровой UserName)",
                placeholder="Введите ваш сикей...",
                custom_id="ckey",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="2. Имя основного персонажа",
                placeholder="Введите имя персонажа...",
                custom_id="character_name",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="3. Описание персонажа",
                placeholder="Опишите вашего персонажа...",
                custom_id="character_desc",
                style=TextInputStyle.paragraph,
                max_length=500,
            ),
            disnake.ui.TextInput(
                label="4. Время на сервере (в часах)",
                placeholder="Укажите количество часов...",
                custom_id="play_time",
                style=TextInputStyle.short,
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="5. Предпочитаемые роли",
                placeholder="Перечислите желаемые роли...",
                custom_id="preferred_roles",
                style=TextInputStyle.paragraph,
                max_length=300,
            ),
            disnake.ui.TextInput(
                label="6. Человек с WL, готовый поручиться",
                placeholder="Напишите его Discord или оставьте пустым...",
                custom_id="recommender",
                style=TextInputStyle.short,
                required=False,
                max_length=100,
            ),
        ]

        super().__init__(title="Заявка на вайтлист", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        """
        Обработка заявки и отправка её в канал голосования.
        """
        vote_channel = bot.get_channel(VOTE_CHANNEL_ID)
        if not vote_channel:
            await inter.response.send_message(
                "⚠ Ошибка: Канал для голосования не найден!",
                ephemeral=True
            )
            return

        # Формируем текст заявки
        embed = disnake.Embed(
            title="📜 Новая заявка на WL",
            color=disnake.Color.blue(),
            timestamp=inter.created_at,
        )
        embed.set_footer(
            text=f"Заявку подал: {inter.author}",
            icon_url=inter.author.display_avatar.url
        )

        # Добавляем поля в эмбед
        embed.add_field(
            name="👤 Сикей",
            value=inter.text_values["ckey"],
            inline=False
        )
        embed.add_field(
            name="🎭 Имя персонажа",
            value=inter.text_values["character_name"],
            inline=False
        )
        embed.add_field(
            name="📖 Описание персонажа",
            value=inter.text_values["character_desc"],
            inline=False
        )
        embed.add_field(
            name="⏳ Время на сервере",
            value=inter.text_values["play_time"] + " часов",
            inline=False
        )
        embed.add_field(
            name="🔧 Предпочитаемые роли",
            value=inter.text_values["preferred_roles"],
            inline=False
        )
        recommender = inter.text_values["recommender"] or "Нет рекомендаций"
        embed.add_field(
            name="🤝 Рекомендации",
            value=recommender,
            inline=False
        )

        # Отправляем заявку в канал голосования
        message = await vote_channel.send(embed=embed)

        # Добавляем реакции для голосования
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        # Ответ пользователю
        await inter.response.send_message(
            "✅ Ваша заявка отправлена на рассмотрение!",
            ephemeral=True
        )


# Класс для кнопки
class WhitelistApplicationButton(disnake.ui.View):
    """
    Кнопка подачи заявки.
    """

    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="📜 Подать заявку на WL", style=disnake.ButtonStyle.primary)
    async def register(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(WhitelistApplicationModal())


@tasks.loop(hours=12)
async def update_whitelist_application():
    """
    Каждые 12 часов очищает канал и обновляет сообщение с кнопкой.
    """
    channel = bot.get_channel(WL_CHANNEL_ID)
    if channel:
        await channel.purge(limit=10)
        embed = disnake.Embed(
            title="📜 Подать заявку на WL",
            description=(
                "Чтобы получить доступ к игре на сервере WL, вам необходимо подать заявку.\n"
                "Нажмите кнопку ниже и заполните анкету."
            ),
            color=disnake.Color.green(),
        )
        embed.set_footer(text="Adventure Time SS14")

        await channel.send(embed=embed, view=WhitelistApplicationButton())
