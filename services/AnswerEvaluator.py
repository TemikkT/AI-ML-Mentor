from schemas.evaluation import Evalution
from langchain_core.prompts import PromptTemplate
from schemas.PromptTemplate import EVALUATION_PROMPT

"""
Данный класс написан для Генерации оценки на ответ пользователя
Опять же берётся наш клиент с ллм, в него подаётся топик, вопрос который задавала ллм и ответ пользователя
в PromptTemplate можно посмотреть схему промпта ответа модели
"""


class AnswerEvaluator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def evaluate(self, topic: str, question: str, answer: str) -> Evalution: # на входе подаются топик, вопрос и ответ пользователя на данный вопрос

        prompt = EVALUATION_PROMPT.format(topic=topic,question=question,answer=answer)
        structured_llm = self.llm.get_structured_llm(Evalution) # вызываем метод ллм клиента для генерации ответа
        result = structured_llm.invoke(prompt) # выводим ответ, пока что без stream

        return result