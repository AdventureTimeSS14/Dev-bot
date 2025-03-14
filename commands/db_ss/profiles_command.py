import disnake
import psycopg2
from datetime import datetime
import pytz
from bot_init import bot
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id

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
        tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(tz)

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
