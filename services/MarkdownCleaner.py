from schemas.Note import Note
from schemas.note_image import NoteImage
from pathlib import Path

import re


class MarkdownCleaner:
    def __init__(self, loader):
        self.loader = loader

    def clean(self, note: Note) -> Note:
        """
        Полностью очищает markdown-заметку.
        """
        cleaned = note.raw_content
        cleaned = self.replace_images(cleaned)
        cleaned = self.normalize_text(cleaned)
        images = []

        for image_name in self.extract_images(note.raw_content):

            context = self.extract_context(cleaned, image_name)
            image_path = self.loader.find_image_path(image_name)
            images.append(NoteImage(name=image_name, path=image_path, context=context))

        note.cleaned_content = cleaned
        note.images = images

        return note

    def extract_images(self, text: str) -> list[str]:
        """
        Извлекает названия всех изображений.
        """
        return re.findall(r'!\[\[(.*?)\]\]', text)

    def replace_images(self, text: str) -> str:
        """
        Заменяет изображения
        на специальные маркеры.
        """
        return re.sub(r'!\[\[(.*?)\]\]', r'[IMAGE:\1]',text)

    def extract_context(self, text: str, image_name: str, paragraphs_before: int = 2) -> str:
        paragraphs = text.split("\n\n")
        marker = f"[IMAGE:{image_name}]"

        for index, paragraph in enumerate(paragraphs):
            if marker in paragraph:
                start = max(0, index - paragraphs_before)
                context = "\n\n".join(paragraphs[start:index])
                context = re.sub(r"\[IMAGE:.*?\]", "", context)
                context = context[-500:]

                return context.strip()

        return ""

    def normalize_text(self, text: str) -> str:
        """
        Убирает лишний markdown.
        """
        # Убираем разделители
        text = re.sub(r'^_{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)

        # Убираем лишние пробелы
        text = re.sub(r'[ \t]+', ' ', text)

        # Убираем больше двух переносов подряд
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()
    

