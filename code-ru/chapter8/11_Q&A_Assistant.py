#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеллектуальный ассистент для работы с документами — система вопросов и ответов на базе HelloAgents

Это полноценное приложение PDF-ассистента для обучения, поддерживающее:
- Загрузку PDF-документов и построение базы знаний
- Интеллектуальные вопросы и ответы (на основе RAG)
- Запись истории обучения (на основе Memory)
- Обзор обучения и генерацию отчётов
"""

from dotenv import load_dotenv
load_dotenv()
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from hello_agents.tools import MemoryTool, RAGTool
import gradio as gr

class PDFLearningAssistant:
    """Интеллектуальный ассистент для работы с документами"""

    def __init__(self, user_id: str = "default_user"):
        """Инициализация учебного ассистента

        Args:
            user_id: Идентификатор пользователя для разделения данных
        """
        self.user_id = user_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Инициализируем инструменты
        self.memory_tool = MemoryTool(user_id=user_id)
        self.rag_tool = RAGTool(rag_namespace=f"pdf_{user_id}")

        # Статистика обучения
        self.stats = {
            "session_start": datetime.now(),
            "documents_loaded": 0,
            "questions_asked": 0,
            "concepts_learned": 0
        }

        # Текущий загруженный документ
        self.current_document = None

    def load_document(self, pdf_path: str) -> Dict[str, Any]:
        """Загрузить PDF-документ в базу знаний

        Args:
            pdf_path: Путь к PDF-файлу

        Returns:
            Dict: Результат с полями success и message
        """
        if not os.path.exists(pdf_path):
            return {"success": False, "message": f"Файл не найден: {pdf_path}"}

        start_time = time.time()

        try:
            # Обрабатываем PDF с помощью инструмента RAG
            result = self.rag_tool.run({
                "action":"add_document",
                "file_path":pdf_path,
                "chunk_size":1000,
                "chunk_overlap":200
            })

            process_time = time.time() - start_time

            # RAGTool возвращает строковое сообщение
            self.current_document = os.path.basename(pdf_path)
            self.stats["documents_loaded"] += 1

            # Записываем в учебную память
            self.memory_tool.run({
                "action":"add",
                "content":f"Загружен документ «{self.current_document}»",
                "memory_type":"episodic",
                "importance":0.9,
                "event_type":"document_loaded",
                "session_id":self.session_id
            })

            return {
                "success": True,
                "message": f"Загрузка успешна! (время: {process_time:.1f} сек)",
                "document": self.current_document
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки: {str(e)}"
            }

    def ask(self, question: str, use_advanced_search: bool = True) -> str:
        """Задать вопрос по документу

        Args:
            question: Вопрос пользователя
            use_advanced_search: Использовать ли расширенный поиск (MQE + HyDE)

        Returns:
            str: Ответ
        """
        if not self.current_document:
            return "⚠️ Сначала загрузите документ! Используйте метод load_document() для загрузки PDF."

        # Записываем вопрос в рабочую память
        self.memory_tool.run({
            "action":"add",
            "content":f"Вопрос: {question}",
            "memory_type":"working",
            "importance":0.6,
            "session_id":self.session_id
        })

        # Используем RAG для поиска ответа
        answer = self.rag_tool.run({
            "action":"ask",
            "question":question,
            "limit":5,
            "enable_advanced_search":use_advanced_search,
            "enable_mqe":use_advanced_search,
            "enable_hyde":use_advanced_search
        })

        # Записываем в эпизодическую память
        self.memory_tool.run({
            "action":"add",
            "content":f"Изучение по теме «{question}»",
            "memory_type":"episodic",
            "importance":0.7,
            "event_type":"qa_interaction",
            "session_id":self.session_id
        })

        self.stats["questions_asked"] += 1

        return answer

    def add_note(self, content: str, concept: Optional[str] = None):
        """Добавить учебную заметку

        Args:
            content: Содержимое заметки
            concept: Связанная концепция (необязательно)
        """
        self.memory_tool.run({
            "action":"add",
            "content":content,
            "memory_type":"semantic",
            "importance":0.8,
            "concept":concept or "general",
            "session_id":self.session_id
        })

        self.stats["concepts_learned"] += 1

    def recall(self, query: str, limit: int = 5) -> str:
        """Просмотр истории обучения

        Args:
            query: Ключевые слова для поиска
            limit: Количество возвращаемых результатов

        Returns:
            str: Связанные воспоминания
        """
        result = self.memory_tool.run({
            "action":"search",
            "query":query,
            "limit":limit
        })
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику обучения

        Returns:
            Dict: Статистическая информация
        """
        duration = (datetime.now() - self.stats["session_start"]).total_seconds()

        return {
            "Длительность сессии": f"{duration:.0f} сек",
            "Загружено документов": self.stats["documents_loaded"],
            "Задано вопросов": self.stats["questions_asked"],
            "Учебных заметок": self.stats["concepts_learned"],
            "Текущий документ": self.current_document or "Не загружен"
        }

    def generate_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """Сгенерировать отчёт об обучении

        Args:
            save_to_file: Сохранить ли отчёт в файл

        Returns:
            Dict: Отчёт об обучении
        """
        # Получаем сводку памяти
        memory_summary = self.memory_tool.run({"action":"summary", "limit":10})

        # Получаем статистику RAG
        rag_stats = self.rag_tool.run({"action":"stats"})

        # Генерируем отчёт
        duration = (datetime.now() - self.stats["session_start"]).total_seconds()
        report = {
            "session_info": {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "start_time": self.stats["session_start"].isoformat(),
                "duration_seconds": duration
            },
            "learning_metrics": {
                "documents_loaded": self.stats["documents_loaded"],
                "questions_asked": self.stats["questions_asked"],
                "concepts_learned": self.stats["concepts_learned"]
            },
            "memory_summary": memory_summary,
            "rag_status": rag_stats
        }

        # Сохраняем в файл
        if save_to_file:
            report_file = f"learning_report_{self.session_id}.json"
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)
                report["report_file"] = report_file
            except Exception as e:
                report["save_error"] = str(e)

        return report




def create_gradio_ui():
    """Создать веб-интерфейс Gradio"""
    # Глобальный экземпляр ассистента
    assistant_state = {"assistant": None}

    def init_assistant(user_id: str) -> str:
        """Инициализировать ассистента"""
        if not user_id:
            user_id = "web_user"
        assistant_state["assistant"] = PDFLearningAssistant(user_id=user_id)
        return f"✅ Ассистент инициализирован (пользователь: {user_id})"

    def load_pdf(pdf_file) -> str:
        """Загрузить PDF-файл"""
        if assistant_state["assistant"] is None:
            return "❌ Сначала инициализируйте ассистента"

        if pdf_file is None:
            return "❌ Загрузите PDF-файл"

        # Файл, загруженный через Gradio, является временным объектом
        pdf_path = pdf_file.name
        result = assistant_state["assistant"].load_document(pdf_path)

        if result["success"]:
            return f"✅ {result['message']}\n📄 Документ: {result['document']}"
        else:
            return f"❌ {result['message']}"

    def chat(message: str, history: List) -> Tuple[str, List]:
        """Функция чата"""
        if assistant_state["assistant"] is None:
            return "", history + [[message, "❌ Сначала инициализируйте ассистента и загрузите документ"]]

        if not message.strip():
            return "", history

        # Определяем, является ли вопрос техническим или вопросом об истории обучения
        if any(keyword in message for keyword in ["раньше", "учил", "повтори", "история", "помню"]):
            # Просмотр истории обучения
            response = assistant_state["assistant"].recall(message)
            response = f"🧠 **Обзор обучения**\n\n{response}"
        else:
            # Технические вопросы и ответы
            response = assistant_state["assistant"].ask(message)
            response = f"💡 **Ответ**\n\n{response}"

        history.append([message, response])
        return "", history

    def add_note_ui(note_content: str, concept: str) -> str:
        """Добавить заметку"""
        if assistant_state["assistant"] is None:
            return "❌ Сначала инициализируйте ассистента"

        if not note_content.strip():
            return "❌ Содержимое заметки не может быть пустым"

        assistant_state["assistant"].add_note(note_content, concept or None)
        return f"✅ Заметка сохранена: {note_content[:50]}..."

    def get_stats_ui() -> str:
        """Получить статистику"""
        if assistant_state["assistant"] is None:
            return "❌ Сначала инициализируйте ассистента"

        stats = assistant_state["assistant"].get_stats()
        result = "📊 **Статистика обучения**\n\n"
        for key, value in stats.items():
            result += f"- **{key}**: {value}\n"
        return result

    def generate_report_ui() -> str:
        """Сгенерировать отчёт"""
        if assistant_state["assistant"] is None:
            return "❌ Сначала инициализируйте ассистента"

        report = assistant_state["assistant"].generate_report(save_to_file=True)

        result = f"✅ Отчёт об обучении сгенерирован\n\n"
        result += f"**Информация о сессии**\n"
        result += f"- Длительность сессии: {report['session_info']['duration_seconds']:.0f} сек\n"
        result += f"- Загружено документов: {report['learning_metrics']['documents_loaded']}\n"
        result += f"- Задано вопросов: {report['learning_metrics']['questions_asked']}\n"
        result += f"- Учебных заметок: {report['learning_metrics']['concepts_learned']}\n"

        if "report_file" in report:
            result += f"\n💾 Отчёт сохранён в: {report['report_file']}"

        return result

    # Создаём интерфейс Gradio
    with gr.Blocks(title="Интеллектуальный ассистент для работы с документами", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 📚 Интеллектуальный ассистент для работы с документами

        Система вопросов и ответов по документам на базе HelloAgents, поддерживающая:
        - 📄 Загрузку PDF-документов и построение базы знаний
        - 💬 Интеллектуальные вопросы и ответы (на основе RAG)
        - 📝 Запись учебных заметок
        - 🧠 Просмотр истории обучения
        - 📊 Генерацию отчётов об обучении
        """)

        with gr.Tab("🏠 Начало работы"):
            with gr.Row():
                user_id_input = gr.Textbox(
                    label="Идентификатор пользователя",
                    placeholder="Введите ваш ID (необязательно, по умолчанию web_user)",
                    value="web_user"
                )
                init_btn = gr.Button("Инициализировать ассистента", variant="primary")

            init_output = gr.Textbox(label="Статус инициализации", interactive=False)
            init_btn.click(init_assistant, inputs=[user_id_input], outputs=[init_output])

            gr.Markdown("### 📄 Загрузка PDF-документа")
            pdf_upload = gr.File(
                label="Загрузить PDF-файл",
                file_types=[".pdf"],
                type="filepath"
            )
            load_btn = gr.Button("Загрузить документ", variant="primary")
            load_output = gr.Textbox(label="Статус загрузки", interactive=False)
            load_btn.click(load_pdf, inputs=[pdf_upload], outputs=[load_output])

        with gr.Tab("💬 Интеллектуальные вопросы и ответы"):
            gr.Markdown("### Задавайте вопросы по документу или просматривайте историю обучения")
            chatbot = gr.Chatbot(
                label="История диалога",
                height=400,
                bubble_full_width=False
            )
            with gr.Row():
                msg_input = gr.Textbox(
                    label="Введите вопрос",
                    placeholder="Например: Что такое Transformer? или Что я изучал раньше?",
                    scale=4
                )
                send_btn = gr.Button("Отправить", variant="primary", scale=1)

            gr.Examples(
                examples=[
                    "Что такое большая языковая модель?",
                    "Каковы основные компоненты архитектуры Transformer?",
                    "Как обучить большую языковую модель?",
                    "Что я изучал раньше?",
                    "Повтори, что я учил о механизме внимания"
                ],
                inputs=msg_input
            )

            msg_input.submit(chat, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
            send_btn.click(chat, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])

        with gr.Tab("📝 Учебные заметки"):
            gr.Markdown("### Записывайте учебные впечатления и важные концепции")
            note_content = gr.Textbox(
                label="Содержимое заметки",
                placeholder="Введите учебную заметку...",
                lines=3
            )
            concept_input = gr.Textbox(
                label="Связанная концепция (необязательно)",
                placeholder="Например: transformer, attention"
            )
            note_btn = gr.Button("Сохранить заметку", variant="primary")
            note_output = gr.Textbox(label="Статус сохранения", interactive=False)
            note_btn.click(add_note_ui, inputs=[note_content, concept_input], outputs=[note_output])

        with gr.Tab("📊 Статистика обучения"):
            gr.Markdown("### Просмотр прогресса и статистики обучения")
            stats_btn = gr.Button("Обновить статистику", variant="primary")
            stats_output = gr.Markdown()
            stats_btn.click(get_stats_ui, outputs=[stats_output])

            gr.Markdown("### Генерация отчёта об обучении")
            report_btn = gr.Button("Сгенерировать отчёт", variant="primary")
            report_output = gr.Textbox(label="Статус отчёта", interactive=False)
            report_btn.click(generate_report_ui, outputs=[report_output])

    return demo


def main():
    """Главная функция — запуск веб-интерфейса Gradio"""
    print("\n" + "="*60)
    print("Интеллектуальный ассистент для работы с документами")
    print("="*60)
    print("Запуск веб-интерфейса...\n")

    demo = create_gradio_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
