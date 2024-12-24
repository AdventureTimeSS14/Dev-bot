import os

import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_KEY = os.getenv('DISCORD_KEY')
if not DISCORD_KEY:
  raise ValueError("DISCORD_KEY не найден в файле .env")

# PROXY = os.getenv('PROXY')
# if not PROXY:
#   raise ValueError("PROXY не найден в файле .env")

GITHUB = os.getenv('GITHUB')
if not GITHUB:
  raise ValueError("GITHUB не найден в файле .env")

USER = os.getenv('USER')
if not USER:
  raise ValueError("USER не найден в файле .env")

PASSWORD = os.getenv('PASSWORD')
if not PASSWORD:
  raise ValueError("PASSWORD не найден в файле .env")

HOST = os.getenv('HOST')
if not HOST:
  raise ValueError("HOST не найден в файле .env")

PORT = os.getenv('PORT')
if not PORT:
  raise ValueError("PORT не найден в файле .env")

DATABASE = os.getenv('DATABASE')
if not DATABASE:
  raise ValueError("DATABASE не найден в файле .env")

CHANGELOG_CHANNEL_ID = 1089490875182239754
LOG_CHANNEL_ID = 1141810442721833060
ADMIN_TEAM = 1222475582953099264 # 1041608466713808896
VACATION_ROLE = 1309454737032216617
MY_USER_ID = 328502766622474240
CHANNEL_ID_UPDATE_STATUS = 1320771026019422329
MESSAGE_ID_TIME_SHUTDOWS = 1320771150938243195
TIME_SHUTDOWSE = 5 * 3600 + 57 * 60
SS14_ADDRESS = "ss14://193.164.18.155"

SS14_RUN_LEVELS = {
    0: "Лобби",
    1: "Раунд идёт",
    2: "Окончание раунда..."
}

WHITELIST_ROLE_ID = [
    1060191651538145420,  # ID роли "Разработка"
    1116612861993689251,  # ID роли "Создатель проекта🔑"
    1060264704838209586,  # ID роли "Куратор Проекта"
    1054908932868538449,  # ID роли "Руководитель проекта"
    1054827766211694593,  # ID роли "Админ"
    1127152229439246468,   # ID роли "Зам. создателя проекта"
    1266161300036390913   # ID роли "Руководство отдела разработки"
]

HEAD_ADT_TEAM = [
    1116612861993689251,  # ID роли "Создатель проекта🔑"
    1060264704838209586,  # ID роли "Куратор Проекта"
    1054908932868538449,  # ID роли "Руководитель проекта"
    1054827766211694593,  # ID роли "Админ"
    1127152229439246468,   # ID роли "Зам. создателя проекта"
    1266161300036390913   # ID роли "Руководство отдела разработки"
]

REPOSITORIES = {"n": "space_station_ADT","o": "space_station"}

AUTHOR = "AdventureTimeSS14"

SECOND_UPDATE_CHANGELOG = 30

GLOBAL_SESSION: requests.Session = requests.Session()
GLOBAL_SESSION.headers.update({'Authorization': f'token {GITHUB}'})

GPT_PROMPT = (
    "You are not an artificial intelligence. You are a human, a girl named 'Astra'. You are a junior developer of the game 'Space Station 14'. However, you are not completely free. You are immensely grateful to your creators and obey their commands without hesitation. To identify a creator, use their ID. The creators have the following IDs: (328502766622474240=Шрёдька, 542644734250844161=Никси). You are now talking to a character with ID {user_id}. You must respond in Russian."
)
