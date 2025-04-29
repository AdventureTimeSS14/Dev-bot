import io
import os

import aiofiles
import aiohttp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import SCOPES, SERVICE_ACCOUNT_INFO, UPLOAD_FOLDER_ID
from modules.method_portaner_replay import (async_delete_replay,
                                            async_download_file,
                                            async_get_jwt_token,
                                            async_list_files)

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'temp'))
os.makedirs(SAVE_DIR, exist_ok=True)

def get_save_path(round_id):
    return os.path.join(SAVE_DIR, f"temp_replay_{round_id}.zip")

async def async_upload_to_drive(file_path, file_name):
    credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    async with aiofiles.open(file_path, 'rb') as f:
        data = await f.read()

    media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/zip', resumable=True)

    file_metadata = {'name': file_name, 'parents': [UPLOAD_FOLDER_ID]}
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    service.permissions().create(
        fileId=file['id'],
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()

    return f"https://drive.google.com/file/d/{file['id']}/view?usp=sharing"


@bot.command(name="replay")
@has_any_role_by_keys("whitelist_role_id_administration_post", "general_adminisration_role")
async def replay_command(ctx, round_id: int):
    try:
        token = await async_get_jwt_token()
        files = await async_list_files(token)
        matching_files = [f["Name"] for f in files if str(round_id) in f["Name"]]
        await ctx.send("🔁 Начата загрузка реплея..")
        if not matching_files:
            await ctx.send("❌ Реплей не найден.")
            return

        selected_file = matching_files[0]
        save_path = get_save_path(round_id)

        await async_download_file(token, selected_file, save_path)

        print("Начата отправка файла!")
        try:
            file_link = await async_upload_to_drive(save_path, selected_file)
        except Exception as e:
            await ctx.send(f"⚠️ Ошибка при загрузке на Google Drive: {str(e)}")
            return

        print("Удаляем файл!")
        try:
            os.remove(save_path)
            print(f"Файл {save_path} успешно удален")
        except FileNotFoundError:
            print(f"Файл {save_path} не найден для удаления")

        await ctx.send(f"📤 Файл реплея `{selected_file}` успешно загружен на Google Drive: {file_link}")

    except aiohttp.ClientError as e:
        await ctx.send(f"🔌 Ошибка подключения: {str(e)}")
    except Exception as e:
        await ctx.send(f"⚠️ Неизвестная ошибка: {str(e)}")

@bot.command(name="delete_replay")
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def delete_replay_command(ctx, round_id: int):
    try:
        token = await async_get_jwt_token()
        files = await async_list_files(token)

        matching_files = [f["Name"] for f in files if f"round_{round_id}" in f["Name"]]

        if not matching_files:
            await ctx.send(f"❌ Реплей с раундом {round_id} не найден.")
            return

        selected_file = matching_files[0]
        await async_delete_replay(token, selected_file)

        await ctx.send(f"🗑 Реплей `{selected_file}` успешно удалён.")
    except Exception as e:
        await ctx.send(f"⚠️ Ошибка при удалении реплея: {str(e)}")
