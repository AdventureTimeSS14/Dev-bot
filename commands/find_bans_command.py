import io
import traceback
from datetime import datetime

import disnake

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from commands.misc.search_bans_in_channel import \
    search_bans_in_multiple_channels


@bot.command(name="find_bans")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def find_bans(ctx, username: str):
    await ctx.send(
        "[⚠] Временно отключено из-за изменений в Discord API.\n" +
        "Статус: Поддержка команды приостановлена."
    )
    
    # await ctx.send(f"🔍 Ищу баны по нику `{username}`...")

    # try:
    #     search_results = await search_bans_in_multiple_channels(username)

    #     if not search_results:
    #         await ctx.send("⚠ Произошла ошибка при поиске.")
    #         return

    #     # Распаковываем: список сообщений, статус и кол-во пермабанов
    #     messages, status_message, permanent_bans_count, total_bans = search_results

    #     if not messages:
    #         await ctx.send(status_message)
    #         return

    #     # Разбиваем на чанки до 1900 символов
    #     chunks = []
    #     current_chunk = ""
    #     for text in messages:
    #         if len(current_chunk) + len(text) > 1900:
    #             chunks.append(current_chunk)
    #             current_chunk = ""
    #         current_chunk += text + "\n"
    #     if current_chunk:
    #         chunks.append(current_chunk)

    #     for chunk in chunks:
    #         await ctx.send(chunk)

    #     await ctx.send(status_message)
    #     await ctx.send(f"📊 Всего банов найдено: **{total_bans}**")
    #     if permanent_bans_count > 0:
    #         await ctx.send(f"🔒 Из них перманентных: **{permanent_bans_count}**")
    #     await ctx.send(f"{ctx.author.mention} поиск банов по нику: `{username}` завершён!")

    # except Exception as e:
    #     await ctx.send(f"⚠ Произошла ошибка: {str(e)}")

@bot.command(name="find_bans_debug")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def find_bans_debug(ctx, username: str):
    """Отправляет результаты поиска банов в виде TXT файла для отладки"""
    await ctx.send(f"🔍 Ищу баны по нику `{username}` (режим отладки)...")

    try:
        search_results = await search_bans_in_multiple_channels(username)
        
        if not search_results:
            await ctx.send("⚠ Произошла ошибка при поиске.")
            return

        *messages, status_message = search_results
        
        # Создаем структурированный TXT файл
        debug_content = f"=== ОТЛАДОЧНАЯ ИНФОРМАЦИЯ О БАНАХ ===\n"
        debug_content += f"Запрос от: {ctx.author.display_name} ({ctx.author.id})\n"
        debug_content += f"Дата запроса: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        debug_content += f"Искомый ник: {username}\n\n"
        
        debug_content += "=== СТАТУС ===\n"
        debug_content += f"{status_message}\n\n"
        
        debug_content += "=== ПОЛНЫЕ ДАННЫЕ ===\n"
        for i, message in enumerate(messages, 1):
            debug_content += f"\n--- Блок данных {i} ---\n"
            debug_content += message + "\n"
        
        debug_content += "\n=== СЫРЫЕ ДАННЫЕ ===\n"
        debug_content += f"Тип объекта: {type(search_results)}\n"
        debug_content += f"Количество элементов: {len(search_results)}\n"
        debug_content += f"Типы элементов: {', '.join(str(type(x)) for x in search_results)}\n"
        
        # Создаем временный файл
        with io.StringIO() as file_stream:
            file_stream.write(debug_content)
            file_stream.seek(0)
            txt_file = disnake.File(file_stream, filename=f"bans_debug_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            await ctx.send(file=txt_file)
            await ctx.send("✅ Файл с отладочной информацией сгенерирован")

    except Exception as e:
        error_msg = f"⚠ Произошла ошибка: {str(e)}\n\nТрейсбек:\n{traceback.format_exc()}"
        # Отправляем ошибку тоже в файле если она слишком большая
        if len(error_msg) > 1500:
            with io.StringIO() as file_stream:
                file_stream.write(error_msg)
                file_stream.seek(0)
                error_file = disnake.File(file_stream, filename=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                await ctx.send(file=error_file)
        else:
            await ctx.send(error_msg)
