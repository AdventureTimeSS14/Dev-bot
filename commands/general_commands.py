"""
Модуль предназначенный для общих комманд бота
"""
import datetime
import os
import platform
import sys
import subprocess
import shutil

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
    """Команда для отображения системной информации в стиле neofetch"""
    hostname = platform.node() or "host"
    username = os.getenv("USERNAME") or os.getenv("USER") or "bot"

    os_line = f"{platform.system()} {platform.release()} {platform.machine()}"
    host_line = platform.platform()
    kernel_line = platform.release()
    uptime_line = get_uptime() or "N/A"

    cpu_model = platform.processor() or "CPU"
    cpu_cores = os.cpu_count() or 1
    cpu_line = f"{cpu_model} ({cpu_cores})"

    mem_info = get_memory_info()
    if mem_info:
        used_b = mem_info['total'] - mem_info['free']
        total_mib = int(round(mem_info['total'] / (1024**2)))
        used_mib = int(round(used_b / (1024**2)))
        mem_line = f"{used_mib}MiB / {total_mib}MiB"
    else:
        mem_line = "N/A"

    # Не всегда есть корректные данные по пакетам/терминалу/GPU в окружении бота
    def run_and_get_lines(cmd_list):
        try:
            completed = subprocess.run(cmd_list, capture_output=True, text=True, timeout=3)
            if completed.returncode == 0 and completed.stdout:
                return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        except Exception:
            return None
        return None

    def detect_packages_count():
        system = platform.system()
        # Linux package managers
        if system == "Linux":
            # dpkg
            if shutil.which("dpkg"):  # count installed packages
                lines = run_and_get_lines(["dpkg", "-l"]) or []
                # filter out header lines starting with '||/' or 'Desired='
                count = sum(1 for ln in lines if ln and not ln.startswith("Desired=") and not ln.startswith("||/"))
                if count:
                    return str(count)
            # rpm
            if shutil.which("rpm"):
                lines = run_and_get_lines(["rpm", "-qa"]) or []
                if lines:
                    return str(len(lines))
            # pacman
            if shutil.which("pacman"):
                lines = run_and_get_lines(["pacman", "-Q"]) or []
                if lines:
                    return str(len(lines))
            # apk
            if shutil.which("apk"):
                lines = run_and_get_lines(["apk", "info"]) or []
                if lines:
                    return str(len(lines))
        # macOS
        if system == "Darwin":
            if shutil.which("brew"):
                lines = run_and_get_lines(["brew", "list"]) or []
                if lines:
                    return str(len(lines))
            if shutil.which("port"):
                lines = run_and_get_lines(["port", "installed"]) or []
                # skip header lines like 'The following ports are currently installed:'
                filtered = [ln for ln in lines if ln and not ln.lower().startswith("the following")]
                if filtered:
                    return str(len(filtered))
        # Windows (best-effort)
        if system == "Windows":
            if shutil.which("winget"):
                lines = run_and_get_lines(["winget", "list"]) or []
                # skip header lines (first 2 usually)
                if len(lines) > 2:
                    return str(max(0, len(lines) - 2))
            if shutil.which("choco"):
                lines = run_and_get_lines(["choco", "list", "-l"]) or []
                # last line is a summary like 'X packages installed.'
                if lines:
                    try:
                        last = lines[-1]
                        num = int("".join(ch for ch in last if ch.isdigit()))
                        if num:
                            return str(num)
                    except Exception:
                        return str(len(lines))
            if shutil.which("scoop"):
                lines = run_and_get_lines(["scoop", "list"]) or []
                if lines:
                    # skip header if present
                    return str(len([ln for ln in lines if not ln.lower().startswith("installed apps")]))
        return "N/A"

    def detect_gpu():
        system = platform.system()
        if system == "Linux":
            if shutil.which("lspci"):
                lines = run_and_get_lines(["sh", "-c", "lspci | grep -i 'vga\|3d' -m 1"]) or []
                if lines:
                    return lines[0]
        if system == "Darwin":
            if shutil.which("system_profiler"):
                lines = run_and_get_lines(["system_profiler", "SPDisplaysDataType"]) or []
                for ln in lines:
                    if "Chipset Model" in ln or "Chipset" in ln or "Model" in ln:
                        parts = ln.split(":", 1)
                        return parts[1].strip() if len(parts) == 2 else ln.strip()
        if system == "Windows":
            # Try PowerShell CIM
            if shutil.which("powershell"):
                lines = run_and_get_lines(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController | Select-Object -First 1 -ExpandProperty Name)"]) or []
                if lines:
                    return lines[0]
        return "N/A"

    packages_line = detect_packages_count()
    shell_line = f"python {sys.version.split()[0]}"
    terminal_line = "discord"
    gpu_line = detect_gpu()

    ascii_art = [
        "            .-/+oossssoo+/-.",
        "        `:+ssssssssssssssssss+:`",
        "      -+ssssssssssssssssssyyssss+-",
        "    .ossssssssssssssssssdMMMNysssso.",
        "   /ssssssssssshdmmNNmmyNMMMMhssssss/",
        "  +ssssssssshmydMMMMMMMNddddyssssssss+",
        " /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/",
        ".ssssssssdMMMNhsssssssssshNMMMdssssssss.",
        "+sssshhhyNMMNyssssssssssssyNMMMysssssss+",
        "ossyNMMMNyMMhsssssssssssssshmmmhssssssso",
        "ossyNMMMNyMMhsssssssssssssshmmmhssssssso",
        "+sssshhhyNMMNyssssssssssssyNMMMysssssss+",
        ".ssssssssdMMMNhsssssssssshNMMMdssssssss.",
        " /sssssssshNMMMyhhyyyyhdNMMMNhssssssss/",
        "  +sssssssssdmydMMMMMMMMddddyssssssss+",
        "   /ssssssssssshdmNNNNmyNMMMMhssssss/",
        "    .ossssssssssssssssssdMMMNysssso.",
        "      -+sssssssssssssssssyyyssss+-",
        "        `:+ssssssssssssssssss+:`",
        "            .-/+oossssoo+/-.",
    ]

    info_lines = [
        f"{username}@{hostname}",
        "--------------------",
        f"OS: {os_line}",
        f"Host: {host_line}",
        f"Kernel: {kernel_line}",
        f"Uptime: {uptime_line}",
        f"Packages: {packages_line}",
        f"Shell: {shell_line}",
        f"Terminal: {terminal_line}",
        f"CPU: {cpu_line}",
        f"GPU: {gpu_line}",
        f"Memory: {mem_line}",
        f"Python: {sys.version.split()[0]}",
        f"Disnake: {disnake.__version__}",
    ]

    left_width = max(len(line) for line in ascii_art)
    gap = "   "
    combined_lines = []
    for i in range(max(len(ascii_art), len(info_lines))):
        left = ascii_art[i] if i < len(ascii_art) else ""
        right = info_lines[i] if i < len(info_lines) else ""
        combined_lines.append(left.ljust(left_width) + gap + right)

    output = "\n".join(combined_lines)
    await ctx.send(f"```\n{output}\n```")
