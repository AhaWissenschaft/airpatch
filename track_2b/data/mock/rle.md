FILE: main.py
```python
import sys


def encode(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    return "".join(out)


def main():
    for line in sys.stdin:
        print(encode(line.rstrip("\n")))


if __name__ == "__main__":
    main()
```
