___
## Экосистема LangChain AI

**LangChain AI** — это большая открытая экосистема инструментов, предназначенных для эффективной разработки современных LLM-приложений.
![[Pasted image 20260614194611.png]]

В экосистему входят несколько инструментов:

- **LangChain** - фреймворк, предоставляющий необходимые компоненты для создания LLM-приложений. На данный момент представлен для двух языков: Python и JavaScript/TypeScript
- **LangGraph** - библиотека для построения LLM-приложений с LLM-агентами в виде направленных графов. На данный момент представлена для двух языков: Python и JavaScript/TypeScript
- **LangServe** - библиотека для быстрого развертывания LLM-приложения в качестве полноценного веб-сервиса. На данный момент доступна только для Python
- **LangSmith** - платформа для мониторинга и тестирования LLM-приложений, созданных на базе компонентов LangChain

### LangChain 

А начнем с основного фреймворка LangChain, который объединяет под собой несколько открытых библиотек:
- langchain-core: основные компоненты для создания LLM-приложений
- langchain-openai, langchain-anthropic и подобные: библиотеки для интеграции с различными вендорами, которые поддерживают разработчики LangChain и разработчики со стороны вендоров
- langchain: компоненты (например, агенты) для создания продвинутых LLM-приложений
- langchain-community: сторонние интеграции, которые поддерживаются сообществом

**ChatModel** является базовым компонентом в LangChain, предоставляющим единый интерфейс для работы с различными LLM-моделями. Свое название компонент получит из-за возможности передачи списка сообщений, то есть истории чата.

Предположим, что мы используем локальную модель, запущенную с помощью Ollama, тогда нам нужно установить пакет langchain-ollama. Из этой библиотеки мы будем импортировать **ChatOllama**. Для других вендоров, например, Open AI или Mistral AI, нужно устанавливать соответствующие пакеты для работы с их моделями.

Список доступных моделей представлен по ссылке: [https://python.langchain.com/docs/integrations/chat/](https://python.langchain.com/docs/integrations/chat/)

Создадим модель на основе загруженной **llama3.2:3b** и зададим для неё температуру:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)

user_message = "Где растут кактусы?"
answer = llm.invoke(user_message)
print(answer.content)
```

Метод **invoke** возвращает не просто текст ответа, а объект класса **AIMessage**, содержащий довольно много различной информации, которую мы уже могли наблюдать, когда обращались к Ollama через API. Фактически под капотом метода invoke выполняется вызов указанной модели.

```1c
AIMessage(
   content='Кактусы — это род семействаоказиантовых (Cactaceae), который включает более 1 500 видов. Они являются уникальными и интересными растениями, которые можно найти в различных регионах мира.\n\nРастут кактусы в тропических и subtropических регионах América, Африки, Аравии и Индии.', 
   additional_kwargs={}, 
   response_metadata={
        'model': 'llama3.2:3b', 
        'created_at': '2024-11-18T19:01:24.5324844Z', 
        'message': {'role': 'assistant', 'content': ''}, 
        'done_reason': 'length', 
        'done': True, 
        'total_duration': 9991480600, 
        'load_duration': 15846500, 
        'prompt_eval_count': 34, 
        'prompt_eval_duration': 65232000,
        'eval_count': 150, 
        'eval_duration': 9909769000
   },
   id='run-51b8f8d7-8cc8-4fc0-b344-d33419f2d505-0',
   usage_metadata={'input_tokens': 34, 'output_tokens': 150, 'total_tokens': 184}
)
```

Текст ответа находится в атрибуте content, информация о используемых токенах содержится в `usage_metadata`.

### Messages

Во фреймворке LangChain сообщения выделены в отдельные классы: **AIMessage**, **HumanMessage** и **SystemMessage**, соответствующие различным ролям и наследующиеся от класса **BaseMessage**. При вызове модели мы можем передать список сообщений, чтобы модель могла учитывать его при ответе. Например, в коде ниже модель переводит сообщения пользователя с русского на английский язык.

```python
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_predict=150
)

messages = [
    SystemMessage(content="You translate Russian to English. Translate the user sentence and write only result:"),
    HumanMessage(content="Я создам успешный AI-продукт!")
]

ai_message = llm.invoke(messages)
print(ai_message.content) # 'I will create a successful AI product!'
```

### Методы invoke, stream, batch

Ранее мы рассматривали метод invoke, который обрабатывает один запрос и возвращает полноценный сгенерированный ответ. Помимо invoke у ChatModel еще есть методы **stream** и **batch**.

ChatModel поддерживает стриминговый или потоковый тип исполнения, при котором ответ модели возвращается по мере его генерации. В качестве ответа возвращается объект класса AIMessageChunk. Попробуем заменить вывод модели из прошлого примера следующими двумя строчками. Это может быть полезно, когда мы не хотим дожидаться конца ответа модели, а хотим видеть результат сразу же.

```python
for message_chunk in llm.stream(messages):
    print(message_chunk.content, end="")
```

Другой тип исполнения это батчевый или пакетный, при котором модель может почти одновременно обрабатывать несколько запросов, что повышает эффективность обработки данных.

```undefined
answer_1, answer_2 = llm.batch([messages_1, messages_2])
```