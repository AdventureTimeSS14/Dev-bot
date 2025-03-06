import disnake
import psycopg2
from bot_init import bot
from config import WHITELIST_ROLE_ID_ADMINISTRATION_POST
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id
from datetime import datetime, timedelta

# Функция для получения статистики игрока
def fetch_player_stats(user_name):
    connection = psycopg2.connect(**DB_PARAMS)
    cursor = connection.cursor()

    cursor.execute('''
        SELECT 
            play_time.tracker,
            play_time.time_spent
        FROM player
        INNER JOIN play_time ON player.user_id = play_time.player_id
        WHERE player.last_seen_user_name = %s;
    ''', (user_name,))

    result = cursor.fetchall()
    cursor.close()
    connection.close()

    return result

# Класс для управления страницами
class PlayerStatsView(disnake.ui.View):
    def __init__(self, ctx, stats, user_name):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.stats = stats
        self.user_name = user_name
        self.per_page = 10  # Количество записей на странице

        # Устанавливаем последнюю страницу
        self.total_pages = max((len(self.stats) - 1) // self.per_page, 0)
        self.page = self.total_pages

        # Если мы на последней странице, отключаем кнопку "➡️ Вперёд"
        self.children[1].disabled = True if self.page == self.total_pages else False

    def format_time(self, time_spent):
        """Форматирует время в нужный формат"""
        if isinstance(time_spent, timedelta):
            total_seconds = time_spent.total_seconds()
            total_days = int(total_seconds // 86400)  # 86400 секунд в дне
            total_hours = int((total_seconds % 86400) // 3600)
            total_minutes = int((total_seconds % 3600) // 60)
        else:
            # Если time_spent строка, разбираем вручную
            time_parts = time_spent.split(':')
            total_hours, total_minutes, total_seconds = map(float, time_parts)
            total_days = 0  # Учитываем только часы, минуты и секунды

        return f'{total_days:04};{total_hours:02};{total_minutes:02}'

    def get_page_embed(self):
        current_time = datetime.now()
        total_stats = len(self.stats)
        start = self.page * self.per_page
        end = start + self.per_page
        stats_slice = self.stats[start:end]

        embed = disnake.Embed(
            title=f"🕒 Временная статистика игрока {self.user_name} ({total_stats})",
            color=disnake.Color.green(),
            timestamp=current_time
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {self.total_pages + 1}")

        for tracker, time_spent in stats_slice:
            time_str = self.format_time(time_spent)

            embed.add_field(
                name=f'📌 Роль: `{tracker}`',
                value=f'> ⏳ **Наиграно:** `{time_str}`',
                inline=True
            )

        return embed

    @disnake.ui.button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple, disabled=False)
    async def previous_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page -= 1
        if self.page == 0:
            button.disabled = True

        self.children[1].disabled = False  # Включаем кнопку "➡️ Вперёд"
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @disnake.ui.button(label="➡️ Вперёд", style=disnake.ButtonStyle.blurple, disabled=True)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Вы не можете управлять этим сообщением!", ephemeral=True)

        self.page += 1
        if self.page == self.total_pages:
            button.disabled = True

        self.children[0].disabled = False  # Включаем кнопку "⬅️ Назад"
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

# Команда для получения временной статистики
@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def player_stats(ctx, *, user_name: str):
    """
    Получает информацию о временной статистике игрока.
    Использование: &player_stats <NickName>
    """
    stats = fetch_player_stats(user_name)

    if not stats:
        embed = disnake.Embed(
            title="📜 Статистика не найдена",
            description=f"Для игрока **{user_name}** нет данных.",
            color=disnake.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text="Информация предоставлена из БД")
        await ctx.send(embed=embed)
        return

    view = PlayerStatsView(ctx, stats, user_name)
    await ctx.send(embed=view.get_page_embed(), view=view)
