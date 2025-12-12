#!/usr/bin/env python3
import sys


def count_file(file):
    lines = 0
    words = 0
    bytes_count = 0
    for line in file:
        lines += 1
        words += len(line.split())
        bytes_count += len(line.encode('utf-8'))
    return lines, words, bytes_count


def main():
    files = sys.argv[1:]
    total = [0, 0, 0]
    results = []

    if not files:
        l, w, b = count_file(sys.stdin)
        print(f"{l} {w} {b}")
    else:
        for filename in files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    l, w, b = count_file(f)
                    results.append((l, w, b, filename))
                    total[0] += l
                    total[1] += w
                    total[2] += b
            except FileNotFoundError:
                print(f"wc: {filename}: No such file or directory", file=sys.stderr)
        for l, w, b, name in results:
            print(f"{l} {w} {b} {name}")
        if len(files) > 1:
            print(f"{total[0]} {total[1]} {total[2]} total")


if __name__ == "__main__":
    main()
