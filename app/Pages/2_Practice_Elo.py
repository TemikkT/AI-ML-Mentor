import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from streamlit_ace import st_ace

from app.bootstrap import build_practice_trainer, get_practice_elo_progress, get_llm_client
from app.chat_helper import render_chat_helper
from app.ui.theme import apply_glass_theme, signal_indicator, glass_card_open, glass_card_close, glass_divider
from config.elo_config import PRACTICE_TOPICS

st.set_page_config(page_title="Практика (Elo)", page_icon="💻")
apply_glass_theme()

st.title("💻 Практика (Elo)")


# ---------------------------------------------------------------------------
# Инициализация трейнера и состояния — один раз за сессию браузера
#
# practice_stage — явная state machine для цикла "проверь код -> ошибка ->
# переписать/сдаться", так как в Streamlit нет блокирующего input():
#   "idle"            — сессия не начата, выбор темы
#   "writing"         — пользователь пишет/правит код
#   "code_failed"     — последняя проверка показала ошибку, ждём решения
#                        пользователя (переписать или сдаться)
#   "reviewed"        — ответ отправлен на оценку, результат показан
# ---------------------------------------------------------------------------

if "practice_trainer" not in st.session_state:
    st.session_state.practice_trainer = build_practice_trainer()
    st.session_state.practice_stage = "idle"
    st.session_state.practice_code_draft = ""
    st.session_state.practice_execution_result = None
    st.session_state.practice_review = None
    st.session_state.practice_updated = None

trainer = st.session_state.practice_trainer
progress = get_practice_elo_progress()


# ---------------------------------------------------------------------------
# Состояние "idle": выбор темы
# ---------------------------------------------------------------------------

if st.session_state.practice_stage == "idle":
    st.subheader("Выбери тему")

    topic_labels = [
        f"{topic} (рейтинг: {progress.get_rating(topic)})"
        for topic in PRACTICE_TOPICS
    ]
    chosen_index = st.selectbox(
        "Доступные темы",
        options=range(len(PRACTICE_TOPICS)),
        format_func=lambda i: topic_labels[i],
    )
    chosen_topic = PRACTICE_TOPICS[chosen_index]

    if st.button("Начать сессию", type="primary"):
        with st.spinner("Генерирую задачу..."):
            trainer.Start_session(topic=chosen_topic)
            st.session_state.practice_stage = "writing"
            st.session_state.practice_code_draft = ""
            st.session_state.practice_execution_result = None
            st.session_state.practice_review = None
            st.rerun()


# ---------------------------------------------------------------------------
# Сессия активна — показываем тему, сложность, текущую задачу
# ---------------------------------------------------------------------------

if st.session_state.practice_stage in ("writing", "code_failed", "reviewed"):
    st.subheader(f"Тема: {trainer.current_topic}")
    signal_indicator("Рейтинг темы", progress.get_rating(trainer.current_topic))
    st.caption(f"Сложность: {trainer.current_difficulty}")

    question = trainer.ask_question()

    if question is not None:
        render_chat_helper(
            llm_client=get_llm_client(),
            question_text=question.question,
            chat_key=f"practice_{trainer.current_topic}",
        )

        glass_card_open(f"Задача {trainer.current_question + 1}")
        st.write(question.question)
        glass_card_close()


# ---------------------------------------------------------------------------
# Состояние "writing": ввод/правка кода
# ---------------------------------------------------------------------------

if st.session_state.practice_stage == "writing":
    st.caption("Код решения")
    code = st_ace(
        value=st.session_state.practice_code_draft,
        language="python",
        theme="tomorrow_night",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        wrap=False,
        auto_update=True,
        height=250,
        key=f"code_{trainer.current_question}",
    )

    if st.button("Проверить код", type="primary"):
        st.session_state.practice_code_draft = code

        with st.spinner("Выполняю код..."):
            execution_result = trainer.check_code(code)

        # execution_result is None — тема не предполагает выполнение
        # (например, SQL на этой итерации), либо код сработал.
        if execution_result is None or execution_result.success:
            with st.spinner("Оцениваю решение..."):
                review, updated = trainer.submit_answer(code)
            st.session_state.practice_review = review
            st.session_state.practice_updated = updated
            st.session_state.practice_stage = "reviewed"
        else:
            st.session_state.practice_execution_result = execution_result
            st.session_state.practice_stage = "code_failed"

        st.rerun()


# ---------------------------------------------------------------------------
# Состояние "code_failed": показываем ошибку, ждём решения пользователя
# ---------------------------------------------------------------------------

if st.session_state.practice_stage == "code_failed":
    execution_result = st.session_state.practice_execution_result

    st.code(st.session_state.practice_code_draft, language="python")

    if execution_result.timed_out:
        st.error("Код не успел выполниться за отведённое время (timeout).")
    else:
        st.error("Код выполнился с ошибкой:")
        st.code(execution_result.stderr, language="text")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Переписать код", type="primary"):
            st.session_state.practice_stage = "writing"
            st.rerun()
    with col2:
        if st.button("Отправить как есть на оценку"):
            with st.spinner("Оцениваю решение..."):
                review, updated = trainer.submit_answer(st.session_state.practice_code_draft)
            st.session_state.practice_review = review
            st.session_state.practice_updated = updated
            st.session_state.practice_stage = "reviewed"
            st.rerun()


# ---------------------------------------------------------------------------
# Состояние "reviewed": показ оценки и навигация
# ---------------------------------------------------------------------------

if st.session_state.practice_stage == "reviewed":
    review = st.session_state.practice_review
    updated = st.session_state.practice_updated

    st.code(st.session_state.practice_code_draft, language="python")

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

    # Проверяем, остался ли ещё вопрос в текущей сессии, БЕЗ побочного
    # эффекта (не вызываем next_question() здесь — только читаем индекс).
    has_next_question = (trainer.current_question + 1) < len(trainer.questions.questions)

    col1, col2 = st.columns(2)
    with col1:
        if has_next_question and st.button("Следующая задача"):
            trainer.next_question()  # сдвигаем указатель именно в момент клика, не раньше
            st.session_state.practice_stage = "writing"
            st.session_state.practice_code_draft = ""
            st.session_state.practice_execution_result = None
            st.session_state.practice_review = None
            st.rerun()
    with col2:
        if st.button("Завершить сессию"):
            session = trainer.finish_session()
            st.session_state.practice_stage = "idle"
            st.session_state.practice_review = None

            if session.results:
                st.success(f"Сессия завершена. Средний балл: {session.average_score:.1f}")
            else:
                st.info("Сессия не сохранена — не было ответов.")
            st.rerun()
