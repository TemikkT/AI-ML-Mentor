import sys
from pathlib import Path

# Позволяет запускать страницу как часть multipage-приложения Streamlit,
# где корень проекта — на уровень выше папки app/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.bootstrap import build_theory_elo_trainer, get_theory_elo_progress, get_llm_client
from app.chat_helper import render_chat_helper
from app.ui.theme import apply_glass_theme, signal_indicator, glass_card_open, glass_card_close, glass_divider

st.set_page_config(page_title="Теория (Elo)")
apply_glass_theme()

st.title("Теория (Elo)")


# ---------------------------------------------------------------------------
# Инициализация трейнера — один раз за сессию браузера
# ---------------------------------------------------------------------------

if "theory_trainer" not in st.session_state:
    st.session_state.theory_trainer = build_theory_elo_trainer()
    st.session_state.theory_session_active = False
    st.session_state.theory_last_review = None
    st.session_state.theory_last_updated = None

trainer = st.session_state.theory_trainer
progress = get_theory_elo_progress()


# ---------------------------------------------------------------------------
# Шаг 1: выбор темы (показывается, если сессия ещё не начата)
# ---------------------------------------------------------------------------

if not st.session_state.theory_session_active:
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

        if st.button("Начать сессию", type="primary"):
            with st.spinner("Генерирую вопрос..."):
                try:
                    trainer.Start_session(topic=chosen_topic)
                    st.session_state.theory_session_active = True
                    st.session_state.theory_last_review = None
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


# ---------------------------------------------------------------------------
# Шаг 2: прохождение текущего вопроса
# ---------------------------------------------------------------------------

if st.session_state.theory_session_active:
    st.subheader(f"Тема: {trainer.current_topic}")
    signal_indicator("Рейтинг темы", progress.get_rating(trainer.current_topic))
    st.caption(f"Сложность: {trainer.current_difficulty}")

    question = trainer.ask_question()

    if question is not None:
        render_chat_helper(
            llm_client=get_llm_client(),
            question_text=question.question,
            chat_key=f"theory_{trainer.current_topic}",
        )

        glass_card_open(f"Вопрос {trainer.current_question + 1}")
        st.write(question.question)
        glass_card_close()

        answer = st.text_area("Твой ответ", key=f"answer_{trainer.current_question}")

        if st.button("Отправить ответ", type="primary"):
            if not answer.strip():
                st.warning("Введи ответ перед отправкой.")
            else:
                with st.spinner("Оцениваю ответ..."):
                    review, updated = trainer.submit_answer(answer)
                    st.session_state.theory_last_review = review
                    st.session_state.theory_last_updated = updated
                st.rerun()

    # Показываем результат последнего ответа, если он есть
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

        signal_indicator("Рейтинг темы теперь", updated["rating"])

        if updated.get("newly_unlocked_topic"):
            st.success(f"🎉 Открыта новая тема: {updated['newly_unlocked_topic']}!")

        col1, col2 = st.columns(2)
        with col1:
            if question is not None and st.button("Следующий вопрос"):
                trainer.next_question()
                st.session_state.theory_last_review = None
                st.rerun()
        with col2:
            if st.button("Завершить сессию"):
                session = trainer.finish_session()
                st.session_state.theory_session_active = False
                st.session_state.theory_last_review = None

                if session.results:
                    st.success(f"Сессия завершена. Средний балл: {session.average_score:.1f}")
                else:
                    st.info("Сессия не сохранена — не было ответов.")
                st.rerun()

    elif question is None:
        # Вопросов в текущей сессии больше нет, и нет результата для показа —
        # сразу предлагаем завершить.
        st.info("Вопросы по этой теме закончились.")
        if st.button("Завершить сессию"):
            session = trainer.finish_session()
            st.session_state.theory_session_active = False

            if session.results:
                st.success(f"Сессия завершена. Средний балл: {session.average_score:.1f}")
            else:
                st.info("Сессия не сохранена — не было ответов.")
            st.rerun()
