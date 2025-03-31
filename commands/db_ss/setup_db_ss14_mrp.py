from config import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_PORT, DB_USER

# Параметры подключения к базе данных
DB_PARAMS = {
    'database': DB_DATABASE,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}

DB_PARAMS_DEV = {
    'database': 'ss14_dev',
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}

DB_PARAMS_SPONSOR = {
    'database': 'sponsors',
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}
