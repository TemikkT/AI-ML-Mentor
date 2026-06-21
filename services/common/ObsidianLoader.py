from pathlib import Path
from schemas.Note import Note
from config.config_for_question import DOMAIN_MAPPING

"""
Класс для выгрузки контента из Обсидиана

Структура:
│
├── load_notes() - Выгружаем все md файлы
│
├── _find_markdown_files() - Находим все md файлы
│
├── _read_file() - читаем сам md файл
│
├── _extract_domain_category() - получаем domain и топик
│
└── _create_note() - Создаём объект Note со всей информацией из записки
"""


class ObsidianLoader:
    IGNORE_FOLDERS = {".obsidian", "cache", ".git", "__pycache__"}

    def __init__(self, vault_path: str): # на вход подаётся то, где находится записка
        self.vault_path = Path(vault_path)

    def load_notes(self) -> list[Note]:
        """
        Загружает все markdown-файлы из Obsidian.
        """
        notes = []
        markdown_files = self._find_markdown_files() # находим все md файлы и сохраняем их

        for path in markdown_files: # перебираем путь к каждому md файлу
            note = self._create_note(path) # создаём записку, в которой будет хранится вся информация md файла. Вся логика Note обозначена в schemas/Note.py
            notes.append(note) # добавляем в notes

        return notes

    def _find_markdown_files(self) -> list[Path]:
        """
        Находит все .md файлы,
        пропуская служебные папки.
        """

        markdown_files = []

        for file in self.vault_path.rglob("*.md"): # перебираем файлы и ищем расширение md
            if any(folder in file.parts for folder in self.IGNORE_FOLDERS): # если же они находятся в директориях, которые сказано игнорировать, по типу директории с изображениями
                continue # то пропускаем
            markdown_files.append(file) # иначе сохраняем

        return markdown_files

    def _read_file(self, path: Path) -> str:
        """
        Читает markdown-файл.
        """
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_domain_category(self, path: Path) -> tuple[str, str]:
        """
        Определяет domain и category
        по расположению markdown-файла.
        """
        relative = path.relative_to(self.vault_path)
        parts = relative.parts

        # Если заметка лежит прямо в корне Vault
        if len(parts) == 1:
            return "General", "General"

        folder = parts[0]
        domain = DOMAIN_MAPPING.get(folder, folder)
        category = folder

        return domain, category

    def _create_note(self, path: Path) -> Note: # создание schemas/Note.py класса
        """
        Создаёт объект Note.
        """
        content = self._read_file(path) # загружаем контент
        domain, category = self._extract_domain_category(path) # сохранем главный домент, по базе это Машинное обучение и Категории. Пример - classic machine learning
        title = path.stem # берём название топиков

        return Note(
            domain=domain,
            category=category,
            title=title,
            path=str(path),
            raw_content=content
        )
    
    def find_image_path(self, image_name: str) -> str: # данная функция нужна только для обработки изображений
        """
        Ищет изображение по всему Obsidian Vault.
        """
        matches = list(self.vault_path.rglob(image_name))
        if matches:
            return str(matches[0])

        return ""