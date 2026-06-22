import random
from schemas.Note import Note

"""
Класс выбора темы для вопросов. Нужен он чтобы на каждую тему была своя вероятность
Делить будем так - 
    Логика:
    - Новые темы получают высокий вес (15),
      чтобы чаще попадаться пользователю.
    - Уже изученные темы получают вес
      в зависимости от среднего балла.
      Чем хуже средний балл, тем выше шанс,
      что тема снова выпадет.
"""

NEW_TOPIC_WEIGHT = 15            # вес новой темы для обычного choose_topic (один топик на сессию)
NEW_TOPIC_WEIGHT_INTERVIEW = 10  # вес новой темы для интервью-режима (несколько топиков подряд)


class TopicSelector:
    def __init__(self, history_manager):
        self.history = history_manager

    def choose_topic(self, notes: list[Note]) -> tuple[str, Note]:
        if not notes:
            raise ValueError(
                "Список заметок пуст: не удалось выбрать тему. "
                "Проверь путь к Obsidian vault (obsidian_path) и наличие .md файлов в нём."
            )

        # темы берём из заметок — это источник правды о том, что вообще существует
        all_topics = {note.title for note in notes}  # или note.topic, если у Note есть такое поле
        statistics = self.history.get_statistics()

        weights = []
        topics = list(all_topics)
        for topic in topics:
            if topic in statistics:
                weights.append(self.history.calculate_weight(topic, statistics[topic]))
            else:
                weights.append(NEW_TOPIC_WEIGHT)  # новая тема — высокий вес

        selected_topic = random.choices(topics, weights=weights, k=1)[0]
        selected_note = next((note for note in notes if note.title == selected_topic), None)

        if selected_note is None:
            raise ValueError(f"Note for topic '{selected_topic}' not found")

        return selected_topic, selected_note

    def choose_topics_for_interview(self, notes: list[Note], count: int) -> list[tuple[str, Note]]:
        """
        Выбирает count РАЗНЫХ тем (без повторов) для интервью-режима,
        используя ту же взвешенную логику, что и choose_topic, но
        с отдельным (более низким) весом новой темы — NEW_TOPIC_WEIGHT_INTERVIEW.

        Реализация — последовательный взвешенный выбор без возвращения:
        выбираем одну тему взвешенно, убираем её из пула, выбираем
        следующую из оставшихся, и так count раз. Это математически
        эквивалентно взвешенной выборке без повторов.

        Если count больше, чем доступно тем — возвращает все доступные
        темы (не падает, но и не размножает их искусственно).
        """
        if not notes:
            raise ValueError(
                "Список заметок пуст: не удалось выбрать темы для интервью. "
                "Проверь путь к Obsidian vault (obsidian_path) и наличие .md файлов в нём."
            )

        all_topics = {note.title for note in notes}
        statistics = self.history.get_statistics()

        topics = list(all_topics)
        weights = []
        for topic in topics:
            if topic in statistics:
                weights.append(self.history.calculate_weight(topic, statistics[topic]))
            else:
                weights.append(NEW_TOPIC_WEIGHT_INTERVIEW)

        count = min(count, len(topics))  # не пытаемся выбрать больше тем, чем существует

        selected_topics = []
        remaining_topics = topics[:]
        remaining_weights = weights[:]

        for _ in range(count):
            chosen = random.choices(remaining_topics, weights=remaining_weights, k=1)[0]
            selected_topics.append(chosen)

            chosen_index = remaining_topics.index(chosen)
            remaining_topics.pop(chosen_index)
            remaining_weights.pop(chosen_index)

        result = []
        for topic in selected_topics:
            note = next((n for n in notes if n.title == topic), None)
            if note is None:
                raise ValueError(f"Note for topic '{topic}' not found")
            result.append((topic, note))

        return result
