
import sys


def detect_deadlock(filename):
    owners = {}
    graph = {}

    with open(filename, encoding="utf-8") as file:
        events = [line.split() for line in file if line.strip()]

    for event in events:
        if len(event) != 3:
            print("Пропущена некорректная строка:", event)
            continue

        action, thread, resource = event

        graph.setdefault(thread, set())

        if action == "acquire":
            owners[resource] = thread

        elif action == "release":
            if owners.get(resource) == thread:
                del owners[resource]

            # После освобождения ресурс больше не создаёт ожидание.
            for waiting_thread in graph:
                graph[waiting_thread] = {
                    owner for owner in graph[waiting_thread]
                    if owner != thread
                }

        elif action == "wait":
            owner = owners.get(resource)
            if owner is not None and owner != thread:
                graph[thread].add(owner)

        else:
            print("Неизвестное событие:", action)

    # DFS ищет цикл в графе ожидания.
    visited = set()
    active = set()
    path = []
    cycle = None

    def dfs(node):
        nonlocal cycle

        visited.add(node)
        active.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in active:
                start = path.index(neighbor)
                cycle = path[start:] + [neighbor]
                return True

        path.pop()
        active.remove(node)
        return False

    for node in graph:
        if node not in visited and dfs(node):
            break

    print("Граф ожидания:")
    for thread, neighbors in sorted(graph.items()):
        print(f"{thread} -> {', '.join(sorted(neighbors)) or 'нет'}")

    if cycle:
        print("ОБНАРУЖЕН DEADLOCK!")
        print("Цикл:", " -> ".join(cycle))
        print("Участники:", ", ".join(cycle[:-1]))
    else:
        print("Цикл не обнаружен.")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "events.txt"
    detect_deadlock(filename)
