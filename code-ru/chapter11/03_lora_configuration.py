"""
Пример 3: Конфигурация и использование LoRA
Демонстрирует настройку и применение LoRA для эффективной по параметрам тонкой настройки
через RLTrainingTool
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# Пример 1: Базовая конфигурация LoRA
# ============================================================================

def basic_lora_config():
    """
    Простейшая конфигурация LoRA

    LoRA (Low-Rank Adaptation):
    - Обучается лишь небольшое число дополнительных параметров
    - Снижает потребление видеопамяти на 60-80%
    - Ускоряет обучение в 2-3 раза
    - Файл модели занимает всего ~10 МБ
    """
    tool = RLTrainingTool()

    # SFT обучение с RLTrainingTool с включённым LoRA
    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/lora_basic",
        "max_samples": 100,
        "num_epochs": 1,

        # Конфигурация LoRA
        "use_lora": True,           # включить LoRA
        "lora_r": 16,               # ранг LoRA (rank)
        "lora_alpha": 32,           # коэффициент масштабирования (обычно 2×r)
    }

    print("Базовая конфигурация LoRA:")
    print(f"  Модель: {config['model_name']}")
    print(f"  use_lora: {config['use_lora']}")
    print(f"  lora_r: {config['lora_r']}")
    print(f"  lora_alpha: {config['lora_alpha']}")
    print(f"  Целевые модули: ['q_proj', 'v_proj'] (по умолчанию)")

    # Раскомментируйте для фактического обучения
    # result = tool.run(config)
    # print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))

    return config


# ============================================================================
# Пример 2: Сравнение разных рангов LoRA
# ============================================================================

def compare_lora_ranks():
    """
    Сравнение конфигураций с разными рангами LoRA

    Выбор ранга LoRA (r):
    - r=8: меньше параметров, подходит для быстрых экспериментов
    - r=16: рекомендуемое значение, баланс производительности и эффективности
    - r=32: больше параметров, для достижения лучшей точности
    """
    configs = {
        "r=8 (быстрый эксперимент)": {
            "lora_r": 8,
            "lora_alpha": 16,
            "params": "~16K"
        },
        "r=16 (рекомендуется)": {
            "lora_r": 16,
            "lora_alpha": 32,
            "params": "~32K"
        },
        "r=32 (высокая точность)": {
            "lora_r": 32,
            "lora_alpha": 64,
            "params": "~65K"
        },
    }

    print("Сравнение различных рангов LoRA:")
    for name, config in configs.items():
        print(f"\n{name}:")
        print(f"  lora_r: {config['lora_r']}")
        print(f"  lora_alpha: {config['lora_alpha']}")
        print(f"  Примерное число параметров: {config['params']}")

    # Пример обучения
    print("\nПример обучения (r=16):")
    print("""
    tool = RLTrainingTool()
    result = tool.run({
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "max_samples": 100,
        "num_epochs": 1,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    })
    """)

    return configs


# ============================================================================
# Пример 3: Сравнение LoRA и полной тонкой настройки
# ============================================================================

def compare_lora_vs_full_finetuning():
    """
    Сравнение конфигураций LoRA и полной тонкой настройки
    """
    print("Сравнение LoRA и полной тонкой настройки:")
    print("\nLoRA тонкая настройка:")
    print("  Видеопамять: ~4 ГБ (модель 0.5B)")
    print("  Скорость обучения: быстро (2-3x)")
    print("  Размер модели: ~10 МБ")
    print("  batch_size: 8")
    print("  use_lora: True")

    print("\nПолная тонкая настройка:")
    print("  Видеопамять: ~14 ГБ (модель 0.5B)")
    print("  Скорость обучения: медленно")
    print("  Размер модели: ~1 ГБ")
    print("  batch_size: 2")
    print("  use_lora: False")

    print("\nРекомендация: используйте LoRA для тонкой настройки")


# ============================================================================
# Пример 4: Примеры практических конфигураций обучения
# ============================================================================

def practical_training_configs():
    """
    Рекомендуемые конфигурации для практического обучения
    """
    tool = RLTrainingTool()

    # Конфигурация для быстрого обучения
    quick_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test",
        "max_samples": 100,
        "num_epochs": 1,
        "batch_size": 8,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
    }

    # Стандартная конфигурация обучения
    standard_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/standard",
        "max_samples": 1000,
        "num_epochs": 3,
        "batch_size": 4,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
        "learning_rate": 5e-5,
    }

    # Конфигурация для высококачественного обучения
    high_quality_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/high_quality",
        "max_samples": None,  # использовать все данные
        "num_epochs": 5,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 32,
        "lora_alpha": 64,
        "learning_rate": 3e-5,
    }

    print("Примеры практических конфигураций обучения:")
    print("\n1. Конфигурация для быстрого эксперимента:")
    print(f"   Образцов: {quick_config['max_samples']}")
    print(f"   epochs: {quick_config['num_epochs']}")
    print(f"   lora_r: {quick_config['lora_r']}")
    print(f"   batch_size: {quick_config['batch_size']}")

    print("\n2. Стандартная конфигурация обучения:")
    print(f"   Образцов: {standard_config['max_samples']}")
    print(f"   epochs: {standard_config['num_epochs']}")
    print(f"   lora_r: {standard_config['lora_r']}")
    print(f"   batch_size: {standard_config['batch_size']}")

    print("\n3. Конфигурация для высококачественного обучения:")
    print(f"   Образцов: все данные (max_samples=None)")
    print(f"   epochs: {high_quality_config['num_epochs']}")
    print(f"   lora_r: {high_quality_config['lora_r']}")
    print(f"   batch_size: {high_quality_config['batch_size']}")

    # Раскомментируйте для фактического обучения
    # result = tool.run(quick_config)
    # print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))

    return quick_config, standard_config, high_quality_config


# ============================================================================
# Пример 5: Рекомендации по подбору параметров LoRA
# ============================================================================

def lora_tuning_guidelines():
    """
    Рекомендации по подбору параметров LoRA
    """
    guidelines = {
        "lora_r (ранг)": {
            "Рекомендуемое значение": 16,
            "Диапазон": "8-32",
            "Описание": "Чем больше — тем лучше точность, но больше параметров и времени обучения",
            "Рекомендации по выбору": {
                "Быстрый эксперимент": 8,
                "Баланс производительности": 16,
                "Максимальная точность": 32,
            }
        },
        "lora_alpha (коэффициент масштабирования)": {
            "Рекомендуемое значение": 32,
            "Диапазон": "16-64",
            "Описание": "Обычно устанавливается как 2×lora_r",
            "Формула": "lora_alpha = 2 * lora_r"
        },
        "max_samples (число образцов)": {
            "Быстрый эксперимент": 100,
            "Стандартное обучение": 1000,
            "Полное обучение": "None (все данные)",
            "Описание": "None означает использование всех данных",
        },
    }

    print("Рекомендации по подбору параметров LoRA:")
    for param, info in guidelines.items():
        print(f"\n{param}:")
        for key, value in info.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  {key}: {value}")

    return guidelines


# ============================================================================
# Главная функция
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Пример 1: Базовая конфигурация LoRA")
    print("="*80)
    basic_lora_config()

    print("\n" + "="*80)
    print("Пример 2: Сравнение разных рангов LoRA")
    print("="*80)
    compare_lora_ranks()

    print("\n" + "="*80)
    print("Пример 3: Сравнение LoRA и полной тонкой настройки")
    print("="*80)
    compare_lora_vs_full_finetuning()

    print("\n" + "="*80)
    print("Пример 4: Примеры практических конфигураций обучения")
    print("="*80)
    practical_training_configs()

    print("\n" + "="*80)
    print("Пример 5: Рекомендации по подбору параметров LoRA")
    print("="*80)
    lora_tuning_guidelines()
