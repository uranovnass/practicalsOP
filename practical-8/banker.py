import json
import sys
from copy import deepcopy


def load_state(filename):
    with open(filename, encoding="utf-8") as file:
        data = json.load(file)

    available = data["Available"]
    allocation = data["Allocation"]
    maximum = data["Max"]

    if len(allocation) != len(maximum):
        raise ValueError("Allocation и Max должны иметь одинаковое число процессов")

    if any(len(row) != len(available) for row in allocation + maximum):
        raise ValueError("Количество типов ресурсов в строках не совпадает")

    if any(
        maximum[p][r] < allocation[p][r]
        for p in range(len(allocation))
        for r in range(len(available))
    ):
        raise ValueError("Max не может быть меньше Allocation")

    return available, allocation, maximum


def need_matrix(allocation, maximum):
    return [
        [maximum[p][r] - allocation[p][r]
         for r in range(len(maximum[p]))]
        for p in range(len(allocation))
    ]


def safety_check(available, allocation, maximum):
    need = need_matrix(allocation, maximum)
    work = available.copy()
    finished = [False] * len(allocation)
    sequence = []

    while True:
        found = False

        for p in range(len(allocation)):
            if not finished[p] and all(
                need[p][r] <= work[r] for r in range(len(work))
            ):
                # Процесс может завершиться и вернуть свои ресурсы.
                work = [
                    work[r] + allocation[p][r]
                    for r in range(len(work))
                ]
                finished[p] = True
                sequence.append(f"P{p}")
                found = True

        if not found:
            break

    return all(finished), sequence


def request_resources(pid, request, available, allocation, maximum):
    n = len(allocation)
    m = len(available)

    if not 0 <= pid < n:
        print("ОТКАЗ: такого процесса нет.")
        return available, allocation

    if len(request) != m or any(x < 0 for x in request):
        print("ОТКАЗ: неверный вектор запроса.")
        return available, allocation

    need = need_matrix(allocation, maximum)

    if any(request[r] > need[pid][r] for r in range(m)):
        print("ОТКАЗ: запрос превышает Need процесса.")
        return available, allocation

    if any(request[r] > available[r] for r in range(m)):
        print("ОТКАЗ: сейчас недостаточно доступных ресурсов.")
        return available, allocation

    # Сохраняем исходное состояние для отката.
    old_available = available.copy()
    old_allocation = deepcopy(allocation)

    for r in range(m):
        available[r] -= request[r]
        allocation[pid][r] += request[r]

    safe, sequence = safety_check(available, allocation, maximum)

    if safe:
        print("ЗАПРОС РАЗРЕШЁН.")
        print("Безопасная последовательность:", " -> ".join(sequence))
        return available, allocation

    # Откат, если после выдачи ресурсов состояние небезопасно.
    print("ЗАПРОС ОТКЛОНЁН: состояние небезопасно.")
    print("Выполняется откат.")
    return old_available, old_allocation


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "bank1.txt"

    try:
        available, allocation, maximum = load_state(filename)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Ошибка чтения данных:", error)
        return

    safe, sequence = safety_check(available, allocation, maximum)

    print(f"Файл: {filename}")
    print("Available:", available)
    print("Состояние:", "БЕЗОПАСНОЕ" if safe else "НЕБЕЗОПАСНОЕ")

    if safe:
        print("Безопасная последовательность:", " -> ".join(sequence))
    else:
        print("Безопасная последовательность не найдена.")

    print("\nВвод запросов: номер процесса, затем 3 числа.")
    print("Например: 1 1 0 2")
    print("Для выхода введи: exit")

    while True:
        try:
            line = input("request> ").strip()
        except EOFError:
            break

        if line.lower() == "exit":
            break
        if not line:
            continue

        try:
            values = list(map(int, line.split()))
            if len(values) != 4:
                print("Нужно 4 числа: pid и три ресурса.")
                continue

            pid, *request = values
            available, allocation = request_resources(
                pid, request, available, allocation, maximum
            )
            print("Текущее Available:", available)

        except ValueError:
            print("Ошибка ввода: используй целые числа.")


if __name__ == "__main__":
    main()
