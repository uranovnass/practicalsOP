
import threading


class DeadlockDetected(RuntimeError):
    pass


class LockTracker:
    def __init__(self):
        self.guard = threading.Lock()
        self.owners = {}
        self.waiting = {}

    def find_path(self, start, target):
        stack = [(start, [start])]
        visited = set()

        while stack:
            node, path = stack.pop()

            if node == target:
                return path

            if node in visited:
                continue

            visited.add(node)

            for neighbor in self.waiting.get(node, set()):
                stack.append((neighbor, path + [neighbor]))

        return None


class TrackedLock:
    def __init__(self, tracker, name):
        self.tracker = tracker
        self.name = name
        self.lock = threading.Lock()

    def acquire(self):
        tid = threading.get_ident()
        tracker = self.tracker

        with tracker.guard:
            if tracker.owners.get(self.name) == tid:
                raise RuntimeError("Повторный захват обычного Lock")

            owner = tracker.owners.get(self.name)

            if owner is not None:
                tracker.waiting.setdefault(tid, set()).add(owner)

                path = tracker.find_path(owner, tid)
                if path:
                    tracker.waiting[tid].discard(owner)
                    raise DeadlockDetected(
                        f"Deadlock: поток {tid} -> "
                        + " -> ".join(map(str, path))
                    )

        try:
            self.lock.acquire()
        except BaseException:
            with tracker.guard:
                tracker.waiting.get(tid, set()).discard(owner)
            raise

        with tracker.guard:
            tracker.waiting.get(tid, set()).discard(owner)
            tracker.owners[self.name] = tid

    def release(self):
        tid = threading.get_ident()
        tracker = self.tracker

        with tracker.guard:
            if tracker.owners.get(self.name) != tid:
                raise RuntimeError("Освобождать Lock может только владелец")

            del tracker.owners[self.name]

        self.lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return False
