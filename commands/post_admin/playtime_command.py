import disnake
import yaml
import aiohttp
import asyncio

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_id
from config import (
    ADDRESS_MRP,
    HEAD_ADT_TEAM,
    POST_ADMIN_HEADERS,
    WHITELIST_ROLE_PLAYTIME_POST,
)

GITHUB_URLS = [
    "https://raw.githubusercontent.com/AdventureTimeSS14/space_station_ADT/master/Resources/Prototypes/Roles/play_time_trackers.yml",
    "https://raw.githubusercontent.com/AdventureTimeSS14/space_station_ADT/master/Resources/Prototypes/Corvax/Roles/play_time_trackers.yml",
    "https://raw.githubusercontent.com/AdventureTimeSS14/space_station_ADT/master/Resources/Prototypes/ADT/Roles/play_time_trackers.yml",
]

async def fetch_yaml(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return yaml.safe_load(await response.text())
            return None

async def get_all_playtime_ids():
    all_ids = []
    for url in GITHUB_URLS:
        yaml_data = await fetch_yaml(url)
        if yaml_data:
            for entry in yaml_data:
                if entry.get("type") == "playTimeTracker":
                    all_ids.append(entry.get("id", "Unknown"))
    return all_ids

class PlaytimeView(disnake.ui.View):
    def __init__(self, playtime_ids, items_per_page=20):
        super().__init__(timeout=500)
        self.playtime_ids = playtime_ids
        self.items_per_page = items_per_page
        self.index = 0

    async def update_message(self, interaction: disnake.MessageInteraction):
        start = self.index * self.items_per_page
        end = start + self.items_per_page
        current_page = self.playtime_ids[start:end]

        embed = disnake.Embed(
            title="**PlayTime Trackers**",
            description="\n".join([f"🆔 {pt}" for pt in current_page]),
            color=disnake.Color.blue()
        )
        total_pages = (len(self.playtime_ids) + self.items_per_page - 1) // self.items_per_page
        embed.set_footer(text=f"Страница {self.index + 1} из {total_pages}")

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="⬅️ Назад", style=disnake.ButtonStyle.blurple)
    async def prev_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.index = (self.index - 1) % ((len(self.playtime_ids) + self.items_per_page - 1) // self.items_per_page)
        await self.update_message(interaction)

    @disnake.ui.button(label="Вперёд ➡️", style=disnake.ButtonStyle.blurple)
    async def next_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.index = (self.index + 1) % ((len(self.playtime_ids) + self.items_per_page - 1) // self.items_per_page)
        await self.update_message(interaction)

@bot.command()
async def playtime(ctx):
    playtime_ids = await get_all_playtime_ids()
    if not playtime_ids:
        await ctx.send("❌ Не удалось загрузить данные о PlayTime Trackers.")
        return
    
    embed = disnake.Embed(
        title="**PlayTime Trackers**",
        description="\n".join([f"🆔 {pt}" for pt in playtime_ids[:20]]),
        color=disnake.Color.blue()
    )
    total_pages = (len(playtime_ids) + 19) // 20
    embed.set_footer(text=f"Страница 1 из {total_pages}")

    view = PlaytimeView(playtime_ids)
    await ctx.send(embed=embed, view=view)


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, WHITELIST_ROLE_PLAYTIME_POST)
async def playtime_addrole(ctx, nickname: str, protojob: str, time: str):
    url = f"http://{ADDRESS_MRP}:1212/admin/actions/play_time_addjob"

    data = {
        "NickName": nickname,
        "JobIdPrototype": protojob,
        "Time": time,
    }

    allIdRoles = await get_all_playtime_ids()

    if protojob not in allIdRoles:
        await ctx.send(f"❌ Ошибка!! Указанной **{protojob}** не существует!")
        return

    # Уведомляем, что запрос отправлен
    await ctx.send(
                f"✅ Запрос на добавление времени для **{nickname}**\n"
                f"на должность **{protojob}** успешно отправлен!\n"
                f"⏱ Добавлено времени: **{time}**."
    )
    
    # Отправка POST запроса асинхронно без ожидания ответа
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=POST_ADMIN_HEADERS) as response:
                # Можно проверять успешность отправки, но не будем ожидать результата
                if response.status == 200:
                    print("Запрос отправлен")
                else:
                    await ctx.send(f"❌ Код ошибки: {response.status}")
        except Exception as e:
            print(f"Ошибка: {str(e)}")


@bot.command()
@has_any_role_by_id(HEAD_ADT_TEAM, WHITELIST_ROLE_PLAYTIME_POST)
async def playtime_generalrole(ctx, nickname: str):
    url = f"http://{ADDRESS_MRP}:1212/admin/actions/play_time_addjob"

    job_times = {
        "JobMedicalDoctor": "300",
        "JobMedicalIntern": "300",
        "JobResearchAssistant": "200",
        "JobScientist": "200",
        "JobCargoTechnician": "600",
        "JobServiceWorker": "600",
        "JobTechnicalAssistant": "300",
        "JobStationEngineer": "300",
        "Overall": "2800",
    }

    await ctx.send(f"✅ Запрос на добавление времени для **{nickname}** отправлен!\n🔄 Обрабатываю...")

    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Отправка запросов на каждую роль
        for job, time in job_times.items():
            data = {
                "NickName": nickname,
                "JobIdPrototype": job,
                "Time": str(time),
            }
            tasks.append(session.post(url, json=data, headers=POST_ADMIN_HEADERS))

        # Выполняем все запросы параллельно
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = 0
        error_messages = []

        for response in responses:
            if isinstance(response, Exception):
                error_messages.append(str(response))
            elif response.status == 200:
                success_count += 1
            else:
                error_text = await response.text()
                error_messages.append(f"Ошибка {response.status}: {error_text}")

    # Вывод результатов
    print(f"✅ Успешно обработано запросов: {success_count}/{len(job_times) + 1}")

    if error_messages:
        print(f"❌ Ошибки при обработке:\n" + "\n".join(error_messages))


# @bot.command() # Для тестов
# async def check_role(ctx, protojob: str):
#     try:
#         ProtoIdJob = protojob

#         all_roles = await get_all_roles()
#         if not ProtoIdJob in all_roles:
#             await ctx.send(f"❌ Ошибка!! Указанной **{ProtoIdJob}** не существует!")
#             return

#         await ctx.send(f"ВСЁ ОКЕЙ 💚 {ProtoIdJob} ТАКАЯ ЕСТЬ")
#     except Exception as e:
#         await ctx.send(f"An error occurred: {e}")