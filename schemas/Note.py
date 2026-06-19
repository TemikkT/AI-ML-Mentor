from pathlib import Path
from pydantic import BaseModel, Field
from schemas.note_image import NoteImage

"""
Класс для топика из обсидиана, просто так сделаем, небольшой тест
тут имеется:
- Domain это основа, пока что у нас только ML
- Категория 
- название записи (title)
- путь к файлам
- Контент внутри записи, как сырой, так и обработанный от лишнего
- Все изображения внутри записи, просто их названия которые указаны в самой записке
"""

class Note(BaseModel):
    domain: str
    category: str

    title: str
    path: str

    raw_content: str
    cleaned_content: str = ""

    images: list[NoteImage] = Field(default_factory=list)