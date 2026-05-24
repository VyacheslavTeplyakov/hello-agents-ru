"""
Полный пайплайн Agentic RL обучения (обновлённая версия)
Сквозной пример от подготовки данных до развёртывания модели

Что изменилось:
1. Исправлена проблема с парсингом JSON
2. Добавлена конфигурация мониторинга обучения (wandb/tensorboard)
3. Поддержка детального вывода логов
"""

import sys
import os

# Добавляем HelloAgents в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "HelloAgents"))

from hello_agents.tools import RLTrainingTool
import json
from datetime import datetime

class AgenticRLPipeline:
    """Пайплайн обучения Agentic RL"""

    def __init__(self, config_path="config.json"):
        """
        Инициализация пайплайна обучения

        Args:
            config_path: путь к файлу конфигурации
        """
        self.rl_tool = RLTrainingTool()
        self.config = self.load_config(config_path)
        self.results = {}

    def load_config(self, config_path):
        """Загрузка файла конфигурации"""
        with open(config_path, 'r') as f:
            return json.load(f)

    def log(self, message):
        """Запись в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def stage1_prepare_data(self):
        """Этап 1: Подготовка данных"""
        self.log("=" * 50)
        self.log("Этап 1: Подготовка данных")
        self.log("=" * 50)

        # Загружаем и проверяем датасет
        result = self.rl_tool.run({
            "action": "load_dataset",
            "format": "sft",
            "max_samples": self.config["data"]["max_samples"],
        })

        # Парсим JSON результат
        dataset_info = json.loads(result)

        self.log(f"✓ Датасет успешно загружен")
        self.log(f"  - Образцов: {dataset_info['dataset_size']}")
        self.log(f"  - Формат: {dataset_info['format']}")
        self.log(f"  - Столбцы данных: {', '.join(dataset_info['sample_keys'])}")

        self.results["data"] = dataset_info

        return dataset_info

    def stage2_sft_training(self):
        """Этап 2: SFT обучение"""
        self.log("\n" + "=" * 50)
        self.log("Этап 2: SFT обучение")
        self.log("=" * 50)

        sft_config = self.config["sft"]

        result = self.rl_tool.run({
            "action": "train",
            "algorithm": "sft",
            "model_name": self.config["model"]["base_model"],
            "output_dir": sft_config["output_dir"],
            "max_samples": self.config["data"]["max_samples"],
            "num_epochs": sft_config["num_epochs"],
            "batch_size": sft_config["batch_size"],
            "use_lora": True,
            # Конфигурация мониторинга обучения
            "use_wandb": self.config.get("monitoring", {}).get("use_wandb", False),
            "use_tensorboard": self.config.get("monitoring", {}).get("use_tensorboard", True),
            "wandb_project": self.config.get("monitoring", {}).get("wandb_project", None),
        })

        # Парсим JSON результат
        result_data = json.loads(result)

        self.log(f"✓ SFT обучение завершено")
        self.log(f"  - Путь к модели: {result_data['output_dir']}")
        self.log(f"  - Статус: {result_data['status']}")

        self.results["sft_training"] = result_data

        return result_data["output_dir"]

    def stage3_sft_evaluation(self, model_path):
        """Этап 3: Оценка SFT модели"""
        self.log("\n" + "=" * 50)
        self.log("Этап 3: Оценка SFT модели")
        self.log("=" * 50)

        result = self.rl_tool.run({
            "action": "evaluate",
            "model_path": model_path,
            "max_samples": self.config["eval"]["max_samples"],
            "use_lora": True,
        })
        eval_data = json.loads(result)

        self.log(f"✓ Оценка SFT завершена")
        self.log(f"  - Точность: {eval_data['accuracy']}")
        self.log(f"  - Среднее вознаграждение: {eval_data['average_reward']}")

        self.results["sft_evaluation"] = eval_data

        return eval_data

    def stage4_grpo_training(self, sft_model_path):
        """Этап 4: GRPO обучение"""
        self.log("\n" + "=" * 50)
        self.log("Этап 4: GRPO обучение")
        self.log("=" * 50)

        grpo_config = self.config["grpo"]

        result = self.rl_tool.run({
            "action": "train",
            "algorithm": "grpo",
            "model_name": sft_model_path,
            "output_dir": grpo_config["output_dir"],
            "max_samples": self.config["data"]["max_samples"],
            "num_epochs": grpo_config["num_epochs"],
            "batch_size": grpo_config["batch_size"],
            "use_lora": True,
            # Конфигурация мониторинга обучения
            "use_wandb": self.config.get("monitoring", {}).get("use_wandb", False),
            "use_tensorboard": self.config.get("monitoring", {}).get("use_tensorboard", True),
            "wandb_project": self.config.get("monitoring", {}).get("wandb_project", None),
        })

        # Парсим JSON результат
        result_data = json.loads(result)

        self.log(f"✓ GRPO обучение завершено")
        self.log(f"  - Путь к модели: {result_data['output_dir']}")
        self.log(f"  - Статус: {result_data['status']}")

        self.results["grpo_training"] = result_data

        return result_data["output_dir"]

    def stage5_grpo_evaluation(self, model_path):
        """Этап 5: Оценка GRPO модели"""
        self.log("\n" + "=" * 50)
        self.log("Этап 5: Оценка GRPO модели")
        self.log("=" * 50)

        result = self.rl_tool.run({
            "action": "evaluate",
            "model_path": model_path,
            "max_samples": self.config["eval"]["max_samples"],
            "use_lora": True,
        })
        eval_data = json.loads(result)

        self.log(f"✓ Оценка GRPO завершена")
        self.log(f"  - Точность: {eval_data['accuracy']}")
        self.log(f"  - Среднее вознаграждение: {eval_data['average_reward']}")

        self.results["grpo_evaluation"] = eval_data

        return eval_data

    def stage6_save_results(self):
        """Этап 6: Сохранение результатов"""
        self.log("\n" + "=" * 50)
        self.log("Этап 6: Сохранение результатов")
        self.log("=" * 50)

        # Сохраняем результаты обучения
        results_path = "training_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.log(f"✓ Результаты сохранены в: {results_path}")

    def run(self):
        """Запуск полного пайплайна"""
        try:
            # Этап 1: Подготовка данных
            self.stage1_prepare_data()

            # Этап 2: SFT обучение
            sft_model_path = self.stage2_sft_training()

            # Этап 3: Оценка SFT модели
            self.stage3_sft_evaluation(sft_model_path)

            # Этап 4: GRPO обучение
            grpo_model_path = self.stage4_grpo_training(sft_model_path)

            # Этап 5: Оценка GRPO модели
            self.stage5_grpo_evaluation(grpo_model_path)

            # Этап 6: Сохранение результатов
            self.stage6_save_results()

            self.log("\n" + "=" * 50)
            self.log("✓ Пайплайн обучения завершён!")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"\n✗ Ошибка обучения: {str(e)}")
            raise

# Пример использования
if __name__ == "__main__":
    # Создаём файл конфигурации
    config = {
        "model": {
            "base_model": "Qwen/Qwen3-0.6B"
        },
        "data": {
            "max_samples": 100  # используем 100 образцов для быстрого теста
        },
        "sft": {
            "output_dir": "./models/sft_model",
            "num_epochs": 2,
            "batch_size": 4,
        },
        "grpo": {
            "output_dir": "./models/grpo_model",
            "num_epochs": 2,
            "batch_size": 2,
        },
        "eval": {
            "max_samples": 20,
            "sft_accuracy_threshold": 0.40
        },
        "monitoring": {
            "use_wandb": False,        # использовать ли Wandb
            "use_tensorboard": True,   # использовать ли TensorBoard
            "wandb_project": "agentic-rl-pipeline"  # название проекта в Wandb
        }
    }

    # Сохраняем конфигурацию
    with open("config.json", 'w') as f:
        json.dump(config, f, indent=2)

    # Запускаем пайплайн обучения
    pipeline = AgenticRLPipeline("config.json")
    pipeline.run()
