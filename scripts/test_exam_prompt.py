import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.LLM_client import LLMClient
from services.common.ObsidianLoader import ObsidianLoader
from services.common.MarkdownCleaner import MarkdownCleaner
from services.common.QuestionGenerator import QuestionGenerator
from config.elo_config import ELO_TOPICS_ORDER, obsidian_path
from config.config_for_question import cache_path, QUESTIONS_PER_EXAM
from config.prompts import EXAM_PROMPT

if __name__ == "__main__":
    topics = [t["topic"] for t in ELO_TOPICS_ORDER]
    print("Доступные темы:")
    for i, t in enumerate(topics, 1):
        print(f"  {i}. {t}")

    choice = input("\nНомер темы (Enter = 1): ").strip()
    idx = int(choice) - 1 if choice else 0
    topic = topics[idx]

    llm = LLMClient(model_name="deepseek/deepseek-v4-flash")
    loader = ObsidianLoader(obsidian_path)
    cleaner = MarkdownCleaner(loader)

    notes = loader.load_notes()
    note = next((n for n in notes if n.title == topic), None)
    if note is None:
        print(f"Ошибка: заметка '{topic}' не найдена в Obsidian.")
        sys.exit(1)

    note = cleaner.clean(note)

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            image_cache = json.load(f)
    except FileNotFoundError:
        image_cache = {}

    pattern = re.compile(r"\[IMAGE:([^\]]+)\]")
    note.cleaned_content = pattern.sub(
        lambda m: image_cache.get(m.group(1), {}).get("description", m.group(0)),
        note.cleaned_content
    )

    generator = QuestionGenerator(llm, prompt_template=EXAM_PROMPT)
    questions = generator.generator_questions(
        topic=topic,
        note=note.cleaned_content,
        num_questions=QUESTIONS_PER_EXAM,
    )

    print(f"\n=== {topic} — {len(questions.questions)} вопросов ===\n")
    for q in questions.questions:
        print(f"[{q.id}] [{q.difficulty}] [{q.question_type}]")
        print(f"    {q.question}\n")