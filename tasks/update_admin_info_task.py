from datetime import datetime

import disnake
from disnake.ext import tasks

from bot_init import bot
from commands.post_admin.admin_info_command import create_admin_info_embed
from config import MOSCOW_TIMEZONE
from Tools import send_log

# Константы для канала и сообщения
ADMIN_INFO_CHANNEL_ID = 1309169384413069372
ADMIN_INFO_MESSAGE_ID = 1416298908757262407


@tasks.loop(minutes=12)
async def update_admin_info_embed():
    """
    Задача для автоматического обновления эмбеда admin_info каждые 12 минут.
    Обновляет сообщение с ID 1416298908757262407 в канале 1309169384413069372.
    """
    try:
        print("▶️ Обновление admin_info эмбеда...")
        channel = bot.get_channel(ADMIN_INFO_CHANNEL_ID)
        if not channel:
            print(f"❌ Канал с ID {ADMIN_INFO_CHANNEL_ID} не найден")
            await send_log(f"❌ Канал с ID {ADMIN_INFO_CHANNEL_ID} не найден")
            return

        # Получаем эмбед с информацией о сервере
        success, embed = await create_admin_info_embed()
        
        # Добавляем timestamp к эмбеду
        embed.timestamp = datetime.now(MOSCOW_TIMEZONE)
        embed.set_footer(
            text="Автоматическое обновление каждые 12 минут | Последнее обновление",
            icon_url="https://media.discordapp.net/attachments/1255118642442403986/1351231449470079046/icon-256x256.png"
        )

        try:
            # Пытаемся обновить существующее сообщение
            message = await channel.fetch_message(ADMIN_INFO_MESSAGE_ID)
            await message.edit(embed=embed)
            print(f"✅ Эмбед admin_info успешно обновлен (ID: {ADMIN_INFO_MESSAGE_ID})")
            print("✅ Эмбед admin_info обновлён.")
            
        except disnake.NotFound:
            print(f"❌ Сообщение с ID {ADMIN_INFO_MESSAGE_ID} не найдено. Создаем новое...")
            await send_log(f"⚠️ Сообщение admin_info {ADMIN_INFO_MESSAGE_ID} не найдено. Создаём новое...")
            
            # Если сообщение не найдено, создаем новое
            new_message = await channel.send(embed=embed)
            print(f"✅ Создано новое сообщение с эмбедом admin_info (ID: {new_message.id})")
            print(f"⚠️ Обновите ADMIN_INFO_MESSAGE_ID в файле на новый ID: {new_message.id}")
            await send_log(f"✅ Создано новое сообщение admin_info (ID: {new_message.id}). Обновите конфиг.")
            
        except disnake.Forbidden:
            print(f"❌ Нет прав для редактирования сообщения с ID {ADMIN_INFO_MESSAGE_ID}")
            await send_log(f"❌ Нет прав для редактирования admin_info {ADMIN_INFO_MESSAGE_ID}")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении сообщения admin_info: {e}")
            await send_log(f"❌ Ошибка при обновлении admin_info: {e}")

    except Exception as e:
        print(f"❌ Ошибка в задаче update_admin_info_embed: {e}")
        await send_log(f"❌ Ошибка в задаче update_admin_info_embed: {e}")


# Функция для ручного запуска обновления (можно использовать для тестирования)
async def manual_update_admin_info():
    """
    Ручное обновление эмбеда admin_info.
    Можно использовать для тестирования или принудительного обновления.
    """
    await update_admin_info_embed()
