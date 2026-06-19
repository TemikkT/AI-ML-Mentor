import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from schemas.training_result import TrainingResult

"""
Класс создания Json файла с историей ответов и оценки пользователя
"""

class HistoryManager:
    def __init__(self, file_path='data/history.json'): # задаём в параметрах путь в json файлу где хранится информация о вопросе и ответах
        self.file_path = Path(file_path)

        if not self.file_path.exists(): # создаём этот файл если его несуществует
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_history(self) -> list:
        """

        Загружает всю историю обучения

        """
        with open(self.file_path,"r",encoding="utf-8") as f: # Выгружаем все данные из файла, чтобы обновлять его
            return json.load(f)


    def save_result(self, result: TrainingResult) -> None:
        """
        Сохраняет результаты после ответа в Json
        """
        history = self.load_history() # забираем всю историю из файла
        history.append(result.model_dump(mode="json")) # добавляем туда новую

        with open(self.file_path, "w",encoding="utf-8") as f: # сохраняем всё то что мы добавили
            json.dump(history,f,ensure_ascii=False,indent=4)

    def topic_statistics(self, last_n: int = 5):
        """
        Считает средний балл по последним last_n ответам.
        """
        history = self.load_history() # забираем всю историю из файла
        topic_scores = defaultdict(list) # 

        for record in history: # перебираем все словари из истории
            topic_scores[record["topic"]].append(record["score"]) # забираем оттуда топик и его скор
        statistics = {}

        for topic, scores in topic_scores.items(): # начинаем перепибрать топики и их скор
            recent_scores = scores[-last_n:]
            statistics[topic] = round(sum(recent_scores) / len(recent_scores),2) # берём среднее каждого топика

        return statistics
    
    def get_weak_topics(self,threshold: float = 7.0) -> list[str]:
        """
        Возвращает темы,
        где средний балл ниже threshold.

        (функция устарела, больше не используется, 
        теперь работаем с весами топиков, 
        но функция решил оставить, вдруг пригодится)
        """
        stats = self.topic_statistics() # забираем всю статистику о топиках
        weak_topics = []
        
        for topic, avg_score in stats.items(): # перебираем их
            if avg_score < threshold: # если средняя оценка ниже 0.7, то это слабый топик
                weak_topics.append(topic)

        return weak_topics
    
    def get_topic_scores(self, topic: str, last_n: int = 5) -> list[int]:
        """
        Возвращает последние last_n оценок по теме.
        """

        history = self.load_history() # забираем всю историю из файла
        scores = [ # перебираем все скоры на заданом топике и выбраем последние 5 оценок
            record["score"]
            for record in history
            if record["topic"] == topic
        ]

        return scores[-last_n:]
    
    def get_topic_weight(self, topic: str, stats: dict) -> float:
        """
        Возвращает вес к каждой теме, чтобы даже среди слабых тем, чаще выбиралась самая слабая
        """

        if topic not in stats: # если топика нету в статике, отдаём ему изначальный вес 15
            return 15

        score = stats[topic] # достаём оценку на топик
        knowledge_weight = 11 - score # определяем вес данного топика, чем ниже оценка, тем выше его вес
        days = self.days_since_review(topic) # берём день, когда последний раз он задавался

        if days is None: # если дня нету в статике, то время никак не будет влиять на вес
            time_weight = 0
        else:
            time_weight = min(10, days * 0.15) # если он имеется, то берём день у множаем на 0.15
        
        return knowledge_weight + time_weight # суммируем весса (таким образом вес с каждым днём будет только больше)
    
    def last_review(self, topic: str):
        """
        Возвращает время когда вопрос был задан, создано для того, чтобы отслеживать какие вопросы давно не задавались
        """

        history = self.load_history() # забираем всю историю из файла

        topic_history = [record # перебираем опять все оценки топика
            for record in history
            if record["topic"] == topic
        ]

        if not topic_history: # если у него нет оценок, выводим None
            return None

        last = topic_history[-1] # смотрим последний вопрос

        return datetime.fromisoformat(last["timestamp"]) # выводим время когда был задан вопрос
    
    def days_since_review(self,topic: str):
        """
        Расчёт времени когда последний раз задавался топик, будет менять веса так же для старых топиков, которых уже успели забыть
        """
        last = self.last_review(topic) # выводим время когда вопрос был последний раз задан, ну топик последний раз выбран
        if last is None: # если информации нет, выводим None
            return None
        else:
            return (datetime.now() - last).days # иначе выводим разницу в днях, сколько дней прошло с его выбора
