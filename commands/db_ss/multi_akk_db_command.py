# import pytz
from datetime import datetime, timezone

import disnake
import psycopg2
from dateutil import parser

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS, DB_PARAMS_SPONSOR
from commands.misc.check_roles import has_any_role_by_keys
from modules.get_creation_date import get_creation_date

# import requests
# from bs4 import BeautifulSoup


# SPONSOR_PATH = '/root/node_sponsors/data/' # моя спонсорка, не учитывать.

# поиск секций в базе данных
def fetch_player_data(user_name):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT player_id, user_id, first_seen_time, last_seen_user_name, last_seen_time, last_seen_address, last_seen_hwid
    FROM player
    WHERE last_seen_user_name = %s
    """
    cursor.execute(query, (user_name,))
    result = cursor.fetchone()

    if result:
        player_id, uuid, first_seen_time, last_seen_user_name, last_seen_time, last_seen_address, last_seen_hwid = result

        query_related = """
        SELECT last_seen_user_name, last_seen_address, last_seen_hwid, last_seen_time
        FROM player
        WHERE last_seen_address = %s OR last_seen_hwid = %s
        """
        cursor.execute(query_related, (last_seen_address, last_seen_hwid))
        related_results = cursor.fetchall()
    else:
        related_results = []

    cursor.close()
    conn.close()

    return result, related_results

def fetch_sponsor_data(user_name):
    """
    Получает данные спонсора по никнейму из таблицы sponsors.
    """
    conn = psycopg2.connect(**DB_PARAMS_SPONSOR)
    cursor = conn.cursor()

    # Запрос для получения данных спонсора
    query = """
    SELECT user_id, player_name, tier, ooccolor, have_priority_join, allowed_markings, extra_slots, expire_date, allow_job
    FROM sponsors
    WHERE player_name = %s
    """
    cursor.execute(query, (user_name,))
    result = cursor.fetchone()  # Получаем первую запись (если есть)

    cursor.close()
    conn.close()

    return result

# нужно для конвертации времени с базы данных
def datetime_to_unix_timestamp(dt):
    if isinstance(dt, datetime):
        return int(dt.timestamp())
    elif isinstance(dt, str):
        try:
            parsed_dt = parser.isoparse(dt)
            return int(parsed_dt.timestamp())
        except Exception as e:
            print(f"Ошибка преобразования строки в метку времени: {e}")
    return None

# Показыват, есть-ли игрок в вайт-листе.
def get_whitelist_roles(uuid):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    query_whitelist = """
    SELECT * FROM whitelist
    WHERE user_id = %s
    """
    cursor.execute(query_whitelist, (uuid,))
    global_whitelist = cursor.fetchone()
    
    query_roles = """
    SELECT role_id FROM role_whitelists
    WHERE player_user_id = %s
    """
    cursor.execute(query_roles, (uuid,))
    role_ids = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not global_whitelist:
        global_status = None
    else:
        global_status = 'Глобально'

# Локализация ролей вайт-листа, пишется id роли, после : его русская версия.
    roles = {
        'Fugitive': 'Беглец',
        'BKCCOperator': 'Оператор ЦК',
        'BKCCOfficial': 'Представитель ЦК',
        'BKCCAdmiral': 'НШЦК',
        'BKCCSecGavna': 'Начальник безопасности ЦК',
        'BKBPLAMED': 'Блюспейс дрон меда',
        'Prisoner': 'Заключенный',
        'BKCCCargo': 'Грузчик ЦК',
        'BKCCSecOfficer': 'Приватный офицер СБ ЦК',
        'BKCCAssistant': 'Ассистент ЦК',
        'BKBPLATech': 'Блюспейс дрон',
        'BKCCCargo': 'Грузчик ЦК',
        'BKCCAssistant': 'Ассистент ЦК',
        'BlueShield': 'Офицер Синего Щита',
        'MobHumanCentComCorvax': 'Представитель ЦК Corvax',
        'MobHumanCentComOperatorCorvax': 'Оператор ЦК Corvax',
        'MobHumanSFOfficer': 'Офицер Cпециальных Операций Corvax',
        'MobHumanCentComOfficerSesurityGavna': 'Начальник Безопасности ЦК Corvax',
    }
    
    role_names = [roles.get(role_id[0], role_id[0]) for role_id in role_ids]
    return global_status, role_names

# продолжение конвертации времени
def format_datetime(dt, format_type='full'):
    if isinstance(dt, datetime):
        if format_type == 'short':
            return dt.strftime('%Y.%m.%d | %H:%M')
        elif format_type == 'minutes':
            return dt
        else:
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dt, str):
        try:
            parsed_dt = parser.isoparse(dt)
            if format_type == 'short':
                return parsed_dt.strftime('%Y.%m.%d | %H:%M')
            elif format_type == 'minutes':
                return parsed_dt
            else:
                return parsed_dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Ошибка преобразования строки в datetime: {e}")
    return 'Неизвестно'

# это для красивой таблицы где показывает ВЛ роли. Можно просто убрать. Но роли показыать не будет.
def format_roles_table(roles_list):
    sorted_roles = sorted(roles_list, key=len, reverse=True)
    
    split_index = (len(sorted_roles) + 1) // 2
    
    first_column = sorted_roles[:split_index]
    second_column = sorted_roles[split_index:]
    
    max_length = max(len(role) for role in sorted_roles) + 2
    formatted_rows = []
    
    for role1, role2 in zip(first_column, second_column):
        formatted_rows.append(f'{role1.ljust(max_length)} | {role2}')
    
    if len(first_column) > len(second_column):
        for role in first_column[len(second_column):]:
            formatted_rows.append(f'{role.ljust(max_length)} |')
    
    table_content = '\n'.join(formatted_rows)
    
    border_length = max_length + len(' | ') + max_length - 4
    decoration = ' ⋆⋅☆⋅⋆ '
    border_with_deco_length = border_length - len(decoration)
    top_border = '┌' + '─' * (border_with_deco_length // 2) + decoration + '─' * (border_with_deco_length // 2) + '┐'
    bottom_border = '└' + '─' * (border_with_deco_length // 2) + decoration + '─' * (border_with_deco_length // 2) + '┘'
    
    result = f'{top_border}\n'
    for line in formatted_rows:
        result += f'│ {line.ljust(border_length - 2)} │\n'
    result += f'{bottom_border}'
    
    return result

# конвертация времени - когда последний раз заходил
def time_since(dt):
    now = datetime.now(timezone.utc)
    delta = now - dt
    minutes = int(delta.total_seconds() // 60)
    return f'{minutes} минут назад'

# конвертирует HWID, если нет нет - в значение ниже.
def format_hwid(hwid):
    if isinstance(hwid, memoryview):
        hwid = hwid.tobytes()
    elif not isinstance(hwid, (bytes, str)):
        return 'Его нету'
    
    if isinstance(hwid, bytes):
        return hwid.hex()
    elif isinstance(hwid, str) and hwid.strip() == '\\x':
        return 'Его нету'
    elif isinstance(hwid, str):
        return hwid
    return 'Его нету'

# # Функция для получения информации о местоположении IP-адреса
# def get_ip_info(ip_address):
#     url = f'https://awebanalysis.com/ru/ip-lookup/{ip_address}/'
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Проверка на HTTP ошибки
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Ищем данные в HTML
#         ip_info = {
#             'country': 'Не удалось получить информацию',
#             'region': '',
#             'city': ''
#         }
        
#         # Поиск элементов с нужной информацией
#         country_elem = soup.find('td', text='Страна')
#         if country_elem:
#             ip_info['country'] = country_elem.find_next_sibling('td').text.strip()
        
#         region_elem = soup.find('td', text='Государство / Регион')
#         if region_elem:
#             ip_info['region'] = region_elem.find_next_sibling('td').text.strip()
        
#         city_elem = soup.find('td', text='город')
#         if city_elem:
#             ip_info['city'] = city_elem.find_next_sibling('td').text.strip()
        
#         return f"{ip_info['country']}, {ip_info['region']}, {ip_info['city']}"
    
#     except requests.RequestException as e:
#         print(f"Ошибка запроса IP информации: {e}")
#         return 'Не удалось получить информацию'

def get_discord_info_by_user_id(user_id: str):
    """
    Получает информацию о привязанном Discord-аккаунте по user_id.

    :param user_id: ID игрока в базе.
    :return: Кортеж (discord_id, discord_name) если найден, иначе None.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT discord_id FROM discord_user WHERE user_id = %s", (user_id,))
    discord_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if discord_data:
        return discord_data[0]  # Возвращаем discord_id
    return None

@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post", "general_adminisration_role")
async def check_nick(ctx, *, user_name: str):
    data, related_accounts = fetch_player_data(user_name)
    data_sponsor = fetch_sponsor_data(user_name)  

    if data:
        player_id, uuid, first_seen_time_str, last_seen_user_name, last_seen_time_str, last_seen_address, last_seen_hwid = data

        try:
            first_seen_time = format_datetime(first_seen_time_str, 'short') if first_seen_time_str else 'Неизвестно'
            last_seen_time_dt = format_datetime(last_seen_time_str, 'minutes') if last_seen_time_str else None
            
            if last_seen_time_dt:
                last_seen_time_formatted = time_since(last_seen_time_dt)
            else:
                last_seen_time_formatted = 'Неизвестно'
        
        except Exception as e:
            print(f"Ошибка преобразования времени: {e}")
            first_seen_time = 'Неизвестно'
            last_seen_time_formatted = 'Неизвестно'
        
        hwid_message = format_hwid(last_seen_hwid) if last_seen_hwid else 'Неизвестно'
        
        # Получаем дату создания аккаунта
        creation_date = get_creation_date(uuid)
        
        # Проверяем привязку Discord-аккаунта
        discord_id = get_discord_info_by_user_id(uuid)

        if discord_id:
            discord_member = await ctx.guild.fetch_member(int(discord_id)) if ctx.guild else None
            discord_name = discord_member.name if discord_member else "Неизвестно"
            discord_message = f'> 🟢 **Привязан Discord:** <@{discord_id}> ({discord_name}, ID: {discord_id})\n'
        else:
            discord_message = '> 🔴 **Discord-аккаунт не привязан.**\n'

        global_whitelist_status, whitelist_roles = get_whitelist_roles(uuid)
        global_whitelist_message = f'> **Присутствует в белом списке:** {global_whitelist_status}\n' if global_whitelist_status else ''

        roles_message = (f'> **Имеет открытые роли Whitelist:**\n'
                         f'```\n'
                         f'{format_roles_table(whitelist_roles)}\n'
                         '```') if whitelist_roles else ''

        related_accounts_str = ''
        if related_accounts:
            related_accounts_str = '> **Совпадение по аккаунтам:**\n'
            count = 0  
            for acc in related_accounts:
                if count >= 30:
                    break  

                related_user_name, related_address, related_hwid, related_last_seen_time = acc
                if related_user_name == last_seen_user_name:
                    continue
                related_last_seen_time_str = format_datetime(related_last_seen_time, 'short')
                if related_address == last_seen_address and related_hwid != last_seen_hwid:
                    related_accounts_str += (f'> **{related_user_name}** [IP] | Последний заход в игру: {related_last_seen_time_str}\n')
                elif related_hwid == last_seen_hwid and related_address != last_seen_address:
                    related_accounts_str += (f'> **{related_user_name}** [HWID] | Последний заход в игру: {related_last_seen_time_str}\n')
                elif related_hwid == last_seen_hwid and related_address == last_seen_address:
                    related_accounts_str += (f'> **{related_user_name}** [IP, HWID] | Последний заход в игру: {related_last_seen_time_str}\n')
                count += 1  

        # Добавляем информацию о спонсоре, если она есть
        sponsor_message = ''
        if data_sponsor:
            user_id, player_name, tier, ooccolor, have_priority_join, allowed_markings, extra_slots, expire_date, allow_job = data_sponsor
            sponsor_message = (
                f'\n> **🎖️ Спонсор:** Да\n'
                f'> **Тиер:** {tier}\n'
                f'> **Цвет OOC:** {ooccolor}\n'
                f'> **Приоритетный вход:** {"Да" if have_priority_join else "Нет"}\n'
                f'> **Разрешённые маркинги:** {len(allowed_markings) if allowed_markings else "Нет"}\n'
                f'> **Extra slots:** {extra_slots}\n'
                f'> **Дата истечения:** {expire_date}\n'
                f'> **Игнор времени должностей:** {allow_job}\n\n'
            )
        else:
            sponsor_message = (
                f'\n> **🎖️ Спонсор:** Нет\n'
            )

        description = (f'> **Первый заход в игру:** {first_seen_time}\n'
                       f'> **Последний заход в игру:** {last_seen_time_formatted}\n'
                       f'> **Дата создания аккаунта:** {creation_date}\n\n'
                       f'> **HWID:** {hwid_message}\n'
                       f'> **UUID:** {uuid}\n\n'
                       f'{discord_message}'
                       f'{sponsor_message}'
                       f'{global_whitelist_message}'
                       f'{roles_message}\n'
                       f'{related_accounts_str}')

        embed = disnake.Embed(
            title=f'{last_seen_user_name} | ID игрока {player_id}',
            description=description,
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send('Игрок не найден.')


import os


@bot.command()
@has_any_role_by_keys("whitelist_role_id_administration_post")
async def check_nick_file(ctx, *, user_name: str):
    data, related_accounts = fetch_player_data(user_name)
    if data:
        player_id, uuid, first_seen_time_str, last_seen_user_name, last_seen_time_str, last_seen_address, last_seen_hwid = data

        related_accounts_str = ''
        if related_accounts:
            related_accounts_str = 'Совпадения по аккаунтам:\n'
            count = 0
            for acc in related_accounts:
                if count >= 10000:
                    break  # Ограничиваем вывод до 10000 совпадений
                
                related_user_name, related_address, related_hwid, related_last_seen_time = acc
                # Пропустить если совпадает с текущими данными
                if related_user_name == last_seen_user_name:
                    continue
                
                if related_address == last_seen_address and related_hwid != last_seen_hwid:
                    related_accounts_str += (f'> **{related_user_name}** [IP] | Последний заход в игру: {related_last_seen_time_str}\n')
                elif related_hwid == last_seen_hwid and related_address != last_seen_address:
                    related_accounts_str += (f'> **{related_user_name}** [HWID] | Последний заход в игру: {related_last_seen_time_str}\n')
                elif related_hwid == last_seen_hwid and related_address == last_seen_address:
                    related_accounts_str += (f'> **{related_user_name}** [IP, HWID] | Последний заход в игру: {related_last_seen_time_str}\n')
                count += 1

        # Создаем текстовый файл с данными
        file_name = f'related_accounts_{user_name}.txt'
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(related_accounts_str)

        # Отправляем файл в Discord
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                await ctx.send(file=disnake.File(file, file_name))
            os.remove(file_name)  # Удаляем файл после отправки

    else:
        await ctx.send('Игрок не найден.')
