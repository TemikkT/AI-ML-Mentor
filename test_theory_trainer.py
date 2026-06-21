from core.LLM_client import LLMClient

from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner
from services.common.QuestionGenerator import QuestionGenerator
from services.theory.AnswerEvaluator import AnswerEvaluator
from services.common.HistoryManager import HistoryManager
from services.theory.TopicSelector import TopicSelector

from services.theory.TheoryTrainer import TheoryTrainer
from config.config_for_question import obsidian_path


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