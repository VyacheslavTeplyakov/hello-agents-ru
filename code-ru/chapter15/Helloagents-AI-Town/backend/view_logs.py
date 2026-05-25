"""Утилита для просмотра логов диалогов в реальном времени"""

import os
import time
from pathlib import Path
from datetime import datetime

# Директория логов
LOGS_DIR = Path(__file__).parent / "logs"
today = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOGS_DIR / f"dialogue_{today}.log"

def tail_log_file(filename, interval=1):
    """Просмотр файла логов в реальном времени (аналог tail -f)"""

    print("\n" + "="*60)
    print(f"📝 Просмотр логов диалогов в реальном времени")
    print(f"📂 Файл логов: {filename}")
    print("="*60)
    print("\nНажмите Ctrl+C для остановки\n")

    # Если файл ещё не создан, ждём
    while not filename.exists():
        print(f"⏳ Ожидание создания файла логов: {filename}")
        time.sleep(interval)

    # Открываем файл
    with open(filename, 'r', encoding='utf-8') as f:
        # Перемещаемся в конец файла
        f.seek(0, 2)

        try:
            while True:
                line = f.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ Просмотр логов остановлен")

def view_full_log(filename):
    """Просмотр полного содержимого лога"""

    print("\n" + "="*60)
    print(f"📝 Просмотр полного лога диалогов")
    print(f"📂 Файл логов: {filename}")
    print("="*60 + "\n")

    if not filename.exists():
        print(f"❌ Файл логов не найден: {filename}")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)

    print("\n" + "="*60)
    print("✅ Просмотр лога завершён")
    print("="*60 + "\n")

def list_log_files():
    """Список всех файлов логов"""

    print("\n" + "="*60)
    print(f"📂 Список файлов логов")
    print(f"📁 Директория: {LOGS_DIR}")
    print("="*60 + "\n")

    if not LOGS_DIR.exists():
        print("❌ Директория логов не существует")
        return

    log_files = sorted(LOGS_DIR.glob("dialogue_*.log"), reverse=True)

    if not log_files:
        print("📭 Файлов логов пока нет")
        return

    for i, log_file in enumerate(log_files, 1):
        size = log_file.stat().st_size
        size_kb = size / 1024
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"{i}. {log_file.name}")
        print(f"   Размер: {size_kb:.2f} КБ")
        print(f"   Изменён: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "tail":
            # Просмотр в реальном времени
            tail_log_file(LOG_FILE)
        elif command == "view":
            # Просмотр полного лога
            view_full_log(LOG_FILE)
        elif command == "list":
            # Список всех логов
            list_log_files()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("\nИспользование:")
            print("  python view_logs.py tail   # Просмотр логов в реальном времени")
            print("  python view_logs.py view   # Просмотр полного лога")
            print("  python view_logs.py list   # Список всех файлов логов")
    else:
        # По умолчанию — просмотр в реальном времени
        tail_log_file(LOG_FILE)
