from hello_agents.protocols import ANPDiscovery, register_service
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools.builtin import ANPTool
import random
from dotenv import load_dotenv

load_dotenv()
llm = HelloAgentsLLM()

# 1. Создаём центр обнаружения сервисов
discovery = ANPDiscovery()

# 2. Регистрируем несколько вычислительных узлов
for i in range(10):
    register_service(
        discovery=discovery,
        service_id=f"compute_node_{i}",
        service_name=f"Вычислительный узел {i}",
        service_type="compute",
        capabilities=["data_processing", "ml_training"],
        endpoint=f"http://node{i}:8000",
        metadata={
            "load": random.uniform(0.1, 0.9),
            "cpu_cores": random.choice([4, 8, 16]),
            "memory_gb": random.choice([16, 32, 64]),
            "gpu": random.choice([True, False])
        }
    )

print(f"✅ Зарегистрировано {len(discovery.list_all_services())} вычислительных узлов")

# 3. Создаём агента-планировщика задач
scheduler = SimpleAgent(
    name="Планировщик задач",
    llm=llm,
    system_prompt="""Ты интеллектуальный планировщик задач. Твои обязанности:
1. Анализировать требования к задаче
2. Выбирать наиболее подходящий вычислительный узел
3. Распределять задачи

При выборе узла учитывай: нагрузку, количество ядер CPU, объём памяти, наличие GPU и другие факторы.

При использовании инструмента service_discovery необходимо указывать параметр action:
- Просмотреть все узлы: {"action": "discover_services", "service_type": "compute"}
- Получить статистику сети: {"action": "get_stats"}"""
)

# Добавляем инструмент ANP
anp_tool = ANPTool(
    name="service_discovery",
    description="Инструмент обнаружения сервисов для поиска и выбора вычислительных узлов",
    discovery=discovery
)
scheduler.add_tool(anp_tool)

# 4. Интеллектуальное распределение задач
def assign_task(task_description):
    print(f"\nЗадача: {task_description}")
    print("=" * 50)

    # Пусть агент интеллектуально выберет узел
    response = scheduler.run(f"""
Пожалуйста, выбери наиболее подходящий вычислительный узел для следующей задачи:
{task_description}

Шаги:
1. Используй инструмент service_discovery для просмотра всех доступных вычислительных узлов (service_type="compute")
2. Проанализируй характеристики каждого узла (нагрузка, количество ядер CPU, объём памяти, GPU и т.д.)
3. Выбери наиболее подходящий узел в соответствии с требованиями задачи
4. Обоснуй свой выбор

Укажи ID выбранного узла и причину выбора.
    """)

    print(response)
    print("=" * 50)

# Тестирование различных типов задач
assign_task("Обучение большой модели глубокого обучения, требуется поддержка GPU")
assign_task("Обработка большого объёма текстовых данных, требуется большой объём памяти")
assign_task("Выполнение лёгкой задачи анализа данных")
