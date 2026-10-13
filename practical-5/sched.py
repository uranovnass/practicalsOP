
import argparse
import csv
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_processes(filename):
    processes = []
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 4:
                raise ValueError(
                    f"Неверная строка: {line}. "
                    "Нужно: PID arrival burst priority"
                )

            pid, arrival, burst, priority = parts
            arrival, burst, priority = (
                int(arrival), int(burst), int(priority)
            )

            if arrival < 0 or burst <= 0:
                raise ValueError(
                    f"{pid}: arrival должен быть >= 0, "
                    "а burst должен быть > 0"
                )

            processes.append({
                "pid": pid,
                "arrival": arrival,
                "burst": burst,
                "priority": priority,
            })

    if not processes:
        raise ValueError("Входной файл не содержит процессов.")

    if len({p["pid"] for p in processes}) != len(processes):
        raise ValueError("PID процессов должны быть уникальными.")

    return processes


def simulate(processes, algorithm, **params):
    """Возвращает список интервалов (start, end, PID)."""
    if algorithm not in {"fcfs", "sjf", "srtf", "priority", "rr"}:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")

    quantum = params.get("quantum", 3)
    aging_interval = params.get("aging_interval", 5)

    if algorithm == "rr" and quantum < 1:
        raise ValueError("Квант должен быть не меньше 1.")

    if aging_interval < 1:
        raise ValueError("Интервал aging должен быть не меньше 1.")

    jobs = []
    for index, p in enumerate(processes):
        jobs.append({
            **p,
            "index": index,
            "remaining": p["burst"],
            "first_start": None,
            "finish": None,
            "executed": 0,
        })

    time = 0
    completed = 0
    running = None
    quantum_used = 0
    ready_queue = deque()
    intervals = []
    n = len(jobs)

    while completed < n:
        # Сначала добавляем процессы, прибывшие в этот момент.
        for job in jobs:
            if job["arrival"] == time:
                if algorithm == "rr":
                    ready_queue.append(job)

        # RR: прибывшие процессы попадают в очередь
        # раньше процесса, у которого закончился квант.
        if (algorithm == "rr" and running is not None
                and quantum_used == quantum
                and running["remaining"] > 0):
            ready_queue.append(running)
            running = None
            quantum_used = 0

        # Выбор процесса для выполнения.
        if algorithm == "rr":
            if running is None and ready_queue:
                running = ready_queue.popleft()
                quantum_used = 0

        elif algorithm in {"fcfs", "sjf"}:
            if running is None:
                ready = [
                    j for j in jobs
                    if j["arrival"] <= time and j["remaining"] > 0
                ]
                if ready:
                    if algorithm == "fcfs":
                        running = min(
                            ready, key=lambda j: (j["arrival"], j["index"])
                        )
                    else:
                        running = min(
                            ready,
                            key=lambda j: (
                                j["burst"], j["arrival"], j["index"]
                            ),
                        )

        elif algorithm == "srtf":
            ready = [
                j for j in jobs
                if j["arrival"] <= time and j["remaining"] > 0
            ]
            if ready:
                running = min(
                    ready,
                    key=lambda j: (
                        j["remaining"], j["arrival"], j["index"]
                    ),
                )
            else:
                running = None

        elif algorithm == "priority":
            ready = [
                j for j in jobs
                if j["arrival"] <= time and j["remaining"] > 0
            ]

            if ready:
                def priority_key(j):
                    waiting = time - j["arrival"] - j["executed"]
                    effective = j["priority"]
                    if params.get("aging", False):
                        effective -= waiting // aging_interval
                    return effective, j["arrival"], j["index"]

                running = min(ready, key=priority_key)
            else:
                running = None

        # Если CPU свободен, пропускаем время до следующего события.
        if running is None:
            future = [
                j["arrival"] for j in jobs if j["arrival"] > time
            ]
            if not future:
                break
            time = min(future)
            continue

        if running["first_start"] is None:
            running["first_start"] = time

        # Выполняем процесс ровно один такт.
        if intervals and intervals[-1][2] == running["pid"] \
                and intervals[-1][1] == time:
            intervals[-1] = (
                intervals[-1][0], time + 1, running["pid"]
            )
        else:
            intervals.append((time, time + 1, running["pid"]))

        running["remaining"] -= 1
        running["executed"] += 1
        time += 1

        if algorithm == "rr":
            quantum_used += 1

        if running["remaining"] == 0:
            running["finish"] = time
            completed += 1
            running = None
            quantum_used = 0

    return intervals


def calculate_metrics(processes, intervals):
    by_pid = {p["pid"]: p for p in processes}
    stats = {}

    for p in processes:
        stats[p["pid"]] = {
            "arrival": p["arrival"],
            "burst": p["burst"],
            "first_start": None,
            "finish": None,
        }

    for start, end, pid in intervals:
        row = stats[pid]
        if row["first_start"] is None:
            row["first_start"] = start
        row["finish"] = end

    waiting = []
    turnaround = []
    response = []

    for pid, row in stats.items():
        if row["finish"] is None:
            raise ValueError(f"Процесс {pid} не завершился.")

        tat = row["finish"] - row["arrival"]
        waiting_time = tat - row["burst"]
        response_time = row["first_start"] - row["arrival"]

        waiting.append(waiting_time)
        turnaround.append(tat)
        response.append(response_time)

    total_burst = sum(p["burst"] for p in processes)
    end_time = max(end for _, end, _ in intervals)
    start_time = min(
        [0] + [p["arrival"] for p in processes]
    )
    elapsed = end_time - start_time
    utilization = 100 * total_burst / elapsed if elapsed else 0

    # Переключение между разными процессами; первый запуск
    # не считается переключением.
    switches = sum(
        1 for i in range(1, len(intervals))
        if intervals[i - 1][2] != intervals[i][2]
    )

    return {
        "waiting": sum(waiting) / len(waiting),
        "turnaround": sum(turnaround) / len(turnaround),
        "response": sum(response) / len(response),
        "utilization": utilization,
        "switches": switches,
        "details": stats,
    }


def print_results(algorithm, metrics):
    print("\nРЕЗУЛЬТАТЫ")
    print("-" * 45)
    print(f"Алгоритм: {algorithm.upper()}")
    print(f"Среднее ожидание:   {metrics['waiting']:.2f}")
    print(f"Средний оборот:     {metrics['turnaround']:.2f}")
    print(f"Средний отклик:     {metrics['response']:.2f}")
    print(f"Загрузка CPU:       {metrics['utilization']:.2f}%")
    print(f"Переключения:       {metrics['switches']}")

    print("\nPID | Ожидание | Оборот | Отклик")
    for pid, row in metrics["details"].items():
        tat = row["finish"] - row["arrival"]
        wait = tat - row["burst"]
        resp = row["first_start"] - row["arrival"]
        print(f"{pid:3} | {wait:8} | {tat:6} | {resp:6}")


def print_gantt(intervals):
    print("\nДиаграмма выполнения (интервалы):")
    for start, end, pid in intervals:
        print(f"[{start:>3}, {end:>3}) {pid}")


def save_metrics_csv(filename, rows):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "algorithm", "waiting", "turnaround",
                "response", "utilization", "switches"
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def plot_rr(processes, output_dir):
    quanta = list(range(1, 11))
    avg_waiting = []
    switches = []

    for q in quanta:
        intervals = simulate(processes, "rr", quantum=q)
        metrics = calculate_metrics(processes, intervals)
        avg_waiting.append(metrics["waiting"])
        switches.append(metrics["switches"])

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(quanta, avg_waiting, marker="o", label="Среднее ожидание")
    ax1.set_xlabel("Квант RR")
    ax1.set_ylabel("Среднее ожидание")
    ax1.set_xticks(quanta)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(
        quanta, switches, marker="s",
        linestyle="--", label="Переключения"
    )
    ax2.set_ylabel("Число переключений")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "rr_quantum.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)

    print(f"График сохранён: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Симулятор планирования CPU"
    )
    parser.add_argument(
        "--algo",
        choices=["fcfs", "sjf", "srtf", "priority", "rr"],
        default="fcfs",
    )
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("--aging", action="store_true")
    parser.add_argument("--aging-interval", type=int, default=5)
    parser.add_argument("--plot-rr", action="store_true")
    parser.add_argument("file", help="Входной файл процессов")
    args = parser.parse_args()

    processes = load_processes(args.file)
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    if args.plot_rr:
        plot_rr(processes, output_dir)
        return

    intervals = simulate(
        processes,
        args.algo,
        quantum=args.quantum,
        aging=args.aging,
        aging_interval=args.aging_interval,
    )
    metrics = calculate_metrics(processes, intervals)
    print_results(args.algo, metrics)
    print_gantt(intervals)

    row = {
        "algorithm": args.algo,
        "waiting": round(metrics["waiting"], 4),
        "turnaround": round(metrics["turnaround"], 4),
        "response": round(metrics["response"], 4),
        "utilization": round(metrics["utilization"], 4),
        "switches": metrics["switches"],
    }
    csv_path = output_dir / "metrics.csv"
    exists = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if not exists:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    main()
