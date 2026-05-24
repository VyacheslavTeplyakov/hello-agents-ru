"""
CodebaseMaintainer - Помощник по обслуживанию кодовой базы

Полная реализация долгосрочного агента, интегрирующая:
1. ContextBuilder - управление контекстом
2. NoteTool - структурированные заметки
3. TerminalTool - мгновенный доступ к файлам
4. MemoryTool - память диалога

Ключевое улучшение: агентный режим, где агент самостоятельно решает, какие инструменты использовать
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from hello_agents import HelloAgentsLLM
from hello_agents.agents import FunctionCallAgent
from hello_agents.context import ContextBuilder, ContextConfig, ContextPacket
from hello_agents.tools import MemoryTool, NoteTool, TerminalTool
from hello_agents.tools.registry import ToolRegistry
from hello_agents.core.message import Message


class CodebaseMaintainer:
    """Помощник по обслуживанию кодовой базы — пример долгосрочного агента

    Интегрирует ContextBuilder + NoteTool + TerminalTool + MemoryTool
    для управления задачами обслуживания кодовой базы между сессиями

    Ключевые особенности:
    - Агент самостоятельно использует инструменты для исследования кодовой базы
    - Рабочий процесс не предопределён — полностью основан на решениях агента
    - Управление памятью и контекстом между сессиями
    """

    def __init__(
        self,
        project_name: str,
        codebase_path: str,
        llm: Optional[HelloAgentsLLM] = None
    ):
        self.project_name = project_name
        self.codebase_path = codebase_path
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Инициализация LLM
        self.llm = llm or HelloAgentsLLM()

        # Инициализация инструментов
        self.memory_tool = MemoryTool(
            user_id=project_name,
            memory_types=["working"]
        )
        self.note_tool = NoteTool(workspace=f"./{project_name}_notes")
        self.terminal_tool = TerminalTool(workspace=codebase_path, timeout=60)

        # Инициализация построителя контекста
        self.context_builder = ContextBuilder(
            memory_tool=self.memory_tool,
            rag_tool=None,  # RAG не используется в данном примере
            config=ContextConfig(
                max_tokens=4000,
                reserve_ratio=0.15,
                min_relevance=0.2,
                enable_compression=True
            )
        )

        # Создание реестра инструментов и регистрация инструментов
        self.tool_registry = ToolRegistry()
        self.tool_registry.register_tool(self.terminal_tool)
        self.tool_registry.register_tool(self.note_tool)
        self.tool_registry.register_tool(self.memory_tool)

        # Создание агента
        self.agent = FunctionCallAgent(
            name="CodebaseMaintainer",
            llm=self.llm,
            system_prompt=self._build_base_system_prompt(),
            tool_registry=self.tool_registry,
            enable_tool_calling=True,
            max_tool_iterations=30
        )

        # История диалога
        self.conversation_history: List[Message] = []

        # Статистика
        self.stats = {
            "session_start": datetime.now(),
            "commands_executed": 0,
            "notes_created": 0,
            "issues_found": 0,
            "tool_calls": 0
        }

        print(f"Помощник по обслуживанию кодовой базы инициализирован: {project_name} (агентный режим)")
        print(f"Рабочая директория: {codebase_path}")
        print(f"ID сессии: {self.session_id}")
        print(f"Доступные инструменты: {', '.join(self.tool_registry.list_tools())}")

    def run(self, user_input: str, mode: str = "auto") -> str:
        """Запуск помощника (агентный режим)

        Args:
            user_input: пользовательский ввод
            mode: режим работы (направляющая подсказка для агента)
                - "auto": автоматически решает, использовать ли инструменты
                - "explore": рекомендует агенту сосредоточиться на исследовании кода
                - "analyze": рекомендует агенту сосредоточиться на анализе проблем
                - "plan": рекомендует агенту сосредоточиться на планировании задач

        Returns:
            str: ответ помощника
        """
        print(f"\n{'='*80}")
        print(f"Пользователь: {user_input}")
        print(f"{'='*80}\n")

        # Шаг 1: поиск релевантных заметок (предоставление контекста агенту)
        relevant_notes = self._retrieve_relevant_notes(user_input)
        note_packets = self._notes_to_packets(relevant_notes)

        # Шаг 2: построение оптимизированного контекста
        context = self.context_builder.build(
            user_query=user_input,
            conversation_history=self.conversation_history,
            system_instructions=self._build_system_instructions(mode),
            additional_packets=note_packets
        )

        # Шаг 3: агент самостоятельно принимает решения и использует инструменты
        print("Агент думает и выбирает инструменты...\n")

        # Обновление системного промпта агента (включает контекст)
        self.agent.system_prompt = context

        # Вызов агента (агент самостоятельно решает, использовать ли инструменты)
        response = self.agent.run(user_input)

        # Шаг 4: учёт использования инструментов
        self._track_tool_usage()

        # Шаг 5: обновление истории диалога
        self._update_history(user_input, response)

        print(f"\nПомощник: {response}\n")
        print(f"{'='*80}\n")

        return response

    def _build_base_system_prompt(self) -> str:
        """Построение базового системного промпта"""
        return f"""Вы помощник по обслуживанию кодовой базы проекта {self.project_name}.

Ваши ключевые возможности:
1. Использование TerminalTool для исследования кодовой базы
   - Вы можете выполнять любые shell-команды: ls, cat, grep, find, git и др.
   - Рабочая директория: {self.codebase_path}

2. Использование NoteTool для записи обнаружений и задач
   - Создание заметок для фиксации важных обнаружений
   - Типы заметок: blocker (блокирующая проблема), action (план действий), task_state (состояние задачи), conclusion (вывод)

3. Использование MemoryTool для хранения ключевой информации
   - Запоминание важной контекстной информации
   - Поддержание непрерывности между сессиями

ID текущей сессии: {self.session_id}

Важные принципы:
- Самостоятельно решайте, какие инструменты использовать и какие команды выполнять
- При исследовании кодовой базы сначала изучите общую структуру, затем углубляйтесь в детали
- При обнаружении важной информации активно используйте NoteTool для её записи
- Поддерживайте профессионализм и практичность ответов
"""

    def _track_tool_usage(self):
        """Учёт использования инструментов"""
        # Статистика из истории выполнения агента
        if hasattr(self.agent, 'message_history'):
            for msg in self.agent.message_history[-10:]:  # Только последние 10 записей
                if msg.role == "tool":
                    self.stats["tool_calls"] += 1
                    # Статистика по имени инструмента
                    if "terminal" in str(msg.content).lower() or "command" in str(msg.content).lower():
                        self.stats["commands_executed"] += 1
                    elif "note" in str(msg.content).lower():
                        if "create" in str(msg.content).lower():
                            self.stats["notes_created"] += 1

    def _retrieve_relevant_notes(self, query: str, limit: int = 3) -> List[Dict]:
        """Поиск релевантных заметок"""
        try:
            # Приоритетный поиск блокирующих проблем
            blockers_raw = self.note_tool.run({
                "action": "list",
                "note_type": "blocker",
                "limit": 2
            })
            blockers = self._normalize_note_results(blockers_raw)

            # Поиск релевантных заметок
            search_results_raw = self.note_tool.run({
                "action": "search",
                "query": query,
                "limit": limit
            })
            search_results = self._normalize_note_results(search_results_raw)

            # Объединение и дедупликация
            all_notes = {}
            for note in blockers + search_results:
                if not isinstance(note, dict):
                    continue
                note_id = note.get('note_id') or note.get('id')
                if not note_id:
                    continue
                if note_id not in all_notes:
                    all_notes[note_id] = note

            return list(all_notes.values())[:limit]

        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка поиска заметок: {e}")
            return []

    def _normalize_note_results(self, result: Any) -> List[Dict]:
        """Преобразование возврата инструмента заметок к списку словарей"""
        if not result:
            return []

        if isinstance(result, dict):
            return [result]

        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]

        if isinstance(result, str):
            text = result.strip()
            if not text:
                return []
            if text.startswith("{") or text.startswith("["):
                try:
                    parsed = json.loads(text)
                    return self._normalize_note_results(parsed)
                except Exception:
                    return []
            return []

        return []

    def _notes_to_packets(self, notes: List[Dict]) -> List[ContextPacket]:
        """Преобразование заметок в пакеты контекста"""
        packets = []

        for note in notes:
            if not isinstance(note, dict):
                continue
            # Установка разных оценок релевантности в зависимости от типа заметки
            relevance_map = {
                "blocker": 0.9,
                "action": 0.8,
                "task_state": 0.75,
                "conclusion": 0.7
            }

            note_type = note.get('type', 'general')
            relevance = relevance_map.get(note_type, 0.6)

            content = f"[Заметка: {note.get('title', 'Без названия')}]\nТип: {note_type}\n\n{note.get('content', '')}"
            updated_at = note.get('updated_at')
            try:
                note_timestamp = datetime.fromisoformat(updated_at) if updated_at else datetime.now()
            except (ValueError, TypeError):
                note_timestamp = datetime.now()

            packets.append(ContextPacket(
                content=content,
                timestamp=note_timestamp,
                token_count=len(content) // 4,
                relevance_score=relevance,
                metadata={
                    "type": "note",
                    "note_type": note_type,
                    "note_id": note.get('note_id') or note.get('id')
                }
            ))

        return packets

    def _build_system_instructions(self, mode: str) -> str:
        """Построение системных инструкций (агентный режим)"""
        base_instructions = self._build_base_system_prompt()

        mode_hints = {
            "explore": """
Текущий фокус пользователя: исследование кодовой базы

Рекомендуемая стратегия:
- Рассмотрите использование TerminalTool для изучения структуры кода (например, find, ls, tree)
- Просмотрите ключевые файлы (например, README, основные модули)
- Запишите архитектурную информацию в заметки для последующего использования
""",
            "analyze": """
Текущий фокус пользователя: анализ качества кода

Рекомендуемая стратегия:
- Рассмотрите использование grep для поиска потенциальных проблем (TODO, FIXME, BUG)
- Проанализируйте сложность и структуру кода
- Записывайте обнаруженные проблемы как заметки типа blocker или action
""",
            "plan": """
Текущий фокус пользователя: планирование задач

Рекомендуемая стратегия:
- Просмотрите исторические заметки для понимания текущего прогресса
- Составьте план действий на основе имеющейся информации
- Создайте или обновите заметки типа task_state
""",
            "auto": """
Текущий фокус пользователя: свободный диалог

Рекомендуемая стратегия:
- Гибко принимайте решения исходя из потребностей пользователя
- При необходимости активно используйте инструменты для получения информации
- Отвечайте напрямую, когда инструменты не нужны
"""
        }

        return base_instructions + "\n" + mode_hints.get(mode, mode_hints["auto"])


    def _update_history(self, user_input: str, response: str):
        """Обновление истории диалога"""
        self.conversation_history.append(
            Message(content=user_input, role="user", timestamp=datetime.now())
        )
        self.conversation_history.append(
            Message(content=response, role="assistant", timestamp=datetime.now())
        )

        # Ограничение длины истории (сохраняем последние 10 раундов диалога)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    # === Удобные методы ===

    def explore(self, target: str = ".") -> str:
        """Исследование кодовой базы (агентный режим)

        Агент самостоятельно решает, какие команды использовать для исследования
        """
        return self.run(f"Пожалуйста, исследуйте структуру кода в {target} и изучите организацию проекта", mode="explore")

    def analyze(self, focus: str = "") -> str:
        """Анализ качества кода (агентный режим)

        Агент самостоятельно решает, как анализировать качество кода
        """
        query = "Пожалуйста, проанализируйте качество кода" + (f", уделив особое внимание {focus}" if focus else "")
        return self.run(query, mode="analyze")

    def plan_next_steps(self) -> str:
        """Планирование следующих задач (агентный режим)

        Агент просматривает исторические заметки и планирует следующие шаги
        """
        return self.run("На основе нашего предыдущего анализа и текущего прогресса спланируйте следующие задачи", mode="plan")

    def execute_command(self, command: str) -> str:
        """Выполнение команды терминала"""
        result = self.terminal_tool.run({"command": command})
        self.stats["commands_executed"] += 1
        return result

    def create_note(
        self,
        title: str,
        content: str,
        note_type: str = "general",
        tags: List[str] = None
    ) -> str:
        """Создание заметки"""
        result = self.note_tool.run({
            "action": "create",
            "title": title,
            "content": content,
            "note_type": note_type,
            "tags": tags or [self.project_name]
        })
        self.stats["notes_created"] += 1
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        duration = (datetime.now() - self.stats["session_start"]).total_seconds()

        # Получение сводки заметок
        try:
            note_summary = self.note_tool.run({"action": "summary"})
        except:
            note_summary = {}

        return {
            "session_info": {
                "session_id": self.session_id,
                "project": self.project_name,
                "duration_seconds": duration
            },
            "activity": {
                "commands_executed": self.stats["commands_executed"],
                "notes_created": self.stats["notes_created"],
                "issues_found": self.stats["issues_found"]
            },
            "notes": note_summary
        }

    def generate_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """Генерация отчёта о сессии"""
        report = self.get_stats()

        if save_to_file:
            report_file = f"maintainer_report_{self.session_id}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            report["report_file"] = report_file
            print(f"Отчёт сохранён: {report_file}")

        return report


def main():
    """Главная функция — демонстрация использования CodebaseMaintainer (агентная версия)

    В этой версии:
    - Агент самостоятельно решает, какие инструменты использовать
    - Рабочий процесс не предопределён
    - Агент гибко исследует кодовую базу в зависимости от потребностей
    """
    print("=" * 80)
    print("Демонстрация CodebaseMaintainer (агентная версия)")
    print("=" * 80 + "\n")

    # Инициализация помощника
    maintainer = CodebaseMaintainer(
        project_name="my_flask_app",
        codebase_path="./my_flask_app",
        llm=HelloAgentsLLM()
    )

    # Исследование кодовой базы (агент самостоятельно решает, как исследовать)
    print("\n### Исследование кодовой базы (агент исследует самостоятельно) ###")
    response = maintainer.explore()

    # Анализ качества кода (агент самостоятельно выбирает метод анализа)
    print("\n### Анализ качества кода (агент анализирует самостоятельно) ###")
    response = maintainer.analyze()

    # Планирование следующих шагов (агент планирует на основе исторической информации)
    print("\n### Планирование следующих задач (агент планирует самостоятельно) ###")
    response = maintainer.plan_next_steps()

    # Генерация отчёта
    print("\n### Генерация отчёта о сессии ###")
    report = maintainer.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("Демонстрация завершена!")
    print("=" * 80)


if __name__ == "__main__":
    main()
