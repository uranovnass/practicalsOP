
import threading
from collections import Counter

BUFFER_SIZE = 5
TOTAL_ITEMS = 1000
PRODUCERS = 3
CONSUMERS = 2

buffer = [None] * BUFFER_SIZE
write_pos = 0
read_pos = 0
buffer_count = 0

condition = threading.Condition()
consumed = []
errors = []


def produce(producer_id):
    global write_pos, buffer_count

    for item in range(producer_id, TOTAL_ITEMS, PRODUCERS):
        with condition:
            while buffer_count == BUFFER_SIZE:
                condition.wait()

            if buffer_count > BUFFER_SIZE:
                errors.append("Буфер переполнен!")

            buffer[write_pos] = item
            write_pos = (write_pos + 1) % BUFFER_SIZE
            buffer_count += 1

            condition.notify_all()


def consume(consumer_id):
    global read_pos, buffer_count

    while True:
        with condition:
            while buffer_count == 0:
                condition.wait()

            item = buffer[read_pos]
            buffer[read_pos] = None
            read_pos = (read_pos + 1) % BUFFER_SIZE
            buffer_count -= 1

            if buffer_count < 0:
                errors.append("Счётчик меньше нуля!")

            condition.notify_all()

        if item is None:
            break

        consumed.append(item)


consumers = [
    threading.Thread(target=consume, args=(i,))
    for i in range(CONSUMERS)
]

producers = [
    threading.Thread(target=produce, args=(i,))
    for i in range(PRODUCERS)
]

for thread in consumers:
    thread.start()

for thread in producers:
    thread.start()

for thread in producers:
    thread.join()

# Помещаем завершающий маркер для каждого потребителя
with condition:
    for _ in range(CONSUMERS):
        while buffer_count == BUFFER_SIZE:
            condition.wait()

        buffer[write_pos] = None
        write_pos = (write_pos + 1) % BUFFER_SIZE
        buffer_count += 1

        condition.notify_all()

for thread in consumers:
    thread.join()

counts = Counter(consumed)
missing = sorted(set(range(TOTAL_ITEMS)) - set(consumed))
duplicates = sorted(
    item for item, count in counts.items() if count > 1
)

print("Всего потреблено:", len(consumed))
print("Пропущено:", len(missing))
print("Дубликатов:", len(duplicates))
print("Остаток в буфере:", buffer_count)
print("Ошибок:", len(errors))

if (
    len(consumed) == TOTAL_ITEMS
    and not missing
    and not duplicates
    and buffer_count == 0
    and not errors
):
    print("РЕЗУЛЬТАТ: ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
else:
    print("РЕЗУЛЬТАТ: ОБНАРУЖЕНЫ НАРУШЕНИЯ")
    print("Примеры пропусков:", missing[:10])
    print("Примеры дубликатов:", duplicates[:10])
    print("Ошибки:", errors[:10])


# Отдельная демонстрация ошибки при использовании if вместо while
def demonstrate_bad_if():
    bad_condition = threading.Condition()
    state = {"items": 0, "waiting": 0}
    violations = []

    def bad_consumer():
        with bad_condition:
            state["waiting"] += 1
            bad_condition.notify_all()

            # Намеренно неправильно: здесь должен быть while
            if state["items"] == 0:
                bad_condition.wait()

            if state["items"] == 0:
                violations.append(
                    "Поток проснулся, но доступных элементов нет!"
                )
            else:
                state["items"] -= 1

    threads = [
        threading.Thread(target=bad_consumer)
        for _ in range(2)
    ]

    for thread in threads:
        thread.start()

    with bad_condition:
        while state["waiting"] < 2:
            bad_condition.wait()

        state["items"] = 1
        bad_condition.notify_all()

    for thread in threads:
        thread.join()

    print("\nДемонстрация неправильного if:")
    print("Ожидалось доступных элементов: 1")
    print("Нарушений после пробуждения:", len(violations))

    for violation in violations:
        print("НАРУШЕНИЕ:", violation)


demonstrate_bad_if()
