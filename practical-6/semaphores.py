
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

empty = threading.Semaphore(BUFFER_SIZE)
full = threading.Semaphore(0)
mutex = threading.Lock()

consumed = []
errors = []
consumed_lock = threading.Lock()


def produce(producer_id):
    global write_pos, buffer_count

    for item in range(producer_id, TOTAL_ITEMS, PRODUCERS):
        empty.acquire()

        with mutex:
            if buffer_count >= BUFFER_SIZE:
                errors.append("Буфер переполнен!")

            buffer[write_pos] = item
            write_pos = (write_pos + 1) % BUFFER_SIZE
            buffer_count += 1

            if buffer_count > BUFFER_SIZE:
                errors.append("Нарушен размер буфера!")

        full.release()


def consume(consumer_id):
    global read_pos, buffer_count

    while True:
        full.acquire()

        with mutex:
            item = buffer[read_pos]
            buffer[read_pos] = None
            read_pos = (read_pos + 1) % BUFFER_SIZE
            buffer_count -= 1

            if buffer_count < 0:
                errors.append("Счётчик буфера меньше нуля!")

        empty.release()

        if item is None:
            break

        with consumed_lock:
            consumed.append(item)


consumer_threads = [
    threading.Thread(target=consume, args=(i,))
    for i in range(CONSUMERS)
]

producer_threads = [
    threading.Thread(target=produce, args=(i,))
    for i in range(PRODUCERS)
]

for thread in consumer_threads:
    thread.start()

for thread in producer_threads:
    thread.start()

for thread in producer_threads:
    thread.join()

# Завершающие маркеры: по одному для каждого потребителя
for _ in range(CONSUMERS):
    empty.acquire()

    with mutex:
        buffer[write_pos] = None
        write_pos = (write_pos + 1) % BUFFER_SIZE
        buffer_count += 1

    full.release()

for thread in consumer_threads:
    thread.join()

counts = Counter(consumed)
missing = sorted(set(range(TOTAL_ITEMS)) - set(consumed))
duplicates = sorted(
    item for item, count in counts.items() if count > 1
)

print("Всего произведено элементов:", TOTAL_ITEMS)
print("Всего потреблено элементов:", len(consumed))
print("Пропущено элементов:", len(missing))
print("Дубликатов:", len(duplicates))
print("Элементов осталось в буфере:", buffer_count)
print("Ошибок буфера:", len(errors))

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
