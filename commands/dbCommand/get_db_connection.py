import mariadb

from config import (
    DATABASE, HOST, PASSWORD, PORT, USER,
    DB_DATABASE, DB_HOST, DB_PASSWORD, DB_PORT, DB_USER,
)


def get_db_connection():
    """
    Устанавливает и возвращает подключение к базе данных MariaDB.

    Возвращает:
        conn (mariadb.connection): Объект подключения к базе данных, если подключение успешно.
        None: Если возникла ошибка при подключении.
    """
    conn = None
    try:
        # Prefer explicit DB_* vars if available, fall back to generic ones
        user_val = DB_USER if DB_USER and DB_USER != "NULL" else USER
        password_val = DB_PASSWORD if DB_PASSWORD and DB_PASSWORD != "NULL" else PASSWORD
        host_val = DB_HOST if DB_HOST and DB_HOST != "NULL" else HOST
        port_val_raw = DB_PORT if DB_PORT and DB_PORT != "NULL" else PORT
        database_val = DB_DATABASE if DB_DATABASE and DB_DATABASE != "NULL" else DATABASE

        if not user_val or user_val == "NULL" or not host_val or host_val == "NULL" or not database_val or database_val == "NULL":
            print("DB connection config invalid: user/host/database is missing. Check .env (USER/DB_USER, HOST/DB_HOST, DATABASE/DB_DATABASE)")
            return None

        try:
            port_val = int(port_val_raw) if port_val_raw and port_val_raw != "NULL" else 3306
        except ValueError:
            print(f"DB connection config invalid: PORT='{port_val_raw}' is not an integer. Using default 3306.")
            port_val = 3306

        conn = mariadb.connect(
            user=user_val,
            password=password_val,
            host=host_val,
            port=port_val,
            database=database_val,
        )
    except mariadb.Error as e:
        print(f"MariaDB connection error: {e}")
    except Exception as e:
        print(f"Unexpected DB connection error: {e}")
    return conn
