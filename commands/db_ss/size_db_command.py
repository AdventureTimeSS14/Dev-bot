from datetime import datetime

import disnake
from disnake import Embed
from disnake.ui import Button, View

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST


class DBTablesView(View):
    def __init__(self, tables, total_size, db_name):
        super().__init__(timeout=60.0)
        self.tables = tables
        self.total_size = total_size
        self.db_name = db_name
        self.current_page = 0
        self.chunk_size = 20
        self.chunks = [self.tables[i:i + self.chunk_size] for i in range(0, len(self.tables), self.chunk_size)]
        
        # Обновляем состояние кнопок при инициализации
        self.update_buttons()

    def create_embed(self):
        embed = Embed(
            title=f"📊 Статистика базы {self.db_name.upper()} (стр. {self.current_page + 1}/{len(self.chunks)})",
            description=f"**Общий размер:** {self.total_size}\n**Всего таблиц:** {len(self.tables)}",
            color=0x2b2d31
        )
        
        tables_text = "\n".join(
            f"`{table['table']}`: {table['size']}" 
            for table in self.chunks[self.current_page]
        )
        
        embed.add_field(
            name="Таблицы и их размеры",
            value=tables_text,
            inline=False)
        
        return embed

    def update_buttons(self):
        # Очищаем существующие кнопки
        self.clear_items()
        
        # Кнопка "Назад"
        prev_button = Button(
            style=disnake.ButtonStyle.secondary,
            emoji="⬅️",
            disabled=self.current_page == 0)
        prev_button.callback = self.on_previous
        self.add_item(prev_button)
        
        # Кнопка "Вперёд"
        next_button = Button(
            style=disnake.ButtonStyle.secondary,
            emoji="➡️",
            disabled=self.current_page == len(self.chunks) - 1)
        next_button.callback = self.on_next
        self.add_item(next_button)

    async def on_previous(self, interaction):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed(),
            view=self)

    async def on_next(self, interaction):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed(),
            view=self)

@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def db_stats(ctx, db_name: str = 'main'):
    """
    Показывает статистику по таблицам базы данных
    Использование: &db_stats [main|dev] (по умолчанию main)
    """
    if db_name not in ['main', 'dev']:
        return await ctx.send("Доступные базы данных: main, dev")

    try:
        tables, total_size = ss14_db.get_tables_size(db_name)
        
        if not tables:
            return await ctx.send("В базе данных нет таблиц")
        
        view = DBTablesView(tables, total_size, db_name)
        await ctx.send(embed=view.create_embed(), view=view)
        
    except Exception as e:
        await ctx.send(f"⚠️ Ошибка при получении статистики: {str(e)}")
