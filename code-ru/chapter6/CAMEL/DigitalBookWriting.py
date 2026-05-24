from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from dotenv import load_dotenv
import os

load_dotenv()
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

# Создаём модель; здесь для примера используется Qwen через платформу Bailian
model = ModelFactory.create(
    model_platform=ModelPlatformType.QWEN,
    model_type=LLM_MODEL,
    url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)

# Определяем задачу совместной работы
task_prompt = """
Написать короткую электронную книгу о «психологии прокрастинации» для широкой аудитории, интересующейся психологией.
Требования:
1. Содержание научно обоснованное, основанное на эмпирических исследованиях
2. Язык доступный, без избыточной профессиональной терминологии
3. Включать практические советы по улучшению и разбор случаев
4. Объём — 8000–10000 слов
5. Чёткая структура: введение, основные главы и заключение
"""

print(Fore.YELLOW + f"Задача совместной работы:\n{task_prompt}\n")

# Инициализируем сессию ролевой игры
role_play_session = RolePlaying(
    assistant_role_name="Психолог",
    user_role_name="Писатель",
    task_prompt=task_prompt,
    model=model
)

print(Fore.CYAN + f"Описание конкретной задачи:\n{role_play_session.task_prompt}\n")

# Начинаем совместный диалог
chat_turn_limit, n = 30, 0
input_msg = role_play_session.init_chat()

while n < chat_turn_limit:
    n += 1
    assistant_response, user_response = role_play_session.step(input_msg)

    print_text_animated(Fore.BLUE + f"Писатель:\n\n{user_response.msg.content}\n")
    print_text_animated(Fore.GREEN + f"Психолог:\n\n{assistant_response.msg.content}\n")

    # Проверяем флаг завершения задачи
    if "CAMEL_TASK_DONE" in user_response.msg.content:
        print(Fore.MAGENTA + "✅ Электронная книга написана!")
        break

    input_msg = assistant_response.msg

print(Fore.YELLOW + f"Всего проведено {n} раундов совместного диалога")
