import disnake
from disnake.ext import commands
from disnake.ui import Button, View

from bot_init import bot
from commands.dbCommand.get_db_connection import get_db_connection


@bot.command(name="show_vacation", description="Показать информацию о всех отпусках.")
async def show_vacation(ctx):
    conn = None
    cursor = None
    try:
        # Подключаемся к базе данных
        conn = get_db_connection()
        if not conn:
            await ctx.send("❌ Ошибка: Не удалось установить соединение с базой данных.")
            return
        cursor = conn.cursor()

        # Получаем все записи из таблицы vacation_team
        cursor.execute("SELECT discord_id, data_end_vacation, reason, created_at FROM vacation_team")
        users_vacation_info = cursor.fetchall()

        if not users_vacation_info:
            await ctx.send("❌ Нет пользователей с данными отпуска.")
            return

        # Создаем класс для пагинации
        class VacationPaginator(View):
            def __init__(self, data, items_per_page=5):
                super().__init__()
                self.data = data
                self.items_per_page = items_per_page
                self.current_page = 0

            def get_page_data(self):
                # Вычисляем, какие записи показывать на текущей странице
                start = self.current_page * self.items_per_page
                end = start + self.items_per_page
                return self.data[start:end]

            def get_total_pages(self):
                # Возвращаем количество страниц
                return (len(self.data) + self.items_per_page - 1) // self.items_per_page

            async def update_embed(self, interaction):
                embed = disnake.Embed(
                    title="Информация об отпусках",
                    description=f"Данные по пользователям с отпусками\n\n"
                                f"Страница {self.current_page + 1}/{self.get_total_pages()}",
                    color=disnake.Color.blue()
                )

                for user_id, data_end_vacation, reason, created_at in self.get_page_data():
                    try:
                        member = await ctx.guild.fetch_member(user_id)
                        user_name = member.name
                    except disnake.NotFound:
                        user_name = "Не найден"

                    embed.add_field(
                        name=f"{user_name} (<@{user_id}>)",
                        value=f"⏳ Окончание: {data_end_vacation}\n"
                            f"💬 Причина: {reason}\n"
                            f"📅 Создано: {created_at}",
                        inline=False
                    )

                # Обновляем сообщение с Embed
                await interaction.response.edit_message(embed=embed, view=self)

            @disnake.ui.button(label="Предыдущая", style=disnake.ButtonStyle.green)
            async def previous_page(self, button: Button, interaction: disnake.MessageInteraction):
                if self.current_page > 0:
                    self.current_page -= 1
                    await self.update_embed(interaction)

            @disnake.ui.button(label="Следующая", style=disnake.ButtonStyle.green)
            async def next_page(self, button: Button, interaction: disnake.MessageInteraction):
                if (self.current_page + 1) * self.items_per_page < len(self.data):
                    self.current_page += 1
                    await self.update_embed(interaction)

        # Создаем View с пагинацией
        paginator = VacationPaginator(users_vacation_info)

        # Отправляем первый Embed с общей информацией и кнопками
        embed = disnake.Embed(
            title="Информация об отпусках",
            description=f"Данные по пользователям с отпусками\n\n"
                        f"Страница 1/{paginator.get_total_pages()}",
            color=disnake.Color.blue()
        )

        for user_id, data_end_vacation, reason, created_at in paginator.get_page_data():
            try:
                member = await ctx.guild.fetch_member(user_id)
                user_name = member.name
            except disnake.NotFound:
                user_name = "Не найден"

            embed.add_field(
                name=f"{user_name} (<@{user_id}>)",
                value=f"⏳ Окончание: {data_end_vacation}\n"
                    f"💬 Причина: {reason}\n"
                    f"📅 Создано: {created_at}",
                inline=False
            )

        # Отправляем сообщение
        await ctx.send(embed=embed, view=paginator)

    except disnake.Forbidden:
        await ctx.send("⚠️ Ошибка: У бота недостаточно прав.")
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Ошибка: Не удалось выполнить запрос. Подробнее: {e}")
    except Exception as e:
        await ctx.send(f"Неожиданная ошибка: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
