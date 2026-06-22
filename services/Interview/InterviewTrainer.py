import json
import re
from datetime import datetime

from services.Interview.TopicSelector import TopicSelector
from services.common.QuestionGenerator import QuestionGenerator
from services.Interview.AnswerEvaluator import AnswerEvaluator
from services.common.HistoryManager import HistoryManager
from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner

from config.config_for_question import cache_path, QUESTIONS_PER_SESSION
from config.interview_config import INTERVIEW_TOPICS_PER_SESSION, INTERVIEW_QUESTIONS_PER_TOPIC
from schemas.training_result import TrainingSession, QuestionResult

"""
InterviewTrainer — режим интервью: вместо одной сессии с одной темой
(как было в исходном TheoryTrainer) запускается INTERVIEW_TOPICS_PER_SESSION
мини-сессий подряд по разным темам (без повторов внутри одного интервью),
по INTERVIEW_QUESTIONS_PER_TOPIC вопросов на каждую.

Темы выбираются СРАЗУ на весь интервью (через
TopicSelector.choose_topics_for_interview), не по одной перед каждой темой —
это гарантирует отсутствие повторов и предсказуемый список тем наперёд.

Каждая тема — полноценная, отдельная TrainingSession (со своим topic,
started_at/finished_at, average_score), которая сохраняется в history.json
сразу по завершении темы (в finish_topic) — так же, как раньше сохранялась
единственная сессия в TheoryTrainer.

Переключение между темами — НЕ автоматическое: вызывающий код сам решает,
когда перейти к следующей теме, вызывая next_topic() после того, как
next_question() внутри текущей темы вернул None.

Структура использования:
    trainer.Start_interview()
    while True:
        question = trainer.ask_question()
        if question is None:
            if trainer.next_topic() is None:
                break  # темы закончились, интервью завершено
            continue
        ... submit_answer(answer) ...
        trainer.next_question()
    trainer.finish_interview()  # на случай, если последняя тема не была явно завершена
"""


class InterviewTrainer:
    def __init__(self, loader: ObsidianLoader, cleaner: MarkdownCleaner,
                 topic_selector: TopicSelector, generator: QuestionGenerator,
                 evaluator: AnswerEvaluator, history: HistoryManager):
        self.loader = loader
        self.cleaner = cleaner
        self.topic_selector = topic_selector
        self.generator = generator
        self.evaluator = evaluator
        self.history = history

        self.topics_queue = []     # список (topic, note), ещё не пройденных в этом интервью
        self.completed_sessions = []  # завершённые TrainingSession этого интервью (для итоговой сводки)

        self.current_topic = None
        self.current_note = None
        self.questions = []
        self.current_question = 0
        self.session = None

    def Start_interview(self):
        """
        Выбирает INTERVIEW_TOPICS_PER_SESSION тем сразу (без повторов)
        и запускает первую из них.
        """
        notes = self.loader.load_notes()

        selected = self.topic_selector.choose_topics_for_interview(
            notes, count=INTERVIEW_TOPICS_PER_SESSION
        )

        self.topics_queue = selected
        self.completed_sessions = []

        return self._start_next_topic_from_queue()

    def _start_next_topic_from_queue(self):
        """
        Берёт следующую тему из topics_queue и запускает по ней мини-сессию.
        Возвращает сгенерированные вопросы, либо None, если тем больше нет.
        """
        if not self.topics_queue:
            self.current_topic = None
            self.current_note = None
            self.questions = []
            self.session = None
            return None

        topic, note = self.topics_queue.pop(0)
        self.current_topic = topic
        self.current_question = 0

        self.current_note = self.cleaner.clean(note)

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

        self.questions = self.generator.generator_questions(
            topic=self.current_topic,
            note=self.current_note.cleaned_content,
            num_questions=INTERVIEW_QUESTIONS_PER_TOPIC,
        )

        self.session = TrainingSession(topic=self.current_topic, started_at=datetime.now(), results=[])

        return self.questions

    def ask_question(self):
        """
        Возвращает текущий вопрос ТЕКУЩЕЙ темы, либо None, если вопросы
        по текущей теме закончились (нужно явно вызвать next_topic()).
        """
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

    def next_topic(self):
        """
        Завершает (сохраняет) текущую тему как отдельную TrainingSession
        и запускает следующую тему из очереди.

        Возвращает сгенерированные вопросы новой темы, либо None,
        если тем в этом интервью больше не осталось — интервью завершено.
        """
        self._finish_current_topic()
        return self._start_next_topic_from_queue()

    def _finish_current_topic(self):
        """
        Сохраняет текущую мини-сессию (тему) как полноценную TrainingSession
        в history.json — так же, как это делал finish_session в TheoryTrainer.
        Не сохраняет сессию, если по теме не было дано ни одного ответа.
        """
        if self.session is None:
            return

        self.session.finished_at = datetime.now()

        if not self.session.results:
            # Пользователь не ответил ни на один вопрос по этой теме —
            # не сохраняем, чтобы не портить статистику и не делить на ноль.
            self.completed_sessions.append(self.session)
            return

        self.session.average_score = (sum(r.score for r in self.session.results) / len(self.session.results))
        self.history.save_session(self.session)
        self.completed_sessions.append(self.session)

    def finish_interview(self):
        """
        Завершает текущую тему (если она ещё не была завершена через
        next_topic()) и возвращает список всех завершённых сессий
        этого интервью — для итоговой сводки пользователю.
        """
        if self.session is not None:
            self._finish_current_topic()
            self.session = None

        return self.completed_sessions


