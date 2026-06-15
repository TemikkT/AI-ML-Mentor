from langchain_openrouter import ChatOpenRouter # Позволяет LongChain отправлять запросы в OpenRouter
from langchain_core.messages import SystemMessage, HumanMessage
"""
SystemMessage - инструкция для модели, то что подаётся всегда модели перед промптами. 
Там говорится кто она и для чего создана, расписан её характер и поведение

HumanMessage - Сообщение пользователя, его вопрос самой модели
"""
from dotenv import load_dotenv
load_dotenv()


def get_llm(): # функция создания модели, берём модель из OpenRouter и задаём ей температуру, уровень её оригинальности при ответах
    return ChatOpenRouter(
        model ="deepseek/deepseek-v4-flash",
        temperature=0.35,
    )

def ask_llm(system_promt: str, user_promt: str): # Функция общения с моделью
    model = get_llm() # получаем модель и её темпарутур из прошлой функции
    messages = [ 
        SystemMessage(content=system_promt), # опеределяем инструкцию для модели
        HumanMessage(content=user_promt) # подём ей сообщение пользователя
    ]

    """
    Стриминг ответа, выводим его по частям в прямом времени, 
    а не ждём пока создаться всё и выведется.
    Если же захотим вывести всё сразу, то вызываем просто 
    response = model.invoke(messages)
    """
    for chunk in model.stream(messages): 
        if chunk.content: # если чанк не пустой, то ответ есть и выводим его, пока не придём к пустому чанку
            print(chunk.content, end="", flush=True) # flush = True : Заставляет Python сразу вывести текст на экран. Без него часть текста может ждать в буфере.
    
    print()

"""
answer = ask_llm( # Создаём ответ и инструкцию, которую подаём в функцию сообщения модели
    system_prompt="Ты ментор по машинному обучению",
    user_promt="Объясни MLE простыми словами"
)
"""



notes = { # Создание небольших записей для модели, проверка, мини обсидиан, как он смотрит вообще на записи
    "MLE": """
Maximum Likelihood Estimation (MLE) —
метод оценки параметров модели.

Основная идея:
найти параметры, которые делают наблюдаемые данные
максимально вероятными.
""",

    "Logistic Regression": """
Логистическая регрессия использует сигмоиду.

Функция потерь:
Binary Cross Entropy.

Обучение выполняется методом градиентного спуска.
"""
}


selected_topic = notes["MLE"] # выбираем из записей тему MLE
prompt = f""" 
Вот заметка пользователя:

{selected_topic}

Сгенерируй 5 вопросов.

Требования:
- вопросы по теме заметки;
- можно слегка дополнить материал;
- от простого к сложному;
- без проектов.
"""

ask_llm( #
    "Ты опытный ML-ментор.",
    prompt
)



