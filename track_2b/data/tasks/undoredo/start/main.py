import sys


def main():
    doc = ""
    history = []
    undone = []
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("type "):
            history.append(doc)
            doc += line[5:]
        elif line.startswith("delete "):
            history.append(doc)
            doc = doc[:-int(line[7:])]
        elif line == "undo":
            if history:
                undone.append(doc)
                doc = history.pop()
        elif line == "redo":
            if undone:
                doc = undone.pop()
        elif line == "print":
            print(f"[{doc}]")


if __name__ == "__main__":
    main()
