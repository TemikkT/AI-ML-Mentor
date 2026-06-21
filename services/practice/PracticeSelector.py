import random
from schemas.Note import Note
from config.config_for_question import PRACTICE_TOPICS

"""
Аналог TopicSelector для тренажёра.

Отличие от TopicSelector: темы тренажёра — это не "все темы из заметок",
а только те заметки, чей title совпадает со списком PRACTICE_TOPICS
из practice_config.py (заметки лежат в общем Obsidian vault, в категории
"Аналитика данных и Python", но используется не вся категория целиком,
а конкретный заданный список).

Логика взвешивания тем (новая тема = вес 15, чем хуже балл/чем давнее
повтор — тем выше вес) полностью идентична TopicSelector — используем
тот же history_manager и тот же calculate_weight, никакой новой логики
весов здесь не вводится.
"""


class PracticeSelector:
    def __init__(self, history_manager):
        self.history = history_manager

    def choose_topic(self, notes: list[Note]) -> tuple[str, Note]:
        # Берём только те заметки, что входят в список тем тренажёра.
        practice_notes = [note for note in notes if note.title in PRACTICE_TOPICS]

        if not practice_notes:
            raise ValueError(
                "Среди заметок не найдено ни одной темы для тренажёра. "
                f"Ожидались темы: {PRACTICE_TOPICS}. "
                "Проверь, что соответствующие заметки существуют в Obsidian vault "
                "и их title точно совпадает с PRACTICE_TOPICS."
            )

        all_topics = {note.title for note in practice_notes}
        statistics = self.history.get_statistics()

        weights = []
        topics = list(all_topics)
        for topic in topics:
            if topic in statistics:
                weights.append(self.history.calculate_weight(topic, statistics[topic]))
            else:
                weights.append(15)  # новая тема — высокий вес

        selected_topic = random.choices(topics, weights=weights, k=1)[0]
        selected_note = next((note for note in practice_notes if note.title == selected_topic), None)

        if selected_note is None:
            raise ValueError(f"Note for topic '{selected_topic}' not found")

        return selected_topic, selected_note
