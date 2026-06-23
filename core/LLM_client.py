from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import base64
from openai import OpenAI
import os
"""
SystemMessage - инструкция для модели, то что подаётся всегда модели перед промптами. 
Там говорится кто она и для чего создана, расписан её характер и поведение

HumanMessage - Сообщение пользователя, его вопрос самой модели

AIMessage - предыдущая реплика самой модели. Нужна для передачи истории
диалога в ask_stream — LLMClient сам не хранит состояние чата
(оно живёт в st.session_state на стороне Streamlit-страницы), поэтому
каждый вызов получает ПОЛНУЮ историю целиком.
"""
from dotenv import load_dotenv
load_dotenv() # выгрузка API ключа
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class LLMClient():
    def __init__(self, model_name: str, temperature: float = 0.3):
        self.model = ChatOpenRouter(model = model_name, temperature = temperature) # получаем модель и её темпарутур из прошлой функции
        self.api_key = os.getenv("OPENROUTER_API_KEY")


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


    def ask_stream(self, system_prompt: str, history: list[dict]):
        """
        Стриминговый чат для UI (Streamlit). В отличие от ask(), НЕ печатает
        в консоль и НЕ ограничен одной репликой — возвращает генератор
        текстовых чанков, который вызывающий код (например, st.write_stream)
        сам отрисовывает по мере поступления.

        LLMClient не хранит историю диалога — она передаётся целиком на
        каждый вызов через параметр history, в формате:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        (именно так удобно хранить историю в st.session_state на стороне
        Streamlit-страницы — обычный список словарей, без зависимости от
        классов langchain).

        system_prompt передаётся отдельно и всегда идёт первым сообщением.
        """
        messages = [SystemMessage(content=system_prompt)]

        for entry in history:
            if entry["role"] == "user":
                messages.append(HumanMessage(content=entry["content"]))
            elif entry["role"] == "assistant":
                messages.append(AIMessage(content=entry["content"]))
            # неизвестные роли молча пропускаем — не должно случаться,
            # но лучше не падать на постороннем мусоре в истории

        for chunk in self.model.stream(messages):
            if chunk.content:
                yield chunk.content


    def get_structured_llm(self, schema): # создаём метод, который будет отвечать за структуру ответа, как будет выглядеть ответ от модели
        return self.model.with_structured_output(schema) # Возвращаем ответ модели по нужной нам, заданой структуре, схеме (PromptTemplate)
    


    def describe_image(self, image_path: str, prompt: str, vision_model: str = "qwen/qwen3-vl-32b-instruct") -> str:
        """
        Анализирует изображение при помощи Vision-модели.
        """

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key) #Создаём опять запрос к модели, в этот раз без HumanMessage, чтобы модель не думала, что это диалог
        image = self._image_to_base64(image_path) # Переопределяем расширение изображения, только такое принимает OpenRouter (или URL ссылка, такого у меня нет)
        response = client.chat.completions.create(model=vision_model, temperature=0, messages=[ # задаём параметры модели, которую модем использовать и сообщение ей
                {
                    "role": "system",
                    "content": (
                        "Ты эксперт по анализу изображений из учебных конспектов. "
                        "Отвечай кратко и только по существу."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image}"
                            }
                        }
                    ]
                }
            ]
        )

        return response.choices[0].message.content


    def _image_to_base64(self, image_path: str) -> str: 
        """
        Кодирует изображение в Base64.
        """

        with open(image_path, "rb") as image: # перебираем все изображения, точнее ищем то, чей путь мы дали.
            encoded = base64.b64encode(
                image.read()
            ).decode("utf-8")

        return encoded

