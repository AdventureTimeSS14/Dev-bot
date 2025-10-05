import os
from dotenv import load_dotenv

load_dotenv()

ROLE_ACCESS_HEADS = [
    1054908932868538449, # Руководство проекта
    1266161300036390913, # Руководство отдела разработки
    1054827766211694593 # Админ
]

# Функция для получения значения скрытого ключа
def get_env(key: str):
    env = os.getenv(f"{key}")

    if not env:
        print("Ключ секрета не найден")

    return env

DISCORD_KEY = get_env("DISCORD_KEY")
USER_KEY_GITHUB = get_env("USER_KEY_GITHUB")