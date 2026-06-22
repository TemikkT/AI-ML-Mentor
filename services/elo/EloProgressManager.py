import json
from pathlib import Path

from config.elo_config import (
    ELO_TOPICS_ORDER,
    NEUTRAL_SCORE,
    SCORE_MULTIPLIER,
    DIFFICULTY_RATING_BOUNDS,
)

"""
Класс для хранения и обновления состояния Elo-режима:
текущий рейтинг каждой темы и факт её разблокировки.

Состояние хранится в отдельном файле (elo_state.json) — снэпшот вида
{topic: {"rating": int, "unlocked": bool}}, обновляется после каждого
ответа пользователя. Это НЕ журнал сессий (для этого есть HistoryManager
с отдельным history_elo.json) — здесь только текущий срез прогресса.

Порядок тем и пороги разблокировки берутся из config.elo_config.ELO_TOPICS_ORDER.
Первая тема в этом списке открыта всегда, остальные открываются по цепочке:
тема N+1 становится unlocked, когда рейтинг темы N достигает её unlock_threshold.
"""


class EloProgressManager:
    def __init__(self, file_path: str = "data/elo_state.json"):
        self.file_path = Path(file_path)
        self.topics_order = [entry["topic"] for entry in ELO_TOPICS_ORDER]
        self.unlock_thresholds = {entry["topic"]: entry["unlock_threshold"] for entry in ELO_TOPICS_ORDER}

        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_state(self._build_initial_state())

    def _build_initial_state(self) -> dict:
        """
        Начальное состояние: первая тема в списке открыта с рейтингом 0,
        все остальные темы закрыты с рейтингом 0.
        """
        state = {}
        for index, topic in enumerate(self.topics_order):
            state[topic] = {
                "rating": 0,
                "unlocked": (index == 0),
            }
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
            raise ValueError(f"Тема '{topic}' не найдена в ELO_TOPICS_ORDER")
        return state[topic]["rating"]

    def is_unlocked(self, topic: str) -> bool:
        state = self._load_state()
        if topic not in state:
            raise ValueError(f"Тема '{topic}' не найдена в ELO_TOPICS_ORDER")
        return state[topic]["unlocked"]

    def get_available_topics(self) -> list[str]:
        """
        Возвращает список тем, доступных пользователю для выбора
        (unlocked=True), в исходном порядке ELO_TOPICS_ORDER.
        """
        state = self._load_state()
        return [topic for topic in self.topics_order if state[topic]["unlocked"]]

    def get_difficulty_for_topic(self, topic: str) -> str:
        """
        Определяет сложность следующего вопроса по текущему рейтингу темы,
        используя жёсткие границы из DIFFICULTY_RATING_BOUNDS.
        """
        rating = self.get_rating(topic)

        for difficulty, (lower, upper) in DIFFICULTY_RATING_BOUNDS.items():
            if upper is None:
                if rating >= lower:
                    return difficulty
            else:
                if lower <= rating < upper:
                    return difficulty

        # Не должно происходить при корректно заданных границах,
        # но на случай дырки в конфиге — безопасный дефолт.
        return "easy"

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
        - проверяет, не пора ли разблокировать следующую тему по цепочке
        - сохраняет обновлённое состояние

        Возвращает обновлённую запись по теме с дополнительным полем
        "newly_unlocked_topic": название темы, которая открылась именно
        в результате ЭТОГО вызова (или None, если ничего не открылось).
        Это явный сигнал для вызывающего кода — не нужно сравнивать
        рейтинг до/после самостоятельно, чтобы понять, произошла ли
        разблокировка прямо сейчас.
        """
        state = self._load_state()

        if topic not in state:
            raise ValueError(f"Тема '{topic}' не найдена в ELO_TOPICS_ORDER")

        delta = self.calculate_delta(score, difficulty)
        new_rating = max(0, state[topic]["rating"] + delta)
        state[topic]["rating"] = new_rating

        newly_unlocked_topic = self._maybe_unlock_next_topic(state, topic)

        self._save_state(state)

        result = dict(state[topic])
        result["newly_unlocked_topic"] = newly_unlocked_topic
        return result

    def _maybe_unlock_next_topic(self, state: dict, topic: str) -> str | None:
        """
        Если рейтинг темы достиг её unlock_threshold — открывает следующую
        тему по порядку (если она ещё не была открыта). Изменяет state на месте.

        Возвращает название только что открытой темы, либо None, если
        ничего не изменилось (порог не достигнут, либо следующая тема
        уже была открыта раньше).
        """
        threshold = self.unlock_thresholds.get(topic)
        if threshold is None:
            return None

        if state[topic]["rating"] < threshold:
            return None

        try:
            current_index = self.topics_order.index(topic)
        except ValueError:
            return None

        next_index = current_index + 1
        if next_index >= len(self.topics_order):
            return None  # это последняя тема в цепочке, дальше открывать нечего

        next_topic = self.topics_order[next_index]

        if state[next_topic]["unlocked"]:
            return None  # уже была открыта раньше — это не новое событие

        state[next_topic]["unlocked"] = True
        return next_topic