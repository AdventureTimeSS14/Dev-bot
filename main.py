"""
Модуль для запуска бота.
"""

# pylint: skip-file
import asyncio
import logging
import signal
import sys

from bot_init import bot
from commands import (admin_help_command, echo_command, find_bans_command,
                      general_commands, gpt_command, help_command,
                      media_clear_command, shutdown_command, status_command,
                      uptime_command, user_role_command,
                      user_role_mention_command)
from commands.adt_team import (add_role_command, add_vacation_command,
                               end_vacation_command, extend_vacation_command,
                               new_team_command, remove_role_command,
                               remove_team_command, slash_team_command,
                               team_help_command, tweak_team_command,
                               while_list_command)
from commands.db_ss import (admin_command, admins_command, baninfo_id_command,
                            banlist_command, multi_akk_db_command,
                            pardon_command, permissions_command,
                            player_notes_command, player_time_command,
                            profiles_command, size_db_command, uploads_command)
from commands.db_ss.discord import discord_command
from commands.dbCommand import (get_vacations_command, help_command,
                                info_command, status_command)
from commands.github import (achang_command, branch_command, check_workflows,
                             deploy_command, forks_command,
                             git_cancel_invite_command, git_help_command,
                             git_invite_command, git_logininfo_command,
                             git_pending_invites_command, git_repoinfo_command,
                             git_team_command, github_processor,
                             milestones_command, pr_changelog_send,
                             publish_command, publish_status_command,
                             review_command)
from commands.misc.shutdows_deff import \
    shutdown_def  # Для выполнения завершающих операций
from commands.post_admin import (admin_info_command, admin_presets_command,
                                 bunker_command, game_rules_command,
                                 kick_command, playtime_command,
                                 replay_command, restart_command,
                                 server_ban_command, update_command)
from config import DISCORD_KEY
from events import (on_button_click, on_command, on_error, on_message,
                    on_ready, update_status)

# Настройка логирования
logging.basicConfig(
    level=logging.ERROR,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[
        logging.FileHandler("bot_logs.log"),  # Логирование в файл
        logging.StreamHandler(sys.stdout),  # Логирование в консоль
    ],
)


async def shutdown(signal_type=None):
    """
    Завершаем работу бота, выполняя все необходимые завершающие операции.

    :param signal_type: Тип сигнала, если он передан
    """
    logging.info(
        "Получен сигнал: %s. Завершаем работу...",
        signal_type.name if signal_type else "Manual Exit",
    )
    try:
        await shutdown_def()  # Выполнение завершающих операций
        await bot.close()  # Закрытие соединения бота
    except Exception as e:
        logging.error("Ошибка при завершении работы бота: %s", e)
    finally:
        sys.exit(0)  # Принудительное завершение процесса


def setup_signal_handlers():
    """
    Настроить обработчики сигналов для корректного завершения работы бота.
    """
    if sys.platform == "win32":
        logging.warning(
            "Сигналы SIGINT и SIGTERM не поддерживаются на Windows."
        )
    else:
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda s=sig: asyncio.create_task(shutdown(s))
            )


async def main():
    """
    Основная функция для запуска бота.
    """
    try:
        setup_signal_handlers()  # Настройка обработчиков сигналов
        logging.info("Запуск бота...")
        await bot.start(DISCORD_KEY)  # Запуск бота с токеном
    except (KeyboardInterrupt, SystemExit):
        await shutdown()  # Обработка принудительного завершения
    except Exception as e:
        logging.error("Неожиданная ошибка при запуске бота: %s", e)
        await shutdown()


if __name__ == "__main__":
    if DISCORD_KEY == "NULL":
        logging.error("Not DISCORD_KEY. Programm Dev-bot shutdown!!")
    else:
        bot.run(DISCORD_KEY)  # Запуск бота, без asyncio.run()
