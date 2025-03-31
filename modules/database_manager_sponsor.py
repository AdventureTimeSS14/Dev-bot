import time

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

    def check_connection(self) -> tuple[bool, float, str]:
        """
        Проверяет подключение к базе данных спонсоров и возвращает статус.
        
        Returns
        -------
        tuple[bool, float, str]
            - bool: Флаг успешного подключения
            - float: Время отклика в миллисекундах
            - str: Сообщение об ошибке (пустая строка при успехе)
        """
        try:
            start_time = time.time()
            with self._get_connection() as conn:  # ✅ Убрали лишний аргумент
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            ping_time = (time.time() - start_time) * 1000
            return True, ping_time, ""
        except Exception as e:
            return False, 0.0, str(e)

    def get_connection_status_report(self) -> str:
        """
        Формирует отчет о состоянии подключений ко всем базам данных.
        
        Returns
        -------
        str
            Отформатированный отчет в виде строки Markdown
        """
        report_lines = ["🤑 **Проверка состояния спонсорской базы данных:**"]

        for db_name in self.db_params.keys():
            success, ping_time, error = self.check_connection()
            if success:
                report_lines.append(
                    f"✅ `{db_name}`: Подключение успешно | Пинг: {ping_time:.2f}мс"
                )
            else:
                report_lines.append(
                    f"❌ `{db_name}`: Ошибка подключения - {error}"
                )

        return "\n".join(report_lines)
