"""
Пример 7: Оценка модели

Демонстрирует, как использовать RLTrainingTool для оценки обученной модели
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# Пример 1: Оценка SFT-модели
# ============================================================================

def evaluate_sft_model():
    """
    Оценка модели после SFT-обучения

    Используем тестовую выборку для измерения точности модели
    """
    tool = RLTrainingTool()

    config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/sft",
        "max_samples": 50  # используем 50 тестовых примеров
    }

    print("Оценка SFT-модели:")
    print(f"  Путь к модели: {config['model_path']}")
    print(f"  Кол-во тестовых примеров: {config['max_samples']}")

    # Раскомментируй для запуска реальной оценки
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Оценка завершена!")
    # print(f"  Точность: {result_dict['accuracy']}")
    # print(f"  Средняя награда: {result_dict['average_reward']}")

    print("\n💡 Подсказка: раскомментируй код выше, чтобы запустить оценку")

    return config


# ============================================================================
# Пример 2: Оценка GRPO-модели
# ============================================================================

def evaluate_grpo_model():
    """
    Оценка модели после GRPO-обучения

    Сравниваем производительность GRPO-модели и SFT-модели
    """
    tool = RLTrainingTool()

    config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/grpo",
        "max_samples": 50
    }

    print("Оценка GRPO-модели:")
    print(f"  Путь к модели: {config['model_path']}")
    print(f"  Кол-во тестовых примеров: {config['max_samples']}")

    # Раскомментируй для запуска реальной оценки
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Оценка завершена!")
    # print(f"  Точность: {result_dict['accuracy']}")
    # print(f"  Средняя награда: {result_dict['average_reward']}")

    print("\n💡 Подсказка: раскомментируй код выше, чтобы запустить оценку")

    return config


# ============================================================================
# Пример 3: Сравнение SFT и GRPO-моделей
# ============================================================================

def compare_sft_grpo():
    """
    Сравнение производительности SFT и GRPO-моделей

    Оцениваем обе модели на одной и той же тестовой выборке
    """
    tool = RLTrainingTool()

    print("="*80)
    print("Сравнение моделей SFT и GRPO")
    print("="*80)

    # Оцениваем SFT-модель
    print("\n1. Оценка SFT-модели...")
    sft_config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/sft",
        "max_samples": 100
    }

    # Раскомментируй для запуска реальной оценки
    # sft_result = tool.run(sft_config)
    # sft_data = json.loads(sft_result)
    # print(f"   Точность SFT: {sft_data['accuracy']}")

    # Оцениваем GRPO-модель
    print("\n2. Оценка GRPO-модели...")
    grpo_config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/grpo",
        "max_samples": 100
    }

    # Раскомментируй для запуска реальной оценки
    # grpo_result = tool.run(grpo_config)
    # grpo_data = json.loads(grpo_result)
    # print(f"   Точность GRPO: {grpo_data['accuracy']}")

    # Итоги сравнения
    print("\nРезультаты сравнения:")
    print("  SFT-модель: обучается базовому формату и шагам рассуждения")
    print("  GRPO-модель: оптимизирует способность рассуждать через RL")
    print("  Ожидается: точность GRPO > точность SFT")

    print("\n💡 Подсказка: раскомментируй код выше, чтобы запустить реальную оценку")

    return sft_config, grpo_config


# ============================================================================
# Пример 4: Оценка базовой модели
# ============================================================================

def evaluate_baseline():
    """
    Оценка базовой модели (исходной, без дообучения)

    Используется для сравнения эффекта обучения
    """
    tool = RLTrainingTool()

    config = {
        "action": "evaluate",
        "model_path": "Qwen/Qwen3-0.6B",  # исходная модель
        "max_samples": 50
    }

    print("Оценка базовой модели:")
    print(f"  Модель: {config['model_path']}")
    print(f"  Кол-во тестовых примеров: {config['max_samples']}")

    # Раскомментируй для запуска реальной оценки
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Оценка завершена!")
    # print(f"  Базовая точность: {result_dict['accuracy']}")

    print("\n💡 Подсказка: базовая модель обычно показывает низкую точность")
    print("   Обученные модели должны значительно превосходить базовую")

    return config


# ============================================================================
# Пример 5: Полный цикл оценки
# ============================================================================

def complete_evaluation():
    """
    Полный цикл оценки

    Оцениваем три модели: базовую, SFT и GRPO
    """
    tool = RLTrainingTool()

    models = {
        "Базовая модель": "Qwen/Qwen3-0.6B",
        "SFT-модель": "./output/quick_test/sft",
        "GRPO-модель": "./output/quick_test/grpo"
    }

    print("="*80)
    print("Полный цикл оценки")
    print("="*80)

    results = {}

    for name, model_path in models.items():
        print(f"\nОценка {name}...")
        print(f"  Путь: {model_path}")

        config = {
            "action": "evaluate",
            "model_path": model_path,
            "max_samples": 100
        }

        # Раскомментируй для запуска реальной оценки
        # result = tool.run(config)
        # result_dict = json.loads(result)
        # results[name] = result_dict
        # print(f"  Точность: {result_dict['accuracy']}")

    print("\n" + "="*80)
    print("Итоги оценки")
    print("="*80)

    # Раскомментируй для запуска реальной оценки
    # for name, result in results.items():
    #     print(f"{name}: {result['accuracy']}")

    print("\nОжидаемые результаты:")
    print("  Базовая модель < SFT-модель < GRPO-модель")
    print("  Это подтверждает, что RL-обучение эффективно повышает качество модели")

    print("\n💡 Подсказка: раскомментируй код выше, чтобы запустить полную оценку")

    return models


# ============================================================================
# Пример 6: Практический пример оценки
# ============================================================================

def practical_evaluation():
    """
    Практический пример оценки — можно запускать напрямую

    Оцениваем модели, обученные в quick_test
    """
    tool = RLTrainingTool()

    print("="*80)
    print("Практический пример оценки")
    print("="*80)

    # Проверяем наличие моделей
    import os
    sft_path = "./output/quick_test/sft"
    grpo_path = "./output/quick_test/grpo"

    if not os.path.exists(sft_path):
        print(f"\n❌ SFT-модель не найдена: {sft_path}")
        print("   Сначала запусти 00_quick_test.py для обучения модели")
        return None

    if not os.path.exists(grpo_path):
        print(f"\n❌ GRPO-модель не найдена: {grpo_path}")
        print("   Сначала запусти 00_quick_test.py для обучения модели")
        return None

    print("\n✅ Файлы моделей найдены, начинаем оценку...")

    # Оцениваем SFT-модель
    print("\n1. Оценка SFT-модели...")
    sft_config = {
        "action": "evaluate",
        "model_path": sft_path,
        "max_samples": 20  # небольшое кол-во примеров для быстрого теста
    }

    print("💡 Подсказка: раскомментируй код ниже, чтобы запустить оценку")
    print("# sft_result = tool.run(sft_config)")
    print("# sft_data = json.loads(sft_result)")
    print("# print(f'Точность SFT: {sft_data[\"accuracy\"]}')")

    # Оцениваем GRPO-модель
    print("\n2. Оценка GRPO-модели...")
    grpo_config = {
        "action": "evaluate",
        "model_path": grpo_path,
        "max_samples": 20
    }

    print("💡 Подсказка: раскомментируй код ниже, чтобы запустить оценку")
    print("# grpo_result = tool.run(grpo_config)")
    print("# grpo_data = json.loads(grpo_result)")
    print("# print(f'Точность GRPO: {grpo_data[\"accuracy\"]}')")

    # Раскомментируй для запуска реальной оценки
    # sft_result = tool.run(sft_config)
    # sft_data = json.loads(sft_result)
    # print(f"\n✅ SFT оценка завершена: {sft_data['accuracy']}")

    # grpo_result = tool.run(grpo_config)
    # grpo_data = json.loads(grpo_result)
    # print(f"✅ GRPO оценка завершена: {grpo_data['accuracy']}")

    return sft_config, grpo_config


# ============================================================================
# Главная функция
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Пример 1: Оценка SFT-модели")
    print("="*80)
    evaluate_sft_model()

    print("\n" + "="*80)
    print("Пример 2: Оценка GRPO-модели")
    print("="*80)
    evaluate_grpo_model()

    print("\n" + "="*80)
    print("Пример 3: Сравнение SFT и GRPO-моделей")
    print("="*80)
    compare_sft_grpo()

    print("\n" + "="*80)
    print("Пример 4: Оценка базовой модели")
    print("="*80)
    evaluate_baseline()

    print("\n" + "="*80)
    print("Пример 5: Полный цикл оценки")
    print("="*80)
    complete_evaluation()

    print("\n" + "="*80)
    print("Пример 6: Практический пример оценки")
    print("="*80)
    practical_evaluation()
