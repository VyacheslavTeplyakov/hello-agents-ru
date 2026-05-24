"""
Пример интеграции NoteTool с ContextBuilder

Демонстрирует, как интегрировать NoteTool с ContextBuilder, реализуя:
1. Долгосрочное отслеживание проекта
2. Поиск заметок и инъекцию контекста
3. Последовательные рекомендации на основе исторических заметок
"""
from dotenv import load_dotenv
load_dotenv()
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.context import ContextBuilder, ContextConfig, ContextPacket
from hello_agents.tools import MemoryTool, RAGTool, NoteTool
from hello_agents.core.message import Message
from datetime import datetime
from typing import List, Dict


class ProjectAssistant(SimpleAgent):
    """Долгосрочный помощник по проекту, интегрирующий NoteTool и ContextBuilder"""

    def __init__(self, name: str, project_name: str, **kwargs):
        # Настройка LLM
        from hello_agents.core.llm import HelloAgentsLLM
        llm = HelloAgentsLLM()

        super().__init__(name=name, llm=llm, **kwargs)

        self.project_name = project_name

        # Инициализация инструментов
        # self.memory_tool = MemoryTool(user_id=project_name)
        # self.rag_tool = RAGTool(knowledge_base_path=f"./{project_name}_kb")
        self.note_tool = NoteTool(workspace=f"./{project_name}_notes")

        # Инициализация построителя контекста
        self.context_builder = ContextBuilder(
            # memory_tool=self.memory_tool,
            # rag_tool=self.rag_tool,
            config=ContextConfig(max_tokens=4000)
        )

        self.conversation_history = []

    def run(self, user_input: str, note_as_action: bool = False) -> str:
        """Запуск помощника с автоматической интеграцией заметок"""

        # 1. Поиск релевантных заметок через NoteTool
        relevant_notes = self._retrieve_relevant_notes(user_input)

        # 2. Преобразование заметок в ContextPacket
        note_packets = self._notes_to_packets(relevant_notes)

        # 3. Построение оптимизированного контекста
        optimized_context = self.context_builder.build(
            user_query=user_input,
            conversation_history=self.conversation_history,
            system_instructions=self._build_system_instructions(),
            additional_packets=note_packets
        )

        # 4. Вызов LLM (передача в виде массива сообщений)
        messages = [
            {"role": "system", "content": optimized_context},
            {"role": "user", "content": user_input}
        ]
        response = self.llm.invoke(messages)

        # 5. При необходимости сохранить взаимодействие как заметку
        if note_as_action:
            self._save_as_note(user_input, response)

        # 6. Обновление истории диалога
        self._update_history(user_input, response)

        return response

    def _retrieve_relevant_notes(self, query: str, limit: int = 3) -> List[Dict]:
        """Поиск релевантных заметок"""
        try:
            # Приоритетный поиск заметок типов blocker и action
            blockers_raw = self.note_tool.run({
                "action": "list",
                "note_type": "blocker",
                "limit": 2
            })

            # Общий поиск
            search_results_raw = self.note_tool.run({
                "action": "search",
                "query": query,
                "limit": limit
            })

            blockers = self._ensure_list_of_dicts(blockers_raw)
            search_results = self._ensure_list_of_dicts(search_results_raw)

            # Объединение и дедупликация
            all_notes = {}
            for note in blockers + search_results:
                if not isinstance(note, dict):
                    continue
                note_id = (
                    note.get("note_id")
                    or note.get("id")
                    or note.get("uuid")
                    or note.get("title")
                    or str(hash(str(note)))
                )
                all_notes[note_id] = note
            return list(all_notes.values())[:limit]

        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка поиска заметок: {e}")
            return []

    def _ensure_list_of_dicts(self, data) -> List[Dict]:
        """Нормализация возврата NoteTool к списку словарей"""
        import json
        if data is None:
            return []
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                return []
        if isinstance(data, dict):
            # Совместимость с {"items": [...]} или одиночной записью
            if "items" in data and isinstance(data["items"], list):
                return [item for item in data["items"] if isinstance(item, dict)]
            return [data]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def _notes_to_packets(self, notes: List[Dict]) -> List[ContextPacket]:
        """Преобразование заметок в пакеты контекста"""
        packets = []

        for note in notes:
            title = note.get("title", "")
            body = note.get("content", "")
            content = f"[Заметка: {title}]\n{body}"

            # Безопасный разбор временной метки
            ts = None
            for key in ("updated_at", "updatedAt", "time", "timestamp"):
                if key in note:
                    ts = note.get(key)
                    break
            parsed_ts = None
            if isinstance(ts, (int, float)):
                try:
                    parsed_ts = datetime.fromtimestamp(ts)
                except Exception:
                    parsed_ts = None
            elif isinstance(ts, str):
                try:
                    parsed_ts = datetime.fromisoformat(ts)
                except Exception:
                    parsed_ts = None
            if parsed_ts is None:
                parsed_ts = datetime.now()

            note_type = note.get("type") or note.get("note_type") or "note"
            note_id = (
                note.get("note_id")
                or note.get("id")
                or note.get("uuid")
                or title
                or str(hash(str(note)))
            )

            packets.append(ContextPacket(
                content=content,
                timestamp=parsed_ts,
                token_count=len(content) // 4,  # Простая оценка
                relevance_score=0.75,  # Заметки имеют высокую релевантность
                metadata={
                    "type": "note",
                    "note_type": note_type,
                    "note_id": note_id
                }
            ))

        return packets

    def _save_as_note(self, user_input: str, response: str):
        """Сохранение взаимодействия как заметки"""
        try:
            # Определение типа заметки
            if "проблем" in user_input or "блокир" in user_input:
                note_type = "blocker"
            elif "план" in user_input or "следующ" in user_input:
                note_type = "action"
            else:
                note_type = "conclusion"

            self.note_tool.run({
                "action": "create",
                "title": f"{user_input[:30]}...",
                "content": f"## Вопрос\n{user_input}\n\n## Анализ\n{response}",
                "note_type": note_type,
                "tags": [self.project_name, "auto_generated"]
            })

        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка сохранения заметки: {e}")

    def _build_system_instructions(self) -> str:
        """Построение системных инструкций"""
        return f"""Вы долгосрочный помощник проекта {self.project_name}.

Ваши обязанности:
1. Давать последовательные рекомендации на основе исторических заметок
2. Отслеживать прогресс проекта и нерешённые проблемы
3. Ссылаться на релевантные исторические заметки в ответах
4. Предоставлять конкретные и применимые рекомендации по следующим шагам

Важно:
- Приоритет отдавать проблемам, помеченным как blocker
- Указывать источник рекомендаций (заметки, память или база знаний)
- Поддерживать осведомлённость об общем прогрессе проекта"""

    def _update_history(self, user_input: str, response: str):
        """Обновление истории диалога"""
        self.conversation_history.append(
            Message(content=user_input, role="user", timestamp=datetime.now())
        )
        self.conversation_history.append(
            Message(content=response, role="assistant", timestamp=datetime.now())
        )

        # Ограничение длины истории
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]


def main():
    print("=" * 80)
    print("Пример интеграции NoteTool с ContextBuilder")
    print("=" * 80 + "\n")

    # Пример использования
    assistant = ProjectAssistant(
        name="Помощник по проекту",
        project_name="data_pipeline_refactoring"
    )

    # Первое взаимодействие: фиксация состояния проекта
    print("Первое взаимодействие: фиксация состояния проекта")
    response = assistant.run(
        "Мы завершили рефакторинг слоя модели данных, покрытие тестами достигло 85%. Следующий шаг — рефакторинг слоя бизнес-логики.",
        note_as_action=True
    )
    print(f"Ответ помощника: {response}\n")

    # Второе взаимодействие: постановка вопроса
    print("Второе взаимодействие: постановка вопроса")
    response = assistant.run(
        "При рефакторинге слоя бизнес-логики я столкнулся с конфликтом версий зависимостей. Как его решить?"
    )
    print(f"Ответ помощника: {response}\n")

    # Просмотр сводки заметок
    print("Просмотр сводки заметок:")
    summary = assistant.note_tool.run({"action": "summary"})
    import json
    print(json.dumps(summary, indent=2, ensure_ascii=False).replace("\\n", "\n"))

    print("\n" + "=" * 80)
    print("Демонстрация завершена!")
    print("=" * 80)


if __name__ == "__main__":
    main()
