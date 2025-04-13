"""
Команда для безопасного выключения бота.
"""

# import asyncio
import sys

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from commands.misc.shutdows_deff import shutdown_def



@bot.command(name="shutdown")
@has_any_role_by_keys("head_adt_team")
async def shutdown(ctx):
    """
    Команда для перезапуска бота.
    Доступна только для пользователей с ролью из HEAD_ADT_TEAM.
    """
    try:
        # Уведомляем пользователя в текущем канале
        await ctx.send(
            "🔄 Запущен протокол завершения работы. Пожалуйста, подождите."
        )

        # Выполняем действия перед завершением работы
        await shutdown_def()

        await ctx.send(
            f"⚠️ {bot.user} завершает свою работу! Перезапуск начнётся в течение 10 минут."
        )

        # Закрываем соединение бота
        await bot.close()

        # Завершаем процесс
        sys.exit(0)

    # except asyncio.CancelledError:
    #     # Обработка отмены асинхронной операции
    #     print("❌ Перезапуск был отменен.")
    #     await ctx.send("❌ Перезапуск был отменен.")

    except ConnectionError as e:
        # Ошибки, связанные с сетью
        print(f"❌ Ошибка соединения: {e}")
        await ctx.send("❌ Ошибка соединения. Проверьте логи.")

    except Exception as e:
        # Общая ошибка, если ничего более специфического не подошло
        print(f"❌ Произошла ошибка при попытке перезапуска: {e}")
        await ctx.send(
            "❌ Произошла ошибка при попытке перезапуска. Проверьте логи."
        )
