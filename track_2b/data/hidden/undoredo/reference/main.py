import sys


def main():
    doc = ""
    undo_stack = []
    redo_stack = []
    for raw in sys.stdin:
        line = raw.rstrip("\n")
        if not line:
            continue
        cmd, _, arg = line.partition(" ")
        if cmd == "type":
            new = doc + arg
        elif cmd == "delete":
            new = doc[:max(0, len(doc) - int(arg))]
        elif cmd == "undo":
            if undo_stack:
                redo_stack.append(doc)
                doc = undo_stack.pop()
            continue
        elif cmd == "redo":
            if redo_stack:
                undo_stack.append(doc)
                doc = redo_stack.pop()
            continue
        elif cmd == "print":
            print(f"[{doc}]")
            continue
        else:
            continue
        if new != doc:
            undo_stack.append(doc)
            redo_stack.clear()
            doc = new


if __name__ == "__main__":
    main()
