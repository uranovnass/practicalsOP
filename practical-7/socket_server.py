
import ast
import operator
import os
import socket
import threading

SOCKET_PATH = "/tmp/ipc7_server.sock"

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Слишком большая степень")

            result = OPS[type(node.op)](left, right)

            if abs(result) > 10**100:
                raise ValueError("Слишком большой результат")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](evaluate(node.operand))

        raise ValueError("Недопустимое выражение")

    return evaluate(tree)


def handle_client(connection, address):
    with connection:
        file = connection.makefile("rwb")
        with file:
            expression = file.readline().decode().strip()

            try:
                answer = str(calculate(expression))
            except Exception as error:
                answer = f"Ошибка: {error}"

            file.write((answer + "\n").encode())
            file.flush()

            print(
                f"Клиент PID {threading.get_native_id()}: "
                f"{expression} = {answer}",
                flush=True,
            )


def main():
    if os.path.lexists(SOCKET_PATH):
        if not stat_is_socket(SOCKET_PATH):
            raise RuntimeError(f"Путь занят не сокетом: {SOCKET_PATH}")
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        server.bind(SOCKET_PATH)
        server.listen(10)
        print(f"Unix-сервер запущен: {SOCKET_PATH}", flush=True)
        print("Ожидаю клиентов. Для остановки нажми Ctrl+C.", flush=True)

        while True:
            connection, address = server.accept()
            threading.Thread(
                target=handle_client,
                args=(connection, address),
                daemon=True,
            ).start()

    except KeyboardInterrupt:
        print("\nСервер останавливается.", flush=True)
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        print("Сокет сервера удалён.", flush=True)


def stat_is_socket(path):
    import stat
    return stat.S_ISSOCK(os.stat(path).st_mode)


if __name__ == "__main__":
    main()
