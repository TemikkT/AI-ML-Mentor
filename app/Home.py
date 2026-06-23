import streamlit as st

from app.ui.theme import apply_glass_theme, glass_card_open, glass_card_close, glass_divider

st.set_page_config(
    page_title="AI Ментор",
    page_icon="🔷",
    layout="centered",
)

apply_glass_theme()

st.title("AI Ментор")
st.write(
    "Адаптивное обучение Machine Learning и Python с помощью AI. "
    "Выбери режим в меню слева."
)

glass_divider()

col1, col2 = st.columns(2)

with col1:
    glass_card_open("Режим")
    st.subheader("Теория (Elo)")
    st.write(
        "Выбираешь тему сам, рейтинг растёт или падает в зависимости "
        "от качества ответов. Чем выше рейтинг — тем сложнее вопросы."
    )
    glass_card_close()

    glass_card_open("Режим")
    st.subheader("Интервью")
    st.write(
        "Случайный набор тем подряд — имитация настоящего собеседования. "
        "Темы с низкими оценками и давно не повторяемые попадаются чаще."
    )
    glass_card_close()

with col2:
    glass_card_open("Режим")
    st.subheader("Практика (Elo)")
    st.write(
        "Решаешь задачи кодом (Python, Pandas, SQL). Код реально "
        "выполняется, рейтинг темы растёт по тем же принципам, что в теории."
    )
    glass_card_close()

    glass_card_open("Режим")
    st.subheader("Статистика")
    st.write(
        "Общий прогресс, средние баллы по темам, история сессий "
        "в виде графиков."
    )
    glass_card_close()

glass_divider()
st.caption("Выбери страницу в боковом меню, чтобы начать.")
