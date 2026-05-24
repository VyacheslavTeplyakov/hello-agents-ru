from dotenv import load_dotenv
# Загружаем переменные окружения из файла .env
load_dotenv()

import os
from serpapi import SerpApiClient
from typing import Dict, Any

def search(query: str) -> str:
    """
    Практический инструмент веб-поиска на базе SerpApi.
    Интеллектуально разбирает результаты поиска, отдавая приоритет прямым ответам
    или информации из графа знаний.
    """
    print(f"🔍 Выполняется [SerpApi] веб-поиск: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Ошибка: SERPAPI_API_KEY не настроен в файле .env."

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "ru",    # Код страны (изменили на ru для русскоязычной локали)
            "hl": "ru",    # Код языка (изменили на ru для русскоязычной локали)
        }
        
        client = SerpApiClient(params)
        results = client.get_dict()
        
        # Умный разбор: сначала ищем наиболее прямой ответ
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # Если прямого ответа нет, возвращаем сводки первых трех органических результатов
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"К сожалению, информация по запросу '{query}' не найдена."

    except Exception as e:
        return f"Ошибка при выполнении поиска: {e}"
    
class ToolExecutor:
    """
    Исполнитель инструментов, отвечающий за управление и запуск инструментов.
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        Регистрирует новый инструмент в наборе инструментов.
        """
        if name in self.tools:
            print(f"Предупреждение: инструмент '{name}' уже существует и будет перезаписан.")
        
        self.tools[name] = {"description": description, "func": func}
        print(f"Инструмент '{name}' зарегистрирован.")

    def getTool(self, name: str) -> callable:
        """
        Возвращает функцию-исполнитель инструмента по его имени.
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        Возвращает отформатированную строку с описанием всех доступных инструментов.
        """
        return "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])


# --- Инициализация инструментов и пример использования ---
if __name__ == '__main__':
    # 1. Инициализируем исполнитель инструментов
    toolExecutor = ToolExecutor()

    # 2. Регистрируем практический инструмент поиска
    search_description = "Поисковая система в интернете. Используйте этот инструмент, когда нужно ответить на вопросы о текущих событиях, фактах и информации, отсутствующей в базе знаний."
    toolExecutor.registerTool("Search", search_description, search)
    
    # 3. Выводим доступные инструменты
    print("\n--- Доступные инструменты ---")
    print(toolExecutor.getAvailableTools())

    # 4. Вызов Action агентом — задаем вопрос о реальном времени
    print("\n--- Выполняем Action: Search['Какая последняя модель GPU NVIDIA'] ---")
    tool_name = "Search"
    tool_input = "Какая последняя модель GPU NVIDIA"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- Наблюдение (Observation) ---")
        print(observation)
    else:
        print(f"Ошибка: инструмент с именем '{tool_name}' не найден.")
