import sys


def wrap(words, width):
    lines = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) < width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main():
    first, _, rest = sys.stdin.read().partition("\n")
    width = int(first)
    for line in wrap(rest.split(), width):
        print(line)


if __name__ == "__main__":
    main()
