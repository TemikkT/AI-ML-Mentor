from services.HistoryManager import HistoryManager

history = HistoryManager()

print("=" * 60)
print("История")
print("=" * 60)

print(history.load_history())

print()

print("=" * 60)
print("Средние оценки")
print("=" * 60)

stats = history.topic_statistics()

for topic, score in stats.items():
    print(f"{topic}: {score}")

print()

print("=" * 60)
print("Последнее повторение")
print("=" * 60)

for topic in stats:
    print(topic)
    print(history.get_last_review(topic))
    print()

print("=" * 60)
print("Дней с последнего повторения")
print("=" * 60)

for topic in stats:
    print(topic)
    print(history.days_since_review(topic))
    print()

print("=" * 60)
print("Вес темы")
print("=" * 60)

for topic in stats:
    print(topic)
    print(history.get_topic_weight(topic))
    print()