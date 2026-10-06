import sys


def wrap(words, width):
    lines = []
    current = ""
    for word in words:
        if len(current) + 1 + len(word) < width:
            current = current + " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def main():
    data = sys.stdin.read().split("\n", 1)
    width = int(data[0])
    words = data[1].split(" ") if len(data) > 1 else []
    for line in wrap(words, width):
        print(line)


if __name__ == "__main__":
    main()
