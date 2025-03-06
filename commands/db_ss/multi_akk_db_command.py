# import pytz
import disnake
import psycopg2
import requests
from datetime import datetime, timezone
from dateutil import parser
from bot_init import bot
from config import (
    WHITELIST_ROLE_ID_ADMINISTRATION_POST
)
from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS
from commands.misc.check_roles import has_any_role_by_id

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

# используем апи визардов для отслеживание - когда была создана учётная запись
def get_creation_date(uuid):
    url = f"https://auth.spacestation14.com/api/query/userid?userid={uuid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()  # Парсинг JSON
        
        player_date = data.get('createdTime', 'Дата создания не найдена')
        date_obj = datetime.fromisoformat(player_date)
        creation_date_unix = int(date_obj.timestamp())  # Преобразование в Unix-время
        
        return f'<t:{creation_date_unix}:f>'  # Форматирование в метку времени Discord
    
    except requests.exceptions.HTTPError as err:
        return f"Ошибка при запросе API: {err}"
    except requests.exceptions.RequestException as err:
        return f"Ошибка соединения: {err}"
    except ValueError:
        return "Ошибка при разборе ответа API (неправильный формат JSON)"
    except Exception as err:
        return f"Произошла ошибка: {err}"

@bot.command()
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
async def check_nick(ctx, *, user_name: str):
    data, related_accounts = fetch_player_data(user_name)
    
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
        
        # # Получаем информацию о IP
        # ip_info = get_ip_info(last_seen_address)
        
        # Получаем дату создания аккаунта
        creation_date = get_creation_date(uuid)
        
        related_accounts_str = ''
        if related_accounts:
            related_accounts_str = '> **Совпадение по аккаунтам:**\n'
            count = 0  # Счётчик для ограничения до 30 совпадений
            for acc in related_accounts:
                if count >= 30:
                    break  # Прекратить цикл, если уже нашли 30 совпадений

                related_user_name, related_address, related_hwid, related_last_seen_time = acc
                # Пропустить если совпадает с текущими данными
                if related_user_name == last_seen_user_name:
                    continue
                related_last_seen_time_str = format_datetime(related_last_seen_time, 'short')
                if related_address == last_seen_address and related_hwid != last_seen_hwid:
                    related_accounts_str += (f'> **{related_user_name}** [IP] | Последний заход в игру: {related_last_seen_time_str}\n')
                elif related_hwid == last_seen_hwid and related_address != last_seen_address:
                    related_accounts_str += (f'> **{related_user_name}** [HWID] | Последний заход в игру: {related_last_seen_time_str}\n')
                elif related_hwid == last_seen_hwid and related_address == last_seen_address:
                    related_accounts_str += (f'> **{related_user_name}** [IP, HWID] | Последний заход в игру: {related_last_seen_time_str}\n')
                count += 1  # Увеличиваем счётчик

        # # Check for sponsor status
        # sponsor_status = get_sponsor_tier(uuid)
        global_whitelist_status, whitelist_roles = get_whitelist_roles(uuid)
        
        # sponsor_message = f'> **Спонсорская привилегия:** {sponsor_status}\n' if sponsor_status else ''
        global_whitelist_message = f'> **Присутствует в белом списке:** {global_whitelist_status}\n' if global_whitelist_status else ''
        
        # Форматирование ролей в таблицу с декоративной рамкой
        roles_message = (f'> **Имеет открытые роли Whitelist:**\n'
                         f'```\n'
                         f'{format_roles_table(whitelist_roles)}\n'
                         '```') if whitelist_roles else ''

        # занчение после "f'> **UUID:** {uuid}\n\n'" можно подчистить. Если они не требуются. Но related_accounts_str используется для поиска совпадений.
        description = (f'> **Первый заход в игру:** {first_seen_time}\n'
                       f'> **Последний заход в игру:** {last_seen_time_formatted}\n'
                       f'> **Дата создания аккаунта:** {creation_date}\n\n'
                    #    f'> **IP:** {last_seen_address}\n'
                    #    f'> **Информация:** {ip_info}\n'
                       f'> **HWID:** {hwid_message}\n'
                       f'> **UUID:** {uuid}\n\n'
                    #    f'{sponsor_message}'
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
@has_any_role_by_id(WHITELIST_ROLE_ID_ADMINISTRATION_POST)
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
