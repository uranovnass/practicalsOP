#!/usr/bin/env python3

import os
import sys
import time


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 runner.py N command [args...]")
        sys.exit(1)

    n = int(sys.argv[1])
    command = sys.argv[2]
    args = sys.argv[2:]

    children = []

    for i in range(n):
        start_time = time.time()

        pid = os.fork()

        if pid == 0:
            os.execvp(command, args)

        children.append((pid, start_time))

    for pid, start_time in children:
        _, status = os.waitpid(pid, 0)

        end_time = time.time()
        elapsed = end_time - start_time

        if os.WIFEXITED(status):
            return_code = os.WEXITSTATUS(status)
            print(
                f"PID {pid}: return code = {return_code}, "
                f"time = {elapsed:.3f} sec"
            )
        else:
            print(
                f"PID {pid}: process did not exit normally, "
                f"time = {elapsed:.3f} sec"
            )


if __name__ == "__main__":
    main()
