
import socket
import sys

SOCKET_PATH = "/tmp/ipc7_server.sock"


def main():
    expression = " ".join(sys.argv[1:])

    if not expression:
        expression = input("Введите выражение: ")

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(SOCKET_PATH)
            client.sendall((expression + "\n").encode())

            with client.makefile("rb") as response:
                print("Ответ сервера:", response.readline().decode().strip())

    except FileNotFoundError:
        print("Сервер не запущен. Запусти socket_server.py в другом терминале.")
    except ConnectionRefusedError:
        print("Сервер не принимает подключения. Перезапусти его.")


if __name__ == "__main__":
    main()
