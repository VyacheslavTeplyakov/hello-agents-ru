"""
Шаг 1: Только генерация задач AIME

Запуск:
python data_generation/step1_generate_only.py 30 3.0

Параметры:
- 30: количество задач для генерации
- 3.0: задержка между генерациями (в секундах)
"""

import sys
from aime_generator import AIMEGenerator


def main():
    # Разбираем аргументы командной строки
    num_problems = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    delay_seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0

    print("\n" + "="*80)
    print("📝 Шаг 1: Генерация задач AIME")
    print("="*80)
    print(f"\nКонфигурация:")
    print(f"  - Количество задач: {num_problems}")
    print(f"  - Задержка API: {delay_seconds} с/задача")
    print(f"  - Референсные данные: TianHongZXY/aime-1983-2025 (900+ задач)")

    # Создаём генератор
    generator = AIMEGenerator(delay_seconds=delay_seconds)

    # Генерируем и сохраняем
    generated_data_path = generator.generate_and_save(
        num_problems=num_problems,
        output_dir="data_generation/generated_data"
    )

    print(f"\n✅ Шаг 1 завершён! Данные сохранены в: {generated_data_path}")
    print(f"\nСледующий шаг: запустите оценку")
    print(f"python data_generation/step2_evaluate_only.py {generated_data_path} 2024")


if __name__ == "__main__":
    main()
