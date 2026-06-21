import json
from pathlib import Path

from schemas.Note import Note
from schemas.note_image import NoteImage

"""
Класс для обработки всех изображений
Будем использовать отдельную модель чисто для обработки видео
Задача из Изображения получить Текст, который модель сможет распознать
Чтобы при каждом заходе в записку, она не обрабатывала изображение заново
"""


class VisionAnalyzer:
    def __init__(self, llm_client, cache_file: str = "data/image_cache.json"): # определяем тут клиент модели, который и будем заниматься всем анализом, а так же куда сохранять
        self.llm = llm_client # создаём клиента модели
        self.cache_path = Path(cache_file) # задаём путь, куда сохранять информацию об изображениях

        if not self.cache_path.exists(): # если его не существует, то создаём его
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def load_cache(self) -> dict: # функция сохранения загрузки всего содержимого из json

        with open(self.cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
 
    def save_cache(self, cache: dict): # функция сохранения обработанного в json
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)


    def build_prompt(self, image: NoteImage) -> str: # Просто построим промпт и выдадим его, хз зачем тут отдельная функция, так выглядит лучше
        """
        Отправляет изображение Vision-модели.
        """

        prompt = f"""
        Ты — система анализа изображений.
        Тебе дан фрагмент конспекта и изображение.
        Контекст:
        {image.context}
        Твоя задача:
        1. Определи, что изображено.
        2. Объясни, какую идею иллюстрирует изображение.
        3. Не повторяй текст из контекста.
        4. Не оценивай качество конспекта.
        5. Не обращайся к пользователю.
        6. Не соглашайся и не спорь.
        7. Не используй вводные фразы вроде:
        "Да",
        "Верно",
        "Вы совершенно правы",
        "Конечно".

        Ответ должен состоять из 2–4 предложений.
        """
        return prompt

    def process_note(self, note: Note) -> Note: # Обработка записки, получение изображения и его обработка
        cache = self.load_cache() # скачиваем всё из json

        for image in note.images: # перебор всех изображений
            if image.name in cache: # смотрим, какие изображения уже обработанны, встречаются и там и там
                print(f" +Cache: {image.name}") # если они уже обработаны, то не будем проходится по ним дважды, пропускам их
                image.description = cache[image.name]["description"]
                continue

            print(f" -Анализ: {image.name}") # все другие же изображения, которых ещё нет в JSON

            description = self.llm.describe_image(image.path, self.build_prompt(image)) # вызываем функцию describe_image в клиенте модели, чтобы она отправила запрос на OpenRouter
            image.description = description #  сохраняем то, что выдала модель в описание изображения
            cache[image.name] = {"description": description} 

            self.save_cache(cache) # сохраняем это целиком в json уже

        return note