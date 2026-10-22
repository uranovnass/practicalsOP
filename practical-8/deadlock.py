import faulthandler
import threading
import time

# Включаем faulthandler на случай непредвиденных зависаний
faulthandler.enable()
# Задаем тайм-аут в 5 секунд (в исправном коде он не должен сработать)
faulthandler.dump_traceback_later(5, exit=True)

lock_a = threading.Lock()
lock_b = threading.Lock()

def worker1():
    # Поток 1 берет сначала A, затем B
    with lock_a:
        print("T1 взял А, жду В")
        time.sleep(0.1)
        with lock_b:
            print("T1 взял А и В")

def worker2():
    # ИСПРАВЛЕНО: Поток 2 теперь тоже берет сначала A, затем B
    with lock_a:
        print("T2 взял A, жду B")
        time.sleep(0.1)
        with lock_b:
            print("T2 взял B и A")

# Создание и запуск потоков
t1 = threading.Thread(target=worker1, name="Thread-1")
t2 = threading.Thread(target=worker2, name="Thread-2")

t1.start()
t2.start()

# Ожидание завершения потоков
t1.join()
t2.join()

# Отмена отслеживания, так как всё прошло успешно, и вывод финального сообщения
faulthandler.cancel_dump_traceback_later()
print("Готово! Программа завершилась успешно.")
import faulthandler
import threading
import time

# Включаем faulthandler на случай непредвиденных зависаний
faulthandler.enable()
# Задаем тайм-аут в 5 секунд (в исправном коде он не должен сработать)
faulthandler.dump_traceback_later(5, exit=True)

lock_a = threading.Lock()
lock_b = threading.Lock()

def worker1():
    # Поток 1 берет сначала A, затем B
    with lock_a:
        print("T1 взял А, жду В")
        time.sleep(0.1)
        with lock_b:
            print("T1 взял А и В")

def worker2():
    # ИСПРАВЛЕНО: Поток 2 теперь тоже берет сначала A, затем B
    with lock_a:
        print("T2 взял A, жду B")
        time.sleep(0.1)
        with lock_b:
            print("T2 взял B и A")

# Создание и запуск потоков
t1 = threading.Thread(target=worker1, name="Thread-1")
t2 = threading.Thread(target=worker2, name="Thread-2")

t1.start()
t2.start()

# Ожидание завершения потоков
t1.join()
t2.join()

# Отмена отслеживания, так как всё прошло успешно, и вывод финального сообщения
faulthandler.cancel_dump_traceback_later()
print("Готово! Программа завершилась успешно.")

