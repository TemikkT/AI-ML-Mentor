import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.bootstrap import build_interview_trainer
from config.interview_config import INTERVIEW_TOPICS_PER_SESSION

st.set_page_config(page_title="Интервью", page_icon="🎤")
st.title("Интервью")
st.caption(
    f"Случайный набор из {INTERVIEW_TOPICS_PER_SESSION} тем подряд — "
    "темы с низкими оценками и давно не повторяемые попадаются чаще."
)


# ---------------------------------------------------------------------------
# Инициализация состояния
#
# interview_stage:
#   "idle"      — интервью не начато
#   "active"    — идёт прохождение вопросов текущей темы
#   "reviewed"  — последний ответ оценён, результат показан
#   "finished"  — интервью полностью пройдено, показана итоговая сводка
# ---------------------------------------------------------------------------

if "interview_trainer" not in st.session_state:
    st.session_state.interview_trainer = None
    st.session_state.interview_stage = "idle"
    st.session_state.interview_review = None
    st.session_state.interview_topics_done = 0


# ---------------------------------------------------------------------------
# Состояние "idle": кнопка начать интервью
# ---------------------------------------------------------------------------

if st.session_state.interview_stage == "idle":
    st.write("Готов пройти интервью?")

    if st.button("Начать интервью", type="primary"):
        trainer = build_interview_trainer()

        with st.spinner("Выбираю темы и генерирую первый вопрос..."):
            try:
                trainer.Start_interview()
            except ValueError as e:
                st.error(str(e))
                st.stop()

        st.session_state.interview_trainer = trainer
        st.session_state.interview_stage = "active"
        st.session_state.interview_topics_done = 0
        st.session_state.interview_review = None
        st.rerun()


trainer = st.session_state.interview_trainer


# ---------------------------------------------------------------------------
# Состояния "active" / "reviewed": прохождение текущей темы
# ---------------------------------------------------------------------------

if st.session_state.interview_stage in ("active", "reviewed"):
    topics_total = INTERVIEW_TOPICS_PER_SESSION
    topics_done = st.session_state.interview_topics_done

    st.progress(
        topics_done / topics_total,
        text=f"Тема {topics_done + 1} из {topics_total}",
    )
    st.subheader(f"Тема: {trainer.current_topic}")

    question = trainer.ask_question()

    if question is not None:
        st.markdown(f"**Вопрос {trainer.current_question + 1}:**")
        st.write(question.question)


if st.session_state.interview_stage == "active":
    question = trainer.ask_question()

    if question is not None:
        answer = st.text_area("Твой ответ", key=f"interview_answer_{trainer.current_topic}_{trainer.current_question}")

        if st.button("Отправить ответ", type="primary"):
            if not answer.strip():
                st.warning("Введи ответ перед отправкой.")
            else:
                with st.spinner("Оцениваю ответ..."):
                    review = trainer.submit_answer(answer)
                st.session_state.interview_review = review
                st.session_state.interview_stage = "reviewed"
                st.rerun()


# ---------------------------------------------------------------------------
# Состояние "reviewed": показ оценки и переход дальше
# ---------------------------------------------------------------------------

if st.session_state.interview_stage == "reviewed":
    review = st.session_state.interview_review

    st.divider()
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

    has_next_question_in_topic = (trainer.current_question + 1) < len(trainer.questions.questions)

    if has_next_question_in_topic:
        if st.button("Следующий вопрос", type="primary"):
            trainer.next_question()
            st.session_state.interview_stage = "active"
            st.session_state.interview_review = None
            st.rerun()
    else:
        label = "Следующая тема" if (st.session_state.interview_topics_done + 1) < INTERVIEW_TOPICS_PER_SESSION else "Завершить интервью"
        if st.button(label, type="primary"):
            with st.spinner("Перехожу к следующей теме..."):
                next_questions = trainer.next_topic()

            st.session_state.interview_topics_done += 1
            st.session_state.interview_review = None

            if next_questions is None:
                st.session_state.interview_stage = "finished"
            else:
                st.session_state.interview_stage = "active"

            st.rerun()


# ---------------------------------------------------------------------------
# Состояние "finished": итоговая сводка по всем темам интервью
# ---------------------------------------------------------------------------

if st.session_state.interview_stage == "finished":
    st.success("Интервью пройдено!")

    completed = trainer.completed_sessions

    if not completed:
        st.info("Ни одна тема не была сохранена (не было ответов).")
    else:
        for session in completed:
            with st.container(border=True):
                st.markdown(f"**{session.topic}**")
                if session.results:
                    st.write(f"Средний балл: {session.average_score:.1f} ({len(session.results)} вопрос(ов))")
                else:
                    st.write("Без ответов — сессия не сохранена в историю.")

    if st.button("Начать новое интервью"):
        st.session_state.interview_trainer = None
        st.session_state.interview_stage = "idle"
        st.session_state.interview_topics_done = 0
        st.session_state.interview_review = None
        st.rerun()