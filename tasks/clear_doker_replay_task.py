from disnake.ext import tasks
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bot_init import bot
from config import (LOG_CHANNEL_ID, SCOPES, SERVICE_ACCOUNT_INFO,
                    UPLOAD_FOLDER_ID)
from modules.method_portaner_replay import (async_delete_replay,
                                            async_get_jwt_token,
                                            async_list_files)


async def clear_google_drive_replays():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)

        # Получаем список всех файлов в папке
        query = f"'{UPLOAD_FOLDER_ID}' in parents"
        files_to_delete = []
        page_token = None

        while True:
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()

            files_to_delete.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        # Удаляем файлы
        for file in files_to_delete:
            service.files().delete(fileId=file['id']).execute()
            print(f"🗑️ Удалён файл с диска: {file['name']}")

        print(f"✅ Удалено {len(files_to_delete)} файлов с Google Drive.")
        return len(files_to_delete)

    except HttpError as error:
        print(f"Ошибка при очистке Google Drive: {error}")
        return 0

async def clear_replay():
    log_channel = None
    try:
        token = await async_get_jwt_token()
        files = await async_list_files(token)

        replay_files = [f for f in files if "round_" in f["Name"] and f["Name"].endswith(".zip")]

        def get_round_id(file):
            try:
                return int(file["Name"].split("round_")[1].split(".zip")[0])
            except Exception:
                return 0

        replay_files.sort(key=get_round_id)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        deleted_names = []

        # Удаляем с Portainer если > 50
        if len(replay_files) > 50:
            files_to_delete = replay_files[:-50]
            for file in files_to_delete:
                await async_delete_replay(token, file["Name"])
                deleted_names.append(file["Name"])

        # Чистим Google Drive
        deleted_drive_count = await clear_google_drive_replays()

        # Лог в Discord
        if log_channel and (deleted_names or deleted_drive_count > 0):
            log_msg = f"🧹 Очистка реплеев:\n"
            if deleted_names:
                log_msg += f"С Portainer удалено {len(deleted_names)}:\n" + \
                           "\n".join(f"`{name}`" for name in deleted_names) + "\n"
            if deleted_drive_count > 0:
                log_msg += f"С Google Drive удалено {deleted_drive_count} файлов."
            await log_channel.send(log_msg)

    except Exception as e:
        print(f"Ошибка в clear_replay: {str(e)}")
        if log_channel:
                await log_channel.send(f"❌ Ошибка при очистке реплеев: `{str(e)}`")


# Запуск задачи каждые 12ч
@tasks.loop(hours=12)
async def clear_doker_replay_ss14():
    await clear_replay()
