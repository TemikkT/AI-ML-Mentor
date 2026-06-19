from pathlib import Path
from schemas.Note import Note
from config.domains import DOMAIN_MAPPING

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
        markdown_files = self._find_markdown_files()

        for path in markdown_files:
            note = self._create_note(path)
            notes.append(note)

        return notes

    def _find_markdown_files(self) -> list[Path]:
        """
        Находит все .md файлы,
        пропуская служебные папки.
        """

        markdown_files = []

        for file in self.vault_path.rglob("*.md"):
            if any(folder in file.parts for folder in self.IGNORE_FOLDERS):
                continue
            markdown_files.append(file)

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

    def _create_note(self, path: Path) -> Note:
        """
        Создаёт объект Note.
        """
        content = self._read_file(path)
        domain, category = self._extract_domain_category(path)
        title = path.stem

        return Note(
            domain=domain,
            category=category,
            title=title,
            path=str(path),
            raw_content=content
        )
    
    def find_image_path(self, image_name: str) -> str:
        """
        Ищет изображение по всему Obsidian Vault.
        """
        matches = list(self.vault_path.rglob(image_name))
        if matches:
            return str(matches[0])

        return ""