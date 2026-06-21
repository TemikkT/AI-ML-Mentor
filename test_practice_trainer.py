from core.LLM_client import LLMClient

from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner
from services.common.QuestionGenerator import QuestionGenerator
from services.practice.PracticeEvaluator import PracticeEvaluator
from services.common.HistoryManager import HistoryManager
from services.practice.PracticeSelector import PracticeSelector
from services.prompt_template.CodeExecutor import CodeExecutor
from services.practice.PracticeTrainer import PracticeTrainer

from config.config_for_question import (
    obsidian_path,
    practice_history_path,
    CODE_EXECUTION_TIMEOUT,
)
from config.prompts import PRACTICE_QUESTION_PROMPT


# -----------------------------
# Создание сервисов
# -----------------------------

llm = LLMClient(model_name="deepseek/deepseek-v4-flash")

loader = ObsidianLoader(obsidian_path)
cleaner = MarkdownCleaner(loader)

# Отдельная история для тренажёра — не смешивается с историей теории.
history = HistoryManager(file_path=practice_history_path)

selector = PracticeSelector(history)

# Тот же QuestionGenerator, что и в теории, но с другим промптом —
# именно для этого в QuestionGenerator добавлен параметр prompt_template.
generator = QuestionGenerator(llm, prompt_template=PRACTICE_QUESTION_PROMPT)
evaluator = PracticeEvaluator(llm)
code_executor = CodeExecutor(timeout=CODE_EXECUTION_TIMEOUT)


trainer = PracticeTrainer(
    loader=loader,
    cleaner=cleaner,
    topic_selector=selector,
    generator=generator,
    evaluator=evaluator,
    history=history,
    code_executor=code_executor,
)


# -----------------------------
# Начало тренировки
# -----------------------------

trainer.Start_session()

print("=" * 70)
print(f"Тема: {trainer.current_topic}")
print("=" * 70)


# -----------------------------
# Проходим все вопросы
# -----------------------------

while True:

    question = trainer.ask_question()

    if question is None:
        break

    print()
    print("-" * 70)
    print(f"Задача {trainer.current_question + 1}")
    print(question.question)
    print()
    print("Введи код решения. Если тема предполагает выполнение —")
    print("не забудь вывести результат через print().")
    print("Ввод многострочный: пустая строка завершает ввод кода.")
    print()

    while True:
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        answer = "\n".join(lines)

        execution_result = trainer.check_code(answer)

        # execution_result is None означает, что тема не предполагает выполнение (например, SQL на этой итерации) — отправляем как есть.
        if execution_result is None or execution_result.success:
            break

        print()
        print("-" * 70)
        if execution_result.timed_out:
            print("Код не успел выполниться за отведённое время (timeout).")
        else:
            print("Код выполнился с ошибкой:")
            print(execution_result.stderr)
        print("-" * 70)
        print()

        choice = input("Переписать код заново (R) или отправить как есть на оценку (S)? [R/S]: ").strip().lower()
        if choice == "s":
            break

        print()
        print("Хорошо, попробуй снова. Ввод многострочный, пустая строка завершает ввод.")
        print()

    result = trainer.submit_answer(answer)

    print("\nОценка:", result.score)
    print()

    print("Что правильно:")

    for item in result.correct_parts:
        print("  +", item)

    print()

    print("Ошибки:")

    for item in result.mistakes:
        print("  -", item)

    print()

    print("Комментарий:")
    print(result.feedback)

    if trainer.next_question() is None:
        break


# -----------------------------
# Завершаем тренировку
# -----------------------------

session = trainer.finish_session()

print()
print("=" * 70)

if not session.results:
    print("Сессия не сохранена — пользователь не ответил ни на один вопрос")
    print("=" * 70)
else:
    print("Сессия завершена")
    print("=" * 70)

    print(f"Средний балл: {session.average_score:.2f}")

    print()

    print("Задачи:")

    for r in session.results:
        print(f"{r.score}/10 — [{r.difficulty}] {r.question}")