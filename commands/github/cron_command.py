from datetime import datetime

import disnake
import pytz
from disnake.ext import commands

from bot_init import bot
from commands.misc.check_roles import has_any_role_by_keys
from config import AUTHOR, GITHUB
from Tools import get_http_session

OWNER = AUTHOR
REPO = 'Dev-bot'
API_URL = f'https://api.github.com/repos/{OWNER}/{REPO}'

def format_time_readable(iso_time_str):
    """Конвертирует ISO время в читаемый формат"""
    try:
        # Парсим ISO время
        dt = datetime.fromisoformat(iso_time_str.replace('Z', '+00:00'))
        
        # Конвертируем в московское время
        moscow_tz = pytz.timezone('Europe/Moscow')
        moscow_time = dt.astimezone(moscow_tz)
        
        # Форматируем в читаемый вид
        return moscow_time.strftime("%d.%m.%Y в %H:%M:%S (МСК)")
    except:
        return iso_time_str

# Заголовки для аутентификации
HEADERS = {
    "Authorization": f"token {GITHUB}",
    "Accept": "application/vnd.github.v3+json",
}

@bot.slash_command(
    name="cron",
    description="Управление cron через GitHub Variables"
)
async def cron_command(inter: disnake.ApplicationCommandInteraction):
    pass

@cron_command.sub_command(
    name="status",
    description="Показать текущий статус cron"
)
@has_any_role_by_keys("head_adt_team")
async def cron_status(inter: disnake.ApplicationCommandInteraction):
    """Показывает текущий статус cron через переменную CRON_ENABLED"""
    await inter.response.defer()
    
    try:
        session = await get_http_session()
        # Получаем переменную CRON_ENABLED
        url = f"{API_URL}/actions/variables"
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                await inter.followup.send(f"❌ Ошибка при получении переменных: {response.status}")
                return
            
            variables_data = await response.json()
            variables = variables_data.get('variables', [])
            
            cron_enabled = None
            for var in variables:
                if var.get('name') == 'CRON_ENABLED':
                    cron_enabled = var.get('value')
                    break
            
            if cron_enabled is None:
                status_msg = "⚠️ **Переменная CRON_ENABLED не установлена** - cron работает по умолчанию"
                status_emoji = "🟡"
            elif cron_enabled.lower() == 'true':
                status_msg = "✅ **Cron активен** - бот запускается автоматически каждые 10 минут"
                status_emoji = "🟢"
            elif cron_enabled.lower() == 'false':
                status_msg = "❌ **Cron отключен** - бот не запускается автоматически"
                status_emoji = "🔴"
            else:
                status_msg = f"⚠️ **Неизвестное значение** CRON_ENABLED: `{cron_enabled}`"
                status_emoji = "🟡"
            
            # Получаем информацию о последних запусках workflow
            runs_url = f"{API_URL}/actions/runs?workflow=run_on_github.yml&per_page=1"
            async with session.get(runs_url, headers=HEADERS) as runs_response:
                if runs_response.status == 200:
                    runs_data = await runs_response.json()
                    if runs_data.get('workflow_runs'):
                        last_run = runs_data['workflow_runs'][0]
                        last_run_time = last_run.get('created_at', 'Неизвестно')
                        last_run_status = last_run.get('status', 'Неизвестно')
                        
                        # Конвертируем время в читаемый формат
                        readable_time = format_time_readable(last_run_time) if last_run_time != 'Неизвестно' else 'Неизвестно'
                        
                        status_msg += f"\n\n📅 **Последний запуск:** {readable_time}"
                        status_msg += f"\n🔄 **Статус:** {last_run_status}"
            
            await inter.followup.send(f"{status_emoji} {status_msg}")
                    
    except Exception as e:
        await inter.followup.send(f"❌ Ошибка: {str(e)}")

@cron_command.sub_command(
    name="enable",
    description="Включить cron (установить CRON_ENABLED=true)"
)
@has_any_role_by_keys("head_adt_team")
async def cron_enable(inter: disnake.ApplicationCommandInteraction):
    """Включает cron через установку переменной CRON_ENABLED=true"""
    await inter.response.defer()
    
    try:
        session = await get_http_session()
        # Проверяем текущее значение
        url = f"{API_URL}/actions/variables"
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                await inter.followup.send(f"❌ Ошибка: {response.status}")
                return
            
            variables_data = await response.json()
            variables = variables_data.get('variables', [])
            
            cron_enabled = None
            for var in variables:
                if var.get('name') == 'CRON_ENABLED':
                    cron_enabled = var.get('value')
                    break
            
            if cron_enabled == 'true':
                await inter.followup.send("⚠️ Cron уже активен!")
                return
            
            # Устанавливаем переменную CRON_ENABLED=true
            if cron_enabled is None:
                # Создаем новую переменную
                create_data = {
                    "name": "CRON_ENABLED",
                    "value": "true"
                }
                async with session.post(url, json=create_data, headers=HEADERS) as create_response:
                    if create_response.status == 201:
                        await inter.followup.send("✅ **Cron включен!** Установлена переменная CRON_ENABLED=true")
                    else:
                        error_text = await create_response.text()
                        await inter.followup.send(f"❌ Ошибка при создании переменной: {create_response.status}\n{error_text}")
            else:
                # Обновляем существующую переменную - используем PATCH вместо PUT
                update_data = {
                    "name": "CRON_ENABLED",
                    "value": "true"
                }
                # Правильный URL для обновления переменной
                update_url = f"{API_URL}/actions/variables/CRON_ENABLED"
                async with session.patch(update_url, json=update_data, headers=HEADERS) as update_response:
                    if update_response.status == 204:
                        await inter.followup.send("✅ **Cron включен!** Обновлена переменная CRON_ENABLED=true")
                    else:
                        error_text = await update_response.text()
                        await inter.followup.send(f"❌ Ошибка при обновлении переменной: {update_response.status}\n{error_text}")
                        
    except Exception as e:
        await inter.followup.send(f"❌ Ошибка: {str(e)}")

@cron_command.sub_command(
    name="disable",
    description="Отключить cron (установить CRON_ENABLED=false)"
)
@has_any_role_by_keys("head_adt_team")
async def cron_disable(inter: disnake.ApplicationCommandInteraction):
    """Отключает cron через установку переменной CRON_ENABLED=false"""
    await inter.response.defer()
    
    try:
        session = await get_http_session()
        # Проверяем текущее значение
        url = f"{API_URL}/actions/variables"
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                await inter.followup.send(f"❌ Ошибка: {response.status}")
                return
            
            variables_data = await response.json()
            variables = variables_data.get('variables', [])
            
            cron_enabled = None
            for var in variables:
                if var.get('name') == 'CRON_ENABLED':
                    cron_enabled = var.get('value')
                    break
            
            if cron_enabled == 'false':
                await inter.followup.send("⚠️ Cron уже отключен!")
                return
            
            # Устанавливаем переменную CRON_ENABLED=false
            if cron_enabled is None:
                # Создаем новую переменную
                create_data = {
                    "name": "CRON_ENABLED",
                    "value": "false"
                }
                async with session.post(url, json=create_data, headers=HEADERS) as create_response:
                    if create_response.status == 201:
                        await inter.followup.send("✅ **Cron отключен!** Установлена переменная CRON_ENABLED=false")
                    else:
                        error_text = await create_response.text()
                        await inter.followup.send(f"❌ Ошибка при создании переменной: {create_response.status}\n{error_text}")
            else:
                # Обновляем существующую переменную - используем PATCH вместо PUT
                update_data = {
                    "name": "CRON_ENABLED",
                    "value": "false"
                }
                # Правильный URL для обновления переменной
                update_url = f"{API_URL}/actions/variables/CRON_ENABLED"
                async with session.patch(update_url, json=update_data, headers=HEADERS) as update_response:
                    if update_response.status == 204:
                        await inter.followup.send("✅ **Cron отключен!** Обновлена переменная CRON_ENABLED=false")
                    else:
                        error_text = await update_response.text()
                        await inter.followup.send(f"❌ Ошибка при обновлении переменной: {update_response.status}\n{error_text}")
                        
    except Exception as e:
        await inter.followup.send(f"❌ Ошибка: {str(e)}")

@cron_command.sub_command(
    name="runs",
    description="Показать последние запуски workflow"
)
@has_any_role_by_keys("head_adt_team")
async def cron_runs(inter: disnake.ApplicationCommandInteraction):
    """Показывает последние запуски workflow"""
    await inter.response.defer()
    
    try:
        session = await get_http_session()
        # Получаем последние запуски
        url = f"{API_URL}/actions/runs?workflow=run_on_github.yml&per_page=5"
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                await inter.followup.send(f"❌ Ошибка: {response.status}")
                return
            
            runs_data = await response.json()
            runs = runs_data.get('workflow_runs', [])
            
            if not runs:
                await inter.followup.send("❌ Запуски workflow не найдены")
                return
            
            # Формируем сообщение о запусках
            runs_message = "🔄 **Последние запуски workflow:**\n\n"
            
            for run in runs:
                run_id = run.get('id', 'Неизвестно')
                status = run.get('status', 'Неизвестно')
                conclusion = run.get('conclusion', 'Неизвестно')
                created_at = run.get('created_at', 'Неизвестно')
                
                # Эмодзи для статуса
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'queued': '⏳',
                    'waiting': '⏸️',
                    'cancelled': '❌',
                    'failure': '💥',
                    'timed_out': '⏰'
                }.get(status, '❓')
                
                # Конвертируем время в читаемый формат
                readable_time = format_time_readable(created_at) if created_at != 'Неизвестно' else 'Неизвестно'
                
                runs_message += f"{status_emoji} **Запуск #{run_id}**\n"
                runs_message += f"   Статус: `{status}`\n"
                runs_message += f"   Результат: `{conclusion}`\n"
                runs_message += f"   Время: `{readable_time}`\n\n"
            
            await inter.followup.send(runs_message)
                    
    except Exception as e:
        await inter.followup.send(f"❌ Ошибка: {str(e)}")
