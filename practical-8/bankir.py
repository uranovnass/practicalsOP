AVAILABLE = [3, 3, 2]
ALLOCATION = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
MAX = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]

def is_safe(available, allocation, maximum):
    o, n = len(allocation), len(available)
    need = [[maximum[i][j] - allocation[i][j] for j in range(n)] for i in range(o)]
    work = available[:]
    finish = [False] * o
    order = []
    progress = True
    while progress:
        progress = False
        for i in range(o):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(n)):
                for j in range(n):
                    work[j] += allocation[i][j]
                finish[i] = True
                order.append(f"P{i}")
                progress = True
    return all(finish), order
is_safe_state, execution_order = is_safe(AVAILABLE, ALLOCATION, MAX)
print(f"Безопасное состояние: {is_safe_state}")
print(f"Порядок выполнения: {execution_order}")
