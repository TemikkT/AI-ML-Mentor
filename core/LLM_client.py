from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage
"""
SystemMessage - инструкция для модели, то что подаётся всегда модели перед промптами. 
Там говорится кто она и для чего создана, расписан её характер и поведение

HumanMessage - Сообщение пользователя, его вопрос самой модели
"""
from dotenv import load_dotenv
load_dotenv() # выгрузка API ключа


class LLMClient():
    def __init__(self, model_name: str, temperature: float = 0.3):
        self.model = ChatOpenRouter(model = model_name, temperature = temperature) # получаем модель и её темпарутур из прошлой функции


    def ask(self, system_prompt: str, user_prompt: str) -> str: # Функция общения с моделью
        messages = [
            SystemMessage(content=system_prompt), # опеределяем инструкцию для модели
            HumanMessage(content=user_prompt) # подём ей сообщение пользователя
        ]

        """
        Стриминг ответа, выводим его по частям в прямом времени, 
        а не ждём пока создаться всё и выведется.
        Если же захотим вывести всё сразу, то вызываем просто 
        response = model.invoke(messages)
        """
        for chunk in self.model.stream(messages):
            if chunk.content: # если чанк не пустой, то ответ есть и выводим его, пока не придём к пустому чанку
                print(chunk.content, end="", flush=True) # flush = True : Заставляет Python сразу вывести текст на экран. Без него часть текста может ждать в буфере.
        print()

    def get_structured_llm(self, schema): # создаём метод, который будет отвечать за структуру ответа, как будет выглядеть ответ от модели
        return self.model.with_structured_output(schema) # Возвращаем ответ модели по нужной нам, заданой структуре, схеме (PromptTemplate)



"""
1. Храним заметки в словаре
2. Выбираем случайную тему
3. Генерируем вопросы
4. Отвечаем на вопросы
5. Получаем оценку
"""