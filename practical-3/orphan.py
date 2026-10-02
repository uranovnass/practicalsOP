#!/usr/bin/env python3

import os
import time


pid = os.fork()

if pid == 0:
    old_ppid = os.getppid()

    print(f"Child PID={os.getpid()}")
    print(f"Initial parent PID={old_ppid}")

    time.sleep(5)

    new_ppid = os.getppid()

    print(f"Parent PID after parent exit={new_ppid}")

    time.sleep(5)

else:
    print(f"Parent PID={os.getpid()}")
    print(f"Child PID={pid}")
    print("Parent exits immediately.")
    os._exit(0)
