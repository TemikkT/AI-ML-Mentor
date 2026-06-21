
# ===================== THEORY MODE =============================
"""
ТУТ ВЕСЬ КОНФИГ ДЛЯ ВОПРОС ПО ТЕОРИИ
"""
cache_path = "data/image_cache.json"

obsidian_path = r"C:\Users\user\Documents\obsidian"

DOMAIN_MAPPING = {
    "Classic Machine Learning": "Machine Learning",
    "Deep Machine Learning ОСНОВЫ": "Machine Learning",
    "Computer Vision (CV)": "Machine Learning",
    "NLP ML": "Machine Learning",
    "Аналитика данных и Python": "Machine Learning",
}

QUESTIONS_PER_SESSION = 3

PARAGRAPHS_BEFORE_IMAGE = 2

MAX_REVIEW_SCORE = 10

# ===================== PRACTICE MODE =============================
"""
ТУТ ВЕСЬ КОНФИГ ДЛЯ Практики, тренажёра по задачам
"""

PRACTICE_TOPICS = [
    "SQL - Postgres",
    "Pandas - Основы DataFrame",
    "Python база",
]
 
# Темы, для которых код реально выполняется (через CodeExecutor).
# Темы из PRACTICE_TOPICS, не попавшие в этот список (например, SQL, его обработка будет выглядеть иначе), 
# оцениваются как текст, без выполнения — execution_result будет None.
EXECUTABLE_TOPICS = [
    "Pandas - Основы DataFrame",
    "Python база",
]
 
practice_history_path = "data/history_practice.json"
 
CODE_EXECUTION_TIMEOUT = 5  # секунд на выполнение кода пользователя, чтобы нельзя было сувать туда бесконечные цикли и ломать систему
 
PRACTICE_QUESTIONS_PER_SESSION = 1 # количество задач за 1 сессию
