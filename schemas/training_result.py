from datetime import datetime
from pydantic import BaseModel, Field

"""
Класс для сохранения ответа пользователя на тот или иной вопрос в том или ином топике
Создан для сохранения ответов пользователя для адаптивного обучения
Модель будет видеть оценки пользователя на ту или иную тему, по тем или иным вопросам
и будет адаптивно учить пользователя, стараться задавать больше вопросов на эту тему
так же добавляем время для вопроса, чтобы система могла выбрать то, что давно не спрашивала
"""

class TrainingResult(BaseModel):
    topic: str

    question: str
    
    score: int

    timestamp: datetime = Field(default_factory=datetime.now)