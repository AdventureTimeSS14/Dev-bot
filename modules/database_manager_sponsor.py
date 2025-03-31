import psycopg2

from config import DB_HOST, DB_PASSWORD, DB_PORT, DB_USER


class SponsorDatabaseManager:
    """
    Специализированный менеджер для работы с базой данных спонсоров.
    
    Отдельный класс в связи с совершенно другой структурой БД
    (содержит всего одну таблицу с уникальной структурой).
    
    Attributes
    ----------
    db_params : dict
        Параметры подключения к БД спонсоров
    """
    def __init__(self):
        self.db_params = {
            'sponsor': {
                'database': 'sponsors',
                'user': DB_USER,
                'password': DB_PASSWORD,
                'host': DB_HOST,
                'port': DB_PORT
            }
        }

    def _get_connection(self):
        """Возвращает соединение с БД спонсоров"""
        return psycopg2.connect(**self.db_params['sponsor'])
