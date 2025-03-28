import disnake
import psycopg2

from commands.db_ss.setup_db_ss14_mrp import DB_PARAMS


def fetch_player_data(user_name):
    """
        Функция поиска пользователя в БД
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    SELECT player_id, user_id, first_seen_time, last_seen_user_name
    FROM player
    WHERE last_seen_user_name = %s
    """
    cursor.execute(query, (user_name,))
    result = cursor.fetchone()

    # Если не нашли в player, ищем в connection_log
    if result is None:
        query = """
        SELECT connection_log_id, user_id, user_name
        FROM connection_log
        WHERE user_name = %s
        """
        cursor.execute(query, (user_name,))
        result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def is_user_linked(user_id, discord_id):
    """
    Проверяет, существует ли уже этот discord_id или user_id в базе.
    Если один из них уже есть — нельзя привязывать, возвращаем True.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # Проверяем, существует ли уже discord_id в базе
    cursor.execute("SELECT 1 FROM discord_user WHERE discord_id = %s", (str(discord_id),))
    result_discord_id = cursor.fetchone()

    # Проверяем, существует ли уже user_id в базе
    cursor.execute("SELECT 1 FROM discord_user WHERE user_id = %s", (user_id,))
    result_user_id = cursor.fetchone()

    cursor.close()
    conn.close()

    # Если нашли хотя бы один результат (discord_id или user_id), возвращаем True
    return bool(result_discord_id or result_user_id)

def link_user_to_discord(user_id, discord_id):
    """
        Функция записи данных в БД
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    query = """
    INSERT INTO discord_user (user_id, discord_id)
    VALUES (%s, %s)
    """
    cursor.execute(query, (user_id, discord_id))
    conn.commit()

    cursor.close()
    conn.close()

def unlink_user_to_discord(discord: disnake.Member):
    """
        Функция отвязки из БД
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM discord_user WHERE discord_id = %s RETURNING user_id", (str(discord.id),))
    result = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    return result

# Функция для получения user_id по discord_id
def get_user_id_by_discord_id(discord_id: str):
    """
    Ищет user_id по discord_id в таблице discord_user.

    :param discord_id: Идентификатор Discord пользователя.
    :return: user_id, если найден, иначе None.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM discord_user WHERE discord_id = %s", (discord_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None

# Функция проверки, является ли user_id администратором
def is_admin(user_id: int):
    """
    Проверяет, является ли user_id администратором.

    :param user_id: ID пользователя в игре.
    :return: True, если пользователь администратор, иначе False.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM admin WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None

def get_username_by_user_id(user_id):
    """
    Получает последний известный никнейм пользователя по его user_id
    
    :param user_id: ID пользователя для поиска
    :return: last_seen_user_name или None, если пользователь не найден
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cursor:
            query = """
            SELECT last_seen_user_name 
            FROM player 
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            return result[0] if result else None
            
    except psycopg2.Error as e:
        print(f"Ошибка при запросе к БД: {e}")
        return None
    finally:
        if conn:
            conn.close()
