
import ast
import operator
import os
import signal

REQUEST_FIFO = "/tmp/ipc7_requests.fifo"

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATIONS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Слишком большая степень")

            result = OPERATIONS[type(node.op)](left, right)

            if abs(result) > 10**100:
                raise ValueError("Слишком большой результат")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATIONS:
            return OPERATIONS[type(node.op)](evaluate(node.operand))

        raise ValueError("Недопустимое выражение")

    return evaluate(tree)


def main():
    if os.path.exists(REQUEST_FIFO):
        if not os.path.exists(REQUEST_FIFO) or not __import__("stat").S_ISFIFO(
            os.stat(REQUEST_FIFO).st_mode
        ):
            raise RuntimeError("Путь занят не FIFO")

        os.unlink(REQUEST_FIFO)

    os.mkfifo(REQUEST_FIFO)
    print(f"Сервер FIFO запущен: {REQUEST_FIFO}", flush=True)
    print("Ожидаю запросы. Для остановки нажми Ctrl+C.", flush=True)

    try:
        while True:
            with open(REQUEST_FIFO, "r") as channel:
                request = channel.readline().strip()

            if not request:
                continue

            client_fifo, separator, expression = request.partition("|")

            if not separator or not client_fifo.startswith("/tmp/ipc7_response_"):
                print("Получен некорректный запрос", flush=True)
                continue

            try:
                answer = str(calculate(expression))
            except Exception as error:
                answer = f"Ошибка: {error}"

            try:
                with open(client_fifo, "w") as response:
                    response.write(answer + "\n")
                print(f"{expression} = {answer}", flush=True)
            except OSError as error:
                print(f"Не удалось отправить ответ: {error}", flush=True)

    except KeyboardInterrupt:
        print("\nСервер останавливается.", flush=True)
    finally:
        if os.path.exists(REQUEST_FIFO):
            os.unlink(REQUEST_FIFO)
        print("FIFO сервера удалён.", flush=True)


if __name__ == "__main__":
    main()
