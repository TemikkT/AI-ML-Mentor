from pydantic import BaseModel, Field
from typing import List

"""
Класс небольшого БД для хранения и вывода всех результатов пользователя
Тут есть - Оценка, Что сказано правильно, Чего не хватает и сказано неверно, Что нужно было сказать или что нужно подучить
"""

class Evalution(BaseModel):
    score: int = Field(description="Оценка от 1 до 10")

    correct_parts: List[str] = Field(description="Что пользователь ответил правильно")

    mistakes: List[str] = Field(description="Что отсутствует или неверно")

    feedback: str = Field(description="Краткая рекомендация по улучшению ответа")