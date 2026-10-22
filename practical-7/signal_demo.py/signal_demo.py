import os
import signal
import time

def handler(signum, frame):
    name = signal.Signals(signum).num
    print(f"Получен {name}, но я не завершаюсь")

signal.signal(signal.SIGINT, handler)
print("Мой PID:", os.getpid())

while True:
    time.sleep(1)
