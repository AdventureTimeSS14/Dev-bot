import logging
import time

import disnake
from disnake.ext import commands

from bot_init import bot
from commands.github import check_workflows
from config import LOG_CHANNEL_ID
from events.shutdows_after_time import shutdown_after_time
from tasks.check_new_commit_task import monitor_commits
from tasks.discord_auth_task import discord_auth_update
from tasks.git_fetch_pull_task import fetch_merged_pull_requests
from tasks.list_team_task import list_team_task
from tasks.update_admin_stats import update_admin_stats
from tasks.update_status_presence_task import update_status_presence
from tasks.update_status_server_message_eddit_task import \
    update_status_server_message_eddit
from tasks.update_time_shutdows_task import update_time_shutdows
from tasks.whitelist_application_task import update_whitelist_application
from tasks.check_end_vacation_task import check_end_vacation


async def start_task_if_not_running(task, task_name: str):
    """
    Запускает задачу, если она еще не запущена.
    """
    if not task.is_running():
        task.start()
        print(f"✅ Задача {task_name} запущена.")
    else:
        print(f"⚙️ Задача {task_name} уже работает.")


@bot.event
async def on_ready():
    """
    Событие, которое выполняется при запуске бота.
    """
    logging.info(
        "Bot %s (ID: %d) is ready to work!", bot.user.name, bot.user.id
    )
    logging.info("Connected to Discord successfully.")
    guild_names = [guild.name for guild in bot.guilds]
    logging.info("Guilds: %s", guild_names)  # Выводит список серверов, к которым подключен бот.

    print("✅ Connected to Discord successfully.")
    print(f"✅ Guilds: {guild_names}")  # Выводит список серверов, к которым подключен бот.

    bot.start_time = time.time()  # Сохраняем время старта бота

    # Проверка workflows на случай повторного запуска на GitHub Actions
    await check_workflows.check_workflows()  # Завершает работу,
                                             # если бот уже запущен на GitHub Actions

    # Запуск всех фоновых задач
    await start_task_if_not_running(fetch_merged_pull_requests, "fetch merged pr")
    await start_task_if_not_running(list_team_task, "list team")
    await start_task_if_not_running(monitor_commits, "monitor commits")
    await start_task_if_not_running(update_status_presence, "update status presence")
    await start_task_if_not_running(update_status_server_message_eddit, "update status server")
    await start_task_if_not_running(update_time_shutdows, "update time shutdows")
    await start_task_if_not_running(discord_auth_update, "Update Discord Auth")
    await start_task_if_not_running(update_whitelist_application, "Update WhiteList Application")
    await start_task_if_not_running(update_admin_stats, "Update Admin Stats")
    await start_task_if_not_running(check_end_vacation, "Check End Vacation")

    print(f"✅ Bot {bot.user.name} (ID: {bot.user.id}) is ready to work!")

    # Уведомляем в лог-канале, что бот активен
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(
            content=(
                f"✅ **{bot.user.name} успешно активирована!**\n"
                f"🔹 **Статус:** Бот запущен и готов к работе.\n_ _"
            )
        )
    else:
        print(f"❌ Не удалось найти канал с ID {LOG_CHANNEL_ID} для логов.")
        
    # await bot.sync_commands()
    # await bot.command_sync_flags()
    # await bot._sync_application_commands()
    # await bot.tree.sync()

    # Запуск задачи для автоматического завершения работы через определённое время
    bot.loop.create_task(shutdown_after_time())
