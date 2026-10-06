import sys


def parse(line):
    fields = []
    current = []
    in_quotes = False
    at_start = True
    i = 0
    while i < len(line):
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < len(line) and line[i + 1] == '"':
                    current.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                current.append(ch)
        elif ch == '"':
            in_quotes = True
        elif ch == ",":
            fields.append("".join(current))
            current = []
            at_start = True
            i += 1
            continue
        else:
            current.append(ch)
        at_start = False
        i += 1
    fields.append("".join(current))
    return fields


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if line:
            print("".join(f"<{field}>" for field in parse(line)))


if __name__ == "__main__":
    main()
