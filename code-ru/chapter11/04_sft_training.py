"""
Пример 4: Полный пайплайн SFT обучения

Демонстрирует supervised fine-tuning (обучение с учителем) с помощью RLTrainingTool
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# Пример 1: Минимальный пример SFT обучения
# ============================================================================

def minimal_sft_training():
    """
    Простейший пример SFT обучения

    Достаточно одного вызова RLTrainingTool
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/sft_minimal",
        "max_samples": 10,
        "num_epochs": 1,
    }

    print("Простейший пример SFT обучения:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: {config['max_samples']}")
    print(f"  Эпох обучения: {config['num_epochs']}")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Обучение завершено! Модель сохранена в: {result_dict['output_dir']}")

    return config


# ============================================================================
# Пример 2: Стандартная конфигурация SFT обучения
# ============================================================================

def standard_sft_training():
    """
    Стандартная конфигурация SFT обучения

    Включает:
    - Эффективную настройку параметров через LoRA
    - Разумные параметры обучения
    - Использование части датасета
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "sft",

        # Конфигурация модели
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/sft_standard",

        # Конфигурация данных
        "max_samples": 1000,  # использовать 1000 образцов

        # Конфигурация обучения
        "num_epochs": 3,
        "batch_size": 4,
        "learning_rate": 5e-5,

        # Конфигурация LoRA
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }

    print("Стандартная конфигурация SFT обучения:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: {config['max_samples']}")
    print(f"  Эпох обучения: {config['num_epochs']}")
    print(f"  batch_size: {config['batch_size']}")
    print(f"  learning_rate: {config['learning_rate']}")
    print(f"  Ранг LoRA: {config['lora_r']}")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Обучение завершено!")
    # print(f"📁 Модель сохранена в: {result_dict['output_dir']}")

    return config


# ============================================================================
# Пример 3: Обучение на полном датасете
# ============================================================================

def full_dataset_training():
    """
    Обучение на полном датасете

    max_samples=None означает использование всех данных
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/sft_full",

        # Использовать все данные
        "max_samples": None,  # None = использовать все данные

        "num_epochs": 3,
        "batch_size": 4,
        "learning_rate": 5e-5,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }

    print("Обучение на полном датасете:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: все данные (max_samples=None)")
    print(f"  Эпох обучения: {config['num_epochs']}")
    print(f"  Ожидаемое число образцов: ~7500 (обучающий набор GSM8K)")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Обучение завершено!")

    return config


# ============================================================================
# Пример 4: Сравнение разных скоростей обучения
# ============================================================================

def compare_learning_rates():
    """
    Сравнение эффекта разных скоростей обучения

    Часто используемые значения learning rate:
    - 1e-5: консервативный, для дотонкой уже хорошей модели
    - 5e-5: рекомендуемый, баланс скорости и стабильности
    - 1e-4: агрессивный, для быстрых экспериментов
    """
    learning_rates = {
        "Консервативный (1e-5)": 1e-5,
        "Рекомендуемый (5e-5)": 5e-5,
        "Агрессивный (1e-4)": 1e-4,
    }

    print("Сравнение различных скоростей обучения:")
    for name, lr in learning_rates.items():
        print(f"\n{name}:")
        print(f"  learning_rate: {lr}")
        print(f"  Применение: ", end="")
        if lr == 1e-5:
            print("модель уже хороша, нужна лишь дотонкая настройка")
        elif lr == 5e-5:
            print("стандартное обучение, рекомендуется")
        else:
            print("быстрый эксперимент (возможна нестабильность)")

    # Пример обучения
    print("\nПример обучения (рекомендуемый learning rate):")
    tool = RLTrainingTool()
    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "max_samples": 1000,
        "num_epochs": 3,
        "learning_rate": 5e-5,
        "use_lora": True,
    }
    print(f"  learning_rate: {config['learning_rate']}")

    # result = tool.run(config)

    return learning_rates


# ============================================================================
# Пример 5: Конфигурация с оптимизацией видеопамяти
# ============================================================================

def memory_optimized_training():
    """
    Конфигурация с оптимизацией видеопамяти

    Применяется при ограниченной видеопамяти:
    - Используем LoRA
    - Уменьшаем batch size
    - Используем меньший ранг LoRA
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/sft_memory_opt",

        # Оптимизация видеопамяти
        "max_samples": 1000,
        "num_epochs": 3,
        "batch_size": 1,  # минимальный batch size
        "learning_rate": 5e-5,

        # Конфигурация LoRA
        "use_lora": True,
        "lora_r": 8,  # меньший ранг
        "lora_alpha": 16,
    }

    print("Конфигурация с оптимизацией видеопамяти:")
    print(f"  batch_size: {config['batch_size']} (минимальный)")
    print(f"  lora_r: {config['lora_r']} (уменьшен)")
    print(f"  use_lora: {config['use_lora']}")
    print(f"  Ожидаемое потребление видеопамяти: ~3-4 ГБ")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)

    return config


# ============================================================================
# Пример 6: Практический пример обучения
# ============================================================================

def practical_training_example():
    """
    Практический пример обучения — можно запустить напрямую
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/sft_practical",

        # Используем меньше образцов для быстрого теста
        "max_samples": 100,
        "num_epochs": 1,
        "batch_size": 4,
        "learning_rate": 5e-5,

        # Используем LoRA
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }

    print("Практический пример обучения:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: {config['max_samples']}")
    print(f"  Эпох обучения: {config['num_epochs']}")
    print(f"  Директория вывода: {config['output_dir']}")

    print("\n💡 Подсказка: раскомментируйте строки ниже, чтобы начать обучение")
    print("# result = tool.run(config)")
    print("# result_dict = json.loads(result)")
    print("# print(f'✅ Обучение завершено! Модель сохранена в: {result_dict[\"output_dir\"]}')")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Обучение завершено!")
    # print(f"📁 Модель сохранена в: {result_dict['output_dir']}")

    return config


# ============================================================================
# Главная функция
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Пример 1: Простейший пример SFT обучения")
    print("="*80)
    minimal_sft_training()

    print("\n" + "="*80)
    print("Пример 2: Стандартная конфигурация SFT обучения")
    print("="*80)
    standard_sft_training()

    print("\n" + "="*80)
    print("Пример 3: Обучение на полном датасете")
    print("="*80)
    full_dataset_training()

    print("\n" + "="*80)
    print("Пример 4: Сравнение разных скоростей обучения")
    print("="*80)
    compare_learning_rates()

    print("\n" + "="*80)
    print("Пример 5: Конфигурация с оптимизацией видеопамяти")
    print("="*80)
    memory_optimized_training()

    print("\n" + "="*80)
    print("Пример 6: Практический пример обучения")
    print("="*80)
    practical_training_example()
