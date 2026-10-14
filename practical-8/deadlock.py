
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()
ready = threading.Barrier(2)


def worker_a():
    with lock_a:
        print("T1: захватил A", flush=True)
        ready.wait()
        print("T1: ждёт B", flush=True)
        with lock_b:
            print("T1: захватил B", flush=True)


def worker_b():
    with lock_b:
        print("T2: захватил B", flush=True)
        ready.wait()
        print("T2: ждёт A", flush=True)
        with lock_a:
            print("T2: захватил A", flush=True)


t1 = threading.Thread(target=worker_a)
t2 = threading.Thread(target=worker_b)

t1.start()
t2.start()

t1.join()
t2.join()

print("Работа завершена")
