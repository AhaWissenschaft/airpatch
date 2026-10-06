import sys


def parse(line):
    fields = []
    current = ""
    in_quotes = False
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == "," and not in_quotes:
            fields.append(current)
            current = ""
        else:
            current += ch
    fields.append(current)
    return fields


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if line:
            print("".join(f"<{field}>" for field in parse(line)))


if __name__ == "__main__":
    main()
