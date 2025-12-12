#!/usr/bin/env python3
import sys
from collections import deque


def tail(file, n):
    last_lines = deque(file, maxlen=n)
    for line in last_lines:
        print(line, end='')


def main():
    files = sys.argv[1:]
    if not files:
        tail(sys.stdin, 17)
    else:
        for idx, filename in enumerate(files):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    if len(files) > 1:
                        if idx > 0:
                            print()
                        print(f"==> {filename} <==")
                    tail(f, 10)
            except FileNotFoundError:
                print(f"tail: cannot open '{filename}' for reading: No such file or directory", file=sys.stderr)


if __name__ == "__main__":
    main()
