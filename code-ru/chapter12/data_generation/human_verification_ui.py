"""
Интерфейс ручной верификации

Создаёт веб-интерфейс на основе Gradio для ручной проверки сгенерированных задач AIME
"""

import json
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
import gradio as gr


class HumanVerificationUI:
    """Интерфейс ручной верификации"""

    def __init__(self, data_path: str):
        """
        Инициализация интерфейса верификации

        Args:
            data_path: путь к JSON-файлу с данными
        """
        self.data_path = data_path
        self.problems = self._load_problems()
        self.current_index = 0
        self.verifications = self._load_verifications()

    def _load_problems(self) -> List[Dict[str, Any]]:
        """Загрузка данных задач"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Файл данных не найден: {self.data_path}")

        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_verifications(self) -> Dict[str, Any]:
        """Загрузка существующих результатов верификации"""
        verification_path = self.data_path.replace(".json", "_verifications.json")

        if os.path.exists(verification_path):
            with open(verification_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {}

    def _save_verifications(self):
        """Сохранение результатов верификации"""
        verification_path = self.data_path.replace(".json", "_verifications.json")

        with open(verification_path, 'w', encoding='utf-8') as f:
            json.dump(self.verifications, f, ensure_ascii=False, indent=2)

    def get_current_problem(self) -> Tuple[str, str, str, str, str, str]:
        """Получение информации о текущей задаче"""
        if not self.problems:
            return "Нет задач", "", "", "", "", "0/0"

        problem = self.problems[self.current_index]
        problem_id = problem.get("id", "unknown")

        # Получаем уже существующую информацию о верификации
        verification = self.verifications.get(problem_id, {})

        return (
            f"Задача {self.current_index + 1}/{len(self.problems)}",
            problem.get("problem", ""),
            f"Ответ: {problem.get('answer', 'N/A')}",
            problem.get("solution", ""),
            f"Тема: {problem.get('topic', 'N/A')}",
            verification.get("comments", "")
        )

    def verify_problem(
        self,
        correctness: int,
        clarity: int,
        difficulty_match: int,
        completeness: int,
        status: str,
        comments: str
    ) -> str:
        """
        Верификация текущей задачи

        Args:
            correctness: оценка корректности (1–5)
            clarity: оценка чёткости (1–5)
            difficulty_match: оценка соответствия сложности (1–5)
            completeness: оценка полноты (1–5)
            status: статус верификации (approved/rejected/needs_revision)
            comments: комментарии

        Returns:
            сообщение о результате верификации
        """
        if not self.problems:
            return "❌ Нет задач для верификации"

        problem = self.problems[self.current_index]
        problem_id = problem.get("id", "unknown")

        # Сохраняем результат верификации
        self.verifications[problem_id] = {
            "problem_id": problem_id,
            "scores": {
                "correctness": correctness,
                "clarity": clarity,
                "difficulty_match": difficulty_match,
                "completeness": completeness
            },
            "total_score": (correctness + clarity + difficulty_match + completeness) / 4,
            "status": status,
            "comments": comments,
            "verified_at": datetime.now().isoformat()
        }

        self._save_verifications()

        return f"✅ Задача {problem_id} верифицирована!\nИтоговый балл: {self.verifications[problem_id]['total_score']:.2f}/5.0"

    def next_problem(self) -> Tuple[str, str, str, str, str, str]:
        """Следующая задача"""
        if self.current_index < len(self.problems) - 1:
            self.current_index += 1
        return self.get_current_problem()

    def prev_problem(self) -> Tuple[str, str, str, str, str, str]:
        """Предыдущая задача"""
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_problem()

    def get_statistics(self) -> str:
        """Получение статистики верификации"""
        if not self.verifications:
            return "Данные верификации отсутствуют"

        total = len(self.problems)
        verified = len(self.verifications)

        approved = sum(1 for v in self.verifications.values() if v["status"] == "approved")
        rejected = sum(1 for v in self.verifications.values() if v["status"] == "rejected")
        needs_revision = sum(1 for v in self.verifications.values() if v["status"] == "needs_revision")

        avg_score = sum(v["total_score"] for v in self.verifications.values()) / verified if verified > 0 else 0

        return f"""
📊 Статистика верификации

Всего задач: {total}
Проверено: {verified} ({verified/total*100:.1f}%)
Не проверено: {total - verified}

Результаты верификации:
- ✅ Принято: {approved}
- ❌ Отклонено: {rejected}
- 🔄 Требует доработки: {needs_revision}

Средний балл: {avg_score:.2f}/5.0
"""

    def launch(self, share: bool = False):
        """Запуск интерфейса Gradio"""
        with gr.Blocks(title="Ручная верификация задач AIME") as demo:
            gr.Markdown("# 🎯 Система ручной верификации задач AIME")
            gr.Markdown(f"Файл данных: `{self.data_path}`")

            with gr.Row():
                with gr.Column(scale=2):
                    # Область отображения задачи
                    title = gr.Textbox(label="Текущая задача", interactive=False)
                    problem_text = gr.Textbox(label="Условие задачи", lines=5, interactive=False)
                    answer_text = gr.Textbox(label="Ответ", interactive=False)
                    solution_text = gr.Textbox(label="Решение", lines=10, interactive=False)
                    metadata_text = gr.Textbox(label="Метаданные", interactive=False)

                with gr.Column(scale=1):
                    # Область оценивания
                    gr.Markdown("### 📝 Оценки (1–5 баллов)")
                    correctness_slider = gr.Slider(1, 5, value=3, step=1, label="Корректность")
                    clarity_slider = gr.Slider(1, 5, value=3, step=1, label="Чёткость")
                    difficulty_slider = gr.Slider(1, 5, value=3, step=1, label="Соответствие сложности")
                    completeness_slider = gr.Slider(1, 5, value=3, step=1, label="Полнота")

                    # Выбор статуса
                    gr.Markdown("### ✅ Статус верификации")
                    status_radio = gr.Radio(
                        choices=["approved", "rejected", "needs_revision"],
                        value="approved",
                        label="Статус"
                    )

                    # Комментарии
                    comments_text = gr.Textbox(label="Комментарии", lines=3, placeholder="Введите комментарии...")

                    # Кнопка верификации
                    verify_btn = gr.Button("✅ Подтвердить верификацию", variant="primary")
                    verify_result = gr.Textbox(label="Результат верификации", interactive=False)

            # Кнопки навигации
            with gr.Row():
                prev_btn = gr.Button("⬅️ Предыдущая")
                next_btn = gr.Button("Следующая ➡️")

            # Статистика
            with gr.Row():
                stats_text = gr.Textbox(label="Статистика верификации", lines=10, interactive=False)
                refresh_stats_btn = gr.Button("🔄 Обновить статистику")

            # Загрузка начальной задачи
            demo.load(
                fn=self.get_current_problem,
                outputs=[title, problem_text, answer_text, solution_text, metadata_text, comments_text]
            )

            # Привязка обработчиков событий
            verify_btn.click(
                fn=self.verify_problem,
                inputs=[correctness_slider, clarity_slider, difficulty_slider, completeness_slider, status_radio, comments_text],
                outputs=verify_result
            )

            next_btn.click(
                fn=self.next_problem,
                outputs=[title, problem_text, answer_text, solution_text, metadata_text, comments_text]
            )

            prev_btn.click(
                fn=self.prev_problem,
                outputs=[title, problem_text, answer_text, solution_text, metadata_text, comments_text]
            )

            refresh_stats_btn.click(
                fn=self.get_statistics,
                outputs=stats_text
            )

        demo.launch(share=share, server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python human_verification_ui.py <data_path>")
        print("Пример: python human_verification_ui.py generated_data/aime_generated_20250110_120000.json")
        sys.exit(1)

    data_path = sys.argv[1]

    ui = HumanVerificationUI(data_path)
    ui.launch(share=False)
