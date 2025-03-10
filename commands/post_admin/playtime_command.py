import disnake
import yaml
import aiohttp
from bot_init import bot

GITHUB_URLS = [
    "https://raw.githubusercontent.com/AdventureTimeSS14/space_station_ADT/master/Resources/Prototypes/Roles/Jobs/departments.yml",
    "https://raw.githubusercontent.com/AdventureTimeSS14/space_station_ADT/master/Resources/Prototypes/ADT/Roles/Jobs/departments.yml"
]

async def fetch_yaml(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return yaml.safe_load(await response.text())
            return None

class DepartmentView(disnake.ui.View):
    def __init__(self, departments):
        super().__init__(timeout=180)
        self.departments = departments
        self.index = 0

    async def update_message(self, interaction: disnake.MessageInteraction):
        dep_id, roles, color = self.departments[self.index]

        if not roles:
            roles = ["Нет доступных ролей"]

        # Форматируем роли с эмодзи 🆔
        formatted_roles = "\n".join([f"🆔 {role}" for role in roles])

        embed = disnake.Embed(
            title=f"**Департамент: {dep_id}**",
            description=formatted_roles,  # Используем форматированные роли
            color=int(color.strip("#"), 16)
        )
        embed.set_footer(text=f"Страница {self.index + 1} из {len(self.departments)}")

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple)
    async def prev_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.index = (self.index - 1) % len(self.departments)
        await self.update_message(interaction)
    
    @disnake.ui.button(label="Вперёд ➡️", style=disnake.ButtonStyle.blurple)
    async def next_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.index = (self.index + 1) % len(self.departments)
        await self.update_message(interaction)

@bot.command()
async def jobs(ctx):
    all_departments = []
    
    for url in GITHUB_URLS:
        yaml_data = await fetch_yaml(url)
        if yaml_data:
            for department in yaml_data:
                dep_id = department.get("id", "Unknown")
                roles = department.get("roles", [])
                color = department.get("color", "#00FF00")
                all_departments.append((dep_id, roles, color))
    
    if not all_departments:
        await ctx.send("Не удалось загрузить данные.")
        return
    
    dep_id, roles, color = all_departments[0]

    if not roles:
        roles = ["Нет доступных ролей"]

    # Форматируем роли с эмодзи 🆔
    formatted_roles = "\n".join([f"🆔 {role}" for role in roles])

    embed = disnake.Embed(
        title=f"**Департамент: {dep_id}**",
        description=formatted_roles,  # Используем форматированные роли
        color=int(color.strip("#"), 16)
    )

    embed.set_footer(text=f"Страница 1 из {len(all_departments)} • Используйте кнопки ниже для навигации")
    
    view = DepartmentView(all_departments)
    
    await ctx.send(embed=embed, view=view)
