from datetime import datetime

import disnake
import psycopg2

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id
from config import MOSCOW_TIMEZONE, WHITELIST_ROLE_ID_ADMINISTRATION_POST


# Функция запроса данных о персонажах игрока
def fetch_profiles(nick_name):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT p.profile_id, p.preference_id, p.char_name, p.age, p.gender, p.species
    FROM profile p
    WHERE p.preference_id IN (
        SELECT pr.preference_id
        FROM preference pr
        WHERE pr.user_id IN (SELECT pl.user_id FROM player pl WHERE pl.last_seen_user_name = %s)
    )
    ORDER BY p.profile_id ASC
    """
    cursor.execute(query, (nick_name,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Класс для управления страницами
class ProfilesView(disnake.ui.View):
    def __init__(self, ctx, profiles, nick_name):
        super().__init__(timeout=500)
        self.ctx = ctx
        self.profiles = profiles
        self.nick_name = nick_name
        self.per_page = 5  # Количество профилей на одной странице

        self.total_pages = max((len(self.profiles) - 1) // self.per_page, 0)
        self.page = self.total_pages

        self.children[1].disabled = True if self.page == self.total_pages else False

    def get_page_embed(self):
        current_time = datetime.now(MOSCOW_TIMEZONE)

        total_profiles = len(self.profiles)
        start = self.page * self.per_page
        end = start + self.per_page
        profiles_slice = self.profiles[start:end]

        embed = disnake.Embed(
            title=f"📜 Персонажи игрока {self.nick_name} ({total_profiles})",
            color=disnake.Color.blue(),
            timestamp=current_time
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for profile_id, preference_id, char_name, age, gender, species in profiles_slice:
            embed.add_field(
                name=f"🆔 Профиль ID: `{profile_id}`",
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

# Команда для бота
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def profiles(ctx, *, nick_name: str):
    """
    Получает информацию о персонажах игрока по его нику.
    Использование: &profiles <NickName>
    """
    profiles = fetch_profiles(nick_name)

    if not profiles:
        embed = disnake.Embed(
            title="📜 Персонажи не найдены",
            description=f"У игрока **{nick_name}** нет зарегистрированных персонажей.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = ProfilesView(ctx, profiles, nick_name)
    await ctx.send(embed=view.get_page_embed(), view=view)

def fetch_profiles_by_id(profile_id):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT 
        p.profile_id, p.slot, p.char_name, p.age, p.sex, p.hair_name, p.hair_color, 
        p.facial_hair_name, p.facial_hair_color, p.eye_color, p.skin_color, p.pref_unavailable, 
        p.preference_id, p.gender, p.species, p.markings, p.flavor_text, p.voice, p.erpstatus, 
        p.spawn_priority, p.bark_pitch, p.bark_proto, p.high_bark_var, p.low_bark_var
    FROM profile p
    WHERE p.profile_id = %s
    """
    cursor.execute(query, (profile_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def profile_id(ctx, *, profile_id: str):
    """
    Получает информацию о персонаже по ID профиля.
    Использование: &profile_id <profile_id>
    """
    # Получаем данные о профиле
    profile_data = fetch_profiles_by_id(profile_id)

    if not profile_data:
        await ctx.send(f"❌ Профиль с ID {profile_id} не найден.")
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
    embed.add_field(name="🎨 Маркинги", value=profile_data[15] if profile_data[15] else "Нет", inline=True)
    embed.add_field(name="📝 Описание", value=profile_data[16] if profile_data[16] else "Нет", inline=True)
    embed.add_field(name="🎙️ Голос", value=profile_data[17] if profile_data[17] else "Не указан", inline=True)

    # Отправляем Embed в чат
    await ctx.send(embed=embed)
