
import threading
import time

counter = 0
THREADS = 4
INCREMENTS = 1000


def increment():
    global counter

    for _ in range(INCREMENTS):
        # Читаем значение отдельно от его изменения
        value = counter
        time.sleep(0)
        counter = value + 1


threads = []

for _ in range(THREADS):
    thread = threading.Thread(target=increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

expected = THREADS * INCREMENTS

print("Ожидаемый результат:", expected)
print("Фактический результат:", counter)

if counter != expected:
    print("НАРУШЕНИЕ: обнаружена гонка!")
else:
    print("Гонка не проявилась в этом запуске.")
