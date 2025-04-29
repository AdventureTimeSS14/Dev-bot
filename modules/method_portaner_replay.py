import aiofiles
import aiohttp

from config import PORTAINER_PASSWORD, PORTAINER_USERNAME

# Конфигурация
AUTH_URL = "http://control.adventurestation.space:9000/api/auth"
LIST_URL = "http://control.adventurestation.space:9000/api/endpoints/4/docker/v2/browse/ls"
DOWNLOAD_URL = "http://control.adventurestation.space:9000/api/endpoints/4/docker/v2/browse/get"


async def async_get_jwt_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_URL, json={"username": PORTAINER_USERNAME, "password": PORTAINER_PASSWORD}) as response:
            response.raise_for_status()
            data = await response.json()
            return data["jwt"]

async def async_list_files(token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"path": "/", "volumeID": "SS14_REPLAY"}
    async with aiohttp.ClientSession() as session:
        async with session.get(LIST_URL, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

async def async_delete_replay(token, file_name):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"path": file_name, "volumeID": "SS14_REPLAY"}
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            "http://control.adventurestation.space:9000/api/endpoints/4/docker/v2/browse/delete",
            headers=headers,
            params=params
        ) as response:
            if response.status == 204:
                print(f"✅ Реплей {file_name} удален")
            else:
                print(f"⚠️ Ошибка при удалении {file_name}: {response.status}")

async def async_get_jwt_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_URL, json={"username": PORTAINER_USERNAME, "password": PORTAINER_PASSWORD}) as response:
            response.raise_for_status()
            data = await response.json()
            return data["jwt"]

async def async_list_files(token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"path": "/", "volumeID": "SS14_REPLAY"}
    async with aiohttp.ClientSession() as session:
        async with session.get(LIST_URL, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

async def async_download_file(token, file_name, save_path):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"path": file_name, "volumeID": "SS14_REPLAY"}
    async with aiohttp.ClientSession() as session:
        async with session.get(DOWNLOAD_URL, headers=headers, params=params) as response:
            response.raise_for_status()
            async with aiofiles.open(save_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
    print(f"Файл сохранён: {save_path}")
