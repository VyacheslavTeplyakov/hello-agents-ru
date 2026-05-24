import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

# Загружаем переменные окружения из файла .env
load_dotenv()

class HelloAgentsLLM:
    """
    Кастомный LLM-клиент для книги «Hello Agents».
    Используется для вызова любого сервиса, совместимого с интерфейсом OpenAI;
    по умолчанию применяет потоковый вывод (stream=True).
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        Инициализирует клиент. Приоритет у переданных параметров;
        если они не указаны, значения берутся из переменных окружения.
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("Необходимо указать ID модели, ключ API и адрес сервиса или определить их в файле .env.")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        Вызывает большую языковую модель для «размышления» и возвращает её ответ.
        """
        print(f"🧠 Вызов модели {self.model}...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            
            # Обработка потокового ответа
            print("✅ Большая языковая модель ответила успешно:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # Перевод строки после завершения потокового вывода
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ Ошибка при вызове LLM API: {e}")
            return None

# --- Пример использования клиента ---
if __name__ == '__main__':
    try:
        llmClient = HelloAgentsLLM()
        
        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "Напиши алгоритм быстрой сортировки"}
        ]
        
        print("--- Вызов LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n--- Полный ответ модели ---")
            print(responseText)

    except ValueError as e:
        print(e)
