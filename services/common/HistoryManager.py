import json
from pathlib import Path
from datetime import datetime

from schemas.training_result import QuestionResult, TrainingSession



"""
Класс создания Json файла с историей ответов и оценки пользователя
Это некий класс Аналитики истории, она нужна для более подробного адаптивного обучения
"""

class HistoryManager:
    def __init__(self, file_path: str = "app/data/history.json"): # получение файла со всеми сессиями, историей обучения
        self.file_path = Path(file_path) 

        if not self.file_path.exists(): # если файл не существует, то осздаём его
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_history(self) -> list:
        """
        Загружает историю обучения.
        """
        with open(self.file_path, "r", encoding="utf-8") as f: # читаем файл и заружаем его в List
            return json.load(f)

    def save_session(self, session: TrainingSession):
        """
        Сохраняет завершённую тренировочную сессию.
        """
        history = self.load_history() # выгружаем всё из файла Load, на выходе получаем List TrainingSession не забываем
        history.append(session.model_dump(mode="json")) # добавляем информацию сессии которую только что обработали

        with open(self.file_path, "w", encoding="utf-8") as f: # открываем файл и загружаем внутрь
            json.dump(history, f, ensure_ascii=False, indent=4)

    def get_topic_sessions(self, topic: str) -> list:
        """
        Возвращает все сессии данной темы.
        """
        history = self.load_history() # выгружаем всё из файла Load, на выходе получаем List TrainingSession не забываем
        return [ # перебираем каждую тему из истории. Обращаемся прямо как в Пандасе, берём именно topic в переборе и возвращаем его
            session
            for session in history
            if session["topic"] == topic
        ]
    
    def get_last_sessions(self, topic: str, last_n_sessions: int | None = None) -> list:
        """
        Получение последних тем для отработки плохих вопросов 
        или чтобы исключить повторение вопросов
        """

        sessions = self.get_topic_sessions(topic)
        sessions = sorted(sessions, key=lambda s: s["finished_at"])

        if last_n_sessions is not None:
            sessions = sessions[-last_n_sessions:]
            return sessions
        else:
            return None


    def get_topic_scores(self, topic: str, last_n_sessions: int | None = None) -> list[int]:
        """
        Оценки пользователя по теме.
        Если last_n_sessions указан, берутся только результаты
        из последних N сессий (по finished_at), а не последних N ответов.
        """

        sessions = self.get_topic_sessions(topic) # сначала вызываем прошлую функцию для получения нужного топика
        sessions = sorted(sessions, key=lambda s: s["finished_at"]) # сортировка по времени, чтобы взять и вправду последние

        if last_n_sessions is not None:
            sessions = sessions[-last_n_sessions:]
        scores = []
        for session in sessions: # проходимся по сессиям 
            for result in session["results"]: # проходимся по всем результатам каждой сессии и забираем скор
                scores.append(result["score"])

        return scores

    def get_average_score(self, topic: str, last_n: int = 2) -> float | None:
        """
        Средний балл по последним last_n сессиям темы.
        """

        scores = self.get_topic_scores(topic, last_n_sessions=last_n) # вызываем прошлую функцию и берём нужный нам топик и его последние 2 сессии
        if not scores: # если же ничего нету, выводим None
            return None

        return round(sum(scores) / len(scores), 2) # Получаем средний скор

    def topic_statistics(self, last_n: int = 2) -> dict[str, float]: # получаем последние 2 сессии, на выходе будет словарь. Название топика и среднее значение
        """
        Средний балл по каждой теме (по последним last_n сессиям).
        """
        history = self.load_history() # выдругаем сессию
        topics = {session["topic"] for session in history} # находим все топики, за последние секции

        statistics = {}

        for topic in topics: # перебираем топики
            average = self.get_average_score(topic, last_n) # берём топик и их последние 2 сессии
            if average is not None: 
                statistics[topic] = average # сохраняем это в статистике. В итоге получаем Топик и его статистика за последние 2 сессии

        return statistics

    def get_last_review(self, topic: str): # подаём название топика, который хотим найти
        """
        Когда тема повторялась последний раз.
        """
        sessions = self.get_topic_sessions(topic) # получаем все сессии с данными топиком

        if not sessions:
            return None

        sessions = sorted(sessions, key=lambda s: s["finished_at"]) # сортируем по времени
        return datetime.fromisoformat(sessions[-1]["finished_at"]) # берём по времени нужный нам

    def days_since_review(self, topic: str): # подаём название топика, который хотим найти
        """
        Сколько дней прошло с последнего повторения темы.
        """
        last = self.get_last_review(topic) # Находим опять же последнюю сессия данного топика
        if last is None:
            return None

        return (datetime.now() - last).days # считаем сколько дней прошло с урока с ним

    def get_sessions_count(self, topic: str) -> int: # считаем количество топика в сеансах
        """
        Сколько раз проходили тему.
        """
        return len(self.get_topic_sessions(topic)) # выводим количество сеансов с данными топиком
    

    def get_statistics(self, last_n: int = 2) -> dict: # статистка по всем топикам, уже был подобдный запрос, но он считал именно по 1 топику
        """
        Возвращает статистику сразу по всем темам.
        {
            topic:
            {
                average_score,
                sessions,
                last_review,
                days_since_review
            }
        }
        """
        history = self.load_history() # выгружаем историю обучения
        topics = { # перебираем все топики пройдясь по сессиям
            session["topic"]
            for session in history
        }

        statistics = {}

        for topic in topics: # перебираем топики и сохраняем в статистику информацию каждого из них
            statistics[topic] = {
                "average_score": self.get_average_score(topic, last_n),
                "sessions": self.get_sessions_count(topic),
                "last_review": self.get_last_review(topic),
                "days_since_review": self.days_since_review(topic)
            }

        return statistics

    def get_statistics_topic(self, topic: str, last_n: int = 2) -> dict: # Вернуть ПОЛНУЮ статистику по топику
        """
        Возвращает статистику сразу по одному топику
        {
            topic:
            {
                average_score,
                sessions,
                last_review,
                days_since_review
            }
        }
        """
        statistics = {}

        statistics[topic] = { # тут уже не делаем перебор, а просто берём один топик
            "average_score": self.get_average_score(topic, last_n),
            "sessions": self.get_sessions_count(topic),
            "last_review": self.get_last_review(topic),
            "days_since_review": self.days_since_review(topic)
        }
        return statistics

    def calculate_weight(self, topic: str, stat: dict) -> float: # расчёт веса топика который подаётся
        weight = 0 # изначально вес нулевой
        average = stat["average_score"] # подаём ему статистику
        weight += 11 - (average or 0) # расчитываем вес в зависимости от оценки
        days = stat["days_since_review"] # берём день последнего
        if days is not None:
            weight += min(days * 0.25, 10) # перерасчитываем вес по дням

        sessions = stat["sessions"] 
        weight += max(0, 5 - sessions)

        return max(weight, 1)

    def get_topic_weight(self, topic: str) -> float: # взять вес определённого топика, нужно для TopicSelector
        stat = self.get_statistics_topic(topic, 2) # Получаем статистику этого топика
        return self.calculate_weight(topic, stat[topic]) # расчитываем его вес

