from datetime import datetime

import disnake
import psycopg2

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys
from config import MOSCOW_TIMEZONE


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
        current_time = datetime.now(MOSCOW_TIMEZONE)

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
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def uploads(ctx, server: str = "mrp"):
    """
    Получает список логов загруженных файлов из базы данных (по умолчанию MRP).
    Использование: &uploads [mrp/dev]
    """
    server = server.lower()

    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    uploads = ss14_db.fetch_uploads(server)

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

@bot.command(name="search")
async def search(ctx, *, user_name: str):
    """
    Поиск эмбедов по нику и вывод количества найденных результатов.
    """
    channel = bot.get_channel(1041654367712976966)
    if not channel:
        await ctx.send("Канал логов не найден!")
        return

    print(f"Поиск по нику: {user_name}")  # Логирование
    print(f"Канал: {channel.name}")  # Логирование

    # Счётчик найденных эмбедов
    embed_count = 0

    # Поиск эмбедов по нику
    async for message in channel.history(limit=4000):  # Проверяем только последние 500 сообщений
        for embed in message.embeds:
            # Проверяем заголовок, описание и поля эмбеда
            if (embed.title and user_name.lower() in embed.title.lower()) or \
               (embed.description and user_name.lower() in embed.description.lower()):
                embed_count += 1
                print(f"Найден эмбед: {embed.title}")  # Логирование
                continue

            # Проверяем поля эмбеда
            for field in embed.fields:
                if user_name.lower() in field.name.lower() or user_name.lower() in field.value.lower():
                    embed_count += 1
                    print(f"Найден эмбед: {field.name}")  # Логирование
                    break

    print(f"Найдено эмбедов: {embed_count}")  # Логирование

    # Отправляем результат
    await ctx.send(f"🔍 Найдено эмбедов с ником **{user_name}**: **{embed_count}**")
