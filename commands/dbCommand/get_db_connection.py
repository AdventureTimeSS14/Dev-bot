import mariadb

from config import DATABASE, HOST, PASSWORD, PORT, USER


def get_db_connection():
    """
    Устанавливает и возвращает подключение к базе данных MariaDB.

    Возвращает:
        conn (mariadb.connection): Объект подключения к базе данных, если подключение успешно.
        None: Если возникла ошибка при подключении.
    """
    conn = None
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=int(PORT),
            database=DATABASE,
        )
    except mariadb.Error as e:
        print(f"Error: {e}")
    return conn
