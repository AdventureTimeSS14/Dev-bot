import os
from dotenv import load_dotenv

load_dotenv()

# Функция для получения значения скрытого ключа
def get_env(key: str):
    env = os.getenv(f"{key}")

    if not env:
        print("Ключ секрета не найден")

    return env

DISCORD_KEY = get_env("DISCORD_KEY")
USER_KEY_GITHUB = get_env("USER_KEY_GITHUB")