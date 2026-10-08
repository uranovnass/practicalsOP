import time
import statistics
import urllib.request
import os

from threading import Thread
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ============================================================
# НАСТРОЙКИ
# ============================================================

NUM_THREADS = 4
REPEATS = 3
NUMBERS_FILE = "numbers.txt"
NETWORK_DIR = "network"
PORT = 8000


# ============================================================
# РАБОТА С ЧИСЛАМИ
# ============================================================

def load_numbers():
    """Загрузка чисел из numbers.txt."""
    with open(NUMBERS_FILE, "r") as file:
        return [int(x) for x in file.read().split()]


def sequential_sum(numbers):
    """Последовательная сумма чисел."""
    total = 0

    for number in numbers:
        total += number

    return total


# ============================================================
# 4 ПОТОКА
# ============================================================

def thread_sum(numbers):
    """Сумма чисел с использованием 4 потоков."""

    results = [0] * NUM_THREADS

    def worker(index, start, end):
        total = 0

        for i in range(start, end):
            total += numbers[i]

        results[index] = total

    threads = []

    part = len(numbers) // NUM_THREADS

    for i in range(NUM_THREADS):

        start = i * part

        if i == NUM_THREADS - 1:
            end = len(numbers)
        else:
            end = (i + 1) * part

        thread = Thread(
            target=worker,
            args=(i, start, end)
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)


# ============================================================
# 4 ПРОЦЕССА
# ============================================================

def process_sum_part(args):
    """Сумма части списка в отдельном процессе."""

    numbers, start, end = args

    total = 0

    for i in range(start, end):
        total += numbers[i]

    return total


def process_sum(numbers):
    """Сумма чисел с использованием 4 процессов."""

    part = len(numbers) // NUM_THREADS

    tasks = []

    for i in range(NUM_THREADS):

        start = i * part

        if i == NUM_THREADS - 1:
            end = len(numbers)
        else:
            end = (i + 1) * part

        tasks.append(
            (numbers, start, end)
        )

    with ProcessPoolExecutor(
        max_workers=NUM_THREADS
    ) as executor:

        results = executor.map(
            process_sum_part,
            tasks
        )

        return sum(results)


# ============================================================
# ИЗМЕРЕНИЕ ВРЕМЕНИ
# ============================================================

def measure(function, *args):
    """Запуск функции 3 раза и расчёт медианы."""

    times = []

    result = None

    for i in range(REPEATS):

        start = time.perf_counter()

        result = function(*args)

        end = time.perf_counter()

        elapsed = end - start

        times.append(elapsed)

        print(
            f"  Запуск {i + 1}: {elapsed:.4f} сек."
        )

    median_time = statistics.median(times)

    print(
        f"  Медиана: {median_time:.4f} сек."
    )

    return result, times, median_time


# ============================================================
# СЕТЕВАЯ ЗАДАЧА
# ============================================================

def download_file(filename):
    """Загрузка одного файла с локального сервера."""

    url = f"http://127.0.0.1:{PORT}/{filename}"

    with urllib.request.urlopen(url) as response:
        data = response.read()

    return len(data)


def network_sequential(files):
    """Последовательная загрузка файлов."""

    results = []

    for filename in files:
        results.append(
            download_file(filename)
        )

    return sum(results)


def network_threads(files):
    """Загрузка файлов с помощью 4 потоков."""

    with ThreadPoolExecutor(
        max_workers=NUM_THREADS
    ) as executor:

        results = executor.map(
            download_file,
            files
        )

        return sum(results)


def network_processes(files):
    """Загрузка файлов с помощью 4 процессов."""

    with ProcessPoolExecutor(
        max_workers=NUM_THREADS
    ) as executor:

        results = executor.map(
            download_file,
            files
        )

        return sum(results)


# ============================================================
# ПРОВЕРКА ОБЩЕЙ ПАМЯТИ
# ============================================================

shared_list = ["parent"]


def thread_change():
    """Поток изменяет общий список."""

    shared_list.append("thread")


def process_change():
    """Процесс изменяет свою копию списка."""

    shared_list.append("process")


def memory_test():

    global shared_list

    shared_list = ["parent"]

    print("\n" + "=" * 60)
    print("ПРОВЕРКА ОБЩЕЙ ПАМЯТИ")
    print("=" * 60)

    # Поток

    thread = Thread(
        target=thread_change
    )

    thread.start()
    thread.join()

    print(
        "После потока:",
        shared_list
    )

    # Процесс

    process = Process(
        target=process_change
    )

    process.start()
    process.join()

    print(
        "После процесса:",
        shared_list
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ПРАКТИЧЕСКАЯ РАБОТА №4 — ПОТОКИ")
    print("=" * 60)

    # --------------------------------------------------------
    # ИНФОРМАЦИЯ О СИСТЕМЕ
    # --------------------------------------------------------

    print(
        f"\nКоличество ядер: {os.cpu_count()}"
    )

    # --------------------------------------------------------
    # ЗАГРУЗКА ЧИСЕЛ
    # --------------------------------------------------------

    print("\nЗагрузка numbers.txt...")

    numbers = load_numbers()

    print(
        f"Количество чисел: {len(numbers)}"
    )

    correct_sum = sum(numbers)

    print(
        f"Правильная сумма: {correct_sum}"
    )

    # ========================================================
    # CPU: ПОСЛЕДОВАТЕЛЬНО
    # ========================================================

    print("\n" + "=" * 60)
    print("1. СУММА ЧИСЕЛ — ПОСЛЕДОВАТЕЛЬНО")
    print("=" * 60)

    result_seq, times_seq, median_seq = measure(
        sequential_sum,
        numbers
    )

    print(
        f"Результат: {result_seq}"
    )

    # ========================================================
    # CPU: 4 ПОТОКА
    # ========================================================

    print("\n" + "=" * 60)
    print("2. СУММА ЧИСЕЛ — 4 ПОТОКА")
    print("=" * 60)

    result_thread, times_thread, median_thread = measure(
        thread_sum,
        numbers
    )

    print(
        f"Результат: {result_thread}"
    )

    # ========================================================
    # CPU: 4 ПРОЦЕССА
    # ========================================================

    print("\n" + "=" * 60)
    print("3. СУММА ЧИСЕЛ — 4 ПРОЦЕССА")
    print("=" * 60)

    result_process, times_process, median_process = measure(
        process_sum,
        numbers
    )

    print(
        f"Результат: {result_process}"
    )

    # ========================================================
    # ТАБЛИЦА CPU
    # ========================================================

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ CPU-ЗАДАЧИ")
    print("=" * 60)

    print(
        f"{'Метод':<25}"
        f"{'Запуск 1':>12}"
        f"{'Запуск 2':>12}"
        f"{'Запуск 3':>12}"
        f"{'Медиана':>12}"
    )

    print(
        f"{'Последовательно':<25}"
        f"{times_seq[0]:>12.4f}"
        f"{times_seq[1]:>12.4f}"
        f"{times_seq[2]:>12.4f}"
        f"{median_seq:>12.4f}"
    )

    print(
        f"{'4 потока':<25}"
        f"{times_thread[0]:>12.4f}"
        f"{times_thread[1]:>12.4f}"
        f"{times_thread[2]:>12.4f}"
        f"{median_thread:>12.4f}"
    )

    print(
        f"{'4 процесса':<25}"
        f"{times_process[0]:>12.4f}"
        f"{times_process[1]:>12.4f}"
        f"{times_process[2]:>12.4f}"
        f"{median_process:>12.4f}"
    )

    # ========================================================
    # СЕТЕВАЯ ЗАДАЧА
    # ========================================================

    files = sorted(
        os.listdir(NETWORK_DIR)
    )

    print("\n" + "=" * 60)
    print("СЕТЕВАЯ ЗАДАЧА")
    print("=" * 60)

    print(
        f"Количество файлов: {len(files)}"
    )

    # --------------------------------------------------------
    # Сеть — последовательно
    # --------------------------------------------------------

    print("\n--- Последовательно ---")

    result_net_seq, net_seq_times, net_seq_median = measure(
        network_sequential,
        files
    )

    # --------------------------------------------------------
    # Сеть — 4 потока
    # --------------------------------------------------------

    print("\n--- 4 потока ---")

    result_net_thread, net_thread_times, net_thread_median = measure(
        network_threads,
        files
    )

    # --------------------------------------------------------
    # Сеть — 4 процесса
    # --------------------------------------------------------

    print("\n--- 4 процесса ---")

    result_net_process, net_process_times, net_process_median = measure(
        network_processes,
        files
    )

    # ========================================================
    # ТАБЛИЦА СЕТИ
    # ========================================================

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ СЕТЕВОЙ ЗАДАЧИ")
    print("=" * 60)

    print(
        f"{'Метод':<25}"
        f"{'Запуск 1':>12}"
        f"{'Запуск 2':>12}"
        f"{'Запуск 3':>12}"
        f"{'Медиана':>12}"
    )

    print(
        f"{'Последовательно':<25}"
        f"{net_seq_times[0]:>12.4f}"
        f"{net_seq_times[1]:>12.4f}"
        f"{net_seq_times[2]:>12.4f}"
        f"{net_seq_median:>12.4f}"
    )

    print(
        f"{'4 потока':<25}"
        f"{net_thread_times[0]:>12.4f}"
        f"{net_thread_times[1]:>12.4f}"
        f"{net_thread_times[2]:>12.4f}"
        f"{net_thread_median:>12.4f}"
    )

    print(
        f"{'4 процесса':<25}"
        f"{net_process_times[0]:>12.4f}"
        f"{net_process_times[1]:>12.4f}"
        f"{net_process_times[2]:>12.4f}"
        f"{net_process_median:>12.4f}"
    )

    # ========================================================
    # ОБЩАЯ ПАМЯТЬ
    # ========================================================

    memory_test()

    # ========================================================
    # ПРОВЕРКА РЕЗУЛЬТАТОВ
    # ========================================================

    print("\n" + "=" * 60)
    print("ПРОВЕРКА РЕЗУЛЬТАТОВ")
    print("=" * 60)

    if result_seq == correct_sum:
        print("✓ Последовательный результат правильный")
    else:
        print("✗ Ошибка в последовательном результате")

    if result_thread == correct_sum:
        print("✓ Результат потоков правильный")
    else:
        print("✗ Ошибка в результате потоков")

    if result_process == correct_sum:
        print("✓ Результат процессов правильный")
    else:
        print("✗ Ошибка в результате процессов")

    print("\nРабота завершена.")
