#!/usr/bin/env python3

import os
import time


pid = os.fork()

if pid == 0:
    print(f"Child process: PID={os.getpid()}")
    os._exit(0)

print(f"Parent process: PID={os.getpid()}")
print(f"Child process: PID={pid}")
print("Child has exited, but parent has not called wait().")
print("The child is now a zombie.")
print("Run ps in another terminal to see it.")

time.sleep(20)

os.waitpid(pid, 0)

print("Zombie was collected.")
