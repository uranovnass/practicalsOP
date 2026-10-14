
import os
import uuid

REQUEST_FIFO = "/tmp/ipc7_requests.fifo"


def main():
    if not os.path.exists(REQUEST_FIFO):
        print("Сначала запусти FIFO-сервер в другом терминале.")
        return

    response_fifo = f"/tmp/ipc7_response_{os.getpid()}_{uuid.uuid4().hex}"

    os.mkfifo(response_fifo)

    try:
        expression = input("Введите выражение (например, 12 * (3 + 2)): ")

        with open(REQUEST_FIFO, "w") as channel:
            channel.write(f"{response_fifo}|{expression}\n")

        with open(response_fifo, "r") as response:
            print("Ответ сервера:", response.readline().strip())

    finally:
        if os.path.exists(response_fifo):
            os.unlink(response_fifo)


if __name__ == "__main__":
    main()
