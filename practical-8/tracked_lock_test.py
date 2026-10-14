
import threading
from tracked_lock import LockTracker, TrackedLock, DeadlockDetected


tracker = LockTracker()
lock_a = TrackedLock(tracker, "A")
lock_b = TrackedLock(tracker, "B")

ready = threading.Barrier(2)


def worker(first, second, name):
    first.acquire()
    print(name, "захватил первый Lock")

    ready.wait()

    try:
        second.acquire()
        print(name, "захватил второй Lock")
        second.release()
    except DeadlockDetected as error:
        print(name, "обнаружил:", error)
    finally:
        first.release()


t1 = threading.Thread(target=worker, args=(lock_a, lock_b, "T1"))
t2 = threading.Thread(target=worker, args=(lock_b, lock_a, "T2"))

t1.start()
t2.start()
t1.join()
t2.join()

print("Тест завершён без зависания.")
