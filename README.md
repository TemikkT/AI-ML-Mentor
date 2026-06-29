# AI-ML-Mentor

> Адаптивная AI-платформа для изучения Machine Learning, Python и Data Analytics.
> Использует заметки из Obsidian как базу знаний, а LLM (через OpenRouter) — для генерации вопросов, оценки ответов и отслеживания прогресса по системе рейтинга Elo.

---

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone <your-repo-url>
cd AI-ML-Mentor
```

### 2. Настройте окружение

Создайте файл `.env` в корне проекта со следующими переменными:

```env
OPENROUTER_API_KEY=sk-or-v1-ваш_ключ_от_openrouter
```

| Переменная | Описание |
|---|---|
| `OPENROUTER_API_KEY` | **Обязательно.** API-ключ от [OpenRouter](https://openrouter.ai/) для доступа к LLM. |
| `OBSIDIAN_PATH` | Укажите путь к вашему Obsidian-хранилищу с заметками или используйте готовый внутри проекта. |

Получить ключ OpenRouter: [openrouter.ai/keys](https://openrouter.ai/keys)

### 3. Установите зависимости

Проект использует Python 3.12. Рекомендуется создать виртуальное окружение:

```bash
python -m venv venv
.\venv\Scripts\Activate   # Windows
source venv/bin/activate  # Linux / macOS
pip install -r req.txt
```

### 4. Запустите приложение

```bash
streamlit run app/Home.py
```

Приложение откроется в браузере по адресу `http://localhost:8501` (если выскакивает ошибка с app директорией, то просто прокликайте все страницы на сайте и оно пропадёт). 

### 5. (Опционально) Соберите кэш изображений

```bash
python build_image_cache.py
```

Это запустит Vision LLM для анализа изображений из заметок и закэширует их описания (если используется встроенный обсидиан, то не нужно).

---

## Архитектура проекта

```
AI_Agent/
│
├── app/                    # Streamlit-фронтенд
│   ├── Home.py             # Главная страница с выбором режима
│   ├── bootstrap.py        # Фабрика сервисов (с кэшированием st.cache_resource)
│   ├── chat_helper.py      # Боковой чат-ассистент (sidebar)
│   ├── ui/
│   │   └── theme.py        # Catppuccin Frappe тёмная тема + glass-morphism стили
│   └── Pages/
│       ├── 0_Notes.py      # Лекции — просмотр заметок по категориям
│       ├── 1_Theory_Elo.py # Теория (Elo) — адаптивные вопросы по темам
│       ├── 2_Practice_Elo.py # Практика (Elo) — задачи с выполнением кода
│       ├── 3_Interview.py  # Собеседование — случайные темы в формате интервью
│       └── 4_Statistics.py # Статистика — графики прогресса (Plotly)
│
├── core/                   # Слой связи с LLM
│   └── LLM_client.py       # Клиент OpenRouter: ask(), ask_stream(), get_structured_llm(), describe_image()
│
├── config/                 # Конфигурация и промпты
│   ├── prompts.py          # Все системные промпты для LLM
│   ├── config_for_question.py  # Глобальные настройки (количество вопросов, пути)
│   ├── elo_config.py       # Настройки Elo: темы, множители, пороги открытия
│   └── interview_config.py # Настройки режима собеседования
│
├── schemas/                # Pydantic-модели данных
│   ├── Note.py             # Заметка (домен, категория, заголовок, контент, изображения)
│   ├── note_image.py       # Изображение в заметке (путь, контекст, описание)
│   ├── questions.py        # Question, QuestionSet
│   ├── evaluation.py       # Evalution (оценка: баллы, ошибки, фидбек)
│   └── training_result.py  # QuestionResult, TrainingSession, ExecutionResult
│
├── services/               # Бизнес-логика
│   ├── common/
│   │   ├── ObsidianLoader.py     # Загрузка .md-файлов из Obsidian
│   │   ├── MarkdownCleaner.py    # Очистка и извлечение изображений из разметки
│   │   ├── QuestionGenerator.py  # Генерация вопросов через LLM (с учётом слабых мест)
│   │   ├── HistoryManager.py     # Менеджер истории сессий (JSON)
│   │   ├── VisionAnalyzer.py     # Описание изображений через Vision LLM
│   │   └── StatisticsManager.py  # Анализ прогресса: средние баллы, сильные/слабые темы
│   │
│   ├── elo/
│   │   ├── EloProgressManager.py # Рейтинг Elo: баллы, открытие новых тем (цепочка)
│   │   └── EloTrainer.py         # Тренировка теории: состояние -> вопрос -> оценка -> рейтинг
│   │
│   ├── practice/
│   │   ├── PracticeEloManager.py # Elo для практики (все темы открыты сразу)
│   │   ├── PracticeEvaluator.py  # Оценка кода + результатов выполнения
│   │   └── PracticeTrainer.py    # Тренировка практики: задача -> код -> выполнение -> фидбек
│   │
│   ├── Interview/
│   │   ├── AnswerEvaluator.py    # Оценка ответа (базовый промпт)
│   │   ├── TopicSelector.py      # Выбор тем: взвешенный random (низкий балл = выше вес)
│   │   └── InterviewTrainer.py   # Полный цикл собеседования (N тем по K вопросов)
│   │
│   ├── exam_topic/
│   │   └── ExamTrainer.py        # Экзамен по теме (20 вопросов, 90% покрытия)
│   │
│   └── prompt_template/
│       └── CodeExecutor.py       # Безопасное выполнение Python-кода в subprocess
│
├── data/                   # Runtime-данные
│   └── image_cache.json    # Кэш описаний изображений (генер. VisionAnalyzer)
│
├── app/data/               # JSON-файлы состояния (создаются в runtime)
│   ├── history.json             # История всех тренировок
│   ├── history_elo.json         # История Elo-сессий (для слабых мест)
│   ├── history_practice.json    # История практических сессий
│   ├── elo_state.json           # Текущие рейтинги Elo (теория)
│   └── practice_elo_state.json  # Текущие рейтинги Elo (практика)
│
├── obsidian/               # База знаний (копия Obsidian-хранилища)
│   ├── Аналитика данных и Python/  # 7 заметок
│   ├── Classic Machine Learning/   # 15 заметок
│   ├── Deep Machine Learning ОСНОВЫ/ # 5 заметок
│   ├── Computer Vision (CV)/       # 4 заметки
│   └── NLP ML/                     # 4 заметки
│
├── scripts/                # Вспомогательные скрипты
│   └── test_exam_prompt.py # CLI-тест промпта экзамена
│
├── .env                    # Переменные окружения (не в git)
├── .gitignore
├── build_image_cache.py    # Скрипт для пакетного кэширования изображений
├── req.txt                 # Полный список зависимостей (pip freeze)
└── README.md               # Этот файл
```

---

## Архитектурные паттерны

| Паттерн | Где используется |
|---|---|
| **State Machine** | `EloTrainer`, `PracticeTrainer`, `InterviewTrainer`, `ExamTrainer` — каждый управляет своим состоянием сессии |
| **Factory** | `bootstrap.py` создаёт и кэширует все сервисы через `st.cache_resource` |
| **Structured Output** | LLM-ответы валидируются Pydantic-схемами через `with_structured_output()` |
| **Elo Rating** | Адаптивная сложность: теория — цепочка с открытием тем, практика — свободный доступ |
| **Кэширование** | Описания изображений — в `image_cache.json`, LLM-клиент и сервисы — в Streamlit cache |

## Режимы работы

| Режим | Страница | Суть |
|---|---|---|
| **Лекции** | `0_Notes.py` | Просмотр заметок с изображениями по категориям |
| **Теория (Elo)** | `1_Theory_Elo.py` | Тема -> вопросы -> оценка -> рейтинг Elo -> открытие новой темы |
| **Практика (Elo)** | `2_Practice_Elo.py` | Код-задачи с выполнением Python в песочнице |
| **Собеседование** | `3_Interview.py` | Случайные темы, имитация реального интервью |
| **Статистика** | `4_Statistics.py` | Графики прогресса (Plotly): динамика, темы, сложность |

## Используемые технологии

- **Streamlit** — UI-фреймворк
- **LangChain / LangGraph** — работа с LLM
- **OpenRouter API** — доступ к моделям (deepseek-v4-pro, qwen3-vl и др.)
- **Pydantic** — схемы данных
- **Plotly** — визуализация статистики
- **Obsidian** — база знаний (markdown + вложения)