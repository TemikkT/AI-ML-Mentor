from collections import defaultdict

from services.HistoryManager import HistoryManager

"""
Анализирует историю обучения пользователя.

Отвечает только за статистику.
Не выбирает темы и не взаимодействует с LLM.

Используется для:

- отображения прогресса;
- поиска слабых тем;
- поиска давно не повторяемых тем;
- построения рекомендаций;
- будущей системы Elo.
"""

class ProgressAnalyzer:
    def __init__(self, history: HistoryManager):
        self.history = history

    def average_score(self) -> float: 
        """
        Возвращает общий средний балл пользователя.
        Используется на главной странице приложения.
        """
        sessions = self.history.load_history() # выгружаем всю историю
        scores = [] # Создаём массив со всеми скорами

        for session in sessions: # перебираем сессии
            for result in session["results"]: # далее в сессии перебираем результаты
                scores.append(result["score"]) # смотрим оценку и добавляем в массив

        if not scores: # если оценки нету, возвращаем 0
            return 0

        return round(sum(scores) / len(scores), 2) # Возвращаем средний балл в целом по всем сессиям

    def topic_statistics(self) -> dict[str, float]:
        """
        Возвращает средний балл по каждой теме.
        Пример:
        {
            "Логистическая регрессия": 8.6,
            "SVM": 5.2,
            ...
        }
        """
        return self.history.topic_statistics()

    def weak_topics(self, threshold: float = 6.5) -> list[str]: # Берём слабые топики, если средняя оценка ниже 6.5
        """
        Возвращает темы,
        средний балл которых ниже threshold.
        """
        stats = self.topic_statistics() # берём сердний бал по каждой теме, логика прописана в HistoryManager topic_statistics
        weak = [] # создаём массив со всеми слабыми
        for topic, score in stats.items(): # перебираем топик и его скор в статистике
            if score < threshold: # если скор ниже нашего порога
                weak.append(topic) # добавляем топик

        return weak

    def strong_topics(self, threshold: float = 9.0) -> list[str]: # Берём сильные топики, если средняя оценка выше 9.0
        """
        Возвращает хорошо изученные темы.
        """
        stats = self.topic_statistics() # берём сердний бал по каждой теме, логика прописана в HistoryManager topic_statistics
        strong = [] # создаём массив со всеми сильными
        for topic, score in stats.items(): # перебираем топик и его скор в статистике
            if score >= threshold: # если скор выше порога
                strong.append(topic) # добавляем топик

        return strong

    def topics_without_practice(self, days: int = 14) -> list[str]: # достаём топики у которых давно не было практики
        """
        Возвращает темы,
        которые давно не повторялись.
        """
        stats = self.topic_statistics() # выводим информацию по каждой теме
        forgotten = [] # создаём массив для тех кого забыли

        for topic in stats.keys(): # перебираем топики
            diff = self.history.days_since_review(topic) # смотрим разницу в днях, сколько прошло с момента его последнего упоминания, логика в HistoryManager days_since_review
            if diff is not None and diff >= days: # оцениваем ситуацию
                forgotten.append(topic) # добавляем если его и правду давно не было

        return forgotten

    def solved_questions(self) -> int: # возвращаем количество отвеченных вопросов
        """
        Возвращает количество отвеченных вопросов.
        """
        sessions = self.history.load_history() # выгружаем всю историю
        total = 0
        for session in sessions: # проходимся по всем сессиям
            total += len(session["results"])  # просто добавляем в total все вопросы на которые есть вопрос

        return total

    def solved_sessions(self) -> int: 
        """
        Возвращает количество завершённых тренировок.
        """
        return len(self.history.load_history()) # выгружаем всю историю и смотрим на его длину, длина по сессиям

    def average_by_difficulty(self) -> dict[str, float]: 
        """
        Средний балл по сложности вопроса.
        Возвращает:
        {
            "easy": 9.3,
            "medium": 7.1,
            "hard": 4.8
        }
        """

        sessions = self.history.load_history() # выгружаем всю историю
        data = defaultdict(list) # создаём объект для хранения данных
        for session in sessions: # проходимся по всем сессиям
            for result in session["results"]: # далее идём в results где содержится вся информация о каждом вопросе в сессии
                difficulty = result.get("difficulty", "unknown") # узнаём его сложность
                data[difficulty].append(result["score"]) # добавляем в словарь

        out = {}

        for difficulty, scores in data.items(): # далее перебираем весь словарь
            out[difficulty] = round(sum(scores) / len(scores), 2) # берём среднее каждой сложности

        return out

    def progress_summary(self) -> dict:
        """
        Краткая сводка по обучению.
        Используется на главном экране приложения.
        """
        return {
            "average_score": self.average_score(),
            "sessions": self.solved_sessions(),
            "questions": self.solved_questions(),
            "weak_topics": self.weak_topics(),
            "strong_topics": self.strong_topics()
        }