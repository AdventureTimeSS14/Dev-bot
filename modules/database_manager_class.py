import disnake
import psycopg2

from config import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_PORT, DB_USER


class DatabaseManagerSS14:
    """
    Менеджер для работы с базами данных Space Station 14 (PostgreSQL).
    
    Предоставляет унифицированный интерфейс для работы с основными БД проекта:
    - Основная база данных (main)
    - База данных для разработки (dev)
    
    Attributes
    ----------
    db_params : dict
        Словарь с параметрами подключения к различным БД проекта.
        Содержит конфигурации для 'main' и 'dev' баз данных.
        
    Examples
    --------
    >>> db_manager = DatabaseManagerSS14()
    >>> player_data = db_manager.fetch_player_data("PlayerName")
    """
    def __init__(self):
        self.db_params = {
            'main': {
                'database': DB_DATABASE,
                'user': DB_USER,
                'password': DB_PASSWORD,
                'host': DB_HOST,
                'port': DB_PORT
            },
            'dev': {
                'database': 'ss14_dev',
                'user': DB_USER,
                'password': DB_PASSWORD,
                'host': DB_HOST,
                'port': DB_PORT
            }
        }

    def _get_connection(self, db_name='main'):
        """Возвращает соединение с указанной базой данных"""
        if db_name not in self.db_params:
            raise ValueError(f"Unknown database name: {db_name}")

        return psycopg2.connect(**self.db_params[db_name])

    def fetch_player_data(self, user_name, db_name='main'):
        """
        Поиск данных игрока по имени пользователя в основной базе или логах подключений.
        
        Осуществляет поиск в следующем порядке:
        1. В таблице player по полю last_seen_user_name
        2. Если не найдено, в таблице connection_log по полю user_name
        
        Parameters
        ----------
        user_name : str
            Имя пользователя для поиска (точное совпадение)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки
        
        Returns
        ----------
        tuple or None
            Возвращает кортеж с данными игрока в зависимости от места нахождения:
            - Если найден в таблице player: 
            (player_id, user_id, first_seen_time, last_seen_user_name)
            - Если найден в таблице connection_log:
            (connection_log_id, user_id, user_name)
            - None если игрок не найден ни в одной таблице
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
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

        return result


    def is_user_linked(self, user_id, discord_id, db_name='main'):
        """
        Проверяет, существует ли уже указанный discord_id или user_id в базе данных.
        
        Parameters
        ----------
        user_id : str
            ID пользователя в игровой базе данных
        discord_id : str
            Discord ID пользователя (обычно snowflake ID как строка)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки

        Returns
        ----------
        bool
            True если пользователь уже привязан (найдено совпадение по discord_id или user_id), 
            иначе False
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                # Проверяем, существует ли уже discord_id в базе
                cursor.execute("SELECT 1 FROM discord_user WHERE discord_id = %s", (str(discord_id),))
                result_discord_id = cursor.fetchone()

                # Проверяем, существует ли уже user_id в базе
                cursor.execute("SELECT 1 FROM discord_user WHERE user_id = %s", (user_id,))
                result_user_id = cursor.fetchone()

                return bool(result_discord_id or result_user_id)


    def link_user_to_discord(self, user_id, discord_id, db_name='main'):
        """
        Функция записи данных о привязке Discord в БД
        
        Parameters
        ----------
        
        user_id : str
            ID пользователя в игровой базе данных
        discord_id : str
            Discord ID пользователя (обычно snowflake ID как строка)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO discord_user (user_id, discord_id)
                VALUES (%s, %s)
                """
                cursor.execute(query, (user_id, discord_id))
                conn.commit()


    def unlink_user_from_discord(self, discord: disnake.Member, db_name='main'):
        """
        Функция отвязки Discord от аккаунта в БД
        
        Parameters
        ----------
        
        user_id : str
            ID пользователя в игровой базе данных
        discord_id : str
            Discord ID пользователя (обычно snowflake ID как строка)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки

        Returns
        ----------
        str
            user_id если отвязка прошла успешно, иначе None
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM discord_user WHERE discord_id = %s RETURNING user_id", 
                    (str(discord.id),)
                )
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else None


    def get_user_id_by_discord_id(self, discord_id: str, db_name='main'):
        """
        Получает user_id из игровой базы данных по Discord ID пользователя.

        Производит поиск в указанной базе данных в таблице discord_user,
        возвращая соответствующий user_id для заданного Discord ID.

        Parameters
        ----------
        discord_id : str
            Уникальный идентификатор пользователя Discord (снежинка/Snowflake ID)
            в строковом формате. Пример: "123456789012345678"
        
        db_name : str, optional
            Наименование базы данных для поиска, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - база данных для разработки

        Returns
        -------
        str | None
            Возвращает user_id в виде строки, если запись найдена.
            Возвращает None, если соответствие не найдено.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id FROM discord_user WHERE discord_id = %s", 
                    (discord_id,))
                result = cursor.fetchone()
                return result[0] if result else None

    def is_admin(self, user_id: int, db_name='main'):
        """
        Проверяет наличие административных прав у пользователя.

        Parameters
        ----------
        user_id : int
            Уникальный идентификатор пользователя в игровой базе данных.
            Должен быть целым числом.
        
        db_name : str, optional
            Наименование базы данных для проверки, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - база данных для разработки

        Returns
        -------
        bool
            True - если пользователь имеет административные права,
            False - если не имеет прав администратора или пользователь не найден.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM admin WHERE user_id = %s", 
                    (user_id,))
                result = cursor.fetchone()
                return result is not None

    def get_username_by_user_id(self, user_id, db_name='main'):
        """
        Получает последний известный никнейм игрока по его уникальному идентификатору.

        Производит поиск в указанной базе данных в таблице player,
        возвращая значение last_seen_user_name для заданного user_id.

        Parameters
        ----------
        user_id : str
            Уникальный идентификатор пользователя в системе.
            Ожидается строковое значение, даже если ID числовой.
        
        db_name : str, optional
            Целевая база данных для поиска, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - тестовая база данных

        Returns
        -------
        str | None
            - Последний известный никнейм пользователя в виде строки, если найден
            - None, если пользователь не найден или произошла ошибка
        """
        try:
            with self._get_connection(db_name) as conn:
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
