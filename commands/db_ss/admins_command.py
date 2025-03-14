from datetime import datetime

import disnake
import psycopg2
import pytz

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import (DB_DATABASE, DB_HOST, DB_PARAMS,
                                              DB_PASSWORD, DB_PORT, DB_USER)
from commands.misc.check_roles import has_any_role_by_id
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST


# Функция запроса списка администраторов из базы данных
def fetch_admins(server):
    db_name = "ss14" if server.lower() == "mrp" else "ss14_dev"

    # Подключение к базе данных
    DB_PARAMS = {
        'database': db_name,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT
    }

    conn_params = {**DB_PARAMS}
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # SQL-запрос
    query = """
    SELECT p.last_seen_user_name, a.title, ar.name
    FROM public.admin a  -- Указываем явную схему public
    JOIN public.admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
    LEFT JOIN public.player p ON a.user_id = p.user_id
    ORDER BY p.last_seen_user_name ASC
    """

    cursor.execute(query)
    admins = cursor.fetchall()

    cursor.close()
    conn.close()

    return admins

# Класс для управления страницами
class AdminsView(disnake.ui.View):
    def __init__(self, ctx, admins, server):
        super().__init__(timeout=500)
        self.ctx = ctx
        self.admins = admins
        self.server = server.upper()
        self.per_page = 10  # Количество админов на одной странице

        self.total_pages = max((len(self.admins) - 1) // self.per_page, 0)
        self.page = self.total_pages

        self.children[1].disabled = self.page == self.total_pages

    def get_page_embed(self):
        tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(tz)

        total_admins = len(self.admins)
        start = self.page * self.per_page
        end = start + self.per_page
        admins_slice = self.admins[start:end]

        embed = disnake.Embed(
            title=f"🔧 Администраторы {self.server} ({total_admins})",
            color=disnake.Color.gold(),
            timestamp=current_time
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for admin_nickname, title, rank_name in admins_slice:
            embed.add_field(
                name=f"👤 {admin_nickname}",
                value=f"🏷 `{title}` | 🎖 `{rank_name}`",
                inline=False
            )

        return embed

    @disnake.ui.button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple, disabled=False)
    async def previous_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page -= 1
        button.disabled = self.page == 0
        self.children[1].disabled = False

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @disnake.ui.button(label="Вперёд ➡️", style=disnake.ButtonStyle.blurple, disabled=True)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page += 1
        button.disabled = self.page == self.total_pages
        self.children[0].disabled = False

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

# Команда для бота
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def admins(ctx, server: str = "mrp"):
    """
    Получает список всех администраторов из указанной базы данных (по умолчанию MRP).
    Использование: &admins [mrp/dev]
    """
    admins = fetch_admins(server)

    if not admins:
        embed = disnake.Embed(
            title=f"🔧 Администраторы {server.upper()} не найдены",
            description="В базе данных нет зарегистрированных администраторов.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = AdminsView(ctx, admins, server)
    await ctx.send(embed=view.get_page_embed(), view=view)
