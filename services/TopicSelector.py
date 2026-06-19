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

class TopicSelector:
    def __init__(self, history_manager):
        self.history = history_manager

    def choose_topic(self, notes: list[Note]) -> tuple[str, Note]:
        if not notes: # если записок вообще никаких не нашли
            raise ValueError(
                "Список заметок пуст: не удалось выбрать тему. "
                "Проверь путь к Obsidian vault (obsidian_path) и наличие .md файлов в нём."
            )
        
        # темы берём из заметок — это источник правды о том, что вообще существует
        all_topics = {note.title for note in notes} # перебираем вообще не топики которые есть в записке
        statistics = self.history.get_statistics() # берём статистику всех топиков

        weights = [] # создаём массив для содержания весов топиков
        topics = list(all_topics) # кортеж для содержания топиков
        for topic in topics: # перебор топиков
            if topic in statistics: # если у топика есть статистика, он есть в стории
                weights.append(self.history.calculate_weight(topic, statistics[topic])) # Добываем его вес при помощи HistoryManager и добавляем в массив весов
            else:
                weights.append(15)  # если топик ещё на задавался, даём ему вес 15

        selected_topic = random.choices(topics, weights=weights, k=1)[0] # выбираем рандомный топик, смотря на веса, чем вес выше, тем вероятно топика выше
        selected_note = next((note for note in notes if note.title == selected_topic), None) # берём записку данного топика, пока что необработанная

        if selected_note is None: # если записка пустая, или её нету
            raise ValueError(f"Note for topic '{selected_topic}' not found") # записка не была найдена

        return selected_topic, selected_note # возвращаем топик и его записку
