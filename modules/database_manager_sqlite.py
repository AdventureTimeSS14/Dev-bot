import sqlite3
from typing import List, Tuple, Optional

from commands.dbCommand.get_sqlite_connection import get_sqlite_connection


class DatabaseManagerSQLite:
	"""
	Простой менеджер для работы с локальной БД SQLite (vacations).
	Сфокусирован на операциях для отпусков.
	"""

	def _get_connection(self) -> sqlite3.Connection:
		return get_sqlite_connection()

	def list_vacations(self) -> List[Tuple[int, str, str, str]]:
		"""Возвращает все отпуска (discord_id, data_end_vacation, reason, created_at)."""
		with self._get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT discord_id, data_end_vacation, reason, created_at FROM vacation_team ORDER BY created_at DESC")
			return cursor.fetchall()

	def add_or_update_vacation(self, discord_id: int, data_end_vacation: str, reason: str) -> None:
		"""Добавляет или обновляет отпуск для пользователя."""
		with self._get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute(
				"INSERT OR REPLACE INTO vacation_team (discord_id, data_end_vacation, reason) VALUES (?, ?, ?)",
				(discord_id, data_end_vacation, reason),
			)
			conn.commit()

	def remove_vacation(self, discord_id: int) -> None:
		"""Удаляет отпуск пользователя по discord_id."""
		with self._get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute("DELETE FROM vacation_team WHERE discord_id = ?", (discord_id,))
			conn.commit()

	def extend_vacation(self, discord_id: int, new_end_date: str, reason: str) -> None:
		"""Продлевает отпуск (обновляет дату и причину)."""
		with self._get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute(
				"UPDATE vacation_team SET data_end_vacation = ?, reason = ? WHERE discord_id = ?",
				(new_end_date, reason, discord_id),
			)
			conn.commit()

	def get_due_vacations(self, date_str: str) -> List[Tuple[int, str]]:
		"""Возвращает отпуска, дата окончания которых <= указанной."""
		with self._get_connection() as conn:
			cursor = conn.cursor()
			cursor.execute(
				"SELECT discord_id, data_end_vacation FROM vacation_team WHERE date(data_end_vacation) <= date(?)",
				(date_str,),
			)
			return cursor.fetchall()
