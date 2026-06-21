"""
Тест адаптивного обучения.

Состоит из двух частей:

1. test_history_manager_and_statistics()
   Прогоняет каждый метод HistoryManager и ProgressAnalyzer
   на заранее известных, контролируемых данных, чтобы можно было
   руками сверить ожидаемый и фактический результат.

2. test_topic_selector_distribution()
   1000 раз вызывает TopicSelector.choose_topic() и считает,
   сколько раз выпала каждая тема — чтобы увидеть, насколько
   адекватно работает взвешенный выбор (плохие/старые темы
   должны выпадать чаще, чем сильные/недавние).

Запуск: python3 simulate.py
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from services.common.HistoryManager import HistoryManager
from services.common.StatisticsManager import ProgressAnalyzer
from services.theory.TopicSelector import TopicSelector


DATA_DIR = Path(__file__).parent / "data"
HISTORY_FILE = DATA_DIR / "test_history.json"


# ---------------------------------------------------------------------------
# Вспомогательные функции для построения тестовых данных
# ---------------------------------------------------------------------------

def iso(days_ago: float) -> str:
    """Возвращает ISO-таймстамп N дней назад от текущего момента."""
    return (datetime.now() - timedelta(days=days_ago)).isoformat()


def make_result(topic: str, score: int, difficulty: str = "medium") -> dict:
    """Собирает один QuestionResult в виде dict (как он реально лежит в JSON)."""
    return {
        "topic": topic,
        "question": f"Вопрос по теме {topic}",
        "answer": "тестовый ответ",
        "difficulty": difficulty,
        "score": score,
        "correct_parts": ["что-то верно"] if score >= 5 else [],
        "mistakes": [] if score >= 5 else ["что-то неверно"],
        "feedback": "тестовый фидбек",
        "timestamp": datetime.now().isoformat(),
    }


def make_session(topic: str, scores: list[int], days_ago: float, difficulty: str = "medium") -> dict:
    """Собирает одну TrainingSession в виде dict."""
    results = [make_result(topic, score, difficulty) for score in scores]
    avg = round(sum(scores) / len(scores), 2) if scores else 0
    return {
        "topic": topic,
        "started_at": iso(days_ago),
        "finished_at": iso(days_ago),
        "results": results,
        "average_score": avg,
    }


def write_history(sessions: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def fresh_history_manager(sessions: list[dict]) -> HistoryManager:
    """Создаёт HistoryManager с заранее заданной историей."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    write_history(sessions)
    return HistoryManager(file_path=str(HISTORY_FILE))


def section(title: str):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def check(label: str, actual, expected=None):
    """Печатает результат проверки. Если expected задан — сверяет и помечает совпадение."""
    if expected is None:
        print(f"  {label}: {actual}")
    else:
        status = "OK " if actual == expected else "FAIL"
        print(f"  [{status}] {label}: actual={actual!r} expected={expected!r}")


# ---------------------------------------------------------------------------
# Тестовые данные:
#
# - "Линейная регрессия"   -> сильная тема: высокие баллы, повторялась недавно
# - "SVM"                  -> слабая тема: низкие баллы, повторялась недавно
# - "Деревья решений"      -> средняя тема, давно не повторялась (21 день)
# - "Кластеризация"        -> 1 сессия, очень давно (60 дней), низкий балл
#
# "Новая тема" из заметок не имеет ни одной сессии в истории вообще —
# это случай новой темы с весом 15 по умолчанию (проверяется в TopicSelector).
# ---------------------------------------------------------------------------

def build_test_sessions() -> list[dict]:
    sessions = []

    # Линейная регрессия: 3 сессии, баллы растут, последняя совсем недавно (1 день назад)
    sessions.append(make_session("Линейная регрессия", [7, 8], days_ago=10, difficulty="easy"))
    sessions.append(make_session("Линейная регрессия", [9, 9], days_ago=5, difficulty="medium"))
    sessions.append(make_session("Линейная регрессия", [10, 9], days_ago=1, difficulty="hard"))

    # SVM: 2 сессии, баллы низкие, последняя 2 дня назад
    sessions.append(make_session("SVM", [3, 4], days_ago=8, difficulty="medium"))
    sessions.append(make_session("SVM", [4, 5], days_ago=2, difficulty="medium"))

    # Деревья решений: 1 сессия, средний балл, давно не повторялась (21 день)
    sessions.append(make_session("Деревья решений", [6, 7], days_ago=21, difficulty="medium"))

    # Кластеризация: 1 сессия, низкий балл, очень давно (60 дней)
    sessions.append(make_session("Кластеризация", [2], days_ago=60, difficulty="hard"))

    return sessions


# ---------------------------------------------------------------------------
# Часть 1: HistoryManager + ProgressAnalyzer
# ---------------------------------------------------------------------------

def test_history_manager_and_statistics():
    section("ЧАСТЬ 1: HistoryManager и ProgressAnalyzer (StatisticsManager)")

    sessions = build_test_sessions()
    history = fresh_history_manager(sessions)
    analyzer = ProgressAnalyzer(history)

    # --- load_history ---
    print("\n-- load_history() --")
    loaded = history.load_history()
    check("количество сессий в истории", len(loaded), expected=7)

    # --- get_topic_sessions ---
    print("\n-- get_topic_sessions() --")
    lr_sessions = history.get_topic_sessions("Линейная регрессия")
    check("сессий по 'Линейная регрессия'", len(lr_sessions), expected=3)
    none_sessions = history.get_topic_sessions("Тема которой нет")
    check("сессий по несуществующей теме", len(none_sessions), expected=0)

    # --- get_topic_scores ---
    print("\n-- get_topic_scores() --")
    lr_scores_all = history.get_topic_scores("Линейная регрессия")
    check("все баллы 'Линейная регрессия'", sorted(lr_scores_all), expected=[7, 8, 9, 9, 9, 10])
    lr_scores_last1 = history.get_topic_scores("Линейная регрессия", last_n_sessions=1)
    check("баллы за последнюю 1 сессию 'Линейная регрессия'", sorted(lr_scores_last1), expected=[9, 10])

    # --- get_average_score ---
    print("\n-- get_average_score() --")
    avg_lr_last2 = history.get_average_score("Линейная регрессия", last_n=2)
    # последние 2 сессии: [9,9] и [10,9] -> (9+9+10+9)/4 = 9.25
    check("средний балл 'Линейная регрессия' (last_n=2)", avg_lr_last2, expected=9.25)

    avg_svm_last2 = history.get_average_score("SVM", last_n=2)
    # обе сессии SVM: [3,4,4,5] -> 4.0
    check("средний балл 'SVM' (last_n=2)", avg_svm_last2, expected=4.0)

    avg_missing = history.get_average_score("Тема которой нет", last_n=2)
    check("средний балл несуществующей темы -> None", avg_missing, expected=None)

    # --- topic_statistics ---
    print("\n-- topic_statistics() --")
    stats_all = history.topic_statistics(last_n=2)
    check("все темы присутствуют в topic_statistics", sorted(stats_all.keys()),
          expected=sorted(["Линейная регрессия", "SVM", "Деревья решений", "Кластеризация"]))

    # --- get_last_review / days_since_review ---
    print("\n-- get_last_review() / days_since_review() --")
    last_review_lr = history.get_last_review("Линейная регрессия")
    print(f"  последний повтор 'Линейная регрессия': {last_review_lr} (ожидалось ~1 день назад)")
    days_lr = history.days_since_review("Линейная регрессия")
    check("дней с повтора 'Линейная регрессия' (примерно)", days_lr in (0, 1), expected=True)

    days_cluster = history.days_since_review("Кластеризация")
    check("дней с повтора 'Кластеризация' (примерно)", days_cluster in (59, 60), expected=True)

    days_missing = history.days_since_review("Тема которой нет")
    check("дней с повтора несуществующей темы -> None", days_missing, expected=None)

    # --- get_sessions_count ---
    print("\n-- get_sessions_count() --")
    check("количество сессий 'SVM'", history.get_sessions_count("SVM"), expected=2)
    check("количество сессий 'Кластеризация'", history.get_sessions_count("Кластеризация"), expected=1)

    # --- get_statistics / get_statistics_topic ---
    print("\n-- get_statistics() / get_statistics_topic() --")
    full_stats = history.get_statistics(last_n=2)
    for topic, stat in full_stats.items():
        print(f"  {topic}: {stat}")

    one_stat = history.get_statistics_topic("SVM", last_n=2)
    print(f"  get_statistics_topic('SVM'): {one_stat}")

    # --- calculate_weight / get_topic_weight ---
    print("\n-- calculate_weight() / get_topic_weight() --")
    for topic in ["Линейная регрессия", "SVM", "Деревья решений", "Кластеризация"]:
        stat = full_stats[topic]
        weight = history.calculate_weight(topic, stat)
        weight_via_method = history.get_topic_weight(topic)
        match = "OK " if abs(weight - weight_via_method) < 1e-9 else "FAIL"
        print(f"  [{match}] {topic}: calculate_weight={weight:.2f} | get_topic_weight={weight_via_method:.2f} "
              f"(avg={stat['average_score']}, days={stat['days_since_review']}, sessions={stat['sessions']})")

    # Ожидаемая логика весов (по комментарию в коде):
    # - чем ниже средний балл, тем выше вес
    # - чем больше дней без повтора, тем выше вес (до +10)
    # - чем меньше сессий, тем выше вес (до +5)
    print("\n  Ожидание: 'SVM' (низкий балл) и 'Кластеризация' (давно+1 сессия) должны иметь")
    print("  заметно более высокий вес, чем 'Линейная регрессия' (высокий балл, недавно, много сессий).")

    # --- ProgressAnalyzer ---
    print("\n-- ProgressAnalyzer.average_score() --")
    overall_avg = analyzer.average_score()
    all_scores = [r["score"] for s in sessions for r in s["results"]]
    expected_overall = round(sum(all_scores) / len(all_scores), 2)
    check("общий средний балл", overall_avg, expected=expected_overall)

    print("\n-- ProgressAnalyzer.topic_statistics() --")
    print(f"  {analyzer.topic_statistics()}")

    print("\n-- ProgressAnalyzer.weak_topics() / strong_topics() --")
    print(f"  weak_topics(threshold=6.5): {analyzer.weak_topics(threshold=6.5)}")
    print(f"  strong_topics(threshold=9.0): {analyzer.strong_topics(threshold=9.0)}")

    print("\n-- ProgressAnalyzer.topics_without_practice() --")
    print(f"  topics_without_practice(days=14): {analyzer.topics_without_practice(days=14)}")
    print("  Ожидание: должны попасть 'Деревья решений' (21 день) и 'Кластеризация' (60 дней)")

    print("\n-- ProgressAnalyzer.solved_questions() / solved_sessions() --")
    total_results = sum(len(s["results"]) for s in sessions)
    check("solved_questions()", analyzer.solved_questions(), expected=total_results)
    check("solved_sessions()", analyzer.solved_sessions(), expected=len(sessions))

    print("\n-- ProgressAnalyzer.average_by_difficulty() --")
    print(f"  {analyzer.average_by_difficulty()}")
    print("  (easy/medium/hard в соответствии с тем, что задано в build_test_sessions)")

    print("\n-- ProgressAnalyzer.progress_summary() --")
    print(f"  {analyzer.progress_summary()}")

    return history


# ---------------------------------------------------------------------------
# Часть 2: распределение TopicSelector за 1000 итераций
# ---------------------------------------------------------------------------

class FakeNote:
    """
    Минимальная замена реальной Note (pydantic-модель) —
    TopicSelector использует только note.title, поэтому полноценная
    модель здесь не нужна.
    """
    def __init__(self, title: str):
        self.title = title


def test_topic_selector_distribution(history: HistoryManager, iterations: int = 1000):
    section(f"ЧАСТЬ 2: распределение TopicSelector за {iterations} итераций")

    # Темы, которые "есть в Obsidian" (notes) — включает темы из истории
    # плюс одну совершенно новую тему без единой сессии.
    note_titles = [
        "Линейная регрессия",
        "SVM",
        "Деревья решений",
        "Кластеризация",
        "Новая тема без истории",
    ]
    notes = [FakeNote(title) for title in note_titles]

    selector = TopicSelector(history)

    # Покажем веса, которые реально участвуют в random.choices
    statistics = history.get_statistics()
    print("\nВеса тем перед прогоном (как их видит TopicSelector.choose_topic):")
    for title in note_titles:
        if title in statistics:
            weight = history.calculate_weight(title, statistics[title])
        else:
            weight = 15  # вес новой темы по умолчанию (см. TopicSelector)
        print(f"  {title}: weight={weight:.2f}")

    counts = {title: 0 for title in note_titles}

    for _ in range(iterations):
        topic, note = selector.choose_topic(notes)
        counts[topic] += 1

    print(f"\nРезультат за {iterations} итераций:")
    total = sum(counts.values())
    for title, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        pct = 100 * count / total
        bar = "#" * int(pct // 2)
        print(f"  {title:30s} {count:5d} ({pct:5.1f}%)  {bar}")

    # Проверка пустого списка notes — должен падать с ValueError (по договорённости)
    print("\n-- Проверка choose_topic() с пустым списком заметок --")
    try:
        selector.choose_topic([])
        print("  [FAIL] ожидался ValueError, но исключение не было выброшено")
    except ValueError as e:
        print(f"  [OK ] ValueError выброшен как и ожидалось: {e}")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    history = test_history_manager_and_statistics()
    test_topic_selector_distribution(history, iterations=1000)

    # Уборка тестового файла истории
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()

    print()
    print("=" * 70)
    print("Тест завершён.")
    print("=" * 70)
