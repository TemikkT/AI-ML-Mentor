from core.LLM_client import LLMClient

from services.ObsidianLoader import ObsidianLoader
from services.MarkdownCleaner import MarkdownCleaner
from services.QuestionGenerator import QuestionGenerator
from services.AnswerEvaluator import AnswerEvaluator
from services.HistoryManager import HistoryManager
from services.TopicSelector import TopicSelector

from config.TheoryTrainer import TheoryTrainer
from config.theory_config import obsidian_path


# -----------------------------
# Создание сервисов
# -----------------------------

llm = LLMClient(model_name="deepseek/deepseek-v4-flash")

loader = ObsidianLoader(obsidian_path)
cleaner = MarkdownCleaner(loader)

history = HistoryManager()

selector = TopicSelector(history)

generator = QuestionGenerator(llm)
evaluator = AnswerEvaluator(llm)


trainer = TheoryTrainer(
    loader=loader,
    cleaner=cleaner,
    topic_selector=selector,
    generator=generator,
    evaluator=evaluator,
    history=history
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
    print(f"Вопрос {trainer.current_question + 1}")
    print(question.question)
    print()

    answer = input("> ")

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
print("Сессия завершена")
print("=" * 70)

print(f"Средний балл: {session.average_score:.2f}")

print()

print("Вопросы:")

for r in session.results:
    print(f"{r.score}/10 — {r.question}")