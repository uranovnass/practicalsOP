#!/usr/bin/env python3

import os
import time


def get_rss():
    with open("/proc/self/status", "r") as file:
        for line in file:
            if line.startswith("VmRSS:"):
                return line.strip()


data = [0] * 5_000_000

print(f"Parent PID: {os.getpid()}")
print(f"Parent RSS before fork: {get_rss()}")

pid = os.fork()

if pid == 0:
    print(f"Child PID: {os.getpid()}")
    print(f"Child RSS before modification: {get_rss()}")

    for i in range(len(data)):
        data[i] = 1

    print(f"Child RSS after modification: {get_rss()}")

    os._exit(0)

else:
    os.waitpid(pid, 0)
    print(f"Parent RSS after child modification: {get_rss()}")
