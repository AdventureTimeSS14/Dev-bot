import random
from datetime import datetime

import disnake
from disnake.ext import tasks

from bot_init import bot


class AnimatedStatus:
    def __init__(self):
        self.status_index = 0
        self.messages = [
            self.get_help_message,
            self.get_fun_fact,
            self.get_date_message,
            self.get_vpn_fact,
        ]
        
        self.fun_facts = [
            "Нажмите &help для списка команд",
            "SS14 - лучший космический симулятор!",
            "Новые фичи добавляются каждую неделю!",
            "Попробуйте сыграть за клоуна! 🤡"
        ]

        self.start_time = datetime.now()

    async def rotate_status(self):
        """Выбираем следующее сообщение для статуса"""
        message_func = self.messages[self.status_index]
        self.status_index = (self.status_index + 1) % len(self.messages)
        return await message_func()

    async def get_help_message(self):
        return {
            "type": disnake.ActivityType.playing,
            "name": "Напишите &help",
            "state": "Узнайте все команды бота"
        }

    async def get_fun_fact(self):
        return {
            "type": disnake.ActivityType.listening,
            "name": random.choice(self.fun_facts),
            "state": "Интересный факт!"
        }
    
    async def get_vpn_fact(self):
        return {
            "type": disnake.ActivityType.listening,
            "name": "Telegram `@HellflareVPN_Bot.` 🛡 HellflareVPN 🔥",
            "state": "Наш VPN - сервис обеспечивает конфиденциальность, надежное шифрование и безопасный интернет. Установить просто — пишите в Telegram @HellflareVPN_Bot."
        }

    async def get_date_message(self):
        today = datetime.now()
        day, month = today.day, today.month

        # Список праздников: (месяц, день) или ((месяц, день_from), (месяц, день_to))
        holidays = {
            # Фиксированные даты
            (1, 1): "🎉 С Новым Годом!",
            (1, 7): "🎄 Православное Рождество",
            (2, 14): "💝 День Святого Валентина",
            (2, 23): "⚔🛡 День защитника Отечества",
            (3, 8): "🌷 Международный женский день",
            (4, 1): "🎭 День смеха",
            (5, 1): "🌼 Праздник весны и труда",
            (5, 9): "🎖 День Победы",
            (6, 12): "🇷🇺 День России",
            (9, 1): "📚 День знаний",
            (10, 31): "🎃 Хэллоуин!",
            (11, 4): "🤝 День народного единства",
            (12, 31): "🍾 С Новым Годом (на подходе)!",

            # Промежутки дат (кортежи кортежей)
            ((8, 3), (8, 5)): "🤖🎉 День рождения Астры — Discord-бота!",
        }

        # Проверка фиксированной даты
        message = holidays.get((month, day))

        # Если не найдена, проверяем интервалы
        if not message:
            for key, value in holidays.items():
                if isinstance(key, tuple) and isinstance(key[0], tuple):
                    (from_month, from_day), (to_month, to_day) = key
                    if from_month == to_month == month and from_day <= day <= to_day:
                        message = value
                        break

        return {
            "type": disnake.ActivityType.watching,
            "name": message if message else today.strftime("%d.%m.%Y"),
            "state": message or "Хорошего дня!"
        }

status_manager = AnimatedStatus()

@tasks.loop(seconds=60)
async def update_presence():
    """Анимированный статус бота"""
    try:
        today = datetime.now()
        
        # Пасхалка на 1 апреля
        if today.month == 4 and today.day == 1:
            activity = disnake.Activity(
                type=disnake.ActivityType.playing,
                name="🎭 Секретный режим активен!",
                state="Ищем пасхалки... 🥚"
            )
        else:
            status = await status_manager.rotate_status()
            activity = disnake.Activity(
                type=status["type"],
                name=status["name"],
                state=status.get("state"),
                url=status.get("url")
            )
        
        await bot.change_presence(activity=activity)

    except Exception as e:
        print(f"Ошибка при обновлении статуса: {e}")
        await bot.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name="🚧 Технические работы..."
            )
        )
