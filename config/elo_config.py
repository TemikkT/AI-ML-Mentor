"""
КОНФИГ ДЛЯ ELO-РЕЖИМА

ELO_TOPICS_ORDER — единый линейный порядок раскрытия тем. Темы разных
доменов идут одним списком (не по доменам отдельно), порядок согласован
с реальной программой обучения (см. обсуждение структуры Obsidian).

Каждая тема — словарь с двумя полями:
  - "topic": название темы (должно точно совпадать с title заметки в Obsidian)
  - "unlock_threshold": сколько рейтинга нужно набрать В ЭТОЙ теме,
    чтобы открылась СЛЕДУЮЩАЯ тема по порядку.

Первая тема в списке открыта всегда (unlocked=True по умолчанию в elo_state.json).
unlock_threshold у последней темы ни на что не влияет (открывать уже нечего),
но оставляем поле для единообразия структуры.

Пороги выставлены ориентировочно и предназначены для ручной донастройки
по мере использования — это НЕ финальные откалиброванные значения.
"""

obsidian_path = r"C:\Users\user\Documents\obsidian"

ELO_TOPICS_ORDER = [
    {"topic": "Python база", "unlock_threshold": 400},
    {"topic": "Статистика", "unlock_threshold": 400},
    {"topic": "Pandas - Основы DataFrame", "unlock_threshold": 400},
    {"topic": "SQL - Postgres", "unlock_threshold": 400},
    {"topic": "Работа с Git и GitHub", "unlock_threshold": 300},

    {"topic": "Метрики регрессии", "unlock_threshold": 300},
    {"topic": "Логистическая регрессия", "unlock_threshold": 400},
    {"topic": "Регуляризация - Линейная регрессия", "unlock_threshold": 400},
    {"topic": "Метрики классификации", "unlock_threshold": 300},
    {"topic": "KNN ближайшие соседи", "unlock_threshold": 400},
    {"topic": "Функции активации и функции потерь", "unlock_threshold": 400},
    {"topic": "SVM Метод опорных векторов", "unlock_threshold": 400},
    {"topic": "Наивный Байес", "unlock_threshold": 400},
    {"topic": "Дерево решений", "unlock_threshold": 400},
    {"topic": "Случайный лес", "unlock_threshold": 400},
    {"topic": "Бустинг и Градиентный бустинг", "unlock_threshold": 400},
    {"topic": "K-means Кластеризация", "unlock_threshold": 400},
    {"topic": "Иерархическая кластеризация", "unlock_threshold": 400},

    {"topic": "Нейронные сети", "unlock_threshold": 400},
    {"topic": "Обучение нейронных сетей back propagation", "unlock_threshold": 400},
    {"topic": "Оптимизаторы под функции потерь", "unlock_threshold": 400},

    {"topic": "Сверточные нейронные сети (CNN)", "unlock_threshold": 400},
    {"topic": "YOLO модель, что умеет и как работать", "unlock_threshold": 400},

    {"topic": "NLP Извлечение признаков", "unlock_threshold": 400},
    {"topic": "NLP Трансформер", "unlock_threshold": 400},
    {"topic": "LangChain", "unlock_threshold": 400},
    {"topic": "AI Agents - LLM", "unlock_threshold": 400},
]

# Очки рейтинга = (score - NEUTRAL_SCORE) * SCORE_MULTIPLIER[difficulty]
NEUTRAL_SCORE = 5

SCORE_MULTIPLIER = {
    "easy": 4,
    "medium": 8,
    "hard": 15,
}

# Границы рейтинга, определяющие сложность следующего генерируемого вопроса.
DIFFICULTY_RATING_BOUNDS = {
    "easy": (0, 150),      # rating in [0, 150)
    "medium": (150, 400),  # rating in [150, 400)
    "hard": (400, None),   # rating >= 400
}

elo_state_path = "data/elo_state.json"
elo_history_path = "data/history_elo.json"

# РАЗБРОС СЛОЖНОСТИ ЭЛО ДЛЯ ПРАКТИКИ
PRACTICE_DIFFICULTY_RATING_BOUNDS = {
    "easy": (0, 700),      # rating in [0, 700)
    "medium": (700, 1700),  # rating in [700, 1700)
    "hard": (1700, None),   # rating >= 1700
}


# ===================== PRACTICE MODE =============================
"""
ТУТ ВЕСЬ КОНФИГ ДЛЯ Практики, тренажёра по задачам
"""

# Темы, для которых код реально выполняется (через CodeExecutor).
# Темы из PRACTICE_TOPICS, не попавшие в этот список (например, SQL, его обработка будет выглядеть иначе), 
# оцениваются как текст, без выполнения — execution_result будет None.
EXECUTABLE_TOPICS = [
    "Pandas - Основы DataFrame",
    "Python база",
]
 
practice_history_path = "data/history_practice.json"
 
CODE_EXECUTION_TIMEOUT = 5  # секунд на выполнение кода пользователя, чтобы нельзя было сувать туда бесконечные цикли и ломать систему
 
PRACTICE_QUESTIONS_PER_SESSION = 5 # количество задач за 1 сессию

PRACTICE_TOPICS = [
    "SQL - Postgres",
    "Pandas - Основы DataFrame",
    "Python база",
]