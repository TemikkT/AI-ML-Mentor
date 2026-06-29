"""
app/ui/theme.py — тема Catppuccin Frappe для AI Ментора.

Подключается одной строкой в начале каждой страницы:

    from app.ui.theme import apply_glass_theme
    apply_glass_theme()
"""

import streamlit as st


# ---------------------------------------------------------------------------
# Палитра Catppuccin Frappe
# ---------------------------------------------------------------------------

# Основные фоны
CRUST = "#232634"
MANTLE = "#292c3c"
BASE = "#303446"

# Поверхности
SURFACE0 = "#414559"
SURFACE1 = "#51576d"
SURFACE2 = "#626880"

# Overlay
OVERLAY0 = "#737994"
OVERLAY1 = "#838ba7"
OVERLAY2 = "#949cbb"

# Текст
SUBTEXT0 = "#a5adce"
SUBTEXT1 = "#b5bfe2"
TEXT = "#c6d0f5"

# Цвета акцентов
LAVENDER = "#babbf1"
BLUE = "#8caaee"
SAPPHIRE = "#85c1dc"
SKY = "#99d1db"
TEAL = "#81c8be"
GREEN = "#a6d189"
YELLOW = "#e5c890"
PEACH = "#ef9f76"
MAROON = "#ea999c"
RED = "#e78284"
MAUVE = "#ca9ee6"
PINK = "#f4b8e4"
FLAMINGO = "#eebebe"
ROSEWATER = "#f2d5cf"

VOID = BASE
VOID_DEEP = CRUST
GLASS_FILL = "rgba(65,69,89,0.45)"
GLASS_FILL_RAISED = "rgba(81,87,109,0.55)"
GLASS_BORDER = "rgba(98,104,128,0.35)"
GLASS_BORDER_HOVER = "rgba(115,121,148,0.55)"
TEXT_PRIMARY = TEXT
TEXT_DIM = OVERLAY1
NEON_BLUE = BLUE
NEON_BLUE_SOFT = LAVENDER
NEON_RED = RED
NEON_RED_SOFT = MAROON


def apply_glass_theme() -> None:

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

        html, body, [data-testid="stAppViewContainer"] {{
            background-color: var(--void);
            background-image:
                radial-gradient(ellipse 70% 45% at 10% -5%, rgba(140,170,238,0.06), transparent 65%),
                radial-gradient(ellipse 55% 40% at 90% 10%, rgba(202,158,230,0.04), transparent 60%);
            color: var(--text-primary);
        }}

        [data-testid="stHeader"] {{
            background-color: transparent;
        }}

        [data-testid="stSidebar"] {{
            background-color: rgba(35,38,52,0.92);
            border-right: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
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
            background-color: rgba(140,170,238,0.1) !important;
            box-shadow: inset 2px 0 0 var(--neon-blue);
            color: var(--neon-blue) !important;
        }}

        .block-container {{
            max-width: 1200px;
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
            text-shadow: 0 0 30px rgba(140,170,238,0.3);
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
            border-left: 2px solid rgba(140,170,238,0.4);
            padding-left: 0.6rem;
        }}

        p, li, label, span, div {{
            font-family: 'JetBrains Mono', monospace;
        }}

        [data-testid="stCaptionContainer"], .stCaption, small {{
            color: var(--text-dim) !important;
        }}

        /* -------------------------------------------------------------
           Кнопки
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
            box-shadow: 0 0 22px rgba(140,170,238,0.2);
        }}

        .stButton button:active {{
            transform: translateY(1px);
        }}

        .stButton button[kind="primary"] {{
            background: linear-gradient(180deg, rgba(140,170,238,0.2), rgba(140,170,238,0.08));
            border: 1px solid rgba(140,170,238,0.5);
            color: #eafbff !important;
            font-weight: 600;
            box-shadow: 0 0 20px rgba(140,170,238,0.25);
        }}

        .stButton button[kind="primary"]:hover {{
            border-color: var(--neon-blue);
            box-shadow: 0 0 32px rgba(140,170,238,0.4);
            color: #ffffff !important;
        }}

        /* -------------------------------------------------------------
           Поля ввода
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
            box-shadow: 0 0 0 1px rgba(140,170,238,0.3), 0 0 22px rgba(140,170,238,0.15) !important;
        }}

        .stSelectbox div[data-baseweb="select"] > div:focus {{
            border-color: var(--neon-blue) !important;
            box-shadow: 0 0 0 1px rgba(140,170,238,0.3) !important;
        }}

        /* -------------------------------------------------------------
           Карточки, контейнеры, code-блоки
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
            background-color: rgba(35,38,52,0.6) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
        }}

        code {{
            font-family: 'JetBrains Mono', monospace !important;
            color: var(--neon-blue) !important;
        }}

        /* -------------------------------------------------------------
           Метрики
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
            text-shadow: 0 0 20px rgba(140,170,238,0.4);
        }}

        [data-testid="stMetricLabel"] {{
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: 0.04em;
            color: var(--text-dim) !important;
            font-size: 0.72rem !important;
            text-transform: uppercase;
        }}

        /* -------------------------------------------------------------
           Прогресс-бар
        ------------------------------------------------------------- */

        .stProgress div[role="progressbar"] > div {{
            background: linear-gradient(90deg, var(--neon-blue-soft), var(--neon-blue)) !important;
            box-shadow: 0 0 14px rgba(140,170,238,0.5);
        }}

        .stProgress div[role="progressbar"] {{
            background-color: var(--glass-fill-raised) !important;
            border-radius: 6px;
        }}

        /* -------------------------------------------------------------
           Алерты
        ------------------------------------------------------------- */

        div[data-testid="stAlertContentError"], .stAlert:has(div[data-testid="stAlertContentError"]) {{
            background-color: rgba(231,130,132,0.08) !important;
            border-left: 3px solid var(--neon-red) !important;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stAlertContentSuccess"], .stAlert:has(div[data-testid="stAlertContentSuccess"]) {{
            background-color: rgba(140,170,238,0.08) !important;
            border-left: 3px solid var(--neon-blue) !important;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stAlertContentWarning"], .stAlert:has(div[data-testid="stAlertContentWarning"]) {{
            background-color: rgba(229,200,144,0.07) !important;
            border-left: 3px solid #e5c890 !important;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stAlertContentInfo"], .stAlert:has(div[data-testid="stAlertContentInfo"]) {{
            background-color: rgba(131,139,167,0.08) !important;
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
           Индикатор сигнала рейтинга
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
            box-shadow: 0 0 10px 3px rgba(140,170,238,0.7);
        }}

        .glass-signal-dot.red {{
            background: var(--neon-red);
            box-shadow: 0 0 8px 2px rgba(231,130,132,0.6);
        }}

        .glass-signal-dot.dim {{
            background: var(--text-dim);
            box-shadow: 0 0 6px 1px rgba(131,139,167,0.4);
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
           Стеклянная карточка
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
            box-shadow: 0 0 28px rgba(140,170,238,0.08);
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
           Разделитель
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
    st.markdown(
        f'<div class="glass-card"><span class="glass-card-label">{label}</span>',
        unsafe_allow_html=True,
    )


def glass_card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def glass_divider() -> None:
    st.markdown('<hr class="glass-divider" />', unsafe_allow_html=True)