from hello_agents.protocols import ANPDiscovery, register_service
import random

# Создаём центр обнаружения сервисов
discovery = ANPDiscovery()

# Регистрируем несколько сервисов одного типа
for i in range(5):
    register_service(
        discovery=discovery,
        service_id=f"api_server_{i}",
        service_name=f"API-сервер {i}",
        service_type="api",
        capabilities=["rest_api"],
        endpoint=f"http://api{i}:8000",
        metadata={"load": random.uniform(0.1, 0.9)}
    )

# Функция балансировки нагрузки
def get_best_server():
    """Выбирает сервер с наименьшей нагрузкой"""
    servers = discovery.discover_services(service_type="api")
    if not servers:
        return None

    best = min(servers, key=lambda s: s.metadata.get("load", 1.0))
    return best

# Симуляция распределения запросов
for i in range(10):
    server = get_best_server()
    print(f"Запрос {i+1} -> {server.service_name} (нагрузка: {server.metadata['load']:.2f})")

    # Обновляем нагрузку (симуляция)
    server.metadata["load"] += 0.1
