import json
from pathlib import Path
from config.elo_config import (
    NEUTRAL_SCORE,
    SCORE_MULTIPLIER,
    PRACTICE_DIFFICULTY_RATING_BOUNDS,
)

"""
Класс для хранения и обновления рейтинга практических тем (Python/Pandas/SQL)
в рамках Practice-Elo режима.

В отличие от EloProgressManager (теоретический Elo-режим), здесь:
- темы НЕ выстроены в цепочку и не имеют порога разблокировки — все темы,
  переданные в topics, доступны пользователю для выбора сразу и всегда.
- у каждой темы есть только её собственный рейтинг (без unlocked-флага).
- сложность вопроса определяется текущим рейтингом темы через
  PRACTICE_DIFFICULTY_RATING_BOUNDS (границы шире, чем в теоретическом
  Elo-режиме, так как рост рейтинга по практическим задачам предполагается
  более медленным/затратным).

Состояние хранится в отдельном файле (practice_elo_state.json) — снэпшот
вида {topic: {"rating": int}}, обновляется после каждого ответа.
"""


class PracticeEloProgressManager:
    def __init__(self, topics: list, file_path: str = "data/practice_elo_state.json"):
        self.file_path = Path(file_path)
        self.topics = topics

        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_state(self._build_initial_state())

    def _build_initial_state(self) -> dict:
        state = {}
        for topic in self.topics:
            state[topic] = {"rating": 0}
        return state

    def _load_state(self) -> dict:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self, state: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=4)

    def get_rating(self, topic: str) -> int:
        state = self._load_state()
        if topic not in state:
            raise ValueError(f"Тема '{topic}' не найдена в списке тем PracticeEloProgressManager")
        return state[topic]["rating"]

    def calculate_delta(self, score: int, difficulty: str) -> int:
        """
        очки = (score - NEUTRAL_SCORE) * множитель_сложности
        """
        if difficulty not in SCORE_MULTIPLIER:
            raise ValueError(f"Неизвестная сложность '{difficulty}', ожидались: {list(SCORE_MULTIPLIER.keys())}")

        return round((score - NEUTRAL_SCORE) * SCORE_MULTIPLIER[difficulty])

    def apply_score(self, topic: str, score: int, difficulty: str) -> dict:
        """
        Применяет результат ответа к рейтингу темы:
        - считает delta по формуле
        - обновляет рейтинг (не ниже 0)
        - сохраняет обновлённое состояние на диск

        Возвращает обновлённую запись по теме: {"rating": int}
        """
        state = self._load_state()

        if topic not in state:
            raise ValueError(f"Тема '{topic}' не найдена в списке тем PracticeEloProgressManager")

        delta = self.calculate_delta(score, difficulty)
        new_rating = max(0, state[topic]["rating"] + delta)
        state[topic]["rating"] = new_rating

        self._save_state(state)

        return state[topic]

    def get_difficulty_for_topic(self, topic: str) -> str:
        """
        Определяет сложность следующего вопроса по текущему рейтингу темы,
        используя жёсткие границы из PRACTICE_DIFFICULTY_RATING_BOUNDS.
        """
        rating = self.get_rating(topic)

        for difficulty, (lower, upper) in PRACTICE_DIFFICULTY_RATING_BOUNDS.items():
            if upper is None:
                if rating >= lower:
                    return difficulty
            else:
                if lower <= rating < upper:
                    return difficulty

        # Не должно происходить при корректно заданных границах,
        # но на случай дырки в конфиге — безопасный дефолт.
        return "easy"