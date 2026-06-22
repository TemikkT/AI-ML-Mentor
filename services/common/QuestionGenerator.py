import json
from schemas.questions import QuestionSet
from config.prompts import QUESTION_PROMPT

"""
Создаём класс вопроса и ответа модели. В инициализации подаётся наша модель LLM, которую мы создали в LLMClient
Далее функция генерации вопроса и получение ответа.

history_manager — опциональная зависимость (по умолчанию None), которая
не нужна для Theory/Practice (там вызывается как раньше, без истории).
Используется только когда переданному prompt_template требуются
плейсхолдеры difficulty/weak_points (сейчас — это ELO_QUESTION_PROMPT) —
в этом случае generator_questions сам тянет последние 1-2 сессии по теме,
выделяет значимые ошибки (score < 7) и передаёт их текстом в промпт.
"""

WEAK_POINTS_SCORE_THRESHOLD = 7   # результаты со score >= этого порога не считаются слабым местом
WEAK_POINTS_SESSIONS_LOOKBACK = 2  # сколько последних сессий по теме просматривать


class QuestionGenerator:
    def __init__(self, llm_client, prompt_template=QUESTION_PROMPT, history_manager=None):
        self.llm = llm_client # Получение LLM клиента, название модели, температура. В общем нужный нам класс
        self.prompt_template = prompt_template # По умолчанию — промпт теории. Для тренажёра/Elo передаётся свой prompt_template
        self.history = history_manager # Нужен только если prompt_template ожидает weak_points (ELO_QUESTION_PROMPT)

    def generator_questions(self, topic: str, note: str, num_questions: int = 5, difficulty: str = None):
        # задаём параметры вопроса. Топик, Какая запись, количество вопросов, сложность (нужна только для Elo)

        format_kwargs = {
            "topic": topic, # Топик, какая тема
            "note": note, # Какая запись нас интересует именно из этой темы
            "num_questions": num_questions, # количество вопросов которые задаст модель
        }

        # Передаём difficulty/weak_points в format() только если этого
        # реально требует переданный prompt_template — иначе PromptTemplate.format()
        # может упасть на лишнем или недостающем аргументе. У PromptTemplate
        # есть атрибут input_variables — список имён плейсхолдеров в тексте.
        required_vars = getattr(self.prompt_template, "input_variables", [])

        if "difficulty" in required_vars:
            format_kwargs["difficulty"] = difficulty

        if "weak_points" in required_vars:
            format_kwargs["weak_points"] = self._build_weak_points_block(topic)

        prompt = self.prompt_template.format(**format_kwargs) # Берём формат ответа который мы сохранили в PromptTemplate

        structured_llm = self.llm.get_structured_llm(QuestionSet) # Используем функцию построения ответа модели по нашей схеме, чтобы вызов был в виде JSON
        result = structured_llm.invoke(prompt) # Выводим то что нам сказала модель
    
        return result

    def _build_weak_points_block(self, topic: str) -> str:
        """
        Достаёт последние WEAK_POINTS_SESSIONS_LOOKBACK сессий по теме,
        отбирает результаты со score < WEAK_POINTS_SCORE_THRESHOLD (значимые
        ошибки) и формирует текстовый блок для промпта.

        Если history_manager не передан, истории по теме нет, или все
        прошлые результаты были с хорошим score — возвращает нейтральную
        фразу, означающую "слабых мест не найдено".
        """
        if self.history is None:
            return "Прошлых сессий по этой теме не найдено."

        sessions = self.history.get_topic_sessions(topic)
        if not sessions:
            return "Прошлых сессий по этой теме не найдено."

        sessions = sorted(sessions, key=lambda s: s["finished_at"])
        recent_sessions = sessions[-WEAK_POINTS_SESSIONS_LOOKBACK:]

        weak_results = []
        for session in recent_sessions:
            for result in session["results"]:
                if result["score"] < WEAK_POINTS_SCORE_THRESHOLD:
                    weak_results.append(result)

        if not weak_results:
            return "Прошлых сессий по этой теме не найдено значимых пробелов — можно двигаться дальше по теме без особого фокуса на повторении."

        lines = [
            "Слабые места пользователя по этой теме (из последних сессий) — "
            "учти их, но НЕ строй вокруг них все вопросы: посвяти их отработке "
            "не более 1-2 вопросов из общего числа, остальные веди обычной логикой по теме."
        ]
        for result in weak_results:
            lines.append(
                f"- Вопрос: {result['question']}\n"
                f"  Балл: {result['score']}/10\n"
                f"  Ошибки: {', '.join(result['mistakes']) if result['mistakes'] else '—'}\n"
                f"  Фидбек: {result['feedback']}"
            )

        return "\n".join(lines)