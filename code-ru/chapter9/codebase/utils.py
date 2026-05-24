"""
Модуль вспомогательных функций
Предоставляет часто используемые утилиты
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Загрузить файл конфигурации

    Args:
        config_path: Путь к файлу конфигурации

    Returns:
        Словарь конфигурации
    """
    # TODO: Поддержать несколько форматов конфигурационных файлов
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Сохранить конфигурацию в файл

    Args:
        config: Словарь конфигурации
        config_path: Путь к файлу конфигурации
    """
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_timestamp() -> str:
    """
    Получить текущую метку времени

    Returns:
        Строка метки времени в формате ISO
    """
    return datetime.now().isoformat()


def ensure_dir(directory: str) -> None:
    """
    Убедиться, что директория существует; создать при необходимости

    Args:
        directory: Путь к директории
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def format_size(size_bytes: int) -> str:
    """
    Форматировать размер файла

    Args:
        size_bytes: Количество байт

    Returns:
        Отформатированная строка размера
    """
    # TODO: Оптимизировать логику форматирования
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def validate_email(email: str) -> bool:
    """
    Проверить формат адреса электронной почты

    Args:
        email: Адрес электронной почты

    Returns:
        True, если адрес корректен
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
