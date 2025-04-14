from datetime import datetime

import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys


# Класс для управления страницами
class PlayerNotesView(disnake.ui.View):
    def __init__(self, ctx, notes, user_name):
        super().__init__(timeout=500)
        self.ctx = ctx
        self.notes = notes
        self.user_name = user_name
        self.per_page = 5  # Количество заметок на странице

        # Устанавливаем последнюю страницу
        self.total_pages = max((len(self.notes) - 1) // self.per_page, 0)
        self.page = self.total_pages

        # Если мы на последней странице, отключаем кнопку "Вперёд ➡️"
        self.children[1].disabled = True if self.page == self.total_pages else False

    def get_page_embed(self):
        current_time = datetime.now()
        total_notes = len(self.notes)
        start = self.page * self.per_page
        end = start + self.per_page
        notes_slice = self.notes[start:end]

        embed = disnake.Embed(
            title=f"📓 Заметки об игроке {self.user_name} ({total_notes})",
            color=disnake.Color.dark_red(),
            timestamp=current_time
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for note in notes_slice:
            note_id, created_at, message, severity, secret, last_edited_at, last_edited_by_id, player_id, last_seen_user_name, created_by_name = note

            # Убираем переносы строк в сообщении
            message = message.replace('\n', ' ') if message else 'Нет сообщения'

            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'Не указано'
            last_edited_at = last_edited_at.strftime('%Y-%m-%d %H:%M:%S') if last_edited_at else 'Не указано'

            # Определяем, нужно ли выводить информацию о редактировании
            edit_info = ''
            if created_at != last_edited_at:
                edit_info = f"> 🖊 **Редактировал:** `{last_edited_at}`"

            embed.add_field(
                name=f'📕 Заметка ID: `{note_id}`',
                value=(
                    f'> 📅 **Дата:** `{created_at}`\n'
                    f'> 👮 **Администратор:** `{created_by_name or "Неизвестно"}`\n'
                    f'> 💬 **Сообщение:** `{message}`\n'
                    f'{edit_info}\n'
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
@has_any_role_by_keys("whitelist_role_id_administration_post", "general_adminisration_role")
async def player_notes(ctx, *, user_name: str):
    """
    Получает информацию о заметках игрока по нику.
    Использование: &player_notes <NickName>
    """
    notes = ss14_db.fetch_player_notes_by_username(user_name)

    if not notes:
        embed = disnake.Embed(
            title="📜 Заметки не найдены",
            description=f"У игрока **{user_name}** нет заметок.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = PlayerNotesView(ctx, notes, user_name)
    await ctx.send(embed=view.get_page_embed(), view=view)
