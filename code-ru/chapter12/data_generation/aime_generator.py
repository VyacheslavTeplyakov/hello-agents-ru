"""
Генератор задач по математике AIME

Использует фреймворк HelloAgents для генерации задач в стиле AIME
"""

import json
import os
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm
from hello_agents import SimpleAgent
from hello_agents import HelloAgentsLLM
from datasets import load_dataset


class AIMEGenerator:
    """Генератор задач AIME"""

    # Промпт для генерации задач AIME (на английском)
    GENERATION_PROMPT = """You are a professional mathematics competition problem designer, skilled in creating AIME (American Invitational Mathematics Examination) style problems.

AIME Problem Characteristics:
1. Answer: An integer between 0 and 999
2. Topics: Algebra, Geometry, Number Theory, Combinatorics, Probability, etc.
3. Style: Requires multi-step reasoning, but no advanced theory
4. Difficulty: Medium to hard (similar to AIME problems 6-9)

Please generate an AIME-style mathematics problem, including:
1. Problem statement (clear and complete)
2. Answer (an integer between 0 and 999)
3. Detailed solution (including all reasoning steps)
4. Topic classification (Algebra/Geometry/Number Theory/Combinatorics/Probability)

Please output in the following JSON format, avoid using special escape characters in JSON:
```json
{
    "problem": "Problem statement in English",
    "answer": 123,
    "solution": "Detailed solution steps in English",
    "topic": "Algebra"
}
```
"""

    def __init__(
        self,
        llm: HelloAgentsLLM = None,
        delay_seconds: float = 1.0,
        use_reference_examples: bool = True,
        reference_dataset: str = "TianHongZXY/aime-1983-2025"
    ):
        """
        Инициализация генератора

        Args:
            llm: экземпляр LLM (опционально)
            delay_seconds: задержка между генерациями (в секундах) для предотвращения rate limit
            use_reference_examples: использовать ли реальные задачи как примеры-референсы
            reference_dataset: имя референсного датасета; по умолчанию TianHongZXY/aime-1983-2025 (900+ задач)
        """
        # Если llm не передан — создаём стандартный HelloAgentsLLM
        if llm is None:
            self.llm = HelloAgentsLLM()
        else:
            self.llm = llm

        self.agent = SimpleAgent(
            name="AIME Generator",
            llm=self.llm,
            system_prompt="Вы — профессиональный эксперт по разработке задач для математических олимпиад."
        )
        self.delay_seconds = delay_seconds
        self.use_reference_examples = use_reference_examples
        self.reference_examples = []

        # Загружаем примеры-референсы
        if use_reference_examples:
            try:
                print(f"📚 Загружаю датасет реальных задач AIME: {reference_dataset}")
                # Пробуем разные сплиты
                try:
                    dataset = load_dataset(reference_dataset, split="train")
                except:
                    dataset = load_dataset(reference_dataset, split="test")

                # Загружаем все задачи как референсы
                self.reference_examples = list(dataset)
                print(f"   ✓ Загружено {len(self.reference_examples)} референсных задач")

                # Статистика по годам (если есть поле year)
                year_counts = {}
                for item in self.reference_examples:
                    year = item.get('year')
                    if year:
                        year_counts[year] = year_counts.get(year, 0) + 1

                if year_counts:
                    year_range = f"{min(year_counts.keys())}-{max(year_counts.keys())}"
                    print(f"   ℹ️  Диапазон годов: {year_range}")

            except Exception as e:
                print(f"   ⚠️ Не удалось загрузить примеры-референсы: {e}")
                print(f"   ℹ️  Будет использован стандартный промпт для генерации")
                self.use_reference_examples = False

    def generate_single(self, max_retries: int = 3) -> Dict[str, Any]:
        """
        Генерация одной задачи

        Args:
            max_retries: максимальное число повторных попыток

        Returns:
            данные задачи
        """
        # Формируем промпт
        prompt = self._build_prompt()

        for attempt in range(max_retries):
            try:
                response = self.agent.run(prompt)
                return self._parse_response(response)
            except Exception as e:
                if attempt < max_retries - 1:
                    tqdm.write(f"⚠️ Генерация не удалась (попытка {attempt + 1}/{max_retries}), повтор через {self.delay_seconds} с...")
                    time.sleep(self.delay_seconds)
                else:
                    tqdm.write(f"❌ Генерация не удалась, достигнут максимум попыток: {e}")
                    return self._get_default_problem()

    def _build_prompt(self) -> str:
        """Формирование промпта для генерации"""
        if not self.use_reference_examples or not self.reference_examples:
            return self.GENERATION_PROMPT

        # Случайно выбираем один пример-референс
        example = random.choice(self.reference_examples)
        example_problem = example.get('problem', 'Example problem')
        example_answer = example.get('answer', 0)

        # Формируем промпт с примером-референсом (на английском)
        prompt = f"""You are a professional mathematics competition problem designer, skilled in creating AIME (American Invitational Mathematics Examination) style problems.

【Reference Example】(For style reference only, please generate a completely different problem)
Problem: {example_problem}
Answer: {example_answer}

AIME Problem Characteristics:
1. Answer: An integer between 0 and 999
2. Topics: Algebra, Geometry, Number Theory, Combinatorics, Probability, etc.
3. Style: Requires multi-step reasoning, but no advanced theory
4. Difficulty: Medium to hard (similar to AIME problems 6-9)

Please generate a **completely different** AIME-style mathematics problem, including:
1. Problem statement (clear and complete, different from the reference)
2. Answer (an integer between 0 and 999, different from the reference)
3. Detailed solution (including all reasoning steps)
4. Topic classification (Algebra/Geometry/Number Theory/Combinatorics/Probability)

Please output in the following JSON format, avoid using special escape characters in JSON:
```json
{{
    "problem": "Problem statement in English",
    "answer": 123,
    "solution": "Detailed solution steps in English",
    "topic": "Algebra"
}}
```

Important Notes:
- **Must generate a completely different problem from the reference**
- You can reference the style, but do not copy the content
- Ensure the problem is creative and original
"""
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа LLM (поддержка математических формул LaTeX)"""
        import re

        # Извлекаем JSON-блок
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()

        # Используем json.loads со strict=False для обработки экранированных символов
        # Но этого недостаточно — нужна более умная обработка
        try:
            problem_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Если парсинг не удался — пробуем исправить типичные проблемы с экранированием LaTeX
            # Метод: заменяем одиночные обратные слэши двойными (кроме уже экранированных)
            # Тогда LaTeX-команда \frac станет \\frac — валидный JSON

            # Регулярное выражение: находим все неэкранированные обратные слэши (не \\)
            # и заменяем на \\
            fixed_json_str = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', json_str)

            try:
                problem_data = json.loads(fixed_json_str)
            except json.JSONDecodeError:
                # Если всё равно не удалось — выводим ошибку и пробрасываем исключение
                print(f"❌ Ошибка парсинга JSON:")
                print(f"Исходный ответ: {response[:500]}...")
                print(f"Извлечённый JSON: {json_str[:500]}...")
                raise

        # Проверяем обязательные поля
        if "problem" not in problem_data or "answer" not in problem_data:
            raise ValueError("Отсутствуют обязательные поля: problem или answer")

        # Проверяем диапазон ответа
        answer = int(problem_data.get("answer", 0))
        if not (0 <= answer <= 999):
            print(f"⚠️ Ответ вне допустимого диапазона: {answer}, приведение к 0–999")
            answer = max(0, min(999, answer))
            problem_data["answer"] = answer

        # Устанавливаем значения по умолчанию
        problem_data.setdefault("solution", "No solution provided")
        problem_data.setdefault("topic", "Uncategorized")

        return problem_data

    def _get_default_problem(self) -> Dict[str, Any]:
        """Возвращает задачу-заглушку (используется при ошибке генерации)"""
        return {
            "problem": "Генерация не удалась, пожалуйста повторите",
            "answer": 0,
            "solution": "N/A",
            "topic": "Неизвестно"
        }

    def generate_batch(
        self,
        num_problems: int = 30,
        checkpoint_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        Пакетная генерация задач

        Args:
            num_problems: количество задач для генерации
            checkpoint_path: путь к файлу чекпоинта (для сохранения прогресса)

        Returns:
            список задач
        """
        print(f"\n🎯 Начинаю генерацию задач AIME")
        print(f"   Целевое количество: {num_problems}")
        print(f"   Модель генерации: {self.llm.model}")
        print(f"   Задержка: {self.delay_seconds} с/задача")

        # Попытка восстановления из чекпоинта
        problems = []
        start_index = 0

        if checkpoint_path and os.path.exists(checkpoint_path):
            print(f"\n📂 Найден файл чекпоинта, пробую восстановиться...")
            try:
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    problems = json.load(f)
                start_index = len(problems)
                print(f"   ✓ Восстановлено {start_index} задач, продолжаю с задачи {start_index + 1}")
            except Exception as e:
                print(f"   ⚠️ Восстановление не удалось: {e}, начинаю сначала")
                problems = []
                start_index = 0

        # Генерация задач (прогресс через tqdm)
        with tqdm(total=num_problems, initial=start_index, desc="Генерация задач AIME", unit="зад.") as pbar:
            last_call_time = 0  # Время последнего вызова API

            for i in range(start_index, num_problems):
                # Вычисляем время с последнего вызова
                if last_call_time > 0:
                    elapsed = time.time() - last_call_time
                    # Если с момента последнего вызова прошло меньше delay_seconds — ждём
                    if elapsed < self.delay_seconds:
                        wait_time = self.delay_seconds - elapsed
                        tqdm.write(f"⏳ Ожидание {wait_time:.1f} с для соблюдения rate limit...")
                        time.sleep(wait_time)

                # Запоминаем время начала
                start_time = time.time()

                # Генерируем задачу
                problem = self.generate_single()
                problem["id"] = f"gen_aime_{i + 1}"
                problem["generated_at"] = datetime.now().isoformat()

                # Запоминаем время окончания
                last_call_time = time.time()
                generation_time = last_call_time - start_time

                problems.append(problem)

                # Обновляем описание прогресс-бара
                pbar.set_postfix({
                    "Тема": problem.get('topic', 'N/A'),
                    "Ответ": problem.get('answer', 'N/A'),
                    "Время": f"{generation_time:.1f}s"
                })
                pbar.update(1)

                # Сохраняем чекпоинт
                if checkpoint_path:
                    try:
                        with open(checkpoint_path, 'w', encoding='utf-8') as f:
                            json.dump(problems, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        tqdm.write(f"⚠️ Не удалось сохранить чекпоинт: {e}")

        print(f"\n✅ Генерация завершена! Всего {len(problems)} задач")
        return problems

    def save_problems(
        self,
        problems: List[Dict[str, Any]],
        output_path: str
    ):
        """Сохранение задач в файл"""
        # Убеждаемся, что директория существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Задачи сохранены: {output_path}")

    def generate_and_save(
        self,
        num_problems: int = 30,
        output_dir: str = "data_generation/generated_data"
    ) -> str:
        """Генерация и сохранение задач"""
        # Создаём выходную директорию
        os.makedirs(output_dir, exist_ok=True)

        # Удаляем старые файлы чекпоинтов
        for file in os.listdir(output_dir):
            if file.startswith("checkpoint_") and file.endswith(".json"):
                old_checkpoint = os.path.join(output_dir, file)
                try:
                    os.remove(old_checkpoint)
                    print(f"🗑️  Удалён старый файл чекпоинта: {file}")
                except Exception as e:
                    print(f"⚠️ Не удалось удалить старый чекпоинт: {e}")

        # Задаём путь к чекпоинту
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = os.path.join(output_dir, f"checkpoint_{timestamp}.json")

        # Генерируем задачи (с чекпоинтом)
        problems = self.generate_batch(num_problems, checkpoint_path=checkpoint_path)

        # Сохраняем задачи
        output_path = os.path.join(output_dir, f"aime_generated_{timestamp}.json")
        self.save_problems(problems, output_path)

        # Генерируем статистический отчёт
        self._generate_statistics_report(problems, output_dir, timestamp)

        # Удаляем файл чекпоинта
        if os.path.exists(checkpoint_path):
            try:
                os.remove(checkpoint_path)
                print(f"\n🗑️  Файл чекпоинта удалён")
            except Exception as e:
                print(f"\n⚠️ Не удалось удалить файл чекпоинта: {e}")

        return output_path

    def _generate_statistics_report(
        self,
        problems: List[Dict[str, Any]],
        output_dir: str,
        timestamp: str
    ):
        """Генерация статистического отчёта"""
        # Статистика по темам
        topics = {}
        answers = []

        for problem in problems:
            topic = problem.get("topic", "Неизвестно")
            topics[topic] = topics.get(topic, 0) + 1

            if "answer" in problem:
                answers.append(problem["answer"])

        # Формируем отчёт
        report = f"""# Статистический отчёт по генерации задач AIME

## Основная информация

- **Время генерации**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Количество задач**: {len(problems)}

## Распределение по темам

| Тема | Количество | Доля |
|------|------------|------|
"""

        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(problems) * 100
            report += f"| {topic} | {count} | {percentage:.1f}% |\n"

        if answers:
            report += f"""
## Анализ ответов

- **Средний ответ**: {sum(answers) / len(answers):.2f}
- **Минимальный ответ**: {min(answers)}
- **Максимальный ответ**: {max(answers)}
- **Диапазон ответов**: {min(answers)}-{max(answers)}
"""

        report += f"""
## Список задач

| ID | Тема | Ответ |
|----|------|-------|
"""

        for problem in problems[:10]:  # Отображаем только первые 10
            report += f"| {problem.get('id', 'N/A')} | {problem.get('topic', 'N/A')} | {problem.get('answer', 'N/A')} |\n"

        if len(problems) > 10:
            report += f"\n*(Показаны первые 10 задач; полный список — в JSON-файле)*\n"

        report += f"""
---

*Отчёт сформирован: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        # Сохраняем отчёт
        report_path = os.path.join(output_dir, f"generation_report_{timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📊 Статистический отчёт сохранён: {report_path}")


if __name__ == "__main__":
    # Создаём генератор
    generator = AIMEGenerator()

    # Генерируем 30 задач
    output_path = generator.generate_and_save(num_problems=30)

    print(f"\n✅ Готово! Сгенерированные задачи сохранены в: {output_path}")
