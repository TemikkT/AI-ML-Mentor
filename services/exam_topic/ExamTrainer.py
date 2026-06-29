from datetime import datetime
import json
import re

from services.common.QuestionGenerator import QuestionGenerator
from services.common.ObsidianLoader import ObsidianLoader
from services.common.HistoryManager import HistoryManager
from services.common.MarkdownCleaner import MarkdownCleaner

from config.config_for_question import cache_path, QUESTIONS_PER_EXAM
from schemas.training_result import TrainingSession, QuestionResult


"""
Класс для экзамена
"""

class ExamTrainer:
    def __init__(self, loader: ObsidianLoader, cleaner: MarkdownCleaner,
                 generator: QuestionGenerator, evaluator, history: HistoryManager):
        self.current_note = None
        self.current_topic = None
        self.current_difficulty = None
        self.questions = []
        self.current_question = 0
        
        self.loader = loader
        self.cleaner = cleaner
        self.generator = generator
        self.evaluator = evaluator
        self.history = history

    def Start_session(self, topic: str):
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
            with open(cache_path, "r", encoding="utf-8") as f:
                image_note = json.load(f)
        except FileNotFoundError:
            # VisionAnalyzer ещё не создавался в этом запуске и не успел
            # инициализировать файл кэша — считаем кэш пустым.
            image_note = {}

        pattern = re.compile(r"\[IMAGE:([^\]]+)\]")
        self.current_note.cleaned_content = pattern.sub(lambda m: image_note.get(m.group(1), \
            {}).get("description", m.group(0)), self.current_note.cleaned_content)

        self.current_difficulty = "Exam"

        self.questions = self.generator.generator_questions(
            topic = self.current_topic,
            note = self.current_note.cleaned_content,
            num_questions=QUESTIONS_PER_EXAM,
        )
        
        self.sessions = TrainingSession(topic=self.current_topic, started_at=datetime.now(), results=[])
    
        return self.questions
    
    def ask_question(self):
        if not self.questions or self.current_question >= len(self.questions.questions):
            return None
        
        return self.questions.questions[self.current_question]

    def submit_answer(self, answer: str):
        current = self.questions.questions[self.current_question]

        review = self.evaluator.evaluate(
            topic = self.current_topic,
            question=current.question,
            answer = answer
        )

        result = QuestionResult(
            topic=self.current_topic,
            question=current.question,
            answer=answer,
            difficulty= self.current_difficulty,

            score=review.score,
            correct_parts=review.correct_parts,
            mistakes=review.mistakes,
            feedback=review.feedback
        )

        self.sessions.results.append(result)

        return review, {}
    
    def next_question(self):
        self.current_question += 1

        if self.current_question >= len(self.questions.questions):
            return None
        
        return self.questions.questions[self.current_question]
    
    def finish_session(self):
        self.sessions.finished_at = datetime.now()

        if not self.sessions.results:
            return self.sessions
        
        self.sessions.average_score = (sum(r.score for r in self.sessions.results) / len(self.sessions.results))

        self.history.save_session(self.sessions)
        
        return self.sessions