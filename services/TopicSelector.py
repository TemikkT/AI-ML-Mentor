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
    def __init__(self,history_manager):
        self.history = history_manager

    def choose_topic(self, notes: list[Note]) -> Note:
        """
        Выбирает тему для следующего занятия.
        В итоге выбор происходит среди ВСЕХ тем,
        но с разной вероятностью.
        """

        stats = self.history.topic_statistics() # Получаем средние оценки пользователя

        topics = []
        weights = []

        for index in range(0, len(notes)): # Проходимся по всем существующим заметкам

            topics.append(notes[index].title)

            if notes[index].title not in stats: # Если тема ещё ни разу не изучалась
                weights.append(15) # Даем высокий вес, чтобы познакомить пользователя с новой темой

            else:
                score = stats[notes[index].title]
                """
                Чем ниже оценка,
                тем выше вероятность повторения темы.
                10 баллов -> вес 1
                9 баллов -> вес 2
                3 балла -> вес 8
                """
                weight = max(1, 11 - score)
                weights.append(weight)

        # Выбираем одну тему с учетом рассчитанных весов
        out_index = random.choices(population=range(len(topics)), weights=weights, k=1)[0]

        return topics[out_index], notes[out_index], weights[out_index]
