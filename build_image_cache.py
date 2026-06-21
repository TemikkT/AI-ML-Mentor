from core.LLM_client import LLMClient

from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner
from services.common.VisionAnalyzer import VisionAnalyzer

"""
Тут мы будем обрабатывать изображения, если повяться новые. запустим его вновь
"""

VAULT_PATH = r"C:\Users\user\Documents\Obsidian"

"""
Создание сервисов
"""
loader = ObsidianLoader(VAULT_PATH)
cleaner = MarkdownCleaner(loader)

llm = LLMClient(model_name="qwen/qwen3-vl-32b-instruct")
vision = VisionAnalyzer(llm)

"""
Загружаем заметки
"""
notes = loader.load_notes()

print("=" * 70)
print(f"Загружено заметок: {len(notes)}")
print("=" * 70)

"""
Считаем количество изображений
"""
total_images = 0

for note in notes:
    cleaner.clean(note)
    total_images += len(note.images)

print(f"Всего найдено изображений: {total_images}")
print()

"""
Обработка
"""
processed = 0

for note_index, note in enumerate(notes, start=1):
    print("=" * 70)
    print(f"[{note_index}/{len(notes)}] {note.title}")
    print("=" * 70)

    cleaner.clean(note)

    for image in note.images:
        processed += 1
        print(
            f"[{processed}/{total_images}] "
            f"{image.name}"
        )
    vision.process_note(note)
print("\nВсе изображения обработаны.")