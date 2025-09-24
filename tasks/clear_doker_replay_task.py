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
from Tools import send_log


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
        if len(files_to_delete) > 0:
            await send_log(f"🧹 Google Drive: удалено {len(files_to_delete)} файлов.")
        return len(files_to_delete)

    except HttpError as error:
        msg = f"❌ Ошибка при очистке Google Drive: {error}"
        print(msg)
        await send_log(msg)
        return 0

async def clear_replay():
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    try:
        await send_log("▶️ Старт очистки реплеев (Portainer + Google Drive)...")
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
            failures = []
            for file in files_to_delete:
                try:
                    await async_delete_replay(token, file["Name"])
                    deleted_names.append(file["Name"])
                except Exception as e:
                    failures.append((file["Name"], str(e)))
            if failures:
                fail_text = "\n".join(f"`{n}`: {err}" for n, err in failures[:20])
                await send_log(f"⚠️ Ошибки удаления {len(failures)} реплеев в Portainer (первые 20):\n{fail_text}")

        # Чистим Google Drive
        deleted_drive_count = await clear_google_drive_replays()

        # Лог в Discord
        if deleted_names or deleted_drive_count > 0:
            log_msg = f"🧹 Очистка реплеев:\n"
            if deleted_names:
                log_msg += f"С Portainer удалено {len(deleted_names)}:\n" + \
                           "\n".join(f"`{name}`" for name in deleted_names[:50]) + ("\n..." if len(deleted_names) > 50 else "\n")
            if deleted_drive_count > 0:
                log_msg += f"С Google Drive удалено {deleted_drive_count} файлов."
            await send_log(log_msg)
        else:
            await send_log("ℹ️ Очистка реплеев: ничего не удалено (порог 50 не превышен).")

    except Exception as e:
        msg = f"❌ Ошибка в clear_replay: {str(e)}"
        print(msg)
        await send_log(msg)


# Запуск задачи каждые 12ч
@tasks.loop(hours=12)
async def clear_doker_replay_ss14():
    await clear_replay()
