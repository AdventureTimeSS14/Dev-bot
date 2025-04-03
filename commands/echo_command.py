"""
Этот модуль содержит команду 'echo', которая повторяет переданное сообщение,
если пользователь является владельцем бота.
"""

import disnake
from disnake import Embed

from bot_init import bot
from config import MY_USER_ID


@bot.command(
    name="echo",
    help="Повторяет переданное сообщение. Доступна только для владельца бота.",
)
async def echo(ctx, *, message: str):
    """
    Команда для повторения сообщения.
    Доступ к команде ограничен пользователем с ID из MY_USER_ID.
    """
    # Проверка прав доступа
    if ctx.author.id != MY_USER_ID:
        await ctx.reply(
            "❌ У вас нет доступа к этой команде.", mention_author=False
        )
        return

    try:
        # Удаление исходного сообщения
        await ctx.message.delete()

        # Отправка повторённого сообщения
        await ctx.send(message)

    except disnake.Forbidden:
        # Если бот не имеет прав на удаление сообщений
        await ctx.reply(
            "⚠️ У меня нет прав для удаления сообщений.", mention_author=False
        )
    except disnake.DiscordException as e:
        # Логирование других ошибок, связанных с Discord
        print(f"❌ Произошла ошибка в команде 'echo': {e}")
        await ctx.reply(
            "❌ Произошла ошибка при выполнении команды. Проверьте логи.",
            mention_author=False,
        )


@bot.command(
    name="embed",
    help="Создаёт тестовый эмбед. Доступна только для владельца бота.",
)
async def embed(ctx, text: str):
    """
    Команда для создания тестового эмбеда.
    Доступ к команде ограничен пользователем с ID из MY_USER_ID.
    """
    # Проверка прав доступа
    if ctx.author.id != MY_USER_ID:
        await ctx.reply(
            "❌ У вас нет доступа к этой команде.", 
            mention_author=False
        )
        return

    try:
        # Удаление исходного сообщения
        await ctx.message.delete()

        # Создание тестового эмбеда
        embed = Embed(
            title=f"📌 {text}",
            description="Это пример эмбеда, созданного ботом",
            color=disnake.Color.blue()
        )
        
        # Добавляем поля
        embed.add_field(name="Поле 1", value="Значение 1", inline=True)
        embed.add_field(name="Поле 2", value="Значение 2", inline=True)
        embed.add_field(name="Поле 3", value="Значение 3", inline=False)
        
        # Добавляем футер
        embed.set_footer(text="Тестовый футер")
        
        # Отправка эмбеда
        await ctx.send(embed=embed)

    except disnake.Forbidden:
        await ctx.reply(
            "⚠️ У меня нет прав для удаления сообщений.", 
            mention_author=False
        )
    except disnake.DiscordException as e:
        print(f"❌ Произошла ошибка в команде 'embed': {e}")
        await ctx.reply(
            "❌ Произошла ошибка при создании эмбеда. Проверьте логи.",
            mention_author=False,
        )
