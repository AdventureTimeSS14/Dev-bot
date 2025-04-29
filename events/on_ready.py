import logging
import time

from bot_init import bot, db_sponsor, ss14_db
from commands.github import check_workflows
from config import LOG_CHANNEL_ID
from events.shutdows_after_time import shutdown_after_time
from tasks.check_end_vacation_task import check_end_vacation
from tasks.check_new_commit_task import monitor_commits
from tasks.check_size_adminlog_ss14_task import check_size_log
from tasks.clear_doker_replay_task import clear_doker_replay_ss14
from tasks.discord_auth_task import discord_auth_update
from tasks.git_fetch_pull_task import fetch_merged_pull_requests
from tasks.list_team_task import list_team_task
from tasks.update_admin_stats import update_admin_stats
from tasks.update_permission_stats import update_permission_stats
from tasks.update_status_presence_task import update_status_presence
from tasks.update_status_server_message_eddit_task import \
    update_status_server_message_eddit
from tasks.update_time_shutdows_task import update_time_shutdows
from tasks.whitelist_application_task import update_whitelist_application


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
    tasks_to_start = [
        (fetch_merged_pull_requests, "fetch merged pr"),
        (list_team_task, "list team"),
        (monitor_commits, "monitor commits"),
        (update_status_presence, "update status presence"),
        (update_status_server_message_eddit, "update status server"),
        (update_time_shutdows, "update time shutdows"),
        (discord_auth_update, "Update Discord Auth"),
        (update_whitelist_application, "Update WhiteList Application"),
        (update_admin_stats, "Update Admin Stats"),
        (check_end_vacation, "Check End Vacation"),
        (update_permission_stats, "Update Permission Stats"),
        (clear_doker_replay_ss14, "Clear Doker Replay"),
        (check_size_log, "Check Adminlogs size")
    ]
    
    # Для дебага
    # tasks_to_start = []

    for task, name in tasks_to_start:
        await start_task_if_not_running(task, name)

    print(ss14_db.get_connection_status_report())
    print(db_sponsor.get_connection_status_report())

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

    # Запуск задачи для автоматического завершения работы через определённое время
    bot.loop.create_task(shutdown_after_time())
