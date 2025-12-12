#!/usr/bin/env python3
import subprocess
import sys
import os


def run_command(cmd, input_data=None):
    result = subprocess.run(cmd, input=input_data, text=True, capture_output=True)
    return result.stdout, result.stderr


def test_nl():
    input_data = "hello\nworld\npython"
    stdout, stderr = run_command([sys.executable, "nl.py"], input_data=input_data)
    assert stdout == "1\thello\n2\tworld\n3\tpython"
    assert stderr == ""


def test_nl_file():
    with open("test_nl.txt", "w") as f:
        f.write("line1\nline2\n")
    stdout, stderr = run_command([sys.executable, "nl.py", "test_nl.txt"])
    assert stdout == "1\tline1\n2\tline2\n"
    os.remove("test_nl.txt")


def test_tail():
    input_data = "\n".join(str(i) for i in range(20))
    stdout, stderr = run_command([sys.executable, "tail.py"], input_data=input_data)
    expected = "\n".join(str(i) for i in range(3, 20))
    assert stdout == expected
    assert stderr == ""


def test_tail_file():
    with open("test_tail.txt", "w") as f:
        f.write("\n".join(str(i) for i in range(15)))
    stdout, stderr = run_command([sys.executable, "tail.py", "test_tail.txt"])
    expected_file = "\n".join(str(i) for i in range(5, 15))
    assert stdout == expected_file
    assert stderr == ""
    os.remove("test_tail.txt")


def test_wc():
    input_data = "hello world\npython\n"
    stdout, stderr = run_command([sys.executable, "wc.py"], input_data=input_data)
    assert stdout.strip() == "2 3 19"
    assert stderr == ""


def test_wc_file():
    with open("test_wc.txt", "w") as f:
        f.write("a b c\n1 2 3\n")
    stdout, stderr = run_command([sys.executable, "wc.py", "test_wc.txt"])
    assert stdout.strip() == "2 6 12 test_wc.txt"
    assert stderr == ""
    os.remove("test_wc.txt")


if __name__ == "__main__":
    test_nl()
    test_nl_file()
    test_tail()
    test_tail_file()
    test_wc()
    test_wc_file()
    print("All integration tests passed!")
