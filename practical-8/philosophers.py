
import threading
import time

N = 5
ROUNDS = 100


def run_philosophers(mode):
    forks = [threading.Lock() for _ in range(N)]
    meals = [0] * N

    # Для режима ограниченного числа философов.
    room = threading.Semaphore(N - 1)

    def philosopher(i):
        left = i
        right = (i + 1) % N

        for _ in range(ROUNDS):
            if mode == "numbering":
                first, second = sorted((left, right))
                forks[first].acquire()
                forks[second].acquire()

            elif mode == "limit":
                with room:
                    forks[left].acquire()
                    forks[right].acquire()

            else:
                # Небезопасный порядок: каждый берёт левую вилку,
                # а затем пытается взять правую.
                forks[left].acquire()
                forks[right].acquire()

            meals[i] += 1

            forks[right].release()
            forks[left].release()

    threads = [
        threading.Thread(target=philosopher, args=(i,))
        for i in range(N)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=3)

    stuck = any(thread.is_alive() for thread in threads)

    if stuck:
        print("Возможна взаимоблокировка; потоки не завершились.")
    else:
        print("Все потоки завершились.")

    print("Режим:", mode)
    for i, count in enumerate(meals):
        print(f"Философ {i}: поел {count} раз")

    print("Всего приёмов пищи:", sum(meals))
    print()


if __name__ == "__main__":
    print("=== Исправление 1: нумерация вилок ===")
    run_philosophers("numbering")

    print("=== Исправление 2: ограничение числа философов ===")
    run_philosophers("limit")
