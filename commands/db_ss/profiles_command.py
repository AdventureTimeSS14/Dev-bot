from datetime import datetime

import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_id
from config import (GENERAL_ADMINISRATION_ROLE, MOSCOW_TIMEZONE,
                    WHITELIST_ROLE_ID_ADMINISTRATION_POST)


# Класс для управления страницами
class ProfilesView(disnake.ui.View):
    def __init__(self, ctx, db_profiles, nick_name):
        super().__init__(timeout=500)
        self.ctx = ctx
        self.db_profiles = db_profiles
        self.nick_name = nick_name
        self.per_page = 5  # Количество профилей на одной странице

        self.total_pages = max((len(self.db_profiles) - 1) // self.per_page, 0)
        self.page = self.total_pages

        self.children[1].disabled = True if self.page == self.total_pages else False

    def get_page_embed(self):
        current_time = datetime.now(MOSCOW_TIMEZONE)

        total_profiles = len(self.db_profiles)
        start = self.page * self.per_page
        end = start + self.per_page
        profiles_slice = self.db_profiles[start:end]

        embed = disnake.Embed(
            title=f"📜 Персонажи игрока {self.nick_name} ({total_profiles})",
            color=disnake.Color.blue(),
            timestamp=current_time
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for player_profile_id, preference_id, char_name, age, gender, species in profiles_slice:
            embed.add_field(
                name=f"🆔 Профиль ID: `{player_profile_id}`",
                value=(
                    f"> 🎭 **Имя:** `{char_name}`\n"
                    f"> ⏳ **Возраст:** `{age}`\n"
                    f"> 🚻 **Гендер:** `{gender}`\n"
                    f"> 👽 **Раса:** `{species}`\n"
                    f"> 🔑 **Preference ID:** `{preference_id}`"
                ),
                inline=False
            )

        return embed

    @disnake.ui.button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple, disabled=False)
    async def previous_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page -= 1
        if self.page == 0:
            button.disabled = True

        self.children[1].disabled = False

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @disnake.ui.button(label="Вперёд ➡️", style=disnake.ButtonStyle.blurple, disabled=True)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page += 1
        if self.page == self.total_pages:
            button.disabled = True

        self.children[0].disabled = False

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)


@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)
async def profiles(ctx, nick_name: str, server: str = "mrp"):
    """
    Получает информацию о персонажах игрока по его нику.
    Использование: &profiles <NickName>
    """
    server = server.lower()

    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    profiles_data = ss14_db.fetch_profiles_by_nickname(nick_name, server)

    if not profiles_data:
        embed = disnake.Embed(
            title="📜 Персонажи не найдены",
            description=f"У игрока **{nick_name}** нет зарегистрированных персонажей.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = ProfilesView(ctx, profiles_data, nick_name)
    await ctx.send(embed=view.get_page_embed(), view=view)


@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)
async def profile_id(ctx, input_profile_id: str, server: str = "mrp"):
    """
    Получает информацию о персонаже по ID профиля.
    Использование: &profile_id <input_profile_id>
    """
    server = server.lower()

    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    # Получаем данные о профиле
    profile_data = ss14_db.fetch_profile_by_id(input_profile_id, server)

    if not profile_data:
        await ctx.send(f"❌ Профиль с ID {input_profile_id} не найден.")
        return

    # Создаем Embed объект
    embed = disnake.Embed(title=f"Профиль: {profile_data[2]}", color=disnake.Color.blue())

    # Добавляем поля в Embed с эмодзи
    embed.add_field(name="🔑 Профиль ID", value=str(profile_data[0]), inline=True)
    embed.add_field(name="🧳 Слот", value=str(profile_data[1]), inline=True)
    embed.add_field(name="👤 Имя персонажа", value=profile_data[2], inline=True)
    embed.add_field(name="🎂 Возраст", value=str(profile_data[3]), inline=True)
    embed.add_field(name="🚻 Пол", value=profile_data[4], inline=True)
    embed.add_field(name="🌐 Гендер", value=profile_data[13], inline=True)
    embed.add_field(name="💇 Название причёски", value=profile_data[5], inline=True)
    embed.add_field(name="🎨 Цвет волос", value=profile_data[6], inline=True)
    embed.add_field(name="👁️ Цвет глаз", value=profile_data[9], inline=True)
    embed.add_field(name="🎭 Цвет кожи", value=profile_data[10], inline=True)
    embed.add_field(name="👽 Раса", value=profile_data[14], inline=True)

    embed.add_field(
        name="🎨 Маркинги",
        value=profile_data[15] if profile_data[15] else "Нет",
        inline=True
    )
    embed.add_field(
        name="📝 Описание",
        value=profile_data[16] if profile_data[16] else "Нет",
        inline=True
    )
    embed.add_field(
        name="🎙️ Голос",
        value=profile_data[17] if profile_data[17] else "Не указан",
        inline=True
    )

    # Отправляем Embed в чат
    await ctx.send(embed=embed)


@bot.command(name="find_char")
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST, GENERAL_ADMINISRATION_ROLE)
async def fetch_username_by_char_name_command(ctx, char_name: str, server: str = "mrp"):
    """
    По имени персонажа выводит список ников с такими именами персов.
    Использование: &find_char <char_name> [server=mrp|dev]
    """
    server = server.lower()

    # Проверка допустимых значений сервера
    if server not in ("mrp", "dev"):
        await ctx.send("❌ Неверный сервер. Используйте `mrp` или `dev`.")
        return

    # Определяем базу данных
    db_name = "main" if server == "mrp" else "dev"

    try:
        # Ищем ники по имени персонажа
        userNameList = ss14_db.fetch_username_by_char_name(char_name, db_name)

        if not userNameList:
            await ctx.send(f"🔍 Персонаж `{char_name}` не найден на сервере `{server}`.")
            return

        # Форматируем список ников
        if len(userNameList) == 1:
            message = f"👤 Персонаж `{char_name}` принадлежит игроку: `{userNameList[0]}`"
        else:
            players_list = "\n".join([f"• `{name}`" for name in userNameList])
            message = f"👥 Персонаж `{char_name}` найден у {len(userNameList)} игроков:\n{players_list}"

        # Отправляем результат с ограничением длины сообщения
        if len(message) > 2000:
            # Если сообщение слишком длинное, разбиваем на части
            parts = [message[i:i+2000] for i in range(0, len(message), 2000)]
            for part in parts:
                await ctx.send(part)
        else:
            await ctx.send(message)

    except Exception as e:
        await ctx.send(f"❌ Произошла ошибка при поиске персонажа: {str(e)}")
        print(f"Error in fetch_username_by_char_name_command: {e}")
