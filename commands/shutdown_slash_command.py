"""
Слэш-команда для безопасного выключения бота.
"""

import asyncio
import sys

import disnake
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from commands.misc.shutdows_deff import shutdown_def


@bot.slash_command(
    name="shutdown",
    description="🔄 Безопасно выключает бота (только для администрации)",
    default_member_permissions=disnake.Permissions(administrator=True)
)
@has_any_role_by_keys("head_adt_team")
async def shutdown_slash(inter: disnake.ApplicationCommandInteraction):
    """
    Слэш-команда для перезапуска бота.
    Доступна только для пользователей с ролью из HEAD_ADT_TEAM.
    """
    try:
        # Проверяем, что пользователь имеет права
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(
                "❌ У вас нет прав администратора для выполнения этой команды.",
                ephemeral=True
            )
            return

        # Уведомляем пользователя
        await inter.response.send_message(
            "🔄 Запущен протокол завершения работы. Пожалуйста, подождите.",
            ephemeral=True
        )

        # Выполняем действия перед завершением работы
        await shutdown_def()

        # Отправляем финальное сообщение
        await inter.followup.send(
            f"⚠️ **{bot.user.name} завершает свою работу!**\n"
            f"🔄 Перезапуск начнётся в течение 10 минут.\n"
            f"📝 Все изменения сохранены.",
            ephemeral=False
        )

        # Небольшая задержка для отправки сообщения
        await asyncio.sleep(2)

        # Закрываем соединение бота
        await bot.close()

        # Завершаем процесс
        sys.exit(0)

    except ConnectionError as e:
        # Ошибки, связанные с сетью
        print(f"❌ Ошибка соединения: {e}")
        await inter.followup.send(
            "❌ Ошибка соединения. Проверьте логи.",
            ephemeral=True
        )

    except Exception as e:
        # Общая ошибка, если ничего более специфического не подошло
        print(f"❌ Произошла ошибка при попытке перезапуска: {e}")
        await inter.followup.send(
            "❌ Произошла ошибка при попытке перезапуска. Проверьте логи.",
            ephemeral=True
        )
