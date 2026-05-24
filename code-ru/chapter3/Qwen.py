# Добавляем HF_ENDPOINT во избежание ошибки Connection aborted.
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Указываем идентификатор модели
model_id = "Qwen/Qwen1.5-0.5B-Chat"

# Настройка устройства, приоритет у GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Используемое устройство: {device}")

# Загружаем токенизатор
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Загружаем модель и перемещаем её на указанное устройство
model = AutoModelForCausalLM.from_pretrained(model_id).to(device)

print("Модель и токенизатор загружены!")

# Подготовка диалогового ввода
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Привет, расскажи о себе."}
]

# Форматируем ввод с помощью шаблона токенизатора
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# Кодируем входной текст
model_inputs = tokenizer([text], return_tensors="pt").to(device)

print("Закодированный входной текст:")
print(model_inputs)

# Используем модель для генерации ответа
# max_new_tokens ограничивает максимальное количество новых токенов, которые может сгенерировать модель
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512
)

# Обрезаем сгенерированные ID токенов, убирая входную часть
# Таким образом декодируем только новую часть, сгенерированную моделью
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

# Декодируем сгенерированные ID токенов
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("\nОтвет модели:")
print(response)
