from core.LLM_client import LLMClient
from services.QuestionGenerator import QuestionGenerator
from services.AnswerEvaluator import AnswerEvaluator
from services.HistoryManager import HistoryManager
from services.TopicSelector import TopicSelector
from services.ObsidianLoader import ObsidianLoader
from services.MarkdownCleaner import MarkdownCleaner
from services.VisionAnalyzer import VisionAnalyzer

from schemas.Note import Note
import json
import re

cache_path = "data/image_cache.json"
"""
Создаем основные объекты
"""
llm = LLMClient(model_name="deepseek/deepseek-v4-flash")

generator = QuestionGenerator(llm)
evaluator = AnswerEvaluator(llm)

history = HistoryManager()
selector = TopicSelector(history)

"""
Выгружаем обсидиан и выбираем топик
"""
loader = ObsidianLoader(r"C:\Users\user\Documents\obsidian") #Загрузка всего обсидиана
notes = loader.load_notes() # берём наш класс Данных Note

topic, notes_topic, weight = selector.choose_topic(notes)
print(topic, weight)


cleaner = MarkdownCleaner(loader) # отчистим текст данной записки
clean_note = cleaner.clean(notes_topic)

with open(cache_path, "r", encoding="utf-8") as f: # достаём JSON с обработанными изображениями
    image_note = json.load(f)

pattern = re.compile(r"\[IMAGE:([^\]]+)\]")

 # заменяем изображения на их обработанный текст
clean_note.cleaned_content = pattern.sub(lambda m: image_note.get(m.group(1), {}).get("description", m.group(0)),clean_note.cleaned_content)

questions = generator.generator_questions(topic = topic, note = clean_note.cleaned_content, num_questions=2)
for question in questions.questions:
    print("\n" + "=" * 50)
    print(f"Вопрос {question.id}")
    print(question.question)
    print(f"Сложность вопроса: {question.difficulty}")

    answer_human = input("Отвеечаааай бляха муха: ")
    answers = evaluator.evaluate(topic = topic, question = question.question, answer = answer_human)
    
    print(f'Оценка: {answers.score}')
    print('_________')
    print('Что ответил верно: ')
    print(answers.correct_parts)
    print('_________')
    print('Где ошибся: ')
    print(answers.mistakes)
    print('_________')
    print(f'Фидбек:')
    print(answers.feedback)