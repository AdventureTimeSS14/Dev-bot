import disnake
import psycopg2
from datetime import datetime
import pytz
from bot_init import bot
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id

# Функция запроса данных о банах игрока
def fetch_banlist(nick_name):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT 
        sb.server_ban_id, 
        sb.ban_time, 
        sb.expiration_time, 
        sb.reason, 
        COALESCE(p.last_seen_user_name, 'Неизвестно') AS admin_nickname,
        ub.unban_time,
        COALESCE(p2.last_seen_user_name, 'Неизвестно') AS unban_admin_nickname
    FROM server_ban sb
    LEFT JOIN player p ON sb.banning_admin = p.user_id
    LEFT JOIN server_unban ub ON sb.server_ban_id = ub.ban_id
    LEFT JOIN player p2 ON ub.unbanning_admin = p2.user_id
    WHERE sb.player_user_id = (
        SELECT user_id FROM player WHERE last_seen_user_name = %s
    )
    ORDER BY sb.server_ban_id ASC
    """
    cursor.execute(query, (nick_name,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Класс для управления страницами
class BanlistView(disnake.ui.View):
    def __init__(self, ctx, bans, nick_name):
        super().__init__(timeout=500)
        self.ctx = ctx
        self.bans = bans
        self.nick_name = nick_name
        self.per_page = 5  # Количество банов на одной странице

        # Устанавливаем изначально последнюю страницу
        self.total_pages = max((len(self.bans) - 1) // self.per_page, 0)
        self.page = self.total_pages

        # Если мы на последней странице, отключаем кнопку "Вперёд ➡️"
        self.children[1].disabled = True if self.page == self.total_pages else False

    def get_page_embed(self):
        tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(tz)

        total_bans = len(self.bans)
        start = self.page * self.per_page
        end = start + self.per_page
        bans_slice = self.bans[start:end]

        embed = disnake.Embed(
            title=f"🔍 Баны игрока {self.nick_name} ({total_bans})",
            color=disnake.Color.orange(),
            timestamp=current_time
        )
        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url if self.ctx.author.avatar else None)
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for ban in bans_slice:
            ban_id, ban_time, expiration_time, reason, admin_nickname, unban_time, unban_admin_nickname = ban

            ban_time_str = ban_time.strftime("%Y-%m-%d %H:%M:%S") if ban_time else "Неизвестно"
            exp_time_str = expiration_time.strftime("%Y-%m-%d %H:%M:%S") if expiration_time else "Постоянный бан"

            ban_info = (
                f"> 📅 **Дата бана:** `{ban_time_str}`\n"
                f"> ⏳ **Истекает:** `{exp_time_str}`\n"
                f"> 📜 **Причина:** `{reason}`\n"
                f"> 👮 **Админ:** `{admin_nickname}`"
            )

            if unban_time:
                unban_time_str = unban_time.strftime("%Y-%m-%d %H:%M:%S")
                ban_info += (
                    f"\n> ✅ **Бан был снят!**\n"
                    f"> 🕒 **Дата разбана:** `{unban_time_str}`\n"
                    f"> 🔓 **Разбанил:** `{unban_admin_nickname}`"
                )

            embed.add_field(
                name=f"🛑 Бан ID: `{ban_id}`",
                value=ban_info,
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

        self.children[1].disabled = False  # Включаем кнопку "Вперёд ➡️"

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @disnake.ui.button(label="Вперёд ➡️", style=disnake.ButtonStyle.blurple, disabled=True)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page += 1
        if self.page == self.total_pages:
            button.disabled = True

        self.children[0].disabled = False  # Включаем кнопку "⬅️ Назад"

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

# Команда для бота
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def banlist(ctx, *, nick_name: str):
    """
    Получает информацию о банах игрока по его нику.
    Использование: &banlist <NickName>
    """
    bans = fetch_banlist(nick_name)

    if not bans:
        embed = disnake.Embed(
            title="🚫 Баны не найдены",
            description=f"Игрок **{nick_name}** не имеет активных банов.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = BanlistView(ctx, bans, nick_name)
    await ctx.send(embed=view.get_page_embed(), view=view)
