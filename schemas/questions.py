from typing import List
from pydantic import BaseModel, Field

"""
Класс вопроса. В связи с тем, что нам нужна система которая будет связывать Вопрос - Ответ - Оценка.
То мы не можем просто брать бесконечные строки которые нам даёт модель, парсить их тот ещё ад.
Поэтому мы будем структурировать выводи нашей модели.
"""

class Question(BaseModel):
    id: int = Field(description="Номер вопроса") # Номер вопроса, которая будет связан с номерами ответов и номером оценки, на какой вопрос какая оценка
    question: str = Field(description="Текст вопроса") # Та же история, Текст вопроса будет привязан именно к номеру вопроса
    difficulty: str = Field(description="easy, medium или hard")
    question_type: str = Field(description="theory, coding, comparison")

class QuestionSet(BaseModel): # Делаем массив из 
    questions: List[Question]


