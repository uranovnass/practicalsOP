import os
import sys

if len(sys.argv) != 2:
    print("Usage: python3 hello.py <file>")
    sys.exit(1)

file_path = sys.argv[1]

with open(file_path, "rb") as file:
    data = file.read()

print(f"File size: {len(data)} bytes")
