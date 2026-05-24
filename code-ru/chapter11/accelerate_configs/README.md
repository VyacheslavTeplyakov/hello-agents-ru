# Описание конфигурационных файлов Accelerate

В этой папке находятся конфигурационные файлы Accelerate для распределённого обучения.

## Список конфигурационных файлов

### 1. multi_gpu_ddp.yaml
**Параллелизм данных (DDP)** — самый простой способ обучения на нескольких GPU

- **Применение**: один сервер с несколькими GPU (2–8 карт)
- **Преимущества**: просто, быстро
- **Недостатки**: каждый GPU требует полную копию модели
- **Требования к памяти**: как при обучении на одном GPU

**Способ запуска**:
```bash
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml train_script.py
```

### 2. deepspeed_zero2.yaml
**DeepSpeed ZeRO-2** — шардинг состояния оптимизатора

- **Применение**: модели среднего размера (1B–7B)
- **Преимущества**: снижает потребление видеопамяти, поддерживает больший batch size
- **Недостатки**: немного медленнее DDP
- **Экономия памяти**: ~30%

**Способ запуска**:
```bash
accelerate launch --config_file accelerate_configs/deepspeed_zero2.yaml train_script.py
```

### 3. deepspeed_zero3.yaml
**DeepSpeed ZeRO-3** — полный шардинг модели

- **Применение**: большие модели (>7B)
- **Преимущества**: максимальное снижение потребления видеопамяти
- **Недостатки**: значительные накладные расходы на коммуникацию
- **Экономия памяти**: ~50%

**Способ запуска**:
```bash
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml train_script.py
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install accelerate deepspeed
```

### 2. Настройка Accelerate

**Способ 1: использование конфигурационного файла** (рекомендуется)
```bash
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml your_script.py
```

**Способ 2: интерактивная настройка**
```bash
accelerate config
```

**Способ 3: аргументы командной строки**
```bash
accelerate launch --num_processes 4 --mixed_precision fp16 your_script.py
```

### 3. Запуск обучения

```bash
# DDP-обучение (4 GPU)
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml 07_distributed_training.py

# DeepSpeed ZeRO-2-обучение (4 GPU)
accelerate launch --config_file accelerate_configs/deepspeed_zero2.yaml 07_distributed_training.py

# DeepSpeed ZeRO-3-обучение (4 GPU)
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml 07_distributed_training.py
```

## Описание параметров конфигурации

### Общие параметры

- `compute_environment`: вычислительная среда (LOCAL_MACHINE/AMAZON_SAGEMAKER и др.)
- `distributed_type`: тип распределения (MULTI_GPU/DEEPSPEED/FSDP и др.)
- `num_processes`: общее кол-во процессов (обычно равно кол-ву GPU)
- `machine_rank`: номер машины (главный узел — 0)
- `num_machines`: кол-во машин
- `gpu_ids`: используемые GPU (all — использовать все GPU)
- `mixed_precision`: смешанная точность обучения (no/fp16/bf16)

### Параметры DeepSpeed

- `zero_stage`: уровень оптимизации ZeRO (1/2/3)
  - ZeRO-1: шардинг состояния оптимизатора
  - ZeRO-2: шардинг состояния оптимизатора + градиентов
  - ZeRO-3: шардинг состояния оптимизатора + градиентов + параметров модели

- `offload_optimizer_device`: устройство для выгрузки состояния оптимизатора (none/cpu/nvme)
- `offload_param_device`: устройство для выгрузки параметров модели (none/cpu/nvme)
- `gradient_accumulation_steps`: шаги накопления градиентов
- `gradient_clipping`: порог обрезки градиентов
- `zero3_init_flag`: флаг инициализации ZeRO-3

## Рекомендации по настройке производительности

### 1. Настройка Batch Size

При распределённом обучении: общий batch size = `per_device_batch_size × num_gpus × gradient_accumulation_steps`

**Пример**:
```python
# Один GPU: batch_size=4, gradient_accumulation=4, итого batch=16
# 4 GPU DDP: batch_size=4, gradient_accumulation=1, итого batch=16
```

### 2. Масштабирование скорости обучения

Используй линейное правило масштабирования:
```python
lr_new = lr_base × sqrt(total_batch_size_new / total_batch_size_base)
```

### 3. Смешанная точность обучения

- **fp16**: подходит для большинства сценариев, работает быстро
- **bf16**: подходит для архитектуры Ampere (A100/A6000), лучше численная стабильность
- **no**: без смешанной точности — максимальная точность, но медленнее

### 4. Накопление градиентов

При нехватке видеопамяти увеличь `gradient_accumulation_steps`:
```yaml
deepspeed_config:
  gradient_accumulation_steps: 8  # увеличить шаги накопления
```

## Частые вопросы

### Q1: Как посмотреть текущую конфигурацию?

```bash
accelerate env
```

### Q2: Скорость обучения на нескольких GPU не растёт линейно?

**Возможные причины**:
- Большие накладные расходы на коммуникацию
- Узкое место при загрузке данных
- Слишком маленький batch size

**Решения**:
- Увеличить batch size
- Использовать более быстрый загрузчик данных
- Проверить пропускную способность сети

### Q3: Обучение с DeepSpeed зависает?

**Возможные причины**:
- Проблема инициализации модели
- Таймаут коммуникации

**Решения**:
```bash
# Включить отладочные логи
export ACCELERATE_LOG_LEVEL=INFO
export NCCL_DEBUG=INFO

# Увеличить таймаут
export NCCL_TIMEOUT=1800
```

### Q4: Как обучать на нескольких узлах?

1. Установить одинаковое окружение на всех узлах
2. Настроить SSH без пароля
3. Изменить `num_machines` и `main_process_ip` в конфигурационном файле
4. Запустить одну и ту же команду на каждом узле

## Полезные ресурсы

- [Документация Accelerate](https://huggingface.co/docs/accelerate)
- [Документация DeepSpeed](https://www.deepspeed.ai/)
- [Руководство по распределённому обучению TRL](https://huggingface.co/docs/trl/customization)
