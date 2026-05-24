# my_advanced_search.py
import os
from typing import Optional, List, Dict, Any
from hello_agents import ToolRegistry

class MyAdvancedSearchTool:
    """
    Пользовательский класс инструмента расширенного поиска.
    Демонстрирует паттерн интеграции нескольких источников и интеллектуального выбора.
    """

    def __init__(self):
        self.name = "my_advanced_search"
        self.description = "Интеллектуальный инструмент поиска с поддержкой нескольких источников и автоматическим выбором лучшего результата"
        self.search_sources = []
        self._setup_search_sources()

    def _setup_search_sources(self):
        """Настройка доступных источников поиска"""
        # Проверяем доступность Tavily
        if os.getenv("TAVILY_API_KEY"):
            try:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                self.search_sources.append("tavily")
                print("✅ Источник поиска Tavily включён")
            except ImportError:
                print("⚠️ Библиотека Tavily не установлена")

        # Проверяем доступность SerpApi
        if os.getenv("SERPAPI_API_KEY"):
            try:
                import serpapi
                self.search_sources.append("serpapi")
                print("✅ Источник поиска SerpApi включён")
            except ImportError:
                print("⚠️ Библиотека SerpApi не установлена")

        if self.search_sources:
            print(f"🔧 Доступные источники поиска: {', '.join(self.search_sources)}")
        else:
            print("⚠️ Нет доступных источников поиска, пожалуйста, настройте API-ключи")

    def search(self, query: str) -> str:
        """Выполнить интеллектуальный поиск"""
        if not query.strip():
            return "❌ Ошибка: поисковый запрос не может быть пустым"

        # Проверяем наличие доступных источников поиска
        if not self.search_sources:
            return """❌ Нет доступных источников поиска. Пожалуйста, настройте один из следующих API-ключей:

1. Tavily API: задайте переменную окружения TAVILY_API_KEY
   Получить: https://tavily.com/

2. SerpAPI: задайте переменную окружения SERPAPI_API_KEY
   Получить: https://serpapi.com/

После настройки перезапустите программу."""

        print(f"🔍 Начинаем интеллектуальный поиск: {query}")

        # Пробуем несколько источников поиска и возвращаем лучший результат
        for source in self.search_sources:
            try:
                if source == "tavily":
                    result = self._search_with_tavily(query)
                    if result and "не найдено" not in result:
                        return f"📊 Результаты поиска Tavily AI:\n\n{result}"

                elif source == "serpapi":
                    result = self._search_with_serpapi(query)
                    if result and "не найдено" not in result:
                        return f"🌐 Результаты поиска SerpApi Google:\n\n{result}"

            except Exception as e:
                print(f"⚠️ Поиск через {source} не удался: {e}")
                continue

        return "❌ Все источники поиска не сработали. Проверьте подключение к сети и настройки API-ключей"

    def _search_with_tavily(self, query: str) -> str:
        """Поиск с использованием Tavily"""
        response = self.tavily_client.search(query=query, max_results=3)

        if response.get('answer'):
            result = f"💡 Прямой ответ AI: {response['answer']}\n\n"
        else:
            result = ""

        result += "🔗 Связанные результаты:\n"
        for i, item in enumerate(response.get('results', [])[:3], 1):
            result += f"[{i}] {item.get('title', '')}\n"
            result += f"    {item.get('content', '')[:150]}...\n\n"

        return result

    def _search_with_serpapi(self, query: str) -> str:
        """Поиск с использованием SerpApi"""
        import serpapi

        search = serpapi.GoogleSearch({
            "q": query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "num": 3
        })

        results = search.get_dict()

        result = "🔗 Результаты поиска Google:\n"
        if "organic_results" in results:
            for i, res in enumerate(results["organic_results"][:3], 1):
                result += f"[{i}] {res.get('title', '')}\n"
                result += f"    {res.get('snippet', '')}\n\n"

        return result

def create_advanced_search_registry():
    """Создать реестр инструментов с расширенным поиском"""
    registry = ToolRegistry()

    # Создаём экземпляр инструмента поиска
    search_tool = MyAdvancedSearchTool()

    # Регистрируем метод инструмента поиска как функцию
    registry.register_function(
        name="advanced_search",
        description="Расширенный инструмент поиска, объединяющий Tavily и SerpAPI для получения более полных результатов",
        func=search_tool.search
    )

    return registry
