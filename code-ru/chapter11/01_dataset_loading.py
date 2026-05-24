"""
Пример 1: Загрузка и форматирование датасета
Демонстрирует загрузку и просмотр датасета GSM8K с помощью RLTrainingTool
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# Пример 1: Загрузка датасета в формате SFT
# ============================================================================

def load_sft_dataset():
    """
    Загрузка датасета GSM8K в формате SFT с помощью RLTrainingTool

    Формат SFT данных:
    {
        "prompt": "Question: ...\n\nLet's solve this step by step:\n",
        "completion": "Step 1: ...\nFinal Answer: 42",
        "text": "Question: ...\n\nLet's solve this step by step:\nStep 1: ...\nFinal Answer: 42"
    }
    """
    tool = RLTrainingTool()

    config = {
        "action": "load_dataset",
        "format": "sft",
        "split": "train",
        "max_samples": 5
    }

    print("Загружаем датасет в формате SFT...")
    result = tool.run(config)
    result_dict = json.loads(result)

    print(f"✅ Размер датасета: {result_dict['dataset_size']}")
    print(f"📋 Столбцы датасета: {result_dict['sample_keys']}")
    print(f"\n💡 Подсказка: датасет загружен и готов к обучению")
    print(f"   Используйте action='train' для начала обучения")

    return result_dict


# ============================================================================
# Пример 2: Загрузка датасета в формате RL
# ============================================================================

def load_rl_dataset():
    """
    Загрузка датасета GSM8K в формате RL с помощью RLTrainingTool

    Формат RL данных:
    {
        "prompt": "<|im_start|>user\nQuestion: ...\n<|im_end|>\n<|im_start|>assistant\n",
        "ground_truth": "42",
        "question": "...",
        "full_answer": "..."
    }
    """
    tool = RLTrainingTool()

    config = {
        "action": "load_dataset",
        "format": "rl",
        "split": "train",
        "max_samples": 5,
        "model_name": "Qwen/Qwen3-0.6B"
    }

    print("Загружаем датасет в формате RL...")
    result = tool.run(config)
    result_dict = json.loads(result)

    print(f"✅ Размер датасета: {result_dict['dataset_size']}")
    print(f"📋 Столбцы датасета: {result_dict['sample_keys']}")
    print(f"\n💡 Подсказка: RL датасет загружен, содержит prompt и ground_truth")
    print(f"   Может использоваться для GRPO обучения")

    return result_dict


# ============================================================================
# Пример 3: Загрузка разных сплитов датасета
# ============================================================================

def load_different_splits():
    """
    Загрузка обучающего и тестового наборов данных
    """
    tool = RLTrainingTool()

    # Загружаем обучающий набор
    train_config = {
        "action": "load_dataset",
        "format": "sft",
        "split": "train",
        "max_samples": 100
    }

    print("Загружаем обучающий набор...")
    train_result = tool.run(train_config)
    train_data = json.loads(train_result)
    print(f"✅ Обучающий набор: {train_data['dataset_size']} образцов")

    # Загружаем тестовый набор
    test_config = {
        "action": "load_dataset",
        "format": "sft",
        "split": "test",
        "max_samples": 50
    }

    print("\nЗагружаем тестовый набор...")
    test_result = tool.run(test_config)
    test_data = json.loads(test_result)
    print(f"✅ Тестовый набор: {test_data['dataset_size']} образцов")

    return train_data, test_data


# ============================================================================
# Пример 4: Загрузка полного датасета
# ============================================================================

def load_full_dataset():
    """
    Загрузка полного датасета (max_samples=None)

    Датасет GSM8K:
    - Обучающий набор: ~7500 образцов
    - Тестовый набор: ~1300 образцов
    """
    tool = RLTrainingTool()

    config = {
        "action": "load_dataset",
        "format": "sft",
        "split": "train",
        "max_samples": None  # None = использовать все данные
    }

    print("Загружаем полный обучающий набор...")
    print("⚠️  Это может занять некоторое время...")

    # Раскомментируйте для фактической загрузки
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"✅ Полный обучающий набор: {result_dict['dataset_size']} образцов")

    print("💡 Подсказка: установите max_samples=None для загрузки всех данных")
    print("   Обучающий набор GSM8K содержит около 7500 образцов")

    return config


# ============================================================================
# Пример 5: Сравнение форматов SFT и RL
# ============================================================================

def compare_sft_rl_formats():
    """
    Сравнение различий форматов данных SFT и RL
    """
    tool = RLTrainingTool()

    print("="*80)
    print("Сравнение форматов данных SFT и RL")
    print("="*80)

    # Формат SFT
    sft_config = {
        "action": "load_dataset",
        "format": "sft",
        "split": "train",
        "max_samples": 1
    }

    print("\n1. Формат SFT:")
    sft_result = tool.run(sft_config)
    sft_data = json.loads(sft_result)
    print(f"   Столбцы: {sft_data['sample_keys']}")
    print(f"   Назначение: Supervised Fine-Tuning (обучение с учителем)")
    print(f"   Особенность: содержит полный prompt и completion")

    # Формат RL
    rl_config = {
        "action": "load_dataset",
        "format": "rl",
        "split": "train",
        "max_samples": 1,
        "model_name": "Qwen/Qwen3-0.6B"
    }

    print("\n2. Формат RL:")
    rl_result = tool.run(rl_config)
    rl_data = json.loads(rl_result)
    print(f"   Столбцы: {rl_data['sample_keys']}")
    print(f"   Назначение: обучение с подкреплением (Reinforcement Learning)")
    print(f"   Особенность: содержит prompt и ground_truth для вычисления вознаграждения")

    print("\nКлючевые различия:")
    print("  - SFT: напрямую обучается на правильных ответах")
    print("  - RL: учится через сигнал вознаграждения, более гибкий подход")

    return sft_data, rl_data


# ============================================================================
# Пример 6: Статистика датасета
# ============================================================================

def dataset_statistics():
    """
    Просмотр статистики датасета
    """
    tool = RLTrainingTool()

    config = {
        "action": "load_dataset",
        "format": "sft",
        "split": "train",
        "max_samples": 100
    }

    print("Загружаем датасет...")
    result = tool.run(config)
    result_dict = json.loads(result)

    print("\nСтатистика датасета:")
    print(f"  Всего образцов: {result_dict['dataset_size']}")
    print(f"  Столбцы данных: {', '.join(result_dict['sample_keys'])}")
    print(f"  Датасет: GSM8K (Grade School Math 8K)")
    print(f"  Тип задачи: математические рассуждения")

    print(f"\n💡 Подсказка: датасет содержит следующие поля:")
    for key in result_dict['sample_keys']:
        print(f"  - {key}")

    return result_dict


# ============================================================================
# Главная функция
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Пример 1: Загрузка датасета в формате SFT")
    print("="*80)
    load_sft_dataset()

    print("\n" + "="*80)
    print("Пример 2: Загрузка датасета в формате RL")
    print("="*80)
    load_rl_dataset()

    print("\n" + "="*80)
    print("Пример 3: Загрузка разных сплитов датасета")
    print("="*80)
    load_different_splits()

    print("\n" + "="*80)
    print("Пример 4: Загрузка полного датасета")
    print("="*80)
    load_full_dataset()

    print("\n" + "="*80)
    print("Пример 5: Сравнение форматов SFT и RL")
    print("="*80)
    compare_sft_rl_formats()

    print("\n" + "="*80)
    print("Пример 6: Статистика датасета")
    print("="*80)
    dataset_statistics()
