import disnake
from disnake import TextInputStyle
from disnake.ext import tasks

from bot_init import bot

WL_ROLE_ID = 1060239440930418828
MESSAGE_WL_ID = 1352243736821895199
VOTE_CHANNEL_ID = 1351277093140303913  # ID канала голосования
WL_CHANNEL_ID = 1351277164217110628  # ID канала с кнопкой
submitted_users = set()  # Хранит ID пользователей, подавших заявку

async def get_pinned_message(channel):
    """
    Получает закреплённое сообщение, если оно есть.
    """
    pinned_messages = await channel.pins()
    for message in pinned_messages:
        if message.author == channel.guild.me:
            return message
    return None

# Форма подачи заявки на WL
class WhitelistApplicationModal(disnake.ui.Modal):
    """
        Класс модальной формы для WL
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
                label="2. Имя и описание персонажа",
                placeholder="Введите имя персонажа и его описание...",
                custom_id="character_info",
                style=TextInputStyle.paragraph,
                max_length=800,
            ),
            disnake.ui.TextInput(
                label="3. Время на сервере (в часах)",
                placeholder="Укажите количество часов...",
                custom_id="play_time",
                style=TextInputStyle.short,
                max_length=30,
            ),
            disnake.ui.TextInput(
                label="4. Предпочитаемые роли",
                placeholder="Перечислите желаемые роли...",
                custom_id="preferred_roles",
                style=TextInputStyle.paragraph,
                max_length=300,
            ),
            disnake.ui.TextInput(
                label="5. Человек с WL, готовый поручиться",
                placeholder="Напишите его Discord или оставьте пустым...",
                custom_id="recommender",
                style=TextInputStyle.short,
                required=False,
                max_length=100,
            ),
        ]
        super().__init__(title="Заявка на WL", components=components)

    async def callback(self, inter: disnake.ModalInteraction): # pylint: disable=W0221
        """
        Отправка анкеты в канал голосования.
        """
        # Проверяем, есть ли у участника роль White List
        if disnake.utils.get(inter.author.roles, id=WL_ROLE_ID):
            await inter.response.send_message(
                "🎉 Вы уже в White List! Повторная подача заявки не требуется.",
                ephemeral=True
            )
            return

        if inter.author.id in submitted_users:
            await inter.response.send_message(
                "⚠️ Вы уже подали заявку! Повторная подача возможна только после перезапуска бота.",
                ephemeral=True
            )
            return

        vote_channel = bot.get_channel(VOTE_CHANNEL_ID)
        if not vote_channel:
            await inter.response.send_message(
                "⚠️ Ошибка: Канал для голосования не найден!",
                ephemeral=True
            )
            return

        # Добавляем пользователя в список уже подавших заявку
        submitted_users.add(inter.author.id)

        # Формируем эмбед с анкетой
        embed = disnake.Embed(
            title="📜 Новая заявка на WL",
            description=(
                f"🔗 **Пользователь:** {inter.author.mention}"
                f"({inter.author})\n🆔 **Discord:** `{inter.author.id}`"
            ),
            color=disnake.Color.gold(),
            timestamp=inter.created_at,
        )

        embed.set_footer(
            text=f"Заявку подал(а): {inter.author}",
            icon_url=inter.author.display_avatar.url
        )

        embed.add_field(
            name="👤 **Сикей**",
            value=inter.text_values["ckey"],
            inline=False
        )

        embed.add_field(
            name="🎭 **Имя и описание персонажа**",
            value=inter.text_values["character_info"],
            inline=False
        )

        embed.add_field(
            name="⏳ **Время на сервере**",
            value=inter.text_values['play_time'],
            inline=False
        )

        embed.add_field(
            name="👾 **Предпочитаемые роли**",
            value=inter.text_values["preferred_roles"],
            inline=False
        )

        recommender = inter.text_values["recommender"] or "Нет рекомендаций"
        embed.add_field(
            name="🤝 **Рекомендации**",
            value=recommender,
            inline=False
        )

        # Отправляем заявку в канал голосования
        message = await vote_channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        # Ответ пользователю
        await inter.response.send_message(
            "✅ Ваша заявка отправлена на рассмотрение!",
            ephemeral=True
        )


# Кнопка подачи заявки
class WhitelistApplicationButton(disnake.ui.View):
    """
        Класс кнопки для вызова модального окна
    """
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="📜 Подать заявку на WL", style=disnake.ButtonStyle.primary)
    async def register(self, button: disnake.ui.Button, inter: disnake.MessageInteraction): # pylint: disable=W0613
        """
            Регистрация кнопки для модального окна
        """
        await inter.response.send_modal(WhitelistApplicationModal())


@tasks.loop(hours=12)
async def update_whitelist_application():
    """
    Обновляет сообщение с кнопкой каждые 12 часов.
    """
    channel = bot.get_channel(WL_CHANNEL_ID)
    if channel:
        # await channel.purge(limit=10)
        embed = disnake.Embed(
            title="📜 Подать заявку на WL",
            description=(
                "Чтобы получить доступ к игре на сервере WL, вам необходимо подать заявку.\n"
                "Нажмите кнопку ниже и заполните анкету.\n"
                "⏳ВНИМАНИЕ! Заявки принимаются только от лиц, наигравших на сервере минимум 100 часов."
            ),
            color=disnake.Color.green(),
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

        message_id = MESSAGE_WL_ID

        try:
            if message_id:
                old_message = await channel.fetch_message(message_id)
                await old_message.edit(embed=embed, view=WhitelistApplicationButton())
                print(f"✅ Сообщение обновлено Update WhiteList Application (ID: {message_id})")
                return
        except disnake.NotFound:
            print("❌ Старое сообщение не найдено. Создаём новое... Update WhiteList Application")

    # Если сообщение не найдено, ищем в закреплённых
    old_message = await get_pinned_message(channel)
    if old_message:
        await old_message.edit(embed=embed, view=WhitelistApplicationButton())
        print(f"✅ Используем закреплённое сообщение Update WhiteList Application (ID: {old_message.id})")
        return

    # Если старого сообщения нет, отправляем новое
    new_message = await channel.send(embed=embed, view=WhitelistApplicationButton())
    await new_message.pin()  # Закрепляем его
    print(f"✅ Отправлено новое сообщение Update WhiteList Application (ID: {new_message.id})")
