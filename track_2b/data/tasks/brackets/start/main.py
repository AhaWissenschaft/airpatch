import sys


def main():
    for line in sys.stdin:
        depth = 0
        for ch in line:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        print("YES" if depth == 0 else "NO")


if __name__ == "__main__":
    main()
