import sys

PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return True


def main():
    for line in sys.stdin:
        print("YES" if balanced(line) else "NO")


if __name__ == "__main__":
    main()
