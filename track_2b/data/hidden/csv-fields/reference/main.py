import sys


def parse(line):
    fields = []
    i, n = 0, len(line)
    while True:
        if i < n and line[i] == '"':
            i += 1
            buf = []
            while True:
                if line[i] == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        buf.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    buf.append(line[i])
                    i += 1
            fields.append("".join(buf))
        else:
            j = line.find(",", i)
            if j == -1:
                j = n
            fields.append(line[i:j])
            i = j
        if i >= n:
            break
        i += 1
    return fields


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if line:
            print("".join(f"<{field}>" for field in parse(line)))


if __name__ == "__main__":
    main()
