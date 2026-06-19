from datetime import datetime
from pydantic import BaseModel, Field

"""
Класс для сохранения ответа пользователя на тот или иной вопрос в том или ином топике
Создан для сохранения ответов пользователя для адаптивного обучения
Модель будет видеть оценки пользователя на ту или иную тему, по тем или иным вопросам
и будет адаптивно учить пользователя, стараться задавать больше вопросов на эту тему
так же добавляем время для вопроса, чтобы система могла выбрать то, что давно не спрашивала
"""

class QuestionResult(BaseModel):
    topic: str

    question: str
    answer: str
    difficulty: str
    
    score: int

    correct_parts: list[str]
    mistakes: list[str]
    feedback: str

    timestamp: datetime = Field(default_factory=datetime.now)


"""
Этот класс уже для хранение для целлой сессии. Вся информация нужна отсюда, чтобы
найти все самые тонкие пробелы в знаниях и ещё сильнее обновить адаптинове обучение у модели
Допустим - Теперь модель будет знать, какой топик был неделю назад, сколько я отвечал на вопросы
сколько вопросов было и средняя оценка.
"""

class TrainingSession(BaseModel):
    topic: str

    started_at: datetime
    finished_at: datetime | None = None

    results: list[QuestionResult] = []

    average_score: float = 0