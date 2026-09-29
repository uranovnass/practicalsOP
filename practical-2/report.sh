#!/bin/bash

usage() {
    echo "Usage: $0 <каталог> <ERROR|WARN> [--top N]" >&2
}

if [ $# -lt 2 ]; then
    usage
    exit 1
fi

DIR="$1"
LEVEL="$2"
TOP=""

if [ "$LEVEL" != "ERROR" ] && [ "$LEVEL" != "WARN" ]; then
    usage
    exit 1
fi

if [ ! -d "$DIR" ]; then
    echo "Ошибка: каталог '$DIR' не существует." >&2
    usage
    exit 1
fi

if [ $# -gt 2 ]; then
    if [ "$3" != "--top" ] || [ $# -ne 4 ]; then
        usage
        exit 1
    fi

    if ! [[ "$4" =~ ^[0-9]+$ ]]; then
        usage
        exit 1
    fi

    TOP="$4"
fi

echo "Модуль             Количество"
echo "----------------------------"

grep -h "level=$LEVEL" "$DIR"/*.log 2>/dev/null |
awk '
{
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^module=/) {
            split($i, a, "=")
            count[a[2]]++
        }
    }
}
END {
    for (module in count)
        print module, count[module]
}
' |
sort -k2,2nr |
if [ -n "$TOP" ]; then
    head -n "$TOP"
else
    cat
fi
