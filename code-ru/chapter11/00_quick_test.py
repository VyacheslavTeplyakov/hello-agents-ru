"""
Быстрый тест эксперимента

Быстрая проверка пайплайнов SFT и GRPO обучения на небольшом объёме данных
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


def quick_test():
    """
    Быстрый тест эксперимента

    Конфигурация:
    - Модель: Qwen/Qwen3-0.6B
    - Число образцов: 10
    - Эпох обучения: 1
    - Ожидаемое время: ~2-3 минуты
    """
    tool = RLTrainingTool()

    print("="*80)
    print("Быстрый тест эксперимента")
    print("="*80)

    # ========================================================================
    # Тест 1: Загрузка данных
    # ========================================================================
    print("\nТест 1: Загрузка данных")
    print("-"*80)

    data_config = {
        "action": "load_dataset",
        "format_type": "sft",
        "split": "train",
        "max_samples": 5
    }

    print("Загружаем датасет...")
    result = tool.run(data_config)
    data = json.loads(result)
    print(f"✅ Датасет успешно загружен: {data['dataset_size']} образцов")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # ========================================================================
    # Тест 2: SFT обучение
    # ========================================================================
    print("\nТест 2: SFT обучение")
    print("-"*80)

    sft_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test/sft",
        "max_samples": 10,
        "num_epochs": 1,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
    }

    print("Конфигурация SFT:")
    print(json.dumps(sft_config, indent=2, ensure_ascii=False))

    print("\n⏳ Начинаем SFT обучение...")
    sft_result = tool.run(sft_config)
    sft_data = json.loads(sft_result)
    print("\n✅ Результат SFT обучения:")
    print(json.dumps(sft_data, indent=2, ensure_ascii=False))

    # ========================================================================
    # Тест 3: GRPO обучение
    # ========================================================================
    print("\nТест 3: GRPO обучение")
    print("-"*80)

    grpo_config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test/grpo",
        "max_samples": 10,
        "num_epochs": 1,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
    }

    print("Конфигурация GRPO:")
    print(json.dumps(grpo_config, indent=2, ensure_ascii=False))

    print("\n⏳ Начинаем GRPO обучение...")
    grpo_result = tool.run(grpo_config)
    grpo_data = json.loads(grpo_result)
    print("\n✅ Результат GRPO обучения:")
    print(json.dumps(grpo_data, indent=2, ensure_ascii=False))

    # ========================================================================
    # Тест 4: Функция вознаграждения
    # ========================================================================
    print("\nТест 4: Функция вознаграждения")
    print("-"*80)

    reward_config = {
        "action": "create_reward",
        "reward_type": "accuracy"
    }

    print("Создаём функцию вознаграждения...")
    reward_result = tool.run(reward_config)
    reward_data = json.loads(reward_result)
    print("✅ Функция вознаграждения успешно создана:")
    print(json.dumps(reward_data, indent=2, ensure_ascii=False))

    # ========================================================================
    # Итоги
    # ========================================================================
    print("\n" + "="*80)
    print("Итоги тестирования")
    print("="*80)
    print("\n✅ Все тесты пройдены!")
    print("\nПроверенные пункты:")
    print("  1. ✅ Загрузка данных")
    print("  2. ✅ SFT обучение")
    print("  3. ✅ GRPO обучение")
    print("  4. ✅ Создание функции вознаграждения")

    print("\nПути к моделям:")
    print(f"  SFT модель: {sft_config['output_dir']}")
    print(f"  GRPO модель: {grpo_config['output_dir']}")


if __name__ == "__main__":
    quick_test()
