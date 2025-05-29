"""
Модуль для запуска бота.
"""

# pylint: skip-file
import asyncio
import logging
import sys
import importlib
import pkgutil
from pathlib import Path
from bot_init import bot
from config import DISCORD_KEY

# Настройка логирования
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot_logs.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

def dynamic_import(package_path: str):
    """Динамически импортирует все модули в указанном пакете"""
    try:
        package = importlib.import_module(package_path)
        
        # Пропускаем модули без файловой привязки
        if not hasattr(package, '__file__') or package.__file__ is None:
            logging.info(f"Skipping namespace package: {package_path}")
            return
            
        package_dir = Path(package.__file__).parent
        
        for (_, module_name, _) in pkgutil.iter_modules([str(package_dir)]):
            full_module_path = f"{package_path}.{module_name}"
            try:
                importlib.import_module(full_module_path)
                logging.info(f"Successfully imported {full_module_path}")
            except Exception as e:
                logging.error(f"Failed to import {full_module_path}: {e}")
    except ImportError as e:
        logging.error(f"Failed to import package {package_path}: {e}")

def load_all_imports():
    """Загружает все команды из поддиректорий commands"""
    base_packages = [
        'commands',
        'commands.adt_team',
        'commands.db_ss',
        'commands.db_ss.discord', 
        'commands.github',
        'commands.post_admin',
        'events'
    ]
    
    for package in base_packages:
        dynamic_import(package)

if __name__ == "__main__":
    # Загружаем все импорты динамически
    load_all_imports()
    
    # Проверка workflows
    try:
        check_workflows = importlib.import_module("commands.github.check_workflows")
        asyncio.run(check_workflows.check_workflows())
    except Exception as e:
        logging.error(f"Failed to run workflow check: {e}")
        sys.exit(1)
    
    if DISCORD_KEY == "NULL":
        logging.error("Not DISCORD_KEY. Programm Dev-bot shutdown!!")
        sys.exit(1)
    else:
        bot.run(DISCORD_KEY)
