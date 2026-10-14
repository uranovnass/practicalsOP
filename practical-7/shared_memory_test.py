import multiprocessing as mp
from multiprocessing import shared_memory
from array import array
import time

N = 10_000_000


def shared_worker(name, n, connection):
    shm = shared_memory.SharedMemory(name=name)
    numbers = None

    try:
        numbers = shm.buf.cast("q")
        result = sum(numbers)
        connection.send(result)
    finally:
        if numbers is not None:
            numbers.release()
        shm.close()
        connection.close()


def pipe_worker(connection):
    try:
        numbers = connection.recv()
        connection.send(sum(numbers))
    finally:
        connection.close()


def test_shared_memory():
    shm = shared_memory.SharedMemory(create=True, size=N * 8)
    parent, child = mp.Pipe()
    process = None

    try:
        numbers = shm.buf.cast("q")
        start = time.perf_counter()

        try:
            for i in range(N):
                numbers[i] = i + 1
        finally:
            numbers.release()

        process = mp.Process(
            target=shared_worker,
            args=(shm.name, N, child),
        )
        process.start()
        child.close()

        result = parent.recv()
        process.join()

        elapsed = time.perf_counter() - start

        if process.exitcode != 0:
            raise RuntimeError("Процесс Shared Memory завершился с ошибкой")

        print("\n=== Shared Memory ===")
        print(f"Количество чисел: {N:,}")
        print(f"Размер данных: {N * 8 / 1024 / 1024:.2f} MiB")
        print(f"Сумма: {result}")
        print(f"Общее время: {elapsed:.4f} секунд")

    finally:
        parent.close()
        child.close()

        if process is not None and process.is_alive():
            process.terminate()
            process.join()

        shm.close()
        shm.unlink()


def test_pipe():
    parent, child = mp.Pipe()
    numbers = array("q", range(1, N + 1))
    process = None

    try:
        process = mp.Process(target=pipe_worker, args=(child,))
        process.start()
        child.close()

        start = time.perf_counter()
        parent.send(numbers)
        result = parent.recv()
        process.join()

        elapsed = time.perf_counter() - start

        if process.exitcode != 0:
            raise RuntimeError("Процесс Pipe завершился с ошибкой")

        print("\n=== Pipe ===")
        print(f"Количество чисел: {N:,}")
        print(
            f"Размер данных: "
            f"{len(numbers) * numbers.itemsize / 1024 / 1024:.2f} MiB"
        )
        print(f"Сумма: {result}")
        print(f"Время передачи и обработки: {elapsed:.4f} секунд")

    finally:
        parent.close()
        child.close()

        if process is not None and process.is_alive():
            process.terminate()
            process.join()


if __name__ == "__main__":
    mp.freeze_support()
    test_shared_memory()
    test_pipe()
