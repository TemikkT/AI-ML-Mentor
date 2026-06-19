from core.LLM_client import LLMClient
from services.QuestionGenerator import QuestionGenerator
from services.AnswerEvaluator import AnswerEvaluator
from services.HistoryManager import HistoryManager
from services.TopicSelector import TopicSelector
from services.ObsidianLoader import ObsidianLoader
from services.MarkdownCleaner import MarkdownCleaner
from services.VisionAnalyzer import VisionAnalyzer

from config.theory_config import obsidian_path, cache_path, QUESTIONS_PER_SESSION
from schemas.Note import Note
from schemas.training_result import TrainingSession, QuestionResult
from datetime import datetime
import json
import re

"""
Класс для вызова вопросам по теории. Тк мы будем делать 
- тренажёр по теории
- тренажёр по задачам
Будет логично разделить их на разные классы, 
чтобы их можно было просто вызывать со своими параметрами 
и они жили отдеально друг от друга
"""

class TheoryTrainer:
    def __init__(self, loader, cleaner, topic_selector, generator, evaluator, history):
        self.current_note = None
        self.questions = []
        self.current_question = 0
        self.session = None

        self.loader = loader
        self.cleaner = cleaner
        self.topic_selector = topic_selector
        self.generator = generator
        self.evaluator = evaluator
        self.history = history

    def Start_session(self):
        self.questions = []
        self.current_question = 0

        notes = self.loader.load_notes()
        print("все записи____________", [n.title for n in notes])
        self.current_topic, self.current_note = self.topic_selector.choose_topic(notes)

        self.current_note = self.cleaner.clean(self.current_note)

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                image_note = json.load(f)
        except FileNotFoundError:
            image_note = {}

        pattern = re.compile(r"\[IMAGE:([^\]]+)\]")
        self.current_note.cleaned_content = pattern.sub(lambda m: image_note.get(m.group(1), \
                        {}).get("description", m.group(0)),self.current_note.cleaned_content)

        self.questions = self.generator.generator_questions(topic = self.current_topic, note = self.current_note.cleaned_content, 
                                                       num_questions=QUESTIONS_PER_SESSION)
        print(self.questions)
        print(type(self.questions))
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

            difficulty = current.difficulty,
            score=review.score,
            correct_parts=review.correct_parts,
            mistakes=review.mistakes,
            feedback=review.feedback
        )

        self.session.results.append(result)

        return review

    def next_question(self):
        self.current_question += 1

        if self.current_question >= len(self.questions.questions):
            return None

        return self.questions.questions[self.current_question]

    def finish_session(self):
        self.session.finished_at = datetime.now()

        if not self.session.results:
            # Пользователь не ответил ни на один вопрос —
            # такую сессию не сохраняем, чтобы не портить статистику
            # и не делить на ноль.
            return self.session

        self.session.average_score = (sum(r.score for r in self.session.results) / len(self.session.results))
        self.history.save_session(self.session)
        return self.session


