"""
app/ui/theme.py — тема "Стеклянная неоновая пустота" для AI Ментора.

Подключается одной строкой в начале каждой страницы:

    from app.ui.theme import apply_glass_theme
    apply_glass_theme()

Идея оформления: интерфейс висит в тёмной пустоте, как HUD нейросети.
Все панели — полупрозрачное стекло (backdrop-filter blur) с тонкой
светящейся голубой обводкой. Рейтинг темы показывается не текстом,
а "индикатором сигнала" — светящейся точкой с пульсацией: чем выше
рейтинг, тем ярче и холоднее свет; чем ниже — тем тревожнее (розово-
красный). Никакой бумаги, никаких насечек — чистый свет на чёрном.

Кроме apply_glass_theme() модуль даёт HTML-хелперы (signal_indicator,
glass_card_open/close, glass_divider), которые оборачивают
st.markdown(..., unsafe_allow_html=True) готовыми классами.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# Палитра и токены
# ---------------------------------------------------------------------------

VOID = "#05070c"            # фон — пустота с едва заметным синим подтоном
VOID_DEEP = "#020306"        # самые глубокие тени / виньетка
GLASS_FILL = "rgba(255,255,255,0.035)"   # заливка стеклянных панелей
GLASS_FILL_RAISED = "rgba(255,255,255,0.06)"  # приподнятые поверхности (инпуты)
GLASS_BORDER = "rgba(140,210,255,0.16)"  # обводка стекла в покое
GLASS_BORDER_HOVER = "rgba(140,210,255,0.4)"
TEXT_PRIMARY = "#e8f4ff"     # основной текст — холодный почти-белый
TEXT_DIM = "#7e93ab"         # притушенный текст / подписи
NEON_BLUE = "#5fd4ff"        # главный неон — успех, активность, фокус
NEON_BLUE_SOFT = "#3a9fc7"   # тот же тон, но тише (для теней/градиентов)
NEON_RED = "#ff5f7a"         # тревога — низкий рейтинг, ошибки
NEON_RED_SOFT = "#b5455a"


def apply_glass_theme() -> None:
    """Внедряет CSS темы 'стеклянная неоновая пустота' в текущую страницу."""

    st.markdown(
        f"""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {{
            --void: {VOID};
            --void-deep: {VOID_DEEP};
            --glass-fill: {GLASS_FILL};
            --glass-fill-raised: {GLASS_FILL_RAISED};
            --glass-border: {GLASS_BORDER};
            --glass-border-hover: {GLASS_BORDER_HOVER};
            --text-primary: {TEXT_PRIMARY};
            --text-dim: {TEXT_DIM};
            --neon-blue: {NEON_BLUE};
            --neon-blue-soft: {NEON_BLUE_SOFT};
            --neon-red: {NEON_RED};
            --neon-red-soft: {NEON_RED_SOFT};
        }}

        /* -------------------------------------------------------------
           Базовый фон — пустота с мягким туманом неона по краям,
           без шума и зерна (это не бумага, это вакуум).
        ------------------------------------------------------------- */

        html, body, [data-testid="stAppViewContainer"] {{
            background-color: var(--void);
            background-image:
                radial-gradient(ellipse 60% 40% at 15% 0%, rgba(95,212,255,0.10), transparent 60%),
                radial-gradient(ellipse 50% 35% at 100% 15%, rgba(95,212,255,0.06), transparent 65%),
                radial-gradient(ellipse 70% 50% at 50% 100%, rgba(2,3,6,0.9), transparent 70%);
            color: var(--text-primary);
        }}

        [data-testid="stHeader"] {{
            background-color: transparent;
        }}

        [data-testid="stSidebar"] {{
            background-color: rgba(5,8,14,0.85);
            border-right: 1px solid var(--glass-border);
            backdrop-filter: blur(18px);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text-dim) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            font-family: 'JetBrains Mono', monospace;
        }}

        section[data-testid="stSidebarNav"] a {{
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: 0.02em;
            border-radius: 6px;
        }}

        section[data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: rgba(95,212,255,0.08) !important;
            box-shadow: inset 2px 0 0 var(--neon-blue);
            color: var(--neon-blue) !important;
        }}

        .block-container {{
            max-width: 880px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }}

        /* -------------------------------------------------------------
           Типографика
        ------------------------------------------------------------- */

        h1 {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.01em;
            text-shadow: 0 0 22px rgba(95,212,255,0.35);
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: 0.6rem;
            margin-bottom: 1.2rem !important;
            position: relative;
        }}

        h1::before {{
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            margin-right: 0.55rem;
            border-radius: 50%;
            background: var(--neon-blue);
            box-shadow: 0 0 10px 2px var(--neon-blue);
            vertical-align: middle;
        }}

        h2, h3 {{
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }}

        h3 {{
            font-size: 1.05rem !important;
            color: var(--neon-blue) !important;
            border-left: 2px solid rgba(95,212,255,0.4);
            padding-left: 0.6rem;
        }}

        p, li, label, span, div {{
            font-family: 'JetBrains Mono', monospace;
        }}

        [data-testid="stCaptionContainer"], .stCaption, small {{
            color: var(--text-dim) !important;
        }}

        /* -------------------------------------------------------------
           Кнопки — стеклянные грани, светятся на hover/focus
        ------------------------------------------------------------- */

        .stButton button, .stDownloadButton button {{
            background-color: var(--glass-fill);
            color: var(--text-primary) !important;
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.03em;
            font-size: 0.85rem;
            padding: 0.55rem 1.15rem;
            backdrop-filter: blur(10px);
            transition: border-color 0.18s ease, box-shadow 0.18s ease, color 0.18s ease, transform 0.05s ease;
        }}

        .stButton button:hover, .stDownloadButton button:hover {{
            border-color: var(--glass-border-hover);
            color: var(--neon-blue) !important;
            box-shadow: 0 0 18px rgba(95,212,255,0.18);
        }}

        .stButton button:active {{
            transform: translateY(1px);
        }}

        .stButton button[kind="primary"] {{
            background: linear-gradient(180deg, rgba(95,212,255,0.18), rgba(95,212,255,0.08));
            border: 1px solid rgba(95,212,255,0.55);
            color: #eafbff !important;
            font-weight: 600;
            box-shadow: 0 0 16px rgba(95,212,255,0.22);
        }}

        .stButton button[kind="primary"]:hover {{
            border-color: var(--neon-blue);
            box-shadow: 0 0 26px rgba(95,212,255,0.4);
            color: #ffffff !important;
        }}

        /* -------------------------------------------------------------
           Поля ввода — тёмное стекло чуть приподнятое над фоном
        ------------------------------------------------------------- */

        .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
            background-color: var(--glass-fill-raised) !important;
            border: 1px solid var(--glass-border) !important;
            color: var(--text-primary) !important;
            font-family: 'JetBrains Mono', monospace !important;
            border-radius: 8px !important;
            backdrop-filter: blur(10px);
        }}

        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: var(--neon-blue) !important;
            box-shadow: 0 0 0 1px rgba(95,212,255,0.3), 0 0 18px rgba(95,212,255,0.15) !important;
        }}

        /* -------------------------------------------------------------
           Карточки/контейнеры и code-блоки — стекло с лёгким blur
        ------------------------------------------------------------- */

        [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{
            background-color: var(--glass-fill);
            backdrop-filter: blur(14px);
        }}

        div[data-testid="stContainer"] {{
            border-color: var(--glass-border) !important;
            border-radius: 10px !important;
        }}

        .stCodeBlock, pre {{
            background-color: rgba(255,255,255,0.025) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            backdrop-filter: blur(10px);
        }}

        code {{
            font-family: 'JetBrains Mono', monospace !important;
            color: var(--neon-blue) !important;
        }}

        /* -------------------------------------------------------------
           Метрики (st.metric) — светящееся число в стекле
        ------------------------------------------------------------- */

        [data-testid="stMetric"] {{
            background-color: var(--glass-fill);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 0.8rem 1.1rem;
            backdrop-filter: blur(12px);
        }}

        [data-testid="stMetricValue"] {{
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--neon-blue) !important;
            font-weight: 600 !important;
            text-shadow: 0 0 16px rgba(95,212,255,0.4);
        }}

        [data-testid="stMetricLabel"] {{
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: 0.04em;
            color: var(--text-dim) !important;
            font-size: 0.72rem !important;
            text-transform: uppercase;
        }}

        /* -------------------------------------------------------------
           Прогресс-бар — луч света
        ------------------------------------------------------------- */

        .stProgress div[role="progressbar"] > div {{
            background: linear-gradient(90deg, var(--neon-blue-soft), var(--neon-blue)) !important;
            box-shadow: 0 0 10px rgba(95,212,255,0.5);
        }}

        .stProgress div[role="progressbar"] {{
            background-color: var(--glass-fill-raised) !important;
            border-radius: 6px;
        }}

        /* -------------------------------------------------------------
           Алерты — error/warning/success/info в неоновой палитре
        ------------------------------------------------------------- */

        div[data-testid="stAlertContentError"], .stAlert:has(div[data-testid="stAlertContentError"]) {{
            background-color: rgba(255,95,122,0.08) !important;
            border-left: 3px solid var(--neon-red) !important;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stAlertContentSuccess"], .stAlert:has(div[data-testid="stAlertContentSuccess"]) {{
            background-color: rgba(95,212,255,0.08) !important;
            border-left: 3px solid var(--neon-blue) !important;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stAlertContentWarning"], .stAlert:has(div[data-testid="stAlertContentWarning"]) {{
            background-color: rgba(255,200,95,0.06) !important;
            border-left: 3px solid #ffc85f !important;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stAlertContentInfo"], .stAlert:has(div[data-testid="stAlertContentInfo"]) {{
            background-color: rgba(126,147,171,0.08) !important;
            border-left: 3px solid var(--text-dim) !important;
            backdrop-filter: blur(10px);
        }}

        [data-testid="stAlertContainer"] p {{
            color: var(--text-primary) !important;
        }}

        hr {{
            border-color: var(--glass-border) !important;
        }}

        /* -------------------------------------------------------------
           Сигнатурный элемент: индикатор сигнала рейтинга.
           Подключается через signal_indicator() ниже.
        ------------------------------------------------------------- */

        .glass-signal-wrap {{
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            margin: 0.35rem 0 0.7rem 0;
            padding: 0.4rem 0.9rem;
            background-color: var(--glass-fill);
            border: 1px solid var(--glass-border);
            border-radius: 999px;
            backdrop-filter: blur(10px);
        }}

        .glass-signal-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex-shrink: 0;
            animation: glass-pulse 2.2s ease-in-out infinite;
        }}

        .glass-signal-dot.blue {{
            background: var(--neon-blue);
            box-shadow: 0 0 8px 2px rgba(95,212,255,0.7);
        }}

        .glass-signal-dot.red {{
            background: var(--neon-red);
            box-shadow: 0 0 8px 2px rgba(255,95,122,0.7);
        }}

        .glass-signal-dot.dim {{
            background: var(--text-dim);
            box-shadow: 0 0 6px 1px rgba(126,147,171,0.5);
            animation: none;
        }}

        @keyframes glass-pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.55; transform: scale(0.82); }}
        }}

        .glass-signal-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--text-dim);
        }}

        .glass-signal-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--text-primary);
        }}

        /* -------------------------------------------------------------
           Стеклянная карточка вопроса/задачи.
           Подключается через glass_card_open()/glass_card_close().
        ------------------------------------------------------------- */

        .glass-card {{
            position: relative;
            background-color: var(--glass-fill);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.15rem 1.35rem 1.05rem 1.35rem;
            margin: 0.8rem 0 1.2rem 0;
            backdrop-filter: blur(14px);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}

        .glass-card:hover {{
            border-color: var(--glass-border-hover);
            box-shadow: 0 0 24px rgba(95,212,255,0.08);
        }}

        .glass-card-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--neon-blue-soft);
            margin-bottom: 0.45rem;
            display: block;
        }}

        /* -------------------------------------------------------------
           Кастомный разделитель — тонкий луч с затуханием по краям
        ------------------------------------------------------------- */

        .glass-divider {{
            border: none;
            height: 1px;
            margin: 1.7rem 0;
            background: linear-gradient(
                90deg,
                transparent,
                var(--glass-border-hover) 20%,
                var(--glass-border-hover) 80%,
                transparent
            );
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# HTML-хелперы
# ---------------------------------------------------------------------------

def signal_indicator(label: str, value, tone: str = "auto", threshold_low: int = 1100, threshold_high: int = 1400) -> None:
    """
    Рисует рейтинг как светящийся индикатор сигнала (точка + значение).

    tone: "blue" | "red" | "dim" | "auto"
      "auto" выбирает цвет по числовому значению value относительно
      threshold_low / threshold_high (полезно для Elo-рейтингов).
    """
    if tone == "auto":
        try:
            numeric = float(value)
            if numeric >= threshold_high:
                tone = "blue"
            elif numeric < threshold_low:
                tone = "red"
            else:
                tone = "dim"
        except (TypeError, ValueError):
            tone = "dim"

    st.markdown(
        f"""
        <div class="glass-signal-wrap">
            <span class="glass-signal-dot {tone}"></span>
            <span class="glass-signal-label">{label}</span>
            <span class="glass-signal-value">{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def glass_card_open(label: str) -> None:
    """Открывает стеклянную карточку. Обязательно закрыть glass_card_close()."""
    st.markdown(
        f'<div class="glass-card"><span class="glass-card-label">{label}</span>',
        unsafe_allow_html=True,
    )


def glass_card_close() -> None:
    """Закрывает стеклянную карточку, открытую glass_card_open()."""
    st.markdown("</div>", unsafe_allow_html=True)


def glass_divider() -> None:
    """Декоративный разделитель — светящийся луч (замена st.divider())."""
    st.markdown('<hr class="glass-divider" />', unsafe_allow_html=True)
