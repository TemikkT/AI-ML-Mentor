from datetime import datetime
import sys
from pathlib import Path

# Позволяет запускать страницу как часть multipage-приложения Streamlit,
# где корень проекта — на уровень выше папки app/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app.bootstrap import build_theory_elo_trainer, get_theory_elo_progress, get_llm_client, build_exam_trainer
from app.chat_helper import render_chat_helper
from app.ui.theme import apply_glass_theme, signal_indicator, glass_card_open, glass_card_close, glass_divider
from services.exam_topic.ExamTrainer import ExamTrainer

st.set_page_config(page_title="Теория (Elo)")
apply_glass_theme()

st.title("Теория (Elo)")



# Инициализация трейнера — один раз за сессию браузера
if "theory_trainer" not in st.session_state:
    st.session_state.theory_trainer = build_theory_elo_trainer()
    st.session_state.Exam_trainer = build_exam_trainer()
    st.session_state.active_trainer = None
    st.session_state.theory_last_review = None
    st.session_state.theory_last_updated = None
    st.session_state.finished_session = None

trainer = st.session_state.theory_trainer
Exam_train = st.session_state.Exam_trainer
progress = get_theory_elo_progress()


# Инициализация сессионного состояния
if "active_trainer" not in st.session_state:
    st.session_state.active_trainer = None


# Шаг 1: выбор темы (пока нет активного тренажёра)
if st.session_state.active_trainer is None:
    available_topics = progress.get_available_topics()
    if not available_topics:
        st.warning("Нет доступных тем. Проверь elo_state.json и ELO_TOPICS_ORDER.")
    else:
        st.subheader("Выбери тему")
        topic_labels = [
            f"{topic} (рейтинг: {progress.get_rating(topic)})"
            for topic in available_topics
        ]
        chosen_index = st.selectbox(
            "Доступные темы",
            options=range(len(available_topics)),
            format_func=lambda i: topic_labels[i],
        )
        chosen_topic = available_topics[chosen_index]

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Начать сессию", type="primary", key="start_theory"):
                with st.spinner("Генерирую вопрос..."):
                    try:
                        trainer.Start_session(topic=chosen_topic)
                        st.session_state.active_trainer = trainer
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        with col2:
            if st.button("Начать экзамен", type="primary", key="start_exam"):
                with st.spinner("Генерирую вопрос..."):
                    try:
                        Exam_train.Start_session(topic=chosen_topic)
                        st.session_state.active_trainer = Exam_train
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

# Шаг 2: прохождение сессии (любого типа)
if st.session_state.active_trainer is not None:
    tr = st.session_state.active_trainer   # <-- единая переменная для любого тренажёра

    st.subheader(f"Тема: {tr.current_topic}")
    signal_indicator("Рейтинг темы", progress.get_rating(tr.current_topic))
    st.caption(f"Сложность: {tr.current_difficulty}")

    if isinstance(tr, ExamTrainer):
        answered = len(tr.sessions.results)
        total = len(tr.questions.questions) if tr.questions else 0
        st.progress(answered / total, text=f"Экзамен: {answered} / {total}")

    question = tr.ask_question()

    if question is not None:
        render_chat_helper(
            llm_client=get_llm_client(),
            question_text=question.question,
            chat_key=f"session_{tr.current_topic}",   # ключ можно сделать уникальным, добавив тип
        )

        glass_card_open(f"Вопрос {tr.current_question + 1}")
        st.write(question.question)
        glass_card_close()

        submitted = st.session_state.theory_last_review is not None
        answer = st.text_area("Твой ответ", key=f"answer_{tr.current_question}", disabled=submitted)

        if st.button("Отправить ответ", type="primary", disabled=submitted):
            if not answer.strip():
                st.warning("Введи ответ перед отправкой.")
            else:
                with st.spinner("Оцениваю ответ..."):
                    review, updated = tr.submit_answer(answer)
                    st.session_state.theory_last_review = review
                    st.session_state.theory_last_updated = updated
                st.rerun()

        # Показываем результат последнего ответа
        if st.session_state.theory_last_review is not None:
            review = st.session_state.theory_last_review
            updated = st.session_state.theory_last_updated

            glass_divider()
            st.metric("Оценка", f"{review.score}/10")
            if review.correct_parts:
                st.markdown("**Что верно:**")
                for item in review.correct_parts:
                    st.markdown(f"- {item}")
            if review.mistakes:
                st.markdown("**Ошибки:**")
                for item in review.mistakes:
                    st.markdown(f"- {item}")
            st.markdown("**Комментарий:**")
            st.write(review.feedback)

            signal_indicator("Рейтинг темы теперь", updated.get("rating", "—"))
            if updated.get("newly_unlocked_topic"):
                st.success(f"🎉 Открыта новая тема: {updated['newly_unlocked_topic']}!")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Следующий вопрос"):
                    tr.next_question()
                    st.session_state.theory_last_review = None
                    st.rerun()
            with col2:
                if st.button("Завершить сессию"):
                    session = tr.finish_session()
                    st.session_state.active_trainer = None
                    st.session_state.theory_last_review = None
                    st.session_state.finished_session = session if session.results else None
                    st.rerun()

    else:
        # Вопросов больше нет
        st.info("Вопросы по этой теме закончились.")
        if st.button("Завершить сессию"):
            session = tr.finish_session()
            st.session_state.active_trainer = None
            st.session_state.finished_session = session if session.results else None
            st.rerun()