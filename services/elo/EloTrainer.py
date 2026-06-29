from datetime import datetime
import json
import re

from services.common.QuestionGenerator import QuestionGenerator
from services.elo.EloProgressManager import EloProgressManager
from services.common.HistoryManager import HistoryManager
from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner

from config.config_for_question import cache_path, QUESTIONS_PER_SESSION
from schemas.training_result import TrainingSession, QuestionResult

"""
EloTrainer — стейт-машина сессии Elo-режима.

Отличия от TheoryTrainer:
- Тема НЕ выбирается случайно: пользователь выбирает её сам заранее
  (например, из EloProgressManager.get_available_topics()) и передаёт
  явным аргументом в Start_session(topic). Внутри EloTrainer темы
  не сравниваются и не взвешиваются — это не его ответственность.
- Сложность вопроса определяется текущим рейтингом темы
  (EloProgressManager.get_difficulty_for_topic), а не задаётся LLM
  свободно "от простого к сложному".
- После каждого ответа (submit_answer) рейтинг темы обновляется
  немедленно через EloProgressManager.apply_score — следующий вопрос
  в той же сессии будет уже учитывать новый рейтинг.
- Сессия сохраняется ДВАЖДЫ: в общий history (используется и Theory,
  и в будущем Interviewer-режимом) и в отдельный history_elo
  (используется QuestionGenerator для подсветки слабых мест именно
  внутри Elo-режима).

ask_question/next_question идентичны TheoryTrainer — порядок прохождения
вопросов внутри сессии не отличается от других режимов.
"""


class EloTrainer:
    def __init__(self, loader: ObsidianLoader, cleaner: MarkdownCleaner,
                 generator: QuestionGenerator, evaluator,
                 progress_manager: EloProgressManager,
                 history: HistoryManager, history_elo: HistoryManager):
        self.current_note = None
        self.current_topic = None
        self.current_difficulty = None
        self.questions = []
        self.current_question = 0
        self.session = None

        self.loader = loader
        self.cleaner = cleaner
        self.generator = generator
        self.evaluator = evaluator
        self.progress = progress_manager
        self.history = history
        self.history_elo = history_elo

    def Start_session(self, topic: str):
        if not self.progress.is_unlocked(topic):
            raise ValueError(
                f"Тема '{topic}' пока не открыта. "
                "Сначала набери достаточный рейтинг в предыдущей теме по порядку."
            )

        self.questions = []
        self.current_question = 0
        self.current_topic = topic

        notes = self.loader.load_notes()
        self.current_note = next((note for note in notes if note.title == topic), None)

        if self.current_note is None:
            raise ValueError(
                f"Заметка для темы '{topic}' не найдена в Obsidian vault. "
                "Проверь, что название темы в ELO_TOPICS_ORDER точно совпадает с title заметки."
            )

        self.current_note = self.cleaner.clean(self.current_note)

        try:
            with open(cache_path, "r", encoding="utf-8") as f:  # достаём JSON с обработанными изображениями
                image_note = json.load(f)
        except FileNotFoundError:
            # VisionAnalyzer ещё не создавался в этом запуске и не успел
            # инициализировать файл кэша — считаем кэш пустым.
            image_note = {}

        pattern = re.compile(r"\[IMAGE:([^\]]+)\]")
        self.current_note.cleaned_content = pattern.sub(lambda m: image_note.get(m.group(1), \
                        {}).get("description", m.group(0)), self.current_note.cleaned_content)

        self.current_difficulty = self.progress.get_difficulty_for_topic(topic)

        self.questions = self.generator.generator_questions(
            topic=self.current_topic,
            note=self.current_note.cleaned_content,
            num_questions=QUESTIONS_PER_SESSION,
            difficulty=self.current_difficulty,
        )

        self.session = TrainingSession(topic=self.current_topic, started_at=datetime.now(), results=[])

        return self.questions

    def ask_question(self):
        if not self.questions or self.current_question >= len(self.questions.questions):
            return None

        return self.questions.questions[self.current_question]

    def submit_answer(self, answer: str):
        current = self.questions.questions[self.current_question]

        review = self.evaluator.evaluate(
            topic=self.current_topic,
            question=current.question,
            answer=answer
        )

        result = QuestionResult(
            topic=self.current_topic,
            question=current.question,
            answer=answer,
            difficulty=self.current_difficulty,

            score=review.score,
            correct_parts=review.correct_parts,
            mistakes=review.mistakes,
            feedback=review.feedback
        )

        self.session.results.append(result)

        # Рейтинг обновляется немедленно после каждого ответа — следующий
        # вопрос в этой же сессии (если он будет) уже учтёт новый рейтинг
        # и, возможно, новую сложность.
        updated = self.progress.apply_score(
            topic=self.current_topic,
            score=review.score,
            difficulty=self.current_difficulty,
        )
        self.current_difficulty = self.progress.get_difficulty_for_topic(self.current_topic)

        return review, updated

    def next_question(self):
        self.current_question += 1

        if self.current_question >= len(self.questions.questions):
            return None

        return self.questions.questions[self.current_question]

    def finish_session(self):
        self.session.finished_at = datetime.now()

        if not self.session.results:
            print(f"[DEBUG finish_session] Нет результатов — пропускаем сохранение")
            return self.session

        self.session.average_score = (sum(r.score for r in self.session.results) / len(self.session.results))

        print(f"[DEBUG finish_session] Сохраняю: {len(self.session.results)} результатов, средний {self.session.average_score}")
        print(f"[DEBUG finish_session] history file: {self.history.file_path}")
        print(f"[DEBUG finish_session] history_elo file: {self.history_elo.file_path}")

        self.history.save_session(self.session)
        self.history_elo.save_session(self.session)

        print(f"[DEBUG finish_session] После сохранения history size: {len(self.history.load_history())}")
        print(f"[DEBUG finish_session] После сохранения history_elo size: {len(self.history_elo.load_history())}")

        return self.session
