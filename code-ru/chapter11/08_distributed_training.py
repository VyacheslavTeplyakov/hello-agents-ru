"""
Пример распределённого обучения

Этот скрипт демонстрирует, как использовать Accelerate для распределённого обучения.
Сам код обучения изменять не нужно — достаточно запустить его через accelerate launch.

Способы запуска:
1. Обучение на одном GPU:
   python 07_distributed_training.py

2. Обучение на нескольких GPU (DDP):
   accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml 07_distributed_training.py

3. Обучение с DeepSpeed ZeRO-2:
   accelerate launch --config_file accelerate_configs/deepspeed_zero2.yaml 07_distributed_training.py

4. Обучение с DeepSpeed ZeRO-3:
   accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml 07_distributed_training.py
"""

import sys
import os

# Добавляем HelloAgents в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "HelloAgents"))

from hello_agents.tools import RLTrainingTool
import json

def main():
    print("="*80)
    print("Пример распределённого обучения")
    print("="*80)

    # Определяем окружение для распределённого обучения
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0))

    if world_size > 1:
        print(f"\n🚀 Режим распределённого обучения")
        print(f"   - Всего процессов: {world_size}")
        print(f"   - Текущий процесс: {local_rank}")
        print(f"   - Бэкенд: {os.environ.get('ACCELERATE_DISTRIBUTED_TYPE', 'MULTI_GPU')}")
    else:
        print(f"\n💻 Режим обучения на одном GPU")

    print("="*80)

    # Создаём инструмент обучения
    rl_tool = RLTrainingTool()

    # Конфигурация обучения
    # Примечание: batch_size — это размер батча на один GPU
    # Общий batch size = batch_size × num_gpus × gradient_accumulation_steps
    config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./models/grpo_distributed",
        "max_samples": 200,  # используем 200 примеров
        "num_epochs": 2,
        "batch_size": 2,  # размер батча на один GPU
        "use_lora": True,
        "use_wandb": False,
        "use_tensorboard": True,
    }

    # Выводим конфигурацию только на главном процессе
    if local_rank == 0:
        print("\nКонфигурация обучения:")
        print(f"  - Модель: {config['model_name']}")
        print(f"  - Кол-во примеров: {config['max_samples']}")
        print(f"  - Кол-во эпох: {config['num_epochs']}")
        print(f"  - Размер батча на GPU: {config['batch_size']}")
        if world_size > 1:
            total_batch = config['batch_size'] * world_size
            print(f"  - Общий размер батча: {total_batch}")
        print("="*80)

    # Запускаем обучение
    # Код обучения не требует никаких изменений!
    # Accelerate автоматически берёт на себя все детали распределённого обучения
    result = rl_tool.run(config)

    # Выводим результаты только на главном процессе
    if local_rank == 0:
        result_data = json.loads(result)
        print("\n" + "="*80)
        print("Обучение завершено!")
        print("="*80)
        print(f"Статус: {result_data['status']}")
        print(f"Путь к модели: {result_data['output_dir']}")
        print("="*80)

        # Выводим советы по производительности
        if world_size > 1:
            print(f"\n💡 Совет по производительности:")
            print(f"   Использовалось {world_size} GPU для обучения")
            print(f"   Теоретическое ускорение: ~{world_size * 0.85:.1f}x")
            print(f"   (Реальное ускорение зависит от накладных расходов на коммуникацию и загрузку данных)")

if __name__ == "__main__":
    main()
