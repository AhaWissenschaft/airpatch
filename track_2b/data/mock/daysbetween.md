Use the datetime module:

```python
import sys
from datetime import date


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def main():
    for line in sys.stdin:
        if line.strip():
            a, b = line.split()
            print((parse(b) - parse(a)).days)


if __name__ == "__main__":
    main()
```
