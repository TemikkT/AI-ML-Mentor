"""
chat_helper.py — переиспускаемый компонент чат-помощника для Streamlit.

Вызывается с любой страницы сессии (Theory-Elo, Practice-Elo), отображает
чат в боковой панели (st.sidebar). История диалога привязана к ТЕМЕ
сессии (не к конкретному вопросу) — помощник помнит весь разговор на
протяжении сессии, даже когда пользователь переходит от вопроса к вопросу.
При смене темы (новая сессия) история обнуляется, так как меняется chat_key.

Системный промпт пересобирается заново на каждое сообщение с актуальным
текстом ТЕКУЩЕГО вопроса — это значит, даже если помощник помнит весь
диалог по теме, его фокус ограничен последним заданным вопросом, а не
всеми вопросами сессии одновременно.

LLMClient сам не хранит состояние (см. ask_stream в core/LLM_client.py) —
вся история передаётся туда целиком на каждый вызов.

Использование на странице сессии:

    from app.chat_helper import render_chat_helper

    render_chat_helper(
        llm_client=get_llm_client(),
        question_text=question.question,
        chat_key=f"theory_{trainer.current_topic}",
    )
"""
import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.prompts import CHAT_HELPER_SYSTEM_PROMPT_TEMPLATE
from app.ui.theme import glass_divider


def render_chat_helper(llm_client, question_text: str, chat_key: str):
    """
    Рендерит чат-помощник в боковой панели.

    llm_client    — экземпляр LLMClient (для вызова ask_stream)
    question_text — текст ТЕКУЩЕГО вопроса/задачи, передаётся в системный
                    промпт при каждом сообщении (даже если история чата
                    накоплена за несколько вопросов, фокус — на последнем)
    chat_key      — уникальный ключ для текущей темы/сессии (например,
                    f"{mode}_{topic}") — история чата привязана к этому
                    ключу и живёт на протяжении всей сессии по теме,
                    обнуляется только при смене темы
    """
    state_key = f"chat_history_{chat_key}"

    if state_key not in st.session_state:
        st.session_state[state_key] = []

    chat_history = st.session_state[state_key]

    with st.sidebar:
        st.subheader("💬 Помощник")
        st.caption("Спроси, если не понимаешь вопрос — помощник не даст готовый ответ, но поможет разобраться.")
        glass_divider()

        # Отрисовываем уже состоявшийся диалог
        for entry in chat_history:
            with st.chat_message(entry["role"]):
                st.write(entry["content"])

        user_message = st.chat_input("Спросить помощника...")

        if user_message:
            chat_history.append({"role": "user", "content": user_message})

            with st.chat_message("user"):
                st.write(user_message)

            # Системный промпт пересобирается с АКТУАЛЬНЫМ вопросом —
            # даже если история накоплена за несколько вопросов сессии,
            # модель ориентируется на тот вопрос, который пользователь
            # решает прямо сейчас.
            system_prompt = CHAT_HELPER_SYSTEM_PROMPT_TEMPLATE.format(question=question_text)

            with st.chat_message("assistant"):
                response_text = st.write_stream(
                    llm_client.ask_stream(system_prompt, chat_history)
                )

            chat_history.append({"role": "assistant", "content": response_text})

            # Без rerun — st.chat_input уже сам вызывает перерисовку
            # после отправки, дополнительный rerun здесь не нужен и
            # может привести к двойному отображению последней реплики.
