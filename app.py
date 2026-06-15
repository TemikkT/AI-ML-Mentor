from core.LLM_client import LLMClient
from services.QuestionGenerator import QuestionGenerator



llm = LLMClient( # Создаём объект клиента, который связывает нас с OpenRouter и задаём название модели для использования
    model_name = 'deepseek/deepseek-v4-flash'
)

generator = QuestionGenerator(llm) # Создаём генератор вопроса. Там задаётся структура вопроса и ответа
topic = "Ансамбли"
note = """
Случайный лес, градиентный бустинг —
метод оценки параметров модели.

Идея:
Чем отличаются,
Особенности каждого,
принципы обучения.
"""

questions = generator.generator_questions(topic=topic, note=note, num_questions=5) # Вызываем функцию генерации ответов модели
for q in questions.questions: # выводим каждую деталь ответа отдеально
    print(q.id) # АЙДИ ОТВЕТА 
    print(q.question) # САМ ВОПРОС
    print(q.difficulty) # СЛОЖНОСТЬ ВОПРОСА
    print(q.question_type) # ТИП ВОПРОСА, ТЕОРИЯ КОД ИЛИ ЧЁТ ЕЩЁ