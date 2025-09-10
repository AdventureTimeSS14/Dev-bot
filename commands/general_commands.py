"""
Модуль предназначенный для общих комманд бота
"""
import datetime
import os
import platform
import sys

import disnake
from disnake.ext import commands

from bot_init import bot


@bot.command(name="ping", help="Проверяет задержку бота.")
async def ping(ctx):
    """
    Команда для проверки задержки бота.
    """
    latency = round(bot.latency * 1000)  # Вычисляем задержку в миллисекундах
    emoji = (
        "🏓" if latency < 100 else "🐢"
    )
    await ctx.send(f"{emoji} Pong! Задержка: **{latency}ms**")

@bot.command(name="git")
async def git_info(ctx):
    """
    Выводит информацию о репозиториях проекта.
    """
    # Создаем Embed
    embed = disnake.Embed(
        title="📚 Репозитории AdventureTimeSS14",
        description="Список основных репозиториев проекта:",
        color=disnake.Color.blue()
    )

    # Добавляем поля с информацией о репозиториях
    embed.add_field(
        name="🚀 Основной репозиторий (новая сборка)",
        value="[space_station_ADT](https://github.com/AdventureTimeSS14/space_station_ADT)",
        inline=False
    )
    embed.add_field(
        name="🛠️ Старый репозиторий (бывшая сборка)",
        value="[space_station](https://github.com/AdventureTimeSS14/space_station)",
        inline=False
    )
    embed.add_field(
        name="🤖 Репозиторий Discord-бота",
        value="[Dev-bot](https://github.com/AdventureTimeSS14/Dev-bot)",
        inline=False
    )

    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    # Отправляем Embed
    await ctx.send(embed=embed)

@bot.command(name="wiki")
async def wiki_info(ctx):
    """
    Выводит ссылки на основные разделы вики проекта.
    """
    # Создаем Embed с красивым оформлением
    embed = disnake.Embed(
        title="📖 Вики AdventureStation",
        description="Основные разделы вики. Выберите нужный:",
        color=disnake.Color.green()
    )

    sections = [
        ("🏠 Заглавная", "Заглавная_страница"),
        ("📋 Рабочие процедуры", "Стандартные_рабочие_процедуры"),
        ("⚖️ Корпоративный закон", "Корпоративный_закон"),
        ("👔 Командный состав", "Процедуры_командного_состава"),
        ("🛡️ Безопасность", "Процедуры_службы_безопасности"),
        ("⚖️ Юридический отдел", "Процедуры_юридического_отдела"),
        ("📟 Тен-коды", "Тен-коды"),
        ("🚫 Контрабанда", "Контрабанда"),
        ("📄 Бюрократия", "Бюрократическая_работа"),
        ("📊 Навыки", "Таблица_навыков")
    ]

    # Формируем список ссылок в одном поле для компактности
    wiki_url = "https://wiki.adventurestation.space/"
    embed.add_field(
        name="🔗 Ссылки на разделы",
        value="\n".join([f"[{name}]({wiki_url}{link})" for name, link in sections]),
        inline=False
    )

    embed.set_footer(text=f"Запрос от {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

def get_memory_info():
    """Получение информации о памяти"""
    try:
        if platform.system() == "Windows":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            
            memory_status = MEMORYSTATUSEX()
            memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
            
            return {
                'total': memory_status.ullTotalPhys,
                'free': memory_status.ullAvailPhys
            }
        else:
            with open('/proc/meminfo') as f:
                meminfo = f.read()
                total = int(meminfo.split('\n')[0].split()[1]) * 1024
                free = int(meminfo.split('\n')[2].split()[1]) * 1024
                return {'total': total, 'free': free}
    except Exception:
        return None

def get_disk_info():
    """Получение информации о диске"""
    try:
        if platform.system() == "Windows":
            import ctypes
            total_bytes = ctypes.c_ulonglong(0)
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p('C:\\'),
                None,
                ctypes.pointer(total_bytes),
                ctypes.pointer(free_bytes)
            )
            return {
                'total': total_bytes.value,
                'free': free_bytes.value
            }
        else:
            stat = os.statvfs('/')
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bfree * stat.f_frsize
            return {'total': total, 'free': free}
    except Exception:
        return None

def get_uptime():
    """Получение времени работы системы"""
    try:
        if platform.system() == "Windows":
            import ctypes
            tick_count = ctypes.windll.kernel32.GetTickCount64()
            return str(datetime.timedelta(milliseconds=tick_count)).split('.')[0]
        else:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return str(datetime.timedelta(seconds=uptime_seconds)).split('.')[0]
    except Exception:
        return None

@bot.command(name="systeminfo", help="Выводит информацию о системе бота")
async def system_info(ctx):
    """Команда для отображения системной информации (Windows/Linux)"""
    embed = disnake.Embed(
        title="📊 Системная информация",
        color=disnake.Color.blue()
    )
    
    # Информация о системе
    embed.add_field(
        name="🖥️ Система",
        value=f"**ОС (тип):** {platform.system()}\n"
              f"**Архитектура:** {platform.machine()}",
        inline=False
    )
    
    # Информация о процессоре
    embed.add_field(
        name="⚙️ Процессор",
        value=f"**Ядер:** {os.cpu_count()}",
        inline=False
    )
    
    # Информация о памяти
    mem_info = get_memory_info()
    if mem_info:
        used = mem_info['total'] - mem_info['free']
        percent = (used / mem_info['total']) * 100
        embed.add_field(
            name="💾 Память",
            value=f"**Всего:** {round(mem_info['total'] / (1024**3), 2)} GB\n"
                  f"**Использовано:** {round(used / (1024**3), 2)} GB\n"
                  f"**Свободно:** {round(mem_info['free'] / (1024**3), 2)} GB\n"
                  f"**Загрузка:** {round(percent, 2)}%",
            inline=False
        )
    else:
        embed.add_field(
            name="💾 Память",
            value="Не удалось получить данные",
            inline=False
        )
    
    # Информация о диске
    disk_info = get_disk_info()
    if disk_info:
        used = disk_info['total'] - disk_info['free']
        percent = (used / disk_info['total']) * 100
        embed.add_field(
            name="💽 Диск" + (" (C:\\)" if platform.system() == "Windows" else ""),
            value=f"**Всего:** {round(disk_info['total'] / (1024**3), 2)} GB\n"
                  f"**Использовано:** {round(used / (1024**3), 2)} GB\n"
                  f"**Свободно:** {round(disk_info['free'] / (1024**3), 2)} GB\n"
                  f"**Загрузка:** {round(percent, 2)}%",
            inline=False
        )
    else:
        embed.add_field(
            name="💽 Диск",
            value="Не удалось получить данные",
            inline=False
        )
    
    # Время работы системы
    uptime = get_uptime()
    if uptime:
        embed.add_field(
            name="⏱️ Время работы",
            value=f"**Аптайм:** {uptime}",
            inline=False
        )

    # Информация о Disnake
    embed.add_field(
        name="🤖 Disnake",
        value=f"**Версия:** {disnake.__version__}",
        inline=False
    )
    
    embed.set_footer(text=f"Запрос выполнен: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await ctx.send(embed=embed)
