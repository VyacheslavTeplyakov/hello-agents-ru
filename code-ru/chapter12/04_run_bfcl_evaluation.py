"""
Глава 12: Скрипт комплексной оценки BFCL

Скрипт реализует полный процесс оценки BFCL:
1. Автоматическая проверка и подготовка данных BFCL
2. Запуск оценки HelloAgents
3. Экспорт результатов в формат BFCL
4. Вызов официального инструмента оценки BFCL
5. Отображение результатов оценки

Использование:
    python examples/04_run_bfcl_evaluation.py

Дополнительные параметры:
    --category: категория оценки (по умолчанию: simple_python)
    --samples: количество примеров (по умолчанию: 5, 0 = все)
    --model-name: название модели (по умолчанию: HelloAgents)
"""

import sys
import subprocess
from pathlib import Path
import argparse
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.evaluation import BFCLDataset, BFCLEvaluator


# Системный промпт для вызова функций
FUNCTION_CALLING_SYSTEM_PROMPT = """Ты — профессиональный ассистент по вызову функций.

Твоя задача: на основе вопроса пользователя и предоставленных определений функций сгенерировать корректный вызов функции.

Требования к формату вывода:
1. Обязательно чистый JSON-формат, без каких-либо пояснений
2. Использовать формат JSON-массива: [{"name": "имя_функции", "arguments": {"имя_параметра": "значение_параметра"}}]
3. Если нужно вызвать несколько функций, добавить несколько объектов в массив
4. Если вызов функции не нужен, вернуть пустой массив: []

Пример:
Вопрос пользователя: Узнай погоду в Москве
Доступная функция: get_weather(city: str)
Правильный вывод: [{"name": "get_weather", "arguments": {"city": "Москва"}}]

Важно:
- Выводить только JSON, без фраз вроде "Хорошо," или "Я помогу тебе"
- Значения параметров должны соответствовать типам из определения функции
- Имена параметров должны точно совпадать с определением функции
"""


def check_bfcl_data(bfcl_data_dir: Path) -> bool:
    """Проверяет наличие данных BFCL"""
    if not bfcl_data_dir.exists():
        print(f"\nДиректория с данными BFCL не существует: {bfcl_data_dir}")
        print(f"\nСначала клонируйте репозиторий BFCL:")
        print(f"   git clone --depth 1 https://github.com/ShishirPatil/gorilla.git temp_gorilla")
        return False
    return True


def run_evaluation(category: str, max_samples: int, model_name: str) -> dict:
    """Запускает оценку HelloAgents"""
    print("\n" + "="*60)
    print("Шаг 1: Запуск оценки HelloAgents")
    print("="*60)

    # Директория данных BFCL
    bfcl_data_dir = project_root / "temp_gorilla" / "berkeley-function-call-leaderboard" / "bfcl_eval" / "data"

    # Проверяем наличие данных
    if not check_bfcl_data(bfcl_data_dir):
        return None

    # Загружаем набор данных
    print(f"\nЗагрузка набора данных BFCL...")
    dataset = BFCLDataset(bfcl_data_dir=str(bfcl_data_dir), category=category)

    # Создаём агента
    print(f"\nСоздание агента...")
    llm = HelloAgentsLLM()
    agent = SimpleAgent(
        name=model_name,
        llm=llm,
        system_prompt=FUNCTION_CALLING_SYSTEM_PROMPT,
        enable_tool_calling=False
    )
    print(f"   Агент: {model_name}")
    print(f"   LLM: {llm.provider}")

    # Создаём оценщик
    evaluator = BFCLEvaluator(dataset=dataset, category=category)

    # Запускаем оценку (передаём параметр max_samples)
    print(f"\nНачало оценки...")
    if max_samples > 0:
        print(f"   Количество примеров: {max_samples}")
        results = evaluator.evaluate(agent, max_samples=max_samples)
    else:
        print(f"   Количество примеров: все")
        results = evaluator.evaluate(agent, max_samples=None)

    # Отображаем результаты
    print(f"\nРезультаты оценки:")
    print(f"   Точность: {results['overall_accuracy']:.2%}")
    print(f"   Верных ответов: {results['correct_samples']}/{results['total_samples']}")

    return results


def export_bfcl_format(results: dict, category: str, model_name: str) -> Path:
    """Экспортирует результаты в формат BFCL"""
    print("\n" + "="*60)
    print("Шаг 2: Экспорт результатов в формат BFCL")
    print("="*60)

    # Директория для вывода
    output_dir = project_root / "evaluation_results" / "bfcl_official"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Файл для вывода
    output_file = output_dir / f"BFCL_v4_{category}_result.json"

    # Создаём оценщик для экспорта
    bfcl_data_dir = project_root / "temp_gorilla" / "berkeley-function-call-leaderboard" / "bfcl_eval" / "data"
    dataset = BFCLDataset(bfcl_data_dir=str(bfcl_data_dir), category=category)
    evaluator = BFCLEvaluator(dataset=dataset, category=category)

    # Экспортируем
    evaluator.export_to_bfcl_format(results, output_file)

    return output_file


def copy_to_bfcl_result_dir(source_file: Path, model_name: str, category: str) -> Path:
    """Копирует файл результатов в директорию результатов BFCL"""
    print("\n" + "="*60)
    print("Шаг 3: Подготовка к официальной оценке BFCL")
    print("="*60)

    # Директория результатов BFCL
    # Примечание: BFCL заменяет "/" в имени модели на "_"
    safe_model_name = model_name.replace("/", "_")
    result_dir = project_root / "result" / safe_model_name
    result_dir.mkdir(parents=True, exist_ok=True)

    # Целевой файл
    target_file = result_dir / f"BFCL_v4_{category}_result.json"

    # Копируем файл
    import shutil
    shutil.copy(source_file, target_file)

    print(f"\nФайл результатов скопирован в:")
    print(f"   {target_file}")

    return target_file


def run_bfcl_official_eval(model_name: str, category: str) -> bool:
    """Запускает официальную оценку BFCL"""
    print("\n" + "="*60)
    print("Шаг 4: Запуск официальной оценки BFCL")
    print("="*60)

    try:
        # Устанавливаем переменные окружения
        import os
        os.environ['PYTHONUTF8'] = '1'

        # Запускаем оценку BFCL
        cmd = [
            "bfcl", "evaluate",
            "--model", model_name,
            "--test-category", category,
            "--partial-eval"
        ]

        print(f"\nВыполняем команду: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Отображаем вывод
        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            print(f"\nОценка BFCL завершилась ошибкой:")
            if result.stderr:
                print(result.stderr)
            return False

        return True

    except FileNotFoundError:
        print("\nКоманда bfcl не найдена")
        print("   Сначала установите: pip install bfcl-eval")
        return False
    except Exception as e:
        print(f"\nОшибка при запуске оценки BFCL: {e}")
        return False


def show_results(model_name: str, category: str):
    """Отображает результаты оценки"""
    print("\n" + "="*60)
    print("Шаг 5: Отображение результатов оценки")
    print("="*60)

    # CSV-файл
    csv_file = project_root / "score" / "data_non_live.csv"

    if csv_file.exists():
        print(f"\nСводка результатов оценки:")
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    else:
        print(f"\nФайл с результатами оценки не найден: {csv_file}")

    # Файл с детальными оценками
    safe_model_name = model_name.replace("/", "_")
    score_file = project_root / "score" / safe_model_name / "non_live" / f"BFCL_v4_{category}_score.json"

    if score_file.exists():
        print(f"\nФайл с детальными оценками:")
        print(f"   {score_file}")

        # Читаем и отображаем точность
        with open(score_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            summary = json.loads(first_line)
            print(f"\nИтоговый результат:")
            print(f"   Точность: {summary['accuracy']:.2%}")
            print(f"   Верных ответов: {summary['correct_count']}/{summary['total_count']}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Скрипт комплексной оценки BFCL")
    parser.add_argument("--category", default="simple_python", help="Категория оценки")
    parser.add_argument("--samples", type=int, default=5, help="Количество примеров (0 = все)")
    parser.add_argument("--model-name", default="Qwen/Qwen3-8B",
                       help="Название модели (должно поддерживаться BFCL; запустите 'bfcl models' для списка)")

    args = parser.parse_args()

    print("="*60)
    print("Скрипт комплексной оценки BFCL")
    print("="*60)
    print(f"\nКонфигурация:")
    print(f"   Категория оценки: {args.category}")
    print(f"   Количество примеров: {args.samples if args.samples > 0 else 'все'}")
    print(f"   Название модели: {args.model_name}")

    # Шаг 1: Запускаем оценку
    results = run_evaluation(args.category, args.samples, args.model_name)
    if not results:
        return

    # Шаг 2: Экспортируем в формат BFCL
    output_file = export_bfcl_format(results, args.category, args.model_name)

    # Шаг 3: Копируем в директорию результатов BFCL
    copy_to_bfcl_result_dir(output_file, args.model_name, args.category)

    # Шаг 4: Запускаем официальную оценку BFCL
    if not run_bfcl_official_eval(args.model_name, args.category):
        print("\nОфициальная оценка BFCL не удалась, но оценка HelloAgents завершена")
        return

    # Шаг 5: Отображаем результаты
    show_results(args.model_name, args.category)

    print("\n" + "="*60)
    print("Оценка завершена!")
    print("="*60)


if __name__ == "__main__":
    main()
