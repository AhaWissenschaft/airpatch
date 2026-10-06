import sys


def balanced(text):
    for opening, closing in ("()", "[]", "{}"):
        depth = 0
        for ch in text:
            if ch == opening:
                depth += 1
            elif ch == closing:
                depth -= 1
                if depth < 0:
                    return False
        if depth:
            return False
    return True


def main():
    for line in sys.stdin:
        print("YES" if balanced(line) else "NO")


if __name__ == "__main__":
    main()
