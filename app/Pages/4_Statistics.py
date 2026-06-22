import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.bootstrap import get_main_history
from services.common.StatisticsManager import ProgressAnalyzer

st.set_page_config(page_title="Статистика", page_icon="📊", layout="wide")
st.title("Статистика")
st.caption("Данные из общей истории (Теория + Интервью). Статистика по практике появится позже.")

history = get_main_history()
analyzer = ProgressAnalyzer(history)

sessions = history.load_history()

if not sessions:
    st.info("История пуста — пройди хотя бы одну сессию, чтобы увидеть статистику.")
    st.stop()


# ---------------------------------------------------------------------------
# Общая сводка — цифры
# ---------------------------------------------------------------------------

summary = analyzer.progress_summary()

col1, col2, col3 = st.columns(3)
col1.metric("Средний балл", f"{summary['average_score']:.1f}")
col2.metric("Сессий пройдено", summary["sessions"])
col3.metric("Вопросов отвечено", summary["questions"])

col4, col5 = st.columns(2)
with col4:
    st.markdown("**🟢 Сильные темы** (средний балл ≥ 9.0)")
    if summary["strong_topics"]:
        for topic in summary["strong_topics"]:
            st.write(f"- {topic}")
    else:
        st.caption("Пока нет тем с настолько высоким баллом.")

with col5:
    st.markdown("**🔴 Слабые темы** (средний балл < 6.5)")
    if summary["weak_topics"]:
        for topic in summary["weak_topics"]:
            st.write(f"- {topic}")
    else:
        st.caption("Слабых тем не найдено — отлично!")


st.divider()


# ---------------------------------------------------------------------------
# Средний балл по темам — горизонтальный bar chart
# ---------------------------------------------------------------------------

st.subheader("Средний балл по темам")

topic_stats = analyzer.topic_statistics()

if topic_stats:
    topics_sorted = sorted(topic_stats.items(), key=lambda kv: kv[1])
    topic_names = [t[0] for t in topics_sorted]
    topic_scores = [t[1] for t in topics_sorted]

    colors = ["#e74c3c" if score < 6.5 else "#f1c40f" if score < 9.0 else "#2ecc71" for score in topic_scores]

    fig = go.Figure(go.Bar(
        x=topic_scores,
        y=topic_names,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.1f}" for s in topic_scores],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis_title="Средний балл",
        yaxis_title=None,
        xaxis_range=[0, 10],
        height=max(300, len(topic_names) * 35),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("Нет данных по темам.")


st.divider()


# ---------------------------------------------------------------------------
# Динамика среднего балла сессий по времени
# ---------------------------------------------------------------------------

st.subheader("Динамика баллов по сессиям")

sessions_sorted = sorted(sessions, key=lambda s: s["finished_at"])
dates = [s["finished_at"][:10] for s in sessions_sorted]  # берём только дату из ISO-таймстампа
scores = [s["average_score"] for s in sessions_sorted]
topics_for_hover = [s["topic"] for s in sessions_sorted]

fig2 = px.line(
    x=range(1, len(scores) + 1),
    y=scores,
    markers=True,
    labels={"x": "Номер сессии", "y": "Средний балл"},
    hover_name=topics_for_hover,
)
fig2.update_traces(hovertemplate="Сессия %{x}<br>Балл: %{y}<br>Тема: %{hovertext}")
fig2.update_layout(yaxis_range=[0, 10], margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)


st.divider()


# ---------------------------------------------------------------------------
# Средний балл по сложности вопроса
# ---------------------------------------------------------------------------

st.subheader("Средний балл по сложности")

by_difficulty = analyzer.average_by_difficulty()

if by_difficulty:
    difficulty_order = ["easy", "medium", "hard", "unknown"]
    sorted_difficulties = sorted(
        by_difficulty.items(),
        key=lambda kv: difficulty_order.index(kv[0]) if kv[0] in difficulty_order else len(difficulty_order)
    )

    fig3 = go.Figure(go.Bar(
        x=[d[0] for d in sorted_difficulties],
        y=[d[1] for d in sorted_difficulties],
        marker_color="#3498db",
        text=[f"{d[1]:.1f}" for d in sorted_difficulties],
        textposition="outside",
    ))
    fig3.update_layout(
        yaxis_title="Средний балл",
        yaxis_range=[0, 10],
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.caption("Нет данных по сложности вопросов.")


st.divider()


# ---------------------------------------------------------------------------
# Темы, давно не повторяемые
# ---------------------------------------------------------------------------

st.subheader("Давно не повторяемые темы (14+ дней)")

forgotten = analyzer.topics_without_practice(days=14)

if forgotten:
    for topic in forgotten:
        days = history.days_since_review(topic)
        st.write(f"- **{topic}** — {days} дней назад")
else:
    st.caption("Все темы повторялись недавно.")