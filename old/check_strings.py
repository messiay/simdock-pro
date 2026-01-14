import sys
import re

def strings(filename, min=4):
    with open(filename, "rb") as f:
        result = ""
        for c in f.read():
            c = chr(c)
            if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_/. ":
                result += c
            else:
                if len(result) >= min:
                    yield result
                result = ""

if __name__ == "__main__":
    for s in strings(sys.argv[1]):
        if "dock" in s.lower() or "help" in s.lower() or "batch" in s.lower() or "gui" in s.lower():
            print(s)
