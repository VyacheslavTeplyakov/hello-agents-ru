"""
Пример 5: Полный пайплайн GRPO обучения

Демонстрирует обучение с подкреплением методом GRPO с помощью RLTrainingTool
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# Пример 1: Минимальный пример GRPO обучения
# ============================================================================

def minimal_grpo_training():
    """
    Простейший пример GRPO обучения

    Достаточно одного вызова RLTrainingTool
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/grpo_minimal",
        "max_samples": 10,
        "num_epochs": 1,
    }

    print("Простейший пример GRPO обучения:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: {config['max_samples']}")
    print(f"  Эпох обучения: {config['num_epochs']}")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ Обучение завершено! Модель сохранена в: {result_dict['output_dir']}")

    return config


# ============================================================================
# Пример 2: Стандартная конфигурация GRPO обучения
# ============================================================================

def standard_grpo_training():
    """
    Стандартная конфигурация GRPO обучения

    Обычно GRPO применяется поверх SFT модели
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "grpo",

        # Конфигурация модели — можно использовать модель после SFT
        "model_name": "Qwen/Qwen3-0.6B",  # или "./output/sft_standard"
        "output_dir": "./output/grpo_standard",

        # Конфигурация данных
        "max_samples": 500,  # для GRPO обычно используют меньше образцов

        # Конфигурация обучения
        "num_epochs": 3,
        "batch_size": 2,  # GRPO требует больше видеопамяти
        "learning_rate": 1e-5,  # в 10 раз меньше, чем при SFT

        # Конфигурация LoRA
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }

    print("Стандартная конфигурация GRPO обучения:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: {config['max_samples']}")
    print(f"  Эпох обучения: {config['num_epochs']}")
    print(f"  batch_size: {config['batch_size']}")
    print(f"  learning_rate: {config['learning_rate']} (меньше, чем при SFT)")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ GRPO обучение завершено!")

    return config


# ============================================================================
# Пример 3: Обучение на полном датасете
# ============================================================================

def full_dataset_training():
    """
    Обучение GRPO на полном датасете
    """
    tool = RLTrainingTool()

    config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/grpo_full",

        # Использовать все данные
        "max_samples": None,  # None = использовать все данные

        "num_epochs": 3,
        "batch_size": 2,
        "learning_rate": 1e-5,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }

    print("GRPO обучение на полном датасете:")
    print(f"  Модель: {config['model_name']}")
    print(f"  Образцов: все данные (max_samples=None)")
    print(f"  Эпох обучения: {config['num_epochs']}")
    print(f"  Ожидаемое число образцов: ~7500 (обучающий набор GSM8K)")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)

    return config


# ============================================================================
# Пример 4: Полный пайплайн SFT + GRPO
# ============================================================================

def complete_sft_grpo_pipeline():
    """
    Полный пайплайн обучения SFT + GRPO

    Шаги:
    1. SFT обучение — изучение базового формата
    2. GRPO обучение — улучшение способности к рассуждениям
    """
    tool = RLTrainingTool()

    # Шаг 1: SFT обучение
    print("Шаг 1: SFT обучение")
    sft_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/pipeline_sft",
        "max_samples": 1000,
        "num_epochs": 3,
        "batch_size": 4,
        "use_lora": True,
    }

    print(f"  Модель: {sft_config['model_name']}")
    print(f"  Образцов: {sft_config['max_samples']}")

    # Раскомментируйте для фактического обучения
    # sft_result = tool.run(sft_config)
    # print(f"✅ SFT обучение завершено: {sft_config['output_dir']}")

    # Шаг 2: GRPO обучение
    print("\nШаг 2: GRPO обучение")
    grpo_config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "./output/pipeline_sft",  # используем SFT модель
        "output_dir": "./output/pipeline_grpo",
        "max_samples": 500,
        "num_epochs": 3,
        "batch_size": 2,
        "learning_rate": 1e-5,
        "use_lora": True,
    }

    print(f"  Базовая модель: {grpo_config['model_name']}")
    print(f"  Образцов: {grpo_config['max_samples']}")

    # Раскомментируйте для фактического обучения
    # grpo_result = tool.run(grpo_config)
    # print(f"✅ GRPO обучение завершено: {grpo_config['output_dir']}")

    print("\n💡 Для инференса рекомендуется использовать GRPO модель")

    return sft_config, grpo_config


# ============================================================================
# Пример 5: Использование различных функций вознаграждения
# ============================================================================

def using_different_rewards():
    """
    GRPO по умолчанию использует функцию вознаграждения за точность

    Поведение можно изменить, создав пользовательскую функцию вознаграждения
    """
    print("Функции вознаграждения GRPO:")
    print("\nФункция вознаграждения по умолчанию: вознаграждение за точность")
    print("  - Правильный ответ: 1.0")
    print("  - Неправильный ответ: 0.0")

    print("\nДругие доступные функции вознаграждения:")
    print("  1. Штраф за длину: поощряет краткие ответы")
    print("  2. Пошаговое вознаграждение: поощряет детальные рассуждения")
    print("  3. Пользовательское вознаграждение: настраивается под задачу")

    print("\nПример создания функции вознаграждения:")
    tool = RLTrainingTool()

    # Создание функции вознаграждения за точность
    accuracy_config = {
        "action": "create_reward",
        "reward_type": "accuracy"
    }
    print("\n1. Вознаграждение за точность:")
    print(f"   Конфигурация: {accuracy_config}")

    # Создание функции вознаграждения со штрафом за длину
    length_config = {
        "action": "create_reward",
        "reward_type": "length_penalty",
        "penalty_weight": 0.001
    }
    print("\n2. Вознаграждение со штрафом за длину:")
    print(f"   Конфигурация: {length_config}")

    # Создание пошаговой функции вознаграждения
    step_config = {
        "action": "create_reward",
        "reward_type": "step",
        "step_bonus": 0.1
    }
    print("\n3. Пошаговое вознаграждение:")
    print(f"   Конфигурация: {step_config}")

    return accuracy_config, length_config, step_config


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
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/grpo_practical",

        # Используем меньше образцов для быстрого теста
        "max_samples": 50,
        "num_epochs": 1,
        "batch_size": 2,
        "learning_rate": 1e-5,

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
    print("Пример 1: Простейший пример GRPO обучения")
    print("="*80)
    minimal_grpo_training()

    print("\n" + "="*80)
    print("Пример 2: Стандартная конфигурация GRPO обучения")
    print("="*80)
    standard_grpo_training()

    print("\n" + "="*80)
    print("Пример 3: Обучение на полном датасете")
    print("="*80)
    full_dataset_training()

    print("\n" + "="*80)
    print("Пример 4: Полный пайплайн SFT + GRPO")
    print("="*80)
    complete_sft_grpo_pipeline()

    print("\n" + "="*80)
    print("Пример 5: Использование различных функций вознаграждения")
    print("="*80)
    using_different_rewards()

    print("\n" + "="*80)
    print("Пример 6: Практический пример обучения")
    print("="*80)
    practical_training_example()
