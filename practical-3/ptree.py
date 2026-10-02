#!/usr/bin/env python3

import os


def read_process(pid):
    try:
        with open(f"/proc/{pid}/status", "r") as file:
            data = file.readlines()
    except (FileNotFoundError, PermissionError):
        return None

    info = {}

    for line in data:
        if line.startswith("Name:"):
            info["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("State:"):
            info["state"] = line.split(":", 1)[1].strip()
        elif line.startswith("PPid:"):
            info["ppid"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("Uid:"):
            info["uid"] = int(line.split(":", 1)[1].split()[0])
        elif line.startswith("VmRSS:"):
            info["rss"] = line.split(":", 1)[1].strip()

    if "uid" not in info or info["uid"] != os.getuid():
        return None

    info["pid"] = pid
    return info


def get_processes():
    processes = {}

    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue

        pid = int(entry)
        process = read_process(pid)

        if process is not None:
            processes[pid] = process

    return processes


def build_tree(processes):
    children = {}

    for pid, process in processes.items():
        ppid = process["ppid"]

        if ppid not in children:
            children[ppid] = []

        children[ppid].append(pid)

    for ppid in children:
        children[ppid].sort()

    return children


def print_tree(pid, children, processes, level=0):
    process = processes[pid]

    print(
        "  " * level
        + f"{process['pid']} "
        + f"[{process['state']}] "
        + f"RSS={process.get('rss', '0 kB')} "
        + f"{process.get('name', '')}"
    )

    for child in children.get(pid, []):
        print_tree(child, children, processes, level + 1)


def main():
    processes = get_processes()
    children = build_tree(processes)

    roots = []

    for pid, process in processes.items():
        if process["ppid"] not in processes:
            roots.append(pid)

    roots.sort()

    print("Process tree for current user")
    print("=" * 50)

    for root in roots:
        print_tree(root, children, processes)


if __name__ == "__main__":
    main()
