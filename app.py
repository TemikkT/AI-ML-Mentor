from core.LLM_client import LLMClient
from services.QuestionGenerator import QuestionGenerator
from services.AnswerEvaluator import AnswerEvaluator


llm = LLMClient(model_name="deepseek/deepseek-v4-flash") # Создаём объект клиента, который связывает нас с OpenRouter и задаём название модели для использования

generator = QuestionGenerator(llm)
evaluator = AnswerEvaluator(llm)

topic = "Ансамбли"

note = """
Случайный лес и градиентный бустинг.

Основные различия:
- принцип обучения
- достоинства
- недостатки
"""

questions = generator.generator_questions( # Создаём генератор вопроса. Там задаётся структура вопроса и ответ
    topic=topic,
    note=note,
    num_questions=3
)

for question in questions.questions: # перебираем каждый вопрос отдеально

    print("\n" + "=" * 50)
    print(f"Вопрос {question.id}")
    print(question.question)

    user_answer = input("\nВаш ответ: ") # ждём ответ пользователя на вопрос

    evaluation = evaluator.evaluate( # Проверка ответа пользователя, даём оценку и рецензии
        topic=topic,
        question=question.question,
        answer=user_answer
    )

    print(f"\nОценка: {evaluation.score}/10")

    print("\nЧто правильно:")
    for item in evaluation.correct_parts:
        print(f"- {item}")

    print("\nЧто упущено:")
    for item in evaluation.mistakes:
        print(f"- {item}")

    print("\nРекомендация:")
    print(evaluation.feedback)