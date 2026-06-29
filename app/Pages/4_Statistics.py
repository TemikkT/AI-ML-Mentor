import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.bootstrap import get_main_history
from services.common.StatisticsManager import ProgressAnalyzer
from app.ui.theme import (
    apply_glass_theme,
    glass_divider,
    VOID,
    TEXT_PRIMARY,
    TEXT_DIM,
    GLASS_BORDER,
    NEON_BLUE,
    NEON_BLUE_SOFT,
    NEON_RED,
)

st.set_page_config(page_title="Статистика", layout="wide")
apply_glass_theme()
st.title("Статистика")

# ---------------------------------------------------------------------------
# Результат последней завершённой сессии
# ---------------------------------------------------------------------------
session = st.session_state.get("finished_session")
if session is not None:
    st.subheader(f"Последняя сессия: {session.topic}")

    delta = session.finished_at - session.started_at
    mins, secs = divmod(int(delta.total_seconds()), 60)
    avg = session.average_score

    col_time, col_q, col_score = st.columns(3)
    col_time.metric("Время", f"{mins} мин {secs} сек")
    col_q.metric("Ответов", len(session.results))
    col_score.metric("Средний балл", f"{avg:.1f} / 10")

    st.progress(avg / 10, text="Общий результат")

    easy = [r for r in session.results if r.difficulty == "easy"]
    medium = [r for r in session.results if r.difficulty == "medium"]
    hard = [r for r in session.results if r.difficulty == "hard"]

    if easy or medium or hard:
        glass_divider()
        st.markdown("**По уровню сложности**")
        c1, c2, c3 = st.columns(3)
        if easy:
            c1.metric("Easy", f"{sum(r.score for r in easy) / len(easy):.1f}", f"{len(easy)} вопросов")
        if medium:
            c2.metric("Medium", f"{sum(r.score for r in medium) / len(medium):.1f}", f"{len(medium)} вопросов")
        if hard:
            c3.metric("Hard", f"{sum(r.score for r in hard) / len(hard):.1f}", f"{len(hard)} вопросов")

    glass_divider()
    st.markdown("**Разбор ответов**")
    for i, r in enumerate(session.results, 1):
        color = "🟢" if r.score >= 7 else "🟡" if r.score >= 4 else "🔴"
        with st.expander(f"{color} Вопрос {i} — {r.score}/10 [{r.difficulty}]"):
            st.markdown(f"**Вопрос:** {r.question}")
            st.markdown(f"**Твой ответ:** {r.answer}")
            if r.correct_parts:
                st.markdown("**✅ Верно:**")
                for part in r.correct_parts:
                    st.markdown(f"- {part}")
            if r.mistakes:
                st.markdown("**❌ Ошибки:**")
                for m in r.mistakes:
                    st.markdown(f"- {m}")
            st.markdown(f"**💬 Рекомендация:** {r.feedback}")

    glass_divider()
    if st.button("Очистить", key="clear_last_session"):
        st.session_state.finished_session = None
        st.rerun()

    glass_divider()

st.caption("Данные из общей истории (Теория + Интервью). Статистика по практике появится позже.")

history = get_main_history()
analyzer = ProgressAnalyzer(history)

sessions = history.load_history()

if not sessions:
    st.info("История пуста — пройди хотя бы одну сессию, чтобы увидеть статистику.")
    st.stop()


# ---------------------------------------------------------------------------
# Общий "паспорт" оформления графиков Plotly — чтобы они растворялись
# в стеклянной неоновой палитре, а не торчали белым фоном.
# ---------------------------------------------------------------------------

PLOTLY_FONT = dict(family="JetBrains Mono, monospace", color=TEXT_PRIMARY, size=12)
GRID_COLOR = "rgba(140,210,255,0.12)"


def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=PLOTLY_FONT,
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GLASS_BORDER),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GLASS_BORDER),
    )
    return fig


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
    st.markdown("**Сильные темы** (средний балл ≥ 9.0)")
    if summary["strong_topics"]:
        for topic in summary["strong_topics"]:
            st.write(f"- {topic}")
    else:
        st.caption("Пока нет тем с настолько высоким баллом.")

with col5:
    st.markdown("**Слабые темы** (средний балл < 6.5)")
    if summary["weak_topics"]:
        for topic in summary["weak_topics"]:
            st.write(f"- {topic}")
    else:
        st.caption("Слабых тем не найдено — отлично!")


glass_divider()


# ---------------------------------------------------------------------------
# Средний балл по темам — горизонтальный bar chart
# ---------------------------------------------------------------------------

st.subheader("Средний балл по темам")

topic_stats = analyzer.topic_statistics()

if topic_stats:
    topics_sorted = sorted(topic_stats.items(), key=lambda kv: kv[1])
    topic_names = [t[0] for t in topics_sorted]
    topic_scores = [t[1] for t in topics_sorted]

    colors = [NEON_RED if score < 6.5 else NEON_BLUE_SOFT if score < 9.0 else NEON_BLUE for score in topic_scores]

    fig = go.Figure(go.Bar(
        x=topic_scores,
        y=topic_names,
        orientation="h",
        marker_color=colors,
        marker_line_color=GLASS_BORDER,
        marker_line_width=1,
        text=[f"{s:.1f}" for s in topic_scores],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY),
    ))
    style_fig(fig)
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


glass_divider()


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
fig2.update_traces(
    hovertemplate="Сессия %{x}<br>Балл: %{y}<br>Тема: %{hovertext}",
    line_color=NEON_BLUE,
    marker=dict(color=NEON_BLUE, size=7, line=dict(color=GLASS_BORDER, width=1)),
)
style_fig(fig2)
fig2.update_layout(yaxis_range=[0, 10], margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)


glass_divider()


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
        marker_color=NEON_BLUE,
        marker_line_color=GLASS_BORDER,
        marker_line_width=1,
        text=[f"{d[1]:.1f}" for d in sorted_difficulties],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY),
    ))
    style_fig(fig3)
    fig3.update_layout(
        yaxis_title="Средний балл",
        yaxis_range=[0, 10],
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.caption("Нет данных по сложности вопросов.")


glass_divider()


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
