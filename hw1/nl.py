#!/usr/bin/env python3
import sys


def number_lines(file):
    for i, line in enumerate(file, start=1):
        print(f"{i}\t{line}", end='')


def main():
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    number_lines(f)
            except FileNotFoundError:
                print(f"nl: {filename}: No such file or directory", file=sys.stderr)
    else:
        number_lines(sys.stdin)


if __name__ == "__main__":
    main()
