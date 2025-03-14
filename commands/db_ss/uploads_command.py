from datetime import datetime

import disnake
import psycopg2
import pytz

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import (DB_DATABASE, DB_HOST, DB_PARAMS,
                                              DB_PASSWORD, DB_PORT, DB_USER)
from commands.misc.check_roles import has_any_role_by_id
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST


# Функция запроса списка загрузок файлов
def fetch_uploads(server):
    db_name = "ss14" if server.lower() == "mrp" else "ss14_dev"

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

    query = """
    SELECT ul.uploaded_resource_log_id, ul.date, p.last_seen_user_name, ul.path
    FROM public.uploaded_resource_log ul
    LEFT JOIN public.player p ON ul.user_id = p.user_id
    ORDER BY ul.date DESC
    """

    cursor.execute(query)
    uploads = cursor.fetchall()

    cursor.close()
    conn.close()

    return uploads

# Класс для управления страницами логов загрузок
class UploadsView(disnake.ui.View):
    def __init__(self, ctx, uploads, server):
        super().__init__(timeout=500)
        self.ctx = ctx
        self.uploads = uploads
        self.server = server.upper()
        self.per_page = 5

        self.total_pages = max((len(self.uploads) - 1) // self.per_page, 0)
        self.page = 0

        self.children[1].disabled = self.page == self.total_pages

    def get_page_embed(self):
        tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(tz)

        total_uploads = len(self.uploads)
        start = self.page * self.per_page
        end = start + self.per_page
        uploads_slice = self.uploads[start:end]

        embed = disnake.Embed(
            title=f"📂 Логи загрузок ({self.server})",
            color=disnake.Color.blue(),
            timestamp=current_time
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for log_id, date, username, path in uploads_slice:
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(
                name=f"📌 Лог ID: {log_id}",
                value=f"🕒 `{date_str}`\n👤 `{username if username else 'Неизвестный'}`\n📂 `{path}`",
                inline=False
            )

        return embed

    @disnake.ui.button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple, disabled=True)
    async def previous_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page -= 1
        button.disabled = self.page == 0
        self.children[1].disabled = False

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @disnake.ui.button(label="Вперёд ➡️", style=disnake.ButtonStyle.blurple, disabled=False)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page += 1
        button.disabled = self.page == self.total_pages
        self.children[0].disabled = False

        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

# Команда для просмотра логов загрузок файлов
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def uploads(ctx, server: str = "mrp"):
    """
    Получает список логов загруженных файлов из базы данных (по умолчанию MRP).
    Использование: &uploads [mrp/dev]
    """
    uploads = fetch_uploads(server)

    if not uploads:
        embed = disnake.Embed(
            title=f"📂 Логи загрузок {server.upper()} не найдены",
            description="В базе данных нет записей о загруженных файлах.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = UploadsView(ctx, uploads, server)
    await ctx.send(embed=view.get_page_embed(), view=view)
