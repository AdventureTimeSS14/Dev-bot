from datetime import datetime

import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys
from config import MOSCOW_TIMEZONE


class AdminsView(disnake.ui.View):
    """
        Класс для управления страницами
    """
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
        current_time = datetime.now(MOSCOW_TIMEZONE)

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

        for admin_nickname, title, rank_name, discord_id in admins_slice:
            discord_info = f"🔗 <@{discord_id}>" if discord_id else "🚫 Не привязан"
            embed.add_field(
                name=f"👤 {admin_nickname}",
                value=f"🏷 `{title}` | 🎖 `{rank_name}`\n{discord_info}",
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

@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def admins(ctx, server: str = "mrp"):
    """
    Получает список всех администраторов из указанной базы данных (по умолчанию MRP).
    Использование: &admins [mrp/dev]
    """
    server = server.lower()
    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    admins = ss14_db.fetch_admins(server)

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
