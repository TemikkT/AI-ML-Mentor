"""
bootstrap.py — фабрики сервисов для Streamlit-приложения.
 
Здесь создаются и кэшируются (через st.cache_resource) все "тяжёлые"
объекты — LLM-клиент, загрузчик Obsidian, менеджеры истории и прогресса.
st.cache_resource гарантирует, что эти объекты создаются ОДИН РАЗ за
всё время жизни приложения (не пересоздаются при каждом перерисовывании
страницы), что важно: LLMClient не нужно плодить, а HistoryManager должен
быть одним и тем же экземпляром, чтобы все страницы видели одну и ту же
историю.
 
ВАЖНО: st.cache_resource кэширует объекты НА УРОВНЕ ВСЕГО ПРИЛОЖЕНИЯ,
общие для всех, кто откроет это приложение в браузере. Для личного
инструмента (один пользователь) это не проблема. Если в будущем
понадобится несколько независимых пользователей — этот момент придётся
пересмотреть (например, привязать историю к st.session_state с разными
файлами на пользователя).
 
Трейнеры (EloTrainer, PracticeTrainer, InterviewTrainer) — НЕ кэшируются
здесь: они хранят состояние текущей сессии (current_topic, questions,
session) и должны жить в st.session_state на стороне конкретной страницы,
создаваясь один раз при старте сессии пользователя, а не заново при
каждом перерисовывании.
"""

import sys
from pathlib import Path

import streamlit as st
 
from core.LLM_client import LLMClient
 
from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner
from services.common.QuestionGenerator import QuestionGenerator
from services.common.HistoryManager import HistoryManager
from services.prompt_template.CodeExecutor import CodeExecutor
 
from services.Interview.AnswerEvaluator import AnswerEvaluator
from services.Interview.TopicSelector import TopicSelector
from services.Interview.InterviewTrainer import InterviewTrainer
 
from services.elo.EloProgressManager import EloProgressManager
from services.elo.EloTrainer import EloTrainer
 
from services.practice.PracticeEvaluator import PracticeEvaluator
from services.practice.PracticeEloManager import PracticeEloProgressManager
from services.practice.PracticeTrainer import PracticeTrainer
 
from config.elo_config import obsidian_path, CODE_EXECUTION_TIMEOUT
from config.elo_config import elo_state_path, elo_history_path, PRACTICE_TOPICS
from config.prompts import ELO_QUESTION_PROMPT, PRACTICE_QUESTION_PROMPT, QUESTION_PROMPT


PRACTICE_HISTORY_PATH = "data/history_practice.json"
PRACTICE_ELO_STATE_PATH = "data/practice_elo_state.json"
MAIN_HISTORY_PATH = "data/history.json"
 
 
# ---------------------------------------------------------------------------
# Базовые, общие для всех режимов сервисы
# ---------------------------------------------------------------------------
 
@st.cache_resource
def get_llm_client() -> LLMClient:
    return LLMClient(model_name="deepseek/deepseek-v4-flash")
 
 
@st.cache_resource
def get_loader() -> ObsidianLoader:
    return ObsidianLoader(obsidian_path)
 
 
@st.cache_resource
def get_cleaner() -> MarkdownCleaner:
    return MarkdownCleaner(get_loader())
 
 
@st.cache_resource
def get_main_history() -> HistoryManager:
    """Общая история — используется и Theory-Elo, и Interview."""
    return HistoryManager(file_path=MAIN_HISTORY_PATH)
 
 
# ---------------------------------------------------------------------------
# Theory-Elo
# ---------------------------------------------------------------------------
 
@st.cache_resource
def get_theory_elo_history() -> HistoryManager:
    """Отдельный журнал только Elo-сессий теории — для подсветки слабых мест."""
    return HistoryManager(file_path=elo_history_path)
 
 
@st.cache_resource
def get_theory_elo_progress() -> EloProgressManager:
    return EloProgressManager(file_path=elo_state_path)
 
 
def build_theory_elo_trainer() -> EloTrainer:
    """
    Создаёт НОВЫЙ экземпляр EloTrainer (теория). Вызывать один раз при
    старте сессии пользователя и сохранять результат в st.session_state —
    повторные вызовы создадут новый трейнер с потерей текущего состояния.
    """
    llm = get_llm_client()
    history = get_main_history()
    history_elo = get_theory_elo_history()
    progress = get_theory_elo_progress()
 
    generator = QuestionGenerator(llm, prompt_template=ELO_QUESTION_PROMPT, history_manager=history_elo)
    evaluator = AnswerEvaluator(llm)
 
    return EloTrainer(
        loader=get_loader(),
        cleaner=get_cleaner(),
        generator=generator,
        evaluator=evaluator,
        progress_manager=progress,
        history=history,
        history_elo=history_elo,
    )
 
 
# ---------------------------------------------------------------------------
# Practice-Elo
# ---------------------------------------------------------------------------
 
@st.cache_resource
def get_practice_history() -> HistoryManager:
    return HistoryManager(file_path=PRACTICE_HISTORY_PATH)
 
 
@st.cache_resource
def get_practice_elo_progress() -> PracticeEloProgressManager:
    return PracticeEloProgressManager(topics=PRACTICE_TOPICS, file_path=PRACTICE_ELO_STATE_PATH)
 
 
def build_practice_trainer() -> PracticeTrainer:
    """
    Создаёт НОВЫЙ экземпляр PracticeTrainer. Вызывать один раз при старте
    сессии пользователя и сохранять в st.session_state.
    """
    llm = get_llm_client()
 
    generator = QuestionGenerator(llm, prompt_template=PRACTICE_QUESTION_PROMPT)
    evaluator = PracticeEvaluator(llm)
    code_executor = CodeExecutor(timeout=CODE_EXECUTION_TIMEOUT)
 
    return PracticeTrainer(
        loader=get_loader(),
        cleaner=get_cleaner(),
        progress_manager=get_practice_elo_progress(),
        generator=generator,
        evaluator=evaluator,
        history=get_practice_history(),
        code_executor=code_executor,
    )
 
 
# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------
 
@st.cache_resource
def get_interview_topic_selector() -> TopicSelector:
    return TopicSelector(get_main_history())
 
 
def build_interview_trainer() -> InterviewTrainer:
    """
    Создаёт НОВЫЙ экземпляр InterviewTrainer. Вызывать один раз при старте
    интервью и сохранять в st.session_state.
    """
    llm = get_llm_client()
 
    generator = QuestionGenerator(llm, prompt_template=QUESTION_PROMPT)
    evaluator = AnswerEvaluator(llm)
 
    return InterviewTrainer(
        loader=get_loader(),
        cleaner=get_cleaner(),
        topic_selector=get_interview_topic_selector(),
        generator=generator,
        evaluator=evaluator,
        history=get_main_history(),
    )
