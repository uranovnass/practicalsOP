with open("numbers.txt", "w") as f:
    for i in range(1, 10_000_001):
        f.write(f"{i}\n")

print("numbers.txt создан")
