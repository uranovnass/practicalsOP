
import threading
import time
import random

THREADS = 4
PHASES = 3


class Barrier:
    def __init__(self, parties):
        self.parties = parties
        self.arrived = 0
        self.generation = 0
        self.condition = threading.Condition()

    def wait(self):
        with self.condition:
            current_generation = self.generation
            self.arrived += 1

            if self.arrived == self.parties:
                # Последний поток открывает барьер
                self.arrived = 0
                self.generation += 1
                self.condition.notify_all()
            else:
                # Остальные ждут открытия барьера
                while current_generation == self.generation:
                    self.condition.wait()


barrier = Barrier(THREADS)


def worker(thread_id):
    for phase in range(1, PHASES + 1):
        print(
            f"Поток {thread_id}: начал фазу {phase}"
        )

        # Имитация работы разной продолжительности
        time.sleep(random.uniform(0.1, 0.5))

        print(
            f"Поток {thread_id}: завершил фазу {phase}"
        )

        barrier.wait()

        print(
            f"Поток {thread_id}: перешёл за барьер фазы {phase}"
        )


threads = [
    threading.Thread(target=worker, args=(i,))
    for i in range(1, THREADS + 1)
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Все 4 потока завершили 3 фазы.")
