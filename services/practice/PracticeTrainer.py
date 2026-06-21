from services.common.QuestionGenerator import QuestionGenerator
from services.practice.PracticeEvaluator import PracticeEvaluator
from services.common.HistoryManager import HistoryManager
from services.practice.PracticeSelector import PracticeSelector
from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner
from services.prompt_template.CodeExecutor import CodeExecutor

from config.config_for_question import cache_path
from config.config_for_question import PRACTICE_QUESTIONS_PER_SESSION, EXECUTABLE_TOPICS
from schemas.Note import Note
from schemas.training_result import TrainingSession, QuestionResult
from datetime import datetime
import json
import re

"""
Аналог TheoryTrainer для тренажёра решения задач (SQL, Pandas, Python).

Отличие от TheoryTrainer — один дополнительный шаг в submit_answer:
если текущая тема входит в EXECUTABLE_TOPICS (см. practice_config.py),
ответ пользователя (код) сначала прогоняется через CodeExecutor,
и результат выполнения передаётся в PracticeEvaluator вместе с кодом.
Если тема не входит в EXECUTABLE_TOPICS (сейчас это SQL) — код не
выполняется, execution_result остаётся None, оценка идёт как текст
(так же, как сейчас работает AnswerEvaluator в теории).

Всё остальное (структура сессии, ask_question/next_question/finish_session)
сделано по тем же принципам, что и в TheoryTrainer, включая фиксы:
- finish_session не сохраняет сессию и не делит на ноль, если results пуст
- ask_question защищён от случая, когда questions is None
- Start_session не падает, если файла кэша изображений ещё нет
"""


class PracticeTrainer:
    def __init__(self, loader: ObsidianLoader, cleaner: MarkdownCleaner,
                 topic_selector: PracticeSelector, generator: QuestionGenerator,
                 evaluator: PracticeEvaluator, history: HistoryManager,
                 code_executor: CodeExecutor):
        self.current_note = None
        self.questions = []
        self.current_question = 0
        self.session = None
        self.current_topic = None

        self.loader = loader
        self.cleaner = cleaner
        self.topic_selector = topic_selector
        self.generator = generator
        self.evaluator = evaluator
        self.history = history
        self.code_executor = code_executor

    def Start_session(self):
        self.questions = []
        self.current_question = 0

        notes = self.loader.load_notes()
        self.current_topic, self.current_note = self.topic_selector.choose_topic(notes)

        self.current_note = self.cleaner.clean(self.current_note)

        try:
            with open(cache_path, "r", encoding="utf-8") as f: # достаём JSON с обработанными изображениями
                image_note = json.load(f)
        except FileNotFoundError:
            # VisionAnalyzer ещё не создавался в этом запуске и не успел
            # инициализировать файл кэша — считаем кэш пустым.
            image_note = {}

        pattern = re.compile(r"\[IMAGE:([^\]]+)\]")
        self.current_note.cleaned_content = pattern.sub(lambda m: image_note.get(m.group(1), \
                        {}).get("description", m.group(0)), self.current_note.cleaned_content)

        self.questions = self.generator.generator_questions(
            topic=self.current_topic,
            note=self.current_note.cleaned_content,
            num_questions=1
        )

        self.session = TrainingSession(topic=self.current_topic, started_at=datetime.now(), results=[])

        return self.questions

    def ask_question(self):
        if not self.questions or self.current_question >= len(self.questions.questions):
            return None

        return self.questions.questions[self.current_question]

    def submit_answer(self, answer: str):
        current = self.questions.questions[self.current_question]

        execution_result = None
        if self.current_topic in EXECUTABLE_TOPICS:
            execution_result = self.code_executor.run(answer)

        print("=" * 70)
        print("DEBUG execution_result:", execution_result)
        print("=" * 70)

        review = self.evaluator.evaluate(
            topic=self.current_topic,
            question=current.question,
            answer=answer,
            execution_result=execution_result,
        )

        result = QuestionResult(
            topic=self.current_topic,
            question=current.question,
            answer=answer,
            difficulty=current.difficulty,

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
    
    def check_code(self, answer: str):

        if self.current_topic not in EXECUTABLE_TOPICS:
            return None
        return self.code_executor.run(answer)