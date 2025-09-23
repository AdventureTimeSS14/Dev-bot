import json
import os
import threading
from typing import Dict, List, Tuple


_LOCK = threading.Lock()
_STORAGE_PATH = os.path.join("cache", "command_usage.json")


def _ensure_storage_dir_exists() -> None:
	os.makedirs(os.path.dirname(_STORAGE_PATH), exist_ok=True)


def _load_data() -> Dict[str, int]:
	_ensure_storage_dir_exists()
	if not os.path.exists(_STORAGE_PATH):
		return {}
	try:
		with open(_STORAGE_PATH, "r", encoding="utf-8") as f:
			data = json.load(f)
			return {str(k): int(v) for k, v in data.items()}
	except Exception:
		return {}


def _save_data(data: Dict[str, int]) -> None:
	_ensure_storage_dir_exists()
	with open(_STORAGE_PATH, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)


def increment_command_usage(command_name: str) -> None:
	"""Инкрементирует счётчик использования команды по имени."""
	if not command_name:
		return
	with _LOCK:
		data = _load_data()
		data[command_name] = data.get(command_name, 0) + 1
		_save_data(data)


def get_top_commands(limit: int = 10) -> List[Tuple[str, int]]:
	"""Возвращает топ команд по количеству использований."""
	with _LOCK:
		data = _load_data()
		items = sorted(data.items(), key=lambda x: x[1], reverse=True)
		return items[: max(1, limit)]


def reset_usage() -> None:
	"""Полностью сбрасывает статистику использования."""
	with _LOCK:
		_save_data({})


