import json
from schemas.questions import QuestionSet
from schemas.PromptTemplate import QUESTION_PROMPT

"""
Создаём класс вопроса и ответа модели. В инициализации подаётся наша модель LLM, которую мы создали в LLMClient
Далее функция генерации вопроса и получение ответа.
"""

class QuestionGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client # Получение LLM клиента, название модели, температура. В общем нужный нам класс

    def generator_questions(self, topic: str, note: str, num_questions: int = 5): # задаём параметры вопроса. Топик, Какая запись, количество вопросов
        prompt = QUESTION_PROMPT.format( # Берём формат ответа который мы сохранили в PromptTemplate. Берём из него всё что нам нужно
            topic=topic, # Топик, какая тема
            note=note, # Какая запись нас интересует именно из этой темы
            num_questions=num_questions, # количество вопросов которые задаст модель
        )

        structured_llm = self.llm.get_structured_llm(QuestionSet) # Используем функцию построения ответа модели по нашей схеме, чтобы вызов был в виде JSON
        result = structured_llm.invoke(prompt) # Выводим то что нам сказала модель

        return result