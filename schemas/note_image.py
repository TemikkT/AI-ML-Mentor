from pydantic import BaseModel

"""
Класс для хранения изображения из топиков
"""

class NoteImage(BaseModel):
    name: str

    # Полный путь до картинки
    path: str

    # Контекст перед картинкой
    context: str

    # Описание Vision-моделью
    description: str = ""