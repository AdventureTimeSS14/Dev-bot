import os
import sqlite3
from datetime import datetime

# Database file under project data directory
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "vacations.sqlite3")


def _ensure_db_initialized(connection: sqlite3.Connection) -> None:
	"""
	Ensure the vacations table exists. Uses TEXT for dates to keep it simple
	and cross-platform. created_at defaults to current timestamp.
	"""
	with connection:
		connection.execute(
			"""
			CREATE TABLE IF NOT EXISTS vacation_team (
				discord_id INTEGER PRIMARY KEY,
				data_end_vacation TEXT NOT NULL,
				reason TEXT NOT NULL,
				created_at TEXT NOT NULL DEFAULT (datetime('now'))
			)
			"""
		)
		# Helpful index for due-date lookups and ordering by created_at
		connection.execute("CREATE INDEX IF NOT EXISTS idx_vacation_due ON vacation_team(date(data_end_vacation))")
		connection.execute("CREATE INDEX IF NOT EXISTS idx_vacation_created ON vacation_team(date(created_at))")

	# Seed initial data once if table is empty
	cur = connection.execute("SELECT COUNT(1) FROM vacation_team")
	count = cur.fetchone()[0]
	if count == 0:
		seed_rows = [
			(1008703699813675050, "2026-03-25", "В бесрочном", "2025-03-24 13:50:44.000"),
			(1067182233741426748, "2026-03-25", "В бесрочном", "2025-03-24 13:42:25.000"),
			(1253136862026137693, "2025-09-10", "Нуждается в отдыхе.", "2025-09-02 17:24:46.000"),
			(1292086494583848982, "2025-09-10", '"Нужна передышка"', "2025-08-26 14:51:23.000"),
			(156083072025100288, "2025-09-10", "Сильная усталость. Убедительная просьба не тревожить начальника.", "2025-08-20 11:36:02.000"),
			(257521600092438529, "2025-09-09", "Всё ещё сильная нагрузка в жизни", "2025-09-02 05:54:34.000"),
			(282922584167940097, "2026-03-25", "В бесрочном", "2025-03-24 13:55:23.000"),
			(328502766622474240, "2025-09-20", "Всё ещё отдыхаю", "2025-08-28 21:38:17.000"),
			(414667623230603290, "2025-12-31", "По состоянию здоровья", "2025-04-03 16:03:32.000"),
			(436231957928476672, "2025-09-20", "Отдыхаем", "2025-08-18 18:46:58.000"),
			(474577432955977738, "2025-09-15", "Устал от игры", "2025-08-25 10:40:39.000"),
			(484332234141335552, "2025-09-16", "Усталость.", "2025-09-09 10:08:37.000"),
			(631892237650886698, "2025-09-15", "Борьба с тех.неполадками.", "2025-08-31 18:49:18.000"),
			(675669928413495317, "2026-03-25", "В бесрочном", "2025-03-24 13:53:14.000"),
			(689713606329106463, "2025-09-11", "Занятость в реальной жизни.", "2025-08-27 18:08:14.000"),
			(698317965359054968, "2025-09-15", '"Неотложные дела в реальной жизни"', "2025-08-24 23:26:01.000"),
			(720064943629664316, "2025-09-15", "Проблемы в реальной жизни.", "2025-08-14 17:30:19.000"),
			(786629333636349993, "2026-07-11", "Бессрочный отпуск из-за тех.неполадок и выгорания.", "2025-07-11 13:16:06.000"),
			(921388905209675847, "2025-09-21", "Крайняя утомлённость.", "2025-09-07 11:02:48.000"),
			(923449970651168768, "2026-04-13", '"Сломался компьютер/блок питания, до окончания ремонта"', "2025-04-12 21:20:31.000"),
			(961530935088656394, "2025-12-03", '"Бессрочный отпуск для решения проблем по здоровьем"', "2025-07-30 11:21:11.000"),
		]
		with connection:
			connection.executemany(
				"INSERT OR REPLACE INTO vacation_team (discord_id, data_end_vacation, reason, created_at) VALUES (?, ?, ?, ?)",
				seed_rows,
			)


def _tune_sqlite(connection: sqlite3.Connection) -> None:
	"""Apply runtime PRAGMAs for better performance with low memory impact."""
	cur = connection.cursor()
	cur.execute("PRAGMA journal_mode=WAL;")
	cur.execute("PRAGMA synchronous=NORMAL;")
	cur.execute("PRAGMA temp_store=MEMORY;")
	cur.execute("PRAGMA mmap_size=33554432;")  # 32MB
	cur.close()


def get_sqlite_connection() -> sqlite3.Connection:
	"""
	Open (and initialize) a SQLite connection for vacation data.
	"""
	os.makedirs(DB_DIR, exist_ok=True)
	conn = sqlite3.connect(DB_PATH)
	_tune_sqlite(conn)
	# Return rows as tuples for compatibility with existing code
	_ensure_db_initialized(conn)
	return conn
