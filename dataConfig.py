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
GITHUB_USER_KEY = get_env("GITHUB_USER_KEY")