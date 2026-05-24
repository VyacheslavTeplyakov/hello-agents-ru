# my_main.py
from dotenv import load_dotenv
from my_llm import MyLLM # Примечание: здесь импортируем наш собственный класс

# Загружаем переменные окружения
load_dotenv()

# Создаём экземпляр нашего переопределённого клиента и указываем provider
llm = MyLLM(provider="modelscope")

# Подготавливаем сообщения
messages = [{"role": "user", "content": "Привет, расскажи о себе."}]

# Выполняем вызов; методы think и другие уже унаследованы от родительского класса, переопределять их не нужно
response_stream = llm.think(messages)

# Выводим ответ
print("ModelScope Response:")
for chunk in response_stream:
    # chunk уже был напечатан один раз внутри библиотеки my_llm, здесь достаточно pass
    # print(chunk, end="", flush=True)
    pass
