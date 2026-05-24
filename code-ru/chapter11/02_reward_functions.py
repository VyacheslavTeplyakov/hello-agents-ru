"""
Пример 2: Проектирование и использование функций вознаграждения
Демонстрирует создание и тестирование функций вознаграждения с помощью RLTrainingTool
"""

import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# Пример 1: Создание функции вознаграждения за точность
# ============================================================================

def create_accuracy_reward():
    """
    Создание функции вознаграждения за точность

    Правила вознаграждения:
    - Правильный ответ: 1.0
    - Неправильный ответ: 0.0
    """
    tool = RLTrainingTool()

    config = {
        "action": "create_reward",
        "reward_type": "accuracy"
    }

    print("Создаём функцию вознаграждения за точность...")
    result = tool.run(config)
    result_dict = json.loads(result)

    print(f"✅ Тип функции вознаграждения: {result_dict['reward_type']}")
    print(f"📋 Описание: {result_dict['description']}")

    return result_dict


# ============================================================================
# Пример 2: Создание функции вознаграждения со штрафом за длину
# ============================================================================

def create_length_penalty_reward():
    """
    Создание функции вознаграждения со штрафом за длину

    Правила вознаграждения:
    - Базовое вознаграждение (точность)
    - Минус штраф за длину (поощряет лаконичность)
    """
    tool = RLTrainingTool()

    config = {
        "action": "create_reward",
        "reward_type": "length_penalty",
        "penalty_weight": 0.001,  # штраф 0.001 за каждый токен
        "max_length": 512
    }

    print("Создаём функцию вознаграждения со штрафом за длину...")
    result = tool.run(config)
    result_dict = json.loads(result)

    print(f"✅ Тип функции вознаграждения: {result_dict['reward_type']}")
    print(f"📋 Вес штрафа: {result_dict.get('penalty_weight', 0.001)}")
    print(f"📋 Максимальная длина: {result_dict.get('max_length', 512)}")

    return result_dict


# ============================================================================
# Пример 3: Создание пошаговой функции вознаграждения
# ============================================================================

def create_step_reward():
    """
    Создание пошаговой функции вознаграждения

    Правила вознаграждения:
    - Базовое вознаграждение (точность)
    - Плюс бонус за шаги (поощряет детальные рассуждения)
    """
    tool = RLTrainingTool()

    config = {
        "action": "create_reward",
        "reward_type": "step",
        "step_bonus": 0.1,  # дополнительное вознаграждение 0.1 за каждый шаг
        "max_steps": 10
    }

    print("Создаём пошаговую функцию вознаграждения...")
    result = tool.run(config)
    result_dict = json.loads(result)

    print(f"✅ Тип функции вознаграждения: {result_dict['reward_type']}")
    print(f"📋 Пошаговый бонус: {result_dict.get('step_bonus', 0.1)}")
    print(f"📋 Максимум шагов: {result_dict.get('max_steps', 10)}")

    return result_dict


# ============================================================================
# Пример 4: Тестирование функции вознаграждения
# ============================================================================

def test_reward_function():
    """
    Тестирование вычисления функции вознаграждения

    Прямое тестирование через MathRewardFunction
    """
    from hello_agents.rl import MathRewardFunction

    reward_fn = MathRewardFunction(tolerance=1e-4)

    # Тестовые примеры
    test_cases = [
        {
            "completion": "Let me calculate: 2+2=4. Final Answer: 4",
            "ground_truth": "4",
            "expected": 1.0
        },
        {
            "completion": "I think 2+2=5. Final Answer: 5",
            "ground_truth": "4",
            "expected": 0.0
        },
        {
            "completion": "The answer is 4",
            "ground_truth": "4",
            "expected": 1.0
        },
        {
            "completion": "2+2 equals four. #### 4",
            "ground_truth": "4",
            "expected": 1.0
        }
    ]

    print("Тестирование функции вознаграждения:")
    print("-" * 80)

    for i, case in enumerate(test_cases, 1):
        # Вычисляем вознаграждение
        rewards = reward_fn(
            completions=[case["completion"]],
            ground_truth=[case["ground_truth"]]
        )
        reward = rewards[0]

        print(f"\nТест {i}:")
        print(f"  Сгенерировано: {case['completion'][:50]}...")
        print(f"  Эталон: {case['ground_truth']}")
        print(f"  Вознаграждение: {reward:.2f} (ожидалось: {case['expected']:.2f})")
        print(f"  {'✅ Верно' if abs(reward - case['expected']) < 0.01 else '❌ Ошибка'}")

    return test_cases


# ============================================================================
# Пример 5: Тестирование извлечения ответа
# ============================================================================

def test_answer_extraction():
    """
    Тестирование функции извлечения ответа
    """
    from hello_agents.rl import MathRewardFunction

    reward_fn = MathRewardFunction()

    test_texts = [
        "Final Answer: 42",
        "The answer is 3.14",
        "#### 100",
        "So the result is 2.5",
        "Let me think... the answer should be 7",
        "42"
    ]

    print("Тест извлечения ответа:")
    print("-" * 80)

    for text in test_texts:
        answer = reward_fn.extract_answer(text)
        print(f"\nТекст: {text}")
        print(f"Извлечено: {answer if answer else '(не найдено)'}")

    return test_texts


# ============================================================================
# Пример 6: Тестирование сравнения ответов
# ============================================================================

def test_answer_comparison():
    """
    Тестирование функции сравнения ответов
    """
    from hello_agents.rl import MathRewardFunction

    reward_fn = MathRewardFunction(tolerance=0.01)

    test_pairs = [
        ("42", "42", True),
        ("3.14", "3.14159", False),  # за пределами допуска
        ("3.14", "3.141", True),     # в пределах допуска
        ("100", "100.0", True),
        ("2.5", "3.0", False),
        ("7", "7.00", True)
    ]

    print("Тест сравнения ответов:")
    print("-" * 80)

    for pred, truth, expected in test_pairs:
        is_correct = reward_fn.compare_answers(pred, truth)
        print(f"\nПредсказание: {pred}, Эталон: {truth}")
        print(f"Результат: {'верно' if is_correct else 'неверно'} (ожидалось: {'верно' if expected else 'неверно'})")
        print(f"{'✅ Пройден' if is_correct == expected else '❌ Не пройден'}")

    return test_pairs


# ============================================================================
# Пример 7: Сравнение различных функций вознаграждения
# ============================================================================

def compare_reward_functions():
    """
    Сравнение эффекта различных функций вознаграждения
    """
    from hello_agents.rl import (
        create_accuracy_reward,
        create_length_penalty_reward,
        create_step_reward
    )

    # Создаём разные функции вознаграждения
    accuracy_fn = create_accuracy_reward()
    base_fn = create_accuracy_reward()  # базовая функция вознаграждения
    length_fn = create_length_penalty_reward(base_fn, penalty_weight=0.001)
    step_fn = create_step_reward(base_fn, step_bonus=0.1)

    # Тестовые примеры
    test_cases = [
        {
            "completion": "4",
            "ground_truth": "4",
            "desc": "Краткий правильный ответ"
        },
        {
            "completion": "Step 1: 2+2=4\nFinal Answer: 4",
            "ground_truth": "4",
            "desc": "Правильный ответ с шагами"
        },
        {
            "completion": "Let me think... " * 20 + "Final Answer: 4",
            "ground_truth": "4",
            "desc": "Многословный правильный ответ"
        }
    ]

    print("Сравнение функций вознаграждения:")
    print("=" * 80)

    for i, case in enumerate(test_cases, 1):
        print(f"\nТест {i}: {case['desc']}")
        print(f"Длина: {len(case['completion'])} символов")

        # Вычисляем разные вознаграждения
        acc_reward = accuracy_fn([case["completion"]], ground_truth=[case["ground_truth"]])[0]
        len_reward = length_fn([case["completion"]], ground_truth=[case["ground_truth"]])[0]
        step_reward = step_fn([case["completion"]], ground_truth=[case["ground_truth"]])[0]

        print(f"  Вознаграждение за точность: {acc_reward:.4f}")
        print(f"  Вознаграждение со штрафом за длину: {len_reward:.4f}")
        print(f"  Пошаговое вознаграждение: {step_reward:.4f}")

    print("\nВыводы:")
    print("  - Вознаграждение за точность: учитывает только правильность ответа")
    print("  - Штраф за длину: поощряет краткие ответы")
    print("  - Пошаговое вознаграждение: поощряет детальные рассуждения")

    return test_cases


# ============================================================================
# Главная функция
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Пример 1: Создание функции вознаграждения за точность")
    print("="*80)
    create_accuracy_reward()

    print("\n" + "="*80)
    print("Пример 2: Создание функции вознаграждения со штрафом за длину")
    print("="*80)
    create_length_penalty_reward()

    print("\n" + "="*80)
    print("Пример 3: Создание пошаговой функции вознаграждения")
    print("="*80)
    create_step_reward()

    print("\n" + "="*80)
    print("Пример 4: Тестирование функции вознаграждения")
    print("="*80)
    test_reward_function()

    print("\n" + "="*80)
    print("Пример 5: Тестирование извлечения ответа")
    print("="*80)
    test_answer_extraction()

    print("\n" + "="*80)
    print("Пример 6: Тестирование сравнения ответов")
    print("="*80)
    test_answer_comparison()

    print("\n" + "="*80)
    print("Пример 7: Сравнение различных функций вознаграждения")
    print("="*80)
    compare_reward_functions()
